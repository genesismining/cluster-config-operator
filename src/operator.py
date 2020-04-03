import kubernetes
import kopf
from os import environ

kubernetes.config.load_incluster_config()
v1_api = kubernetes.client.CoreV1Api()

SEC_SCHEMA = {
    'apiVersion': 'v1',
    'kind': 'Secret',
    'metadata': {
        'name': 'placeholder',
        'namespace': 'placeholder'
    },
    'type': 'Opaque'
}


@kopf.on.create('', 'v1', 'namespaces')
def create_secret(body, spec, **kwargs):
    NS_NAME = body['metadata']['name']
    try:
        SECRET = v1_api.read_namespaced_secret(
            name=environ.get('SECRET_NAME'),
            namespace=environ.get('SECRET_NAMESPACE'),
        )
        DATA = SECRET.data
    except Exception:
        print("Source Secret not found")

    SEC_SCHEMA['metadata']['name'] = environ.get('SECRET_NAME')
    SEC_SCHEMA['metadata']['namespace'] = NS_NAME
    SEC_SCHEMA['data'] = DATA

    try:
        v1_api.create_namespaced_secret(
            namespace=NS_NAME,
            body=SEC_SCHEMA
        )
    except Exception:
        print("Could not apply secret")
