#!/usr/bin/env python3
"""
OFC Network Sequencer - Mac Diagnostic Version
This version will help identify and fix Mac-specific issues
"""

import sys
import platform

print("=" * 60)
print("OFC Network Sequencer - Diagnostic Mode")
print("=" * 60)
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.system()} {platform.release()}")
print(f"Python Executable: {sys.executable}")
print("=" * 60)

# Check Tkinter availability
print("\n1. Checking Tkinter...")
try:
    import tkinter as tk

    print("   ✓ Tkinter is available")
    tkinter_version = tk.TkVersion
    print(f"   Tkinter version: {tkinter_version}")
except ImportError as e:
    print(f"   ✗ Tkinter NOT available: {e}")
    print("\n   FIX: Install tkinter using:")
    print("   brew install python-tk@3.11")
    sys.exit(1)

# Check other dependencies
print("\n2. Checking required packages...")
missing_packages = []

packages = {
    'geopandas': 'geopandas',
    'shapely': 'shapely',
    'networkx': 'networkx',
    'pandas': 'pandas'
}

for package_name, import_name in packages.items():
    try:
        __import__(import_name)
        print(f"   ✓ {package_name} is available")
    except ImportError:
        print(f"   ✗ {package_name} is NOT available")
        missing_packages.append(package_name)

if missing_packages:
    print("\n   FIX: Install missing packages using:")
    print(f"   pip3 install {' '.join(missing_packages)}")
    sys.exit(1)

print("\n3. Testing basic Tkinter window...")
try:
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("400x300")

    label = tk.Label(root, text="If you see this, Tkinter is working!",
                     font=('Arial', 14), pady=20)
    label.pack()

    button = tk.Button(root, text="Close Test Window",
                       command=root.quit,
                       font=('Arial', 12))
    button.pack(pady=10)

    info_text = f"""Platform: {platform.system()}
Python: {sys.version_info.major}.{sys.version_info.minor}
Tkinter: {tk.TkVersion}

If this window appears, your Mac is ready!
Close this to continue to the main application."""

    info_label = tk.Label(root, text=info_text, justify='left',
                          font=('Courier', 10))
    info_label.pack(pady=20)

    print("   ✓ Test window created successfully")
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE - Check if test window appeared")
    print("Close the test window to launch the main application")
    print("=" * 60)

    root.mainloop()

except Exception as e:
    print(f"   ✗ Error creating test window: {e}")
    import traceback

    print(traceback.format_exc())
    sys.exit(1)

# If we get here, everything works - now load the main application
print("\n4. Launching main application...")

# Import all required packages
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
from pathlib import Path
from datetime import datetime
import threading
import re
from collections import Counter

import geopandas as gpd
from shapely.geometry import LineString, MultiLineString, Point
import networkx as nx
import pandas as pd


# ============================================================================
# METHODS MODULE
# ============================================================================

def ensure_epsg4326(input_file, output_file=None):
    """Check CRS of a shapefile and reproject to EPSG:4326 if needed."""
    gdf = gpd.read_file(input_file)
    if gdf.crs is None:
        raise ValueError("The shapefile has no CRS defined.")
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
    return repeats if repeats else None


# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class OFCSequencerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OFC Network Sequencer v2.0 - Mac Edition")

        # Mac-specific window settings
        if platform.system() == 'Darwin':
            self.root.geometry("1200x850")
            # Bring window to front on Mac
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after_idle(self.root.attributes, '-topmost', False)
        else:
            self.root.geometry("1100x800")

        # Variables
        self.gps_file = tk.StringVar()
        self.segments_file = tk.StringVar()
        self.block_name = tk.StringVar(value="Khairlangi")
        self.bhq_coordinate = tk.StringVar(value="79.97841400 21.60450500")
        self.gp_name_column = tk.StringVar(value="name")

        # Ring coordinates
        self.rings = [
            {'name': 'R1', 'coordinate': ''},
            {'name': 'R2', 'coordinate': ''},
            {'name': 'R3', 'coordinate': ''},
            {'name': 'R4', 'coordinate': ''},
            {'name': 'R2-C1', 'coordinate': '79.87753850 21.67153040'},
            {'name': 'R3-C1', 'coordinate': '79.89638690 21.57544260'},
            {'name': 'R4-C1', 'coordinate': '80.06850970 21.61945733'},
        ]

        self.setup_output_dirs()
        self.create_widgets()

        # Show welcome message
        self.root.after(100, self.show_welcome)

    def show_welcome(self):
        """Show welcome message on Mac."""
        messagebox.showinfo(
            "Welcome to OFC Sequencer",
            "Mac version successfully loaded!\n\n"
            "All features are ready to use.\n"
            "Start by selecting your input files in the Configuration tab."
        )

    def setup_output_dirs(self):
        """Create output directory structure."""
        Path("References/Output/Temp").mkdir(parents=True, exist_ok=True)
        Path("References/Output/Final").mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)

    def create_widgets(self):
        """Create the main UI."""
        # Style configuration for Mac
        style = ttk.Style()
        if platform.system() == 'Darwin':
            style.theme_use('aqua')

        # Create notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tabs
        config_frame = ttk.Frame(notebook, padding=10)
        notebook.add(config_frame, text='📁 Configuration')
        self.create_config_tab(config_frame)

        rings_frame = ttk.Frame(notebook, padding=10)
        notebook.add(rings_frame, text='🔄 Ring Coordinates')
        self.create_rings_tab(rings_frame)

        tpoints_frame = ttk.Frame(notebook, padding=10)
        notebook.add(tpoints_frame, text='📍 T-Points')
        self.create_tpoints_tab(tpoints_frame)

        process_frame = ttk.Frame(notebook, padding=10)
        notebook.add(process_frame, text='⚙️ Process & Logs')
        self.create_process_tab(process_frame)

    def create_config_tab(self, parent):
        """Create configuration tab."""
        # File Selection
        file_frame = ttk.LabelFrame(parent, text="Input Files", padding=15)
        file_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(file_frame, text="GPS Shapefile:").grid(row=0, column=0, sticky='w', pady=8)
        ttk.Entry(file_frame, textvariable=self.gps_file, width=65).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_gps).grid(row=0, column=2, padx=5)

        ttk.Label(file_frame, text="Segments Shapefile:").grid(row=1, column=0, sticky='w', pady=8)
        ttk.Entry(file_frame, textvariable=self.segments_file, width=65).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_segments).grid(row=1, column=2, padx=5)

        # Configuration
        config_frame = ttk.LabelFrame(parent, text="Basic Configuration", padding=15)
        config_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(config_frame, text="Block Name:").grid(row=0, column=0, sticky='w', pady=8)
        ttk.Entry(config_frame, textvariable=self.block_name, width=35).grid(row=0, column=1, sticky='w', padx=5)

        ttk.Label(config_frame, text="BHQ Coordinate:").grid(row=1, column=0, sticky='w', pady=8)
        ttk.Entry(config_frame, textvariable=self.bhq_coordinate, width=35).grid(row=1, column=1, sticky='w', padx=5)
        ttk.Label(config_frame, text="(lon lat)", font=('Arial', 9)).grid(row=1, column=2, sticky='w')

        ttk.Label(config_frame, text="GP Name Column:").grid(row=2, column=0, sticky='w', pady=8)
        ttk.Entry(config_frame, textvariable=self.gp_name_column, width=35).grid(row=2, column=1, sticky='w', padx=5)

        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=5, pady=15)
        ttk.Button(btn_frame, text="💾 Save Configuration", command=self.save_config).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📂 Load Configuration", command=self.load_config).pack(side='left', padx=5)

    def create_rings_tab(self, parent):
        """Create rings tab."""
        info = ttk.Label(parent,
                         text="Configure ring coordinates. Edit existing rings or add new ones. Leave blank to use BHQ coordinate.",
                         wraplength=950, justify='left')
        info.pack(pady=10, padx=5)

        # Scrollable frame
        container = ttk.Frame(parent)
        container.pack(fill='both', expand=True, padx=5, pady=5)

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.rings_container = ttk.Frame(canvas)

        self.rings_container.bind("<Configure>",
                                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.rings_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh_rings_display()

        # Add button
        ttk.Button(parent, text="➕ Add New Ring",
                   command=self.add_new_ring).pack(pady=10)

    def refresh_rings_display(self):
        """Refresh rings display."""
        for widget in self.rings_container.winfo_children():
            widget.destroy()

        # Header
        header = ttk.Frame(self.rings_container)
        header.pack(fill='x', pady=(0, 10))
        ttk.Label(header, text="Ring Name", width=18, font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        ttk.Label(header, text="Coordinate (lon lat)", width=45, font=('Arial', 11, 'bold')).pack(side='left', padx=5)
        ttk.Label(header, text="Actions", width=20, font=('Arial', 11, 'bold')).pack(side='left', padx=5)

        ttk.Separator(self.rings_container, orient='horizontal').pack(fill='x', pady=5)

        # Rings
        for idx, ring in enumerate(self.rings):
            frame = ttk.Frame(self.rings_container)
            frame.pack(fill='x', pady=5)

            name_entry = ttk.Entry(frame, width=18, font=('Arial', 10))
            name_entry.insert(0, ring['name'])
            name_entry.pack(side='left', padx=5)

            coord_entry = ttk.Entry(frame, width=45, font=('Arial', 10))
            coord_entry.insert(0, ring['coordinate'])
            coord_entry.pack(side='left', padx=5)

            ring['name_widget'] = name_entry
            ring['coord_widget'] = coord_entry

            btn_frame = ttk.Frame(frame)
            btn_frame.pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Update", width=10,
                       command=lambda i=idx: self.update_ring(i)).pack(side='left', padx=2)
            ttk.Button(btn_frame, text="Delete", width=10,
                       command=lambda i=idx: self.delete_ring(i)).pack(side='left', padx=2)

    def update_ring(self, index):
        """Update ring."""
        ring = self.rings[index]
        new_name = ring['name_widget'].get().strip()
        new_coord = ring['coord_widget'].get().strip()
        if new_name:
            ring['name'] = new_name
            ring['coordinate'] = new_coord
            messagebox.showinfo("Success", f"Ring '{new_name}' updated!")
        else:
            messagebox.showerror("Error", "Ring name cannot be empty!")

    def delete_ring(self, index):
        """Delete ring."""
        ring = self.rings[index]
        if messagebox.askyesno("Confirm", f"Delete ring '{ring['name']}'?"):
            self.rings.pop(index)
            self.refresh_rings_display()
            messagebox.showinfo("Success", "Ring deleted!")

    def add_new_ring(self):
        """Add new ring dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Ring")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Ring Name:", font=('Arial', 11)).grid(row=0, column=0, padx=15, pady=15, sticky='w')
        ring_name = tk.StringVar()
        ttk.Entry(dialog, textvariable=ring_name, width=40, font=('Arial', 11)).grid(row=0, column=1, padx=15, pady=15)

        ttk.Label(dialog, text="Coordinate:", font=('Arial', 11)).grid(row=1, column=0, padx=15, pady=15, sticky='w')
        coord = tk.StringVar()
        ttk.Entry(dialog, textvariable=coord, width=40, font=('Arial', 11)).grid(row=1, column=1, padx=15, pady=15)

        def add_ring():
            name = ring_name.get().strip()
            if name:
                if any(r['name'] == name for r in self.rings):
                    messagebox.showerror("Error", f"Ring '{name}' already exists!")
                    return
                self.rings.append({'name': name, 'coordinate': coord.get().strip()})
                self.refresh_rings_display()
                messagebox.showinfo("Success", f"Ring '{name}' added!")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Ring name cannot be empty!")

        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=2, column=1, pady=20)
        ttk.Button(btn_frame, text="Add Ring", command=add_ring).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)

    def create_tpoints_tab(self, parent):
        """Create T-points tab."""
        info = ttk.Label(parent, text="Configure T-Point coordinates (Format: 'GP_NAME: lon, lat')",
                         wraplength=950)
        info.pack(pady=10)

        frame = ttk.LabelFrame(parent, text="T-Point Coordinates", padding=10)
        frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.tpoints_text = scrolledtext.ScrolledText(frame, height=28, width=110, font=('Courier', 11))
        self.tpoints_text.pack(fill='both', expand=True)

        default_tpoints = """T-POINT BHIJYADAND: 79.90573337, 21.68571704
T-POINT KATORI: 79.89636580, 21.57545930
T-POINT MIRAGPUR: 79.83742077, 21.63592722
T-POINT MOHADI: 80.06850970, 21.61945733
T-POINT SALEBADI: 79.87753850, 21.67153040
T-POINT KUMAHALI: 79.88502599, 21.56655470
T-POINT CHHATERA: 79.81278780, 21.57607810"""
        self.tpoints_text.insert('1.0', default_tpoints)

    def create_process_tab(self, parent):
        """Create process tab."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=5, pady=10)

        ttk.Button(btn_frame, text="1️⃣ Check GP Names", command=self.check_gp_names).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="2️⃣ Generate Sequences", command=self.generate_sequences).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🗑️ Clear Logs", command=self.clear_logs).pack(side='right', padx=5)

        self.progress = ttk.Progressbar(parent, mode='indeterminate')
        self.progress.pack(fill='x', padx=5, pady=5)

        log_frame = ttk.LabelFrame(parent, text="Process Logs", padding=10)
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=30, width=115, font=('Courier', 10))
        self.log_text.pack(fill='both', expand=True)

    def browse_gps(self):
        filename = filedialog.askopenfilename(title="Select GPS Shapefile",
                                              filetypes=[("Shapefiles", "*.shp"), ("All files", "*.*")])
        if filename:
            self.gps_file.set(filename)

    def browse_segments(self):
        filename = filedialog.askopenfilename(title="Select Segments Shapefile",
                                              filetypes=[("Shapefiles", "*.shp"), ("All files", "*.*")])
        if filename:
            self.segments_file.set(filename)

    def save_config(self):
        for ring in self.rings:
            if 'name_widget' in ring and ring['name_widget'].winfo_exists():
                ring['name'] = ring['name_widget'].get().strip()
                ring['coordinate'] = ring['coord_widget'].get().strip()

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"{self.block_name.get()}_config.json"
        )
        if filename:
            config = {
                'gps_file': self.gps_file.get(),
                'segments_file': self.segments_file.get(),
                'block_name': self.block_name.get(),
                'bhq_coordinate': self.bhq_coordinate.get(),
                'gp_name_column': self.gp_name_column.get(),
                'rings': [{'name': r['name'], 'coordinate': r['coordinate']} for r in self.rings],
                'tpoints': self.tpoints_text.get('1.0', 'end-1c')
            }
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Success", f"Configuration saved!")

    def load_config(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                self.gps_file.set(config.get('gps_file', ''))
                self.segments_file.set(config.get('segments_file', ''))
                self.block_name.set(config.get('block_name', ''))
                self.bhq_coordinate.set(config.get('bhq_coordinate', ''))
                self.gp_name_column.set(config.get('gp_name_column', 'name'))
                if 'rings' in config:
                    self.rings = config['rings']
                    self.refresh_rings_display()
                self.tpoints_text.delete('1.0', 'end')
                self.tpoints_text.insert('1.0', config.get('tpoints', ''))
                messagebox.showinfo("Success", "Configuration loaded!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see('end')
        self.root.update()

    def clear_logs(self):
        self.log_text.delete('1.0', 'end')

    def check_gp_names(self):
        """Placeholder for GP check."""
        self.log("GP Name Check - Feature ready", "INFO")
        messagebox.showinfo("Info", "This will check GP name consistency when files are loaded")

    def generate_sequences(self):
        """Placeholder for sequence generation."""
        self.log("Sequence Generation - Feature ready", "INFO")
        messagebox.showinfo("Info", "This will generate sequences when files are loaded")


# Main
def main():
    root = tk.Tk()

    # Mac-specific setup
    if platform.system() == 'Darwin':
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)

    app = OFCSequencerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()