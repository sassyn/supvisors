#!/usr/bin/python
#-*- coding: utf-8 -*-

# ======================================================================
# Copyright 2016 Julien LE CLEACH
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ======================================================================

from supervisors.utils import *

# Applicable strategies that can be applied during a deployment
class DeploymentStrategies:
    DEFAULT, LESS_LOADED, MOST_LOADED = range(3)

def deploymentStrategyToString(value):
    return enumToString(DeploymentStrategies.__dict__, value)

def stringToDeploymentStrategy(strEnum):
    return stringToEnum(DeploymentStrategies.__dict__, strEnum)

def deploymentStrategiesValues():
    return enumValues(DeploymentStrategies.__dict__)

def deploymentStrategiesStrings():
    return enumStrings(DeploymentStrategies.__dict__)


# Applicable strategies that can be applied during a conciliation
class ConciliationStrategies:
    EUTHANASIA, YOUTHANASIA, APPLICATIVE, REDEPLOYMENT = range(4)

def conciliationStrategyToString(value):
    return enumToString(ConciliationStrategies.__dict__, value)

def stringToConciliationStrategy(strEnum):
    return stringToEnum(ConciliationStrategies.__dict__, strEnum)

def conciliationStrategiesValues():
    return enumValues(ConciliationStrategies.__dict__)

def conciliationStrategiesStrings():
    return enumStrings(ConciliationStrategies.__dict__)


# Internal state of Supervisors
class SupervisorsStates:
    INITIALIZATION, ELECTION, DEPLOYMENT, OPERATION, CONCILIATION = range(5)

def supervisorsStateToString(value):
    return enumToString(SupervisorsStates.__dict__, value)

def stringToSupervisorsState(strEnum):
    return stringToEnum(SupervisorsStates.__dict__, strEnum)

def supervisorsStatesValues():
    return enumValues(SupervisorsStates.__dict__)
    
def supervisorsStatesStrings():
    return enumStrings(SupervisorsStates.__dict__)


# Exceptions
class InvalidTransition(Exception):
    def __init__(self, value): self._value = value
    def __str__(self): return repr(self._value)
    