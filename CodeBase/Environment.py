import random
from CodeBase.Agent import Agent
import time

class Environment:

    def __init__(self, number_of_agents, health_list, settings):
        self.number_of_agents = number_of_agents
        self.health_list = list(health_list)
        self.stable_health_list = list(health_list)
        self.settings = settings
        self.agents_list = self.create_agents(number_of_agents, health_list, settings)
        self.animosity_table = self.initialize_animosities(self.agents_list, settings)
        self.stable_animosity_table = list(self.animosity_table)
        self.alpha = settings.alpha
        self.beta = settings.beta
        self.health_granularity = settings.health_granularity
        self.max_health = settings.max_health
        # print('order of actions = n_attacks + n_alliances + defend + recover + n_accept_alliances')

        print('\nInitializing the environment', end="")
        time.sleep(1)
        for i in range(4):
            print('.', end="")
            time.sleep(1)
        print('\n')

    def create_agents(self, number_of_agents, health_list, settings):
        ags = []
        for agent_i in range(0, number_of_agents):
            # Create agent with the specified type from settings
            agent_type = settings.agent_types[agent_i] if agent_i < len(settings.agent_types) else "Random"
            ags.append(Agent(agent_i, number_of_agents, health_list, settings, agent_type))
        return ags

    def initialize_animosities(self, agents_list, settings):
        anim_profile = settings.anim_profile
        anim_table = []
        for eachagent in agents_list:
            animositylistofeachagent = []
            for eachopponent in agents_list:
                if eachagent == eachopponent:
                    animositylistofeachagent.append('N/A')
                elif anim_profile == 1:
                    animositylistofeachagent.append(2)
                elif anim_profile == 2:
                    animositylistofeachagent.append(0)
                elif anim_profile == 3:
                    animositylistofeachagent.append(random.randrange(0, 3, 1))
            anim_table.append(animositylistofeachagent)
        return anim_table
        
    def adjust_health(self, health_value, increase=True):
        """Adjust health according to granularity settings"""
        if increase:
            # Increase health
            new_health = health_value + self.health_granularity
            # Cap at max health
            return min(new_health, self.max_health)
        else:
            # Decrease health
            new_health = health_value - self.health_granularity
            # Floor at 0
            return max(new_health, 0)