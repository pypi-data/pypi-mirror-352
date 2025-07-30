import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import os


def visualize_multi_agent_trajectory(trajectory, filename="output/multi_agent_trajectory.png"):
    """
    Visualize a multi-agent trajectory as a directed graph.

    Args:
        trajectory: Multi-agent trajectory in flattened format
        filename: Path to save the visualization
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    graph = nx.DiGraph()
    node_colors = {}
    agent_to_color = {}
    current_agent = None
    prev_node = None

    color_palette = sns.color_palette("pastel").as_hex()
    color_index = 0

    for item in trajectory:
        if item.endswith("_agent"):
            current_agent = item.replace("_agent", "")
            if current_agent not in agent_to_color:
                agent_to_color[current_agent] = color_palette[color_index % len(color_palette)]
                color_index += 1
        else:
            graph.add_node(item)
            node_colors[item] = agent_to_color.get(current_agent, "lightgray")

            if prev_node:
                graph.add_edge(prev_node, item)

            prev_node = item

    # Visualization
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(graph, seed=42)

    # Draw nodes with colors
    for node, color in node_colors.items():
        nx.draw_networkx_nodes(graph, pos, nodelist=[node], node_color=color, alpha=0.7, node_size=700)

    # Draw edges
    nx.draw_networkx_edges(graph, pos, edgelist=graph.edges(), edge_color='black', width=2, alpha=0.7)

    # Draw labels
    nx.draw_networkx_labels(graph, pos, font_size=10, font_family='sans-serif', font_weight='bold')

    # Legend
    agent_patches = [
        plt.Line2D([0], [0], marker='o', color='w',
                   markerfacecolor=color, markersize=15, label=agent)
        for agent, color in agent_to_color.items()
    ]
    plt.legend(handles=agent_patches, loc='upper right')

    plt.title("Multi-Agent Trajectory", fontsize=20, fontweight='bold')
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()
    plt.close()

    print(f"Visualization saved to {filename}")



def visualize_given_graph(graph: nx.DiGraph, filename: str):
    pos = nx.spring_layout(graph, seed=42)  
    plt.figure(figsize=(14, 10))

    node_size = [500 + 100 * graph.degree(n) for n in graph.nodes()]
    nx.draw_networkx_nodes(graph, pos, node_size=node_size, node_color='lightcoral', alpha=0.7)
    nx.draw_networkx_edges(graph, pos, edge_color='black', width=2, alpha=0.7)
    nx.draw_networkx_labels(graph, pos, font_size=14, font_family='sans-serif', font_weight='bold', font_color='darkblue')

    plt.title("Tool Dependency Graph", fontsize=20, fontweight='bold', family='Arial', color='darkblue')
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()

