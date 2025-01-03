import Field
import PokemonAI

class AIBattle:
    def __init__(self, playerTeam, opponentTeam,roundNumber,battleNumber,level, trainerType,phraseNumber):
        self.playerTeam = playerTeam # List of Pokemon objects
        self.opponentTeam = opponentTeam 
        self.activePlayerPokemon = playerTeam[0]
        self.activeOpponentPokemon = opponentTeam[0]
        self.field = Field.Field()
        self.roundNumber = roundNumber
        self.battleNumber = battleNumber
        self.level = level
        self.trainerType = trainerType
        self.phraseNumber = phraseNumber
        self.opponentIVs= self.getIVsForRound()
        self.ai = PokemonAI.PokemonAI(self)

    def start(self):
        print("Battle started!")
        self.ai.identifyPokemon()
        print(self.ai.possibleSets)
        # while self.player.is_alive() and self.enemy.is_alive():
        #     self.player.attack(self.enemy)
        #     self.enemy.attack(self.player)

    def getIVsForRound(self):
        if self.battleNumber % 21 == 0:
            return 31
        else:
            return 3
