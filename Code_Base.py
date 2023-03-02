# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 21:27:27 2022

@author: Balu
"""
import random;
import itertools;
import time;

class Environment():
    
    def __init__(self, number_of_agents, health_list):
        
        self.number_of_agents = number_of_agents
        #print('number of agents = ', self.number_of_agents)
        
        self.health_list = list(health_list)
        #print('environment health_list = ', self.health_list)
        
        self.stable_health_list = list(health_list)
        #print('environment stable_health_list = ', self.stable_health_list)
        
        self.agents_list = self.create_agents(number_of_agents, health_list)
        #print('agents created')
        
        self.animosity_table = self.initialize_animosities(self.agents_list)
        #print('initialized animosity_table = ', self.animosity_table)
        
        self.stable_animosity_table = list(self.animosity_table)
        
        print('\nPlease input the learning rate (decimal value between 0 and 1):')
        self.alpha = float(input())
        #print('learning rate, alpha = ', self.alpha)
        
        print('\nPlease input the discount factor (decimal value between 0 and 1):')
        self.beta = float(input())
        #print('discount factor, beta = ', self.beta)
        
        #print('order of actions = n_attacks + n_alliances + defend + recover + n_accept_alliances')
        
        print('\nInitializing the environment', end = "")
        time.sleep(1)
        for i in range(4):
            print('.', end = "")
            time.sleep(1)
        print('\n')
        
    def create_agents(self, number_of_agents, health_list):
        ags = []
        for agent_i in range(0, number_of_agents):
            ags.append(Agent(agent_i, number_of_agents, health_list))
        return ags
            
    def initialize_animosities(self, agents_list):
        
        print('\nPlease select the beginning animosities profile, input a number from (1,2,3): \
            \n  1. High intial animosity between all the agents \
            \n  2. Low initial animosity between all the agents \
            \n  3. Random initial animosities between all the agents')
        anim_profile = int(input())
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
                        animositylistofeachagent.append(random.randrange(0,3,1))
                anim_table.append(animositylistofeachagent)
                
        return anim_table
    

class transitionsRewards():
    def __init__(self, env):
        self.env = env
        self.baseline_att_prob = 0.25
        self.baseline_def_prob = 0.66
        self.baseline_recover_prob = 0.90
        self.basline_underattack_attack_multiplier = 1.20
        self.baseline_notunderattack_attack_prob = 0.20        
        #refreshing and documenting proposals for each agent:
        for eachagent in env.agents_list:
            eachagent.proposal_request = None
            if eachagent.latest_action > env.number_of_agents-1 and eachagent.latest_action < 2*env.number_of_agents:
                eachagent.proposal_request = eachagent.latest_action-env.number_of_agents #gives the agent_id of the agent that was proposed to
        
        #iterating over each opponent:
        for eachagent in env.agents_list:
            
            #Refreshing the current reward:
            eachagent.current_reward = 0;
            E = 0
            
            #checking if the agent is alive:
            if eachagent.is_alive == False:
                continue;
            
            for eachopponent in env.agents_list:
                
                #checking is agent and opponent are not the same agent:
                if eachagent.agent_id != eachopponent.agent_id:
                    
                    #checking if the agent is still alive:
                    if eachagent.is_alive == False:
                        continue;
                
                    #checking if the opponent is alive:
                    if eachopponent.is_alive == False:
                        #penalizing the agent for attacking a dead opponent:
                        if eachagent.latest_action == eachopponent.agent_id:
                            E -= 0.2                    
                        continue;
                
                #checking if agent and opponent are the same agent:
                if eachagent.agent_id != eachopponent.agent_id:
                    
                    #case where the agent chooses the defend action:
                    if eachagent.latest_action == (2*env.number_of_agents): #returns the defend action
                        
                        #handling health_transition:
                        rand_health_prob = random.uniform(0,1)
                        health_prob = 0
                        
                        #agent is being attacked by this opponent:                        
                        if eachopponent.latest_action == eachagent.agent_id: #attack of agent by the opponent
                            
                            #updating agent's knowledge of opponent's actual health:                           
                            eachagent.health_list[eachopponent.agent_id] = env.health_list[eachopponent.agent_id]                           
                            
                            #checking for dead opponent after the above update:
                            if eachopponent.is_alive == False:
                                continue;
                                                        
                            health_prob = \
                            self.baseline_att_prob * \
                            env.health_list[eachopponent.agent_id] * \
                            env.agents_list[eachopponent.agent_id].alliance_status * \
                            self.baseline_def_prob * \
                            1/env.health_list[eachagent.agent_id] * \
                            1/env.agents_list[eachagent.agent_id].alliance_status
                            
                        #agent is not being attacked by this opponent:
                        else:
                            health_prob = 0
                        
                        #updating the agent's health:
                        if rand_health_prob < health_prob:
                            #updating environmental agent health:
                            if env.health_list[eachagent.agent_id] > 0:
                                env.health_list[eachagent.agent_id] -= 1
                                #updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = env.health_list[eachagent.agent_id]
                             
                            #checking if the agent is dead    
                            if env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False

                        #handling animosity:
                        #no change in animosity when the agent is defending against opponent
                            
                    #case where the agent chooses recover action:
                    elif eachagent.latest_action == (2*env.number_of_agents+1): #returns the recover action
                        #handling health_transition:
                        rand_health_prob = random.uniform(0,1)
                        health_prob = 0
                        
                        #agent is being attacked by this opponent:                        
                        if eachopponent.latest_action == eachagent.agent_id: #attack of agent by the opponent
                            
                            #updating agent's knowledge of opponent's actual health:
                            eachagent.health_list[eachopponent.agent_id] = env.health_list[eachopponent.agent_id]
                            
                            #checking for dead opponent after the above update:
                            if eachopponent.is_alive == False:
                                continue;
                            
                            
                            health_prob = \
                            self.baseline_att_prob * \
                            1/env.health_list[eachopponent.agent_id] * \
                            1/env.agents_list[eachopponent.agent_id].alliance_status *\
                            self.baseline_recover_prob
                            
                        #agent is not being attacked by this opponent:
                        else:
                            health_prob = self.baseline_recover_prob
                        
                        #updating the agent's health:
                        if rand_health_prob < health_prob:
                            #updating environmental agent health:
                            if env.health_list[eachagent.agent_id] < 2 and eachagent.is_alive == True:
                                env.health_list[eachagent.agent_id] += 1
                                #updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = env.health_list[eachagent.agent_id]
                             
                        #handling animosity:
                        rand_prob_recover = random.uniform(0,1)
                        anim_level = env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        if rand_prob_recover < 0.3:
                            if anim_level > 0:
                                #decreasing the animosity level
                                env.animosity_table[eachagent.agent_id][eachopponent.agent_id] -= 1                        
                            
                            
                    #case where the agent chooses attack action:
                    elif eachagent.latest_action < env.number_of_agents: # returns one of the attack actions
                        
                        #penalizing the agent for attacking its alliance member:
                        if eachagent.alliance_pair != None:
                            if eachagent.latest_action == eachagent.alliance_pair.agent_id:
                                E -= 0.3
                                
                        #checking if the agent is attacking this particular opponent:
                        if eachagent.latest_action == eachopponent.agent_id:
                            #updating agent's knowledge of opponent's actual health:
                            eachagent.health_list[eachopponent.agent_id] = env.health_list[eachopponent.agent_id]
                            
                            #checking for dead opponent after the above update:
                            if eachopponent.is_alive == False:
                                continue;
                        
                        #handling health_transition:
                        rand_health_prob = random.uniform(0,1)
                        health_prob = 0
                        
                        #agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id: #attack of agent by the opponent
                            health_prob = \
                            self.baseline_att_prob * \
                            env.health_list[eachopponent.agent_id] * \
                            env.agents_list[eachopponent.agent_id].alliance_status *\
                            self.basline_underattack_attack_multiplier
                        #agent is not being attacked by this opponent:
                        else:
                            health_prob = self.baseline_notunderattack_attack_prob
                        
                        #updating the agent's health:
                        if rand_health_prob < health_prob:
                            #updating environmental agent health:
                            if env.health_list[eachagent.agent_id] > 0:
                                env.health_list[eachagent.agent_id] -= 1
                                #updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = env.health_list[eachagent.agent_id]
                             
                            #checking if the agent is dead    
                            if env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False 
                            
                        #handling animosity:
                        rand_prob_attack = random.uniform(0,1)
                        anim_level = env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        if rand_prob_attack < 0.5:
                            if anim_level < 2:
                                #increasing the animosity level
                                env.animosity_table[eachagent.agent_id][eachopponent.agent_id] += 1 
                            
                            
                    #case where the agent proposed an alliance:
                    elif eachagent.latest_action > env.number_of_agents-1 and eachagent.latest_action < 2*env.number_of_agents: #returns one ofthe alliance actions
                        
                        #penalizing the agent for proposing to an alliance member:
                        if eachagent.latest_action == eachagent.proposal_request+env.number_of_agents:
                            E -= 0.2
                            
                        
                        #handling health_transition:
                        rand_health_prob = random.uniform(0,1)
                        health_prob = 0
                        
                        #agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id: #attack of agent by the opponent
                            health_prob = \
                            self.baseline_att_prob * \
                            env.health_list[eachopponent.agent_id] * \
                            env.agents_list[eachopponent.agent_id].alliance_status
                        #agent is not being attacked by this opponent:
                        else:
                            health_prob = 0
                        
                        #updating the agent's health:
                        if rand_health_prob < health_prob:
                            #updating environmental agent health:
                            if env.health_list[eachagent.agent_id] > 0:
                                env.health_list[eachagent.agent_id] -= 1
                                #updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = env.health_list[eachagent.agent_id]
                             
                            #checking if the agent is dead    
                            if env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False 
                                                  
                        #handling animosity:
                        rand_prob_propose = random.uniform(0,1)
                        anim_level = env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        #checking if the agent proposed alliance to this particular opponent:
                        if eachagent.latest_action == env.number_of_agents+eachopponent.agent_id:
                            if rand_prob_propose < 0.6:
                                if anim_level > 0:
                                    #decreasing the animosity level
                                    env.animosity_table[eachagent.agent_id][eachopponent.agent_id] -= 1                                                 
                        
                    
                    #case where the agent accepted an alliance:
                    elif eachagent.latest_action > 2*env.number_of_agents+1+1-1: # returns action that accepted an alliance
                        
                        #handling health_transition:
                        rand_health_prob = random.uniform(0,1)
                        health_prob = 0
                        
                        #agent is being attacked by this opponent:
                        if eachopponent.latest_action == eachagent.agent_id: #attack of agent by the opponent
                            health_prob = \
                            self.baseline_att_prob * \
                            env.health_list[eachopponent.agent_id] * \
                            env.agents_list[eachopponent.agent_id].alliance_status  
                        #agent is not being attacked by this opponent:
                        else:
                            health_prob = 0
                            
                        #updating the agent's health:
                        if rand_health_prob < health_prob:
                            #updating environmental agent health:
                            if env.health_list[eachagent.agent_id] > 0:
                                env.health_list[eachagent.agent_id] -= 1
                                #updating self agent health:
                                eachagent.health_list[eachagent.agent_id] = env.health_list[eachagent.agent_id]
                             
                            #checking if the agent is dead    
                            if env.health_list[eachagent.agent_id] == 0:
                                eachagent.is_alive = False
                        
                        #handling animosity:
                        rand_prob_accept = random.uniform(0,1)
                        anim_level = env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                        #checking if the agent accepted alliance from this particular opponent:
                        if eachagent.latest_action == 2*env.number_of_agents+2+eachopponent.agent_id:
                            if rand_prob_accept < 0.6:
                                if anim_level > 0:
                                    #decreasing the animosity level
                                    env.animosity_table[eachagent.agent_id][eachopponent.agent_id] -= 1
                        
                        #alliance_handling:
                        rand_alliance_prob = random.uniform(0,1)
                        #checking if THIS opponent's proposal was accepted:
                        if eachagent.latest_action == 2*env.number_of_agents+2+eachopponent.agent_id:
                            
                            #checking if the opponent proposed in the first place:
                                if eachopponent.proposal_request == eachagent.agent_id:
                                    
                                    #checking if agent also proposed this opponent:
                                    if eachagent.proposal_request == eachopponent.agent_id:
                                        if rand_alliance_prob < 1:
                                            eachagent.alliane_pair = eachopponent
                                            eachopponent.alliance_pair = eachagent
                                            
                                    #case where agent didnt' propose, it depends on animosity:
                                    else:
                                        animos = env.animosity_table[eachagent.agent_id][eachopponent.agent_id]
                                        if animos != 0:
                                            anim_alliance_prob = 0.6/animos
                                        else:
                                            anim_alliance_prob = 0.9
                                        #alliance formation    
                                        if anim_alliance_prob < rand_alliance_prob:
                                            
                                            #Handling betrayal animosities:
                                            if eachagent.alliance_pair != None:
                                                env.animosity_table[eachagent.agent_id][eachopponent.agent_id] = 2                                                                                   
                                            
                                            #updating the alliance_pair for both the agents:
                                            eachagent.alliane_pair = eachopponent
                                            eachopponent.alliance_pair = eachagent
                                            
                                            #updating the alliance_status for both the agents:
                                            eachagent.alliance_status = 1.5
                                            eachopponent.alliance_status = 1.5
                                            
                                            #printing alliance formations:
                                            #print('alliances formed between agent {} and agent {}'.format(eachagent.agent_id, eachopponent.agent_id) )
                                            
        
            #calculating rewards based on each agent's perspective:
            #refreshing a, b, c:
            a = b = c = 0;
                                            
            a = eachagent.health_list[eachagent.agent_id]
            if eachagent.alliance_pair != None:
                b = eachagent.health_list[eachagent.alliance_pair.agent_id]
            else:
                b = 0
            #finding the id of the opponent this agent chooses to attack, if at all:
            if eachagent.latest_action < env.number_of_agents:
                if eachagent.health_list[eachagent.latest_action] == True:
                    c = 1/eachagent.health_list[eachagent.latest_action]
                else:
                    c = 1.3
            eachagent.current_reward = a+b+c+E
                       
class Agent():
    
    def __init__(self, agent_id, number_of_agents, health_list):
        self.number_of_agents = number_of_agents
        self.agent_id = agent_id
        
        self.health_list = list(health_list)
        self.stable_health_list = list(health_list)
        
        self.actions = self.create_actions(agent_id, number_of_agents)
        self.latest_action = None
        
        self.alliance_status = 1 #this is 1 by default, will change to 1.5 with alliance formations
        self.stable_alliance_status = 1
        
        self.proposal_request = None
        
        self.alliance_pair = None #this agent object is updated as per alliance formation/breakups
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
        #n_attacks + n_alliances + defend + recover + n_accept_alliances
        for act in range(0, number_of_agents+number_of_agents+1+1+number_of_agents):
            acts.append(act)
        acts.remove(agent_id) #removing agent's self-attack
        acts.remove(agent_id+number_of_agents) #removing agent's self-alliance
        acts.remove(2*number_of_agents+2+agent_id) #removing agent's self-acceptance
        return acts
    
    def choose_action(self, t): # t is a time-step until which agents choose random actions
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
        for i in range(self.number_of_agents*3+2):
            if self.Q_table[self.snext_index][i] > max:
                max = self.Q_table[self.snext_index][i]
        self.val_snext = max
    

class Simulation():
    def __init__(self):
        
        print('Please enter the number of agents for the battle: ')
        number_of_agents = int(input())
        
        print('\nPlease select the beginning health profile for the agents, input a number from (1, 2, 3, 4): \
              \n  1. Each agent starts with full health \
              \n  2. Each agent starts with low health \
              \n  3. Each agent starts with random health \
              \n  4. Half the agents start with low health and half the agents start with full health')
        starting_health_config = int(input())
        
        start_health_list = []
        
        if starting_health_config == 1:
            start_health_list = []
            for eachagent in range(number_of_agents):
                start_health_list.append(2)
        elif starting_health_config == 2:
            start_health_list = []
            for eachagent in range(number_of_agents):
                start_health_list.append(1)
        elif starting_health_config == 3:
            start_health_list = []
            for eachagent in range(number_of_agents):
                start_health_list.append(random.randrange(0,2,1))
        elif starting_health_config == 4:
            start_health_list = []
            counter = 0
            for eachagent in range(number_of_agents):
                if counter < number_of_agents/2 - 1:
                    start_health_list.append(1)
                else:
                    start_health_list.append(2)
                counter += 1
        
        self.env = Environment(number_of_agents, start_health_list);
        
        print('\nPlease input the number of iterations for the Q-learning algorithm:')
        self.max_iteration = int(input());
        
        self.game_is_on = True;
        
        #creating the states:
        self.states_list = []
        iterables = []
        #appending all possible healths to the state:
        for eachagent in self.env.agents_list:
            iterables.append([0, 1, 2])
        
        #appending alliance status to the state:
        iterables.append([1, 1.5])
        
        #creating the list of states:
        for t in itertools.product(*iterables):
            self.states_list.append(t)
        
        #creating the keys(of indices) dictionary of each state:
        self.states_dict = {}
        i = 0;
        for eachstate in self.states_list:
            #print('printing each state: ', eachstate)
            self.states_dict[eachstate] = i
            i += 1
    
        #creating a Q-table for each agent:
        for everyagent in self.env.agents_list:
            for eachstate in self.states_list:
                temp = []
                #using the generic total number of actions
                for i in range(self.env.number_of_agents*3+2):
                    temp.append(0)   
                everyagent.Q_table.append(temp)
    
        #print('printing sample Q table: ', self.env.agents_list[0].Q_table)
        #print('Simulation running successfully')
        
        
    #starting the run
    def run(self):
        print('\nAgents are now fighting', end = "")
        time.sleep(1)
        
        for i in range(4):
            print('.', end = "")
            time.sleep(1)
        print('\n')
        
        while self.game_is_on:
            t = 0;
            reset = False;
            while t < self.max_iteration:
                                
                alive_list = []
		    
                #computing state index for the Q-table:
                for eachagent in self.env.agents_list:
                    temp_state = list(eachagent.health_list)
                    temp_state.append(eachagent.alliance_status)
                    s_key = tuple(temp_state)
                    eachagent.s_index = self.states_dict[tuple(s_key)]                        
                
                #choosing an action for each agent
                for eachagent in self.env.agents_list:
                    eachagent.choose_action(t)
                    
                #updating the dummy game's state
                transitionsRewards(self.env)
                
                #computing s_next index for the Q-table:
                for eachagent in self.env.agents_list:
                    temp_next_state = list(eachagent.health_list)
                    temp_next_state.append(eachagent.alliance_status)
                    snext_key = tuple(temp_next_state)
                    eachagent.snext_index = self.states_dict[tuple(snext_key)]
                    #updating the value of snext:
                    eachagent.compute_val_snext();
                    """
                    #checking for state transition for the rewards:
                    """ 
                
                #updating the Q-table:
                for eachagent in self.env.agents_list:
                    eachagent.Q_table[eachagent.s_index][eachagent.latest_action] = \
                        (1-self.env.alpha)*eachagent.Q_table[eachagent.s_index][eachagent.latest_action] \
                            + self.env.alpha*(eachagent.current_reward + self.env.beta*eachagent.val_snext)
                    
                #checking how many agents are alive:               
                for eachagent in self.env.agents_list:
                    if eachagent.is_alive == True:
                        alive_list.append(eachagent)
                
                #checking if only members from one alliance are left:
                if len(alive_list) == 2:
                    if alive_list[0].alliance_pair == alive_list[1]:
                        reset = True;
                        
                #checking only if one agent is left:
                elif len(alive_list) == 1:
                    reset = True;
                    
                #resetting to the original state if the dummy game is over:   
                if reset == True:
                    
                    #refreshing environment health_list with the original values:
                    self.env.health_list = list(self.env.stable_health_list)
                    self.animosity_table = list(self.env.stable_animosity_table)
                    
                    #refreshing the attributes of the agent with original values:
                    for eachagent in self.env.agents_list:
                        eachagent.health_list = list(eachagent.stable_health_list)
                        eachagent.alliance_status = eachagent.stable_alliance_status
                        eachagent.alliance_pair = eachagent.stable_alliance_pair
                        eachagent.is_alive = eachagent.stable_is_alive
                
                t += 1;
            
            #print('subgame timestep = {}'.format(t))
            self.update_time_step()
            

    #executing the actions of each agent and taking the game to the next time step:
    def update_time_step(self):
        
        alive_list_final = []
        
        #refreshing environment health_list and animosity table with the original values:
        self.env.health_list = list(self.env.stable_health_list)
        self.animosity_table = list(self.env.stable_animosity_table)
        
        #refreshing the attributes of the agent with original values:
        for eachagent in self.env.agents_list:
            eachagent.health_list = list(eachagent.stable_health_list)
            eachagent.alliance_status = eachagent.stable_alliance_status
            eachagent.alliance_pair = eachagent.stable_alliance_pair
            eachagent.is_alive = eachagent.stable_is_alive
        
        #choosing action for each agent:
        for eachagent in self.env.agents_list:
            eachagent.choose_action(10000) #agents should always choose best action
        
        #updating the game:
        transitionsRewards(self.env)
        
        #updating the environment health_list and animosity table:
        self.env.stable_health_list = list(self.env.health_list)
        self.env.stable_animosity_table = list(self.env.animosity_table)
        
        #updating the state indirectly by updating the health list and alliance status:
        for eachagent in self.env.agents_list:
            eachagent.stable_health_list = list(eachagent.health_list)
            eachagent.stable_alliance_status = eachagent.alliance_status
            eachagent.stable_alliance_pair = eachagent.alliance_pair
            eachagent.stable_is_alive = eachagent.is_alive
        
        #checking how many agents are alive:               
        for eachagent in self.env.agents_list:
            if eachagent.is_alive == True:
                alive_list_final.append(eachagent)
                
        #checking if only members from one alliance are left:
        if len(alive_list_final) == 2:
            if alive_list_final[0].alliance_pair == alive_list_final[1]:
                self.game_is_on = False;
                print('\nThe winner is the team of Agents - {} and {}'.format(alive_list_final[0].agent_id,alive_list_final[1].agent_id))
                        
        #checking only if one agent is left:
        elif len(alive_list_final) == 1:
            self.game_is_on = False;
            print('\nThe winner is Agent - {}'.format(alive_list_final[0].agent_id))
            #print(alive_list_final[0].Q_table)
        
        
def main():
    print('Murugan')
    print('Launching the program', end = "")
    time.sleep(1)
    for i in range(4):
        print('.', end = "")
        time.sleep(1)
    
    print('\n')
    Simulation().run()

if __name__ == '__main__':
    main()
                
                
            
        
        
        
    
        
    
    

