# Kubernetes Architecture Visualizer

This project generates a visual diagram of Kubernetes resources (Deployments, StatefulSets, Services, PVCs, Ingresses, and Pods) in a Google Kubernetes Engine (GKE) cluster using Graphviz. It is designed to visualize resources across specified namespaces, with enhanced features like distinct namespace colors, pod status, and StatefulSet support for database workloads (e.g., Redis, MongoDB, RabbitMQ).

## Prerequisites

- **Python 3.8+**: Ensure Python is installed.
- **Google Cloud CLI (`gcloud`)**: Required for GKE authentication and kubeconfig setup.
- **Graphviz**: Required for rendering the diagram.
- **Kubernetes Cluster Access**: A GKE cluster with sufficient permissions to list resources (Deployments, StatefulSets, Services, PVCs, Ingresses, Pods).
- **Dependencies**: Listed in `requirements.txt` (Kubernetes Python client, Graphviz).

## Installation

### On Windows

1. **Install Python**:
   - Download and install Python 3.8+ from [python.org](https://www.python.org/downloads/windows/).
   - Ensure `python` and `pip` are added to your PATH during installation.

2. **Install Graphviz**:
   - Download the Graphviz installer from [graphviz.org](https://graphviz.org/download/).
   - Install Graphviz and add its `bin` directory (e.g., `C:\Program Files\Graphviz\bin`) to your system PATH.
   - Verify installation:
     ```bash
     dot -V
     ```

3. **Install Google Cloud CLI**:
   - Download the `gcloud` installer from [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install#windows).
   - Run the installer and follow the prompts.
   - Initialize `gcloud`:
     ```bash
     gcloud init
     ```
   - Log in with your Google Cloud account and select your project.

4. **Install Python Dependencies**:
   - Navigate to the project directory:
     ```bash
     cd path\to\k8s-visualizer
     ```
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

### On Linux

1. **Install Python**:
   - Install Python 3.8+ using your package manager (e.g., for Ubuntu):
     ```bash
     sudo apt update
     sudo apt install python3 python3-pip
     ```
   - Verify:
     ```bash
     python3 --version
     pip3 --version
     ```

2. **Install Graphviz**:
   - Install Graphviz (e.g., for Ubuntu):
     ```bash
     sudo apt install graphviz
     ```
   - Verify:
     ```bash
     dot -V
     ```

3. **Install Google Cloud CLI**:
   - Follow the instructions for your Linux distribution at [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install#linux).
   - Example for Ubuntu:
     ```bash
     sudo apt update
     sudo apt install apt-transport-https ca-certificates gnupg
     echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
     curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
     sudo apt update && sudo apt install google-cloud-sdk
     ```
   - Initialize `gcloud`:
     ```bash
     gcloud init
     ```
   - Log in with your Google Cloud account and select your project.

4. **Install Python Dependencies**:
   - Navigate to the project directory:
     ```bash
     cd /path/to/k8s-visualizer
     ```
   - Install dependencies:
     ```bash
     pip3 install -r requirements.txt
     ```

## Google Cloud Authentication and Permissions

1. **Authenticate with GKE**:
   - Ensure you have a GKE cluster running.
   - Authenticate with your cluster to generate a kubeconfig file:
     ```bash
     gcloud container clusters get-credentials <CLUSTER_NAME> --region <REGION> --project <PROJECT_ID>
     ```
     Replace `<CLUSTER_NAME>`, `<REGION>`, and `<PROJECT_ID>` with your cluster details.

2. **Verify Permissions**:
   - Ensure your Google Cloud account or service account has the necessary IAM roles to access Kubernetes resources:
     - Minimum required roles: `roles/container.viewer` or higher (e.g., `roles/container.admin` for full access).
     - Example to grant a role to your account:
       ```bash
       gcloud projects add-iam-policy-binding <PROJECT_ID> \
         --member "user:<YOUR_EMAIL>" \
         --role "roles/container.viewer"
       ```
   - Verify access by listing pods:
     ```bash
     kubectl get pods -A
     ```
   - If you encounter errors, ensure your kubeconfig is correctly configured and your account has permissions to list Deployments, StatefulSets, Services, PVCs, Ingresses, and Pods.

## Running the Script

1. **Clone or Set Up the Project**:
   - If using a repository, clone it:
     ```bash
     git clone <REPO_URL>
     cd k8s-visualizer
     ```
   - Alternatively, ensure all project files (`main.py`, `k8s_visualizer/`, `requirements.txt`) are in the `k8s-visualizer` directory.

2. **Run the Script**:
   - On Windows:
     ```bash
     python main.py
     ```
   - On Linux:
     ```bash
     python3 main.py
     ```
   - This generates `gke_architecture.svg` in the project directory, visualizing resources across the specified namespaces (`lamprell`, `lamprell-dev`, `test-argocd`, `redis-prod`, `redis-nonprd`, `mongodb`, `rabbitmq`, `monitor`).
   - The diagram includes:
     - Deployments (non-database namespaces) and StatefulSets (database namespaces: `redis-prod`, `redis-nonprd`, `mongodb`, `rabbitmq`).
     - Services, PVCs, Ingresses, and Pods.
     - Distinct colors for namespaces, wrapped labels, tooltips, pod status, edge labels, and zero-replica highlighting.

3. **View the Output**:
   - Open `gke_architecture.svg` in a web browser or SVG viewer that supports tooltips (e.g., Chrome, Firefox).
   - The diagram shows namespaces as clusters, with StatefulSets in database namespaces using a `tab` shape and `#BBDEFB` color.

## Troubleshooting

- **Kubeconfig Errors**: Ensure your kubeconfig file is correctly set up and points to the right cluster. Run `kubectl cluster-info` to verify.
- **Permission Denied**: Check your IAM roles and ensure your account has `container.viewer` or higher permissions.
- **Graphviz Not Found**: Verify Graphviz is installed and its `bin` directory is in your PATH. Run `dot -V` to confirm.
- **No Resources Fetched**: Ensure the specified namespaces exist in your cluster. Run `kubectl get namespaces` to verify.
- **SVG Not Displaying**: Ensure the output file (`gke_architecture.svg`) is generated and try opening it in a different browser or SVG viewer.

## Customization

- **Change Namespaces**: Modify the `namespaces` list in `main.py` to visualize different namespaces.
- **Adjust Styling**: Edit `NAMESPACE_COLORS` or node attributes in `k8s_visualizer/visualizer.py` to customize colors or shapes.
- **Add Resources**: Extend `k8s_visualizer/client.py` and `k8s_visualizer/collector.py` to fetch additional resources (e.g., ConfigMaps, Secrets).

For issues or contributions, please contact the project maintainer or open an issue in the repository (if applicable).