import json
import logging
import os
import platform
import sys
from subprocess import PIPE, run

import yaml
from kubernetes import config
from trolley_agent_deployment_utils import ContainerIndexes, Environs, update_env_value

if "macOS" in platform.platform():
    home_path = f"{os.getcwd()}"
    deployment_yaml_path_ = "/".join(home_path.split("/")[:-1])
else:
    home_path = Environs.GITHUB_WORKSPACE
    print(f"home_path is: {home_path}")
    print(f"trolley_deployment_path is: {home_path}")
    deployment_yaml_path_ = "/".join(home_path.split("/"))
    print(f"deployment_yaml_path is: {deployment_yaml_path_}")

log_file_name = "agent_main.log"
deployment_yaml_path = (
    f"{deployment_yaml_path_}/agents/k8s_agent/agent_deployment_yamls"
)
print(f"deployment_yaml_path is: {deployment_yaml_path}")
base_trolley_agent_full_path = f"{deployment_yaml_path}/full_agent_deployment.yml"
print(f"base_trolley_agent_full_path is: {base_trolley_agent_full_path}")
edited_trolley_agent_full_path = f"{deployment_yaml_path}/edited_agent_deployment.yml"
print(f"edited_trolley_agent_full_path is: {edited_trolley_agent_full_path}")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{home_path}/{log_file_name}"),
        logging.StreamHandler(sys.stdout),
    ],
)

logging.info(f"deployment_yaml_path_ is {deployment_yaml_path_}")
logging.info(f"deployment_yaml_path is {deployment_yaml_path}")
logging.info(f"base_trolley_agent_full_path is {base_trolley_agent_full_path}")
logging.info(f"edited_trolley_agent_full_path is {edited_trolley_agent_full_path}")
logging.info(os.getcwd())
logging.info(os.listdir())


def main():
    kubeconfig_gen_command = (
        f"gcloud container clusters get-credentials {Environs.CLUSTER_NAME} "
        f"--region {Environs.ZONE_NAME} --project {Environs.PROJECT_NAME}"
    )

    logging.info(f"Running kubeconfig creation command {kubeconfig_gen_command}")
    result = run(
        kubeconfig_gen_command, stdout=PIPE, stderr=PIPE, text=True, shell=True
    )
    if result.returncode > 0:
        logging.error(f"A problem occurred: {result.stderr}")
        sys.exit()
    else:
        logging.info(
            f"{kubeconfig_gen_command} command ran successfully: {result.stdout}"
        )
    try:
        config.load_kube_config(Environs.KUBECONFIG_PATH)
    except config.config_exception:
        raise Exception("Could not configure kubernetes python client")
    stream = open(base_trolley_agent_full_path, "r")
    deployment_yamls = yaml.load_all(stream, yaml.FullLoader)

    # Find a better way to handle this monstrosity
    deployments_string = ""
    for deployment_yaml in deployment_yamls:
        if deployment_yaml["kind"] == "Deployment":
            containers = deployment_yaml["spec"]["template"]["spec"]["containers"]
            env_list = containers[0]["env"]

            for env_value in env_list:
                if env_value in [
                    "SERVER_URL",
                    "CLUSTER_NAME",
                    "CLUSTER_TYPE",
                    "MONGO_USER",
                    "MONGO_PASSWORD",
                    "MONGO_URL",
                    "PROJECT_NAME",
                ]:
                    update_env_value(env_list=env_list, name=env_value)

        deployment_string = json.dumps(deployment_yaml)
        deployments_string += f"---\n{deployment_string}\n"

    with open(edited_trolley_agent_full_path, "w") as f:
        f.write(deployments_string)
    command = f"kubectl apply -f {edited_trolley_agent_full_path}"
    result = run(command, stdout=PIPE, stderr=PIPE, text=True, shell=True)
    if result.returncode > 0:
        logging.error(f"A problem occurred: {result.stderr}")
        sys.exit()
    else:
        logging.info(f"{command} command ran successfully: {result.stdout}")
    logging.info(result)


if __name__ == "__main__":
    main()
