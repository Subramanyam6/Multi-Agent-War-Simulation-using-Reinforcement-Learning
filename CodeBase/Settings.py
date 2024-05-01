

class Settings:

    def __init__(self):
        self.number_of_agents = \
            int(input('Please enter the number of agents for the battle (> 1): \n'))

        self.starting_health_config = \
            int(input(
                 '\nPlease select the beginning health profile for the agents, input a number from (1, 2, 3, 4): \
                  \n  1. Each agent starts with full health \
                  \n  2. Each agent starts with low health \
                  \n  3. Each agent starts with random health \
                  \n  4. Half the agents start with low health and half the agents start with full health\n'))

        self.max_iteration = \
            int(input('\nPlease input the number of iterations for the Q-learning algorithm:\n'))

        self.anim_profile = \
            int(input(
                 '\nPlease select the beginning animosities profile, input a number from (1,2,3): \
                  \n  1. High initial animosity between all the agents \
                  \n  2. Low initial animosity between all the agents \
                  \n  3. Random initial animosities between all the agents\n'))

        self.alpha = \
            float(input('\nPlease input the learning rate (decimal value between 0 and 1):\n'))

        self.beta = float(input('\nPlease input the discount factor (decimal value between 0 and 1):\n'))
        self.baseline_att_prob = 0.25
        self.baseline_def_prob = 0.66
        self.baseline_recover_prob = 0.90
        self.baseline_underattack_attack_multiplier = 1.20
        self.baseline_notunderattack_attack_prob = 0.20
        self.attack_dead_opponent_penalty = 0.2
        self.attack_alliance_member_penalty = 0.3
        self.propose_alliance_member_penalty = 0.2
        self.animosity_decrease_prob = 0.3
        self.animosity_decrease_prob_alliance_proposal = 0.6
        self.animosity_increase_prob = 0.5
        self.alliance_prob_with_some_animosity_baseline = 0.6 # divide with runtime animosity value for final prob
        self.alliance_prob_with_no_animosity = 0.9
        self.alliance_status_weight = 1.5 # this is used in transition prob to update health. No alliance val = 1