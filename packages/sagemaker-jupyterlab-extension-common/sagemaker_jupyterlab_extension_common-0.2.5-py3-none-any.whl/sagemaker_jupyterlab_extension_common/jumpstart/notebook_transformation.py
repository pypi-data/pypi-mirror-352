"""This notebook util is translated based on
https://code.amazon.com/packages/RhinestoneSagemakerUI/blobs/mainline/--/packages/sagemaker-ui-graphql-server/src/services/penny/utils/notebookUtils.ts
https://code.amazon.com/packages/SageMakerHubJavascriptSDK/blobs/mainline/--/src/utils/notebookUtils.ts

TODO: refactor the update notebook logic to make it more clear and efficient
"""

import json
from typing import List, Optional
from sagemaker_jupyterlab_extension_common.jumpstart.constants import (
    DEFAULT_PYTHON3_KERNEL_SPEC,
    JUMPSTART_ALTERATIONS,
    REMOVAL_OPERATIONS,
)
from sagemaker_jupyterlab_extension_common.jumpstart.notebook_types import (
    JumpStartModelNotebookAlterationType,
    JumpStartModelNotebookGlobalActionType,
    JumpStartModelNotebookSubstitution,
    JumpStartModelNotebookSubstitutionTarget,
    JumpStartModelNotebookMetadataUpdateType,
    UpdateHubNotebookUpdateOptions,
)
from abc import ABC, abstractmethod
import nbformat


from sagemaker_jupyterlab_extension_common.util.app_metadata import (
    get_region_name,
)


def _replace_line_with_none(line: str, find: str, replace: Optional[str]) -> str:
    if replace:
        return line.replace(find, replace)
    else:
        return line.replace(f'"{find}"', str(None))


def _is_cell_replacement(alteration: JumpStartModelNotebookAlterationType) -> bool:
    if (
        alteration == JumpStartModelNotebookAlterationType.modelIdVersion
        or alteration == JumpStartModelNotebookAlterationType.modelIdOnly
        or alteration == JumpStartModelNotebookAlterationType.clusterName
        or alteration == JumpStartModelNotebookAlterationType.clusterId
        or alteration == JumpStartModelNotebookAlterationType.hyperPodStudio
        or alteration == JumpStartModelNotebookAlterationType.hyperPodUnifiedStudio
        or alteration == JumpStartModelNotebookAlterationType.estimatorInitHubName
        or alteration == JumpStartModelNotebookAlterationType.modelInitHubName
    ):
        return True
    return False


def _is_cell_removal(alteration: JumpStartModelNotebookAlterationType) -> bool:
    if (
        alteration == JumpStartModelNotebookAlterationType.dropModelSelection
        or alteration == JumpStartModelNotebookAlterationType.dropForDeploy
        or alteration == JumpStartModelNotebookAlterationType.dropForTraining
    ):
        return True
    return False


def _should_remove_cell(notebook_cell: dict) -> bool:
    cell_alterations = notebook_cell["metadata"].get(JUMPSTART_ALTERATIONS)
    if not cell_alterations:
        return False
    try:
        return any(
            JumpStartModelNotebookAlterationType(alteration) in REMOVAL_OPERATIONS
            for alteration in cell_alterations
        )
    except ValueError:
        return False


def _get_substitute_cell(
    model_id: str,
    current_cell: dict,
    cluster_id: Optional[str] = None,
    hub_name: Optional[str] = None,
    connection_id: Optional[str] = None,
    domain: Optional[str] = None,
) -> dict:
    current_alterations = current_cell.get("metadata", {}).get(
        JUMPSTART_ALTERATIONS, []
    )
    if not current_alterations:
        return current_cell
    # currently for each cell we only support one alteration
    current_alteration = current_alterations[0]
    if current_alteration == JumpStartModelNotebookAlterationType.modelIdVersion.value:
        current_cell["source"] = [f'model_id, model_version = "{model_id}", "*"']
    elif current_alteration == JumpStartModelNotebookAlterationType.modelIdOnly.value:
        current_cell["source"] = [f'model_id = "{model_id}"']
    elif current_alteration == JumpStartModelNotebookAlterationType.clusterId.value:
        current_cell["source"] = [
            "%%bash\n",
            f"aws ssm start-session --target sagemaker-cluster:{cluster_id} --region {get_region_name()}",
        ]
    elif current_alteration == JumpStartModelNotebookAlterationType.clusterName.value:
        current_cell["source"] = [
            f"!hyperpod connect-cluster --cluster-name {cluster_id}"
        ]
    elif (
        current_alteration
        == JumpStartModelNotebookAlterationType.estimatorInitHubName.value
        and hub_name
    ):
        substitution = (
            "estimator = JumpStartEstimator(\n"
            "        model_id=train_model_id,\n"
            "        hyperparameters=hyperparameters,\n"
            "        instance_type=training_instance_type,\n"
            f'        hub_name="{hub_name}",\n'
            ")"
        )
        current_cell["source"] = [substitution]
    elif (
        current_alteration
        == JumpStartModelNotebookAlterationType.modelInitHubName.value
        and hub_name
    ):
        substitution = f'model = JumpStartModel(model_id=model_id, model_version=model_version, hub_name="{hub_name}")'
        current_cell["source"] = [substitution]
    elif (
        current_alteration == JumpStartModelNotebookAlterationType.hyperPodStudio.value
    ):
        current_cell["source"] = [f'HYPERPOD_CLUSTER_NAME = "{cluster_id}"']
    elif (
        current_alteration
        == JumpStartModelNotebookAlterationType.hyperPodUnifiedStudio.value
    ):
        current_cell["source"] = [
            f'HYPERPOD_CLUSTER_NAME = "{cluster_id}"\n',
            f'DOMAIN_ID = "{domain}"\n',
            f'CONNECTION_ID = "{connection_id}"',
        ]
    return current_cell


