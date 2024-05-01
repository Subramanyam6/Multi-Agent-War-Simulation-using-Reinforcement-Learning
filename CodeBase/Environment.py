import random
from CodeBase.Agent import Agent
import time

class Environment:

    def __init__(self, number_of_agents, health_list, settings):

        self.number_of_agents = number_of_agents
        # print('number of agents = ', self.number_of_agents)

        self.health_list = list(health_list)
        # print('environment health_list = ', self.health_list)

        self.stable_health_list = list(health_list)
        # print('environment stable_health_list = ', self.stable_health_list)

        self.agents_list = self.create_agents(number_of_agents, health_list)
        # print('agents created')

        self.animosity_table = self.initialize_animosities(self.agents_list, settings)
        # print('initialized animosity_table = ', self.animosity_table)

        self.stable_animosity_table = list(self.animosity_table)

        # print('\nPlease input the learning rate (decimal value between 0 and 1):')
        # self.alpha = float(input())
        self.alpha = settings.alpha
        # print('learning rate, alpha = ', self.alpha)

        # print('\nPlease input the discount factor (decimal value between 0 and 1):')
        # self.beta = float(input())
        self.beta = settings.beta
        # print('discount factor, beta = ', self.beta)

        # print('order of actions = n_attacks + n_alliances + defend + recover + n_accept_alliances')

        print('\nInitializing the environment', end="")
        time.sleep(1)
        for i in range(4):
            print('.', end="")
            time.sleep(1)
        print('\n')

    def create_agents(self, number_of_agents, health_list):
        ags = []
        for agent_i in range(0, number_of_agents):
            ags.append(Agent(agent_i, number_of_agents, health_list))
        return ags

    def initialize_animosities(self, agents_list, settings):

        anim_profile = settings.anim_profile

        if anim_profile == 1:
            anim_table = []
            for eachagent in agents_list:
                animositylistofeachagent = []
                for eachopponent in agents_list:
                    if eachagent == eachopponent:
                        animositylistofeachagent.append('N/A')
                    else:
                        animositylistofeachagent.append(2)
                anim_table.append(animositylistofeachagent)
        elif anim_profile == 2:
            anim_table = []
            for eachagent in agents_list:
                animositylistofeachagent = []
                for eachopponent in agents_list:
                    if eachagent == eachopponent:
                        animositylistofeachagent.append('N/A')
                    else:
                        animositylistofeachagent.append(0)
                anim_table.append(animositylistofeachagent)
        elif anim_profile == 3:
            anim_table = []
            for eachagent in agents_list:
                animositylistofeachagent = []
                for eachopponent in agents_list:
                    if eachagent == eachopponent:
                        animositylistofeachagent.append('N/A')
                    else:
                        animositylistofeachagent.append(random.randrange(0, 3, 1))
                anim_table.append(animositylistofeachagent)

        return anim_table