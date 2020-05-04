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
        body['spec']['namespace'],
        body['metadata']['name']
    )
    clusterConfigMap.applyInExistingNamespaces()


@kopf.on.create('genesis-mining.com', 'v1beta1', 'clustersecrets')
def createClusterSecret(body, spec, **kwargs):
    clusterSecret = ClusterSecret(
        body['spec']['name'],
        body['spec']['namespace'],
        body['metadata']['name']
    )
    clusterSecret.applyInExistingNamespaces()


@kopf.on.create('', 'v1', 'namespaces')
def createResources(body, spec, **kwargs):
    namespace = body['metadata']['name']

    clusterConfigMaps = ClusterConfigMap.collectConfigMaps()
    clusterSecrets = ClusterSecret.collectSecrets()

    for clusterConfigMap in clusterConfigMaps:
        clusterConfigMap.applyInNewNamespace(namespace)

    for clusterSecret in clusterSecrets:
        clusterSecret.applyInNewNamespace(namespace)

"""
Deletion of ClusterObjects
"""
@kopf.on.delete('genesis-mining.com', 'v1beta1', 'clusterconfigmaps')
def deleteClusterConfigMap(body, spec, **kwargs):
    clusterConfigMap = ClusterConfigMap(
        body['spec']['name'],
        body['spec']['namespace'],
        body['metadata']['name']
    )
    clusterConfigMap.deleteInExistingNamespaces()


@kopf.on.delete('genesis-mining.com', 'v1beta1', 'clustersecrets')
def deleteClusterSecret(body, spec, **kwargs):
    clusterSecret = ClusterSecret(
        body['spec']['name'],
        body['spec']['namespace'],
        body['metadata']['name']
    )
    clusterSecret.deleteInExistingNamespaces()

"""
Updating of ClusterObjects
"""
@kopf.on.update('genesis-mining.com', 'v1beta1', 'clusterconfigmaps')
def updateClusterConfigMap(body, spec, **kwargs):
    deleteClusterConfigMap(body=body, spec=spec)
    createClusterConfigMap(body=body, spec=spec)

@kopf.on.update('genesis-mining.com', 'v1beta1', 'clustersecrets')
def updateClusterSecret(body, spec, **kwargs):
    deleteClusterSecret(body=body, spec=spec)
    createClusterSecret(body=body, spec=spec)