def update_notebook(
    content: str,
    modelId: Optional[str],
    options: UpdateHubNotebookUpdateOptions,
    clusterId: Optional[str] = None,
    hubName: Optional[str] = None,
    connectionId: Optional[str] = None,
    domain: Optional[str] = None,
) -> str:
    """notebook transformation logic. it contains 3 options types to transform the notebook.
    1. remove cells required to be dropped.
    2. replace cells required to be replaced.
    3. substitute part of the cells based on endpoint_name and/or inference_component_name

    :param content: notebook content
    :param modelId: model id
    :param options: update notebook options
    :param clusterId: cluster id
    :param hubName: private hub name
    :param connectionId: connectionid for Unified Studio
    :param domain: domain for Unified Studio
    :return: transformed notebook content.
    :raises ValueError: if notebook is not a valid JSON or if notebook validation fails.
    """
    try:
        nb = json.loads(content)
    except json.decoder.JSONDecodeError as je:
        raise ValueError(f"Notebook is not a valid JSON: {je}")

    # validate notebook by using nbformat version 4 schema
    # https://github.com/jupyter/nbformat/blob/main/nbformat/v4/nbformat.v4.schema.json
    try:
        nbformat.validate(nb, version=4)
    except nbformat.reader.ValidationError as ve:
        raise ValueError(f"Notebook validation failed: {ve}")

    completedSubstitutions = set()
    remove_alterations = [
        alteration for alteration in options.alterations if _is_cell_removal(alteration)
    ]
    replace_alterations = [
        alteration
        for alteration in options.alterations
        if _is_cell_replacement(alteration)
    ]

    # first: remove cells required to be dropped.
    if remove_alterations:
        nb["cells"] = [cell for cell in nb["cells"] if not _should_remove_cell(cell)]

    if JumpStartModelNotebookGlobalActionType.dropAllMarkdown in options.globalActions:
        nb["cells"] = [cell for cell in nb["cells"] if cell["cell_type"] != "markdown"]

    # second: perform alteration, ie remove or replace whole code cell.
    if replace_alterations:
        if modelId or hubName:
            nb["cells"] = [
                (
                    _get_substitute_cell(modelId, cell, hub_name=hubName)
                    if cell["cell_type"] == "code"
                    else cell
                )
                for cell in nb["cells"]
            ]
        elif clusterId:
            nb["cells"] = [
                (
                    _get_substitute_cell(
                        "",
                        cell,
                        cluster_id=clusterId,
                        connection_id=connectionId,
                        domain=domain,
                    )
                    if cell["cell_type"] == "code"
                    else cell
                )
                for cell in nb["cells"]
            ]

    #  third: perform the substitutions, ie find/replace inside a code cells.
    if options.substitutions:
        for substitution in options.substitutions:
            for cell in nb["cells"]:
                if cell["cell_type"] == "code":
                    for i, line in enumerate(cell["source"]):
                        if substitution.find.value in line:
                            line = _replace_line_with_none(
                                line, substitution.find.value, substitution.replace
                            )
                            cell["source"][i] = line
                            if substitution.onlyOnce:
                                completedSubstitutions.add(substitution.find)
                                break
                if substitution.find in completedSubstitutions:
                    break

    # fourth: perform metadata updates (note: this can only replace keys at the top-level)
    for metadata_update in options.metadataUpdates:
        nb["metadata"][metadata_update.key] = metadata_update.value

    # fifth: clean notebook by clearing any output
    for cell in nb["cells"]:
        cell["outputs"] = []

    return json.dumps(nb)


