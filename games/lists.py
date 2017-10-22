"""
Created in July 2016

@author: the_roth
"""


import random

#_______________________________________________________________________________
# List of Arnie quotes for HNAARGHbot. Accessed by typing a variation of HNAARGH.
HNAARGHList = [
	"HNAARGH",
	"HNAARGH",
	"HNAARGH",
	"HNAARGH",
	"HNAARGH",
	"HNAARGH",
	"HNAARGH HNAARGH !!",
	"HNAARGH HNAARGH !!",
	"HNAARGH HNAARGH !!",
	"HNAARGH HNAARGH !!",
	"HNAARGH HNAARGH !!",
	"HNAARGH HNAARGH !!",

	#Batman and Robin
	"What killed the dinosaurs? The Ice Age!",
	"Allow me to break the ice",
	"Tonight's forecast... a freeze is coming!",

	#Conan the Barbarian
	"Conan, what is best in life? To crush your enemies, see them driven before you, and to hear the lamentation of their women!",
	"Grant me revenge! And if you do not listen, then to HELL with you!",
	"Crom laughs at your four winds. He laughs from his mountain.",

	#Commando
	"Let off some steam, Bennett",
	"I eat Green Berets for breakfast. And right now, I'm very hungry!",
	"Remember, Sully, when I promised to kill you last? I lied!",

	#Jingle all the Way
	"Put that cookie down. NOW!",

	#Kindergarten Cop
	"It's not a tumor!",
	"I'm a cop, you idiot!",
	"I'm detective John Kimble!",
	"Stop whining! You kids are soft. You lack discipline.",
	"Who is your daddy, and what does he do?",
	"Dillon! You son of a bitch!",

	#Last Action Hero
	"I'm the famous comedian Arnold Braunschweiger!",
	"You've seen these movies where they say \"Make my day\" or \"I'm your worst nightmare\"? Well, listen to this one: Rubber baby buggie bumpers!",
	"Who the hell are you?",

	#Predator
	"Run! Go! Get to the chopper!",
	"Do it... DO IT! COME ON, Kill me, I'm here!",
	"If it bleeds, we can kill it.",

	#Terminator
	"I'll be back.",
	"Hasta la vista, baby!",
	"Come with me if you want to live.",
	"My CPU is a neural-net processor; a learning computer. The more contact I have with humans, the more I learn.",

	#The Expendables 3
	"Good morning! Let's get to the chopper!",

	#The Running Man
	"I hope you leave enough room for my fist, because I'm going to ram it into your stomach and break your goddamn spine!",
	"Killian! Here is Sub Zero, now.... Plain Zero!",
	"Hey, Lighthead! Hey, Christmas Tree!",

	#Total Recall
	"See you at the party Richter!",
	"Now this is the plan. Get your ass to Mars!",

	#True Lies
	"Have you ever killed anyone? Yeah, but they were all bad.",
	"You're fired!"
	]

#_______________________________________________________________________________
# Outback and Meateo Guessing Game things

# Both Meateo and Outback games use the description list
description = [
	"a massive", "a really ugly", "a tiny but angry", "a huge", "a gigantic",
	"a scary looking", "a vicious", "the biggest ever", "a big bulky"
	]

meateoDict = {
	"warriors_description": [
		"valiant", "fearless", "brave",	"silly", "merry", "silly", "happy",
		"noble", "courageous", "honourable"
		],

	"group": [
		"group", "band", "team", "pack", 'company'
		],

	"warriors": [
		"warriors", "knights", "NPCs", "wizards and witches",
		"white and black mages", "goobs", "twitch viewers", "soldiers",
		"summoners", "healers", "monks", "paladins", "dark knights",
		"chemists", "hunters", "pixels"
		],

	"background": [
		"an open field", "the Octomamm cave", "Kaipo", "Mysidia",
		"the Lunar Subterrane", "the 64 door glitch", "Twitch chat",
		"the outback", "the desert", "Baron", "a dark  and gloomy cave",
		"Australia", "the raging sea", "Eblan", "Fabul", "Tororia",
		"Tororia Castle", "Mt. Ordeals", "the Baron sewers",
		"a chocobo forest", "Silvera", "Agart",	"Mythril",
		"the black chocobo forest"
		],

	"enemy": [
		"Zeromus", "zombie Tellah", "Octomamm's wife", "Mombomb", "Valvalis",
		"Rubicante", "MilonZ", "Kainazzo", "Rydia's Mom", "Ifrit",
		"Shiva", "Milon", "Lugae", "a lone imp", "the Mist Dragon",	"Antlion",
		"Bahamut", "Leviatan", "Kefka"
		] + [random.choice(description) + " kangaroo"] * 4
		+ [random.choice(description) + " emu"] * 4
		+ [random.choice(description) + " drop bear"] * 4
		+ ["bichDoll"] * 4,

	"friend": [
		"the Magus Sisters", "Golbez", "FuSoYa", "Mrs. Cid", "KittyT",
		"Buffalax", "an innkeeper", "the NPCs from Kaipo", "Cecil", "Rydia",
		"Edward", "Rosa", "Yang", "Edge", "Kain", "Fcoughlin", "Neerrm",
		"Sephiroth"
		],
	}

outbackDict = {
	"activity": [
		"walking around", "lost out in", "sunbathing in", "rubbernecking in",
		"strolling about in", "wandering around"
		],

	"animal": [
		"western grey kangaroo", "red kangaroo", "emu", "drop bear", "dingo",
		"redback spider", "sting ray", "drop bear", "black-footed rock wallaby",
		"endangered bilby", "numbat", "thorny devil", "salt-water crocodile",
		"echidna", "galah", "koala", "pelican", "tasmanian devil",
		"western swamp tortoise", "great white shark", "platypus",
		"common brown snake", "brown snake", "inland taipan","mainland tiger snake"
		],

	"tourists_regroup": [
		"regroup and ", "band together and then ",
		"hesitate for a second, but rally together and "
		] + [""]*8,

	"tourist_regroup": [
		"regroups and ", "recovers, and then ",
		"hesitates for a second, but holds it together and "
		] + [""]*8,

	"tourists_attack": [
		"attack", "attack back", "launch a counter attack",
		"reply, swatting at the beast",	"reply, whacking the beast",
		"respond with a blow", "retaliate with a counter attack"
		],

	"tourist_attack": [
		"attacks", "attacks back", "launches a counter attack",
		"replies, swatting at the beast", "replies, whacking the beast",
		"responds with a blow", "retaliates with a counter attack"
		],

	"enemy_growl": [
		"growls deeply, and then ", "sees a tasty tourist, and ",
		"spots a tasty tourist, and ", "is battered but hungry, and so ",
		"thinks to itself \"Oooo, fresh meat!\" and "
		] + [""]*10,

	"enemy_counter":[
		"responds", "retaliates", "attacks back", "attacks",
		"retaliates with an attack of its own", "jumps on everyone",
		"goes for the legs", "snaps at a meaty arm", "bites at some toes",
		"snaps at a leg"
		]
	}

outbackLevels = [
	250, 200, 160, 130, 100, 75,
	50, 35, 25, 18, 12, 7, 3, 1
	]

outbackLevelDesc = [
	"Crocodile Dundee", "Bush Tucker", "Steve Irwin", "King's Feast",
	"Master Survivor", "3 Course Meal",	"Expert Camper", "Gourmet Food",
	"Crazy Rubbernecker", "Lean Cuisine", "Drunken Backpacker",
	"Tasty Appetizer", "Stingy Tourist", "Fresh Meat"
	]
