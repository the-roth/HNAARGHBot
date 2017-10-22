"""
Created on Mar 04, 2017

@author: the_roth
"""

"""
Define items that will be used in the game and whether they are fractional or
damage based attacks
Structure: 'Item Name': [
	'Attack Name',
	[Min Dmg, Max Dmg] / No of attacks / Spell,
	No. of Items / Game,
	Probability of getting item
	]
Fractional attacks have numbers between 0 and 1, and will be multiplied by the
Jelly's current HP later
"""
weaponDict = {
	#Fractional Weapons
	'Dekar Blade': ['Fatal Blow', [0.50, 0.62], 1, 0.33],
	'Myth Blade': ['Battle Fury', [0.25, 0.31], 2, 0.25],
	'Old Sword': ['Battle Cry', [0.167, 0.217], 2, 0.25],
	'Deadly Sword': ['Battle Cry', [0.167, 0.217], 1, 0.33],
	'Deadly Rod': ['Devastation', [0.115, 0.135], 3, 0.25],	# Not correct, fix for front row damage later, [.125, .155]

	#Damage Weapons
	'Gades Blade': ['Octo Strike', 8, 1, 0.33],
	'Lizard Blow': ['Dragon Rush', 3, 2, 0.25],
	'Fry Sword': ['Sizzle', 'Fry', 1, 0.33],
	'Sky Sword': ['Sky Splitter', 'Dragon', 1, 0.33],
	'Snow Sword': ['Deep Freeze', 'Ice Valk', 1, 0.33],

	#Rocks
	'Gorgon Rock': ['Axe Attack', [0.115, 0.135], 1, 0.2],
	'Cancer Rock': ['Scissor Slash', 2, 1, 0.2],
	'Hidora Rock': ['Triple Attack', 3, 1, 0.2]
	}

# These weapons should be in the order that you want to equip them in.
weaponEquipDict = {
	'Arty':['Deadly Rod', 'Lizard Blow'],
	'Selan':['Deadly Rod', 'Lizard Blow', 'Snow Sword'],
	'Tia':['Deadly Rod', 'Lizard Blow', 'Snow Sword'],
	'Lexis':['Lizard Blow'],
	'Dekar':[
		'Dekar Blade', 'Gades Blade', 'Myth Blade', 'Old Sword',
		'Lizard Blow', 'Sky Sword', 'Mega Ax', 'Fry Sword'
		],
	'Guy':[
		'Gades Blade', 'Myth Blade', 'Old Sword', 'Lizard Blow',
		'Sky Sword', 'Mega Ax', 'Fry Sword'
		],

	'Maxim':[
		'Myth Blade', 'Old Sword', 'Lizard Blow',
		'Deadly Sword', 'Sky Sword'
		]
	}

# Structure = [ATP boost, INT boost]
defaultAttackDict = {
	'Default': [325, 0],
	'Deadly Rod': [0, 0],
	'Deadly Sword': [120, 0],
	'Lizard Blow': [360, 0],
	'Dekar Blade': [188, 0],
	'Gades Blade': [200, 0],
	'Myth Blade': [450, 0],
	'Old Sword': [400, 0],
	'Mega Ax': [400, 0],
	'Fry Sword': [390, 10],	# Normally 380 ATP + 10 STR but just add here now
	'Sky Sword': [500, 0],	# Normally 450 ATP + 50 STR but just add here now
	'Snow Sword': [380, 0]
	}

# Different people can use different magic, for differing damage ranges
# A better way is to combine this dictionary with the one below it but I can't be bothered
magicDict = {
	'Fry': 300,
	'Firebird': 360,
	'Dragon': 390,
	'Ice Valk': 420,
	'Thunder': 480,
	'Zap': 600
	}

