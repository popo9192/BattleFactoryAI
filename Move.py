import TypeEffectiveness
class Move:
    def __init__(self, basePower, name, effect, moveType, accuracy, pp, effectChance, moveTargetSelected, priority, flags,moveStyle):
        self.basePower = basePower
        self.name = name
        self.effect = effect
        self.moveType = moveType
        self.accuracy = accuracy
        self.pp = pp
        self.effectChance = effectChance
        self.moveTargetSelected = moveTargetSelected
        self.priority = priority
        self.flags = flags
        self.moveStyle = moveStyle
        self.moveAttackType = TypeEffectiveness.attackStatByType[moveType]

    def getInfo(self):
        return f"{self.name} Power: {self.basePower} Type: {self.moveType} Style: {self.moveStyle}"
