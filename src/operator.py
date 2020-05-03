import kopf
from clusterclasses import ClusterSecret, ClusterConfigMap

__author__ = "Christopher Becker"
__license__ = "GNU GPLv3"
__email__ = "christopher.becker@genesis-group.com"

@kopf.on.create('', 'v1', 'namespaces')
def createResources(body, spec, **kwargs):
    namespace = body['metadata']['name']

    # Get the configuration
    clusterConfigMaps = ClusterConfigMap.collectConfig()
    clusterSecrets = ClusterSecret.collectConfig()

    # Apply all configMaps
    for clusterConfigMap in clusterConfigMaps:
            clusterConfigMap.apply(namespace)

    # Apply all secrets
    for clusterSecret in clusterSecrets:
            clusterSecret.apply(namespace)
