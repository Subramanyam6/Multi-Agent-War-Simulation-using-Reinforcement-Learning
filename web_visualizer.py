#!/usr/bin/env python3
"""
Web-based Visualization for Multi-Agent War Simulation using Matplotlib
Shows the health of each agent as animated bars in a browser-compatible format
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rcParams
import numpy as np
import time
import io
import base64
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle
from matplotlib.path import Path
import matplotlib.patches as patches

# Import necessary components with correct package paths
from CodeBase.Environment import Environment
from CodeBase.GameStatusUpdate import GameStatusUpdate
from CodeBase.Settings import Settings
from CodeBase.Agent import Agent
from CodeBase.Simulation import Simulation

# Colors
BACKGROUND = '#14141E'  # Dark blue background
PANEL_BG = '#1E1E28'    # Slightly lighter panel background
COLORS = [
    '#FF6464',  # Red
    '#64FF64',  # Green
    '#6464FF',  # Blue
    '#FFFF64',  # Yellow
    '#FF64FF',  # Magenta
]
TEXT_COLOR = '#DCDCDC'  # Light gray text
TEXT_SECONDARY = '#B4B4B4'  # Slightly darker gray text
RL_COLOR = '#FFD700'       # Gold for RL
HEURISTIC_COLOR = '#00BFFF' # Deep Sky Blue for Heuristic
RANDOM_COLOR = '#C8C8C8'    # Light gray for Random
ALLIANCE_COLOR = '#FFA500'  # Orange for alliance indicator

class WebSimulationVisualizer:
    def __init__(self, simulation):
        self.simulation = simulation
        self.env = simulation.env
        self.num_agents = self.env.number_of_agents
        
        # Figure setup - make it fit the container properly
        plt.style.use('dark_background')
        
        # More drastic adjustments to ensure visibility
        # Adjust figure size for better proportions - wider for more agents
        width = max(8, 5 + self.num_agents * 0.5)  # Scale width based on agent count
        self.fig = plt.figure(figsize=(width, 7), facecolor=BACKGROUND)
        
        # Increase left margin further to ensure axis labels are visible
        left_margin = 0.15
        right_margin = 0.95
        top_margin = 0.85
        bottom_margin = 0.2
        
        self.fig.subplots_adjust(left=left_margin, right=right_margin, top=top_margin, bottom=bottom_margin)
        
        # Main plot for health bars
        self.ax_main = self.fig.add_subplot(111)
        self.ax_main.set_facecolor(BACKGROUND)
        self.ax_main.set_title('Multi-Agent War Simulation', color=TEXT_COLOR, fontsize=16, pad=15)
        
        # Ensure tick labels are fully visible
        self.ax_main.tick_params(axis='both', colors=TEXT_COLOR, labelsize=9)
        
        # Animation settings
        self.step = 0
        self.paused = False
        
        # Agent type colors
        self.agent_type_colors = {
            "RL": RL_COLOR,
            "Heuristic": HEURISTIC_COLOR,
            "Random": RANDOM_COLOR
        }
        
        # Agent icons (small colored circles)
        self.agent_icons = {}
        for i, agent in enumerate(self.env.agents_list):
            color = self.agent_type_colors[agent.agent_type]
            self.agent_icons[agent.agent_id] = color
            
        # Bar chart settings
        self.bar_width = 0.6
        self.max_bar_height = 2.0  # Max health
        
        # Set up the plot
        self.setup_plot()
        
    def setup_plot(self):
        """Set up the initial plot layout"""
        # Add more horizontal padding to prevent cutting off
        self.ax_main.set_xlim(-0.7, self.num_agents - 0.3)
        self.ax_main.set_ylim(0, self.env.max_health * 1.1)  # Add 10% margin at top
        
        # Set tick positions and labels
        self.ax_main.set_xticks(range(self.num_agents))
        self.ax_main.set_xticklabels([f'Agent {i}' for i in range(self.num_agents)])
        
        # Rotate x-axis labels slightly if there are many agents
        if self.num_agents > 6:
            for tick in self.ax_main.get_xticklabels():
                tick.set_rotation(15)
        
        # Set y-axis label with sufficient padding
        self.ax_main.set_ylabel('Health', color=TEXT_COLOR, fontsize=12, labelpad=10)
        
        # Create initial bars with zero height
        self.bars = []
        self.bar_colors = []
        self.alliance_lines = []
        self.agent_circles = []
        self.agent_labels = []
        self.health_labels = []
        
        for i, agent in enumerate(self.env.agents_list):
            # Create bar
            color = self.agent_type_colors[agent.agent_type]
            bar = self.ax_main.bar(i, 0, width=self.bar_width, color=color, alpha=0.7)[0]
            self.bars.append(bar)
            self.bar_colors.append(color)
            
            # Create agent type indicator (colored circle)
            circle = Circle((i, -0.15), 0.1, color=color)
            self.ax_main.add_patch(circle)
            self.agent_circles.append(circle)
            
            # Add agent type label
            agent_type_label = self.ax_main.text(i, -0.3, agent.agent_type, 
                                               ha='center', va='center', 
                                               color=TEXT_COLOR, fontsize=8)
            self.agent_labels.append(agent_type_label)
            
            # Add health value label
            health_label = self.ax_main.text(i, 0.1, '0.0', 
                                           ha='center', va='bottom', 
                                           color=TEXT_COLOR, fontsize=10)
            self.health_labels.append(health_label)
        
        # Draw title
        self.ax_main.set_title('Multi-Agent War Simulation', color=TEXT_COLOR, fontsize=16)
        
        # Add step counter text and alive counter in top-left corner with background box for better visibility
        info_box = dict(boxstyle="round,pad=0.3", facecolor=PANEL_BG, alpha=0.7, edgecolor='none')
        
        self.step_text = self.ax_main.text(0.02, 0.95, 'Step: 0', 
                                         ha='left', va='center', 
                                         color=TEXT_COLOR, fontsize=10,
                                         transform=self.ax_main.transAxes,
                                         bbox=info_box)
        
        self.alive_text = self.ax_main.text(0.02, 0.90, f'Alive: {self.num_agents}/{self.num_agents}', 
                                          ha='left', va='center', 
                                          color=TEXT_COLOR, fontsize=10,
                                          transform=self.ax_main.transAxes,
                                          bbox=info_box)
        
    def update_plot(self, frame):
        """Update the plot for animation"""
        if self.paused:
            return self.bars + self.alliance_lines
        
        # Update simulation state
        if not self.simulation.game_is_on:
            # If game is over, stop animation
            self.paused = True
            return self.bars + self.alliance_lines
            
        self.simulation.update_time_step()
        self.step += 1
        
        # Update step counter
        self.step_text.set_text(f'Step: {self.step}')
        
        # Update alive agents count
        alive_count = sum(1 for agent in self.env.agents_list if agent.is_alive)
        self.alive_text.set_text(f'Alive: {alive_count}/{self.num_agents}')
        
        # Clear previous alliance lines
        for line in self.alliance_lines:
            line.remove()
        self.alliance_lines = []
        
        # Update health bars and alliance lines
        for i, agent in enumerate(self.env.agents_list):
            if agent.is_alive:
                health = agent.health_list[agent.agent_id]
                self.bars[i].set_height(health)
                self.health_labels[i].set_text(f'{health:.1f}')
                self.health_labels[i].set_position((i, health + 0.1))
                
                # Draw alliance line if exists
                if agent.alliance_pair is not None:
                    ally_id = agent.alliance_pair.agent_id
                    # Only draw the alliance line once (from lower ID to higher)
                    if i < ally_id:
                        # Calculate bar positions - these are the centers of the bars
                        bar1_x = i
                        bar2_x = ally_id
                        bar_bottom = 0  # Bottom of the health bars
                        
                        # Create a modern curved connection between the bars
                        # Using ConnectionPatch for a sleek curved look
                        connection = patches.ConnectionPatch(
                            xyA=(bar1_x, bar_bottom),  # Start at bottom of first bar
                            xyB=(bar2_x, bar_bottom),  # End at bottom of second bar
                            coordsA='data',
                            coordsB='data',
                            axesA=self.ax_main,
                            axesB=self.ax_main,
                            arrowstyle='-',            # No arrow heads
                            connectionstyle='arc3,rad=0.3',  # Curved connection
                            color='#FF8800',           # Bright orange color
                            linewidth=3,               # Thick line for visibility
                            linestyle=(0, (5, 2)),     # Dotted line pattern
                            zorder=90,                 # High z-order
                            alpha=1.0                  # Full opacity
                        )
                        
                        # Add the connection to the plot
                        self.ax_main.add_artist(connection)
                        self.alliance_lines.append(connection)
                        
                        # Add small circular indicators at the connection points
                        circle1 = Circle((bar1_x, bar_bottom), radius=0.05, 
                                        facecolor='#FF8800', edgecolor='white', 
                                        linewidth=1, alpha=1.0, zorder=91)
                        circle2 = Circle((bar2_x, bar_bottom), radius=0.05,
                                        facecolor='#FF8800', edgecolor='white',
                                        linewidth=1, alpha=1.0, zorder=91)
                                        
                        self.ax_main.add_patch(circle1)
                        self.ax_main.add_patch(circle2)
                        self.alliance_lines.append(circle1)
                        self.alliance_lines.append(circle2)
            else:
                # Agent is dead
                self.bars[i].set_height(0.05)  # Small bar to indicate death
                self.bars[i].set_color(COLORS[0])  # Red for dead
                self.health_labels[i].set_text('DEAD')
                self.health_labels[i].set_position((i, 0.1))
                self.health_labels[i].set_color(COLORS[0])
        
        return self.bars + self.alliance_lines
        
    def on_key_press(self, event):
        """Handle key press events"""
        if event.key == ' ':
            self.paused = not self.paused
        elif event.key == 'escape':
            plt.close()
    
    def run(self):
        """Run the animation"""
        # Connect key press handler
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # Create animation
        ani = animation.FuncAnimation(
            self.fig, self.update_plot, interval=500, save_count=self.simulation.max_iteration
        )
        plt.show()
    
    def save_animation(self, filename='simulation.mp4'):
        """Save the animation to a file"""
        ani = animation.FuncAnimation(
            self.fig, self.update_plot, frames=self.simulation.max_iteration
        )
        ani.save(filename, writer='ffmpeg', fps=1)
        print(f"Animation saved to {filename}")
        
    def get_html_animation(self):
        """
        Return a self‑contained <div> with JS playback instead of a video file.
        Works on Safari, Chrome, Edge, etc.
        """
        # Pre-compute all frames to avoid delay and ensure smooth playback
        frames_data = []
        max_frames = min(100, self.simulation.max_iteration)  # Limit total frames for performance
        
        # Store initial state
        frames_data.append(self.capture_current_state())
        
        # Track if game completed naturally
        natural_completion = False
        
        # Run simulation steps and capture each state
        for _ in range(max_frames-1):
            if not self.simulation.game_is_on:
                natural_completion = True
                break
            self.simulation.update_time_step()
            self.step += 1  # Increment step counter here
            frames_data.append(self.capture_current_state())
        
        # If we hit the frame limit but game isn't over, keep running until completion
        if not natural_completion and self.simulation.game_is_on:
            while self.simulation.game_is_on and _ < self.simulation.max_iteration * 1.5:  # Safety limit
                self.simulation.update_time_step()
                self.step += 1  # Increment step counter here
                _ += 1
                # Only capture a few more frames to prevent massive animations
                if _ < max_frames + 10:
                    frames_data.append(self.capture_current_state())
        
        # Add a final frame that stays visible longer if simulation ended
        if len(frames_data) > 0:
            # Duplicate the last frame 3 times to make it stay visible longer
            final_state = frames_data[-1]
            
            # Add game over information to the final state
            if not self.simulation.game_is_on:
                # Get list of alive agents
                alive_agents = [agent for agent in self.env.agents_list if agent.is_alive]
                
                # Create game over message
                game_over_message = "GAME OVER"
                if len(alive_agents) == 1:
                    # Single winner
                    winner = alive_agents[0]
                    game_over_message += f"\nWinner: Agent {winner.agent_id} ({winner.agent_type})"
                elif len(alive_agents) == 2 and alive_agents[0].alliance_pair == alive_agents[1]:
                    # Alliance winners
                    game_over_message += f"\nAlliance Winners: Agent {alive_agents[0].agent_id} ({alive_agents[0].agent_type}) & Agent {alive_agents[1].agent_id} ({alive_agents[1].agent_type})"
                else:
                    # Multiple survivors
                    agent_info = [f"Agent {agent.agent_id} ({agent.agent_type})" for agent in alive_agents]
                    game_over_message += f"\nSurvivors: {', '.join(agent_info)}"
                
                # Add game over message to the final state
                final_state['game_over_message'] = game_over_message
            
            # Add 20 duplicates of the final frame to create a 5-second pause (250ms per frame * 20 = 5000ms)
            for _ in range(20):
                frames_data.append(final_state)
        
        # Ensure we have at least some frames
        if len(frames_data) < 2:
            # Generate at least one more frame to have animation
            if self.simulation.game_is_on:
                self.simulation.update_time_step()
            frames_data.append(self.capture_current_state())
        
        # Define frame update function that uses pre-computed states
        def animation_update(frame_idx):
            # Use modulo to loop through frames if we run out
            idx = min(frame_idx, len(frames_data)-1)
            return self.apply_state(frames_data[idx])
        
        # Set figure DPI for better sizing in browser
        self.fig.set_dpi(100)
        
        # Build the animation with pre-computed states
        anim = animation.FuncAnimation(
            self.fig,
            animation_update,
            frames=len(frames_data),
            interval=250,  # 250ms per frame (4 frames per second)
            blit=False,
            repeat=True   # Enable looping
        )

        # Use the JavaScript HTML backend with customizations
        rcParams['animation.html'] = 'jshtml'
        rcParams['animation.embed_limit'] = 100_000_000  # 100 MB to ensure full animation works
        
        # Get the HTML output
        html_output = anim.to_jshtml()
        
        # Insert custom CSS to make controls more visible and improve sizing
        custom_css = """
        <style>
        .animation-container {
            width: 100% !important;
            max-width: 100% !important;
            height: auto !important;
            margin: 0 auto !important;
            overflow: visible !important;
        }
        .animation-container button {
            background-color: #444 !important;
            color: white !important;
            border: 1px solid #666 !important;
            padding: 5px 10px !important;
            margin: 5px !important;
            font-size: 14px !important;
            border-radius: 4px !important;
            cursor: pointer !important;
            display: inline-block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        .animation-container img, .animation-container canvas {
            max-width: 100% !important;
            width: auto !important; 
            height: auto !important;
            margin: 0 auto !important;
            display: block !important;
        }
        /* Ensure the figure has proper spacing */
        .matplotlib-figure {
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }
        /* Make sure the SVG doesn't get clipped */
        svg.matplotlib-canvas {
            overflow: visible !important;
            max-width: 100% !important;
        }
        </style>
        """
        
        # Add custom JavaScript for message handling
        custom_js = """
        <script>
        // Listen for messages from parent window
        window.addEventListener('message', function(event) {
            // Find the animation object
            var animDivs = document.querySelectorAll('div[id^="animation_"]');
            if (animDivs.length > 0) {
                var animId = animDivs[0].id.replace('animation_', '');
                var animObj = window['anim_' + animId];
                
                if (animObj) {
                    if (event.data === 'play') {
                        animObj.play();
                    } else if (event.data === 'pause') {
                        animObj.pause();
                    } else if (event.data === 'reload') {
                        animObj.pause();
                        animObj.frame(0);
                        setTimeout(function() {
                            animObj.play();
                        }, 100);
                    }
                }
            }
        });
        </script>
        """
        
        # Insert the custom CSS and JS into the animation HTML
        html_output = html_output.replace('</div>', custom_css + custom_js + '</div>')
        
        return html_output

    def capture_current_state(self):
        """Capture the current state of the simulation for animation"""
        state = {
            'step': self.step,
            'agents': []
        }
        
        # Store alive count for sidebar
        state['alive_count'] = sum(1 for agent in self.env.agents_list if agent.is_alive)
        
        # Store agent states
        for agent in self.env.agents_list:
            agent_data = {
                'id': agent.agent_id,
                'is_alive': agent.is_alive,
                'health': agent.health_list[agent.agent_id] if agent.is_alive else 0,
                'alliance_with': agent.alliance_pair.agent_id if agent.alliance_pair else None
            }
            state['agents'].append(agent_data)
        
        return state

    def apply_state(self, state):
        """Apply a stored state to the visualization"""
        # Update step counter
        self.step = state['step']
        self.step_text.set_text(f'Step: {self.step}')
        
        # Update alive agents count
        self.alive_text.set_text(f'Alive: {state["alive_count"]}/{self.num_agents}')
        
        # Display game over message if it exists
        if 'game_over_message' in state:
            # Remove old game over text if exists
            if hasattr(self, 'game_over_text'):
                self.game_over_text.remove()
                
            # Split message into lines
            message_lines = state['game_over_message'].split('\n')
            
            # Create info box with more prominent styling
            info_box = dict(
                boxstyle="round,pad=0.6", 
                facecolor='#2D2D44', 
                alpha=0.95, 
                edgecolor='#666666',
                linewidth=2
            )
            
            # Add game over text at the center
            self.game_over_text = self.ax_main.text(
                0.5, 0.5, state['game_over_message'],
                ha='center', va='center',
                color='#FFFFFF', fontsize=14, fontweight='bold',
                transform=self.ax_main.transAxes,
                bbox=info_box,
                linespacing=1.5,  # Add more space between lines
                zorder=1000  # Ensure it appears on top
            )
            
            # Add a title above the message box
            self.ax_main.text(
                0.5, 0.65, 'SIMULATION COMPLETED',
                ha='center', va='center',
                color='#FFD700', fontsize=16, fontweight='bold',
                transform=self.ax_main.transAxes,
                zorder=1000
            )
            
            # Adjust layout to fit the text
            self.fig.tight_layout(rect=[0, 0, 1, 0.95])
        
        # Clear previous alliance lines
        for line in self.alliance_lines:
            line.remove()
        self.alliance_lines = []
        
        # First pass to update bars
        for i, agent_data in enumerate(state['agents']):
            if agent_data['is_alive']:
                health = agent_data['health']
                self.bars[i].set_height(health)
                self.bars[i].set_color(self.bar_colors[i])
                self.health_labels[i].set_text(f'{health:.1f}')
                self.health_labels[i].set_position((i, health + 0.1))
                self.health_labels[i].set_color(TEXT_COLOR)
            else:
                # Agent is dead
                self.bars[i].set_height(0.05)  # Small bar to indicate death
                self.bars[i].set_color(COLORS[0])  # Red for dead
                self.health_labels[i].set_text('DEAD')
                self.health_labels[i].set_position((i, 0.1))
                self.health_labels[i].set_color(COLORS[0])
        
        # Second pass to draw all alliances after bars are updated
        for i, agent_data in enumerate(state['agents']):
            if agent_data['is_alive'] and agent_data['alliance_with'] is not None:
                ally_id = agent_data['alliance_with']
                # Only draw once for each pair (from lower index to higher)
                if i < ally_id:
                    # Calculate bar positions - these are the centers of the bars
                    bar1_x = i
                    bar2_x = ally_id
                    bar_bottom = 0  # Bottom of the health bars
                    
                    # Create a modern curved connection between the bars
                    # Using ConnectionPatch for a sleek curved look
                    connection = patches.ConnectionPatch(
                        xyA=(bar1_x, bar_bottom),  # Start at bottom of first bar
                        xyB=(bar2_x, bar_bottom),  # End at bottom of second bar
                        coordsA='data',
                        coordsB='data',
                        axesA=self.ax_main,
                        axesB=self.ax_main,
                        arrowstyle='-',            # No arrow heads
                        connectionstyle='arc3,rad=0.3',  # Curved connection
                        color='#FF8800',           # Bright orange color
                        linewidth=3,               # Thick line for visibility
                        linestyle=(0, (5, 2)),     # Dotted line pattern
                        zorder=90,                 # High z-order
                        alpha=1.0                  # Full opacity
                    )
                    
                    # Add the connection to the plot
                    self.ax_main.add_artist(connection)
                    self.alliance_lines.append(connection)
                    
                    # Add small circular indicators at the connection points
                    circle1 = Circle((bar1_x, bar_bottom), radius=0.05, 
                                    facecolor='#FF8800', edgecolor='white', 
                                    linewidth=1, alpha=1.0, zorder=91)
                    circle2 = Circle((bar2_x, bar_bottom), radius=0.05,
                                    facecolor='#FF8800', edgecolor='white',
                                    linewidth=1, alpha=1.0, zorder=91)
                                        
                    self.ax_main.add_patch(circle1)
                    self.ax_main.add_patch(circle2)
                    self.alliance_lines.append(circle1)
                    self.alliance_lines.append(circle2)
        
        return self.bars + self.alliance_lines

def main():
    """Run a test simulation and visualization"""
    # Create settings with auto-config
    settings = Settings(auto_config=True)
    settings.number_of_agents = 6  # 6 agents for testing
    
    # Initialize simulation
    simulation = Simulation(settings)
    
    # Create and run visualizer
    visualizer = WebSimulationVisualizer(simulation)
    visualizer.run()

if __name__ == "__main__":
    main() 