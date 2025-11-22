"""
OFC Network Sequencer - Complete GUI Application
Integrates all functionality from your existing scripts into a single interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
from pathlib import Path
from datetime import datetime
import threading
import sys

# Try importing required packages
try:
    import geopandas as gpd
    from shapely.geometry import LineString, MultiLineString, Point
    import networkx as nx
    import pandas as pd
    from collections import Counter
    import re

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    MISSING_PACKAGES = str(e)


# ============================================================================
# METHODS MODULE (from methods.py)
# ============================================================================

def ensure_epsg4326(input_file, output_file=None):
    """Check CRS of a shapefile and reproject to EPSG:4326 if needed."""
    gdf = gpd.read_file(input_file)

    if gdf.crs is None:
        raise ValueError("The shapefile has no CRS defined. Please set it manually.")

    if gdf.crs.to_epsg() == 4326:
        return gdf

    gdf = gdf.to_crs(epsg=4326)

    if output_file:
        gdf.to_file(output_file)

    return gdf


def smart_split(s):
    """Split span name to get starting GP."""
    if " TO " in s.upper():
        return s.upper().split(" TO ")[0].strip()
    elif "-" in s:
        return s.split("-")[0].strip()
    elif " " in s:
        return s.split(" ")[0].strip()
    else:
        return s.strip()


def smart_split2(s):
    """Split span name into parts."""
    if " TO " in s.upper():
        return s.upper().split(" TO ")
    elif "-" in s:
        return s.split("-")
    elif " " in s:
        return s.split(" ")
    else:
        return [s.strip()]


def coords_match(c1, c2, tol):
    """Check if two coordinates are within tolerance."""
    return Point(c1).distance(Point(c2)) <= tol


def get_coords(geom):
    """Extract coordinates from geometry."""
    try:
        return (geom.x, geom.y)
    except:
        return None


def merged_line_geometry(lines):
    """Merge multiple LineStrings into one."""
    merged_coords = []
    for line in lines:
        try:
            coords = list(line.coords)
            if not merged_coords:
                merged_coords.extend(coords)
            else:
                merged_coords.extend(coords[1:])
        except:
            continue
    return LineString(merged_coords)


def get_start_end_coords(geom):
    """Returns the start and end coordinates of a LineString or MultiLineString."""
    try:
        if isinstance(geom, LineString):
            coords = list(geom.coords)
            return coords[0], coords[-1]
        elif isinstance(geom, MultiLineString):
            lines = list(geom.geoms)
            if not lines:
                raise ValueError("Empty MultiLineString.")
            start = list(lines[0].coords)[0]
            end = list(lines[-1].coords)[-1]
            return start, end
        else:
            raise TypeError(f"Unsupported geometry type: {type(geom)}")
    except Exception as e:
        return None, None


def build_span_graph(df):
    """Build a directed graph from span geometries."""
    G = nx.DiGraph()
    for idx, row in df.iterrows():
        try:
            start, end = get_start_end_coords(row['geometry'])
            G.add_edge(start, end, index=idx)
        except:
            pass
    return G


def dfs_order(G, start_node):
    """Perform DFS traversal to get span order."""
    visited = set()
    span_indices = []

    def dfs(node):
        for _, neighbor, data in G.out_edges(node, data=True):
            idx = data['index']
            if idx not in visited:
                visited.add(idx)
                span_indices.append(idx)
                dfs(neighbor)

    dfs(start_node)
    return span_indices


def clean_name(name):
    """Clean and normalize GP name."""
    s = name.strip().upper()
    s = re.sub(r"[-_\s]+", " ", s)
    if s.startswith("T POINT"):
        s = s.replace("T POINT", "", 1).strip()
    return s


def check_gp_consistency(spans, gps):
    """Check consistency between span names and GP names."""
    span_gps = set()
    for s in spans:
        parts = smart_split2(s)
        for p in parts:
            cleaned = clean_name(p)
            if cleaned:
                span_gps.add(cleaned.strip().upper())

    gp_set = set(g.upper() for g in gps)
    return {
        "extra_in_spans": span_gps - gp_set,
        "unused_gps": gp_set - span_gps
    }


def checking_repetitions(counter):
    """Check for repeated items in counter."""
    repeats = [(name, count) for name, count in counter.items() if count > 1]
    if len(repeats) == 0:
        return None
    else:
        return repeats


# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class OFCSequencerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OFC Network Sequencer v1.0")
        self.root.geometry("1000x750")

        # Check dependencies
        if not DEPENDENCIES_AVAILABLE:
            self.show_dependency_error()
            return

        # Variables
        self.gps_file = tk.StringVar()
        self.segments_file = tk.StringVar()
        self.block_name = tk.StringVar(value="Khairlangi")
        self.bhq_coordinate = tk.StringVar(value="79.97841400 21.60450500")
        self.gp_name_column = tk.StringVar(value="name")

        # Ring coordinates
        self.ring_coords = {
            'R1': tk.StringVar(value=''),
            'R2': tk.StringVar(value=''),
            'R3': tk.StringVar(value=''),
            'R4': tk.StringVar(value=''),
            'R2-C1': tk.StringVar(value='79.87753850 21.67153040'),
            'R3-C1': tk.StringVar(value='79.89638690 21.57544260'),
            'R4-C1': tk.StringVar(value='80.06850970 21.61945733'),
        }

        # T-point data
        self.tpoint_data = {}

        # Output directories
        self.setup_output_dirs()

        self.create_widgets()

    def setup_output_dirs(self):
        """Create output directory structure."""
        Path("References/Output/Temp").mkdir(parents=True, exist_ok=True)
        Path("References/Output/Final").mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

    def show_dependency_error(self):
        """Show error if dependencies are missing."""
        error_frame = ttk.Frame(self.root)
        error_frame.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(error_frame, text="⚠️ Missing Dependencies",
                  font=('Arial', 16, 'bold'), foreground='red').pack(pady=20)

        msg = """This application requires the following Python packages:

