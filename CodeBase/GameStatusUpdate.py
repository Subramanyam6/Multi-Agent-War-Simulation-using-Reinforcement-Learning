import random
import matplotlib.pyplot as plt
import pandas as pd


class GameStatusUpdate:
    def __init__(self, settings):
        self.settings = settings

    def update(self, dynamic_env):
        # Track alliance proposals to detect cycles
        alliance_proposals = {}
        
        # refreshing and documenting proposals for each agent:
        for eachagent in dynamic_env.agents_list:
            eachagent.proposal_request = None
            if eachagent.latest_action > dynamic_env.number_of_agents - 1 \
                    and eachagent.latest_action < 2 * dynamic_env.number_of_agents:
                eachagent.proposal_request \
                    = eachagent.latest_action - dynamic_env.number_of_agents
                # gives the agent_id of the agent that was proposed to
                
                # Track alliance proposals to detect potential cycles
                proposer_id = eachagent.agent_id
                proposed_id = eachagent.proposal_request
                
                if proposer_id not in alliance_proposals:
                    alliance_proposals[proposer_id] = []
                alliance_proposals[proposer_id].append(proposed_id)
                
                # If the same proposal has been made too many times, penalize it
                if len(alliance_proposals[proposer_id]) > 3 and alliance_proposals[proposer_id][-3:].count(proposed_id) == 3:
                    # Penalize repetitive alliance proposals to break cycles
                    eachagent.current_reward -= 0.5

        # iterating over each opponent:
        for eachagent in dynamic_env.agents_list: #TODO: Make sure there isn't any unnecessarily duplicated code
            # Refreshing the current reward:
            eachagent.current_reward = 0
            E = 0
            # checking if the agent is alive:
            if eachagent.is_alive == False:
                continue

            health_prob = 0 # default initialization #TODO: Check if the health_prob updates can be generalized

            for eachopponent in dynamic_env.agents_list:
                rand_health_prob = random.uniform(0, 1)
                # checking if agent and opponent are not the same agent:
                if eachagent.agent_id != eachopponent.agent_id:
                    # checking if the agent is still alive:
                    if eachagent.is_alive == False:
                        continue
                    # checking if the opponent is alive:
                    if eachopponent.is_alive == False:
                        # penalizing the agent for attacking a dead opponent:
                        if eachagent.latest_action == eachopponent.agent_id:
                            E -= self.settings.attack_dead_opponent_penalty
                        continue
                # checking if agent and opponent are the same agent:
                if eachagent.agent_id != eachopponent.agent_id:

                    ########### CASE 1 where the agent chooses the defend action: ###########
                    if eachagent.latest_action == (2 * dynamic_env.number_of_agents):  # returns the defend action
                        # handling health_transition:
                        # agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id:  # attack of agent by the opponent
                            # updating agent's knowledge of opponent's actual health:
                            eachagent.health_list[eachopponent.agent_id] \
                                = dynamic_env.health_list[eachopponent.agent_id]
                            # checking for dead opponent after the above update:
                            if eachopponent.is_alive == False:
                                continue
                            health_prob = \
                                self.settings.baseline_att_prob * dynamic_env.health_list[eachopponent.agent_id] * \
                                dynamic_env.agents_list[eachopponent.agent_id].alliance_status * \
                                self.settings.baseline_def_prob * \
                                1 / dynamic_env.health_list[eachagent.agent_id] * \
                                1 / dynamic_env.agents_list[eachagent.agent_id].alliance_status
                        # agent is not being attacked by this opponent:
                        else:
                            health_prob = 0
                        # updating the agent's health:
                        if rand_health_prob < health_prob:
                            # updating environmental agent health:
                            if dynamic_env.health_list[eachagent.agent_id] > 0:
                                # Use health granularity for decreasing health
                                dynamic_env.health_list[eachagent.agent_id] = dynamic_env.adjust_health(
                                    dynamic_env.health_list[eachagent.agent_id], increase=False)
                                # updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = dynamic_env.health_list[eachagent.agent_id]
                            # checking if the agent is dead:
                            if dynamic_env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False
                        # handling animosity:
                        # no change in animosity when the agent is defending against opponent

                    ########### CASE 2 where the agent chooses recover action: ###########
                    elif eachagent.latest_action == (2 * dynamic_env.number_of_agents + 1):  # returns recover action
                        # handling health_transition:
                        # agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id:  # attack of agent by the opponent
                            # updating agent's knowledge of opponent's actual health:
                            eachagent.health_list[eachopponent.agent_id] \
                                = dynamic_env.health_list[eachopponent.agent_id]
                            # checking for dead opponent after the above update:
                            if eachopponent.is_alive == False:
                                continue
                            health_prob = \
                                self.settings.baseline_att_prob * \
                                1 / dynamic_env.health_list[eachopponent.agent_id] * \
                                1 / dynamic_env.agents_list[eachopponent.agent_id].alliance_status * \
                                self.settings.baseline_recover_prob
                        # agent is not being attacked by this opponent:
                        else:
                            health_prob = self.settings.baseline_recover_prob
                        # updating the agent's health:
                        if rand_health_prob < health_prob:
                            # updating environmental agent health:
                            if dynamic_env.health_list[eachagent.agent_id] < dynamic_env.max_health and eachagent.is_alive == True:
                                # Use health granularity for increasing health
                                dynamic_env.health_list[eachagent.agent_id] = dynamic_env.adjust_health(
                                    dynamic_env.health_list[eachagent.agent_id], increase=True)
                                # updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = dynamic_env.health_list[eachagent.agent_id]
                        # handling animosity:
                        rand_prob_recover = random.uniform(0, 1)
                        anim_level = dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        if rand_prob_recover < self.settings.animosity_decrease_prob:
                            if anim_level > 0:
                                # decreasing the animosity level
                                dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id] -= 1

                    ########### CASE 3 where the agent chooses attack action: ###########
                    elif eachagent.latest_action < dynamic_env.number_of_agents:  # returns one of the attack actions
                        # penalizing the agent for attacking its alliance member:
                        if eachagent.alliance_pair != None:
                            if eachagent.latest_action == eachagent.alliance_pair.agent_id:
                                E -= self.settings.attack_alliance_member_penalty
                        # checking if the agent is attacking this particular opponent:
                        if eachagent.latest_action == eachopponent.agent_id:
                            # updating agent's knowledge of opponent's actual health:
                            eachagent.health_list[eachopponent.agent_id] \
                                = dynamic_env.health_list[eachopponent.agent_id]
                            # checking for dead opponent after the above update:
                            if eachopponent.is_alive == False:
                                continue
                        # handling health_transition:
                        # agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id:  # attack of agent by the opponent
                            health_prob = \
                                self.settings.baseline_att_prob * \
                                dynamic_env.health_list[eachopponent.agent_id] * \
                                dynamic_env.agents_list[eachopponent.agent_id].alliance_status * \
                                self.settings.baseline_underattack_attack_multiplier
                        # agent is not being attacked by this opponent:
                        else:
                            health_prob = self.settings.baseline_notunderattack_attack_prob
                        # updating the agent's health:
                        if rand_health_prob < health_prob:
                            # updating environmental agent health:
                            if dynamic_env.health_list[eachagent.agent_id] > 0:
                                # Use health granularity for decreasing health
                                dynamic_env.health_list[eachagent.agent_id] = dynamic_env.adjust_health(
                                    dynamic_env.health_list[eachagent.agent_id], increase=False)
                                # updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = dynamic_env.health_list[eachagent.agent_id]
                            # checking if the agent is dead:
                            if dynamic_env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False
                        # handling animosity:
                        rand_prob_attack = random.uniform(0, 1)
                        anim_level = dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        if rand_prob_attack < self.settings.animosity_increase_prob:
                            if anim_level < 2:
                                # increasing the animosity level
                                dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id] += 1

                    ########### CASE 4 where the agent proposed an alliance: ###########
                    elif eachagent.latest_action > dynamic_env.number_of_agents - 1 \
                            and eachagent.latest_action < 2 * dynamic_env.number_of_agents:
                        # returns one of the alliance actions
                        # penalizing the agent for proposing to an alliance member:
                        if eachagent.latest_action == eachagent.proposal_request + dynamic_env.number_of_agents:
                            E -= self.settings.propose_alliance_member_penalty
                        # handling health_transition:
                        # agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id:  # attack of agent by the opponent
                            health_prob = \
                                self.settings.baseline_att_prob * \
                                dynamic_env.health_list[eachopponent.agent_id] * \
                                dynamic_env.agents_list[eachopponent.agent_id].alliance_status
                        # agent is not being attacked by this opponent:
                        else:
                            health_prob = 0
                        # updating the agent's health:
                        if rand_health_prob < health_prob:
                            # updating environmental agent health:
                            if dynamic_env.health_list[eachagent.agent_id] > 0:
                                # Use health granularity for decreasing health
                                dynamic_env.health_list[eachagent.agent_id] = dynamic_env.adjust_health(
                                    dynamic_env.health_list[eachagent.agent_id], increase=False)
                                # updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = dynamic_env.health_list[eachagent.agent_id]
                            # checking if the agent is dead:
                            if dynamic_env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False
                        # handling animosity:
                        rand_prob_propose = random.uniform(0, 1)
                        anim_level = dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        # checking if the agent proposed alliance to this particular opponent:
                        if eachagent.latest_action == dynamic_env.number_of_agents + eachopponent.agent_id:
                            if rand_prob_propose < self.settings.animosity_decrease_prob_alliance_proposal:
                                if anim_level > 0:
                                    # decreasing the animosity level:
                                    dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id] -= 1

                    ########### CASE 5 where the agent accepted an alliance: ###########
                    elif eachagent.latest_action > 2 * dynamic_env.number_of_agents + 1 + 1 - 1: # returns action
                        # that accepted an alliance
                        # handling health_transition:
                        # agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id:
                            health_prob = \
                                self.settings.baseline_att_prob * \
                                dynamic_env.health_list[eachopponent.agent_id] * \
                                dynamic_env.agents_list[eachopponent.agent_id].alliance_status
                        # agent is not being attacked by this opponent:
                        else:
                            health_prob = 0
                        # updating the agent's health:
                        if rand_health_prob < health_prob:
                            # updating environmental agent health:
                            if dynamic_env.health_list[eachagent.agent_id] > 0:
                                # Use health granularity for decreasing health
                                dynamic_env.health_list[eachagent.agent_id] = dynamic_env.adjust_health(
                                    dynamic_env.health_list[eachagent.agent_id], increase=False)
                                # updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = dynamic_env.health_list[eachagent.agent_id]
                            # checking if the agent is dead:
                            if dynamic_env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False
                        # handling animosity:
                        rand_prob_accept = random.uniform(0, 1)
                        anim_level = dynamic_env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        # checking if the agent accepted alliance from this particular opponent:
                        if eachagent.latest_action == 2 * dynamic_env.number_of_agents + 2 + eachopponent.agent_id:
                            if rand_prob_accept < self.settings.animosity_decrease_prob_alliance_proposal:
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
                                        anim_alliance_prob = self.settings.alliance_prob_with_some_animosity_baseline / animos
                                    else:
                                        anim_alliance_prob = self.settings.alliance_prob_with_no_animosity
                                    # alliance formation
                                    if rand_alliance_prob < anim_alliance_prob:
                                        # First, properly dissolve any existing alliances
                                        
                                        # If eachagent already has an alliance, dissolve it
                                        if eachagent.alliance_pair is not None:
                                            # Increase animosity with the betrayed ally
                                            dynamic_env.animosity_table[eachagent.agent_id][eachagent.alliance_pair.agent_id] = 2
                                            # Reset the betrayed ally's alliance
                                            old_ally = eachagent.alliance_pair
                                            old_ally.alliance_pair = None
                                            old_ally.alliance_status = 1.0  # Reset to default
                                        
                                        # If eachopponent already has an alliance, dissolve it
                                        if eachopponent.alliance_pair is not None:
                                            # Increase animosity with the betrayed ally
                                            dynamic_env.animosity_table[eachopponent.agent_id][eachopponent.alliance_pair.agent_id] = 2
                                            # Reset the betrayed ally's alliance
                                            old_ally = eachopponent.alliance_pair
                                            old_ally.alliance_pair = None
                                            old_ally.alliance_status = 1.0  # Reset to default
                                        
                                        # Now form the new alliance
                                        eachagent.alliance_pair = eachopponent
                                        eachopponent.alliance_pair = eachagent
                                        # updating the alliance_status for both the agents:
                                        eachagent.alliance_status = self.settings.alliance_status_weight
                                        eachopponent.alliance_status = self.settings.alliance_status_weight
                                        # printing alliance formations:
                                        # print('alliances formed between agent {} and agent {}'.
                                        #       format(eachagent.agent_id, eachopponent.agent_id) )

            # calculating rewards based on each agent's perspective:
            # refreshing a, b, c:
            a = b = c = 0 # a is the agent health, b is the alliance's health, and c is the opponent health
            a = eachagent.health_list[eachagent.agent_id]
            if eachagent.alliance_pair != None:
                b = eachagent.health_list[eachagent.alliance_pair.agent_id]
            # finding the id of the opponent this agent chooses to attack, if at all:
            if eachagent.latest_action < dynamic_env.number_of_agents \
                    and eachagent.health_list[eachagent.latest_action] != 0:
                c = 1/eachagent.health_list[eachagent.latest_action]
            eachagent.current_reward = a + b + c + E # (agent's own health + alliance member's health +
            # opponent's health + action-based reward)