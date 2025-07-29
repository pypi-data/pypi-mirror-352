from pathlib import Path
from typing import Optional
import networkx as nx

NODE_COLOR = "#b8d5b8"
ROOT_COLOR = "#ce6c47"

# TODO:
# - Colour the nodes based on out-degree
# - Perhaps colour based on the different analyses?


def generate_dot_data(graph: nx.DiGraph) -> list[str]:
    """
    Generate DOT data for the given dependency graph.

    Args:
        graph: The dependency graph to export.
    """
    graph_to_export = graph

    # Start the DOT file
    dot_data = [
        "digraph DependencyNetwork {",
    ]

    graph_settings = [
        "  graph [",
        "    layout=dot,",  # Use dot layout engine
        "    rankdir=LR,",  # Left to right layout
        "    ranksep=1.0",  # Rank separation
        "    pad=0.5",  # Add padding around the graph (in inches)
        # '    bgcolor="transparent"',  # Set transparent background
        "  ];",
    ]

    node_settings = [
        "  node [",
        "    shape=box,",  # Box shape for nodes
        "    style=filled,",  # Fill nodes with color
        "    fontsize=10",  # Font size
        "  ];",
    ]

    edge_settings = [
        "  edge [",
        "    arrowsize=0.4,",  # Smaller arrowheads
        "    arrowhead=vee",  # Optional: use vee style arrowheads which look cleaner
        '    color="#888888"',  # Grey color for edges
        "    penwidth=0.5,",  # Thinner lines
        "    style=bezier",  # Use bezier curves for smoother edges
        "  ];",
    ]

    edge_handling = [
        "  concentrate=true;",  # Merge edges going to the same destination
        # "  compound=true;",  # Enable edge routing between clusters
        "  mclimit=1.5;",  # Increase iterations for edge crossing minimization
    ]

    # Add all settings to the DOT data
    dot_data.extend(graph_settings)
    dot_data.extend(node_settings)
    dot_data.extend(edge_settings)
    dot_data.extend(edge_handling)

    # Add nodes with attributes
    for node, data in graph_to_export.nodes(data=True):
        node_name = data.get("name", node.split("@")[0])
        node_type = data.get("type", "unknown")

        # Set color based on node type
        if node_type == "root":
            color = ROOT_COLOR
        elif node_type == "dependency":
            color = NODE_COLOR
        else:
            color = "white"

        # Create a label with package name and version
        if "version" in data:
            label = f"{node_name}\\n{data['version']}"
        elif "version_constraint" in data:
            label = f"{node_name}\\n{data['version_constraint']}"
        else:
            label = node_name

        # Escape quotes in node names for DOT format
        safe_node = node.replace('"', '\\"')

        if node_type == "root":
            dot_data.append(
                f'  "{safe_node}" [label="{label}", fillcolor="{color}", style="filled, bold", fontsize=14, padding=4, width=1.5, height=6, penwidth=2];'
            )
        else:
            dot_data.append(f'  "{safe_node}" [label="{label}", fillcolor="{color}"];')

    # Add edges with attributes
    for source, target, data in graph_to_export.edges(data=True):
        edge_type = data.get("type", "unknown")

        # Set edge style based on type
        if edge_type == "installed":
            style = "solid"
        elif edge_type == "required":
            style = "dashed"
        else:
            style = "dotted"

        # Escape quotes in node names for DOT format
        safe_source = source.replace('"', '\\"')
        safe_target = target.replace('"', '\\"')

        dot_data.append(f'  "{safe_source}" -> "{safe_target}" [style={style}];')

    dot_data.append("}")
    return dot_data


def export_to_dot(graph: nx.DiGraph, output_file: Optional[Path]):
    """
    Export the dependency graph to a DOT file.

    Args:
        graph: The dependency graph to export.
        output_file: The path to the output DOT file.
    """
    dot_data = "\n".join(generate_dot_data(graph))
    if not output_file:
        print(dot_data)
        return

    # Write to file
    with open(output_file, "w") as f:
        f.write(dot_data)
        print(f"DOT file exported to {output_file}")
