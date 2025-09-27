import math


class RingDiagramGenerator:
    def __init__(self, width=800, height=600, main_ring_radius=200):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.radius = main_ring_radius
        self.main_nodes_map = {}  # Stores node name -> (x, y) coordinates
        self.main_ring_points = []

    def calculate_main_ring_coords(self, node_names):
        """Calculates coordinates for N nodes arranged in a circle."""
        N = len(node_names)
        self.main_nodes_map = {}
        self.main_ring_points = []

        # Start angle (offset by 90 deg to put the first node at the top)
        start_angle = math.pi / 2

        for i, name in enumerate(node_names):
            angle = start_angle + (i * 2 * math.pi / N)
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y - self.radius * math.sin(angle)  # Subtract for SVG Y-axis

            # Rounding for clean SVG output
            x, y = round(x), round(y)

            self.main_nodes_map[name] = (x, y)
            self.main_ring_points.append(f"{x},{y}")

    def get_child_ring_coords(self, start_node, end_node, offset_distance=100):
        """Calculates coordinates for a simple child ring path."""

        if start_node not in self.main_nodes_map or end_node not in self.main_nodes_map:
            raise ValueError("Child ring nodes must be present in the main ring.")

        x1, y1 = self.main_nodes_map[start_node]
        x2, y2 = self.main_nodes_map[end_node]

        # 1. Find midpoint (P_mid) of the span
        x_mid, y_mid = (x1 + x2) / 2, (y1 + y2) / 2

        # 2. Find the vector perpendicular to the span (V_perp)
        # Vector V_span: (x2 - x1, y2 - y1)
        # Perpendicular vector V_perp: (y1 - y2, x2 - x1)
        dx_perp, dy_perp = y1 - y2, x2 - x1

        # 3. Normalize V_perp
        length = math.sqrt(dx_perp ** 2 + dy_perp ** 2)
        if length == 0: return []
        dx_unit, dy_unit = dx_perp / length, dy_perp / length

        # 4. Calculate the 'peak' point (P_peak) for the child ring
        # P_peak = P_mid + V_unit * offset_distance
        x_peak = x_mid + dx_unit * offset_distance
        y_peak = y_mid + dy_unit * offset_distance

        # Ensure the child ring points outward relative to the center
        # We need a simple check: if P_peak is closer to the center than P_mid, flip the direction
        dist_mid_to_center = math.sqrt((x_mid - self.center_x) ** 2 + (y_mid - self.center_y) ** 2)
        dist_peak_to_center = math.sqrt((x_peak - self.center_x) ** 2 + (y_peak - self.center_y) ** 2)

        # If the peak moved inward (closer to center), flip it
        if dist_peak_to_center < dist_mid_to_center:
            x_peak = x_mid - dx_unit * offset_distance
            y_peak = y_mid - dy_unit * offset_distance

        # For a simple diagram, use two main points and one peak point
        child_points = [(x1, y1), (round(x_peak), round(y_peak)), (x2, y2)]
        return child_points

    def generate_svg(self, main_node_names, child_rings_data):
        """Generates the full SVG string."""

        self.calculate_main_ring_coords(main_node_names)

        svg_template = f"""
<svg width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}" xmlns="http://www.w3.org/2000/svg">
    <title>Dynamic OFC Ring Diagram</title>

    <style>
        .main-ring-line {{ stroke: #0077b6; stroke-width: 3; fill: none; }}
        .child-ring-line {{ stroke: #00b894; stroke-width: 2; fill: none; stroke-dasharray: 6 3; }}
        .node {{ fill: #d63031; stroke: white; stroke-width: 1.5; }}
        .node-label {{ font-family: Arial, sans-serif; font-size: 14px; fill: #333; text-anchor: middle; }}
        .ring-label {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #555; text-anchor: middle; }}
    </style>

    <polyline 
        class="main-ring-line" 
        points="{' '.join(self.main_ring_points)} {self.main_ring_points[0]}" 
    />
    <text x="{self.center_x}" y="{self.center_y - self.radius + 30}" class="ring-label">R1 (Main Ring)</text>

    """
        # Add Child Rings
        for i, child in enumerate(child_rings_data):
            name, start, end = child['name'], child['start'], child['end']

            try:
                child_coords = self.get_child_ring_coords(start, end, offset_distance=70 + i * 30)

                # Format coordinates for SVG path
                d_path = f"M {child_coords[0][0]},{child_coords[0][1]} L {child_coords[1][0]},{child_coords[1][1]} L {child_coords[2][0]},{child_coords[2][1]}"

                svg_template += f"""
    <path 
        class="child-ring-line" 
        d="{d_path}" 
    />
    <text x="{child_coords[1][0]}" y="{child_coords[1][1] - 10}" class="node-label" style="fill: #00b894; font-weight: bold;">{name}</text>
"""
            except ValueError as e:
                print(f"Error drawing child ring {name}: {e}")

        svg_template += "\n    \n"

        # Add Nodes and Labels
        for name, (x, y) in self.main_nodes_map.items():
            svg_template += f"""
    <circle class="node" cx="{x}" cy="{y}" r="8" />
    <text class="node-label" x="{x}" y="{y - 15}">{name}</text>
"""

        svg_template += "\n</svg>"
        return svg_template


# --- Example Usage ---

# Define Main Ring Nodes (N nodes)
# N=4 is simple to visualize, but it works for any N >= 3
main_nodes = ['A', 'B', 'C', 'D', 'E', 'F']

# Define Child Rings (X rings)
# start and end must be node names from main_nodes
child_rings = [
    # R1-C1 starts at B and ends at C
    {'name': 'R1-C1', 'start': 'B', 'end': 'C'},

    # R1-C2 starts at D and ends at E
    {'name': 'R1-C2', 'start': 'D', 'end': 'E'},

    # R1-C3 starts at F and ends at A
    {'name': 'R1-C3', 'start': 'F', 'end': 'A'},
]

# 1. Create the generator instance
generator = RingDiagramGenerator(width=800, height=600, main_ring_radius=250)

# 2. Generate the SVG string
svg_output = generator.generate_svg(main_nodes, child_rings)

# 3. Save the output to an SVG file
file_name = "ring_diagram.svg"
with open(file_name, "w") as f:
    f.write(svg_output)

print(f"SVG generated successfully! Check '{file_name}' to view the diagram.")