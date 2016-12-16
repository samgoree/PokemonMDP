# POMDP.py
# Rather than a truely POMDP model (with state being probabilistic), we assume that a given state is fully 
# observable, but that our knowledge of probabilities that actions taken in a given state lead to another given 
# state is limited. This is more accurate to the pokemon problem, since we can observe most of the features of a state

# Instead of constantly updating our model, we use an update method to update our frequency counts that any state 
# will lead to any other state and a generate_policy method to use the frequencies to recalculate probabilities, 
# then use the modified policy iteration algorithm for solving MDPs to figure out a policy. This is Q-Learning

# We don't use the Q-learning algorithm built into mdptoolbox because it just samples data from what it assumes is
# perfect information, which we don't have

import numpy as np
import mdptoolbox

verbose = True

epsilon = 10**-6

class POMDP:
	# state_attribute_values should be a list of the number of possible values for each attribute of a gamestate, the "shape" of state space
	# num_actions_possible is the number of total possible actions that exist
	# value_function is a function that takes a state two states and outputs the integer value
	def __init__(self, state_attribute_values, num_actions_possible, value_function):
		self.state_attribute_values = state_attribute_values
		self.num_actions_possible = num_actions_possible
		self.value_function = value_function
		num_states = np.prod(state_attribute_values)
		# initialize Actions * States * States array of frequencies, let each start with a pseudocount of 1
		
		self.freqs = np.ones([num_actions_possible, num_states, num_states], dtype=np.int32)
		# initialize matrix tracking rewards, states by actions
		self.reward_frequencies = np.ones([num_states, num_actions_possible], dtype=np.int32)
		# call generate_policy to have an initial policy
		self.generate_policy()


	def state_to_int(self, state):
		index = 0
		stride = 1
		for i,attribute in reversed(list(enumerate(self.state_attribute_values))):
			index += stride * state[i]
			stride *= attribute
		return index

	def int_to_state(self, index):
		rev_state = []
		for i,attribute in reversed(list(enumerate(self.state_attribute_values))):
			rev_state.append(index % attribute)
			index //= attribute
		rev_state.reverse()
		return rev_state


	def getMove(self, state):
		return self.policy[self.state_to_int(state)]

	def update(self, start_state, end_state, action):
		self.freqs[action, self.state_to_int(start_state), self.state_to_int(end_state)] +=1
		self.reward_frequencies[self.state_to_int(start_state), action] += self.value_function(start_state, end_state)

	# this function is computationally expensive and should not be called mid-game!
	# stochastic adds gaussian noise to probabilities so that the policy doesn't deterministically depend on the frequencies
	# if seed is None, numpy won't be fed a specific seed and will probably use system time instead
	def generate_policy(self, stochastic=True, seed=None):
		# convert frequencies into probabilities
		if stochastic:
			if seed is not None:
				np.random.seed(seed)
			stddev = np.std(self.freqs)/10 + epsilon # prevent this from ever being zero
			freqs = np.float32(self.freqs) + np.random.normal(scale=stddev, size=self.freqs.shape)
		else:
			freqs = self.freqs
		P = np.zeros_like(self.freqs, dtype=np.float64)
		for i, action in enumerate(self.freqs):
			for j, state in enumerate(action):
				total = np.sum(state)
				for k, state2 in enumerate(state):
					P[i,j,k] = state2 / total
				P[i,j,-1] = 1 - np.sum(P[i,j,:-1])
				#assert np.sum(P[i,j]) == 1

		# This might be dumb, I'm just using the reward frequencies (i.e. each time we have a good or bad thing happen we
		# increment/decrement reward frequency so that eventually it probably resembles a reward function)
		print(P[P<0])
		P = np.maximum(np.zeros_like(P), P)
		mdp = mdptoolbox.mdp.PolicyIterationModified(P, self.reward_frequencies, 0.9)
		mdp.run()
		# a policy is a list of all the states, where the value in position i is the index of the best move to make in position i
		self.policy = mdp.policy

	# write the frequencies (human readable) to a file for use later
	def save_freqs(self, path):
		f = open(path, 'w')
		shape = ''.join([str(val) + ',' for val in self.state_attribute_values])
		f.write(shape + '\n')
		f.write(str(self.num_actions_possible) + '\n')
		for i in range(len(self.freqs)):
			for j in range(len(self.freqs[i])):
				for k in range(len(self.freqs[i][j])):
					f.write(str(self.freqs[i][j][k]) + ',')
				f.write('\n')
			f.write('\n')
		f.write('\n')
		for i in range(len(self.reward_frequencies)):
			for j in range(len(self.reward_frequencies[i])):
				f.write(str(self.reward_frequencies[i][j]) + ',')
			f.write('\n')

	# load frequencies from a file
	# if replace is true, these frequencies will replace the frequencies in this POMDP object instead of summing
	def load_freqs(self, path, replace=False):
		f = open(path, 'r')
		lines = f.split('\n')
		shape = [int(i) for i in lines[0].split(',')]
		# check that we're describing the same shaped state space
		assert (shape == self.state_attribute_values).all()
		num_actions = int(lines[1])
		# check that we have the same number of possible actions
		assert num_actions == self.num_actions_possible
		line_num = 2
		if replace:
			for i in range(num_actions):
				for j in range(np.prod(shape)):
					for k,val in enumerate(lines[line_num].split(',')[:-1]):
						self.freqs[i,j,k] = val
					line_num += 1
				# we should have a blank line in between each of the first dimension rows
				assert lines[line_num] == ''
				line_num += 1
			# now that we're done processing transition frequencies, we should have another newline
			assert lines[line_num] == ''
			line_num += 1
			for i in range(np.prod(shape)):
				for j,val in enumerate(lines[line_num].split(',')):
					self.reward_frequencies[i,j] = val
				line_num += 1
		else: # sum instead
			for i in range(num_actions):
				for j in range(np.prod(shape)):
					for k,val in enumerate(lines[line_num].split(',')):
						self.freqs[i,j,k] += val
					line_num += 1
				# we should have a blank line in between each of the first dimension rows
				assert lines[line_num] == ''
				line_num += 1
			# now that we're done processing transition frequencies, we should have another newline
			assert lines[line_num] == ''
			line_num += 1
			for i in range(np.prod(shape)):
				for j,val in enumerate(lines[line_num].split(',')):
					self.reward_frequencies[i,j] += val
				line_num += 1
	def save_policy(self, path):
		f = open(path, 'w')
		# enumerate every possible gamestate
		for i in range(np.prod(self.state_attribute_values)):
			state = self.int_to_state(i)
			s = str(state) + ':' + str(self.policy[i]) + '\n'
			f.write(s)

				


def test():
	import mdptoolbox.example
	P, R = mdptoolbox.example.forest()
	mdp = POMDP([len(P[0])], len(P), lambda s, a: R[s[0],a])
	for i in range(100):
		total_reward = 0
		for i2 in range(100):
			first_state = [np.random.randint(len(P[0]))]
			action = mdp.getMove(first_state)
			# sample state from dist in P[action,first_state]
			second_state = [np.random.choice(len(P[action,first_state[0]]), 1, p=P[action,first_state[0]])]
			mdp.update(first_state, second_state, action)
			total_reward += mdp.value_function(first_state, second_state)
		print("Trial", i,"Total reward:", total_reward)
		mdp.generate_policy()
	print(mdp.policy)
	mdp.save_freqs('output.csv')