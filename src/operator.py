import kopf
from clusterclasses import ClusterSecret, ClusterConfigMap

__author__ = "Christopher Becker"
__license__ = "GNU GPLv3"
__email__ = "christopher.becker@genesis-group.com"


"""
Creation of new ClusterObjects or new Namespaces
"""
@kopf.on.create('genesis-mining.com', 'v1beta1', 'clusterconfigmaps')
def createClusterConfigMap(body, spec, **kwargs):
    clusterConfigMap = ClusterConfigMap(
        body['spec']['name'],
        body['spec']['namespace']
    )
    clusterConfigMap.applyInExistingNamespaces()


@kopf.on.create('genesis-mining.com', 'v1beta1', 'clustersecrets')
def createClusterSecret(body, spec, **kwargs):
    clusterSecret = ClusterSecret(
        body['spec']['name'],
        body['spec']['namespace']
    )
    clusterSecret.applyInExistingNamespaces()


@kopf.on.create('', 'v1', 'namespaces')
def createResources(body, spec, **kwargs):
    namespace = body['metadata']['name']

    clusterConfigMaps = ClusterConfigMap.collectConfigMaps()
    clusterSecrets = ClusterSecret.collectSecrets()

    for clusterConfigMap in clusterConfigMaps:
        clusterConfigMap.apply(namespace)

    for clusterSecret in clusterSecrets:
        clusterSecret.apply(namespace)


"""
Deletion of ClusterObjects
"""
@kopf.on.delete('genesis-mining.com', 'v1beta1', 'clusterconfigmaps')
def deleteClusterConfigMap(body, spec, **kwargs):
    clusterConfigMap = ClusterConfigMap(
        body['spec']['name'],
        body['spec']['namespace']
    )
    clusterConfigMap.deleteInExistingNamespaces()


@kopf.on.delete('genesis-mining.com', 'v1beta1', 'clustersecrets')
def deleteClusterSecret(body, spec, **kwargs):
    clusterSecret = ClusterSecret(
        body['spec']['name'],
        body['spec']['namespace']
    )
    clusterSecret.deleteInExistingNamespaces()
