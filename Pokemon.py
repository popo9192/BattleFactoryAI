import copy
class Pokemon:
    def __init__(self, species, set,level,ivs, moves, types, stats, ability, item, status="Healthy"):
        self.species = species
        self.set = set
        self.level = level
        self.ivs = ivs  
        self.moves = moves  # List of move dictionaries
        self.types = types  # Pokémon's types{"primary": "FIRE", "secondary": None}
        self.baseStats = stats  # Dictionary of stats (e.g., {"speed": 100}) from the JSON
        self.adjustedStats = self.adjustStatsForIVs() # Dictionary of stats that are adjusted for IVs
        self.currentStats = copy.deepcopy(self.adjustedStats) # Dictionary of stats that can be modified during battle
        self.hp = copy.deepcopy(self.adjustedStats["hp"])  # Current HP
        self.maxHp = copy.deepcopy(self.adjustedStats["hp"])   # Max HP for healing reference
        self.statStages = {"attack": 0, "defense": 0, "specialAttack": 0, "specialDefense": 0, "speed": 0, "accuracy": 0, "evasion": 0}
        self.ability = ability  # Ability name
        self.status = status  # Current status condition (e.g., "burned", "Healhty")
        self.item = item
        self.moveLog = []  # List of moves used in battle
        self.turnsInBattle = 0  # Number of turns the Pokémon has been in battle
        self.alive = True  # Pokémon is alive by default
        
     # All pokemon in the JSON have 31 IVs, need to adjust down based on IVs of the created pokemon
    def adjustStatsForIVs(self):
        difference = 31 - self.ivs  
        adjustedStats = copy.deepcopy(self.baseStats)
        for key in adjustedStats:
            adjustedStats[key] = int(adjustedStats[key]) - difference
        return adjustedStats
    
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
    
    def SwitchOut(self):
        self.currentStats = self.adjustedStats
        self.statStages = {"attack": 0, "defense": 0, "specialAttack": 0, "specialDefense": 0, "speed": 0, "accuracy": 0, "evasion": 0}
        if self.ability == "Flash Fire (activated)":
            self.ability = "Flash Fire"
    
    def handleStatChange(self, statChangeDict):
        for stat in statChangeDict.keys():
            amount = statChangeDict[stat]
            if self.statStages[stat] >= 6:
                return "{self.species}'s {stat} can't go any higher!"
            else:
                self.statStages[stat] += amount
                if stat != "accuracy" and stat != "evasion":
                    self.updateStat(stat)
                    
    def updateStat(self, stat):
        amount = self.statStages[stat]
        if amount > 0:
            self.currentStats[stat] = int(self.adjustedStats[stat] * (2 + amount) / 2)
        else:
            self.currentStats[stat] = int(self.adjustedStats[stat] * 2 / (2 - amount))

    def UseItem(self):
        item = None
        
    
    def getInfo(self):
        return f"{self.species}{self.set} Types:({self.types["primary"], self.types["secondary"]}) HP: {self.hp}/{self.maxHp} Stats: {self.currentStats}" 
