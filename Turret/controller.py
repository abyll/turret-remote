#! /usr/bin/env python
## Networked Turret Controller
# acts as a remote controlling client

#Copyright 2017 - Abyll Breil

from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.application.service import Application
#from twisted.application.internet import ClientService, backoffPolicy

from twisted.protocols.amp import Integer, Float, String, Boolean, Command
from twisted.protocols import amp


class TiltCommand(Command):
    arguments = [(b'speed', Float())]
    requiresAnswer = False

class PanCommand(Command):
    arguments = [(b'speed', Float())]
    requiresAnswer = False

class StopTiltCommand(Command):
    requiresAnswer = False

class StopPanCommand(Command):
    requiresAnswer = False

class FireCommand(Command):
    requiresAnswer = False

class KeepalivePing(Command):
    pass

class TurretControlProtocol(amp.AMP):
    @TiltCommand.responder
    def tilt(self, speed):
        self.factory.Tilt(speed)
        return {b"result": True}
    
    @PanCommand.responder
    def pan(self, speed):
        self.factory.Pan(speed)
        return {b"result": True}
    
    @StopTiltCommand.responder
    def stop_tilt(self):
        self.factory.StopTilt()
        return {}
    @StopPanCommand.responder
    def stop_pan(self):
        self.factory.StopPan()
        return {}
    
    @FireCommand.responder
    def fire(self):
        self.factory.Fire()
        return {}

    @KeepalivePing.responder
    def keepalive(self):
        print("alive")
        return {}
    
    def disconnect(self):
        return self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.connectionLost(reason)
        return super(TurretControlProtocol, self).connectionLost(reason)
    
    def connectionMade(self):
        self.factory.connectionMade()
        return super(TurretControlProtocol, self).connectionMade()

def connect(factory):
    endpoint = TCP4ClientEndpoint(reactor, '192.168.43.160', 8750)
    #service = ClientService(endpoint, factory, retryPolicy=backoffPolicy(0.5, 15.0))
    #service.startService()
    #d = service.whenConnected()
    d = endpoint.connect(factory)
    return d