PokemonMDP - a reinforcement learning approach to Pokemon Showdown
==========
## Sam Goree and Josh Parker

The architecture we envision has two components: a “frontend” that interfaces with the Pokemon Showdown server (available open-source at https://github.com/Zarel/Pokemon-Showdown) and a “backend” that keeps track of the gamestate and manages the Markov decision process and chooses moves. The frontend will imitate the networking I/O of the pokemon showdown client so that we can use a locally hosted server to manage the game with little to no modification to their source code. The backend will get information about the transitions in gamestate that occurred from the frontend, and use the MDP model to decide what move to make, which the frontend will send to the server.


The internals of the backend will probably be tabular -- a MDP is a five-tuple of a finite set of states, a finite set of actions, probabilities that actions taken in a given state will lead to a certain other state, expected rewards from a given state and action and a discount factor, which tells us how much to prioritize short-term rewards over long-term rewards. All of these will be stored in lists and built on-line according to the algorithm in Arvey and Aaron -- every move will add to the stored data and new transition probabilities/expected rewards will be computed periodically.

While the on-line training procedure didn't end up working out, we did manage to build a working MDP, train it on game logs and output a policy that could control a bot we wrote in javascript (a [fork](https://github.com/samgoree/leftovers-again) of [leftovers-again](https://github.com/dramamine/leftovers-again)).

## To Use:

0. Make sure you have python installed, with numpy and scipy (I like [Anaconda](https://www.continuum.io/downloads), since it ships with both)
1. Install PyMDPToolbox using pip (follow the instructions at https://github.com/sawcordwell/pymdptoolbox) or by calling python setup.py install in the included pymdptoolbox directory
2. Install pokemon showdown server (follow the instructions at https://github.com/zarel/Pokemon-Showdown), in the included Pokemon-Showdown directory
3. call python MDPRecorder.py and put the training data (in JSON format, like testout3) into stdin (I did this by using cat ../game/log/directory/output* | MDPRecorder.py to train on lots of game logs)
4. MDPRecorder.py will save a policy to 'policy.txt' in the same directory
5. move policy.txt to leftovers-again/src/bots/mdp
6. start your pokemon showdown server, then call npm start -- mdp --opponent=<other bot name, for instance, meethefakers>