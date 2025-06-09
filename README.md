# Kubernetes Architecture Visualizer

## Project Overview
The **Kubernetes Architecture Visualizer** is a sophisticated Python-based tool designed to streamline the exploration, visualization, and documentation of Kubernetes cluster resources. It leverages the Kubernetes Python client to interact with cluster APIs, collecting comprehensive data on resources such as Deployments, StatefulSets, Services, Persistent Volume Claims (PVCs), Ingresses, Pods, and Secrets. The tool offers a feature-rich Tkinter-based GUI for intuitive configuration, enabling users to generate Graphviz-powered SVG diagrams, detailed CSV and Excel reports with embedded charts, and export resource manifests as YAML files. It is optimized for DevOps engineers, Kubernetes administrators, and architects seeking to analyze and document cluster topologies with customizable visualizations and robust error handling.

## Key Features
- **Dynamic Resource Collection**: Fetches real-time data on Kubernetes resources across specified namespaces, with special handling for database-centric namespaces (e.g., Redis, MongoDB).
- **Interactive Visualization**: Generates SVG diagrams using Graphviz, depicting resource relationships (e.g., Ingress-to-Service, Service-to-Deployment) with customizable node shapes and namespace-specific color schemes.
- **Comprehensive Reporting**:
  - **CSV Reports**: Tabular summaries of resources, including ComponentType, Name, Namespace, Replicas, Status, Parent, and RelatedComponents.
  - **Excel Reports**: Enhanced with pie charts for cluster-wide resource distribution and per-namespace bar charts for detailed analysis.
- **YAML Export**: Exports Kubernetes resource manifests and namespace definitions as YAML files for backup, auditing, or redeployment.
- **Advanced GUI**:
  - Scrollable namespace and resource selection with "Select All" options.
  - Customizable node shapes (e.g., box, cylinder, ellipse) and namespace colors for tailored visualizations.
  - Real-time progress bars and status logs for operation feedback.
  - File browsing for output paths and validation for write permissions.
- **Robust Error Handling**: Gracefully manages Kubernetes API errors, file access issues, and invalid configurations with user-friendly error messages.
- **Cross-Platform Compatibility**: Supports Windows, Linux, and macOS with platform-specific file handling and application launching.

