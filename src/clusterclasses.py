import kubernetes


class KubernetesObject():
    """
    Generic Kubernetes Object.
    Initializes the connection to the Kubernetes API Server

    Attributes:
        objectName: name of the object which has to be cloned
        readNamespace: source namespace of the object which has to be cloned
    """
    def __init__(self, objectName, readNamespace):
        kubernetes.config.load_incluster_config()
        self.v1Api = kubernetes.client.CoreV1Api()
        self.objectName = objectName
        self.readNamespace = readNamespace


class ClusterConfigMap(KubernetesObject):
    """
    Class for storing secrets and applying them to a new
    namespace if created.
    Inherited by KubernetesObject.
    Attributes:
        objectName: see KubernetesObject class
        readNamespace: see KubernetesObject class
    """
    def __init__(self, objectName, readNamespace):
        super().__init__(objectName, readNamespace)
        self.__configMap = self.v1Api.read_namespaced_config_map(
            name=self.objectName,
            namespace=self.readNamespace
        )
        self.__configMap.metadata.namespace = None
        self.__configMap.metadata.resource_version = None

    """
    Applies the configured configmap to writeNamespace
    Attributes:
        writeNamespace: namespace where the configmap is applied to
    """
    def applyInNewNamespace(self, writeNamespace):
        self.v1Api.create_namespaced_config_map(
            namespace=writeNamespace,
            body=self.__configMap
        )

    """
    Applies the configured configmap to all existing namespaces
    """
    def applyInExistingNamespaces(self):
        namespaces = self.v1Api.list_namespace()
        for namespace in namespaces.items:
            try:
                self.applyInNewNamespace(writeNamespace=namespace.metadata.name)
            except kubernetes.client.rest.ApiException as e:
                print(e)

    """
    Deletes all configured configmaps
    """
    def deleteInExistingNamespaces(self):
        namespaces = self.v1Api.list_namespace()
        for namespace in namespaces.items:
            if not namespace.metadata.name == self.readNamespace:
                self.v1Api.delete_namespaced_config_map(
                    name=self.objectName,
                    namespace=namespace.metadata.name
                )

    """
    Collects all configured configmaps out of CRDs and
    creates an array of ClusterConfigMap objects out of it.
    Static Method.
    """
    @staticmethod
    def collectConfigMaps():
        clusterConfigMapList = []
        kubernetes.config.load_incluster_config()
        crdApi = kubernetes.client.CustomObjectsApi()
        customObjectList = crdApi.list_cluster_custom_object(
            group='genesis-mining.com',
            version='v1beta1',
            plural='clusterconfigmaps'
        )
        for customObject in customObjectList['items']:
            clusterConfigMapList.append(ClusterConfigMap(
                customObject['spec']['name'],
                customObject['spec']['namespace']
            ))
        return clusterConfigMapList


class ClusterSecret(KubernetesObject):
    """
    Class for storing configmaps and applying them to a new
    namespace if created.
    Inherited by KubernetesObject.
    Attributes:
        objectName: see KubernetesObject class
        readNamespace: see KubernetesObject class
    """
    def __init__(self, objectName, readNamespace):
        super().__init__(objectName, readNamespace)
        self.__secret = self.v1Api.read_namespaced_secret(
            name=self.objectName,
            namespace=self.readNamespace
        )
        self.__secret.metadata.namespace = None
        self.__secret.metadata.resource_version = None

    """
    Applies the configured secret to writeNamespace
    Attributes:
        writeNamespace: namespace where the secret is applied to
    """
    def applyInNewNamespace(self, writeNamespace):
        self.v1Api.create_namespaced_secret(
            namespace=writeNamespace,
            body=self.__secret
        )

    """
    Applies the configured secret to all existing namespaces
    """
    def applyInExistingNamespaces(self):
        namespaces = self.v1Api.list_namespace()
        for namespace in namespaces.items:
            try:
                self.applyInNewNamespace(writeNamespace=namespace.metadata.name)
            except kubernetes.client.rest.ApiException as e:
                print(e)

    """
    Deletes all configured secrets
    """
    def deleteInExistingNamespaces(self):
        namespaces = self.v1Api.list_namespace()
        for namespace in namespaces.items:
            if not namespace.metadata.name == self.readNamespace:
                self.v1Api.delete_namespaced_secret(
                    name=self.objectName,
                    namespace=namespace.metadata.name
                )

    """
    Collects all configured secrets out of CRDs and
    creates an array of ClusterSecret objects out of it.
    Static Method.
    """
    @staticmethod
    def collectSecrets():
        clusterSecretList = []
        kubernetes.config.load_incluster_config()
        crdApi = kubernetes.client.CustomObjectsApi()
        customObjectList = crdApi.list_cluster_custom_object(
            group='genesis-mining.com',
            version='v1beta1',
            plural='clustersecrets'
        )
        for customObject in customObjectList['items']:
            clusterSecretList.append(ClusterSecret(
                customObject['spec']['name'],
                customObject['spec']['namespace']
            ))
        return clusterSecretList
