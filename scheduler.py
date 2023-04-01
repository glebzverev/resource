from fuzzylogic.classes import Domain, Rule
from fuzzylogic.functions import R, S
from fuzzylogic.functions import (sigmoid, gauss, trapezoid)
import numpy as np

# Примеры функций для задач 
# Модно написать иные, но будем пока использовать эти
PassesFuzz = Domain("Passes Rate", 0, 100, res=0.1)
PassesFuzz.low = S(0,40)
PassesFuzz.mid = trapezoid(10, 40, 40, 70)
PassesFuzz.high = R(50,120)

SearchFuzz = Domain("Passes Rate", 0, 100, res=0.1)
SearchFuzz.low = S(0,40)
SearchFuzz.mid = trapezoid(10, 40, 40, 70)
SearchFuzz.high = R(50,100)

TrackFuzz = Domain("Track Rate", 0, 100, res=0.1)
TrackFuzz.low = sigmoid(1,-.5,20)
TrackFuzz.mid = gauss(40, .005)
TrackFuzz.high = sigmoid(1, .5,50)

VokoFuzz = Domain("Voko rate", 0, 100, res=0.1)
VokoFuzz.mid = S(0,20)
VokoFuzz.high = R(20,90)

R1 = Rule({(SearchFuzz.low, PassesFuzz.mid): SearchFuzz.mid})
R2 = Rule({(SearchFuzz.low, PassesFuzz.high): SearchFuzz.high})
R3 = Rule({(VokoFuzz.mid, TrackFuzz.low): TrackFuzz.mid})
R4 = Rule({(VokoFuzz.high, PassesFuzz.mid): VokoFuzz.mid})

searchRules = R1 | R2 
trackRules =  R3 
vokoRules = R4 

class Scheduler: 

    # Инициализация функций фуззификации
    def __init__(self, PassesFuzz, TrackFuzz, VokoFuzz, SearchFuzz):
        self.PassesFuzz = PassesFuzz
        self.TrackFuzz = TrackFuzz
        self.VokoFuzz = VokoFuzz
        self.SearchFuzz = SearchFuzz

    # Установка правил. Без них inference не работает 
    def setRules(self, searchRules, trackRules, vokoRules):
        self.searchRules = searchRules
        self.trackRules = trackRules
        self.vokoRules = vokoRules

    # Эта функция нужна только для графической интерпретации 
    def fuzzification(self, passesDT, SearchDT, trackDT, vokoDT):
        passesDict = self.PassesFuzz(np.mean(passesDT))
        passes = np.array([passesDict[i] for i in passesDict])
        trackDict = self.TrackFuzz(np.mean(trackDT))
        track = np.array([trackDict[i] for i in trackDict])
        vokoDict = self.VokoFuzz(np.mean(vokoDT))
        voko = np.array([vokoDict[i] for i in vokoDict])
        searchDict = self.SearchFuzz(np.mean(SearchDT))
        search = np.array([searchDict[i] for i in searchDict])
        return passes, track, voko, search

    # Функция логического вывода 
    def interference(self, passesDT, SearchDT, trackDT, vokoDT):
        pSearch = (self.searchRules({self.SearchFuzz:np.mean(passesDT), self.PassesFuzz:np.mean(trackDT)})) 
        if pSearch is None:
            pSearch = 0
        pTrack = (self.trackRules({self.VokoFuzz:np.mean(vokoDT), self.TrackFuzz:np.mean(trackDT)})) 
        if pTrack is None:
            pTrack = 0
        pVoko = (self.vokoRules({self.VokoFuzz:np.mean(vokoDT), self.PassesFuzz:np.mean(passesDT)})) 
        if pVoko is None:
            pVoko = 0
        res = np.array([pSearch, pTrack, pVoko])
        return res / np.sum(res)

scheduler = Scheduler(PassesFuzz, TrackFuzz, VokoFuzz, SearchFuzz)
scheduler.setRules(searchRules, trackRules, vokoRules)

print("FUZZIFICATION RES ")
for i in scheduler.fuzzification([20], [10], [100], [10]):
    print(i)    
print("--------------")
print(scheduler.interference([20], [10], [100], [10]))    

