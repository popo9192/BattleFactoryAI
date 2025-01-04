import json
import buildPokemon
import damageCalc
import random
import TypeEffectiveness
import os

file_path = os.path.join(os.path.dirname(__file__), "pokedex.json")
with open(file_path, "r") as file:
    pokedex = json.load(file)

discouragedMoves = [
    "EXPLOSION", "SELF_DESTRUCT", "RAZOR_WIND", "SOLAR_BEAM", "BLAST_BURN", 
    "HYDRO_CANNON", "FRENZY_PLANT", "HYPER_BEAM", "DREAM_EATER", "FOCUS_PUNCH"
]

class PokemonAI:
    def __init__(self, battle):
        self.battle = battle
        self.species = battle.activeOpponentPokemon
        self.identifiedPokemon = None
        self.possibleSets = []

    def getInfo(self):
        return f"{self.species}{self.set}"
    
    def identifyPokemon(self):
        print("Identifying Pokemon")
        if(self.battle.roundNumber <= 4):
            self.identifiedPokemon= buildPokemon.buildPokemonBySet(self.species,self.battle.roundNumber,self.battle.opponentIVs)
        else:
            setNumbers = []
            possibleSets = []
            for p in pokedex:
                if p["Species"] == self.species:
                    setNumbers.append(p["Set"])
            for s in setNumbers:
                pokemon = buildPokemon.buildPokemonBySet(self.species,s,self.battle.opponentIVs)
                possibleSets.append(pokemon)
                if len(self.battle.opponentMoveLog) > 0:
                    possibleSets = self.checkMoves(possibleSets)
            self.possibleSets = possibleSets

            if len(possibleSets) == 1:
                self.identifiedPokemon = possibleSets[0]
        # take type and phrase into consideration for probabilities
        # check if we know item
        # Check item of pokeon if we know it
        # Take damage roll into consideration
        # Take into consideration the moves used by the opponent
        
        
    def checkMoves(self, possibleSets):
        setsWithRightMove = []
        for p in possibleSets:
            for m in p.moves:
                if m.name == self.battle.opponentMoveLog[-1].upper():
                    setsWithRightMove.append(p)
        return setsWithRightMove

    def calculate_move_scores(self,battle):
        attacker = self.identifiedPokemon
        target = battle.activePlayerPokemon
        scores = {}
        moveDamages = damageCalc.getDamageForMoves(attacker, target, battle.field)
        

        for move in attacker.moves:
            score = 0
            moveDamage = moveDamages[move.name]
            isDoubleEffective = self.checkDoubleEffectiveness(move, target)

            # Rule 1: Avoid invalid moves
            if self.move_would_fail(move, attacker, target):
                scores[move.name] = -100
                continue

            # Rule 2: Look for kills
            if self.move_can_kill(move, moveDamage, target):
                score += 4
                if move.priority > 0 and move.name != "FAKE_OUT":
                    score += 2
            else:
                # Rule 3: Damage-based scoring if move cannot kill
                highestDamage = self.calculate_highest_damage(moveDamages)
                if move.basePower > 1 and move.name != highestDamage:
                    score -= 1
                elif move.basePower > 1 and move.name == highestDamage:
                    score += 0
                elif (move.basePower <= 1 or move.name in discouragedMoves) and isDoubleEffective and random.random() <= 0.69:
                    score += 2
            # Rule 4: Special logic for status or situational moves
            score += self.apply_special_logic(move, attacker, target, battle)

            scores[move.name] = score
        print(scores)
        return scores
    
    def move_would_fail(self,move, attacker, target):
        # Check for immunities
        isImmune = damageCalc.checkIfDefenderHasImmuneAbility(target, move)
        if isImmune:
            return True
        # Explosion/Self-Destruct logic
        if move.name in ["EXPLOSION", "SELF_DESTRUCT"] and attacker.hp <= 0: #update to check if last opponent pokemon
            return True
        # Add other invalid move checks here
        if (move.name == "SUBSTITTE" and attacker.hp / attacker.maxHp < .3):
            return False
    
    def move_can_kill(self,move, moveDamage, target):
        rollsThatKill = 0
        if move.basePower <= 1 or (move.name in ["EXPLOSION", "SELF_DESTRUCT"]):
            return False
        for roll in moveDamage:
            if roll >= target.hp:
                rollsThatKill += 1
        if rollsThatKill / len(moveDamage) >= 0.5:
            return True
    
    def calculate_highest_damage(self, moveDamages):
        best_move = None
        max_damage = 0

        for move in moveDamages.keys():
            damage = max(moveDamages[move])
            if damage > max_damage:
                max_damage = damage
                best_move = move
        return best_move
    
    def checkDoubleEffectiveness(self, move, target):
        moveEffectiveness = TypeEffectiveness.getMoveEffectiveness(move.moveType, target)
        if moveEffectiveness == 4:
            return True

    def apply_special_logic(self,move, attacker, target, battle):
        scoreAdjustment = 0
        moveEffectiveness = TypeEffectiveness.getMoveEffectiveness(move.moveType, target)
        # Example: Always Hit moves
        if (move.name in ["AERIAL_ACE", "FAINT_ATTACK", "MAGICAL_LEAF", "SHADOW_PUNCH", "SHOCK_WAVE", "SWIFT"] 
            and attacker.statStages["accuracy"] <= -3):
            scoreAdjustment += 1
            if attacker.statStages["accuracy"] <= -5:
                scoreAdjustment += 1

        if move.name in ["SWORDS_DANCE", "MEDITATE"]:
            attackStage = attacker.statsStage["attack"]  # Get current attack stage

            # If the user is at +3 attack or higher
            if attackStage >= 3:
                if random.random() < 0.61:  # 61% chance of -1 score
                    scoreAdjustment -= 1
            else:
                # HP-based adjustments
                hpRatio = attacker.hp / attacker.maxHp  # Current HP as a percentage

                if hpRatio == 1.0:  # At 100% HP
                    if attackStage <= 2 and random.random() < 0.5:  # 50% chance of +1 score
                        scoreAdjustment += 1
                elif 0.71 <= hpRatio < 1.0:  # 71-99% HP
                    scoreAdjustment += 0  # No change
                elif 0.4 <= hpRatio < 0.71:  # 40-70% HP
                    if random.random() < 0.84:  # 84% chance of -2 score
                        scoreAdjustment -= 2
                elif hpRatio < 0.4:  # 0-39% HP
                    scoreAdjustment -= 2  # Always -2 score

        if move.name == "Charm":
            # Check if the target's attack has already been lowered
            attackStage = target.statStages["attack"]
            hpRatio = attacker.hp / attacker.maxHp  # Attacker's HP ratio

            if attackStage < 0:  # Target's attack has been lowered
                scoreAdjustment -= 1  # Base penalty
                if hpRatio < 0.9:  # Attacker is under 90% HP
                    scoreAdjustment -= 1
                if attackStage <= -3:  # Target's attack is already down to -3 or lower
                    if random.random() < 0.8:  # High chance of another -1 score
                        scoreAdjustment -= 1
            else:  # Target's attack has not been lowered
                if hpRatio <= 0.7:  # Attacker is at 70% HP or less
                    scoreAdjustment -= 2
                else:  # Attacker is above 70% HP
                    # Check if the target has a physical type, excluding Flying, Poison, and Ghost
                    physicalTypes = TypeEffectiveness.getPhysicalTypes()
                    targetHasPhysicalType = any(t in physicalTypes for t in target.types)
                    
                    if targetHasPhysicalType:
                        scoreAdjustment += 0  # No adjustment
                    else:  # Target does not have a valid physical type
                        if random.random() < 0.8:  # 80% chance of -2 score
                            scoreAdjustment -= 2
         # Belly Drum
        if move.name == "Belly Drum":
            if attacker.hp <= attacker.maxHp * 0.9:  # 90% or lower HP
                scoreAdjustment -= 2

        # Brick Break
        if move.name == "Brick Break":
            if battle.field.isReflect :  # Check for Reflect
                scoreAdjustment += 1

        # Solarbeam
        if move.name == "Solarbeam":
            if moveEffectiveness < 1:  # Resisted
                scoreAdjustment -= 2
            # elif battle.targetKnowsProtect or battle.targetKnowsDetect:
            #     scoreAdjustment -= 2
            elif attacker.hp <= attacker.maxHp * 0.38:  # 38% or less HP
                scoreAdjustment -= 1
            elif moveEffectiveness == 4:  # Super effective
                scoreAdjustment += 2  # Target is doubly weak to Solarbeam

        # Confusing Moves
        if move.name in ["Confuse Ray", "Supersonic", "Sweet Kiss", "Swagger", "Flatter"]:
            if move.name in ["Swagger", "Flatter"]:
                if random.random() < 0.5:  # 50% chance of additional +1 for Swagger/Flatter
                    scoreAdjustment += 1

            targetHpRatio = target.hp / target.maxHp
            if targetHpRatio <= 0.7:
                if random.random() < 0.5:  # 50% chance of -1 for each threshold
                    scoreAdjustment -= 1
            if targetHpRatio <= 0.5:
                if random.random() < 0.5:
                    scoreAdjustment -= 1
            if targetHpRatio <= 0.3:
                if random.random() < 0.5:
                    scoreAdjustment -= 1

        # Conversion
        if move.name == "Conversion":
            isFirstTurn = attacker.turnsInBattle == 0
            if attacker.hp > attacker.maxHp * 0.9 and isFirstTurn:
                scoreAdjustment += 0  # Conversion is neutral on first turn at high HP
            elif attacker.hp > attacker.maxHp * 0.9 and not isFirstTurn:
                if random.random() < 0.2:  # 20% chance to remain at +0
                    scoreAdjustment += 0
                else:
                    scoreAdjustment -= 2
            else:  # Below 90% HP
                scoreAdjustment -= 2  


        # Example: Fake Out gets +2 on the first turn
        if move.name == "FAKE_OUT" and attacker.turnsInBattle == 0:
            scoreAdjustment += 2

        # Example: Baton Pass logic
        if move.name == "Baton Pass" and (attacker.statStages["attack"] >= 3 or attacker.statStages["defense"] >= 3
            or attacker.statStages["special_attack"] >= 3 or attacker.statStages["special_defense"] >= 3 
            or attacker.statStages["evasion"] >= 3):
            if (attacker.hp <= attacker.maxHp * 0.6 and attacker.stats["speed"] > target.stats["speed"] 
                and random.random() < 0.69):
                scoreAdjustment += 2
            elif (attacker.hp <= attacker.maxHp * 0.7 and attacker.stats["speed"] < target.stats["speed"] 
                and random.random() < 0.69):
                scoreAdjustment += 2
            else:
                scoreAdjustment -= 2

        # Counter and Mirror Coat Logic
        if move.name in ["Counter", "Mirror Coat"]:
            if target.status in ["Infatuated", "Confused", "Asleep"]:
                scoreAdjustment -= 100  # Early exit for invalid conditions

            if attacker.hp < attacker.maxHp * 0.3 and random.random() < 0.96:
                scoreAdjustment -= 1
            if attacker.hp < attacker.maxHp * 0.5 and random.random() < 0.61:
                scoreAdjustment -= 1

            # Special logic if both moves are known
            if "Counter" in [m.name for m in attacker.moves] and "Mirror Coat" in [m.name for m in attacker.moves]:
                if random.random() < 0.61:
                    scoreAdjustment += 4

            # Logic for only one move
            last_move = battle.known_player_moves[-1] if battle.known_player_moves else None
            if last_move:
                if move.name == "Counter" and last_move.category == "Physical":
                    scoreAdjustment += 1 if random.random() < 0.61 else 0
                elif move.name == "Mirror Coat" and last_move.category == "Special":
                    scoreAdjustment += 1 if random.random() < 0.61 else 0
                else:
                    scoreAdjustment -= 1

        # Curse Logic
        if move.name == "Curse":
            if "Ghost" in attacker.types:
                scoreAdjustment -= 1 if random.random() < 0.69 else 0
            else:
                defense_stages = attacker.stats.get("defense_stage", 0)
                for threshold in [3, 1, 0]:
                    if defense_stages <= threshold and random.random() < 0.5:
                        scoreAdjustment += 1

        # Defense Boosting Moves
        if move.name in ["Bulk Up", "Harden", "Acid Armor", "Iron Defense"]:
            if attacker.hp == attacker.maxHp and attacker.stats["defense_stage"] <= 2:
                scoreAdjustment += 2 if random.random() < 0.5 else 0
            if attacker.stats["special_defense_stage"] >= 3 and random.random() < 0.61:
                scoreAdjustment -= 1
            if attacker.hp < attacker.maxHp * 0.4:
                scoreAdjustment -= 2

        # Destiny Bond Logic
        if move.name == "Destiny Bond":
            scoreAdjustment -= 1
            if attacker.stats["speed"] > target.stats["speed"]:
                if attacker.hp >= attacker.maxHp * 0.7 and random.random() < 0.5:
                    scoreAdjustment += 1
                if attacker.hp >= attacker.maxHp * 0.5 and random.random() < 0.5:
                    scoreAdjustment += 1
                if attacker.hp <= attacker.maxHp * 0.3 and random.random() < 0.61:
                    scoreAdjustment += 2

        # Disable Logic
        if move.name == "Disable":
            last_move = battle.known_player_moves[-1] if battle.known_player_moves else None
            if last_move:
                if last_move.category == "Damaging" and attacker.stats["speed"] > target.stats["speed"]:
                    scoreAdjustment += 1
                elif last_move.category == "Status" and random.random() < 0.61:
                    scoreAdjustment -= 1
        
        # Dragon Dance logic
        if move.name == "Dragon Dance":
            if attacker.stats["speed"] < target.stats["speed"]:  # Slower than target
                if random.random() < 0.5:  # 50% chance for +1 score
                    scoreAdjustment += 1
            elif attacker.hp < attacker.maxHp / 2:  # Below half HP and not slower
                if random.random() < 0.73:  # 73% chance for -1 score
                    scoreAdjustment -= 1
            
        if move.name in ["Giga Drain", "Leech Life", "Mega Drain"]:
            if move.move_type in target.types:  # If resisted
                if random.random() < 0.8:  # 80% chance of -3 score
                    scoreAdjustment -= 3

        if move.name == "Dream Eater":
            if move.move_type in target.types:  # If resisted
                scoreAdjustment -= 1
                
        if move.name == "Encore":
            if target.stats["speed"] > attacker.stats["speed"]:  # Target is faster
                scoreAdjustment -= 2
            else:  # Check the last move used by the target
                last_move = battle.known_player_moves[-1] if battle.known_player_moves else None
                if last_move and last_move.name in [
                    "Attract", "Camouflage", "Charge", "Confuse Ray", "Conversion", "Conversion 2",
                    "Detect", "Dream Eater", "Encore", "Endure", "Fake Out", "Follow Me", "Foresight",
                    "Glare", "Growth", "Harden", "Haze", "Heal Bell", "Imprison", "Ingrain", "Knock Off",
                    "Light Screen", "Mean Look", "Mud Sport", "Poisonpowder", "Protect", "Recycle",
                    "Refresh", "Rest", "Roar", "Role Play", "Safeguard", "Skill Swap", "Stun Spore",
                    "Super Fang", "Supersonic", "Swagger", "Sweet Kiss", "Teeter Dance", "Thief",
                    "Thunder Wave", "Toxic", "Water Sport", "Will-O-Wisp"
                ]:
                    if random.random() < 0.88:  # 88% chance of +3 score
                        scoreAdjustment += 3
                else:
                    scoreAdjustment -= 2

        if move.name == "Endeavor":
            if target.hp < target.maxHp * 0.7:  # Target is below 70% HP
                scoreAdjustment -= 1
            else:
                hp_threshold = 0.4 if attacker.stats["speed"] > target.stats["speed"] else 0.5
                if attacker.hp > attacker.maxHp * hp_threshold:
                    scoreAdjustment -= 1
                else:
                    scoreAdjustment += 1
        
        if move.name == "Endure":
            if attacker.hp / attacker.maxHp < 0.34 and attacker.hp / attacker.maxHp > 0.04:
                if random.random() < 0.73:  # 73% chance of +1 score
                    scoreAdjustment += 1
            else:
                scoreAdjustment -= 1
        
        if move.name == "Double Team":
            if attacker.hp / attacker.maxHp >= 0.9:  # User has 90%+ HP
                if random.random() < 0.61:  # 61% chance of +3 score
                    scoreAdjustment += 3
            if attacker.stats.get("evasion", 0) >= 3:  # Evasion is +3 or higher
                if random.random() < 0.5:
                    scoreAdjustment -= 1
            if attacker.hp < attacker.maxHp * 0.4:  # Below 40% HP
                scoreAdjustment -= 2
            if 0.41 < attacker.hp / attacker.maxHp < 0.7 and attacker.stats.get("evasion", 0) > 0:
                if random.random() < 0.73:
                    scoreAdjustment -= 2
        
        if move.name in ["Milk Drink", "Softboiled", "Moonlight", "Morning Sun", "Recover", "Slack Off", "Swallow", "Synthesis"]:
            if attacker.hp == attacker.maxHp:  # At full HP
                scoreAdjustment -= 3
            elif attacker.stats["speed"] > target.stats["speed"]:  # Faster
                scoreAdjustment -= 8
            else:  # Slower and below full HP
                if attacker.hp >= attacker.maxHp * 0.7:
                    if random.random() < 0.88:
                        scoreAdjustment -= 3
                else:
                    if random.random() < 0.92:
                        scoreAdjustment += 2
        if move.name in ["Blaze Kick", "Aeroblast", "Crabhammer", "Cross Chop", "Dragon Claw", "Drill Peck", "Drill Run", "Karate Chop", "Leaf Blade", "Razor Leaf", "Slash", "X-Scissors"]:
            if move.move_type in target.types:  # Super effective
                if random.random() < 0.5:
                    scoreAdjustment += 1
            elif move.move_type not in target.types:  # Neutral
                if random.random() < 0.25:
                    scoreAdjustment += 1

        if move.name == "Poisonpowder":
            if attacker.hp < attacker.maxHp * 0.5 or target.hp < target.maxHp * 0.5:
                scoreAdjustment -= 1
        
        if move.name in ["Protect", "Detect"]:
            if battle.protect_count >= 2:  # Discourage after two consecutive uses
                scoreAdjustment -= 2
            elif attacker.status in ["Badly Poisoned", "Infatuated"] or battle.is_perish_song_active:
                scoreAdjustment += 0  # Bug: No discouragement
            else:
                scoreAdjustment += 2
                if random.random() < 0.5:
                    scoreAdjustment -= 1
                if battle.last_used_move == "Protect" or battle.last_used_move == "Detect":
                    scoreAdjustment -= random.choice([-1, -2])

        if move.name in ["Blast Burn", "Frenzy Plant", "Hydro Cannon", "Hyper Beam"]:
            if move.move_type in target.types:  # Resisted
                scoreAdjustment -= 1
            else:
                hp_threshold = 0.6 if attacker.stats["speed"] < target.stats["speed"] else 0.41
                if attacker.hp >= attacker.maxHp * hp_threshold:
                    scoreAdjustment -= 1

        if move.name == "Recycle":
            if attacker.held_item in ["Chesto Berry", "Lum Berry", "Starf Berry"]:
                if random.random() < 0.8:
                    scoreAdjustment += 1
            else:
                scoreAdjustment -= 2
        
        if move.name == "Rest":
            if attacker.hp == attacker.maxHp:
                scoreAdjustment -= 8
            elif attacker.stats["speed"] > target.stats["speed"]:
                if attacker.hp >= attacker.maxHp * 0.5:
                    scoreAdjustment -= 3
                elif attacker.hp >= attacker.maxHp * 0.4 and random.random() < 0.73:
                    scoreAdjustment -= 3
                else:
                    if random.random() < 0.96:
                        scoreAdjustment += 3
            else:
                if attacker.hp >= attacker.maxHp * 0.71:
                    scoreAdjustment -= 3
                elif attacker.hp >= attacker.maxHp * 0.6 and random.random() < 0.8:
                    scoreAdjustment -= 3
                else:
                    if random.random() < 0.96:
                        scoreAdjustment += 3
            
            if move.name == "Revenge":
                if attacker.status not in ["Asleep", "Infatuated", "Confused"]:
                    if random.random() < 0.27:  # 27% chance of +2
                        scoreAdjustment += 2
                else:
                    scoreAdjustment -= 2
            
            if move.name in ["Light Screen", "Reflect"]:
                if attacker.hp < attacker.maxHp * 0.5:
                    scoreAdjustment -= 2
                elif move.move_type not in target.types:
                    if random.random() < 0.8:  # 80% chance of -2
                        scoreAdjustment -= 2

        if move.name in ["Explosion", "Selfdestruct"]:
            if attacker.hp >= attacker.maxHp * 0.8:
                scoreAdjustment -= random.choice([1, 3])  # 80% chance of -1 or -3
            elif attacker.hp >= attacker.maxHp * 0.51:
                if random.random() < 0.8:  # 80% chance of -1
                    scoreAdjustment -= 1
            elif attacker.hp >= attacker.maxHp * 0.3:
                if random.random() < 0.5:  # 50% chance of +1
                    scoreAdjustment += 1
            else:
                chance = random.random()
                if chance < 0.4:
                    scoreAdjustment += 2
                elif chance < 0.9:
                    scoreAdjustment += 1

        if move.name in ["Bounce", "Dig", "Dive", "Fly"]:
            if battle.target_knows_protect():
                scoreAdjustment -= 1
            elif random.random() < 0.69:  # 69% chance of +1
                if attacker.stats["speed"] > target.stats["speed"] or target.status in ["Badly Poisoned", "Leech Seeded"]:
                    scoreAdjustment += 1
        
        if move.name in ["Cosmic Power", "Stockpile", "CALM_MIND", "Amnesia"]:
            if attacker.hp == attacker.maxHp and attacker.statStages["specialAttack"] <= 2:
                if random.random() < 0.5:  # 50% chance of +2
                    scoreAdjustment += 2
            elif attacker.statStages["specialAttack"] >= 3:
                if random.random() < 0.61:  # 61% chance of -1
                    scoreAdjustment -= 1
            elif attacker.hp < attacker.maxHp * 0.4:
                scoreAdjustment -= 2











        return scoreAdjustment

    def predict_opponent_move(self, battle):
        opponent = self.identifiedPokemon
        player = battle.activePlayerPokemon

        # Calculate scores for all moves
        move_scores = self.calculate_move_scores(battle)

        # Choose the move with the highest score
        best_move = max(move_scores, key=move_scores.get)
        return best_move




