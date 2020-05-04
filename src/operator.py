import kopf
from .clusterclasses import ClusterSecret, ClusterConfigMap

__author__ = "Christopher Becker"
__license__ = "GNU GPLv3"
__email__ = "christopher.becker@genesis-group.com"


"""
Creation of new ClusterObjects or new Namespaces
"""


@kopf.on.create('genesis-mining.com', 'v1beta1', 'clusterconfigmaps')
def create_cluster_config_map(body, spec, **kwargs):
    cluster_config_map = ClusterConfigMap(
        body['spec']['name'],
        body['spec']['namespace'],
        body['metadata']['name']
    )
    cluster_config_map.apply_in_existing_namespaces()


@kopf.on.create('genesis-mining.com', 'v1beta1', 'clustersecrets')
def create_cluster_secret(body, spec, **kwargs):
    cluster_secret = ClusterSecret(
        body['spec']['name'],
        body['spec']['namespace'],
        body['metadata']['name']
    )
    cluster_secret.apply_in_existing_namespaces()


@kopf.on.create('', 'v1', 'namespaces')
def create_resources(body, spec, **kwargs):
    namespace = body['metadata']['name']

    cluster_config_maps = ClusterConfigMap.collect_config_maps()
    cluster_secrets = ClusterSecret.collect_secrets()

    for cluster_config_map in cluster_config_maps:
        cluster_config_map.apply_in_new_namespace(namespace)

    for cluster_secret in cluster_secrets:
        cluster_secret.apply_in_new_namespace(namespace)


"""
Deletion of ClusterObjects
"""


@kopf.on.delete('genesis-mining.com', 'v1beta1', 'clusterconfigmaps')
def delete_cluster_config_map(body, spec, **kwargs):
    cluster_config_map = ClusterConfigMap(
        body['spec']['name'],
        body['spec']['namespace'],
        body['metadata']['name']
    )
    cluster_config_map.delete_in_existing_namespaces()


@kopf.on.delete('genesis-mining.com', 'v1beta1', 'clustersecrets')
def delete_cluster_secret(body, spec, **kwargs):
    cluster_secret = ClusterSecret(
        body['spec']['name'],
        body['spec']['namespace'],
        body['metadata']['name']
    )
    cluster_secret.delete_in_existing_namespaces()


"""
Updating of ClusterObjects
"""


@kopf.on.update('genesis-mining.com', 'v1beta1', 'clusterconfigmaps')
def update_cluster_config_map(body, spec, **kwargs):
    delete_cluster_config_map(body=body, spec=spec)
    create_cluster_config_map(body=body, spec=spec)


@kopf.on.update('genesis-mining.com', 'v1beta1', 'clustersecrets')
def update_cluster_secret(body, spec, **kwargs):
    delete_cluster_secret(body=body, spec=spec)
    create_cluster_secret(body=body, spec=spec)
