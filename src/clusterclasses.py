import kubernetes
import re

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
        self.crdApi = kubernetes.client.CustomObjectsApi()
        self.objectName = objectName
        self.readNamespace = readNamespace
        self.includePattern = []
        self.excludePattern = []


class ClusterConfigMap(KubernetesObject):
    """
    Class for storing secrets and applying them to a new
    namespace if created.
    Inherited by KubernetesObject.
    Attributes:
        objectName: see KubernetesObject class
        readNamespace: see KubernetesObject class
    """
    def __init__(self, objectName, readNamespace, crdName):
        super().__init__(objectName, readNamespace)
        self.__configMap = self.v1Api.read_namespaced_config_map(
            name=self.objectName,
            namespace=self.readNamespace
        )
        self.__configMap.metadata.namespace = None
        self.__configMap.metadata.resource_version = None

        customObject = self.crdApi.get_cluster_custom_object(
            group='genesis-mining.com',
            version='v1beta1',
            plural='clusterconfigmaps',
            name=crdName
        )
        try:
            for pattern in customObject['spec']['includeNamespaces']:
                self.includePattern.append(pattern)
        except KeyError:
            pass
        
        try:
            for pattern in customObject['spec']['excludeNamespaces']:
                self.excludePattern.append(pattern)
        except KeyError:
            pass

    """
    Applies the configured configmap to writeNamespace
    Attributes:
        writeNamespace: namespace where the configmap is applied to
    """
    def applyInNewNamespace(self, writeNamespace):
        if len(self.includePattern) == 0 and len(self.excludePattern) == 0:
            # No patterns defined
            deployCM = True
        else:
            if len(self.excludePattern) > 0:
                # Exclude matches? > False
                deployCM = True
                for pattern in self.excludePattern:
                    if re.match(pattern, writeNamespace):
                        deployCM = False
                        break
            if len(self.includePattern) > 0:
                # Include matches? > True
                deployCM = False
                for pattern in self.includePattern:
                    if re.match(pattern, writeNamespace):
                        deployCM = True
                        break
        if deployCM:
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
                try:
                    self.v1Api.delete_namespaced_config_map(
                        name=self.objectName,
                        namespace=namespace.metadata.name
                    )
                except kubernetes.client.rest.ApiException:
                    pass

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
                customObject['spec']['namespace'],
                customObject['metadata']['name']
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
    def __init__(self, objectName, readNamespace, crdName):
        super().__init__(objectName, readNamespace)
        self.__secret = self.v1Api.read_namespaced_secret(
            name=self.objectName,
            namespace=self.readNamespace
        )
        self.__secret.metadata.namespace = None
        self.__secret.metadata.resource_version = None

        customObject = self.crdApi.get_cluster_custom_object(
            group='genesis-mining.com',
            version='v1beta1',
            plural='clustersecrets',
            name=crdName
        )
        try:
            for pattern in customObject['spec']['includeNamespaces']:
                self.includePattern.append(pattern)
        except KeyError:
            pass
        
        try:
            for pattern in customObject['spec']['excludeNamespaces']:
                self.excludePattern.append(pattern)
        except KeyError:
            pass

    """
    Applies the configured secret to writeNamespace
    Attributes:
        writeNamespace: namespace where the secret is applied to
    """
    def applyInNewNamespace(self, writeNamespace):
        if len(self.includePattern) == 0 and len(self.excludePattern) == 0:
            # No patterns defined
            deploySecret = True
        else:
            if len(self.excludePattern) > 0:
                # Exclude matches? > False
                deploySecret = True
                for pattern in self.excludePattern:
                    if re.match(pattern, writeNamespace):
                        deploySecret = False
                        break
            if len(self.includePattern) > 0:
                # Include matches? > True
                deploySecret = False
                for pattern in self.includePattern:
                    if re.match(pattern, writeNamespace):
                        deploySecret = True
                        break
        if deploySecret:
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
                try:
                    self.v1Api.delete_namespaced_secret(
                        name=self.objectName,
                        namespace=namespace.metadata.name
                    )
                except kubernetes.client.rest.ApiException:
                    pass

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
                customObject['spec']['namespace'],
                customObject['metadata']['name']
            ))
        return clusterSecretList
