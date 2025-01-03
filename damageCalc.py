import TypeEffectiveness
import buildPokemon
import copy
import random
import math
import Field

# Takes an 2 pokemon and calcuates the damage of the attackers moves against the defender
attacker = buildPokemon.buildPokemonBySet("Zapdos", 3,31)
defender = buildPokemon.buildPokemonBySet("Espeon", 2,31)
field = Field.Field()

# field.weather = "Sun"
# attacker.ability = "Flash Fire (activated)"

def formatMoveDamageResponse(move, damage):
    return f"{move.name} does {damage} damage"

def getDamageForMoves(attacker, defender,battle):
    moveDamages = {}

    for m in attacker.moves:
        attackerStats = copy.deepcopy(attacker.currentStats)
        defenderStats = copy.deepcopy(defender.currentStats)
        moveEffectiveness = TypeEffectiveness.getMoveEffectiveness(m.moveType, defender)
        defenderIsAbilityImmune = checkIfDefenderHasImmuneAbility(defender, m)
        if(moveEffectiveness == 0 or m.basePower == 0 or defenderIsAbilityImmune):
            moveDamages[m.name] = 0
            continue

        if m.name == "SEISMIC_TOSS" or m.name == "NIGHT_SHADE":
            moveDamages[m.name] = attacker.level
            continue

        if m.name == "EXPLOSION" or m.name == "SELF_DESTRUCT":
            defenderStats["defense"] = math.floor(int(defenderStats["defense"] / 2))

        moveAttackStat = TypeEffectiveness.attackStatByType[m.moveType]
        if moveAttackStat == "physical":
            attackStat = "attack"
            defenseStat = "defense"
        else:
            attackStat = "specialAttack"
            defenseStat = "specialDefense"
        
        if attacker.status != "Healthy":
            if attacker.ability == "Guts":
                attackerStats["attack"] = math.floor(int(attackerStats["attack"] * 1.5))
            elif attacker.status == "Burned":
                attackerStats["attack"] = int(attackerStats["attack"] / 2)

        if attacker.ability == "Huge Power" or attacker.ability == "Pure Power":
            attackerStats["attack"] = int(attackerStats["attack"] * 2)

        if defender.ability == "Thick Fat" and (m.moveType == "FIRE" or m.moveType == "ICE"):
            attackerStats["specialAttack"] = int(attackerStats["specialAttack"] / 2)
        
        if defender.ability == "Marvel Scale" and defender.status != "Healthy":
            defenderStats["defense"] = int(defenderStats["defense"] * 1.5)
        
        if (m.moveType == attacker.types["primary"].upper() or (m.moveType == attacker.types["secondary"].upper() 
            if attacker.types["secondary"] is not None else None)):
            stabModifier = 1.5
        else:
            stabModifier = 1.0

        m.basePower = checkVariableDamageMoves(m)
        itemModifier = getAttackerItemModifier(attacker, m)
        attackerStats["attack"] = int(attackerStats["attack"] * itemModifier)
        
        overgrowModifier = getAttackerAbilityModifier(attacker, m)
        m.basePower = math.floor(int(m.basePower * overgrowModifier))
        weatherModifier = getWeatherModifier(m, field)
        baseDamage = calculate_base_damage(attacker, m, attackerStats[attackStat], defenderStats[defenseStat], 
                                           {"stab": stabModifier, "effectiveness": moveEffectiveness, "weather": weatherModifier})
        damageRange = generate_damage_range(baseDamage)
        moveDamages[m.name] = damageRange
    print(moveDamages)
    return moveDamages

def getAttackerAbilityModifier(attacker, move):
    modifier = 1.0
    # blaze/torrent/overgrow/swarm
    if (attacker.hp <= int(attacker.maxHp) / 3 and 
    ((attacker.ability == "Overgrow" and move.moveType == "GRASS") or (attacker.ability == "Blaze" 
    and move.moveType == "FIRE") or (attacker.ability == "Torrent" and move.moveType == "WATER") or 
    (attacker.ability == "Swarm" and move.moveType == "BUG"))):
        modifier = 1.5
    return modifier

def checkIfDefenderHasImmuneAbility(defender, move):
    if ((defender.ability == 'Flash Fire' and move.moveType == 'FIRE') 
    or (defender.ability == 'Levitate' and move.moveType == 'GROUND') 
    or (defender.ability == 'Water Absorb' and move.moveType == 'WATER') 
    or (defender.ability == 'Volt Absorb' and move.moveType == 'ELECTRIC')):
        return True
    else:
        return False

