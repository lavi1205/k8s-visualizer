from .client import KubernetesClient

class ResourceCollector:
    """Collects and processes Kubernetes resources from specified namespaces."""
    
    DATABASE_NAMESPACES = {"redis-prod", "redis-nonprd", "mongodb", "rabbitmq"}
    
    def __init__(self, namespaces, kubeconfig_path=None):
        """Initialize the resource collector.
        
        Args:
            namespaces (list): List of namespaces to collect resources from.
            kubeconfig_path (str, optional): Path to kubeconfig file.
        """
        self.namespaces = namespaces
        self.client = KubernetesClient(kubeconfig_path)
    
    def shorten(self, name, max_len=30):
        """Shorten a name with line breaks for display and return full name for tooltip.
        
        Args:
            name (str): Resource name to shorten.
            max_len (int): Maximum length before wrapping.
        
        Returns:
            tuple: (display_name, full_name)
        """
        if len(name) <= max_len:
            return name, name
        parts = name.split("-")
        wrapped = ""
        current_len = 0
        for part in parts:
            if current_len + len(part) > max_len:
                wrapped += "\\n" + part
                current_len = len(part)
            else:
                wrapped += ("-" if wrapped else "") + part
                current_len += len(part) + 1
        return wrapped, name
    
    def collect_resources(self):
        """Collect deployments, statefulsets, services, PVCs, ingresses, and pods from all namespaces.
        
        Returns:
            tuple: Lists of raw Kubernetes resource objects (deployments, statefulsets, services, pvcs, ingresses, pods, secrets).
        """
        deployments = []
        statefulsets = []
        services = []
        pvcs = []
        ingresses = []
        pods = []
        secrets = []
        for ns in self.namespaces:
            try:
                # Fetch deployments (skip for database namespaces)
                if ns not in self.DATABASE_NAMESPACES:
                    try:
                        deployments.extend(self.client.list_deployments(ns))
                    except Exception as e:
                        print(f"Error fetching deployments in namespace {ns}: {str(e)}")
                
                # Fetch statefulsets (prioritize for database namespaces)
                try:
                    statefulsets.extend(self.client.list_statefulsets(ns))
                except Exception as e:
                    print(f"Error fetching statefulsets in namespace {ns}: {str(e)}")
                
                # Fetch services
                try:
                    services.extend(self.client.list_services(ns))
                except Exception as e:
                    print(f"Error fetching services in namespace {ns}: {str(e)}")
                
                # Fetch PVCs
                try:
                    pvcs.extend(self.client.list_pvcs(ns))
                except Exception as e:
                    print(f"Error fetching PVCs in namespace {ns}: {str(e)}")
                
                # Fetch ingresses
                try:
                    ingresses.extend(self.client.list_ingresses(ns))
                except Exception as e:
                    print(f"Error fetching ingresses in namespace {ns}: {str(e)}")
                
                # Fetch pods with status
                try:
                    pods.extend(self.client.list_pods(ns))
                except Exception as e:
                    print(f"Error fetching pods in namespace {ns}: {str(e)}")
                
                # Fetch secrets
                try:
                    secrets.extend(self.client.list_secrets(ns))
                except Exception as e:
                    print(f"Error fetching secrets in namespace {ns}: {str(e)}")
            except Exception as e:
                print(f"Error processing namespace {ns}: {str(e)}")
        return deployments, statefulsets, services, pvcs, ingresses, pods, secrets
    
    def collect_summary(self):
        """Collect summarized data for visualizations.
        
        Returns:
            tuple: Lists of summarized data (name, replicas/count, namespace) for each resource type.
        """
        deployments, statefulsets, services, pvcs, ingresses, pods, secrets = [], [], [], [], [], [], []
        for ns in self.namespaces:
            try:
                # Fetch deployments (skip for database namespaces)
                if ns not in self.DATABASE_NAMESPACES:
                    try:
                        for d in self.client.list_deployments(ns):
                            deployments.append((d.metadata.name, d.status.replicas or 0, ns))
                    except Exception as e:
                        print(f"Error fetching deployments in namespace {ns}: {str(e)}")
                
                # Fetch statefulsets (prioritize for database namespaces)
                try:
                    for s in self.client.list_statefulsets(ns):
                        statefulsets.append((s.metadata.name, s.status.replicas or 0, ns))
                except Exception as e:
                        print(f"Error fetching statefulsets in namespace {ns}: {str(e)}")
                
                # Fetch services
                try:
                    for s in self.client.list_services(ns):
                        services.append((s.metadata.name, ns))
                except Exception as e:
                    print(f"Error fetching services in namespace {ns}: {str(e)}")
                
                # Fetch PVCs
                try:
                    for p in self.client.list_pvcs(ns):
                        pvcs.append((p.metadata.name, ns))
                except Exception as e:
                    print(f"Error fetching PVCs in namespace {ns}: {str(e)}")
                
                # Fetch ingresses
                try:
                    for i in self.client.list_ingresses(ns):
                        ingresses.append((i.metadata.name, ns))
                except Exception as e:
                    print(f"Error fetching ingresses in namespace {ns}: {str(e)}")
                
                # Fetch pods with status
                try:
                    for p in self.client.list_pods(ns):
                        pods.append((p.metadata.name, p.metadata.owner_references, ns, p.status.phase))
                except Exception as e:
                    print(f"Error fetching pods in namespace {ns}: {str(e)}")
                
                # Fetch secrets with status
                try:
                    for s in self.client.list_secrets(ns):
                        secrets.append((s.metadata.name, ns))
                except Exception as e:
                    print(f"Error fetching secrets in namespace {ns}: {str(e)}")
            except Exception as e:
                print(f"Error processing namespace {ns}: {str(e)}")
        return deployments, statefulsets, services, pvcs, ingresses, pods, secrets