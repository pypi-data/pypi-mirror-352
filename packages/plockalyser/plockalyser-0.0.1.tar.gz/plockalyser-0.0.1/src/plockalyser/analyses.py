from dataclasses import dataclass
from typing import Iterable, Optional
import networkx as nx
from networkx import find_cycle
import numpy as np

from plockalyser.markdown import generate_markdown_table, table_margin_marker

TOP_X_TO_SHOW = 20
BOTTOM_X_TO_SHOW = 10


def analyse_connectivity(graph: nx.DiGraph) -> str:
    """Analyse the degree of connectivity in the network."""
    assert callable(graph.degree)
    degrees = dict(graph.degree())
    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())

    # Sort by total degree
    sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)

    output: list[str] = []
    marker = "degree_of_connectivity"
    output.append(f"\n<!-- BEGIN {marker} -->")

    output.append(f"table: Degree of connectivity per package {{#tbl:{marker}}}\n")
    output.append("| Package | In | Out | Tot. |")
    # First column really wide to make the table full-width with Pandoc/LaTeX.
    output.append(
        "|--------------------------------------------------------------------|-----:|-----:|-----:|"
    )
    for i, (pkg, degree) in enumerate(sorted_degrees[:TOP_X_TO_SHOW], 1):
        output.append(
            f"| {table_margin_marker(i)}`{pkg}` | {in_degrees[pkg]} | {out_degrees[pkg]} | {degree} |"
        )
    output.append(f"\n<!-- END {marker} -->")
    return "\n".join(output)


def analyse_closeness(graph: nx.DiGraph) -> str:
    closeness_in = nx.closeness_centrality(graph)
    # reverse to get the out links (the dependencies)
    closeness_out = nx.closeness_centrality(graph.reverse())
    sorted_closeness_in = sorted(closeness_in.items(), key=lambda x: x[1], reverse=True)
    sorted_closeness_out = sorted(
        closeness_out.items(), key=lambda x: x[1], reverse=True
    )

    output: list[str] = []
    output.append(
        generate_markdown_table(
            "closeness_centrality_in",
            sorted_closeness_in[:TOP_X_TO_SHOW],
            "Closeness centrality -- dependents, highest",
        )
    )

    output.append(
        generate_markdown_table(
            "closeness_centrality_in_lowest",
            sorted_closeness_in[-BOTTOM_X_TO_SHOW:],
            "Closeness centrality -- dependents, lowest",
        )
    )

    output.append(
        generate_markdown_table(
            "closeness_centrality_out",
            sorted_closeness_out[:TOP_X_TO_SHOW],
            "Closeness centrality -- dependencies, highest",
        )
    )

    output.append(
        generate_markdown_table(
            "closeness_centrality_out_lowest",
            [(p, s) for p, s in sorted_closeness_out if s > 0][-BOTTOM_X_TO_SHOW:],
            "Closeness centrality -- dependencies, lowest non-zero",
        )
    )

    return "\n".join(output)


def analyse_betweenness(graph: nx.DiGraph) -> str:
    betweenness_directed = nx.betweenness_centrality(graph)
    betweenness_undirected = nx.betweenness_centrality(graph.to_undirected())
    sorted_betweenness_directed = sorted(
        betweenness_directed.items(), key=lambda x: x[1], reverse=True
    )
    sorted_betweenness_undirected = sorted(
        betweenness_undirected.items(), key=lambda x: x[1], reverse=True
    )

    output: list[str] = []

    output.append(
        generate_markdown_table(
            "betweenness_centrality_directed",
            sorted_betweenness_directed[:TOP_X_TO_SHOW],
            "Betweenness centrality -- directed",
        )
    )

    output.append(
        generate_markdown_table(
            "betweenness_centrality_undirected",
            sorted_betweenness_undirected[:TOP_X_TO_SHOW],
            "Betweenness centrality -- undirected",
        )
    )

    return "\n".join(output)


def analyse_pagerank(graph: nx.DiGraph) -> str:
    pagerank = nx.pagerank(graph)  # PageRank as a prestige metric
    sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)

    output: list[str] = []
    output.append(
        generate_markdown_table(
            "pagerank_centrality",
            sorted_pagerank[:TOP_X_TO_SHOW],
            "Prestige centrality (PageRank algorithm)",
        )
    )
    return "\n".join(output)


def analyse_centrality(graph: nx.DiGraph) -> str:
    output: list[str] = []
    output.append(analyse_closeness(graph))
    output.append(analyse_betweenness(graph))
    output.append(analyse_pagerank(graph))
    return "\n\n".join(output)


@dataclass
class DependencyNetworkStats:
    """Statistics about a dependency network."""

    nodes: int
    edges: int
    direct_dependencies: Optional[int]
    max_path_length: int
    avg_path_length: float
    clustering: float
    density: float
    packages_with_more_than_one_version: int


