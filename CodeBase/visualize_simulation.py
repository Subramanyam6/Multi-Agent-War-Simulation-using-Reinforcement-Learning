#!/usr/bin/env python3
"""
Visualization for Multi-Agent War Simulation using PyGame
Shows the health of each agent as animated bars
"""

import pygame
import time
import random
import numpy as np
from pygame import gfxdraw

# Import necessary components
from Environment import Environment
from GameStatusUpdate import GameStatusUpdate
from Settings import Settings
from Agent import Agent
from Simulation import Simulation

# Initialize pygame
pygame.init()

# Colors
BACKGROUND = (20, 20, 30)
PANEL_BG = (30, 30, 40)
COLORS = [
    (255, 100, 100),    # Red
    (100, 255, 100),    # Green
    (100, 100, 255),    # Blue
    (255, 255, 100),    # Yellow
    (255, 100, 255),    # Magenta
]
TEXT_COLOR = (220, 220, 220)
TEXT_SECONDARY = (180, 180, 180)
RL_COLOR = (255, 215, 0)       # Gold for RL
HEURISTIC_COLOR = (0, 191, 255) # Deep Sky Blue for Heuristic
RANDOM_COLOR = (200, 200, 200)  # Light gray for Random
ALLIANCE_COLOR = (255, 165, 0)  # Orange for alliance indicator

