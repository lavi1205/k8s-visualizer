from k8s_visualizer.collector import ResourceCollector
from k8s_visualizer.visualizer import ResourceVisualizer
from k8s_visualizer.reporter import ReportGenerator, ExcelReportGenerator
import tkinter as tk
from ttkthemes import ThemedTk
from k8s_visualizer.gui import K8sVisualizerGUI
def main():
    # # Define namespaces to visualize
    # namespaces = ["lamprell", "lamprell-dev", "test-argocd", "redis-prod", "redis-nonprd", "mongodb", "rabbitmq", "monitor"]
    # database_namespaces = {"redis-prod", "redis-nonprd", "mongodb", "rabbitmq"}
    # # Initialize collector, visualizer, and reporter
    # collector = ResourceCollector(namespaces, database_namespaces)
    # visualizer = ResourceVisualizer(output_file="gke_architecture", output_format="svg")
    # reporter = ExcelReportGenerator(output_file="gke_components_report.xlsx")
    # csv = ReportGenerator(output_file="gke_components_report.csv")
    # # Collect resources
    # deployments, statefulsets, services, pvcs, ingresses, pods, secrets = collector.collect_summary()
    
    # # Generate CSV report
    # reporter.generate_report(deployments, statefulsets, services, pvcs, ingresses, pods,secrets, namespaces)
    # csv.generate_report(deployments, statefulsets, services, pvcs, ingresses, pods, secrets, namespaces)
    # # Build and render diagram
    # visualizer.build_diagram(deployments, statefulsets, services, pvcs, ingresses, pods, secrets, namespaces)
    # visualizer.render(view=True)
    root = tk.Tk()
    app = K8sVisualizerGUI(root)
    app.run()


if __name__ == "__main__":
    main()
