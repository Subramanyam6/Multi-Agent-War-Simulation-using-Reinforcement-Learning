import random
import itertools
import time
from CodeBase.Environment import Environment
from CodeBase.GameStatusUpdate import GameStatusUpdate

class Simulation:
    def __init__(self, settings):
        self.game_status_update = GameStatusUpdate(settings)
        self.settings = settings
        number_of_agents = self.settings.number_of_agents # number of agents

        # initializing each agent's health based on the input setting
        starting_health_config = self.settings.starting_health_config
        start_health_list = []
        if starting_health_config == 1:
            for eachagent in range(number_of_agents):
                start_health_list.append(2)
        elif starting_health_config == 2:
            for eachagent in range(number_of_agents):
                start_health_list.append(1)
        elif starting_health_config == 3:
            for eachagent in range(number_of_agents):
                start_health_list.append(random.randrange(0, 2, 1))
        elif starting_health_config == 4:
            counter = 0
            for eachagent in range(number_of_agents):
                if counter < number_of_agents / 2 - 1:
                    start_health_list.append(1)
                else:
                    start_health_list.append(2)
                counter += 1

        self.env = Environment(number_of_agents, start_health_list, self.settings) # initializing the environment
        self.max_iteration = self.settings.max_iteration
        self.game_is_on = True

        # creating the states:
        self.states_list = []
        iterables = []
        # appending all possible healths to the state:
        for eachagent in self.env.agents_list:
            iterables.append([0, 1, 2])

        # appending alliance status to the state:
        iterables.append([1, 1.5])

        # creating the list of states:
        for t in itertools.product(*iterables):
            self.states_list.append(t)

        # creating the keys(of indices) dictionary of each state:
        self.states_dict = {}
        i = 0
        for eachstate in self.states_list:
            # print('printing each state: ', eachstate)
            self.states_dict[eachstate] = i
            i += 1

        # creating a Q-table for each agent:
        for everyagent in self.env.agents_list:
            for eachstate in self.states_list:
                temp = []
                # using the generic total number of actions
                for i in range(self.env.number_of_agents * 3 + 2):
                    temp.append(0)
                everyagent.Q_table.append(temp)

        # print('printing sample Q table: ', self.env.agents_list[0].Q_table)
        # print('Simulation running successfully')

    # starting the run
    def run(self):
        print('\nAgents are now fighting', end="")
        time.sleep(1)

        for i in range(4):
            print('.', end="")
            time.sleep(1)
        print('\n')

        while self.game_is_on:
            t = 0
            reset = False
            while t < self.max_iteration:

                alive_list = []

                # computing state index for the Q-table:
                for eachagent in self.env.agents_list:
                    temp_state = list(eachagent.health_list)
                    temp_state.append(eachagent.alliance_status)
                    s_key = tuple(temp_state)
                    eachagent.s_index = self.states_dict[tuple(s_key)]

                # choosing an action for each agent
                for eachagent in self.env.agents_list:
                    eachagent.choose_action(t)

                # updating the dummy game's state
                self.game_status_update.update(self.env)

                # computing s_next index for the Q-table:
                for eachagent in self.env.agents_list:
                    temp_next_state = list(eachagent.health_list)
                    temp_next_state.append(eachagent.alliance_status)
                    snext_key = tuple(temp_next_state)
                    eachagent.snext_index = self.states_dict[tuple(snext_key)]
                    # updating the value of snext:
                    eachagent.compute_val_snext() #checking for state transition to compute the rewards:

                # updating the Q-table:
                for eachagent in self.env.agents_list:
                    eachagent.Q_table[eachagent.s_index][eachagent.latest_action] = \
                        (1 - self.env.alpha) * eachagent.Q_table[eachagent.s_index][eachagent.latest_action] \
                        + self.env.alpha * (eachagent.current_reward + self.env.beta * eachagent.val_snext)

                # checking how many agents are alive:
                for eachagent in self.env.agents_list:
                    if eachagent.is_alive == True:
                        alive_list.append(eachagent)

                # checking if members from only one alliance are left:
                if len(alive_list) == 2:
                    if alive_list[0].alliance_pair == alive_list[1]:
                        reset = True

                # checking if only one agent is left:
                elif len(alive_list) == 1:
                    reset = True

                # resetting to the original state if the dummy game is over:
                if reset == True:

                    # refreshing environment health_list with the original values:
                    self.env.health_list = list(self.env.stable_health_list)
                    self.animosity_table = list(self.env.stable_animosity_table)

                    # refreshing the attributes of the agent with original values:
                    for eachagent in self.env.agents_list:
                        eachagent.health_list = list(eachagent.stable_health_list)
                        eachagent.alliance_status = eachagent.stable_alliance_status
                        eachagent.alliance_pair = eachagent.stable_alliance_pair
                        eachagent.is_alive = eachagent.stable_is_alive

                t += 1

            # print('subgame timestep = {}'.format(t))
            self.update_time_step()

    # executing the actions of each agent and taking the game to the next time step:
    def update_time_step(self):

        alive_list_final = []

        # refreshing environment health_list and animosity table with the original values:
        self.env.health_list = list(self.env.stable_health_list)
        self.animosity_table = list(self.env.stable_animosity_table)

        # refreshing the attributes of the agent with original values:
        for eachagent in self.env.agents_list:
            eachagent.health_list = list(eachagent.stable_health_list)
            eachagent.alliance_status = eachagent.stable_alliance_status
            eachagent.alliance_pair = eachagent.stable_alliance_pair
            eachagent.is_alive = eachagent.stable_is_alive

        # choosing action for each agent:
        for eachagent in self.env.agents_list:
            eachagent.choose_action(999999999) # agents don't choose random actions anymore since learning is complete

        # updating the game:
        self.game_status_update.update(self.env)

        # updating the environment health_list and animosity table:
        self.env.stable_health_list = list(self.env.health_list)
        self.env.stable_animosity_table = list(self.env.animosity_table)

        # updating the state indirectly by updating the health list and alliance status:
        for eachagent in self.env.agents_list:
            eachagent.stable_health_list = list(eachagent.health_list)
            eachagent.stable_alliance_status = eachagent.alliance_status
            eachagent.stable_alliance_pair = eachagent.alliance_pair
            eachagent.stable_is_alive = eachagent.is_alive

        # checking how many agents are alive:
        for eachagent in self.env.agents_list:
            if eachagent.is_alive == True:
                alive_list_final.append(eachagent)

        # checking if only members from one alliance are left:
        if len(alive_list_final) == 2:
            if alive_list_final[0].alliance_pair == alive_list_final[1]:
                self.game_is_on = False
                print('\nThe winner is the team of Agents - {} and {}'.format(alive_list_final[0].agent_id,
                                                                              alive_list_final[1].agent_id))

        # checking only if one agent is left:
        elif len(alive_list_final) == 1:
            self.game_is_on = False
            print('\nThe winner is Agent - {}'.format(alive_list_final[0].agent_id))
            # print(alive_list_final[0].Q_table)