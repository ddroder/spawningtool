import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parser import parse_replay
import sc2reader
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.colors as mcolors

# Include the parse_replay function here
# (Copy the entire parse_replay function from the original code)

def get_player_info(parsed_data):
    player_info = {}
    for player_id, player_data in parsed_data['players'].items():
        player_info[player_id] = {
            'name': player_data['name'],
            'race': player_data['race'],
            'is_winner': player_data['is_winner']
        }
    return player_info

def create_tech_path_visualization(parsed_data, player_id):
    build_order = parsed_data['players'][player_id]['buildOrder']
    
    G = nx.DiGraph()
    node_colors = []
    node_sizes = []
    edge_labels = {}
    
    # Create nodes and edges
    for i, item in enumerate(build_order):
        name = item['name']
        time = float(item['time'].replace(':', '.'))
        
        if name not in G.nodes():
            G.add_node(name, time=time)
            node_colors.append(time)
            node_sizes.append(1000)  # Base size
        else:
            node_sizes[list(G.nodes()).index(name)] += 500  # Increase size for repeated nodes
        
        if i > 0:
            prev_name = build_order[i-1]['name']
            G.add_edge(prev_name, name)
            edge_labels[(prev_name, name)] = f"{time:.2f}"
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(20, 12))
    
    # Use a hierarchical layout
    pos = nx.spring_layout(G, k=0.9, iterations=50)
    
    # Adjust x-coordinates based on build order
    for i, (node, coords) in enumerate(pos.items()):
        coords[0] = G.nodes[node]['time']
    
    # Normalize x-coordinates
    x_values = [coord[0] for coord in pos.values()]
    x_min, x_max = min(x_values), max(x_values)
    for node, coords in pos.items():
        coords[0] = (coords[0] - x_min) / (x_max - x_min)
    
    # Color map
    color_map = plt.colormaps['cool']
    norm = mcolors.Normalize(vmin=min(node_colors), vmax=max(node_colors))
    
    # Draw the graph
    nx.draw(G, pos, ax=ax, with_labels=True, node_color=[color_map(norm(c)) for c in node_colors], 
            node_size=node_sizes, font_size=8, font_weight='bold', 
            arrows=True, edge_color='gray', width=0.5, arrowsize=10)

    # Add edge labels
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=color_map, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, label='Time (minutes)', orientation='vertical', pad=0.1)

    # Set title and remove axis
    ax.set_title(f"Tech Path for Player {player_id}")
    ax.axis('off')
    
    # Save the plot
    filename = f"tech_path_player_{player_id}_left_to_right.png"
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Left-to-right visualization saved as '{filename}'")



def visualize_tech_path(replay_file, player_id):
    parsed_data = parse_replay(replay_file)
    create_tech_path_visualization(parsed_data, player_id)

# Main execution
if __name__ == "__main__":
    replay_file="/mnt/c/Users/ddroder/Documents/StarCraft II/Accounts/351383877/1-S2-1-13090078/Replays/Multiplayer/Alcyone LE (2).SC2Replay"
    #replay_file = input("Enter the path to your SC2 replay file: ")

    parsed_data = parse_replay(replay_file)
    player_info = get_player_info(parsed_data)

    print("Player Information:")
    for player_id, info in player_info.items():
        print(f"Player ID: {player_id}")
        print(f"Name: {info['name']}")
        print(f"Race: {info['race']}")
        print(f"Winner: {'Yes' if info['is_winner'] else 'No'}")
        print()

    #chosen_player_id = input("Enter the ID of the player whose tech path you want to visualize: ")
    chosen_player_id=1
    visualize_tech_path(replay_file, int(chosen_player_id))