# These spells should be in the order of damage output
spellUseList = {
	'Arty': ['Zap', 'Thunder', 'Ice Valk', 'Dragon'],
	'Lexis': ['Thunder', 'Ice Valk', 'Dragon'],
	'Maxim': ['Thunder', 'Ice Valk', 'Dragon'],
	'Selan': ['Thunder', 'Ice Valk', 'Dragon'],
	'Tia': ['Thunder', 'Ice Valk', 'Dragon'],
	'Dekar': ['Dragon'],	# Dekar and Guy cannot use magic - magic slot gets removed after making the character.
	'Guy': ['Dragon']
	}

# Capsule monster special attack. A 25% chance of attacking is built in later (see Capsule function)
capsuleMonstersDict = {
	'Sully': {
		'Level 28': {'ATP': 318, 'INT': 44},
		'Level 34': {'ATP': 345, 'INT': 50},
		'Level 39': {'ATP': 367, 'INT': 55},
		'Specials': {
			'Battle Anger': ['ATP', 4.15],	# Formula is (ATP + INT) * 4 but making it *4.15 for simplicity
			'Head Butt': ['ATP', 3.5],
			'Stone Crush': ['ATP', 3],
			'defends': ['ATP', 0],
			'proudly defends': ['ATP', 0],
			'DEFENDS!': ['ATP', 0]
			},
		'Position': [4] # Denotes which position the capsule monster might attack from in the current game
		},
	'Darbi': {
		'Level 28': {'ATP': 261, 'INT': 155},
		'Level 34': {'ATP': 279, 'INT': 177},
		'Level 39': {'ATP': 294, 'INT': 196},
		'Specials': {
			'Dark Thunder': ['INT', 2.5],
			'Evil Aura': ['INT', 6],
			'Sizzle Smash': ['ATP', 3],
			'Terminate': ['INT', 4]
			},
		'Position': [1, 2]
		},
	'Blaze': {
		'Level 28': {'ATP': 236, 'INT': 116},
		'Level 34': {'ATP': 252, 'INT': 132},
		'Level 39': {'ATP': 266, 'INT': 145},
		'Specials': {
			'Flame Punch': ['ATP', 1.5],
			'Burning Fang': ['INT', 2],
			'Terminate': ['INT', 4],
			'tries to run': ['ATP', 0]
			},
		'Position': [1]
		},
	'Flash': {
		'Level 28': {'ATP': 64, 'INT': 185},
		'Level 34': {'ATP': 70, 'INT': 206},
		'Level 39': {'ATP': 75, 'INT': 224},
		'Specials': {
			'Bolt Attack': ['INT', 4],
			'defends': ['ATP', 0],
			'uselessly heals': ['ATP', 0]
			},
		'Position': [1,2]
		},
	'Gusto': {
		'Level 28': {'ATP': 185, 'INT': 114},
		'Level 34': {'ATP': 197, 'INT': 130},
		'Level 39': {'ATP': 206, 'INT': 144},
		'Specials': {
			'Iron Fist': ['ATP', 3],
			'Twister': ['ATP', 2],
			'Sonic Blast': ['INT', 7]
			},
		'Position': [0]
		},
	'Foomy': {
		'Level 28': {'ATP': 200, 'INT': 59},
		'Level 34': {'ATP': 215, 'INT': 67},
		'Level 39': {'ATP': 228, 'INT': 73},
		'Specials': {
			'Mega Punch': ['ATP', 4],
			'Tackle': ['ATP', 2],
			'Head Butt': ['ATP', 3],
			},
		'Position': [2]
		},
	'Zeppy': {
		'Level 28': {'ATP': 211, 'INT': 112},
		'Level 34': {'ATP': 226, 'INT': 129},
		'Level 39': {'ATP': 239, 'INT': 143},
		'Specials': {
			'Power Fist': ['ATP', 3],
			'Thunderblast': ['INT', 4]
			},
		'Position': [3]
		}
	}
