#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import pandas as pd
import random
import matplotlib
import matplotlib.pyplot as plt

from components import *

deltaTime = 1                   # такт работы модели (секунды)

monitoring = Monitoring()
detection = Detection()
tracker = Tracker()
voko = VOKO()

resourseObservOut = []
resourseTrackerOut = []
resourseVokoOut = []
resoursePkOut = []

timeOut = []                    #
sumObjTraker = []               # количество объектов на сопровождении
sumObjDetect = []               # количество обнаруженных объектов (кол-во в такт)

dataSat = pd.read_csv("satellite_mask.csv", sep = ',')

for time in range(0, 3600, deltaTime):

    #########  получение от компонентов требуемое количество ресурса
    rOobserv = monitoring.get_resourse(deltaTime)
    rTracker = tracker.get_resourse(deltaTime)
    rVoko = voko.get_resourse(deltaTime, time)
    rPk = 0.03                                                   # помеховый канал
    rFault = 0.05                                                # для красоты задаём потери ресурса

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

    # вернуть компонентам доступный/разрешенный ресурс
    #R_traker.let_resousce(R_observ)


with open("result_resourse.csv", mode="w", encoding='utf-8') as w_file:
    w_file_writer = csv.writer(w_file, delimiter = ",", lineterminator="\n")
    w_file_writer.writerow(["resourse_observ", "resourse_traker", "resourse_voko", "resourse_pk"])
    for j in range(len(resourseObservOut)):
        w_file_writer.writerow([resourseObservOut[j], resourseTrackerOut[j], resourseVokoOut[j], resoursePkOut[j]])


fig, ax = plt.subplots()
my_colors = []
my_colors.append('green')
my_colors.append('blue')
my_colors.append('red')
my_colors.append('gray')
ax.stackplot(timeOut,
             [resoursePkOut] + [resourseTrackerOut] + [resourseVokoOut] + [resourseObservOut],
             colors=my_colors, alpha=0.7)
plt.xlabel(r'Время')
#plt.ylabel(r'Распределение ресурса между решаемыми задачами РЛС')
plt.title('Распределение ресурса между решаемыми задачами РЛС')
plt.grid(True)
plt.show()

dataSat['skip'] = 0
dataSat['skip'] = dataSat['flowSat'] - sumObjTraker

f = open('config.json')
config = json.load(f)





fig, ax = plt.subplots()
ax.plot(timeOut, dataSat['inSector'], color = 'black')
plt.stackplot(timeOut, dataSat['flowSat'], color = 'red')
plt.stackplot(timeOut, sumObjTraker, color = 'blue', alpha = 1.0)
plt.stackplot([config['Consts for VOKO']['startTime']/60, config['Consts for VOKO']['stopTime']/60], [100, 100], color = 'red', alpha = 0.3)
plt.xlabel(r'Время')
plt.ylabel(r'Количество ИСЗ')
plt.title('Оценка количества ИСЗ в секторе, оценка количества обнаруженных и пропущенных объектов')
ax.legend(loc = 1)
plt.grid(True)
timeFmt = matplotlib.dates.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(timeFmt)
ax.legend(['количество объектов в секторе действия РЛС',
           'пропущенные объекты',
           'обнаруженных'], loc = 2)
plt.show()

