PokemonMDP - a reinforcement learning approach to Pokemon Showdown
==========
## Sam Goree and Josh Parker

The architecture we envision has two components: a “frontend” that interfaces with the Pokemon Showdown server (available open-source at https://github.com/Zarel/Pokemon-Showdown) and a “backend” that keeps track of the gamestate and manages the Markov decision process and chooses moves. The frontend will imitate the networking I/O of the pokemon showdown client so that we can use a locally hosted server to manage the game with little to no modification to their source code. The backend will get information about the transitions in gamestate that occurred from the frontend, and use the MDP model to decide what move to make, which the frontend will send to the server.


The internals of the backend will probably be tabular -- a MDP is a five-tuple of a finite set of states, a finite set of actions, probabilities that actions taken in a given state will lead to a certain other state, expected rewards from a given state and action and a discount factor, which tells us how much to prioritize short-term rewards over long-term rewards. All of these will be stored in lists and built on-line according to the algorithm in Arvey and Aaron -- every move will add to the stored data and new transition probabilities/expected rewards will be computed periodically.


Alternatively if Professor Eck is ok with it, we’ll use code modified from a library (https://github.com/sawcordwell/pymdptoolbox) for the backend and save time.


So far we haven’t made any progress on the implementation, though we have constructed the two teams to pair off against one another with help from a third-party consultant (our friend, who used to be a moderator on pokemonshowdown.com).


We still need to construct the front end (the program which will interface with the pokemon showdown servers) and our backend (the program which makes the choices for each team in our simulation). The length of time budgeted for each part will likely need to be at least a couple of weeks. However, if we’re allowed to use libraries for any of the machine learning, that should reduce the amount of time we’ll need to budget for the backend. Because of that, I think our timeline should be such that we start by early November, finish the front end first since we can’t test either of the others without it, and then the backend. 