def checkVariableDamageMoves(move):
    basePower = move.basePower
    if move.name == "FLAIL" or move.name == "REVERSAL":
        healthRatio = ((attacker.hp) / float(attacker.maxHp))*100
        if healthRatio < 4.2:
            basePower = 200
        elif healthRatio < 10.4:
            basePower = 150
        elif healthRatio < 20.8:
            basePower = 100
        elif healthRatio < 35.4:
            basePower = 80
        elif healthRatio < 68.8:
            basePower = 40
        else:
            basePower = 20
    elif move.name == "ERUPTION" or move.name == "WATER_SPOUT":
        basePower = max(1, math.floor(150 * attacker.hp / int(attacker.maxHp)))
    elif move.name == "LOW_KICK":
        basePower = 0
        # We dont have weights...
    return basePower
    
def getAttackerItemModifier(attacker, move):
    modifier = 1.0
    if attacker.item == "Choice Band":
        modifier = 1.5
    if attacker.item == "Thick Club" and attacker.species == "Cubone" or attacker.species == "Marowak":
        modifier = 2.0
    return modifier

def getWeatherModifier(move, field):
    modifier = 1.0
    if field.weather == "Rain" and move.moveType == "WATER":
        modifier = 1.5
    elif field.weather == "Sun" and move.moveType == "FIRE":
        modifier = 1.5
    elif field.weather =="Rain" and move.moveType == "FIRE":
        modifier = 0.5
    elif field.weather == "Sun" and move.moveType == "WATER":
        modifier = 0.5
    elif move.name == "SOLAR_BEAM" and (field.weather == "Hail" or field.weather == "Sand"
     or field.weather == "Rain"):
        modifier = 0.5
    return modifier
    
def calculate_base_damage(attacker, move, attack, defense, base_damage_modifiers):
    """
    Calculate damage for Pokémon Gen 3 mechanics.
    
    Parameters:
        level (int): The level of the attacking Pokémon.
        power (int): The power of the move being used.
        attack (int): The effective Attack (or Special Attack) stat of the attacker.
        defense (int): The effective Defense (or Special Defense) stat of the defender.
        base_damage_modifiers (dict): Modifiers including STAB, type effectiveness, and other effects.
        
    Returns:
        int: The damage dealt to the opponent.
    """
    # Extracting the modifiers
    stab = base_damage_modifiers.get("stab", 1.0)  # Same-Type Attack Bonus
    effectiveness = base_damage_modifiers.get("effectiveness", 1.0)  # Type effectiveness
    critical = base_damage_modifiers.get("critical", 1.0)  # Critical hit multiplier
    weatherModifier = base_damage_modifiers.get("weather", 1.0)  # Weather modifier
    other_modifiers = base_damage_modifiers.get("other", 1.0)  # Miscellaneous modifiers

    # Step 1: Base damage calculation
    base_damage = math.floor(math.floor(math.floor(2 * attacker.level / 5 + 2) * move.basePower * int(attack) / int(defense)) / 50)
    base_damage = math.floor(base_damage * weatherModifier)

    if attacker.status == "Burned":
        base_damage = math.floor(base_damage / 2)

    if attacker.ability == "Flash Fire (activated)" and move.moveType == "FIRE":
        base_damage = math.floor(base_damage * 1.5)

    base_damage =(base_damage + 2)
    # Step 2: Apply modifiers
    total_damage = math.floor(base_damage * stab) * effectiveness * critical * other_modifiers
    # Return the final integer damage value
    return int(total_damage)


def calculate_actual_damage(base_damage):
    """
    Calculates a random damage value based on the base damage 
    and the random factor range from 0.85 to 1.0.
    """
    random_factor = random.uniform(0.85, 1.0)
    actual_damage = int(base_damage * random_factor)
    return actual_damage

def generate_damage_range(base_damage):
    """
    Generates the full range of possible damage values 
    (from 0.85 to 1.0 in increments of 0.01).
    """
    damage_range = [int(base_damage * factor) for factor in [x / 100 for x in range(85, 101)]]
    print(damage_range)
    return damage_range


getDamageForMoves(attacker, defender,field)


