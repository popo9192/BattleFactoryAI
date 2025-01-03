import Field
import PokemonAI
import buildPokemon

class AIBattle:
    def __init__(self, playerTeam,opponentPokemon,roundNumber,battleNumber, trainerType,phraseNumber):
        self.playerTeam = playerTeam # List of Pokemon objects
        self.opponentTeam = [] 
        self.activePlayerPokemon = playerTeam[0]
        self.activeOpponentPokemon = opponentPokemon
        self.field = Field.Field()
        self.roundNumber = roundNumber
        self.battleNumber = battleNumber
        self.trainerType = trainerType
        self.phraseNumber = phraseNumber
        self.opponentIVs= self.getIVsForRound()
        self.opponentMoveLog = []
        self.playerMoveLog = []
        self.ai = PokemonAI.PokemonAI(self)

    def start(self):
        print("Battle started!")
        self.opponentMoveLog.append("Thunderbolt")
        self.ai.identifyPokemon()
        self.ai.predict_opponent_move(self)
        # Once we have all the identified pokemon, figure out what move they will do.
        # Then we figure out how much damage we do against each of the sets
        # Decide what move is best
        if self.ai.identifiedPokemon != None:
            print("Opponent: ",self.ai.identifiedPokemon.getInfo())
        if len(self.ai.possibleSets) > 0:
            for set in self.ai.possibleSets:
                print( set.getInfo())
        # while self.player.is_alive() and self.enemy.is_alive():
        #     self.player.attack(self.enemy)
        #     self.enemy.attack(self.player)

    def getIVsForRound(self):
        if self.battleNumber % 21 == 0:
            return 31
        else:
            return 3

roundNumber = 1
battleNumber = 1
trainerType = None
phraseNumber = None
pokemon1 = buildPokemon.buildPokemonBySet("Espeon", 2,31)
pokemon2 = buildPokemon.buildPokemonBySet("Medicham", 3,31)
pokemon3 = buildPokemon.buildPokemonBySet("Machamp", 1,31)
playerTeam = [pokemon1,pokemon2,pokemon3]
opponentPokemon = "Latias"


AIBattle(playerTeam,opponentPokemon,roundNumber,battleNumber, trainerType,phraseNumber).start()