import random

class GameStatusUpdate:
    def __init__(self, settings):
        self.baseline_att_prob = settings.baseline_att_prob
        self.baseline_def_prob = settings.baseline_def_prob
        self.baseline_recover_prob = settings.baseline_recover_prob
        self.baseline_underattack_attack_multiplier = settings.baseline_underattack_attack_multiplier
        self.baseline_notunderattack_attack_prob = settings.baseline_notunderattack_attack_prob

    def update(self, dynamic_env):
        # refreshing and documenting proposals for each agent:
        for eachagent in dynamic_env.agents_list:
            eachagent.proposal_request = None
            if eachagent.latest_action > dynamic_env.number_of_agents - 1 \
                    and eachagent.latest_action < 2 * dynamic_env.number_of_agents:
                eachagent.proposal_request \
                    = eachagent.latest_action - dynamic_env.number_of_agents
                # gives the agent_id of the agent that was proposed to

        # iterating over each opponent:
        for eachagent in dynamic_env.agents_list:

            # Refreshing the current reward:
            eachagent.current_reward = 0
            E = 0

            # checking if the agent is alive:
            if eachagent.is_alive == False:
                continue

            for eachopponent in dynamic_env.agents_list:

                # checking is agent and opponent are not the same agent:
                if eachagent.agent_id != eachopponent.agent_id:

                    # checking if the agent is still alive:
                    if eachagent.is_alive == False:
                        continue

                    # checking if the opponent is alive:
                    if eachopponent.is_alive == False:
                        # penalizing the agent for attacking a dead opponent:
                        if eachagent.latest_action == eachopponent.agent_id:
                            E -= 0.2
                        continue

                # checking if agent and opponent are the same agent:
                if eachagent.agent_id != eachopponent.agent_id:

                    # case where the agent chooses the defend action:
                    if eachagent.latest_action == (2 * dynamic_env.number_of_agents):  # returns the defend action

                        # handling health_transition:
                        rand_health_prob = random.uniform(0, 1)
                        health_prob = 0

                        # agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id:  # attack of agent by the opponent

                            # updating agent's knowledge of opponent's actual health:
                            eachagent.health_list[eachopponent.agent_id] \
                                = dynamic_env.health_list[eachopponent.agent_id]

                            # checking for dead opponent after the above update:
                            if eachopponent.is_alive == False:
                                continue

                            health_prob = \
                                self.baseline_att_prob * \
                                dynamic_env.health_list[eachopponent.agent_id] * \
                                dynamic_env.agents_list[eachopponent.agent_id].alliance_status * \
                                self.baseline_def_prob * \
                                1 / dynamic_env.health_list[eachagent.agent_id] * \
                                1 / dynamic_env.agents_list[eachagent.agent_id].alliance_status

                        # agent is not being attacked by this opponent:
                        else:
                            health_prob = 0

                        # updating the agent's health:
                        if rand_health_prob < health_prob:
                            # updating environmental agent health:
                            if dynamic_env.health_list[eachagent.agent_id] > 0:
                                dynamic_env.health_list[eachagent.agent_id] -= 1
                                # updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = dynamic_env.health_list[eachagent.agent_id]

                            # checking if the agent is dead
                            if dynamic_env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False

                        # handling animosity:
                        # no change in animosity when the agent is defending against opponent

                    # case where the agent chooses recover action:
                    elif eachagent.latest_action == (2 * dynamic_env.number_of_agents + 1):  # returns recover action
                        # handling health_transition:
                        rand_health_prob = random.uniform(0, 1)
                        health_prob = 0

                        # agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id:  # attack of agent by the opponent

                            # updating agent's knowledge of opponent's actual health:
                            eachagent.health_list[eachopponent.agent_id] \
                                = dynamic_env.health_list[eachopponent.agent_id]

                            # checking for dead opponent after the above update:
                            if eachopponent.is_alive == False:
                                continue

                            health_prob = \
                                self.baseline_att_prob * \
                                1 / dynamic_env.health_list[eachopponent.agent_id] * \
                                1 / dynamic_env.agents_list[eachopponent.agent_id].alliance_status * \
                                self.baseline_recover_prob

                        # agent is not being attacked by this opponent:
                        else:
                            health_prob = self.baseline_recover_prob

                        # updating the agent's health:
                        if rand_health_prob < health_prob:
                            # updating environmental agent health:
                            if dynamic_env.health_list[eachagent.agent_id] < 2 and eachagent.is_alive == True:
                                dynamic_env.health_list[eachagent.agent_id] += 1
                                # updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = dynamic_env.health_list[eachagent.agent_id]

                        # handling animosity:
                        rand_prob_recover = random.uniform(0, 1)
                        anim_level = dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        if rand_prob_recover < 0.3:
                            if anim_level > 0:
                                # decreasing the animosity level
                                dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id] -= 1

                    # case where the agent chooses attack action:
                    elif eachagent.latest_action < dynamic_env.number_of_agents:  # returns one of the attack actions

                        # penalizing the agent for attacking its alliance member:
                        if eachagent.alliance_pair != None:
                            if eachagent.latest_action == eachagent.alliance_pair.agent_id:
                                E -= 0.3

                        # checking if the agent is attacking this particular opponent:
                        if eachagent.latest_action == eachopponent.agent_id:
                            # updating agent's knowledge of opponent's actual health:
                            eachagent.health_list[eachopponent.agent_id] \
                                = dynamic_env.health_list[eachopponent.agent_id]

                            # checking for dead opponent after the above update:
                            if eachopponent.is_alive == False:
                                continue

                        # handling health_transition:
                        rand_health_prob = random.uniform(0, 1)
                        health_prob = 0

                        # agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id:  # attack of agent by the opponent
                            health_prob = \
                                self.baseline_att_prob * \
                                dynamic_env.health_list[eachopponent.agent_id] * \
                                dynamic_env.agents_list[eachopponent.agent_id].alliance_status * \
                                self.baseline_underattack_attack_multiplier
                        # agent is not being attacked by this opponent:
                        else:
                            health_prob = self.baseline_notunderattack_attack_prob

                        # updating the agent's health:
                        if rand_health_prob < health_prob:
                            # updating environmental agent health:
                            if dynamic_env.health_list[eachagent.agent_id] > 0:
                                dynamic_env.health_list[eachagent.agent_id] -= 1
                                # updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = dynamic_env.health_list[eachagent.agent_id]

                            # checking if the agent is dead
                            if dynamic_env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False

                        # handling animosity:
                        rand_prob_attack = random.uniform(0, 1)
                        anim_level = dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        if rand_prob_attack < 0.5:
                            if anim_level < 2:
                                # increasing the animosity level
                                dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id] += 1

                    # case where the agent proposed an alliance:
                    elif eachagent.latest_action > dynamic_env.number_of_agents - 1 \
                            and eachagent.latest_action < 2 * dynamic_env.number_of_agents:
                        # returns one of the alliance actions

                        # penalizing the agent for proposing to an alliance member:
                        if eachagent.latest_action == eachagent.proposal_request + dynamic_env.number_of_agents:
                            E -= 0.2

                        # handling health_transition:
                        rand_health_prob = random.uniform(0, 1)
                        health_prob = 0

                        # agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id:  # attack of agent by the opponent
                            health_prob = \
                                self.baseline_att_prob * \
                                dynamic_env.health_list[eachopponent.agent_id] * \
                                dynamic_env.agents_list[eachopponent.agent_id].alliance_status
                        # agent is not being attacked by this opponent:
                        else:
                            health_prob = 0

                        # updating the agent's health:
                        if rand_health_prob < health_prob:
                            # updating environmental agent health:
                            if dynamic_env.health_list[eachagent.agent_id] > 0:
                                dynamic_env.health_list[eachagent.agent_id] -= 1
                                # updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = dynamic_env.health_list[eachagent.agent_id]

                            # checking if the agent is dead
                            if dynamic_env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False

                        # handling animosity:
                        rand_prob_propose = random.uniform(0, 1)
                        anim_level = dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        # checking if the agent proposed alliance to this particular opponent:
                        if eachagent.latest_action == dynamic_env.number_of_agents + eachopponent.agent_id:
                            if rand_prob_propose < 0.6:
                                if anim_level > 0:
                                    # decreasing the animosity level
                                    dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id] -= 1

                    # case where the agent accepted an alliance:
                    elif eachagent.latest_action > 2 * dynamic_env.number_of_agents + 1 + 1 - 1: # returns action
                        # that accepted an alliance

                        # handling health_transition:
                        rand_health_prob = random.uniform(0, 1)
                        health_prob = 0

                        # agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id:
                            health_prob = \
                                self.baseline_att_prob * \
                                dynamic_env.health_list[eachopponent.agent_id] * \
                                dynamic_env.agents_list[eachopponent.agent_id].alliance_status
                        # agent is not being attacked by this opponent:
                        else:
                            health_prob = 0

                        # updating the agent's health:
                        if rand_health_prob < health_prob:
                            # updating environmental agent health:
                            if dynamic_env.health_list[eachagent.agent_id] > 0:
                                dynamic_env.health_list[eachagent.agent_id] -= 1
                                # updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = dynamic_env.health_list[eachagent.agent_id]

                            # checking if the agent is dead
                            if dynamic_env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False

                        # handling animosity:
                        rand_prob_accept = random.uniform(0, 1)
                        anim_level = dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        # checking if the agent accepted alliance from this particular opponent:
                        if eachagent.latest_action == 2 * dynamic_env.number_of_agents + 2 + eachopponent.agent_id:
                            if rand_prob_accept < 0.6:
                                if anim_level > 0:
                                    # decreasing the animosity level
                                    dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id] -= 1

                        # alliance_handling:
                        rand_alliance_prob = random.uniform(0, 1)
                        # checking if the agent accepted alliance from this particular opponent:
                        if eachagent.latest_action == 2 * dynamic_env.number_of_agents + 2 + eachopponent.agent_id:

                            # checking if the opponent proposed in the first place:
                            if eachopponent.proposal_request == eachagent.agent_id:

                                # checking if the agent also proposed this opponent:
                                if eachagent.proposal_request == eachopponent.agent_id:
                                    if rand_alliance_prob < 1.001: # they match with a probability of 1
                                        eachagent.alliance_pair = eachopponent
                                        eachopponent.alliance_pair = eachagent

                                # case where agent didn't propose, it depends on animosity:
                                else:
                                    animos = dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                                    if animos != 0:
                                        anim_alliance_prob = 0.6 / animos
                                    else:
                                        anim_alliance_prob = 0.9
                                    # alliance formation
                                    if anim_alliance_prob < rand_alliance_prob:

                                        # handling betrayal animosities with ex-alliance members:
                                        if eachagent.alliance_pair != None: # @TODO: double check this
                                            dynamic_env.animosity_table[eachagent.agent_id][eachagent.alliance_pair.agent_id] = 2

                                        # updating the alliance_pair for both the agents:
                                        eachagent.alliance_pair = eachopponent
                                        eachopponent.alliance_pair = eachagent

                                        # updating the alliance_status for both the agents:
                                        eachagent.alliance_status = 1.5
                                        eachopponent.alliance_status = 1.5

                                        # printing alliance formations:
                                        # print('alliances formed between agent {} and agent {}'.
                                        #       format(eachagent.agent_id, eachopponent.agent_id) )

            # calculating rewards based on each agent's perspective:
            # refreshing a, b, c:
            a = b = c = 0

            a = eachagent.health_list[eachagent.agent_id]
            if eachagent.alliance_pair != None:
                b = eachagent.health_list[eachagent.alliance_pair.agent_id]
            else:
                b = 0
            # finding the id of the opponent this agent chooses to attack, if at all:
            if eachagent.latest_action < dynamic_env.number_of_agents:
                if eachagent.health_list[eachagent.latest_action] == True:
                    c = 1 / eachagent.health_list[eachagent.latest_action]
                else:
                    c = 1.3
            eachagent.current_reward = a + b + c + E