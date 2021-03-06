# coding=utf-8
import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

import numpy as np

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5, get_future_value=False):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        #self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        self.testing = False
        self.train_number = 0
        self.valid_actions =self.env.valid_actions

        self.get_future_value = get_future_value #控制Learn的时候，是否使用下一步的Q值

        return

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
        if testing:
            self.epsilon = 0
            self.testing = True
        else:
            #self.epsilon = 1.0 - self.train_number * 0.001
            #self.epsilon = math.pow(0.999, self.train_number)
            #self.train_number += 1
            #self.epsilon -= 0.05

            #self.epsilon = 1.0/(self.train_number ** 2)

            #self.epsilon = math.exp(-1.0 * self.train_number * 0.002)
            
            self.epsilon = math.cos(self.train_number * 0.001)
	    self.train_number += 1

            #self.epsilon = 1.0

        return

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
                environment. The next waypoint, the intersection inputs, and the deadline 
                are all features available to the agent. """
        # Collect data about the environment
        next_waypoint = self.planner.next_waypoint() # The next waypoint
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        # Set 'state' as a tuple of relevant data for the agent

        state = (inputs['light'], inputs['oncoming'], inputs['left'], inputs['right'], next_waypoint)
        
        return state

    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0

        if state not in self.Q:
            self.Q[state] = {item:0.0 for item in self.valid_actions}
            if self.testing:
                self.emptyQ_during_test += 1

        return

    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ###########
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state
        actions = self.Q[state]
        #key, value = max(actions.items(), key = lambda x: x[1])

        highest = max(actions.values())
        result = [k for k, v in actions.items() if v == highest]

        key = random.choice(result)
        value = actions[key]
        return key,value

    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        # When learning, choose a random action with 'epsilon' probability
        #   Otherwise, choose an action with the highest Q-value for the current state

        if self.learning == False:
            action = random.choice(self.valid_actions)
        else: #base on current state to get action
            if self.testing == False:
                if random.random() < self.epsilon:
                    action = random.choice(self.valid_actions)
                else:
                    action, __ = self.get_maxQ(state)
            else: #testing
                action, __ = self.get_maxQ(state)

        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')

        if self.learning == True and self.testing == False:
            #get current state reward
            current_state = state
            current_state_reward = self.Q[current_state][action]

            #get future_state
            # in env act(), if agent moved to next location, the location and heading of env.agent_state will
            # be set with new location and new heading

            #get new inputs, new next way point according to new location, new heading
            new_inputs = self.env.sense(self)
            new_next_waypoint = self.planner.next_waypoint()

            new_state = (new_inputs['light'], new_inputs['oncoming'],
                         new_inputs['left'], new_inputs['right'], new_next_waypoint)

            if new_state not in self.Q:
                maxq_value = 0
            else:
                maxq_key, maxq_value = self.get_maxQ(new_state)

            if self.get_future_value:
                self.Q[current_state][action] = (1- self.alpha)*current_state_reward + self.alpha*(reward + maxq_value)
            else:
                self.Q[current_state][action] = (1- self.alpha)*current_state_reward + self.alpha*(reward)


        return


    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn

        return

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    #env = Environment(num_dummies=2) # set to 2 as testing
    env = Environment()
    #env.hard_time_limit = -1000
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent, learning=True, epsilon=1.0, alpha = 0.5, get_future_value=False)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, update_delay=0.01, display=False, log_metrics = True, optimized = True)
    
    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test = 10, tolerance=0.1)


if __name__ == '__main__':
    run()
