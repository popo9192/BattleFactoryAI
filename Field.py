class Field:
    def __init__(self):
        self.weather = None
        self.weatherTurnsLeft = 0
        self.isReflect = False
        self.reflectTurnsLeft = 0
        self.isLightScreen = False
        self.lightScreenTurnsLeft = 0
        self.isHelpingHand = False
        self.spikesCount = 0
        self.stealthRock = False

    def __str__(self):
        return f"Weather: {self.weather} Reflect: {self.isReflect} Light Screen: {self.isLightScreen} Helping Hand: {self.isHelpingHand}"
    
    def setWeather(self, weather):
        self.weather = weather
        self.weatherTurnsLeft = 5
    
    def setReflect(self):
        self.isReflect = True
        self.reflectTurnsLeft = 5
    
    def setLightScreen(self):
        self.isLightScreen = True
        self.lightScreenTurnsLeft = 5

    def setHelpingHand(self):
        self.isHelpingHand = True

    def clearWeather(self):
        self.weather = None
        self.weatherTurnsLeft = 0
    
    def clearReflect(self):
        self.isReflect = False
        self.reflectTurnsLeft = 0
    
    def clearLightScreen(self):
        self.isLightScreen = False
        self.lightScreenTurnsLeft = 0
    
    def clearHelpingHand(self):
        self.isHelpingHand = False
    
    def decrementTurns(self):
        if self.weatherTurnsLeft > 0:
            if self.weatherTurnsLeft == 1:
                self.clearWeather()
            else:
                self.weatherTurnsLeft -= 1
        if self.reflectTurnsLeft > 0:
            if self.reflectTurnsLeft == 1:
                self.clearReflect()
            else:
                self.reflectTurnsLeft -= 1
        if self.lightScreenTurnsLeft > 0:
            if self.lightScreenTurnsLeft == 1:
                self.clearLightScreen()
            else:
                self.lightScreenTurnsLeft -= 1
    
    def setSpikes(self):
        self.spikesCount += 1
    
    def setStealthRock(self):
        self.stealthRock = True

    def clearSpikes(self):
        self.spikesCount = 0
    
    def clearStealthRock(self):
        self.stealthRock = False
