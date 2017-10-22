"""
Created in October 2016

@author: the_roth
"""


from games.Meateo import Meateo

testGame = Meateo()
testGame.initialize_game()
testGame.guessList = [
	["g", 1606, 0],
	["h", 1607, 0],
	["i", 1608, 0],
	["j", 1609, 0],
	["k", 1610, 0],
	["l", 1611, 0]
]
print(testGame.results(addResults=False))
