import random

class Agent:

    def __init__(self, agent_id, number_of_agents, health_list):
        self.number_of_agents = number_of_agents
        self.agent_id = agent_id

        self.health_list = list(health_list)
        self.stable_health_list = list(health_list)

        self.actions = self.create_actions(agent_id, number_of_agents)
        self.latest_action = None

        self.alliance_status = 1  # this is 1 by default, will change to 1.5 with alliance formations
        self.stable_alliance_status = 1

        self.proposal_request = None

        self.alliance_pair = None  # this agent object is updated as per alliance formation/breakups
        self.stable_alliance_pair = None

        self.current_reward = 0

        self.is_alive = True
        self.stable_is_alive = True

        self.Q_table = []
        self.s_index = None
        self.snext_index = None
        self.val_snext = 0

    def create_actions(self, agent_id, number_of_agents):
        acts = []
        # n_attacks + n_alliances + defend + recover + n_accept_alliances
        for act in range(0, number_of_agents + number_of_agents + 1 + 1 + number_of_agents):
            acts.append(act)
        acts.remove(agent_id)  # removing agent's self-attack
        acts.remove(agent_id + number_of_agents)  # removing agent's self-alliance
        acts.remove(2 * number_of_agents + 2 + agent_id)  # removing agent's self-acceptance
        return acts

    def choose_action(self, t):  # t is a time-step until which agents choose random actions
        chosen_action = self.agent_id
        if self.is_alive == True:
            if t < 1000:
                chosen_action = random.choice(self.actions)
            else:
                Q_max = self.Q_table[self.s_index][0]
                for eachaction in self.actions:
                    if self.Q_table[self.s_index][eachaction] > Q_max:
                        Q_max = self.Q_table[self.s_index][eachaction]
                        chosen_action = eachaction
        self.latest_action = chosen_action

    def compute_val_snext(self):
        max = self.Q_table[self.snext_index][0]
        for i in range(self.number_of_agents * 3 + 2):
            if self.Q_table[self.snext_index][i] > max:
                max = self.Q_table[self.snext_index][i]
        self.val_snext = max