"""
Old dictionary if I need it for the probabilities
{
	'Sully': [['defends', 40, [0,0]], ['Battle Anger', 50, [800, 1000]], ['Head Butt', 75, [500, 700]], ['Stone Crush', 100, [500, 700]]],
	'Darbi': [['Evil Aura', 10, [800, 1100]], ['Sizzle Smash', 60, [350, 500]], ['Terminate', 100, [400, 550]]],	# Attack 140 - 160 Crrool lvl 35
	'Blaze': [['tries to run', 10, [0,0]], ['Flame Punch', 40, [400, 550]], ['Burning Fang', 70, [350, 600]], ['Terminate', 100,[500, 650]]],
	'Flash': [['uselessly heals', 70, [0,0]], ['Thunderbolt', 100, [600, 700]]],
	'Gusto': [['Iron Fist', 35, [400, 550]], ['Twister', 70, [350, 600]], ['Sonic Blast', 100, [500, 650]]],
	'Foomy': [['Foomy Punch', 35, [400, 550]], ['Tackle', 70, [350, 600]], ['Head Butt', 100, [500, 650]]]
}
"""

# Might as well put these here as well for the time being
jellySayings = {
	'Normal Saying': [
		'Now then - I\'ll show you my gelatin gestures! Let\'s regain our strength.',
		'Right, let\'s go!',
		'Are we ready?'
		],
	'Hit': [
		'dealing',
		'hitting for',
		'which hits for',
		'whacking the jelly for',
		'which deals',
		'which does',
		'hitting the jelly for',
		'which hits the jelly for',
		'doing'
		],
	'Death': [
		'GRRRR... ZRRRRR.... GRAAAAM!',
		'Ohhh... My Body!',
		'You little hoochies!',
		'Son of a submariner! You\'ll pay for this!',
		'I hate hate hate hate hate hate... hate hate hate hate hate hate hate hate hate hate HATE YOU!',
		'Je...Jelly\'s in a pickle!',
		'You...snot nose!',
		'The mustachioed one is strong...',
		'Fungah! Foiled again!',
		'You spoony bard!'
		],
	'Trophy': [
		'half a chicken sandwich! Guess you can all share it...',
		'half a jelly sandwich! Looks mighty tasty!',
		'half a ham sandwich! Mmmmmmmm, yum!',
		'half a turkey sandwich! Nom nom nom nom...',
		'A whole sandwich! There\'s enough for everybody!',
		'Providence! Your capsule monster then eats it, leaving you stuck on floor 99 forever.',
		'a tenpin bowling trophy for you to admire before you sleep at night. Look at its stance!',
		'a commemorative shot glass! Will you ever use it?',
		'a gold star trophy. You should all be proud of yourselves.',
		'an engraved silver spoon. If only there was some raspberry jelly around oh wait...',
		'the perpetual Ancient Cave trophy. It is soft to the touch, and has your name already engraved on it.',
		'a blue ribbon. First prize!',
		'a wobbly key. You are not convinced that it will unlock anything at all.'
		],
	'Escape': [
		'refusing to be turned into your trophy.',
		'free to live another day.',
		'and goes back to floor 98 to practice against gold dragons.',
		'seeks out 8 ninja packs and beats them without healing once.',
		'and heads to floor 45 to practice dodging ninjas.',
		'laughing at your feeble attempt to defeat it.',
		'wobbling away as fast as it can.'
		],
	'Taunt':[
		'Hasta la bye bye!',
		'Don\'t tease the erm, jelly, kids!',
		'I\'m out of here!',
		'lol',
		'I\'m the best!',
		'lols',
		'I\'m out of here!',
		'Adios!'
		],
	'Taunt2500':[
		'Nice attacks. Does your husband fight too?',
		'Not even close!',
		'You hit with your hand bag!',
		'Hahahahahahahaha!',
		'You guys really suck today! Seeya!',
		'Ten years, and not a single win!'
		],
	'Taunt400':[
		'That was close... Phew!',
		'Yeesh... close but no cigar!',
		'Almost.. Next time, suckers!',
		'You guys almost got me...',
		'One more attack could have done me in!'
		]
	}
