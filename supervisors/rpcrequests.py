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

from supervisors.addressmapper import addressMapper
from supervisors.infosource import infoSource
from supervisors.xmlrpcclient import XmlRpcClient


# utilities to determine if using XmlRpcClient or internal handler directly
def _useProxy(address):
    return address != addressMapper.local_address

def _getXmlRpcClient(address):
    return XmlRpcClient(address)

def _getSupervisorProxy(address):
    # return client so as is it not destroyed when exiting
    client = _getXmlRpcClient(address)
    return client, client.proxy.supervisor

def _getSupervisorsProxy(address):
    # return client so as is it not destroyed when exiting
    client = _getXmlRpcClient(address)
    return client, client.proxy.supervisors

def _getInternalSupervisor():
    return None, infoSource.getSupervisorRpcInterface()

def _getInternalSupervisors():
    return None, infoSource.getSupervisorsRpcInterface()

def _getSupervisor(address):
    return _getSupervisorProxy(address) if _useProxy(address) else _getInternalSupervisor()

def _getSupervisors(address):
    return _getSupervisorsProxy(address) if _useProxy(address) else _getInternalSupervisors()


# Requests
def getAllProcessInfo(address):
    client, supervisor = _getSupervisor(address)
    return supervisor.getAllProcessInfo()

def getSupervisorsState(address):
    client, supervisors = _getSupervisors(address)
    return supervisors.getSupervisorsState()

def internalStartProcess(address, program, wait):
    client, supervisors = _getSupervisors(address)
    return supervisors.internalStartProcess(program, wait)

def getRemoteInfo(address, remoteAddress):
    client, supervisors = _getSupervisors(address)
    return supervisors.getRemoteInfo(remoteAddress)

def startProcess(address, program, wait):
    client, supervisor = _getSupervisor(address)
    return supervisor.startProcess(program, wait)

def stopProcess(address, program, wait):
    client, supervisor = _getSupervisor(address)
    return supervisor.stopProcess(program, wait)

def restart(address):
    client, supervisor = _getSupervisor(address)
    return supervisor.restart()

def shutdown(address):
    client, supervisor = _getSupervisor(address)
    return supervisor.shutdown()
