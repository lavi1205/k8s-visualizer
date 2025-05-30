import csv
import xlsxwriter
from collections import Counter, defaultdict
class ReportGenerator:
    """Generates a CSV report of Kubernetes resources."""
    
    def __init__(self, output_file="gke_components_report.csv"):
        """Initialize the report generator.
        
        Args:
            output_file (str): Path to the output CSV file.
        """
        self.output_file = output_file
    
    def generate_report(self, deployments, statefulsets, services, pvcs, ingresses, pods, secrets, namespaces):
        """Generate a CSV report from collected resources.
        
        Args:
            deployments (list): List of (name, replicas, namespace) tuples.
            statefulsets (list): List of (name, replicas, namespace) tuples.
            services (list): List of (name, namespace) tuples.
            pvcs (list): List of (name, namespace) tuples.
            ingresses (list): List of (name, namespace) tuples.
            pods (list): List of (name, owner_references, namespace, status) tuples.
            namespaces (list): List of namespaces.
            secrets (list): List of secrets tuples.
        """
        # Prepare report data
        report_data = []
        
        # Process deployments
        for name, replicas, ns in deployments:
            report_data.append({
                "ComponentType": "Deployment",
                "Name": name,
                "Namespace": ns,
                "Replicas": replicas,
                "Status": "",
                "Parent": "",
                "RelatedComponents": ""
            })
        
        # Process statefulsets
        for name, replicas, ns in statefulsets:
            report_data.append({
                "ComponentType": "StatefulSet",
                "Name": name,
                "Namespace": ns,
                "Replicas": replicas,
                "Status": "",
                "Parent": "",
                "RelatedComponents": ""
            })
        
        # Process services
        for name, ns in services:
            related = []
            for dep_name, _, dep_ns in deployments:
                if dep_ns == ns and name.replace("-service", "") in dep_name:
                    related.append(f"Deployment:{dep_name}")
            for sts_name, _, sts_ns in statefulsets:
                if sts_ns == ns and name.replace("-service", "") in sts_name:
                    related.append(f"StatefulSet:{sts_name}")
            report_data.append({
                "ComponentType": "Service",
                "Name": name,
                "Namespace": ns,
                "Replicas": "",
                "Status": "",
                "Parent": "",
                "RelatedComponents": ";".join(related)
            })
        
        # Process PVCs
        for name, ns in pvcs:
            related = []
            for dep_name, _, dep_ns in deployments:
                if dep_ns == ns and name in dep_name:
                    related.append(f"Deployment:{dep_name}")
            for sts_name, _, sts_ns in statefulsets:
                if sts_ns == ns and name in sts_name:
                    related.append(f"StatefulSet:{sts_name}")
            report_data.append({
                "ComponentType": "PVC",
                "Name": name,
                "Namespace": ns,
                "Replicas": "",
                "Status": "",
                "Parent": "",
                "RelatedComponents": ";".join(related)
            })
        
        # Process ingresses
        for name, ns in ingresses:
            related = [f"Service:{svc_name}" for svc_name, svc_ns in services if svc_ns == ns]
            report_data.append({
                "ComponentType": "Ingress",
                "Name": name,
                "Namespace": ns,
                "Replicas": "",
                "Status": "",
                "Parent": "",
                "RelatedComponents": ";".join(related)
            })
        
        # Process pods
        for pod_name, owners, ns, status in pods:
            parent = ""
            for owner in owners or []:
                if owner.kind == "ReplicaSet":
                    parent = f"Deployment:{owner.name.rsplit('-', 1)[0]}"
                elif owner.kind == "StatefulSet":
                    parent = f"StatefulSet:{owner.name}"
            report_data.append({
                "ComponentType": "Pod",
                "Name": pod_name,
                "Namespace": ns,
                "Replicas": "",
                "Status": status,
                "Parent": parent,
                "RelatedComponents": ""
            })
        
        # Write to CSV
        headers = ["ComponentType", "Name", "Namespace", "Replicas", "Status", "Parent", "RelatedComponents"]
        with open(self.output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in report_data:
                writer.writerow(row)
        
        print(f"CSV report generated: {self.output_file}")



class ExcelReportGenerator:
    """Generates an Excel report of Kubernetes resources with charts."""
    
    def __init__(self, output_file="gke_components_report.xlsx"):
        self.output_file = output_file
    
    def generate_report(self, deployments, statefulsets, services, pvcs, ingresses, pods, namespaces):
        workbook = xlsxwriter.Workbook(self.output_file)
        worksheet = workbook.add_worksheet("Resources")
        bold = workbook.add_format({'bold': True})

        # Headers
        headers = ["ComponentType", "Name", "Namespace", "Replicas", "Status", "Parent", "RelatedComponents"]
        worksheet.write_row(0, 0, headers, bold)
        
        row = 1
        for name, replicas, ns in deployments:
            worksheet.write_row(row, 0, ["Deployment", name, ns, replicas, "", "", ""])
            row += 1
        for name, replicas, ns in statefulsets:
            worksheet.write_row(row, 0, ["StatefulSet", name, ns, replicas, "", "", ""])
            row += 1
        for name, ns in services:
            worksheet.write_row(row, 0, ["Service", name, ns, "", "", "", ""])
            row += 1
        for name, ns in pvcs:
            worksheet.write_row(row, 0, ["PVC", name, ns, "", "", "", ""])
            row += 1
        for name, ns in ingresses:
            worksheet.write_row(row, 0, ["Ingress", name, ns, "", "", "", ""])
            row += 1
        for pod_name, owners, ns, status in pods:
            parent = ""
            for owner in owners or []:
                if owner.kind == "ReplicaSet":
                    parent = f"Deployment:{owner.name.rsplit('-', 1)[0]}"
                elif owner.kind == "StatefulSet":
                    parent = f"StatefulSet:{owner.name}"
            worksheet.write_row(row, 0, ["Pod", pod_name, ns, "", status, parent, ""])
            row += 1

        # Component type counts (overall)
        component_counts = Counter({
            "Deployment": len(deployments),
            "StatefulSet": len(statefulsets),
            "Service": len(services),
            "PVC": len(pvcs),
            "Ingress": len(ingresses),
            "Pod": len(pods),
            "Namespace": len(namespaces),
        })

        chart_start_row = row + 2
        worksheet.write(chart_start_row, 0, "ResourceType", bold)
        worksheet.write(chart_start_row, 1, "Count", bold)
        for idx, (k, v) in enumerate(component_counts.items()):
            worksheet.write(chart_start_row + 1 + idx, 0, k)
            worksheet.write(chart_start_row + 1 + idx, 1, v)

        # Colors
        colors = ['#4F81BD', '#C0504D', '#9BBB59', '#8064A2', '#4BACC6', '#F79646', '#7F7F7F']

        # Overall pie chart
        pie_chart = workbook.add_chart({'type': 'pie'})
        pie_chart.add_series({
            'name': 'Resource Distribution',
            'categories': ['Resources', chart_start_row + 1, 0, chart_start_row + len(component_counts), 0],
            'values':     ['Resources', chart_start_row + 1, 1, chart_start_row + len(component_counts), 1],
            'data_labels': {'percentage': True, 'value': True, 'leader_lines': True},
            'points': [{'fill': {'color': c}} for c in colors]
        })
        pie_chart.set_title({
            'name': 'Kubernetes Resource Distribution',
            'name_font': {'bold': True, 'italic': True, 'size': 14, 'color': '#1F497D'},
        })
        pie_chart.set_legend({'position': 'bottom'})
        pie_chart.set_chartarea({'border': {'color': 'black'}, 'fill': {'color': '#F2F2F2'}})
        worksheet.insert_chart('H2', pie_chart)

        # Namespace-wise counts
        ns_component_counts = defaultdict(lambda: Counter())
        for name, _, ns in deployments:
            ns_component_counts[ns]['Deployment'] += 1
        for name, _, ns in statefulsets:
            ns_component_counts[ns]['StatefulSet'] += 1
        for name, ns in services:
            ns_component_counts[ns]['Service'] += 1
        for name, ns in pvcs:
            ns_component_counts[ns]['PVC'] += 1
        for name, ns in ingresses:
            ns_component_counts[ns]['Ingress'] += 1
        for name, _, ns, _ in pods:
            ns_component_counts[ns]['Pod'] += 1

        # Add per-namespace summary and column charts
        ns_chart_start = chart_start_row + len(component_counts) + 5
        for ns_idx, (ns, counts) in enumerate(ns_component_counts.items()):
            ns_row = ns_chart_start + ns_idx * 15
            worksheet.write(ns_row, 0, f"Namespace: {ns}", bold)
            worksheet.write(ns_row + 1, 0, "ResourceType", bold)
            worksheet.write(ns_row + 1, 1, "Count", bold)
            
            for i, (rtype, count) in enumerate(counts.items()):
                worksheet.write(ns_row + 2 + i, 0, rtype)
                worksheet.write(ns_row + 2 + i, 1, count)
            
            # Per-namespace bar chart
            ns_chart = workbook.add_chart({'type': 'column'})
            ns_chart.add_series({
                'name': f"{ns} Resources",
                'categories': ['Resources', ns_row + 2, 0, ns_row + 1 + len(counts), 0],
                'values': ['Resources', ns_row + 2, 1, ns_row + 1 + len(counts), 1],
                'points': [{'fill': {'color': colors[i % len(colors)]}} for i in range(len(counts))]
            })
            ns_chart.set_title({'name': f'Resources in {ns}'})
            ns_chart.set_legend({'none': True})
            worksheet.insert_chart(ns_row, 4, ns_chart)

        workbook.close()
        print(f"Excel report with charts generated: {self.output_file}")
