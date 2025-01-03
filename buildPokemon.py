# store the pokemon data in a dictionary
import json
import Move
import Pokemon
import MoveStyles


with open("pokedex.json", "r") as file:
    pokedex = json.load(file)

def findSet(species, set):
    for p in pokedex:
        if p["Species"] == species and p["Set"] == set:
            return p
    return None

def findPokemon(species):
    for p in pokedex:
        if p["Species"] == species:
            return p
    return None

def buildPokemonBySet(species, set,ivs):
    p = findSet(species, set)
    if p is not None:
        return buildPokemon(p,ivs)
    else:
        return print("Pokemon not found")

# Take a pokemon from the pokedex and look up its moves from the moves dictionary
def buildPokemon(set,ivs):
    level = 100
    # Get the moves from the set
    move1= set["Move1"]
    move2= set["Move2"]
    move3= set["Move3"]
    move4= set["Move4"]
    moves = [move1, move2, move3, move4]

    # Find the Moves from the moves dictionary and build the moves object
    builtMoves = buildMoves(moves)
    stats = parseStats(set["Stats"])
    types = parseTypes(set["Types"])
    abilities = set["Abilities"].split(" / ")
    # Create the Pokemon object
    pokemon = Pokemon.Pokemon(set["Species"], set["Set"],level,ivs, builtMoves, types, stats, abilities[0], set["Item"])
    # print(pokemon.getInfo())
    # for m in pokemon.moves:
    #     print(m.getInfo())
    return pokemon

def buildMoves(moves: list):
    with open("movesList.json", "r") as file:
        moveList = json.load(file)
    builtMoves = []

    for m in moves:
        movestyle = 0
        if m in MoveStyles.moveStylesDictionary:
            movestyle = MoveStyles.moveStylesDictionary[m] 
        m = m.upper()
        m = m.replace(" ", "_")
        for x in moveList:
            if x["name"] == m:
                builtMove = Move.Move(x["basePower"], x["name"], x["effect"], x["moveType"], x["accuracy"], 
                                      x["pp"], x["effectChance"], x["moveTargetSelected"], x["priority"], x["flags"], movestyle)
                builtMoves.append(builtMove)
    return builtMoves


def parseStats(stats):
    splitStats = stats.split("/")
    return {"hp": splitStats[0], "attack": splitStats[1], "defense": splitStats[2], "specialAttack": splitStats[3],
            "specialDefense": splitStats[4], "speed": splitStats[5]}

def parseTypes(types):
    splitTypes = types.split(" ")
    if len(splitTypes) == 2:
        return {"primary": splitTypes[0], "secondary": splitTypes[1]}
    else:
        return {"primary": splitTypes[0], "secondary": None}