• geopandas
• shapely
• networkx
• pandas

Please install them using:

pip install geopandas shapely networkx pandas

Or if using conda:

conda install geopandas shapely networkx pandas
"""

        ttk.Label(error_frame, text=msg, justify='left',
                  font=('Courier', 10)).pack(pady=10)

        ttk.Button(error_frame, text="Exit",
                   command=self.root.quit).pack(pady=20)

    def create_widgets(self):
        """Create the main UI."""
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: Configuration
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text='📁 Configuration')
        self.create_config_tab(config_frame)

        # Tab 2: Ring Coordinates
        rings_frame = ttk.Frame(notebook)
        notebook.add(rings_frame, text='🔄 Ring Coordinates')
        self.create_rings_tab(rings_frame)

        # Tab 3: T-Points
        tpoints_frame = ttk.Frame(notebook)
        notebook.add(tpoints_frame, text='📍 T-Points')
        self.create_tpoints_tab(tpoints_frame)

        # Tab 4: Process & Logs
        process_frame = ttk.Frame(notebook)
        notebook.add(process_frame, text='⚙️ Process & Logs')
        self.create_process_tab(process_frame)

    def create_config_tab(self, parent):
        """Create configuration tab."""
        # File Selection Frame
        file_frame = ttk.LabelFrame(parent, text="Input Files", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)

        # GPS Shapefile
        ttk.Label(file_frame, text="GPS Shapefile:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(file_frame, textvariable=self.gps_file, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_gps).grid(row=0, column=2)

        # Segments Shapefile
        ttk.Label(file_frame, text="Segments Shapefile:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(file_frame, textvariable=self.segments_file, width=60).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_segments).grid(row=1, column=2)

        # Configuration Frame
        config_frame = ttk.LabelFrame(parent, text="Basic Configuration", padding=10)
        config_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(config_frame, text="Block Name:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(config_frame, textvariable=self.block_name, width=30).grid(row=0, column=1, sticky='w', padx=5)

        ttk.Label(config_frame, text="BHQ Coordinate:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(config_frame, textvariable=self.bhq_coordinate, width=30).grid(row=1, column=1, sticky='w', padx=5)
        ttk.Label(config_frame, text="(Format: 'lon lat')", font=('Arial', 8, 'italic')).grid(row=1, column=2,
                                                                                              sticky='w')

        ttk.Label(config_frame, text="GP Name Column:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(config_frame, textvariable=self.gp_name_column, width=30).grid(row=2, column=1, sticky='w', padx=5)
        ttk.Label(config_frame, text="(Column name in GPS shapefile)", font=('Arial', 8, 'italic')).grid(row=2,
                                                                                                         column=2,
                                                                                                         sticky='w')

        # Load/Save Configuration
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="💾 Save Configuration", command=self.save_config).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📂 Load Configuration", command=self.load_config).pack(side='left', padx=5)

    def create_rings_tab(self, parent):
        """Create rings configuration tab."""
        info = ttk.Label(parent, text="Configure start coordinates for each ring. Leave blank to use BHQ coordinate.",
                         wraplength=900, justify='left')
        info.pack(pady=10, padx=10)

        rings_frame = ttk.LabelFrame(parent, text="Ring Start Coordinates", padding=10)
        rings_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create scrollable frame
        canvas = tk.Canvas(rings_frame)
        scrollbar = ttk.Scrollbar(rings_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add ring entries
        for i, (ring_name, var) in enumerate(self.ring_coords.items()):
            ttk.Label(scrollable_frame, text=f"{ring_name}:", width=15).grid(row=i, column=0, sticky='w', pady=5,
                                                                             padx=5)
            ttk.Entry(scrollable_frame, textvariable=var, width=50).grid(row=i, column=1, pady=5, padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add new ring button
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame, text="➕ Add New Ring", command=self.add_new_ring).pack(side='left', padx=5)

    def create_tpoints_tab(self, parent):
        """Create T-Points configuration tab."""
        info = ttk.Label(parent, text="Configure T-Point coordinates (Format: 'GP_NAME: lon, lat')",
                         wraplength=900, justify='left')
        info.pack(pady=10, padx=10)

        # Text area for T-points
        tpoints_frame = ttk.LabelFrame(parent, text="T-Point Coordinates", padding=10)
        tpoints_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.tpoints_text = scrolledtext.ScrolledText(tpoints_frame, height=25, width=100, font=('Courier', 10))
        self.tpoints_text.pack(fill='both', expand=True)

        # Default T-points
        default_tpoints = """T-POINT BHIJYADAND: 79.90573337, 21.68571704
