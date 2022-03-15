import configparser
import os
import platform

from pymongo import MongoClient
from pymongo.collection import Collection
from variables import GKE, MACOS, GKE_AUTOPILOT

CUR_DIR = os.getcwd()
print(f'Current directory is: {CUR_DIR}')
PROJECT_ROOT = "/".join(CUR_DIR.split('/'))
print(f'Project root is: {PROJECT_ROOT}')
config = configparser.ConfigParser()
if MACOS in platform.platform():
    config.read(f'{PROJECT_ROOT}/config.ini')
else:
    config.read(f'{CUR_DIR}/config.ini')

JENKINS_URL = config['DEFAULT']['jenkins_url']
PROJECT_NAME = config['DEFAULT']['project_id']
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_USER = os.getenv('MONGO_USER')


client = MongoClient(JENKINS_URL, connect=False, username=MONGO_USER, password=MONGO_PASSWORD)
db = client[PROJECT_NAME]
gke_clusters: Collection = db.gke_clusters
gke_autopilot_clusters: Collection = db.gke_autopilot_clusters
eks_clusters: Collection = db.eks_clusters
aks_clusters: Collection = db.aks_clusters
users: Collection = db.users


def insert_gke_deployment(cluster_type: str = '', gke_deployment_object: dict = None) -> bool:
    """
    @param cluster_type: The type of the cluster we want to add to the DB. Ex: GKE/GKE Autopilot
    @param gke_deployment_object: The dictionary with all the cluster data.
    """
    if cluster_type == GKE:
        try:
            gke_clusters.insert_one(gke_deployment_object)
            return True
        except:
            print('failure to insert data into gke_clusters table')
            return False
    elif cluster_type == GKE_AUTOPILOT:
        try:
            gke_autopilot_clusters.insert_one(gke_deployment_object)
            return True
        except:
            print('failure to insert data into gke_autopilot_clusters table')
            return False