def get_summary_statistics(graph: nx.DiGraph) -> DependencyNetworkStats:
    """Get summary statistics about the dependency network."""
    # Basic stats
    nodes = graph.number_of_nodes()
    edges = graph.number_of_edges()

    # Find which packages that have more than one version:
    version_count: dict[str, int] = {}
    for node, nodedata in graph.nodes.items():
        if nodedata["name"] in version_count:
            version_count[nodedata["name"]] += 1
        else:
            version_count[nodedata["name"]] = 1
    more_than_one_version = {k: v for k, v in version_count.items() if v > 1}

    # Find loops. Just print them out for now.
    loops = find_cycle(graph)
    print(f"{loops=}")

    # Find the root node (should have in_degree of 0)
    root_nodes = [node for node in graph.nodes() if graph.in_degree(node) == 0]
    assert len(root_nodes) == 1
    root_node = root_nodes[0]  # Assume the first root node is the main one
    # Count direct dependencies (distance 1 from root)
    direct_deps = list(graph.successors(root_node))
    direct_dependencies = len(direct_deps)

    # Connected components in the undirected graph
    undirected = graph.to_undirected()
    connected_components = list(nx.connected_components(undirected))

    # Average path length (only for the largest component to avoid errors)
    largest_cc = max(connected_components, key=len)
    largest_subgraph = undirected.subgraph(largest_cc)
    max_path_length = nx.diameter(largest_subgraph)
    avg_path_length = nx.average_shortest_path_length(largest_subgraph)

    # Clustering coefficient
    clustering = nx.average_clustering(undirected)

    # Density
    density = nx.density(graph)

    return DependencyNetworkStats(
        nodes=nodes,
        edges=edges,
        direct_dependencies=direct_dependencies,
        max_path_length=max_path_length,
        avg_path_length=avg_path_length,
        clustering=clustering,
        density=density,
        packages_with_more_than_one_version=len(more_than_one_version),
    )


def format_summary_statistics(stats: DependencyNetworkStats) -> str:
    """Print summary statistics about the dependency network."""

    output: list[str] = []
    marker = "basic_stats"

    # Basic stats
    output.append(f"\n<!-- BEGIN {marker} -->\n")
    output.append("table: Basic network statistics {#tbl:basic_stats}\n")
    output.append("| Basic statistics | Value |")
    output.append("|-------|-------:|")
    output.append(f"| Number of packages (nodes) | {stats.nodes} |")
    output.append(f"| Number of dependencies (edges) | {stats.edges} |")
    # Direct dependencies
    if stats.direct_dependencies is not None:
        output.append(
            f"| Number of direct dependencies of `root` | {stats.direct_dependencies} |"
        )
    else:
        output.append(
            "| Number of direct dependencies of `root` | Warning: No `root` node found |"
        )
    output.append(f"| Maximum path length | {stats.max_path_length} |")
    output.append(
        f"| Packages with more than one version | {stats.packages_with_more_than_one_version} |"
    )
    output.append(f"\n<!-- END {marker} -->\n")
    return "\n".join(output)


def calculate_gini_coefficients(data: Iterable[float]) -> float:
    """Calculate the Gini coefficient for the data.

    The Gini coefficient measures inequality in a distribution.
    A value of 0 represents perfect equality, while 1 represents maximum inequality.
    """
    values = sorted(data)
    n = len(values)

    # If there are no values or only one value, return 0 (perfect equality)
    if n <= 1:
        return 0.0

    # Slightly adapted from https://stackoverflow.com/a/61154922

    x = np.array(data)
    diffsum: float = 0
    for i, xi in enumerate(x[:-1], 1):
        diffsum += np.sum(np.abs(xi - x[i:]))

    return diffsum / (len(x) ** 2 * np.mean(x, dtype=np.float64))


def format_gini(graph: nx.DiGraph) -> str:
    """Print Gini coefficients for some of the graph's measures."""

    data: list[tuple[str, float]] = []

    # Closeness (dependencies)
    closeness_out = nx.closeness_centrality(graph.reverse())
    gini_closeness_out = calculate_gini_coefficients(
        [v for v in closeness_out.values()]
    )
    data.append(("Closeness (dependencies)", gini_closeness_out))

    # Degree of connectivity (out-degree/dependencies)
    out_degree = graph.out_degree()
    assert type(out_degree) is not int
    gini_out_degree = calculate_gini_coefficients([v for _, v in out_degree])
    data.append(("Degree of connectivity (dependencies)", gini_out_degree))

    # Prestige (PageRank)
    pagerank = nx.pagerank(graph)
    gini_pagerank = calculate_gini_coefficients([v for v in pagerank.values()])
    data.append(("Prestige (PageRank)", gini_pagerank))

    id = "gini_coefficients"
    caption = "Gini coefficients"

    output: list[str] = []

    output.append(f"\n<!-- BEGIN {id} -->")
    output.append(f"table: {caption} {{#tbl:{id}}}\n")
    output.append("| Measure | Gini coefficient |")
    # output.append(f"|{FULL_WIDTH_HEADER_SEPARATOR}|------:|")
    output.append("|------|------:|")
    for i, (pkg, score) in enumerate(data, 1):
        output.append(f"| {pkg} | {score:.4f} |")
    output.append(f"\n<!-- END {id} -->")

    return "\n".join(output)
