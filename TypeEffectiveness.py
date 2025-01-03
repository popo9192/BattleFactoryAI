import Pokemon
import copy

typeResistances = {
    "NORMAL": {"FIGHTING": 2.0, "GHOST": 0.0},
    "FIRE": {"WATER": 2.0, "GRASS": 0.5, "ICE": 0.5, "BUG": 0.5, "ROCK": 2.0, "FIRE": 0.5},
    "WATER": {"ELECTRIC": 2.0, "GRASS": 2.0, "FIRE": 0.5, "WATER": 0.5, "ICE": 0.5},
    "ELECTRIC": {"GROUND": 2.0, "ELECTRIC": 0.5, "FLYING": 0.5, "STEEL": 0.5},
    "GRASS": {"FIRE": 2.0, "WATER": 0.5, "GRASS": 0.5, "ELECTRIC": 0.5, "ICE": 2.0, "POISON": 2.0, "FLYING": 2.0, "BUG": 2.0},
    "ICE": {"FIRE": 2.0, "ICE": 0.5, "FIGHTING": 2.0, "ROCK": 2.0, "STEEL": 2.0},
    "FIGHTING": {"FLYING": 2.0, "PSYCHIC": 2.0, "BUG": 0.5, "ROCK": 0.5, "DARK": 0.5},
    "POISON": {"GROUND": 2.0, "PSYCHIC": 2.0, "GRASS": 0.5, "FIGHTING": 0.5, "POISON": 0.5, "BUG": 0.5},
    "GROUND": {"WATER": 2.0, "GRASS": 2.0, "ICE": 2.0, "ELECTRIC": 0.0, "POISON": 0.5, "ROCK": 0.5},
    "FLYING": {"ELECTRIC": 2.0, "ICE": 2.0, "ROCK": 2.0, "GROUND": 0.0, "GRASS": 0.5, "FIGHTING": 0.5, "BUG": 0.5},
    "PSYCHIC": {"BUG": 2.0, "GHOST": 2.0, "DARK": 2.0, "FIGHTING": 0.5, "PSYCHIC": 0.5},
    "BUG": {"FIRE": 2.0, "FLYING": 2.0, "ROCK": 2.0, "GRASS": 0.5, "FIGHTING": 0.5, "GROUND": 0.5},
    "ROCK": {"WATER": 2.0, "GRASS": 2.0, "FIGHTING": 2.0, "GROUND": 2.0, "STEEL": 2.0, "NORMAL": 0.5, "FIRE": 0.5, "POISON": 0.5, "FLYING": 0.5},
    "GHOST": {"GHOST": 2.0, "DARK": 2.0, "NORMAL": 0.0, "FIGHTING": 0.0, "POISON": 0.5, "BUG": 0.5},
    "DRAGON": {"ICE": 2.0, "DRAGON": 2.0, "FIRE": 0.5, "WATER": 0.5, "ELECTRIC": 0.5, "GRASS": 0.5},
    "DARK": {"FIGHTING": 2.0, "BUG": 2.0, "DARK": 0.5, "GHOST": 0.5, "PSYCHIC": 0.0},
    "STEEL": {
        "FIRE": 2.0, "FIGHTING": 2.0, "GROUND": 2.0, "NORMAL": 0.5, "GRASS": 0.5,
        "ICE": 0.5, "FLYING": 0.5, "PSYCHIC": 0.5, "BUG": 0.5, "ROCK": 0.5, "DRAGON": 0.5,
        "STEEL": 0.5, "POISON": 0.0
    }
}

attackStatByType = {
    "NORMAL": "physical",
    "FIRE": "special",
    "WATER": "special",
    "ELECTRIC": "special",
    "GRASS": "special",
    "ICE": "special",
    "FIGHTING": "physical",
    "POISON": "physical",
    "GROUND": "physical",
    "FLYING": "physical",
    "PSYCHIC": "special",
    "BUG": "physical",
    "ROCK": "physical",
    "GHOST": "physical",
    "DRAGON": "special",
    "DARK": "special",
    "STEEL": "physical"
}


def getPokemonsResistances(type1: str, type2: str | None=None):
    resistances = copy.deepcopy(typeResistances[type1])
    if type2 is None:
        return resistances
    else:
        type2Resistances = copy.deepcopy(typeResistances[type2])
        for key in type2Resistances.keys():
            if key in resistances.keys():
                resistances[key] *= type2Resistances[key]
            else:
                resistances[key] = type2Resistances[key]
            if resistances[key] == 1.0:
                resistances.pop(key)
        return resistances

def getMoveEffectiveness(moveType, target : Pokemon):
    targetResistances = getPokemonsResistances(target.types["primary"].upper(), target.types["secondary"].upper() if target.types["secondary"] is not None else None)
    if moveType in targetResistances:
        return targetResistances[moveType]
    else:
        return 1.0

def getAttackStat(moveType):
    return attackStatByType[moveType]

def getPhysicalTypes():
    return [key for key, value in attackStatByType.items() if value == "physical"]

x = getPhysicalTypes()
print(x)