T-POINT KATORI: 79.89636580, 21.57545930
T-POINT MIRAGPUR: 79.83742077, 21.63592722
T-POINT MOHADI: 80.06850970, 21.61945733
T-POINT SALEBADI: 79.87753850, 21.67153040
T-POINT KUMAHALI: 79.88502599, 21.56655470
T-POINT CHHATERA: 79.81278780, 21.57607810"""

        self.tpoints_text.insert('1.0', default_tpoints)

    def create_process_tab(self, parent):
        """Create process and logs tab."""
        # Action buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(btn_frame, text="1️⃣ Check GP Names",
                   command=self.check_gp_names, width=20).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="2️⃣ Generate Sequences",
                   command=self.generate_sequences, width=20).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🗑️ Clear Logs",
                   command=self.clear_logs, width=15).pack(side='right', padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(parent, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=5)

        # Log output
        log_frame = ttk.LabelFrame(parent, text="Process Logs", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=30, width=120,
                                                  bg='#1e1e1e', fg='#00ff00',
                                                  font=('Courier', 9))
        self.log_text.pack(fill='both', expand=True)

    def browse_gps(self):
        """Browse for GPS shapefile."""
        filename = filedialog.askopenfilename(
            title="Select GPS Shapefile",
            filetypes=[("Shapefiles", "*.shp"), ("All files", "*.*")]
        )
        if filename:
            self.gps_file.set(filename)

    def browse_segments(self):
        """Browse for segments shapefile."""
        filename = filedialog.askopenfilename(
            title="Select Segments Shapefile",
            filetypes=[("Shapefiles", "*.shp"), ("All files", "*.*")]
        )
        if filename:
            self.segments_file.set(filename)

    def add_new_ring(self):
        """Dialog to add a new ring."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Ring")
        dialog.geometry("450x180")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Ring Name:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        ring_name = tk.StringVar()
        ttk.Entry(dialog, textvariable=ring_name, width=35).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(dialog, text="Coordinate:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        coord = tk.StringVar()
        ttk.Entry(dialog, textvariable=coord, width=35).grid(row=1, column=1, padx=10, pady=10)

        def add_ring():
            name = ring_name.get().strip()
            if name and name not in self.ring_coords:
                self.ring_coords[name] = tk.StringVar(value=coord.get())
                messagebox.showinfo("Success", f"Ring '{name}' added! Restart to see it in the Rings tab.")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Invalid or duplicate ring name")

        ttk.Button(dialog, text="Add Ring", command=add_ring).grid(row=2, column=1, pady=15, sticky='e')

    def save_config(self):
        """Save configuration to JSON file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"{self.block_name.get()}_config.json"
        )
        if filename:
            config = {
                'gps_file': self.gps_file.get(),
                'segments_file': self.segments_file.get(),
                'block_name': self.block_name.get(),
                'bhq_coordinate': self.bhq_coordinate.get(),
                'gp_name_column': self.gp_name_column.get(),
                'ring_coords': {k: v.get() for k, v in self.ring_coords.items()},
                'tpoints': self.tpoints_text.get('1.0', 'end-1c')
            }
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Success", f"Configuration saved to:\n{filename}")

    def load_config(self):
        """Load configuration from JSON file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)

                self.gps_file.set(config.get('gps_file', ''))
                self.segments_file.set(config.get('segments_file', ''))
                self.block_name.set(config.get('block_name', ''))
                self.bhq_coordinate.set(config.get('bhq_coordinate', ''))
                self.gp_name_column.set(config.get('gp_name_column', 'name'))

                for k, v in config.get('ring_coords', {}).items():
                    if k in self.ring_coords:
                        self.ring_coords[k].set(v)
                    else:
                        self.ring_coords[k] = tk.StringVar(value=v)

                self.tpoints_text.delete('1.0', 'end')
                self.tpoints_text.insert('1.0', config.get('tpoints', ''))

                messagebox.showinfo("Success", "Configuration loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration:\n{str(e)}")

    def log(self, message, level="INFO"):
        """Add message to log with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌"
        }.get(level, "•")

        self.log_text.insert('end', f"[{timestamp}] {prefix} {message}\n")
        self.log_text.see('end')
        self.root.update()

    def clear_logs(self):
        """Clear the log text area."""
        self.log_text.delete('1.0', 'end')

    def parse_tpoints(self):
        """Parse T-points from text area."""
        tpoints = {}
        text = self.tpoints_text.get('1.0', 'end-1c')
        for line in text.strip().split('\n'):
            if ':' in line:
                parts = line.split(':')
                name = parts[0].strip().upper()
                coords = parts[1].strip().split(',')
                if len(coords) == 2:
                    try:
                        lon = float(coords[0].strip())
                        lat = float(coords[1].strip())
                        tpoints[name] = (lon, lat)
                    except ValueError:
                        pass
        return tpoints

    def check_gp_names(self):
        """Run GP name consistency check."""
        if not self.gps_file.get() or not self.segments_file.get():
            messagebox.showerror("Error", "Please select both GPS and Segments shapefiles!")
            return

        self.log("=" * 80)
        self.log("Starting GP Name Consistency Check...", "INFO")
        self.log("=" * 80)
        self.progress.start()

        def run_check():
            try:
                gp_col = self.gp_name_column.get()

                self.log(f"Loading GPS file: {Path(self.gps_file.get()).name}")
                gps = gpd.read_file(self.gps_file.get())

                self.log(f"Loading Segments file: {Path(self.segments_file.get()).name}")
                segments = gpd.read_file(self.segments_file.get())

                # Check GP names
                if gp_col not in gps.columns:
                    self.log(f"Column '{gp_col}' not found in GPS file!", "ERROR")
                    self.log(f"Available columns: {', '.join(gps.columns)}", "INFO")
                    return

                gp_names = gps[gp_col].tolist()
                gp_name_lat_lon = list(zip(gps[gp_col], zip(gps.geometry.x, gps.geometry.y)))

                # Check for repetitions
                gp_name_counts = Counter(gp_names)
                gp_geometry_counts = Counter(gp_name_lat_lon)

                gp_repetitions = checking_repetitions(gp_name_counts)
                gp_geo_repetitions = checking_repetitions(gp_geometry_counts)

                if gp_repetitions:
                    if gp_geo_repetitions:
                        self.log(f"Duplicate GPs found: {gp_repetitions}", "WARNING")
                        self.log(f"Duplicate geometries: {gp_geo_repetitions}", "WARNING")
                    else:
                        self.log(f"Duplicate GP names with different geometries: {gp_repetitions}", "WARNING")
                        df = pd.DataFrame(list(gp_geometry_counts.keys()), columns=["gp_name", "coords"])
                        duplicates = df[df.duplicated("gp_name", keep=False)]
                        for _, row in duplicates.iterrows():
                            self.log(f"  {row['gp_name']}: {row['coords']}", "INFO")
                else:
                    self.log("No duplicate GP names found", "SUCCESS")

                # Check consistency with span names
                if 'span_name' in segments.columns:
                    spans = segments.span_name.tolist()
                    consistency = check_gp_consistency(spans, gp_names)

                    if consistency['extra_in_spans']:
                        self.log(f"GPs in spans but not in GPS file: {consistency['extra_in_spans']}", "WARNING")
                    else:
                        self.log("All span GPs found in GPS file", "SUCCESS")

                    if consistency['unused_gps']:
                        self.log(f"Unused GPs (in GPS but not in spans): {len(consistency['unused_gps'])} GPs", "INFO")

                self.log("=" * 80)
                self.log("GP Name Check Complete!", "SUCCESS")
                self.log("=" * 80)

            except Exception as e:
                self.log(f"ERROR: {str(e)}", "ERROR")
                import traceback
                self.log(traceback.format_exc(), "ERROR")
            finally:
                self.progress.stop()

        thread = threading.Thread(target=run_check)
        thread.daemon = True
        thread.start()

    def generate_sequences(self):
        """Generate segment and span sequences."""
        if not self.gps_file.get() or not self.segments_file.get():
            messagebox.showerror("Error", "Please select both GPS and Segments shapefiles!")
            return

        response = messagebox.askyesno(
            "Confirm",
            "This will generate sequences and save output files.\nContinue?"
        )
        if not response:
            return

        self.log("=" * 80)
        self.log("Starting Sequence Generation...", "INFO")
        self.log("=" * 80)
        self.progress.start()

        def run_generation():
            try:
                block_name = self.block_name.get()
                version = f"{block_name}-1"
                gp_col = self.gp_name_column.get()

                # Parse configurations
                rings = {}
                bhq = self.bhq_coordinate.get()
                for ring_name, var in self.ring_coords.items():
                    coord = var.get().strip()
                    rings[ring_name] = coord if coord else bhq

                t_point_ring_spans = self.parse_tpoints()

                self.log(f"Block: {block_name}", "INFO")
                self.log(f"BHQ Coordinate: {bhq}", "INFO")
                self.log(f"Processing {len(rings)} rings", "INFO")
                self.log(f"Loaded {len(t_point_ring_spans)} T-points", "INFO")

                # Load and prepare data
                self.log("Loading shapefiles...", "INFO")
                gdf = ensure_epsg4326(self.segments_file.get(),
                                      f"References/{block_name}/{block_name}-SHP_4326.shp")
                gdf_gp = gpd.read_file(self.gps_file.get())

                # Create output GeoDataFrames
                gdf_new_sp = gdf.iloc[0:0].copy()
                gdf_new_sp["seg_seq"] = None

                gdf_span = gpd.GeoDataFrame(
                    columns=['span_name', 'ring', 'start_cord', 'end_cord', 'span_seq', 'geometry'],
                    geometry='geometry'
                )

                error_gdf = gpd.GeoDataFrame(
                    columns=['span_name', 'error', 'geometry'],
                    geometry='geometry'
                )

                # Process each span
                span_list = gdf.sort_values('span_name').span_name.unique()
                self.log(f"Processing {len(span_list)} spans...", "INFO")

                for idx, s in enumerate(span_list, 1):
                    self.log(f"[{idx}/{len(span_list)}] Processing span: {s}", "INFO")
                    temp_df = gdf[gdf.span_name == s].copy()
                    temp_df['start'] = temp_df.geometry.apply(lambda geom: get_start_end_coords(geom)[0])
                    temp_df['end'] = temp_df.geometry.apply(lambda geom: get_start_end_coords(geom)[1])

                    # Get starting GP
                    start_gp = smart_split(s).lower()
                    if start_gp.upper() in t_point_ring_spans.keys():
                        gp_node = t_point_ring_spans[start_gp.upper()]
                    else:
                        try:
                            s_c = gdf_gp[gdf_gp[gp_col].str.lower() == start_gp].geometry.iloc[0]
                            gp_node = get_coords(s_c)
                        except:
                            self.log(f"  GP coordinate not found for {start_gp}", "WARNING")
                            gp_node = None

                    sorted_indices = []
                    remaining = temp_df.copy()

                    # Find true starting segment
                    all_endpoints = list(temp_df['start']) + list(temp_df['end'])
                    counts = Counter(all_endpoints)
                    true_starts = [pt for pt, c in counts.items() if c == 1]

                    if len(true_starts) >= 2:
                        node1 = true_starts[0]
                        node2 = true_starts[1]

                        if gp_node is not None:
                            try:
                                segment_of_gp_node = temp_df[
                                    (temp_df['start'] == gp_node) | (temp_df['end'] == gp_node)].iloc[0]
                                start_row = segment_of_gp_node
                                start_node = Point(gp_node)
                            except:
                                candidates = temp_df["start"].tolist() + temp_df["end"].tolist()
                                candidate_points = [Point(x, y) for (x, y) in candidates]
                                nearest = min(candidate_points, key=lambda pt: pt.distance(Point(gp_node)))
                                nearest_coords = (nearest.x, nearest.y)
                                segment_of_nearest_node = temp_df[
                                    (temp_df['start'] == nearest_coords) | (temp_df['end'] == nearest_coords)].iloc[0]
                                start_row = segment_of_nearest_node
                                start_node = nearest
                        else:
                            segment_of_node1 = temp_df[
                                (temp_df['start'] == node1) | (temp_df['end'] == node1)].iloc[0]
                            segment_of_node2 = temp_df[
                                (temp_df['start'] == node2) | (temp_df['end'] == node2)].iloc[0]

                            try:
                                if int(segment_of_node1.OBJECTID) < int(segment_of_node2.OBJECTID):
                                    start_row = segment_of_node1
                                    start_node = Point(node1)
                                else:
                                    start_row = segment_of_node2
                                    start_node = Point(node2)
                            except:
                                start_row = segment_of_node1
                                start_node = Point(node1)

                        current_idx = start_row.name
                        current = start_row.copy()

                        # Flip geometry if needed
                        if current['end'] == (start_node.x, start_node.y):
                            flipped_geom = LineString(list(current['geometry'].coords)[::-1])
                            temp_df.at[current_idx, 'geometry'] = flipped_geom
                            current['geometry'] = flipped_geom
                            current['start'], current['end'] = list(flipped_geom.coords)[0], list(flipped_geom.coords)[
                                -1]

                        sorted_indices.append(current_idx)
                        remaining = remaining.drop(index=current_idx)

                        # Traverse segments
                        while not remaining.empty:
                            found = False
                            for ridx, row in remaining.iterrows():
                                try:
                                    if row['start'] == current['end']:
                                        sorted_indices.append(ridx)
                                        current = row
                                        remaining = remaining.drop(ridx)
                                        found = True
                                        break
                                    elif row['end'] == current['end']:
                                        reversed_geom = LineString(list(row['geometry'].coords)[::-1])
                                        temp_df.at[ridx, 'geometry'] = reversed_geom
                                        row['geometry'] = reversed_geom
                                        row['start'], row['end'] = get_start_end_coords(reversed_geom)
                                        sorted_indices.append(ridx)
                                        current = row
                                        remaining = remaining.drop(ridx)
                                        found = True
                                        break
                                    elif row['end'] == current['start']:
                                        reversed_geom = LineString(list(row['geometry'].coords)[::-1])
                                        temp_df.at[ridx, 'geometry'] = reversed_geom
                                        row['geometry'] = reversed_geom
                                        row['start'], row['end'] = get_start_end_coords(reversed_geom)
                                        sorted_indices.insert(0, ridx)
                                        current = row
                                        remaining = remaining.drop(ridx)
                                        found = True
                                        break
                                except:
                                    pass

                            if not found:
                                self.log(f"  Disconnected segment in span '{s}' at {current['end']}", "WARNING")
                                error_row = gpd.GeoDataFrame([{
                                    'span_name': s,
                                    'error': f"Disconnected at {current['end']}",
                                    'geometry': Point(current['end']),
                                }], geometry='geometry', crs=temp_df.crs)
                                error_gdf = pd.concat([error_gdf, error_row], ignore_index=True)
                                break

                        # Assign segment sequence
                        sequence_series = temp_df.index.to_series().apply(
                            lambda x: sorted_indices.index(x) + 1 if x in sorted_indices else None
                        )
                        temp_df['seg_seq'] = sequence_series
                        temp_df = temp_df.drop(columns=['start', 'end'])

                        # Merge geometry
                        complete_span_line = merged_line_geometry(temp_df.loc[sorted_indices].geometry)

                        # Add span-level geometry
                        new_span_row = gpd.GeoDataFrame([{
                            'span_name': s,
                            'ring': str(temp_df.loc[temp_df.index[0], 'ring_no']),
                            'start_cord': get_start_end_coords(complete_span_line)[0],
                            'end_cord': get_start_end_coords(complete_span_line)[1],
                            'span_seq': '',
                            'geometry': complete_span_line
                        }], geometry='geometry', crs=temp_df.crs)

                        gdf_span = pd.concat([gdf_span, new_span_row], ignore_index=True)
                        gdf_new_sp = pd.concat([gdf_new_sp, temp_df])

                # Save temporary outputs
                self.log("Saving segment sequences...", "INFO")
                gdf_new_sp.to_file(f'References/Output/Temp/OFC_NEW_{version}.shp')
                gdf_span.to_file(f'References/Output/Temp/OFC_NEW_SPAN_{version}.shp')
                if not error_gdf.empty:
                    error_gdf.to_file(f"References/Output/Temp/error_{version}.shp")
                    self.log(f"Found {len(error_gdf)} errors - saved to error_{version}.shp", "WARNING")

                # Process span sequences
                self.log("Generating span sequences...", "INFO")
                gdf_span['ring'] = gdf_span['ring'].astype(str)
                gdf_span['span_name'] = gdf_span['span_name'].astype(str)
                gdf_new_sp['span_name'] = gdf_new_sp['span_name'].astype(str)
                gdf_new_sp['ring_no'] = gdf_new_sp['ring_no'].astype(str)

                if 'span_seq' not in gdf_new_sp.columns:
                    gdf_new_sp['span_seq'] = None

                span_sequence_map = {}
                unique_rings = sorted(gdf_span['ring'].unique())

                for ring in unique_rings:
                    self.log(f"Processing ring: {ring}", "INFO")
                    ring_df = gdf_span[gdf_span['ring'] == ring].copy()
                    G = build_span_graph(ring_df)

                    coord_str = rings.get(ring, bhq)
                    try:
                        x_str, y_str = coord_str.strip().split()
                        start_coord = (float(x_str), float(y_str))
                        start_point = Point(start_coord)

                        closest_node = min(G.nodes, key=lambda node: Point(node).distance(start_point))

                        if Point(closest_node).distance(start_point) > 0.001:
                            self.log(f"  Warning: Start point far from closest node", "WARNING")

                        ordered_indices = dfs_order(G, closest_node)

                        for seq, ridx in enumerate(ordered_indices, 1):
                            span_name = ring_df.loc[ridx, 'span_name']
                            span_sequence_map[span_name] = seq
                            gdf_span.loc[gdf_span['span_name'] == span_name, 'span_seq'] = seq
                            gdf_new_sp.loc[gdf_new_sp['span_name'] == span_name, 'span_seq'] = seq

                        self.log(f"  Completed {ring} with {len(ordered_indices)} spans", "SUCCESS")
                    except Exception as e:
                        self.log(f"  Error processing ring {ring}: {str(e)}", "ERROR")

                # Save final outputs
                self.log("Saving final outputs...", "INFO")
                gdf_new_sp.to_file(f"References/Output/Final/OFC_New_{version}_Seg_Span_Seq.shp")
                gdf_span.to_file(f"References/Output/Final/Spans_Geo_{version}.shp")

                self.log("=" * 80)
                self.log("Sequence Generation Complete!", "SUCCESS")
                self.log(f"Output files saved in: References/Output/Final/", "SUCCESS")
                self.log("=" * 80)

                messagebox.showinfo("Success",
                                    f"Sequences generated successfully!\n\nOutput files:\n"
                                    f"• OFC_New_{version}_Seg_Span_Seq.shp\n"
                                    f"• Spans_Geo_{version}.shp")

            except Exception as e:
                self.log(f"ERROR: {str(e)}", "ERROR")
                import traceback
                self.log(traceback.format_exc(), "ERROR")
                messagebox.showerror("Error", f"Failed to generate sequences:\n{str(e)}")
            finally:
                self.progress.stop()

        thread = threading.Thread(target=run_generation)
        thread.daemon = True
        thread.start()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    root = tk.Tk()

    # Set icon and styling
    try:
        root.iconbitmap('icon.ico')  # Optional: add your icon
    except:
        pass

    style = ttk.Style()
    style.theme_use('clam')

    app = OFCSequencerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
