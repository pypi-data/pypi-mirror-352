from enum import Enum
import os
from sagemaker_jupyterlab_extension_common.constants import DEFAULT_HOME_DIRECTORY
from sagemaker_jupyterlab_extension_common.jumpstart.notebook_types import (
    JumpStartModelNotebookAlterationType,
    JumpStartResourceType,
)

NOTEBOOK_TRANSFORMATION_TYPE = frozenset(
    [
        JumpStartResourceType.inferNotebook,
        JumpStartResourceType.modelSdkNotebook,
        JumpStartResourceType.hyperpodNotebook,
    ]
)
REMOVAL_OPERATIONS = frozenset(
    [
        JumpStartModelNotebookAlterationType.dropModelSelection,
        JumpStartModelNotebookAlterationType.dropForDeploy,
        JumpStartModelNotebookAlterationType.dropForTraining,
    ]
)

HOME_PATH = os.environ.get("HOME", DEFAULT_HOME_DIRECTORY)
NOTEBOOK_FOLDER = "DemoNotebooks"
NOTEBOOK_PATH = f"{HOME_PATH}/{NOTEBOOK_FOLDER}/"
MD_PATH = "src"
MD_NOTEBOOK_PATH = f"{HOME_PATH}/{MD_PATH}/{NOTEBOOK_FOLDER}/"


JUMPSTART_ALTERATIONS = "jumpStartAlterations"

# Setup notebook max size based on:
# https://docs.anaconda.com/anaconda-repository/user-guide/tasks/work-with-notebooks/#:~:text=Uploading%20a%20notebook,MAX_IPYNB_SIZE%20variable%20in%20the%20config.
NOTEBOOK_SIZE_LIMIT_IN_BYTES = 26214400  # 25MB
NOTEBOOK_SIZE_LIMIT_IN_MB = NOTEBOOK_SIZE_LIMIT_IN_BYTES / 1048576

CLIENT_REQUEST_ID_HEADER = "X-Client-Req-Id"
SERVER_REQUEST_ID_HEADER = "X-Server-Req-Id"

MISSING_CLIENT_REQUEST_ID = "MISSING_CLIENT_REQUEST_ID"
MISSING_SERVER_REQUEST_ID = "MISSING_SERVER_REQUEST_ID"

# TODO: support RIP.
JUMPSTART_GA_REGIONS = frozenset(
    [
        "eu-north-1",
        "me-south-1",
        "ap-south-1",
        "eu-west-3",
        "us-east-2",
        "af-south-1",
        "eu-west-1",
        "eu-central-1",
        "sa-east-1",
        "ap-east-1",
        "us-east-1",
        "ap-northeast-2",
        "eu-west-2",
        "eu-south-1",
        "ap-northeast-1",
        "us-west-2",
        "us-west-1",
        "ap-southeast-1",
        "ap-southeast-2",
        "ca-central-1",
        "ap-northeast-3",
        "il-central-1",
        "ap-southeast-3",
        "me-central-1",
        "eu-central-2",
        "ap-southeast-5",
        "ap-south-2",
        "ap-southeast-4",
        "ap-southeast-7",
        "ca-west-1",
        "eu-south-2",
        "mx-central-1",
        "us-gov-west-1",
        "us-gov-east-1",
        "cn-north-1",
        "cn-northwest-1",
    ]
)


class ErrorCode(str, Enum):
    NOTEBOOK_NOT_AVAILABLE = "NOTEBOOK_NOT_AVAILABLE"
    NOTEBOOK_SIZE_TOO_LARGE = "NOTEBOOK_SIZE_TOO_LARGE"
    INVALID_REQUEST = "INVALID_REQUEST"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DOWNLOAD_DIRECTORY_NOT_FOUND = "DOWNLOAD_DIRECTORY_NOT_FOUND"


DEFAULT_PYTHON3_KERNEL_SPEC = {
    "display_name": "Python 3 (ipykernel)",
    "language": "python",
    "name": "python3",
}
