import numpy as np

class Loss:
    # Инциаилизация 
    def __init__(self, passesCoef, trackCoef, vokoCoef):
        self.passesCoef=passesCoef
        self.trackCoef=trackCoef
        self.vokoCoef =vokoCoef 
        assert(np.abs(passesCoef+ trackCoef+ vokoCoef-1)<1e-6)

    def count_loss(self, passes, track, voko):
        return self.passesCoef * np.mean(passes) - self.trackCoef * np.mean(track) - self.vokoCoef * np.mean(voko)

