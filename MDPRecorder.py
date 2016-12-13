# MDPRecorder.py
# when run, accepts game states from stdin and outputs moves to stdout

import sys
import POMDP
import json
from collections import OrderedDict

mdp = None

pokemon_statuses = [] #TODO!!
pokemon_name_codes = OrderedDict([
	("gliscor", 0), 
	("shedinja", 1), 
	("scyther", 2), 
	("carracosta", 3), 
	("torterra", 4), 
	("blissey", 5), 
	("guzzlord", 6), 
	("victini", 7), 
	("clawitzer", 8), 
	("vespiquen", 9), 
	('skuntank', 10),
	('exeggutor', 11)])

# we've probably got a lot of unnecessary state information that we want to clean up
# we want the opponent's active pokemon (with HP to nearest 10% and statuses), our active pokemon (same stuff)
# whether each pokemon in our reserves is alive and whether each pokemon in their reserves is alive
# active pokemon number
# HP%
# 1-hot for each status
def att_to_state(att_dict):
	state = []
	# if we have no active pokemon, skip this part
	if att_dict["self"]["active"] == []:
		pass # TODO: figure out how to handle this
	else:
		# our name
		state.append(pokemon_name_codes[att_dict["self"]["active"]["id"]])
		# our HP
		state.append(att_dict["self"]["active"]["hppct"] // 10)
		# our statuses
		for status in pokemon_statuses:
			if status in att_dict["self"]["active"]["statuses"]:
				state.append(1)
			else: state.append(0)
		# our remaining reserves 
		for name in pokemon_name_codes.keys():
			if att_dict["self"]["active"]["id"] == name:
				state.append(1)
				continue
			for mon in att_dict["self"]["reserve"]:
				if mon["id"] == name:
					if "hppct" in mon.keys():
						state.append(0 if mon["hppct"] == 0 else 1)
					elif "dead" in mon.keys():
						state.append(0 if mon["dead"] == True else 1)
					else:
						print(mon)
						print("Something's fucked with this pokemon")
					break
			
	if att_dict["opponent"]["active"] == []:
		pass # TODO: figure out how to handle this
	else:
		# their name
		state.append(pokemon_name_codes[att_dict["opponent"]["active"]["id"]])
		# their HP
		state.append(att_dict["opponent"]["active"]["hppct"] // 10)
		# their statuses
		for status in pokemon_statuses:
			if status in att_dict["opponent"]["active"]["statuses"]:
				state.append(1)
			else: state.append(0)
		# their remaining reserves
		for name in pokemon_name_codes.keys():
			if att_dict["opponent"]["active"]["id"] == name:
				state.append(1)
				continue
			for mon in att_dict["opponent"]["reserve"]:
				if mon["id"] == name:
					if "hppct" in mon.keys():
						state.append(0 if mon["hppct"] == 0 else 1)
					elif "dead" in mon.keys():
						state.append(0 if mon["dead"] == True else 1)
					else:
						print(mon)
						print("Something's fucked with this pokemon")
					break
			
	return state


num_values_per_attribute = [len(pokemon_name_codes), 11] + [2 * len(pokemon_statuses)] + [2 * len(pokemon_name_codes
							)] + [len(pokemon_name_codes), 11] + [2 * len(pokemon_statuses)] + [2 * len(pokemon_name_codes)]

prev_action = None
prev_state = None
for line in sys.stdin:
	attributes = json.loads(line)
	if "self" not in attributes.keys():
		continue  # I think this case corresponds to the move encoding, TODO
	current_state = att_to_state(attributes)
	if mdp is None:
		# Important: update this is the state encoding changes at all!!
		our_pokemon = 2 + len(pokemon_statuses)
		their_pokemon = 4 + 2 * len(pokemon_statuses) + len(pokemon_name_codes)
		value = lambda first_state, second_state: sum(second_state[our_pokemon: our_pokemon + len(pokemon_name_codes)]
													) - sum(first_state[our_pokemon: our_pokemon + len(pokemon_name_codes)]
													) - (sum(second_state[their_pokemon: their_pokemon + len(pokemon_name_codes)])
															- sum(first_state[their_pokemon: their_pokemon + len(pokemon_name_codes)])
		mdp = POMDP.POMDP(num_values_per_attribute, 9, value)
	if prev_state is not None and prev_action is not None:
		mdp.update(prev_state, current_state, prev_action)
	prev_state = current_state

# record the resulting policy
mdp.generate_policy()
mdp.save_policy('policy.txt')


"""
{"self":{"active":[],
		"reserve":[
			{"dead":true,
			 "condition":"0 fnt",
			 "statuses":[],
			 "id":"kartana",
			 "species":"Kartana",
			 "moves":[
			 	{"accuracy":true,
			 	 "category":"Status",
			 	 "id":"swordsdance",
			 	 "name":"Swords Dance",
			 	 "flags":{"snatch":1},
			 	 "target":"self",
			 	 "type":"Normal"},
			 	{"accuracy":100,
			 	 "basePower":70,
			 	 "category":"Physical",
			 	 "id":"psychocut",
			 	 "name":"Psycho Cut",
			 	 "flags":{"protect":1,"mirror":1},
			 	 "target":"normal","type":"Psychic"},
			 	{"accuracy":100,
			 	 "basePower":90,
			 	 "category":"Physical",
			 	 "id":"sacredsword",
			 	 "name":"Sacred Sword",
			 	 "flags":{"contact":1,"protect":1,"mirror":1},
			 	 "target":"normal",
			 	 "type":"Fighting"},
			 	{"accuracy":100,
			 	 "basePower":90,
			 	 "category":"Physical",
			 	 "id":"leafblade",
			 	 "name":"Leaf Blade",
			 	 "flags":{"contact":1,"protect":1,"mirror":1},
			 	 "target":"normal","type":"Grass"}
			 	],
			 "level":75,
			 "gender":"M",
			 "maxhp":212,
			 "types":["Grass","Steel"],
			 "baseStats":{"hp":59,"atk":181,"def":131,"spa":59,"spd":31,"spe":109},
			 "abilities":{"0":"Beast Boost"},
			 "baseAbility":"beastboost",
			 "stats":{"atk":315,"def":240,"spa":132,"spd":90,"spe":207},
			 "position":"p2a",
			 "owner":"p2",
			 "item":"lifeorb",
			 "boosts":{"atk":2},
			 "prevMoves":["leafblade","sacredsword","sacredsword","sacredsword"],
			 "nickname":"Kartana",
			 "seenMoves":["sacredsword","leafblade"],
			 "boostedStats":{"atk":630,"def":240,"spa":132,"spd":90,"spe":207}},
			{"condition":"229/229",
			  "statuses":[],
			  "id":"lilligant",
			  "species":"Lilligant","moves":[{"accuracy":100,"basePower":120,"category":"Special","id":"petaldance","name":"Petal Dance","flags":{"contact":1,"protect":1,"mirror":1},"self":{"volatileStatus":"lockedmove"},"target":"randomNormal","type":"Grass"},{"accuracy":100,"basePower":60,"category":"Special","id":"hiddenpower","name":"Hidden Power Rock","flags":{"protect":1,"mirror":1},"target":"normal","type":"Rock"},{"accuracy":75,"category":"Status","id":"sleeppowder","name":"Sleep Powder","flags":{"powder":1,"protect":1,"reflectable":1,"mirror":1},"target":"normal","type":"Grass"},{"accuracy":true,"category":"Status","id":"quiverdance","name":"Quiver Dance","flags":{"snatch":1},"target":"self","type":"Bug"}],"level":75,"gender":"F","hp":229,"maxhp":229,"hppct":100,"types":["Grass"],"baseStats":{"hp":70,"atk":60,"def":75,"spa":110,"spd":75,"spe":90},"abilities":{"0":"Chlorophyll","1":"Own Tempo","H":"Leaf Guard"},"baseAbility":"owntempo","stats":{"atk":95,"def":156,"spa":209,"spd":156,"spe":179},"owner":"p2","item":"leftovers","prevMoves":[],"order":1,"nickname":"Lilligant","seenMoves":[],"boostedStats":{"atk":95,"def":156,"spa":209,"spd":156,"spe":179}},{"condition":"229/229","statuses":[],"id":"vespiquen","species":"Vespiquen","moves":[{"accuracy":true,"category":"Status","id":"healorder","name":"Heal Order","flags":{"snatch":1,"heal":1},"heal":[1,2],"target":"self","type":"Bug"},{"accuracy":100,"basePower":20,"category":"Special","id":"infestation","name":"Infestation","volatileStatus":"partiallytrapped","flags":{"contact":1,"protect":1,"mirror":1},"target":"normal","type":"Bug"},{"accuracy":true,"category":"Status","id":"defendorder","name":"Defend Order","flags":{"snatch":1},"target":"self","type":"Bug"},{"accuracy":100,"basePower":90,"category":"Physical","id":"attackorder","name":"Attack Order","flags":{"protect":1,"mirror":1},"target":"normal","type":"Bug"}],"level":75,"gender":"F","hp":229,"maxhp":229,"hppct":100,"types":["Bug","Flying"],"baseStats":{"hp":70,"atk":80,"def":102,"spa":80,"spd":102,"spe":40},"abilities":{"0":"Pressure","H":"Unnerve"},"baseAbility":"unnerve","stats":{"atk":164,"def":197,"spa":164,"spd":197,"spe":104},"owner":"p2","item":"leftovers","prevMoves":[],"order":2,"nickname":"Vespiquen","seenMoves":[],"boostedStats":{"atk":164,"def":197,"spa":164,"spd":197,"spe":104}},{"condition":"274/274","statuses":[],"id":"swampert","species":"Swampert","moves":[{"accuracy":100,"basePower":120,"category":"Physical","id":"superpower","name":"Superpower","flags":{"contact":1,"protect":1,"mirror":1},"self":{"boosts":{"atk":-1,"def":-1}},"target":"normal","type":"Fighting"},{"accuracy":100,"basePower":100,"category":"Physical","id":"earthquake","name":"Earthquake","flags":{"protect":1,"mirror":1,"nonsky":1},"target":"allAdjacent","type":"Ground"},{"accuracy":true,"category":"Status","id":"raindance","name":"Rain Dance","flags":{},"target":"all","type":"Water"},{"accuracy":100,"basePower":80,"category":"Physical","id":"waterfall","name":"Waterfall","flags":{"contact":1,"protect":1,"mirror":1},"target":"normal","type":"Water"}],"level":75,"gender":"F","hp":274,"maxhp":274,"hppct":100,"types":["Water","Ground"],"baseStats":{"hp":100,"atk":110,"def":90,"spa":85,"spd":90,"spe":60},"abilities":{"0":"Torrent","H":"Damp"},"baseAbility":"torrent","stats":{"atk":209,"def":179,"spa":171,"spd":179,"spe":134},"owner":"p2","item":"swampertite","prevMoves":[],"order":3,"nickname":"Swampert","seenMoves":[],"boostedStats":{"atk":209,"def":179,"spa":171,"spd":179,"spe":134}},{"condition":"266/266","statuses":[],"id":"slowking","species":"Slowking","moves":[{"accuracy":true,"category":"Status","id":"nastyplot","name":"Nasty Plot","flags":{"snatch":1},"target":"self","type":"Dark"},{"accuracy":85,"basePower":110,"category":"Special","id":"fireblast","name":"Fire Blast","flags":{"protect":1,"mirror":1},"target":"normal","type":"Fire"},{"accuracy":100,"basePower":80,"category":"Special","id":"psyshock","name":"Psyshock","flags":{"protect":1,"mirror":1},"target":"normal","type":"Psychic"},{"accuracy":100,"basePower":80,"category":"Special","id":"scald","name":"Scald","flags":{"protect":1,"mirror":1,"defrost":1},"target":"normal","type":"Water"}],"level":75,"gender":"M","hp":266,"maxhp":266,"hppct":100,"types":["Water","Psychic"],"baseStats":{"hp":95,"atk":75,"def":80,"spa":100,"spd":110,"spe":30},"abilities":{"0":"Oblivious","1":"Own Tempo","H":"Regenerator"},"baseAbility":"regenerator","stats":{"atk":117,"def":164,"spa":194,"spd":209,"spe":89},"owner":"p2","item":"leftovers","prevMoves":[],"order":4,"nickname":"Slowking","seenMoves":[],"boostedStats":{"atk":117,"def":164,"spa":194,"spd":209,"spe":89}},{"condition":"221/221","statuses":[],"id":"weezing","species":"Weezing","moves":[{"accuracy":85,"category":"Status","id":"willowisp","name":"Will-O-Wisp","flags":{"protect":1,"reflectable":1,"mirror":1},"target":"normal","type":"Fire"},{"accuracy":100,"basePower":90,"category":"Special","id":"sludgebomb","name":"Sludge Bomb","flags":{"bullet":1,"protect":1,"mirror":1},"target":"normal","type":"Poison"},{"accuracy":85,"basePower":110,"category":"Special","id":"fireblast","name":"Fire Blast","flags":{"protect":1,"mirror":1},"target":"normal","type":"Fire"},{"accuracy":true,"category":"Status","id":"protect","name":"Protect","volatileStatus":"protect","priority":4,"flags":{},"target":"self","type":"Normal"}],"level":75,"gender":"M","hp":221,"maxhp":221,"hppct":100,"types":["Poison"],"baseStats":{"hp":65,"atk":90,"def":120,"spa":85,"spd":70,"spe":60},"abilities":{"0":"Levitate"},"baseAbility":"levitate","stats":{"atk":140,"def":224,"spa":171,"spd":149,"spe":134},"owner":"p2","item":"blacksludge","prevMoves":[],"order":5,"nickname":"Weezing","seenMoves":[],"boostedStats":{"atk":140,"def":224,"spa":171,"spd":149,"spe":134}}]},"opponent":{"active":{"condition":"100/100","statuses":[],"id":"walrein","species":"Walrein","level":75,"gender":"M","hp":100,"maxhp":100,"hppct":100,"active":true,"types":["Ice","Water"],"baseStats":{"hp":110,"atk":80,"def":90,"spa":95,"spd":90,"spe":65},"abilities":{"0":"Thick Fat","1":"Ice Body","H":"Oblivious"},"position":"p1a","owner":"p1","prevMoves":[],"nickname":"Walrein","seenMoves":[]},"reserve":[{"dead":true,"condition":"0 fnt","statuses":[],"id":"shaymin","species":"Shaymin","level":75,"gender":"M","maxhp":100,"types":["Grass"],"baseStats":{"hp":100,"atk":100,"def":100,"spa":100,"spd":100,"spe":100},"abilities":{"0":"Natural Cure"},"owner":"p1","prevMoves":["psychic","seedflare"],"nickname":"Shaymin","seenMoves":["seedflare","psychic"]},{"dead":true,"condition":"0 fnt","statuses":[],"id":"keldeo","species":"Keldeo","level":75,"gender":"M","maxhp":100,"types":["Water","Fighting"],"baseStats":{"hp":91,"atk":72,"def":90,"spa":129,"spd":90,"spe":108},"abilities":{"0":"Justified"},"owner":"p1","prevMoves":[],"nickname":"Keldeo","seenMoves":[]},{"condition":"100/100","statuses":[],"id":"walrein","species":"Walrein","level":75,"gender":"M","hp":100,"maxhp":100,"hppct":100,"active":true,"types":["Ice","Water"],"baseStats":{"hp":110,"atk":80,"def":90,"spa":95,"spd":90,"spe":65},"abilities":{"0":"Thick Fat","1":"Ice Body","H":"Oblivious"},"position":"p1a","owner":"p1","prevMoves":[],"nickname":"Walrein","seenMoves":[]}]},"forceSwitch":true,"rqid":8,"turn":5,"weather":"none","prevStates":[{"turn":5,"self":{"active":{"hp":13,"hppct":6,"statuses":[]}},"opponent":{"active":{"hp":100,"hppct":100,"statuses":[]}}},{"turn":4,"self":{"active":{"hp":34,"hppct":16,"statuses":[]}},"opponent":{"active":{"hp":100,"hppct":100,"statuses":[]}}},{"turn":3,"self":{"active":{"hp":55,"hppct":26,"statuses":[]}},"opponent":{"active":{"hp":27,"hppct":27,"statuses":[]}}},{"turn":2,"self":{"active":{"hp":135,"hppct":64,"statuses":[]}},"opponent":{"active":{"hp":62,"hppct":62,"statuses":[]}}},{"turn":1,"self":{"active":{"hp":212,"hppct":100,"statuses":[]}},"opponent":{"active":{"hp":100,"hppct":100,"statuses":[]}}}]}
"""