# client.py
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class KubernetesClient:
    """Handles Kubernetes API interactions."""
    
    def __init__(self, kubeconfig_path=None):
        """Initialize the Kubernetes client, loading kubeconfig.
        
        Args:
            kubeconfig_path (str, optional): Path to kubeconfig file. Defaults to None (uses default kubeconfig).
        
        Raises:
            Exception: If kubeconfig loading fails.
        """
        try:
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path)
            else:
                config.load_kube_config()
        except Exception as e:
            raise Exception(f"Failed to load kubeconfig: {e}")
        
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.networking_v1 = client.NetworkingV1Api()
    
    def list_namespaces(self):
        """List all namespaces in the cluster."""
        try:
            return [ns.metadata.name for ns in self.core_v1.list_namespace().items]
        except ApiException as e:
            print(f"Error fetching namespaces: {e}")
            return []
    
    def list_deployments(self, namespace):
        """List deployments in a namespace."""
        try:
            return self.apps_v1.list_namespaced_deployment(namespace).items
        except ApiException as e:
            print(f"Error fetching deployments in {namespace}: {e}")
            return []
    
    def list_statefulsets(self, namespace):
        """List statefulsets in a namespace."""
        try:
            return self.apps_v1.list_namespaced_stateful_set(namespace).items
        except ApiException as e:
            print(f"Error fetching statefulsets in {namespace}: {e}")
            return []
    def list_secrets(self, namespace):
        """List secret in a namespace"""
        try:
            return self.core_v1.list_namespaced_secret(namespace).items
        except ApiException as e:
            print(f"Error fetching secrets in {namespace}: {e}")
            return []
        
    def list_services(self, namespace):
        """List services in a namespace."""
        try:
            return self.core_v1.list_namespaced_service(namespace).items
        except ApiException as e:
            print(f"Error fetching services in {namespace}: {e}")
            return []
    
    def list_pvcs(self, namespace):
        """List persistent volume claims in a namespace."""
        try:
            return self.core_v1.list_namespaced_persistent_volume_claim(namespace).items
        except ApiException as e:
            print(f"Error fetching PVCs in {namespace}: {e}")
            return []
    
    def list_ingresses(self, namespace):
        """List ingresses in a namespace."""
        try:
            return self.networking_v1.list_namespaced_ingress(namespace).items
        except ApiException as e:
            print(f"Error fetching ingresses in {namespace}: {e}")
            return []
    
    def list_pods(self, namespace):
        """List pods in a namespace."""
        try:
            return self.core_v1.list_namespaced_pod(namespace).items
        except ApiException as e:
            print(f"Error fetching pods in {namespace}: {e}")
            return []