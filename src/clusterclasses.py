import kubernetes
import re


class KubernetesObject:
    """
    Generic Kubernetes Object.
    Initializes the connection to the Kubernetes API Server

    Attributes:
        object_name: name of the object which has to be cloned
        read_namespace: source namespace of the object which has to be cloned
    """
    def __init__(self, object_name, read_namespace):
        kubernetes.config.load_incluster_config()
        self.v1_api = kubernetes.client.CoreV1Api()
        self.crd_api = kubernetes.client.CustomObjectsApi()
        self.object_name = object_name
        self.read_namespace = read_namespace
        self.exclude_pattern = []
        self.include_pattern = []


    def get_includes_and_excludes(self, custom_object):
        try:
            for pattern in custom_object['spec']['includeNamespaces']:
                self.include_pattern.append(pattern)
        except KeyError:
            pass

        try:
            for pattern in custom_object['spec']['excludeNamespaces']:
                self.exclude_pattern.append(pattern)
        except KeyError:
            pass

    def analyze_includes_and_excludes(self, write_namespace):
        if len(self.include_pattern) == 0 and len(self.exclude_pattern) == 0:
            # No patterns defined
            apply = True
        else:
            if len(self.exclude_pattern) > 0:
                # Exclude matches? > False
                apply = True
                for pattern in self.exclude_pattern:
                    if re.match(pattern, write_namespace):
                        apply = False
                        break
            if len(self.include_pattern) > 0:
                # Include matches? > True
                apply = False
                for pattern in self.include_pattern:
                    if re.match(pattern, write_namespace):
                        apply = True
                        break
        return apply

class ClusterConfigMap(KubernetesObject):
    """
    Class for storing secrets and applying them to a new
    namespace if created.
    Inherited by KubernetesObject.
    Attributes:
        object_name: see KubernetesObject class
        read_namespace: see KubernetesObject class
    """
    def __init__(self, object_name, read_namespace, crd_name):
        super().__init__(object_name, read_namespace)
        self.__config_map = self.v1_api.read_namespaced_config_map(
            name=self.object_name,
            namespace=self.read_namespace
        )
        self.__config_map.metadata.namespace = None
        self.__config_map.metadata.resource_version = None

        custom_object = self.crd_api.get_cluster_custom_object(
            group='genesis-mining.com',
            version='v1beta1',
            plural='clusterconfigmaps',
            name=crd_name
        )
        super().get_includes_and_excludes(custom_object)

    """
    Applies the configured configmap to write_namespace
    Attributes:
        write_namespace: namespace where the configmap is applied to
    """
    def apply_in_new_namespace(self, write_namespace):
        if self.analyze_includes_and_excludes(write_namespace):
            self.v1_api.create_namespaced_config_map(
                namespace=write_namespace,
                body=self.__config_map
            )

    """
    Applies the configured configmap to all existing namespaces
    """
    def apply_in_existing_namespaces(self):
        namespaces = self.v1_api.list_namespace()
        for namespace in namespaces.items:
            try:
                self.apply_in_new_namespace(write_namespace=namespace.metadata.name)
            except kubernetes.client.rest.ApiException as e:
                print(e)

    """
    Deletes all configured configmaps
    """
    def delete_in_existing_namespaces(self):
        namespaces = self.v1_api.list_namespace()
        for namespace in namespaces.items:
            if not namespace.metadata.name == self.read_namespace:
                try:
                    self.v1_api.delete_namespaced_config_map(
                        name=self.object_name,
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
    def collect_config_maps():
        cluster_config_map_list = []
        kubernetes.config.load_incluster_config()
        crd_api = kubernetes.client.CustomObjectsApi()
        custom_objects_list = crd_api.list_cluster_custom_object(
            group='genesis-mining.com',
            version='v1beta1',
            plural='clusterconfigmaps'
        )
        for custom_object in custom_objects_list['items']:
            cluster_config_map_list.append(ClusterConfigMap(
                custom_object['spec']['name'],
                custom_object['spec']['namespace'],
                custom_object['metadata']['name']
            ))
        return cluster_config_map_list


class ClusterSecret(KubernetesObject):
    """
    Class for storing configmaps and applying them to a new
    namespace if created.
    Inherited by KubernetesObject.
    Attributes:
        object_name: see KubernetesObject class
        read_namespace: see KubernetesObject class
    """
    def __init__(self, object_name, read_namespace, crd_name):
        super().__init__(object_name, read_namespace)
        self.__secret = self.v1_api.read_namespaced_secret(
            name=self.object_name,
            namespace=self.read_namespace
        )
        self.__secret.metadata.namespace = None
        self.__secret.metadata.resource_version = None

        custom_object = self.crd_api.get_cluster_custom_object(
            group='genesis-mining.com',
            version='v1beta1',
            plural='clustersecrets',
            name=crd_name
        )
        self.get_includes_and_excludes(custom_object)


    """
    Applies the configured secret to write_namespace
    Attributes:
        write_namespace: namespace where the secret is applied to
    """
    def apply_in_new_namespace(self, write_namespace):
        if self.analyze_includes_and_excludes(write_namespace):
            self.v1_api.create_namespaced_secret(
                namespace=write_namespace,
                body=self.__secret
            )

    """
    Applies the configured secret to all existing namespaces
    """
    def apply_in_existing_namespaces(self):
        namespaces = self.v1_api.list_namespace()
        for namespace in namespaces.items:
            try:
                self.apply_in_new_namespace(write_namespace=namespace.metadata.name)
            except kubernetes.client.rest.ApiException as e:
                print(e)

    """
    Deletes all configured secrets
    """
    def delete_in_existing_namespaces(self):
        namespaces = self.v1_api.list_namespace()
        for namespace in namespaces.items:
            if not namespace.metadata.name == self.read_namespace:
                try:
                    self.v1_api.delete_namespaced_secret(
                        name=self.object_name,
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
    def collect_secrets():
        cluster_secret_list = []
        kubernetes.config.load_incluster_config()
        crd_api = kubernetes.client.CustomObjectsApi()
        custom_object_list = crd_api.list_cluster_custom_object(
            group='genesis-mining.com',
            version='v1beta1',
            plural='clustersecrets'
        )
        for custom_object in custom_object_list['items']:
            cluster_secret_list.append(ClusterSecret(
                custom_object['spec']['name'],
                custom_object['spec']['namespace'],
                custom_object['metadata']['name']
            ))
        return cluster_secret_list
