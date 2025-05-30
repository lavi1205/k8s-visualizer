import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import yaml
from .collector import ResourceCollector
from .visualizer import ResourceVisualizer
from .reporter import ReportGenerator
from .client import KubernetesClient

class K8sVisualizerGUI:
    """GUI for generating Kubernetes visualizations and reports."""
    
    def __init__(self, root):
        """Initialize the GUI.
        
        Args:
            root: Tkinter root window.
        """
        self.root = root
        self.root.title("Kubernetes Architecture Visualizer")
        self.root.geometry("600x800")  # Increased size for new export section
        
        # Initialize components
        self.collector = None
        self.visualizer = None
        self.reporter = None
        self.namespace_vars = {}  # For checkbox states
        self.namespaces = []  # To store all namespaces
        
        # Available shapes and colors
        self.node_shapes = ["box", "box3d", "ellipse", "circle", "tab", "component", "cylinder"]
        self.color_options = {
            "Light Blue": "#B3E5FC", "Light Green": "#C8E6C9", "Light Red": "#FFCDD2",
            "Light Yellow": "#FFECB3", "Light Purple": "#D1C4E9", "Light Cyan": "#B2DFDB",
            "Light Lime": "#F0F4C3", "Light Orange": "#FFCCBC", "Light Gray": "#E6F3FF"
        }
        
        # GUI elements
        self.shape_vars = {}
        self.color_vars = {}  # Holds the StringVar for each namespace's Combobox
        self.selected_colors = {}  # Persistent storage for selected colors
        self.color_frame = None
        
        # Create GUI elements
        self.create_widgets()
    
    def create_widgets(self):
        """Create GUI elements."""
        # Main frame for better layout management
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Namespace selection with scrollable checkboxes
        tk.Label(main_frame, text="Select Namespaces:").grid(row=0, column=0, sticky="w", pady=5)
        
        # Create a frame to hold the Canvas and Scrollbar for namespaces
        namespace_container = ttk.Frame(main_frame)
        namespace_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        main_frame.grid_rowconfigure(1, weight=0)  # Prevent row 1 from expanding
        
        canvas = tk.Canvas(namespace_container, height=150, highlightthickness=0)  # Fixed height, no border
        scrollbar = ttk.Scrollbar(namespace_container, orient=tk.VERTICAL, command=canvas.yview)
        self.namespace_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Embed frame in canvas
        canvas_frame = canvas.create_window((0, 0), window=self.namespace_frame, anchor="nw")
        
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_frame, width=event.width)
        
        def on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.namespace_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<MouseWheel>", on_mouse_wheel)  # For Windows
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # For Linux: scroll up
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # For Linux: scroll down
        
        # Fetch namespaces
        try:
            client = KubernetesClient()
            self.namespaces = client.list_namespaces()
            if not self.namespaces:
                messagebox.showwarning("Warning", "No namespaces found in the cluster.")
                self.namespaces = ["default"]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch namespaces: {str(e)}")
            self.namespaces = ["default"]
        
        # Add Select All checkbox
        self.select_all_var = tk.IntVar()
        ttk.Checkbutton(self.namespace_frame, text="Select All", variable=self.select_all_var, command=self.toggle_select_all).grid(row=0, column=0, sticky="w", pady=2)
        
        # Populate checkboxes for namespaces
        for idx, ns in enumerate(sorted(self.namespaces)):
            var = tk.IntVar()
            self.namespace_vars[ns] = var
            chk = ttk.Checkbutton(self.namespace_frame, text=ns, variable=var, command=self.update_color_options)
            chk.grid(row=idx + 1, column=0, sticky="w", pady=2)
        
        # Add separator to clearly distinguish sections
        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, sticky="ew", pady=10)
        
        # Styling options
        tk.Label(main_frame, text="Node Shapes:").grid(row=3, column=0, sticky="w", pady=5)
        shape_frame = ttk.Frame(main_frame)
        shape_frame.grid(row=4, column=0, sticky="ew", pady=5)
        
        for idx, resource in enumerate(["Deployment", "StatefulSet", "Service", "PVC", "Ingress", "Pod"]):
            ttk.Label(shape_frame, text=f"{resource}:").grid(row=idx, column=0, sticky="w")
            var = tk.StringVar(value=ResourceVisualizer().node_shapes[resource])
            self.shape_vars[resource] = var
            ttk.Combobox(shape_frame, textvariable=var, values=self.node_shapes, state="readonly", width=15).grid(row=idx, column=1, sticky="ew")
            shape_frame.grid_columnconfigure(1, weight=1)
        
        # Namespace colors with scrollable section
        tk.Label(main_frame, text="Namespace Colors:").grid(row=5, column=0, sticky="w", pady=5)
        
        # Create a frame to hold the Canvas and Scrollbar for colors
        color_container = ttk.Frame(main_frame)
        color_container.grid(row=6, column=0, sticky="nsew", pady=5)
        main_frame.grid_rowconfigure(6, weight=0)  # Prevent row 6 from expanding
        
        color_canvas = tk.Canvas(color_container, height=150, highlightthickness=0)
        color_scrollbar = ttk.Scrollbar(color_container, orient=tk.VERTICAL, command=color_canvas.yview)
        self.color_frame = ttk.Frame(color_canvas)
        
        color_canvas.configure(yscrollcommand=color_scrollbar.set)
        color_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        color_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Embed frame in canvas
        color_canvas_frame = color_canvas.create_window((0, 0), window=self.color_frame, anchor="nw")
        
        def configure_color_canvas(event):
            color_canvas.configure(scrollregion=color_canvas.bbox("all"))
            color_canvas.itemconfig(color_canvas_frame, width=event.width)
        
        def on_color_mouse_wheel(event):
            color_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.color_frame.bind("<Configure>", configure_color_canvas)
        color_canvas.bind("<MouseWheel>", on_color_mouse_wheel)  # For Windows
        color_canvas.bind("<Button-4>", lambda e: color_canvas.yview_scroll(-1, "units"))  # For Linux: scroll up
        color_canvas.bind("<Button-5>", lambda e: color_canvas.yview_scroll(1, "units"))   # For Linux: scroll down
        
        self.update_color_options()  # Initial population
        
        # SVG output file
        tk.Label(main_frame, text="SVG Output File:").grid(row=7, column=0, sticky="w", pady=5)
        self.svg_entry = ttk.Entry(main_frame, width=50)
        self.svg_entry.insert(0, "k8s_architecture.svg")
        self.svg_entry.grid(row=8, column=0, sticky="ew", pady=5)
        
        # CSV output file
        tk.Label(main_frame, text="CSV Report File:").grid(row=9, column=0, sticky="w", pady=5)
        self.csv_entry = ttk.Entry(main_frame, width=50)
        self.csv_entry.insert(0, "k8s_components_report.csv")
        self.csv_entry.grid(row=10, column=0, sticky="ew", pady=5)
        
        # YAML export directory
        tk.Label(main_frame, text="YAML Export Directory:").grid(row=11, column=0, sticky="w", pady=5)
        self.yaml_export_entry = ttk.Entry(main_frame, width=50)
        self.yaml_export_entry.insert(0, "k8s_yaml_export")
        self.yaml_export_entry.grid(row=12, column=0, sticky="ew", pady=5)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=13, column=0, sticky="ew", pady=10)
        ttk.Button(button_frame, text="Generate Visualization", command=self.generate_visualization).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Generate CSV Report", command=self.generate_report).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Export YAML", command=self.export_yaml).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Open SVG", command=self.open_svg).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Open CSV", command=self.open_csv).grid(row=0, column=4, padx=5)
        button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", wraplength=550)
        self.status_label.grid(row=14, column=0, sticky="ew", pady=10)
        main_frame.grid_rowconfigure(14, weight=1)
        
        # Ensure window resizes properly
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
    
    def toggle_select_all(self):
        """Toggle all namespace checkboxes based on Select All state."""
        select_all = self.select_all_var.get()
        for var in self.namespace_vars.values():
            var.set(select_all)
        self.update_color_options()
    
    def update_color_options(self):
        """Update the Namespace Colors section based on selected namespaces, preserving existing colors."""
        # Get selected namespaces
        selected_namespaces = [ns for ns, var in self.namespace_vars.items() if var.get()]
        if not selected_namespaces:
            selected_namespaces = [self.namespaces[0]] if self.namespaces else []  # Default to first if none selected
        
        # Sort selected namespaces
        selected_namespaces = sorted(selected_namespaces)
        
        # Clear existing color widgets
        for widget in self.color_frame.winfo_children():
            widget.destroy()
        self.color_vars.clear()
        
        # Populate color options for selected namespaces
        for idx, ns in enumerate(selected_namespaces):
            # Create label for namespace
            ttk.Label(self.color_frame, text=f"{ns}:").grid(row=idx, column=0, sticky="w")
            
            # Restore previously selected color or default to Light Gray
            previous_color = self.selected_colors.get(ns, "Light Gray")
            
            # Create StringVar and Combobox
            var = tk.StringVar(value=previous_color)
            self.color_vars[ns] = var
            
            # Create Combobox with all available colors
            combobox = ttk.Combobox(self.color_frame, textvariable=var, values=list(self.color_options.keys()), state="readonly", width=15)
            combobox.grid(row=idx, column=1, sticky="ew")
            
            # Bind the selection event to update selected_colors
            combobox.bind("<<ComboboxSelected>>", lambda event, namespace=ns: self.update_selected_color(namespace, self.color_vars[namespace].get()))
            
            self.color_frame.grid_columnconfigure(1, weight=1)
    
    def update_selected_color(self, namespace, color):
        """Update the persistently stored color for a namespace.
        
        Args:
            namespace (str): The namespace name.
            color (str): The selected color.
        """
        self.selected_colors[namespace] = color
    
    def export_yaml(self):
        """Export YAML files for all resources in selected namespaces."""
        try:
            selected_namespaces = [ns for ns, var in self.namespace_vars.items() if var.get()]
            if not selected_namespaces:
                messagebox.showwarning("Warning", "Please select at least one namespace.")
                return
            
            export_dir = self.yaml_export_entry.get()
            if not export_dir:
                export_dir = "k8s_yaml_export"
            
            # Create export directory if it doesn't exist
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            client = KubernetesClient()
            self.collector = ResourceCollector(selected_namespaces)
            
            # Fetch all resources
            deployments, statefulsets, services, pvcs, ingresses, pods = self.collector.collect_resources()
            
            # Export namespace manifests
            for ns in selected_namespaces:
                ns_manifest = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": ns}}
                with open(os.path.join(export_dir, f"{ns}_namespace.yaml"), "w") as f:
                    yaml.dump(ns_manifest, f)
            
            # Export resource manifests with error handling for metadata
            resource_types = {
                "deployments": deployments,
                "statefulsets": statefulsets,
                "services": services,
                "pvcs": pvcs,
                "ingresses": ingresses,
                "pods": pods
            }
            
            for resource_type, resources in resource_types.items():
                for resource in resources:
                    try:
                        if hasattr(resource, 'metadata') and hasattr(resource.metadata, 'name') and hasattr(resource.metadata, 'namespace'):
                            resource_name = resource.metadata.name
                            ns = resource.metadata.namespace
                            with open(os.path.join(export_dir, f"{ns}_{resource_name}_{resource_type}.yaml"), "w") as f:
                                yaml.dump(resource.to_dict(), f)
                        else:
                            messagebox.showwarning("Warning", f"Skipping {resource_type} with missing metadata: {resource}")
                    except AttributeError as e:
                        messagebox.showwarning("Warning", f"Skipping invalid {resource_type} object: {str(e)}")
            
            self.status_label.config(text=f"YAML files exported to: {export_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export YAML: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
    
    def generate_visualization(self):
        """Generate the SVG visualization."""
        try:
            selected_namespaces = [ns for ns, var in self.namespace_vars.items() if var.get()]
            if not selected_namespaces:
                messagebox.showwarning("Warning", "Please select at least one namespace.")
                return
            
            # Prepare custom shapes and colors based on selected namespaces
            node_shapes = {resource: var.get() for resource, var in self.shape_vars.items()}
            namespace_colors = {ns: self.color_options[var.get()] for ns, var in self.color_vars.items() if ns in selected_namespaces}
            
            # Strip .svg from the filename to avoid duplicate extensions
            svg_filename = self.svg_entry.get()
            if svg_filename.lower().endswith(".svg"):
                svg_filename = svg_filename[:-4]  # Remove the .svg extension
            
            self.collector = ResourceCollector(selected_namespaces)
            self.visualizer = ResourceVisualizer(
                output_file=svg_filename,
                output_format="svg",
                node_shapes=node_shapes,
                namespace_colors=namespace_colors
            )
            
            # Use collect_summary for visualization
            deployments, statefulsets, services, pvcs, ingresses, pods = self.collector.collect_summary()
            self.visualizer.build_diagram(deployments, statefulsets, services, pvcs, ingresses, pods, selected_namespaces)
            self.visualizer.render(view=False)
            
            self.status_label.config(text=f"Visualization generated: {svg_filename}.svg")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate visualization: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate the CSV report."""
        try:
            selected_namespaces = [ns for ns, var in self.namespace_vars.items() if var.get()]
            if not selected_namespaces:
                messagebox.showwarning("Warning", "Please select at least one namespace.")
                return
            
            self.collector = ResourceCollector(selected_namespaces)
            self.reporter = ReportGenerator(output_file=self.csv_entry.get())
            
            # Use collect_summary for report generation
            deployments, statefulsets, services, pvcs, ingresses, pods = self.collector.collect_summary()
            self.reporter.generate_report(deployments, statefulsets, services, pvcs, ingresses, pods, selected_namespaces)
            
            self.status_label.config(text=f"CSV report generated: {self.csv_entry.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
    
    def open_svg(self):
        """Open the SVG file in the default application."""
        svg_file = self.svg_entry.get()
        # Ensure we're opening the correct file (with .svg extension)
        if not svg_file.lower().endswith(".svg"):
            svg_file += ".svg"
        
        if os.path.exists(svg_file):
            try:
                if os.name == "nt":  # Windows
                    os.startfile(svg_file)
                else:  # Linux
                    subprocess.run(["xdg-open", svg_file])
                self.status_label.config(text=f"Opened SVG: {svg_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open SVG: {str(e)}")
                self.status_label.config(text=f"Error: {str(e)}")
        else:
            messagebox.showwarning("Warning", f"SVG file not found: {svg_file}")
    
    def open_csv(self):
        """Open the CSV file in the default application."""
        csv_file = self.csv_entry.get()
        if os.path.exists(csv_file):
            try:
                if os.name == "nt":  # Windows
                    os.startfile(csv_file)
                else:  # Linux
                    subprocess.run(["xdg-open", csv_file])
                self.status_label.config(text=f"Opened CSV: {csv_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open CSV: {str(e)}")
                self.status_label.config(text=f"Error: {str(e)}")
        else:
            messagebox.showwarning("Warning", f"CSV file not found: {csv_file}")
    
    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()