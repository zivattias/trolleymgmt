import os
from enum import Enum


# Util enums for data mapping
class Environs(Enum):
    SERVER_URL = os.environ.get("TROLLEY_SERVER_URL", "https://something.eu.ngrok.io")
    CLUSTER_NAME = os.environ.get("CLUSTER_NAME", "pavelzagalsky-gke-qjeigibl")
    ZONE_NAME = os.environ.get("ZONE_NAME", "us-east1-b")
    PROJECT_NAME = os.environ.get("PROJECT_NAME", "trolley-361905")
    CLUSTER_TYPE = os.environ.get("CLUSTER_TYPE", "gke")
    MONGO_USER = os.environ.get("MONGO_USER", "pavelzagalsky-gke-qjeigibl")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "password")
    MONGO_URL = os.environ.get("MONGO_URL", "localhost")
    KUBECONFIG_PATH = os.environ.get("KUBECONFIG_PATH", "/home/runner/.kube/config")
    GITHUB_WORKSPACE = os.environ.get("GITHUB_WORKSPACE")


class ContainerIndexes(Enum):
    SERVER_URL = 2
    CLUSTER_NAME = 3
    CLUSTER_TYPE = 5
    MONGO_USER = 7
    MONGO_PASSWORD = 8
    MONGO_URL = 9
    PROJECT_NAME = 10


# Util func for usage in trolley_agent_deployment.main()
def update_env_value(env_list: list, name: str):
    env_list[ContainerIndexes[name].value]["value"] = (
        Environs[name].value.split("-")[0]
        if name == "PROJECT_NAME"
        else Environs[name].value
    )
