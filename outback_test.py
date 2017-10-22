"""
Created in October 2016

@author: the_roth

This was written to test the party/individual survival win rates at various
levels. Also tested are the round lengths as I need to make sure that games
aren't played too quickly or slowly.

I should probably write code to generate optimal parameters if I want to
change the win rates later on. Since they're tied in with the game lengths
it makes changing parameters by hand rather tedious.
"""


import collections

from games.Outback import Outback

testGame = Outback()
testGame.initialize_game()

gameLengths = []
noPlayersLeft = []
survivalDict = {'a': 0, 'b': 0, 'c':0, 'd':0,
				'e':0, 'f':0, 'g':0, 'h':0,
				'i':0, 'j':0, 'k':0, 'l':0
				}
Animal = 'Goob'
testGame._level = 5
# Comment out next line if you want a random no. of players between 1 and 12
testGame._testNumPlayers = 1

# Test win rate of the Outback game
j = 1
tests = 10000
count = 0
while j <= tests:

	test = testGame.results(testing = True)
	testResult, gameLength, playersLeft = test
	gameLengths.append(gameLength)
	noPlayersLeft.append(len(playersLeft))
	if testResult == True:
		count += 1

	for i in playersLeft.keys():
		survivalDict[i] += 1
	j += 1

# collect frequency of rounds taken to complete game, and their survivors
freq = collections.Counter(gameLengths)
survivors = collections.Counter(noPlayersLeft)

print("Number of tests: " + str(j - 1))
print("Number of tourist victories: " + str(count))
print("Average Number of survivors: " + str(sum(noPlayersLeft)*1.0/tests))
print("Average number of rounds / game: "
		+ str(round(sum(gameLengths)*1.0/(j-1),2)))
print("Minimum # of rounds: " + str(min(gameLengths)))
print("Maximum # of rounds: " + str(max(gameLengths)))
print("\nNo. of rounds taken over " + str(tests) + " tests:")
print(sorted(freq.items(), key=lambda pair: pair[0]))

print("\nSurvivors over " + str(tests) + " tests:")
print(sorted(survivors.items(), key=lambda pair: pair[0])) # sorts dictionary by key

print('\nSurvival Dictionary is: ')
print(survivalDict)
