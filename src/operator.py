import kopf
from clusterclasses import ClusterSecret, ClusterConfigMap

clusterConfigMaps = ClusterConfigMap.collectConfig()
clusterSecrets = ClusterSecret.collectConfig()

@kopf.on.create('', 'v1', 'namespaces')
def createResources(body, spec, **kwargs):
    namespace = body['metadata']['name']

    for clusterConfigMap in clusterConfigMaps:
            clusterConfigMap.apply(namespace)


    for clusterSecret in clusterSecrets:
            clusterSecret.apply(namespace)
