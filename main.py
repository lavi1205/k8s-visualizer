from k8s_visualizer.collector import ResourceCollector
from k8s_visualizer.visualizer import ResourceVisualizer
from k8s_visualizer.reporter import ReportGenerator, ExcelReportGenerator
import tkinter as tk
from k8s_visualizer.gui import K8sVisualizerGUI
def main():
    # Define namespaces to visualize
    # namespaces = ["lamprell", "lamprell-dev", "test-argocd", "redis-prod", "redis-nonprd", "mongodb", "rabbitmq", "monitor"]
    
    # # Initialize collector, visualizer, and reporter
    # collector = ResourceCollector(namespaces)
    # visualizer = ResourceVisualizer(output_file="gke_architecture", output_format="svg")
    # reporter = ExcelReportGenerator(output_file="gke_components_report.xlsx")
    
    # Collect resources
    # deployments, statefulsets, services, pvcs, ingresses, pods = collector.collect_summary()
    
    # Generate CSV report
    # reporter.generate_report(deployments, statefulsets, services, pvcs, ingresses, pods, namespaces)
    
    # Build and render diagram
    # visualizer.build_diagram(deployments, statefulsets, services, pvcs, ingresses, pods, namespaces)
    # visualizer.render(view=True)
    root = tk.Tk()
    app = K8sVisualizerGUI(root)
    app.run()


if __name__ == "__main__":
    main()
