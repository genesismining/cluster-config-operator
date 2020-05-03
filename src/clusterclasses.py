import kubernetes
import json

class KubernetesObject():
    def __init__(self, objectName, readNamespace):
        kubernetes.config.load_incluster_config()
        self.v1Api = kubernetes.client.CoreV1Api()
        self.objectName = objectName
        self.readNamespace = readNamespace


class ClusterConfigMap(KubernetesObject):
    def __init__(self, objectName, readNamespace):
        super().__init__(objectName, readNamespace)

    def __getConfigMap(self):
        self.__configMap = self.v1Api.read_namespaced_config_map(
            name=self.objectName,
            namespace=self.readNamespace
        )

    def apply(self, writeNamespace):
        self.__getConfigMap()
        self.__configMap.metadata.namespace = None
        self.__configMap.metadata.resource_version = None
        self.v1Api.create_namespaced_config_map(
            namespace=writeNamespace,
            body=self.__configMap
        )

    @staticmethod
    def collectConfig():
        objectList = []
        with open('config.json') as configFile:
            configMaps = json.load(configFile)
            del configMaps['configmaps'][-1]
            for configMap in configMaps['configmaps']:
                objectList.append(ClusterConfigMap(
                    configMap['name'],
                    configMap['namespace']
                ))
        return objectList
                

class ClusterSecret(KubernetesObject):
    def __init__(self, objectName, readNamespace):
        super().__init__(objectName, readNamespace)

    def __getSecret(self):
        self.__secret = self.v1Api.read_namespaced_secret(
            name=self.objectName,
            namespace=self.readNamespace
        )

    def apply(self, writeNamespace):
        self.__getSecret()
        self.__secret.metadata.namespace = None
        self.__secret.metadata.resource_version = None
        self.v1Api.create_namespaced_secret(
            namespace=writeNamespace,
            body=self.__secret
        )

    @staticmethod
    def collectConfig():
        objectList = []
        with open('config.json') as configFile:
            secrets = json.load(configFile)
            del secrets['secrets'][-1]
            for secret in secrets['secrets']:
                objectList.append(ClusterSecret(
                    secret['name'],
                    secret['namespace']
                ))
        return objectList
