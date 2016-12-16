# MDPRecorder.py
# when run, accepts game states from stdin and outputs moves to stdout

import sys
import POMDP
import json
from collections import OrderedDict

mdp = None

pokemon_name_codes = OrderedDict([
	("medicham", 0), 
	("hitmonlee", 1),
	("jynx", 2),
	("ludicolo", 3),
	("weavile", 4),
	("infernape", 5)])

# we've probably got a lot of unnecessary state information that we want to clean up
# we want the opponent's active pokemon (with HP to nearest 50%), our active pokemon (same stuff)
# whether each pokemon in our reserves is alive and whether each pokemon in their reserves is alive
# active pokemon number
# HP%
# 1-hot for each status
def att_to_state(att_dict):
	state = []
	# if we have no active pokemon, skip this part
	if att_dict["self"]["active"] == []:
		state.append(6) # not a pokemon
		state.append(3) # no hp
	else:
		# our name
		state.append(pokemon_name_codes[att_dict["self"]["active"]["id"]])
		# our HP
		if "hppct" in att_dict["self"]["active"]:
			state.append((att_dict["self"]["active"]["hppct"]-1) // 50)
		else:
			state.append((att_dict["self"]["active"]["hp"] * 2 // att_dict["self"]["active"]["maxhp"]))
		# our remaining reserves 
	state.append(6)
	for name in pokemon_name_codes.keys():
		if att_dict["self"]["active"] != []:
			if att_dict["self"]["active"]["id"] == name:
				continue
		else:
			for mon in att_dict["self"]["reserve"]:
				if mon["id"] == name:
					if "hppct" in mon.keys():
						state[-1] -= 1 if mon["hppct"] == 0 else 0
					elif "dead" in mon.keys():
						state[-1] -= 1 if mon["dead"] == True else 0
					else:
						print(mon)
						print("Something's fucked with this pokemon")
					break
			
	# their name
	#state.append(pokemon_name_codes[att_dict["opponent"]["active"]["id"]])
	# their HP
	#state.append(att_dict["opponent"]["active"]["hppct"]-1 // 50)
	# their remaining reserves
	state.append(6)
	for name in pokemon_name_codes.keys():
		if att_dict["opponent"]["active"] != []:
			if att_dict["opponent"]["active"]["id"] == name:
				continue
		for mon in att_dict["opponent"]["reserve"]:
			if mon["id"] == name:
				if "hppct" in mon.keys():
					state[-1] -= 1 if mon["hppct"] == 0 else 0
				elif "dead" in mon.keys():
					state[-1] -= 1 if mon["dead"] == True else 0
				else:
					print(mon)
					print("Something's fucked with this pokemon")
				break
			
	return state


num_values_per_attribute = [len(pokemon_name_codes)+1, 4, 7, 7]

prev_action = None
prev_state = None
for line in sys.stdin:
	try:
		state_str, action_str = line.split('###')
		attributes = json.loads(state_str)
		current_state = att_to_state(attributes)
		if mdp is None:
			# Important: update this is the state encoding changes at all!!
			our_pokemon = 2
			their_pokemon = 3
			value = lambda first_state, second_state: second_state[our_pokemon] - first_state[our_pokemon] - second_state[their_pokemon] + first_state[their_pokemon]
			mdp = POMDP.POMDP(num_values_per_attribute, 10, value)

		# handle action
		if len(action_str) <= 3:
			prev_action = int(action_str)
		else:
			current_action = json.loads(action_str)
			prev_action = 4 + pokemon_name_codes[current_action['id']['id']]
		if prev_state is not None and prev_action is not None:
			mdp.update(prev_state, current_state, prev_action)
		prev_state = current_state
	except KeyError:
		print(line)
		print("ignoring parse error line")
		prev_action = None
		prev_state = None

# record the resulting policy
mdp.generate_policy()
mdp.save_policy('policy.txt')


