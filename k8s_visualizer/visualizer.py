#visualizer.py
from graphviz import Digraph

class ResourceVisualizer:
    """Visualizes Kubernetes resources as a Graphviz diagram."""
    
    def __init__(self, output_file="gke_architecture", output_format="svg", node_shapes=None, namespace_colors=None):
        """Initialize the visualizer.
        
        Args:
            output_file (str): Base name for the output file.
            output_format (str): Output format (e.g., svg, png).
            node_shapes (dict): Custom shapes for resource types (e.g., {"Deployment": "box3d"}).
            namespace_colors (dict): Custom colors for namespaces (e.g., {"lamprell": "#FFFFFF"}).
        """
        self.output_file = output_file
        self.output_format = output_format
        self.node_shapes = node_shapes or {
            "Deployment": "box3d",
            "StatefulSet": "tab",
            "Service": "component",
            "PVC": "cylinder",
            "Ingress": "ellipse",
            "Pod": "box",
            "Secret": "folder"
        }
        self.namespace_colors = namespace_colors
        self.dot = Digraph("GKE_Architecture", format=output_format)
        self.dot.attr(
            rankdir="TB",
            bgcolor="#FDFDFD",
            fontname="Arial",
            fontsize="15",
            splines="polyline",
            concentrate="true",
            nodesep="1.4",
            ranksep="1.6"
        )
        # Add Cloud Load Balancer node
        self.dot.node("CloudLB", "Cloud Load Balancer", shape="box", style="filled", fillcolor="#FFCCCB")
    
    def build_diagram(self, deployments, statefulsets, services, pvcs, ingresses, pods, secrets, namespaces):
        """Build the diagram from collected resources.
        
        Args:
            deployments (list): List of (name, replicas, namespace) tuples.
            statefulsets (list): List of (name, replicas, namespace) tuples.
            services (list): List of (name, namespace) tuples.
            pvcs (list): List of (name, namespace) tuples.
            ingresses (list): List of (name, namespace) tuples.
            pods (list): List of (name, owner_references, namespace, status) tuples.
            secrets (list): List of (name, namespace) tuples.
            namespaces (list): List of namespaces.
        """
        ns_map = {ns: {"dep": [], "sts": [], "svc": [], "pvc": [], "ing": [], "pods": [], "sec": []} for ns in namespaces}
        dep_replicas = {}
        sts_replicas = {}
        
        # Process deployments
        for d, replica_count, ns in deployments:
            display_name, full_name = self._shorten(d)
            ns_map[ns]["dep"].append((display_name, full_name))
            dep_replicas[display_name] = replica_count
        
        # Process statefulsets
        for s, replica_count, ns in statefulsets:
            display_name, full_name = self._shorten(s)
            ns_map[ns]["sts"].append((display_name, full_name))
            sts_replicas[display_name] = replica_count
        
        # Process services
        for s, ns in services:
            display_name, full_name = self._shorten(s)
            ns_map[ns]["svc"].append((display_name, full_name))
        
        # Process PVCs
        for p, ns in pvcs:
            display_name, full_name = self._shorten(p)
            ns_map[ns]["pvc"].append((display_name, full_name))
        
        # Process ingresses
        for i, ns in ingresses:
            display_name, full_name = self._shorten(i)
            ns_map[ns]["ing"].append((display_name, full_name))
        
        # Process pods
        for pod_name, owners, ns, status in pods:
            owner_name = None
            owner_type = None
            for owner in owners or []:
                if owner.kind == "ReplicaSet":
                    owner_name = owner.name.rsplit("-", 1)[0]
                    owner_type = "Deployment"
                elif owner.kind == "StatefulSet":
                    owner_name = owner.name
                    owner_type = "StatefulSet"
            if owner_name and owner_type:
                display_pod, full_pod = self._shorten(pod_name)
                display_owner, _ = self._shorten(owner_name)
                ns_map[ns]["pods"].append((display_pod, display_owner, full_pod, status, owner_type))
        
        # Process secrets
        for s, ns in secrets:
            display_name, full_name = self._shorten(s)
            ns_map[ns]["sec"].append((display_name, full_name))
        
        # Build the diagram
        for ns, resources in ns_map.items():
            with self.dot.subgraph(name=f"cluster_{ns}") as cluster:
                if self.namespace_colors is None:  
                    self.namespace_colors = {}
                cluster.attr(label=f"Namespace: {ns}", style="filled", fillcolor=self.namespace_colors.get(ns, "#E6F3FF"))
                # Add ingress nodes
                for ing, full_ing in resources["ing"]:
                    cluster.node(f"{ns}_ing_{ing}", f"Ingress: {ing}", shape=self.node_shapes["Ingress"], fillcolor="#C8E6C9", style="filled", tooltip=full_ing)
                
                # Add service nodes
                for svc, full_svc in resources["svc"]:
                    cluster.node(f"{ns}_svc_{svc}", f"Service: {svc}", shape=self.node_shapes["Service"], fillcolor="#B2DFDB", style="filled", tooltip=full_svc)
                
                # Add deployment nodes
                for dep, full_dep in resources["dep"]:
                    replica_text = f"Deployment: {dep}\\nReplicas: {dep_replicas.get(dep, 0)}"
                    style = "filled,bold" if dep_replicas.get(dep, 0) == 0 else "filled"
                    cluster.node(f"{ns}_dep_{dep}", replica_text, shape=self.node_shapes["Deployment"], fillcolor="#FFF9C4", style=style, tooltip=full_dep)
                
                # Add statefulset nodes
                for sts, full_sts in resources["sts"]:
                    replica_text = f"StatefulSet: {sts}\\nReplicas: {sts_replicas.get(sts, 0)}"
                    style = "filled,bold" if sts_replicas.get(sts, 0) == 0 else "filled"
                    cluster.node(f"{ns}_sts_{sts}", replica_text, shape=self.node_shapes["StatefulSet"], fillcolor="#BBDEFB", style=style, tooltip=full_sts)
                
                # Add PVC nodes
                for pvc, full_pvc in resources["pvc"]:
                    cluster.node(f"{ns}_pvc_{pvc}", f"PVC: {pvc}", shape=self.node_shapes["PVC"], fillcolor="#FFECB3", style="filled", tooltip=full_pvc)
                
                # Add secret nodes
                for sec, full_sec in resources["sec"]:
                    cluster.node(f"{ns}_sec_{sec}", f"Secret: {sec}", shape=self.node_shapes["Secret"], fillcolor="#D3D3D3", style="filled", tooltip=full_sec)
                
                # Add pod nodes with status
                for pod, parent, full_pod, status, owner_type in resources["pods"]:
                    cluster.node(f"{ns}_pod_{pod}", f"Pod: {pod}\\nStatus: {status}", shape=self.node_shapes["Pod"], fillcolor="#E1BEE7", style="filled", tooltip=full_pod)
                    if owner_type == "Deployment":
                        cluster.edge(f"{ns}_dep_{parent}", f"{ns}_pod_{pod}")
                    elif owner_type == "StatefulSet":
                        cluster.edge(f"{ns}_sts_{parent}", f"{ns}_pod_{pod}")
                
                # Add edges with labels
                for ing, _ in resources["ing"]:
                    for svc, _ in resources["svc"]:
                        cluster.edge(f"{ns}_ing_{ing}", f"{ns}_svc_{svc}", label="routes to")
                
                for svc, _ in resources["svc"]:
                    for dep, _ in resources["dep"]:
                        if svc.replace("-service", "") in dep:
                            cluster.edge(f"{ns}_svc_{svc}", f"{ns}_dep_{dep}", label="exposes")
                    for sts, _ in resources["sts"]:
                        if svc.replace("-service", "") in sts:
                            cluster.edge(f"{ns}_svc_{svc}", f"{ns}_sts_{sts}", label="exposes")
                
                for dep, _ in resources["dep"]:
                    for pvc, _ in resources["pvc"]:
                        if pvc in dep:
                            cluster.edge(f"{ns}_dep_{dep}", f"{ns}_pvc_{pvc}", label="binds")
                    for sec, _ in resources["sec"]:
                        if sec in dep:
                            cluster.edge(f"{ns}_dep_{dep}", f"{ns}_sec_{sec}", label="uses")
                
                for sts, _ in resources["sts"]:
                    for pvc, _ in resources["pvc"]:
                        if pvc in sts:
                            cluster.edge(f"{ns}_sts_{sts}", f"{ns}_pvc_{pvc}", label="binds")
                    for sec, _ in resources["sec"]:
                        if sec in sts:
                            cluster.edge(f"{ns}_sts_{sts}", f"{ns}_sec_{sec}", label="uses")
                
                for ing, _ in resources["ing"]:
                    self.dot.edge("CloudLB", f"{ns}_ing_{ing}", label="routes to")
                
    def _shorten(self, name, max_len=30):
        """Shorten a name with line breaks for display and return full name for tooltip."""
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
    
    def render(self, view=True):
        """Render the diagram to a file.
        
        Args:
            view (bool): Whether to open the rendered file.
        """
        self.dot.render(self.output_file, view=view)