class Notebook(ABC):
    @abstractmethod
    def transform(self, notebook: str, *args, **kwargs) -> str:
        """
        Transform the notebook.
        Args:
            notebook (str): The notebook to transform.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.
        Returns:
            str: The transformed notebook.
        """
        pass


class InferNotebook(Notebook):
    def transform(
        self,
        notebook: str,
        endpoint_name: str,
        inference_component_name: Optional[str] = None,
        set_default_kernel: Optional[bool] = False,
    ) -> str:
        substitutions = self._prepare_substitutions(
            notebook, endpoint_name, inference_component_name
        )
        metadata_updates = self._prepare_metadata_updates(set_default_kernel)

        options = UpdateHubNotebookUpdateOptions(
            substitutions=substitutions,
            alterations=[],
            globalActions=[],
            metadataUpdates=metadata_updates,
        )

        return update_notebook(notebook, None, options)

    def _prepare_substitutions(
        self, notebook: str, endpoint_name: str, inference_component_name: Optional[str]
    ) -> List[JumpStartModelNotebookSubstitution]:
        substitutions = [
            self._create_substitution(
                JumpStartModelNotebookSubstitutionTarget.endpointName, endpoint_name
            )
        ]
        if self._has_placeholder(
            notebook, JumpStartModelNotebookSubstitutionTarget.inferenceComponent
        ):
            substitutions.append(
                self._create_substitution(
                    JumpStartModelNotebookSubstitutionTarget.inferenceComponent,
                    inference_component_name,
                )
            )
        elif inference_component_name:
            substitutions.extend(
                self._handle_inference_component_substitutions(
                    notebook, inference_component_name
                )
            )
        return substitutions

    def _prepare_metadata_updates(
        self, set_default_kernel: Optional[bool]
    ) -> List[JumpStartModelNotebookMetadataUpdateType]:
        return (
            [
                JumpStartModelNotebookMetadataUpdateType(
                    key="kernelspec",
                    value=DEFAULT_PYTHON3_KERNEL_SPEC,
                )
            ]
            if set_default_kernel
            else []
        )

    def _has_placeholder(
        self, notebook: str, target: JumpStartModelNotebookSubstitutionTarget
    ) -> bool:
        """Check if the notebook contains the given placeholder."""
        return target.value in notebook

    def _create_substitution(
        self,
        target: JumpStartModelNotebookSubstitutionTarget,
        replacement: str,
        onlyOnce: bool = True,
    ) -> JumpStartModelNotebookSubstitution:
        """Create a substitution object for the given target and replacement."""
        return JumpStartModelNotebookSubstitution(target, replacement, onlyOnce)

    def _handle_inference_component_substitutions(
        self, notebook: str, component_name: str
    ) -> List[JumpStartModelNotebookSubstitution]:
        """Create substitutions for inference component based on the notebook's content."""
        substitutions = []
        for target in [
            JumpStartModelNotebookSubstitutionTarget.inferenceComponentBoto3,
            JumpStartModelNotebookSubstitutionTarget.inferenceComponentSdk,
        ]:
            if self._has_placeholder(notebook, target):
                if (
                    target
                    == JumpStartModelNotebookSubstitutionTarget.inferenceComponentSdk
                ):
                    replacement = f"(endpoint_name=endpoint_name, inference_component_name='{component_name}')"
                else:
                    replacement = (
                        f"{target.value}, InferenceComponentName='{component_name}'"
                    )
                substitutions.append(self._create_substitution(target, replacement))
        return substitutions


class ModelSdkNotebook(Notebook):
    def transform(
        self, notebook: str, modelId: str, hubName: Optional[str] = None
    ) -> str:
        alterations = [
            JumpStartModelNotebookAlterationType.dropModelSelection,
            JumpStartModelNotebookAlterationType.modelIdOnly,
            JumpStartModelNotebookAlterationType.modelIdVersion,
            JumpStartModelNotebookAlterationType.modelInitHubName,
            JumpStartModelNotebookAlterationType.estimatorInitHubName,
        ]
        options = UpdateHubNotebookUpdateOptions([], alterations, [])
        notebook = update_notebook(notebook, modelId, options, hubName=hubName)
        return notebook


class HyperpodNotebook(Notebook):
    def transform(
        self,
        notebook: str,
        clusterId: str,
        connectionId: str = None,
        domain: str = None,
    ) -> str:
        alterations = [
            JumpStartModelNotebookAlterationType.clusterName,
            JumpStartModelNotebookAlterationType.clusterId,
            JumpStartModelNotebookAlterationType.hyperPodStudio,
            JumpStartModelNotebookAlterationType.hyperPodUnifiedStudio,
        ]
        options = UpdateHubNotebookUpdateOptions([], alterations, [])
        notebook = update_notebook(
            notebook,
            None,
            options,
            clusterId=clusterId,
            connectionId=connectionId,
            domain=domain,
        )
        return notebook
