import math
import buildPokemon
# base_damage = math.floor(math.floor(math.floor(2 * 100 / 5 + 2) * 95 * int(287) / int(196)) / 50)
# print(base_damage)

# base_damage =(base_damage + 2)
# # Step 2: Apply modifiers
# total_damage = math.floor(base_damage * 1.5) * 1.0 * 1.0 * 1.0
# print(total_damage)

attacker = buildPokemon.buildPokemonBySet("Zapdos", 3,31)
attacker.handleStatChange({"specialAttack": 1, "speed": 1})
attacker.handleStatChange({"specialAttack": 1, "evasion": 1})
attacker.handleStatChange({"specialAttack": -2, "attack": -3})

# Test Mons:

# Medicham 3 vs Hariyama 1 Pure power/thickfat 