## Prerequisites
To run the Kubernetes Architecture Visualizer, ensure the following:
- **Python Version**: 3.8 or higher (recommended for compatibility with dependencies).
- **Kubernetes Cluster Access**: A valid kubeconfig file (default: `~/.kube/config`) or a specified path with appropriate permissions.
- **System Dependencies**:
  - Graphviz (`dot` executable) installed for SVG rendering.
    - **Ubuntu/Debian**: `sudo apt-get install graphviz`
    - **macOS**: `brew install graphviz`
    - **Windows**: Install via [Graphviz website](https://graphviz.org/download/) and add to PATH.
- **Python Dependencies**:
  ```bash
  pip install kubernetes graphviz xlsxwriter pyyaml ttkthemes
  ```
  - `kubernetes`: For API interactions.
  - `graphviz`: For rendering SVG diagrams.
  - `xlsxwriter`: For generating Excel reports with charts.
  - `pyyaml`: For YAML export functionality.
  - `ttkthemes`: For a modern, themed Tkinter GUI.
  - `tkinter`: Included with Python for GUI rendering.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/lavi1205/k8s-visualizer.git
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure Graphviz is installed and accessible in your system PATH.
4. Verify kubeconfig is configured for your Kubernetes cluster.

## Project Structure
The project is modular, with each component handling specific functionality:
- **`client.py`**: Implements `KubernetesClient`, a wrapper for the Kubernetes Python client, providing methods to list namespaces, deployments, statefulsets, services, PVCs, ingresses, pods, and secrets. Handles kubeconfig loading and API exceptions.
- **`collector.py`**: Defines `ResourceCollector`, which aggregates resource data from specified namespaces, supports database namespace prioritization, and includes a `shorten` method for readable resource names in visualizations.
- **`visualizer.py`**: Contains `ResourceVisualizer`, which constructs Graphviz-based SVG diagrams with customizable node shapes, namespace colors, and relationship edges (e.g., "exposes", "binds", "routes to").
- **`reporter.py`**: Includes `ReportGenerator` for CSV reports and `ExcelReportGenerator` for Excel reports with embedded charts, summarizing resource details and relationships.
- **`gui.py`**: Implements `K8sVisualizerGUI`, a Tkinter-based interface with scrollable namespace/resource selection, color/shape customization, file browsing, progress bars, and status logging.
- **`main.py`**: Serves as the entry point, initializing the GUI or supporting programmatic execution with predefined namespaces (commented out for flexibility).

## Usage
### GUI-Based Usage
1. Run the application:
   ```bash
   python main.py
   ```
2. **GUI Workflow**:
   - **Namespace Selection**: Choose namespaces from the scrollable list and mark database namespaces (e.g., for statefulset-heavy workloads like MongoDB).
   - **Resource Selection**: Select resource types (Deployments, Pods, etc.) to include, with a "Select All Resources" option.
   - **Customization**: Adjust node shapes (e.g., "box3d" for Deployments) and namespace colors via dropdowns.
   - **Output Configuration**: Specify paths for SVG, CSV, Excel, and YAML outputs using file/directory browsers.
   - **Actions**:
     - **Generate Visualization**: Creates an SVG diagram of selected resources.
     - **Generate CSV/Excel Report**: Produces detailed reports with resource summaries and charts (Excel).
     - **Export YAML**: Saves resource manifests to a specified directory.
     - **Open Outputs**: Launches generated SVG, CSV, or Excel files in the default application.
   - **Status Monitoring**: View real-time logs and progress in the GUI's status window.

### Programmatic Usage
Uncomment the code in `main.py` to run programmatically:
```python
from k8s_visualizer.collector import ResourceCollector
from k8s_visualizer.visualizer import ResourceVisualizer
from k8s_visualizer.reporter import ReportGenerator, ExcelReportGenerator

namespaces = ["lamprell", "redis-prod", "mongodb"]
database_namespaces = {"redis-prod", "mongodb"}
collector = ResourceCollector(namespaces, database_namespaces)
visualizer = ResourceVisualizer(
    output_file="k8s_architecture",
    output_format="svg",
    node_shapes={"Deployment": "box3d", "Pod": "ellipse"},
    namespace_colors={"lamprell": "#B3E5FC", "redis-prod": "#C8E6C9"}
)
reporter = ExcelReportGenerator(output_file="k8s_components_report.xlsx")
csv_reporter = ReportGenerator(output_file="k8s_components_report.csv")

deployments, statefulsets, services, pvcs, ingresses, pods, secrets = collector.collect_summary()
visualizer.build_diagram(deployments, statefulsets, services, pvcs, ingresses, pods, secrets, namespaces)
visualizer.render(view=True)
reporter.generate_report(deployments, statefulsets, services, pvcs, ingresses, pods, secrets, namespaces)
csv_reporter.generate_report(deployments, statefulsets, services, pvcs, ingresses, pods, secrets, namespaces)
```

## Configuration
- **Kubeconfig**: Specify a custom kubeconfig path in `client.py` or `collector.py` via the `kubeconfig_path` parameter.
- **Node Shapes**: Customize in `gui.py` (`node_shapes`) or programmatically in `visualizer.py`. Supported shapes: `box`, `box3d`, `ellipse`, `circle`, `tab`, `component`, `cylinder`, `folder`.
- **Namespace Colors**: Define in `gui.py` (`color_options`) or programmatically in `visualizer.py`. Uses hex color codes (e.g., `#B3E5FC` for Light Blue).
- **Output Paths**: Configurable via GUI or programmatically (`output_file` in `visualizer.py`, `reporter.py`).

## Output Details
- **SVG Diagram**:
  - Visualizes namespaces as Graphviz clusters with customizable colors.
  - Displays resources as nodes with shapes (e.g., cylinder for PVCs) and tooltips for full names.
  - Shows relationships (e.g., "exposes" for Service-to-Deployment, "binds" for Deployment-to-PVC).
  - Includes a "Cloud Load Balancer" node for Ingress routing.
- **CSV Report**:
  - Columns: ComponentType, Name, Namespace, Replicas, Status, Parent, RelatedComponents.
  - Captures resource relationships (e.g., Service exposing a Deployment).
- **Excel Report**:
  - Similar to CSV, with additional sheets for resource data.
  - Includes:
    - ascendancy="8feda1e5-f9e4-4f6e-9f3e-0d6e6e9e9e9e" contentType="text/plain">Pie chart for cluster-wide resource distribution.
    - Per-namespace bar charts for resource counts.
- **YAML Export**:
  - Generates one YAML file per resource and namespace.
  - Files named as `<namespace>_<resource_name>_<resource_type>.yaml` (e.g., `lamprell_my-app_deployment.yaml`).
  - Includes namespace manifests (e.g., `lamprell_namespace.yaml`).

## Advanced Features
- **Database Namespace Handling**: Prioritizes StatefulSets over Deployments in database namespaces, ideal for stateful workloads.
- **Threaded Visualization**: Runs diagram generation in a separate thread to keep the GUI responsive, with a progress bar for user feedback.
- **Tooltip Support**: Full resource names are displayed as tooltips in SVG diagrams for long names.
- **Error Recovery**: Automatically falls back to the `default` namespace if no namespaces are found or API calls fail.
- **Custom Styling**: Uses `ttkthemes` for a modern GUI look and custom checkbox styles for database namespaces.

## Troubleshooting
- **No Namespaces Found**: Ensure kubeconfig is valid and has cluster access. Check API server connectivity.
- **Graphviz Rendering Errors**: Verify Graphviz is installed and `dot` is in the system PATH.
- **File Permission Issues**: Ensure write permissions for output directories. The GUI tests write access before generation.
- **Long Resource Names**: Automatically shortened with line breaks for readability, with full names in tooltips.
- **Large Clusters**: For clusters with many resources, consider increasing `nodesep` and `ranksep` in `visualizer.py` for better diagram clarity.

## Limitations
- **Cluster Size**: Large clusters with thousands of resources may produce complex diagrams, potentially requiring manual layout adjustments in Graphviz.
- **API Rate Limits**: Heavy API usage may hit rate limits in large clusters; consider increasing timeouts in `client.py`.
- **Dependencies**: Requires external Graphviz installation, which may not be pre-installed on all systems.
- **Excel Charts**: Limited to `xlsxwriter` capabilities; complex customizations may require additional libraries.

## Contributing
Contributions are encouraged! To contribute:
1. Fork the repository and create a feature branch (`git checkout -b feature/new-feature`).
2. Ensure code adheres to PEP 8 style guidelines (use `flake8` or `pylint`).
3. Add unit tests for new functionality using `unittest` or `pytest`.
4. Submit a pull request with a clear description of changes and test results.
5. Address any feedback during code review.

Report bugs or suggest features via the GitHub Issues page.

## License
Licensed under the [MIT License](LICENSE). See the `LICENSE` file for details.

## Roadmap
- Add support for additional Kubernetes resources (e.g., ConfigMaps, Jobs).
- Implement real-time resource monitoring with live updates in the GUI.
- Enhance visualization with interactive SVG outputs (e.g., zoomable diagrams).
- Support Helm chart detection and visualization.
- Add command-line interface (CLI) for non-GUI usage.

## Acknowledgments
- Built with the [Kubernetes Python Client](https://github.com/kubernetes-client/python).
- Visualizations powered by [Graphviz](https://graphviz.org/).
- Excel reports generated with [XlsxWriter](https://xlsxwriter.readthedocs.io/).
- GUI enhanced by [ttkthemes](https://ttkthemes.readthedocs.io/).

For support, contact the maintainers via GitHub Issues or contribute to the project to help improve it!