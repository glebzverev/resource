#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import pandas as pd
import random
import json
from metrics import Loss
from scheduler import (Scheduler, SearchFuzz, PassesFuzz,TrackFuzz, VokoFuzz,
    searchRules, trackRules, vokoRules)

from components import Monitoring, Detection, Tracker, VOKO

deltaTime = 1                   # такт работы модели (секунды)
dt = 10 # Для планировщика

monitoring = Monitoring()
detection = Detection()
tracker = Tracker()
voko = VOKO()

scheduler = Scheduler(PassesFuzz, TrackFuzz, VokoFuzz, SearchFuzz)
scheduler.setRules(searchRules, trackRules, vokoRules)


resourseObservOut = []
resourseTrackerOut = []
resourseVokoOut = []
resoursePkOut = []

timeOut = []                    #
sumObjTraker = []               # количество объектов на сопровождении
sumObjDetect = []               # количество обнаруженных объектов (кол-во в такт)

dataSat = pd.read_csv("satellite_mask.csv", sep = ',')

rPk = 0.03                                                   # помеховый канал
rFault  = 0.05 


for time in range(0, 3600, deltaTime):

    #########  получение от компонентов требуемое количество ресурса
    rOobserv = monitoring.get_resourse(deltaTime)
    rTracker = tracker.get_resourse(deltaTime)
    rVoko = voko.get_resourse(deltaTime, time)
                                            # для красоты задаём потери ресурса

    # # # # # # # # # # #      Р А Б О Т А    П Л А Н И Р О В Щ И К А       # # # # # # # # # # # # # #
    # главное условие: R_observ + R_traker + R_voko = 100%


    # if  (resourseTracker > deltaTime - resourseVoko - resoursePk * deltaTime - resourseFault * deltaTime):
    #     rTrackerOut = deltaTime - resourseVoko - resoursePk * deltaTime - resourseFault * deltaTime
    # else:
    #     rTrackerOut = resourseTracker

    rObservOut = deltaTime - rTracker - rVoko - rPk * deltaTime - rFault * deltaTime
    if  (rObservOut < 0):
        rObservOut = 0
    rTrackerOut = rTracker
    rVokoOut = rVoko
    rPkOut = rPk
    rFoult = rFault

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    #########  логирование + случайности для красоты выдаваемых графиков
    resourseObservOut.append(rObservOut)
    resourseTrackerOut.append(rTrackerOut)
    resourseVokoOut.append(rVokoOut)
    resoursePkOut.append(rPk + random.uniform(-0.005, 0.005))
    timeOut.append(time/60)
    sumObjTraker.append(tracker.get_sum_sat())

    # розыгрыш обнаружения объекта исходя из того, как много потратилось ресурса на поиск
    detection.set_potok(dataSat['inSector'].iloc[time])
    detection.set_potok(dataSat['flowSat'].iloc[time])
    if detection.check_detection(rObservOut):
        tracker.add_object(time)
        sumObjDetect.append(1)
    else:
        sumObjDetect.append(0)

    tracker.remove_object(time)

    if time>dt and time < 3600-dt:
        scheduler.interference(
            sumObjDetect[time-10:time],
            resourseObservOut[time-10:time],
            resourseTrackerOut[time-10:time],
            resourseVokoOut[time-10:time]
        )
    # вернуть компонентам доступный/разрешенный ресурс
    #R_traker.let_resousce(R_observ)


with open("result_resourse.csv", mode="w", encoding='utf-8') as w_file:
    w_file_writer = csv.writer(w_file, delimiter = ",", lineterminator="\n")
    w_file_writer.writerow(["resourse_observ", "resourse_traker", "resourse_voko", "resourse_pk"])
    for j in range(len(resourseObservOut)):
        w_file_writer.writerow([resourseObservOut[j], resourseTrackerOut[j], resourseVokoOut[j], resoursePkOut[j]])


dataSat['skip'] = 0
dataSat['skip'] = dataSat['flowSat'] - sumObjTraker

f = open('config.json')
config = json.load(f)


# print(dataSat['flowSat'])
# print(dataSat['skip'])

loss = Loss(0.7, 0.2, 0.1)
print(loss.count_loss(dataSat['skip'], resourseTrackerOut, resoursePkOut))
