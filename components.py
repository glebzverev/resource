#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random

from math import e
from math import factorial


class Monitoring:
    """ Модель компонента/задачи "поиск космических объектов в барьерных зонах".
        Имитируем поиск объектов только в одном барьере.
    """

    def __init__(self):
        """
        """
        with open('config.json') as f:
            config = json.load(f)
            self.tau = config['Consts for observ']['tau']               # длительность используемых заявок
            self.delta_t = config['Consts for observ']['delta_t']       # заданное время осмотра барьерной зоны
            self.n_dir = config['Consts for observ']['n_dir']           # количество направлений (количество заявок, необходимое реализовать за период осмотра)

    def get_resourse(self, dT):
        """ Возвращает количество требуемого ресурса
        """
        return (self.tau * self.n_dir / self.delta_t )


class Detection:
    """ Модель обнаружеия. Вероятность обнаружения зависит от текущего потока ИСЗ
        через сектор и от кол-ва ресурса, потраченного на поиск.
    """

    def __init__(self):
        """
        """
        with open('config.json') as f:
            config = json.load(f)
            self.potok = config['Consts for detection']['potok']

    def set_potok(self, potok):
        """ Установить текущий поток
        """
        self.potok = potok

    def check_detection(self, resourseMonitoring):
        """ Розыгрыш вероятности обнаружения за . ИСЗ в секунду. По значению потока КО в час.
        """
        # поток -- [объектов в час]
        #

        k = 1
        P = 75 * resourseMonitoring * ((self.potok/60/60)**k) / factorial(k) * e**(-self.potok/60/60)

        if  (P > random.random()):
            return True
        else:
            return False


class Tracker:
    """ Модель компонента "сопровождение".
    """
    def __init__(self):
        with open('config.json') as f:
            self.config = json.load(f)

        self.delta_t = self.config['Consts for Tracker']['delta t']
        self.p_sopr = self.config['Consts for Tracker']['p_sopr']
        self.tau1 = self.config['Consts for Tracker']['tau1']
        self.tau2 = self.config['Consts for Tracker']['tau2']

        self.lastNumberObject = 0

        self.trackingObjects = []


    def get_resourse(self, dT):
        """ Возвращает требуемый ресурс.
        """
        sum_resourse = 0
        for obj in self.trackingObjects:
            sum_resourse += obj.resourse(dT)
        return sum_resourse


    def let_resourse(self):
        """ Сообщить компоненту сколько ему выделили ресурса.
        Если выделенного ресурса недостаточно, сбросить объекты.
        При сбросе объекта, по условию (длительность сопровождения)
        принимаем цель как отработанную, либо считаем как пропуск.
        """
        pass


    def add_object(self, time):
        """ Добавить новый объект
        """
        self.lastNumberObject += 1
        trObject = TrackingObject(time,
                                self.lastNumberObject,
                                self.p_sopr,
                                random.uniform(self.tau1, self.tau2),
                                self.delta_t)
        self.trackingObjects.append(trObject)


    def remove_object(self, time):
        """ Проверка не пора ли удалить объект
        """
        for index, obj in enumerate(self.trackingObjects):
            if obj.is_expired(time):
                self.trackingObjects.pop(index)
                return



    def get_sum_sat(self):
        """ Возвращает количество объектов на сопровождении в данный момент
        """
        return (len(self.trackingObjects))


class TrackingObject:
    """ Сопровождаемый объект. Для каждого объекта определены:
        start_time -- начало сопровождения объекта
        number -- порядковый номер объекта
        p_sopr -- период сопровождения
        tau -- длительность заявки, используемоф для этого объекта
        delta_t -- период сопровождения
    """

    def __init__(self, time, number, p_sopr, tau, delta_t):
        self.startTime = time
        self.number = number
        self.p_sopr = p_sopr
        self.tau = tau
        self.delta_t = delta_t


    def resourse(self, dT):
        """ Ресурс требуемый для данного объекта (в долях от всего ресурса)
        """
        return (self.tau / self.delta_t)


    def is_expired(self, currentTime):
        """ Проверяет, не пора ли сбросить объект?
        """
        return  (self.startTime + self.p_sopr < currentTime)


class VOKO:
    """ Модель работы компонента работы по ВОКО. Для ВОКО определены:
        startTime -- начало работы по ВОКО
        stopTime -- конец работы по ВОКО
        delta_t -- период выставления заявки по ВОКО
        tau -- длительность заявки
    """

    def __init__(self):
        with open('config.json') as f:
            config = json.load(f)
            self.startTime = config['Consts for VOKO']['startTime']
            self.stopTime = config['Consts for VOKO']['stopTime']
            self.delta_t = config['Consts for VOKO']['delta_t']
            self.tau = config['Consts for VOKO']['tau']


    def get_resourse(self, dT, currentTime):
        """ Возвращает долю требуемого ресурса.
        """
        if (self.startTime < currentTime and currentTime < self.stopTime):
            return  (self.tau / self.delta_t)
        else:
            return 0
