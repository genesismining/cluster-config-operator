import kopf
from clusterclasses import ClusterSecret, ClusterConfigMap
from os import environ

__author__ = "Christopher Becker"
__license__ = "GNU GPLv3"
__email__ = "christopher.becker@genesis-group.com"

# Apply configured objects to all namespaces initally
if environ.get('APPLY_EXISTING') == 'true':
    # Get the configuration
    clusterConfigMaps = ClusterConfigMap.collectConfig()
    clusterSecrets = ClusterSecret.collectConfig()

    for clusterConfigMap in clusterConfigMaps:
        clusterConfigMap.applyExistingNamespaces()

    for clusterSecret in clusterSecrets:
        clusterSecret.applyExistingNamespaces()

# Apply configured objects to new created namespace
@kopf.on.create('', 'v1', 'namespaces')
def createResources(body, spec, **kwargs):
    namespace = body['metadata']['name']

    # Get the configuration
    clusterConfigMaps = ClusterConfigMap.collectConfig()
    clusterSecrets = ClusterSecret.collectConfig()

    for clusterConfigMap in clusterConfigMaps:
            clusterConfigMap.apply(namespace)

    for clusterSecret in clusterSecrets:
            clusterSecret.apply(namespace)