class SimulationVisualizer:
    def __init__(self, simulation):
        self.simulation = simulation
        self.env = simulation.env
        self.num_agents = self.env.number_of_agents
        
        # Screen setup
        self.width = 1000
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Multi-Agent War Simulation")
        
        # Font setup
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Layout settings
        self.margin = 20
        self.sidebar_width = 250
        self.main_area_width = self.width - self.sidebar_width - self.margin * 3
        
        # Bar chart settings
        self.bar_width = min(80, (self.main_area_width - (self.num_agents + 1) * 10) // self.num_agents)
        self.max_bar_height = 300
        self.bar_spacing = (self.main_area_width - (self.num_agents * self.bar_width)) // (self.num_agents + 1)
        self.bar_y_base = self.height - 100
        
        # Animation settings
        self.clock = pygame.time.Clock()
        self.fps = 1  # Frames per second (simulation speed)
        
        # Game state
        self.running = True
        self.paused = False
        self.step = 0
        
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
    
    def draw_sidebar(self):
        """Draw the sidebar with simulation information"""
        # Draw sidebar background
        sidebar_rect = pygame.Rect(self.width - self.sidebar_width - self.margin, self.margin, 
                                  self.sidebar_width, self.height - self.margin * 2)
        pygame.draw.rect(self.screen, PANEL_BG, sidebar_rect)
        pygame.draw.rect(self.screen, TEXT_SECONDARY, sidebar_rect, 1)  # Border
        
        # Draw simulation info
        title = self.title_font.render("Simulation Info", True, TEXT_COLOR)
        self.screen.blit(title, (self.width - self.sidebar_width - self.margin + 15, self.margin + 15))
        
        # Draw step counter
        step_text = f"Step: {self.step}"
        text_surface = self.font.render(step_text, True, TEXT_COLOR)
        self.screen.blit(text_surface, (self.width - self.sidebar_width - self.margin + 15, self.margin + 50))
        
        # Draw alive agents count
        alive_count = sum(1 for agent in self.env.agents_list if agent.is_alive)
        alive_text = f"Agents Alive: {alive_count}/{self.num_agents}"
        alive_surface = self.font.render(alive_text, True, TEXT_COLOR)
        self.screen.blit(alive_surface, (self.width - self.sidebar_width - self.margin + 15, self.margin + 80))
        
        # Draw agent type legend
        legend_y = self.margin + 120
        legend_title = self.font.render("Agent Types:", True, TEXT_COLOR)
        self.screen.blit(legend_title, (self.width - self.sidebar_width - self.margin + 15, legend_y))
        
        # RL agent legend
        legend_y += 30
        pygame.draw.circle(self.screen, RL_COLOR, 
                          (self.width - self.sidebar_width - self.margin + 25, legend_y + 8), 8)
        rl_text = self.font.render("RL Agent", True, TEXT_COLOR)
        self.screen.blit(rl_text, (self.width - self.sidebar_width - self.margin + 40, legend_y))
        
        # Heuristic agent legend
        legend_y += 30
        pygame.draw.circle(self.screen, HEURISTIC_COLOR, 
                          (self.width - self.sidebar_width - self.margin + 25, legend_y + 8), 8)
        heuristic_text = self.font.render("Heuristic Agent", True, TEXT_COLOR)
        self.screen.blit(heuristic_text, (self.width - self.sidebar_width - self.margin + 40, legend_y))
        
        # Random agent legend
        legend_y += 30
        pygame.draw.circle(self.screen, RANDOM_COLOR, 
                          (self.width - self.sidebar_width - self.margin + 25, legend_y + 8), 8)
        random_text = self.font.render("Random Agent", True, TEXT_COLOR)
        self.screen.blit(random_text, (self.width - self.sidebar_width - self.margin + 40, legend_y))
        
        # Draw controls info
        controls_y = self.height - self.margin - 120
        controls_title = self.font.render("Controls:", True, TEXT_COLOR)
        self.screen.blit(controls_title, (self.width - self.sidebar_width - self.margin + 15, controls_y))
        
        controls_y += 30
        space_text = self.small_font.render("SPACE - Pause/Resume", True, TEXT_SECONDARY)
        self.screen.blit(space_text, (self.width - self.sidebar_width - self.margin + 25, controls_y))
        
        controls_y += 25
        esc_text = self.small_font.render("ESC - Exit", True, TEXT_SECONDARY)
        self.screen.blit(esc_text, (self.width - self.sidebar_width - self.margin + 25, controls_y))
    
    def draw_agent_status(self, agent, x, y, width, height):
        """Draw an agent's status box"""
        # Draw background
        agent_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, PANEL_BG, agent_rect)
        pygame.draw.rect(self.screen, self.agent_type_colors[agent.agent_type], agent_rect, 2)  # Colored border
        
        # Draw agent ID with colored circle
        circle_x = x + 15
        circle_y = y + 15
        pygame.draw.circle(self.screen, self.agent_type_colors[agent.agent_type], (circle_x, circle_y), 8)
        
        agent_text = f"Agent {agent.agent_id}"
        text_surface = self.font.render(agent_text, True, TEXT_COLOR)
        self.screen.blit(text_surface, (x + 30, y + 5))
        
        # Draw health value
        if agent.is_alive:
            health = agent.health_list[agent.agent_id]
            health_text = f"Health: {health:.1f}"
            health_color = TEXT_COLOR
        else:
            health_text = "DEAD"
            health_color = COLORS[0]  # Red for dead
            
        health_surface = self.small_font.render(health_text, True, health_color)
        self.screen.blit(health_surface, (x + 10, y + 30))
        
        # Draw alliance status
        if agent.alliance_pair is not None:
            alliance_text = f"Allied with: {agent.alliance_pair.agent_id}"
            alliance_surface = self.small_font.render(alliance_text, True, ALLIANCE_COLOR)
            self.screen.blit(alliance_surface, (x + 10, y + 50))
    
    def draw_health_bars(self):
        """Draw health bars for each agent"""
        # Draw title
        title = self.title_font.render("Agent Health", True, TEXT_COLOR)
        self.screen.blit(title, (self.margin + 10, self.margin + 10))
        
        # Calculate layout
        bar_area_width = self.width - self.sidebar_width - self.margin * 3
        bar_width = min(60, (bar_area_width - (self.num_agents + 1) * 10) // self.num_agents)
        bar_spacing = (bar_area_width - (self.num_agents * bar_width)) // (self.num_agents + 1)
        bar_y_base = self.margin + 50 + self.max_bar_height
        
        for i, agent in enumerate(self.env.agents_list):
            # Calculate bar position
            x = self.margin + bar_spacing + i * (bar_width + bar_spacing)
            
            # Draw agent ID below bar
            agent_text = f"Agent {agent.agent_id}"
            text_surface = self.small_font.render(agent_text, True, TEXT_COLOR)
            text_width = text_surface.get_width()
            self.screen.blit(text_surface, (x + (bar_width - text_width) // 2, bar_y_base + 10))
            
            # Draw agent type indicator (colored circle)
            pygame.draw.circle(self.screen, self.agent_type_colors[agent.agent_type], 
                              (x + bar_width // 2, bar_y_base + 30), 5)
            
            # Draw health bar only if agent is alive
            if agent.is_alive:
                health = agent.health_list[agent.agent_id]
                max_health = self.env.max_health
                
                # Calculate bar height based on health
                bar_height = (health / max_health) * self.max_bar_height
                
                # Draw bar
                bar_rect = pygame.Rect(x, bar_y_base - bar_height, bar_width, bar_height)
                
                # Use color based on agent type with transparency
                color = self.agent_type_colors[agent.agent_type]
                
                # Draw bar with rounded corners
                self.draw_rounded_rect(bar_rect, color, 5)
                
                # Draw health value on top of bar
                health_text = f"{health:.1f}"
                health_surface = self.small_font.render(health_text, True, TEXT_COLOR)
                text_width = health_surface.get_width()
                self.screen.blit(health_surface, (x + (bar_width - text_width) // 2, bar_y_base - bar_height - 20))
                
                # Draw alliance indicator if exists
                if agent.alliance_pair is not None:
                    ally_id = agent.alliance_pair.agent_id
                    # Calculate position of the allied agent's bar
                    ally_x = self.margin + bar_spacing + ally_id * (bar_width + bar_spacing) + bar_width // 2
                    # Draw curved alliance line with arrows
                    self.draw_curved_alliance_line(
                        x + bar_width // 2, bar_y_base + 40,
                        ally_x, bar_y_base + 40,
                        ALLIANCE_COLOR
                    )
            else:
                # Draw a small "dead" indicator
                bar_rect = pygame.Rect(x, bar_y_base - 10, bar_width, 10)
                pygame.draw.rect(self.screen, COLORS[0], bar_rect)  # Red for dead
                pygame.draw.rect(self.screen, TEXT_COLOR, bar_rect, 1)  # Border
                
                # Draw "DEAD" text
                dead_text = "DEAD"
                dead_surface = self.small_font.render(dead_text, True, COLORS[0])
                text_width = dead_surface.get_width()
                self.screen.blit(dead_surface, (x + (bar_width - text_width) // 2, bar_y_base - 30))
    
    def draw_agent_details(self):
        """Draw detailed information about each agent"""
        # Draw title
        title = self.title_font.render("Agent Details", True, TEXT_COLOR)
        self.screen.blit(title, (self.margin + 10, self.bar_y_base + 70))
        
        # Calculate layout for agent status boxes
        box_width = (self.width - self.sidebar_width - self.margin * (self.num_agents + 3)) // min(3, self.num_agents)
        box_height = 80
        boxes_per_row = min(3, self.num_agents)
        
        for i, agent in enumerate(self.env.agents_list):
            row = i // boxes_per_row
            col = i % boxes_per_row
            
            x = self.margin + col * (box_width + self.margin)
            y = self.bar_y_base + 110 + row * (box_height + self.margin)
            
            self.draw_agent_status(agent, x, y, box_width, box_height)
    
    def draw_rounded_rect(self, rect, color, radius=10):
        """Draw a rounded rectangle"""
        rect_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, color, (0, 0, rect.width, rect.height), border_radius=radius)
        self.screen.blit(rect_surface, rect.topleft)
    
    def draw_curved_alliance_line(self, x1, y1, x2, y2, color, arrow_size=8):
        """Draw a curved alliance line with double-headed arrows"""
        # Calculate control point for the curve (below the line)
        mid_x = (x1 + x2) / 2
        mid_y = y1 + 20  # Curve downward
        
        # Draw the curved line using multiple small line segments
        points = []
        steps = 20  # Number of segments for the curve
        for i in range(steps + 1):
            t = i / steps
            # Quadratic Bezier curve
            bx = (1-t)**2 * x1 + 2*(1-t)*t * mid_x + t**2 * x2
            by = (1-t)**2 * y1 + 2*(1-t)*t * mid_y + t**2 * y2
            points.append((bx, by))
        
        # Draw the curve
        if len(points) > 1:
            pygame.draw.lines(self.screen, color, False, points, 2)
        
        # Draw arrowheads on both ends
        # Left arrowhead
        if len(points) > 1:
            angle1 = np.arctan2(points[1][1] - points[0][1], points[1][0] - points[0][0])
            x1_arrow = x1 + arrow_size * np.cos(angle1 + np.pi/6)
            y1_arrow = y1 + arrow_size * np.sin(angle1 + np.pi/6)
            x2_arrow = x1 + arrow_size * np.cos(angle1 - np.pi/6)
            y2_arrow = y1 + arrow_size * np.sin(angle1 - np.pi/6)
            pygame.draw.polygon(self.screen, color, [(x1, y1), (x1_arrow, y1_arrow), (x2_arrow, y2_arrow)])
        
        # Right arrowhead
        if len(points) > 1:
            angle2 = np.arctan2(points[-2][1] - points[-1][1], points[-2][0] - points[-1][0])
            x1_arrow = x2 + arrow_size * np.cos(angle2 + np.pi/6)
            y1_arrow = y2 + arrow_size * np.sin(angle2 + np.pi/6)
            x2_arrow = x2 + arrow_size * np.cos(angle2 - np.pi/6)
            y2_arrow = y2 + arrow_size * np.sin(angle2 - np.pi/6)
            pygame.draw.polygon(self.screen, color, [(x2, y2), (x1_arrow, y1_arrow), (x2_arrow, y2_arrow)])
    
    def handle_events(self):
        """Handle PyGame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
    
    def update_simulation(self):
        """Update the simulation state"""
        if not self.paused and self.simulation.game_is_on:
            self.simulation.update_time_step()
            self.step += 1
    
    def run(self):
        """Main visualization loop"""
        while self.running and self.simulation.game_is_on:
            # Handle events
            self.handle_events()
            
            # Update simulation
            if not self.paused:
                self.update_simulation()
            
            # Draw everything
            self.screen.fill(BACKGROUND)
            self.draw_sidebar()
            self.draw_health_bars()
            self.draw_agent_details()
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(self.fps)
        
        # Show final state for a few seconds before closing
        if not self.running:
            return
            
        # Display winner information
        self.screen.fill(BACKGROUND)
        self.draw_sidebar()
        self.draw_health_bars()
        self.draw_agent_details()
        
        # Create a semi-transparent overlay for the winner message
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Check for winners
        alive_agents = [agent for agent in self.env.agents_list if agent.is_alive]
        
        if len(alive_agents) == 1:
            winner_text = f"Winner: Agent {alive_agents[0].agent_id}"
            winner_color = self.agent_type_colors[alive_agents[0].agent_type]
            winner_surface = self.title_font.render(winner_text, True, winner_color)
            self.screen.blit(winner_surface, (self.width // 2 - winner_surface.get_width() // 2, self.height // 2 - 15))
            
            agent_type = alive_agents[0].agent_type
            type_text = f"Agent Type: {agent_type}"
            type_surface = self.font.render(type_text, True, TEXT_COLOR)
            self.screen.blit(type_surface, (self.width // 2 - type_surface.get_width() // 2, self.height // 2 + 20))
            
        elif len(alive_agents) == 2 and alive_agents[0].alliance_pair == alive_agents[1]:
            winner_text = f"Winners: Alliance between Agent {alive_agents[0].agent_id} and Agent {alive_agents[1].agent_id}"
            winner_surface = self.title_font.render(winner_text, True, ALLIANCE_COLOR)
            self.screen.blit(winner_surface, (self.width // 2 - winner_surface.get_width() // 2, self.height // 2 - 15))
            
            types_text = f"Types: {alive_agents[0].agent_type} and {alive_agents[1].agent_type}"
            types_surface = self.font.render(types_text, True, TEXT_COLOR)
            self.screen.blit(types_surface, (self.width // 2 - types_surface.get_width() // 2, self.height // 2 + 20))
            
        else:
            stalemate_text = "Stalemate - No clear winner"
            stalemate_surface = self.title_font.render(stalemate_text, True, TEXT_COLOR)
            self.screen.blit(stalemate_surface, (self.width // 2 - stalemate_surface.get_width() // 2, self.height // 2))
        
        pygame.display.flip()
        time.sleep(5)  # Show final state for 5 seconds
        
        pygame.quit()

def main():
    print('Initializing Multi-Agent War Simulation with PyGame Visualization')
    print('\n=== PROJECT PURPOSE ===')
    print('This simulation demonstrates a multi-agent war environment with different agent types:')
    print('1. RL Agents: Use reinforcement learning to make decisions')
    print('2. Heuristic Agents: Use rule-based strategies')
    print('3. Random Agents: Make random decisions')
    print('\nThe goal is to observe how different agent types perform against each other,')
    print('and whether RL agents can learn effective strategies in this competitive environment.')
    
    # Create settings (simplified to avoid user input)
    settings = Settings(auto_config=True)
    
    # Display agent configuration
    print(f"\n=== AGENT CONFIGURATION ({settings.number_of_agents} agents) ===")
    agent_counts = {"RL": 0, "Heuristic": 0, "Random": 0}
    for agent_type in settings.agent_types:
        agent_counts[agent_type] += 1
    print(f"RL Agents: {agent_counts['RL']}")
    print(f"Heuristic Agents: {agent_counts['Heuristic']}")
    print(f"Random Agents: {agent_counts['Random']}")
    
    # Display health configuration
    print(f"\n=== HEALTH CONFIGURATION ===")
    print(f"Max Health: {settings.max_health}")
    print(f"Health Granularity: {settings.health_granularity}")
    if settings.health_granularity < 1.0:
        print(f"Using fine-grained health with {int(settings.max_health/settings.health_granularity) + 1} possible health levels")
    else:
        print(f"Using standard health with {int(settings.max_health/settings.health_granularity) + 1} possible health levels")
    
    # Create and run simulation
    simulation = Simulation(settings)
    
    # Train the agents first (without visualization)
    print("\n=== TRAINING PHASE ===")
    print("Training RL agents while others act according to their strategies...")
    simulation.train()
    
    # Create visualizer for the final game
    print("\n=== VISUALIZATION PHASE ===")
    print("Starting visualization of the final game...")
    visualizer = SimulationVisualizer(simulation)
    visualizer.run()

if __name__ == '__main__':
    main() 