import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import yaml
import threading
import datetime
import time
from ttkthemes import ThemedTk
from .collector import ResourceCollector
from .visualizer import ResourceVisualizer
from .reporter import ReportGenerator, ExcelReportGenerator
from .client import KubernetesClient

class K8sVisualizerGUI:
    """GUI for generating Kubernetes visualizations and reports."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Kubernetes Architecture Visualizer")
        self.root.geometry("850x1000")  # Increased size for new elements
        
        # Initialize components
        self.collector = None
        self.visualizer = None
        self.reporter = None
        self.excel_reporter = None
        self.namespace_vars = {}
        self.database_namespace_vars = {}
        self.resource_vars = {}
        self.namespaces = []
        
        # Available shapes, colors, and resources
        self.node_shapes = ["box", "box3d", "ellipse", "circle", "tab", "component", "cylinder", "folder"]
        self.color_options = {
            "Light Blue": "#B3E5FC", "Light Green": "#C8E6C9", "Light Red": "#FFCDD2",
            "Light Yellow": "#FFECB3", "Light Purple": "#D1C4E9", "Light Cyan": "#B2DFDB",
            "Light Lime": "#F0F4C3", "Light Orange": "#FFCCBC", "Light Gray": "#E6F3FF"
        }
        self.resource_types = ["Deployment", "StatefulSet", "Service", "PVC", "Ingress", "Pod", "Secret"]
        
        # GUI elements
        self.shape_vars = {}
        self.color_vars = {}
        self.selected_colors = {}
        self.color_frame = None
        self.select_all_var = tk.IntVar()
        self.select_all_db_var = tk.IntVar()
        self.select_all_resources_var = tk.IntVar()
        self.generate_button = None
        self.progress = None
        self.status_text = None
        self.selection_count_label = None
        
        # Create GUI elements
        self.create_widgets()
    
    def create_widgets(self):
        """Create GUI elements."""
        # Main canvas for scrolling the entire window
        main_canvas = tk.Canvas(self.root, highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=main_canvas.yview)
        main_frame = ttk.Frame(main_canvas)
        
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        main_canvas_frame = main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
        
        def configure_main_canvas(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
            main_canvas.itemconfig(main_canvas_frame, width=main_canvas.winfo_width())
        
        main_frame.bind("<Configure>", configure_main_canvas)
        main_canvas.bind_all("<MouseWheel>", lambda event: main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        main_canvas.bind_all("<Button-4>", lambda event: main_canvas.yview_scroll(-1, "units"))
        main_canvas.bind_all("<Button-5>", lambda event: main_canvas.yview_scroll(1, "units"))
        
        # Namespace selection
        tk.Label(main_frame, text="Select Namespaces:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        
        namespace_frame = ttk.LabelFrame(main_frame, text="Namespaces", padding="5")
        namespace_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        main_frame.grid_rowconfigure(1, weight=0)
        
        canvas = tk.Canvas(namespace_frame, height=120, highlightthickness=0)
        scrollbar = ttk.Scrollbar(namespace_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.namespace_inner_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas_frame = canvas.create_window((0, 0), window=self.namespace_inner_frame, anchor="nw")
        
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_frame, width=canvas.winfo_width())
        
        def on_mouse_wheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.namespace_inner_frame.bind("<Configure>", configure_canvas)
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        canvas.bind_all("<Button-4>", on_mouse_wheel)
        canvas.bind_all("<Button-5>", on_mouse_wheel)
        
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
        
        # Add Select All checkboxes
        ttk.Checkbutton(self.namespace_inner_frame, text="Select All Namespaces", variable=self.select_all_var, command=self.toggle_select_all).grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
        ttk.Checkbutton(self.namespace_inner_frame, text="Select All Database Namespaces", variable=self.select_all_db_var, command=self.toggle_select_all_db).grid(row=0, column=2, sticky="w", pady=2)
        
        # Add headers
        ttk.Label(self.namespace_inner_frame, text="Namespace").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(self.namespace_inner_frame, text="Database Namespace").grid(row=1, column=2, sticky="w", pady=2)
        
        # Add tooltips
        def create_tooltip(widget, text):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry("+1000+1000")
            label = tk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
            label.pack()
            
            def show_tooltip(event):
                tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                tooltip.deiconify()
            
            def hide_tooltip(event):
                tooltip.withdraw()
            
            widget.bind("<Enter>", show_tooltip)
            widget.bind("<Leave>", hide_tooltip)
        
        # Populate namespace checkboxes
        for idx, ns in enumerate(sorted(self.namespaces)):
            var = tk.IntVar()
            self.namespace_vars[ns] = var
            chk = ttk.Checkbutton(self.namespace_inner_frame, text=ns, variable=var, command=self.validate_and_update)
            chk.grid(row=idx + 2, column=0, sticky="w", pady=2)
            
            db_var = tk.IntVar()
            self.database_namespace_vars[ns] = db_var
            db_chk = ttk.Checkbutton(self.namespace_inner_frame, text="", variable=db_var, command=self.validate_and_update)
            db_chk.grid(row=idx + 2, column=2, sticky="w", pady=2)
            db_chk.configure(style="DB.TCheckbutton")
            
            create_tooltip(db_chk, "Mark as a database namespace for special visualization/reporting")
        
        # Configure custom style for database checkboxes
        style = ttk.Style()
        style.configure("DB.TCheckbutton", background="#E6FFE6")
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, sticky="ew", pady=10)
        
        # Resource type selection
        tk.Label(main_frame, text="Select Resources to Visualize:", font=("Helvetica", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        
        resource_frame = ttk.LabelFrame(main_frame, text="Resources", padding="5")
        resource_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        main_frame.grid_rowconfigure(4, weight=0)
        
        ttk.Checkbutton(resource_frame, text="Select All Resources", variable=self.select_all_resources_var, command=self.toggle_select_all_resources).grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
        
        for idx, resource in enumerate(self.resource_types):
            var = tk.IntVar(value=1)
            self.resource_vars[resource] = var
            chk = ttk.Checkbutton(resource_frame, text=resource, variable=var, command=self.validate_and_update)
            chk.grid(row=idx + 1, column=0, sticky="w", pady=2)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, sticky="ew", pady=10)
        
        # Styling options (Node Shapes)
        tk.Label(main_frame, text="Node Shapes:", font=("Helvetica", 10, "bold")).grid(row=6, column=0, sticky="w", pady=5)
        shape_frame = ttk.Frame(main_frame)
        shape_frame.grid(row=7, column=0, sticky="ew", pady=5)
        
        for idx, resource in enumerate(self.resource_types):
            ttk.Label(shape_frame, text=f"{resource}:").grid(row=idx, column=0, sticky="w")
            var = tk.StringVar(value=ResourceVisualizer().node_shapes.get(resource, "box"))
            self.shape_vars[resource] = var
            ttk.Combobox(shape_frame, textvariable=var, values=self.node_shapes, state="readonly", width=15).grid(row=idx, column=1, sticky="ew")
            shape_frame.grid_columnconfigure(1, weight=1)
        
        # Namespace colors
        tk.Label(main_frame, text="Namespace Colors:", font=("Helvetica", 10, "bold")).grid(row=8, column=0, sticky="w", pady=5)
        
        color_container = ttk.Frame(main_frame)
        color_container.grid(row=9, column=0, sticky="nsew", pady=5)
        main_frame.grid_rowconfigure(9, weight=0)
        
        color_canvas = tk.Canvas(color_container, height=120, highlightthickness=0)
        color_scrollbar = ttk.Scrollbar(color_container, orient=tk.VERTICAL, command=color_canvas.yview)
        self.color_frame = ttk.Frame(color_canvas)
        
        color_canvas.configure(yscrollcommand=color_scrollbar.set)
        color_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        color_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        color_canvas_frame = color_canvas.create_window((0, 0), window=self.color_frame, anchor="nw")
        
        def configure_color_canvas(event):
            color_canvas.configure(scrollregion=color_canvas.bbox("all"))
            color_canvas.itemconfig(color_canvas_frame, width=color_canvas.winfo_width())
        
        def on_color_mouse_wheel(event):
            if event.num == 4:
                color_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                color_canvas.yview_scroll(1, "units")
            else:
                color_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.color_frame.bind("<Configure>", configure_color_canvas)
        color_canvas.bind_all("<MouseWheel>", on_color_mouse_wheel)
        color_canvas.bind_all("<Button-4>", on_color_mouse_wheel)
        color_canvas.bind_all("<Button-5>", on_color_mouse_wheel)
        
        # File entries with browse buttons
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=10, column=0, sticky="ew", pady=5)
        
        tk.Label(file_frame, text="SVG Output File:").grid(row=0, column=0, sticky="w", pady=2)
        self.svg_entry = ttk.Entry(file_frame, width=40)
        self.svg_entry.insert(0, "k8s_architecture.svg")
        self.svg_entry.grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Button(file_frame, text="Browse", command=self.browse_svg).grid(row=0, column=2, padx=5, pady=2)
        
        tk.Label(file_frame, text="CSV Report File:").grid(row=1, column=0, sticky="w", pady=2)
        self.csv_entry = ttk.Entry(file_frame, width=40)
        self.csv_entry.insert(0, "k8s_components_report.csv")
        self.csv_entry.grid(row=1, column=1, sticky="ew", pady=2)
        ttk.Button(file_frame, text="Browse", command=self.browse_csv).grid(row=1, column=2, padx=5, pady=2)
        
        tk.Label(file_frame, text="Excel Report File:").grid(row=2, column=0, sticky="w", pady=2)
        self.excel_entry = ttk.Entry(file_frame, width=40)
        self.excel_entry.insert(0, "k8s_components_report.xlsx")
        self.excel_entry.grid(row=2, column=1, sticky="ew", pady=2)
        ttk.Button(file_frame, text="Browse", command=self.browse_excel).grid(row=2, column=2, padx=5, pady=2)
        
        tk.Label(file_frame, text="YAML Export Directory:").grid(row=3, column=0, sticky="w", pady=2)
        self.yaml_export_entry = ttk.Entry(file_frame, width=40)
        self.yaml_export_entry.insert(0, "k8s_yaml_export")
        self.yaml_export_entry.grid(row=3, column=1, sticky="ew", pady=2)
        ttk.Button(file_frame, text="Browse", command=self.browse_yaml_dir).grid(row=3, column=2, padx=5, pady=2)
        
        file_frame.grid_columnconfigure(1, weight=1)
        
        # Selection count display
        self.selection_count_label = ttk.Label(main_frame, text="Selected: 0 namespaces, 7 resources")
        self.selection_count_label.grid(row=11, column=0, sticky="w", pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress.grid(row=12, column=0, sticky="ew", pady=5)
        
        # Buttons (3-row layout)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=13, column=0, sticky="ew", pady=10)
        self.generate_button = ttk.Button(button_frame, text="Generate Visualization", command=self.start_generate_visualization)
        self.generate_button.grid(row=0, column=0, padx=3, pady=2, sticky="ew")
        ttk.Button(button_frame, text="Generate CSV Report", command=self.generate_report).grid(row=0, column=1, padx=3, pady=2, sticky="ew")
        ttk.Button(button_frame, text="Generate Excel Report", command=self.generate_excel_report).grid(row=0, column=2, padx=3, pady=2, sticky="ew")
        ttk.Button(button_frame, text="Export YAML", command=self.export_yaml).grid(row=0, column=3, padx=3, pady=2, sticky="ew")
        ttk.Button(button_frame, text="Open SVG", command=self.open_svg).grid(row=1, column=0, padx=3, pady=2, sticky="ew")
        ttk.Button(button_frame, text="Open CSV", command=self.open_csv).grid(row=1, column=1, padx=3, pady=2, sticky="ew")
        ttk.Button(button_frame, text="Open Excel", command=self.open_excel).grid(row=1, column=2, padx=3, pady=2, sticky="ew")
        ttk.Button(button_frame, text="Clear Selections", command=self.clear_selections).grid(row=2, column=0, columnspan=4, padx=3, pady=2, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Status log
        status_frame = ttk.LabelFrame(main_frame, text="Status Log", padding="5")
        status_frame.grid(row=14, column=0, sticky="nsew", pady=10)
        main_frame.grid_rowconfigure(14, weight=1)
        
        self.status_text = tk.Text(status_frame, height=5, wrap="word", state="disabled")
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        status_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.validate_and_update()
        self.log_status("Ready")
    
    def log_status(self, message):
        """Log a status message with timestamp."""
        self.status_text.configure(state="normal")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.configure(state="disabled")
    
    def browse_svg(self):
        """Open file dialog for SVG output file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
            initialfile=self.svg_entry.get()
        )
        if file_path:
            self.svg_entry.delete(0, tk.END)
            self.svg_entry.insert(0, file_path)
    
    def browse_csv(self):
        """Open file dialog for CSV output file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=self.csv_entry.get()
        )
        if file_path:
            self.csv_entry.delete(0, tk.END)
            self.csv_entry.insert(0, file_path)
    
    def browse_excel(self):
        """Open file dialog for Excel output file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=self.excel_entry.get()
        )
        if file_path:
            self.excel_entry.delete(0, tk.END)
            self.excel_entry.insert(0, file_path)
    
    def browse_yaml_dir(self):
        """Open directory dialog for YAML export directory."""
        directory = filedialog.askdirectory(initialdir=self.yaml_export_entry.get())
        if directory:
            self.yaml_export_entry.delete(0, tk.END)
            self.yaml_export_entry.insert(0, directory)
    
    def toggle_select_all(self):
        """Toggle all namespace checkboxes based on Select All state."""
        select_all = self.select_all_var.get()
        for var in self.namespace_vars.values():
            var.set(select_all)
        self.validate_and_update()
    
    def toggle_select_all_db(self):
        """Toggle all database namespace checkboxes based on Select All Database state."""
        select_all_db = self.select_all_db_var.get()
        for ns, db_var in self.database_namespace_vars.items():
            if self.namespace_vars[ns].get():
                db_var.set(select_all_db)
        self.validate_and_update()
    
    def toggle_select_all_resources(self):
        """Toggle all resource checkboxes based on Select All Resources state."""
        select_all = self.select_all_resources_var.get()
        for var in self.resource_vars.values():
            var.set(select_all)
        self.validate_and_update()
    
    def clear_selections(self):
        """Clear all selections to default state."""
        for var in self.namespace_vars.values():
            var.set(0)
        for var in self.database_namespace_vars.values():
            var.set(0)
        for var in self.resource_vars.values():
            var.set(1)  # Default to all resources selected
        self.select_all_var.set(0)
        self.select_all_db_var.set(0)
        self.select_all_resources_var.set(1)
        self.svg_entry.delete(0, tk.END)
        self.svg_entry.insert(0, "k8s_architecture.svg")
        self.csv_entry.delete(0, tk.END)
        self.csv_entry.insert(0, "k8s_components_report.csv")
        self.excel_entry.delete(0, tk.END)
        self.excel_entry.insert(0, "k8s_components_report.xlsx")
        self.yaml_export_entry.delete(0, tk.END)
        self.yaml_export_entry.insert(0, "k8s_yaml_export")
        self.validate_and_update()
        self.log_status("All selections cleared to default")
    
    def validate_and_update(self):
        """Validate namespace, database namespace, and resource selections and update UI."""
        selected_namespaces = [ns for ns, var in self.namespace_vars.items() if var.get()]
        for ns, db_var in self.database_namespace_vars.items():
            if not self.namespace_vars[ns].get() and db_var.get():
                db_var.set(0)
        
        if all(var.get() for var in self.namespace_vars.values()):
            self.select_all_var.set(1)
        elif not any(var.get() for var in self.namespace_vars.values()):
            self.select_all_var.set(0)
        else:
            self.select_all_var.set(0)
        
        if selected_namespaces and all(self.database_namespace_vars[ns].get() for ns in selected_namespaces):
            self.select_all_db_var.set(1)
        elif not any(var.get() for var in self.database_namespace_vars.values()):
            self.select_all_db_var.set(0)
        else:
            self.select_all_db_var.set(0)
        
        if all(var.get() for var in self.resource_vars.values()):
            self.select_all_resources_var.set(1)
        elif not any(var.get() for var in self.resource_vars.values()):
            self.select_all_resources_var.set(0)
        else:
            self.select_all_resources_var.set(0)
        
        self.update_color_options()
        self.update_selection_count()
    
    def update_color_options(self):
        """Update Namespace Colors section based on selected namespaces."""
        selected_namespaces = [ns for ns, var in self.namespace_vars.items() if var.get()]
        if not selected_namespaces:
            selected_namespaces = [self.namespaces[0]] if self.namespaces else []
        
        selected_namespaces = sorted(selected_namespaces)
        
        for widget in self.color_frame.winfo_children():
            widget.destroy()
        self.color_vars.clear()
        
        for idx, ns in enumerate(selected_namespaces):
            ttk.Label(self.color_frame, text=f"{ns}:").grid(row=idx, column=0, sticky="w")
            previous_color = self.selected_colors.get(ns, "Light Gray")
            var = tk.StringVar(value=previous_color)
            self.color_vars[ns] = var
            combobox = ttk.Combobox(self.color_frame, textvariable=var, values=list(self.color_options.keys()), state="readonly", width=15)
            combobox.grid(row=idx, column=1, sticky="ew")
            combobox.bind("<<ComboboxSelected>>", lambda event, namespace=ns: self.update_selected_color(namespace, self.color_vars[namespace].get()))
            self.color_frame.grid_columnconfigure(1, weight=1)
    
    def update_selected_color(self, namespace, color):
        """Update the persistently stored color for a namespace."""
        self.selected_colors[namespace] = color
    
    def update_selection_count(self):
        """Update the selection count display."""
        selected_namespaces = len([ns for ns, var in self.namespace_vars.items() if var.get()])
        selected_resources = len([res for res, var in self.resource_vars.items() if var.get()])
        self.selection_count_label.config(text=f"Selected: {selected_namespaces} namespaces, {selected_resources} resources")
    
    def check_namespaces_selected(self):
        """Check if namespaces are selected and show warning if not."""
        selected_namespaces = [ns for ns, var in self.namespace_vars.items() if var.get()]
        if not selected_namespaces:
            messagebox.showwarning("Warning", "Please select at least one namespace.")
        return selected_namespaces
    
    def check_resources_selected(self):
        """Check if resources are selected and show warning if not."""
        selected_resources = [res for res, var in self.resource_vars.items() if var.get()]
        if not selected_resources:
            messagebox.showwarning("Warning", "Please select at least one resource type.")
        return selected_resources
    
    def check_file_writable(self, file_path, extension):
        """Check if a file path is writable and has the correct extension."""
        if not file_path:
            return False
        if not file_path.lower().endswith(extension):
            file_path += extension
        try:
            directory = os.path.dirname(file_path) or "."
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(file_path, "w") as f:
                pass  # Test write access
            os.remove(file_path) if os.path.exists(file_path) else None
            return True
        except Exception:
            return False
    
    def warn_no_database_namespaces(self, selected_namespaces):
        """Warn if no database namespaces are selected."""
        selected_database_namespaces = [ns for ns, var in self.database_namespace_vars.items() if var.get()]
        if not selected_database_namespaces and selected_namespaces:
            messagebox.showwarning("Warning", "No database namespaces selected. Treating all selected namespaces as normal namespaces.")
        return selected_database_namespaces
    
    def start_generate_visualization(self):
        """Start visualization generation in a separate thread with progress bar."""
        selected_namespaces = self.check_namespaces_selected()
        selected_resources = self.check_resources_selected()
        if not selected_namespaces or not selected_resources:
            return
        
        svg_file = self.svg_entry.get()
        if not self.check_file_writable(svg_file, ".svg"):
            messagebox.showerror("Error", "Invalid SVG file path or no write permission.")
            self.log_status("Error: Invalid SVG file path or no write permission")
            return
        
        self.generate_button.config(state="disabled")
        self.log_status("Generating visualization, please wait...")
        self.progress["value"] = 0
        self.progress.start(10)
        self.root.update_idletasks()
        
        def generate_in_thread():
            try:
                selected_database_namespaces = self.warn_no_database_namespaces(selected_namespaces)
                
                node_shapes = {resource: var.get() for resource, var in self.shape_vars.items() if resource in selected_resources}
                namespace_colors = {ns: self.color_options[var.get()] for ns, var in self.color_vars.items() if ns in selected_namespaces}
                
                svg_filename = self.svg_entry.get()
                if svg_filename.lower().endswith(".svg"):
                    svg_filename = svg_filename[:-4]
                
                self.collector = ResourceCollector(selected_namespaces, selected_database_namespaces)
                self.visualizer = ResourceVisualizer(
                    output_file=svg_filename,
                    output_format="svg",
                    node_shapes=node_shapes,
                    namespace_colors=namespace_colors
                )
                
                deployments = [] if "Deployment" not in selected_resources else self.collector.collect_summary()[0]
                statefulsets = [] if "StatefulSet" not in selected_resources else self.collector.collect_summary()[1]
                services = [] if "Service" not in selected_resources else self.collector.collect_summary()[2]
                pvcs = [] if "PVC" not in selected_resources else self.collector.collect_summary()[3]
                ingresses = [] if "Ingress" not in selected_resources else self.collector.collect_summary()[4]
                pods = [] if "Pod" not in selected_resources else self.collector.collect_summary()[5]
                secrets = [] if "Secret" not in selected_resources else self.collector.collect_summary()[6]
                
                self.root.after(0, lambda: self.progress["value"])
                self.visualizer.build_diagram(deployments, statefulsets, services, pvcs, ingresses, pods, secrets, selected_namespaces)
                self.visualizer.render(view=False)
                
                self.root.after(0, lambda: self.finish_generate_visualization(f"Visualization generated: {svg_filename}.svg"))
            except Exception as e:
                self.root.after(0, lambda: self.finish_generate_visualization(f"Error: {str(e)}", error=True))
        
        threading.Thread(target=generate_in_thread, daemon=True).start()
    
    def finish_generate_visualization(self, message, error=False):
        """Update UI after visualization generation."""
        self.progress.stop()
        self.progress["value"] = 100 if not error else 0
        self.generate_button.config(state="normal")
        self.log_status(message)
        if error:
            messagebox.showerror("Error", message)
    
    def generate_report(self):
        """Generate the CSV report."""
        try:
            selected_namespaces = self.check_namespaces_selected()
            selected_resources = self.check_resources_selected()
            if not selected_namespaces or not selected_resources:
                return
            
            csv_file = self.csv_entry.get()
            if not self.check_file_writable(csv_file, ".csv"):
                messagebox.showerror("Error", "Invalid CSV file path or no write permission.")
                self.log_status("Error: Invalid CSV file path or no write permission")
                return
            
            selected_database_namespaces = self.warn_no_database_namespaces(selected_namespaces)
            
            self.collector = ResourceCollector(selected_namespaces, selected_database_namespaces)
            self.reporter = ReportGenerator(output_file=self.csv_entry.get())
            
            deployments = [] if "Deployment" not in selected_resources else self.collector.collect_summary()[0]
            statefulsets = [] if "StatefulSet" not in selected_resources else self.collector.collect_summary()[1]
            services = [] if "Service" not in selected_resources else self.collector.collect_summary()[2]
            pvcs = [] if "PVC" not in selected_resources else self.collector.collect_summary()[3]
            ingresses = [] if "Ingress" not in selected_resources else self.collector.collect_summary()[4]
            pods = [] if "Pod" not in selected_resources else self.collector.collect_summary()[5]
            secrets = [] if "Secret" not in selected_resources else self.collector.collect_summary()[6]
            
            self.reporter.generate_report(deployments, statefulsets, services, pvcs, ingresses, pods, secrets, selected_namespaces)
            
            self.log_status(f"CSV report generated: {self.csv_entry.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            self.log_status(f"Error: {str(e)}")
    
    def generate_excel_report(self):
        """Generate the Excel report."""
        try:
            selected_namespaces = self.check_namespaces_selected()
            selected_resources = self.check_resources_selected()
            if not selected_namespaces or not selected_resources:
                return
            
            excel_file = self.excel_entry.get()
            if not self.check_file_writable(excel_file, ".xlsx"):
                messagebox.showerror("Error", "Invalid Excel file path or no write permission.")
                self.log_status("Error: Invalid Excel file path or no write permission")
                return
            
            selected_database_namespaces = self.warn_no_database_namespaces(selected_namespaces)
            
            self.collector = ResourceCollector(selected_namespaces, selected_database_namespaces)
            self.excel_reporter = ExcelReportGenerator(output_file=self.excel_entry.get())
            
            deployments = [] if "Deployment" not in selected_resources else self.collector.collect_summary()[0]
            statefulsets = [] if "StatefulSet" not in selected_resources else self.collector.collect_summary()[1]
            services = [] if "Service" not in selected_resources else self.collector.collect_summary()[2]
            pvcs = [] if "PVC" not in selected_resources else self.collector.collect_summary()[3]
            ingresses = [] if "Ingress" not in selected_resources else self.collector.collect_summary()[4]
            pods = [] if "Pod" not in selected_resources else self.collector.collect_summary()[5]
            secrets = [] if "Secret" not in selected_resources else self.collector.collect_summary()[6]
            
            self.excel_reporter.generate_report(deployments, statefulsets, services, pvcs, ingresses, pods, secrets, selected_namespaces)
            
            self.log_status(f"Excel report generated: {self.excel_entry.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate Excel report: {str(e)}")
            self.log_status(f"Error: {str(e)}")
    
    def export_yaml(self):
        """Export YAML files for all resources in selected namespaces."""
        try:
            selected_namespaces = self.check_namespaces_selected()
            selected_resources = self.check_resources_selected()
            if not selected_namespaces or not selected_resources:
                return
            
            export_dir = self.yaml_export_entry.get()
            if not export_dir or not os.access(export_dir, os.W_OK):
                if not export_dir:
                    export_dir = "k8s_yaml_export"
                try:
                    os.makedirs(export_dir, exist_ok=True)
                except Exception:
                    messagebox.showerror("Error", "Invalid YAML export directory or no write permission.")
                    self.log_status("Error: Invalid YAML export directory or no write permission")
                    return
            
            selected_database_namespaces = self.warn_no_database_namespaces(selected_namespaces)
            
            client = KubernetesClient()
            self.collector = ResourceCollector(selected_namespaces, selected_database_namespaces)
            
            resources = self.collector.collect_resources()
            resource_types = {
                "deployments": resources[0] if "Deployment" in selected_resources else [],
                "statefulsets": resources[1] if "StatefulSet" in selected_resources else [],
                "services": resources[2] if "Service" in selected_resources else [],
                "pvcs": resources[3] if "PVC" in selected_resources else [],
                "ingresses": resources[4] if "Ingress" in selected_resources else [],
                "pods": resources[5] if "Pod" in selected_resources else [],
                "secrets": resources[6] if "Secret" in selected_resources else []
            }
            
            for ns in selected_namespaces:
                ns_manifest = {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": ns}}
                with open(os.path.join(export_dir, f"{ns}_namespace.yaml"), "w") as f:
                    yaml.dump(ns_manifest, f)
            
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
            
            self.log_status(f"YAML files exported to: {export_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export YAML: {str(e)}")
            self.log_status(f"Error: {str(e)}")
    
    def open_svg(self):
        """Open the SVG file in the default application."""
        svg_file = self.svg_entry.get()
        if not svg_file.lower().endswith(".svg"):
            svg_file += ".svg"
        
        if os.path.exists(svg_file):
            try:
                if os.name == "nt":
                    os.startfile(svg_file)
                else:
                    subprocess.run(["xdg-open", svg_file])
                self.log_status(f"Opened SVG: {svg_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open SVG: {str(e)}")
                self.log_status(f"Error: {str(e)}")
        else:
            messagebox.showwarning("Warning", f"SVG file not found: {svg_file}")
            self.log_status(f"Warning: SVG file not found: {svg_file}")
    
    def open_csv(self):
        """Open the CSV file in the default application."""
        csv_file = self.csv_entry.get()
        if os.path.exists(csv_file):
            try:
                if os.name == "nt":
                    os.startfile(csv_file)
                else:
                    subprocess.run(["xdg-open", csv_file])
                self.log_status(f"Opened CSV: {csv_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open CSV: {str(e)}")
                self.log_status(f"Error: {str(e)}")
        else:
            messagebox.showwarning("Warning", f"CSV file not found: {csv_file}")
            self.log_status(f"Warning: CSV file not found: {csv_file}")
    
    def open_excel(self):
        """Open the Excel file in the default application."""
        excel_file = self.excel_entry.get()
        if os.path.exists(excel_file):
            try:
                if os.name == "nt":
                    os.startfile(excel_file)
                else:
                    subprocess.run(["xdg-open", excel_file])
                self.log_status(f"Opened Excel: {excel_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open Excel: {str(e)}")
                self.log_status(f"Error: {str(e)}")
        else:
            messagebox.showwarning("Warning", f"Excel file not found: {excel_file}")
            self.log_status(f"Warning: Excel file not found: {excel_file}")
    def run(self):
        """Run the GUI main loop."""
        self.root.mainloop()