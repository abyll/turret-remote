#! /usr/bin/env python
## Networked Turret Controller

#Copyright 2017 - Abyll Breil
from sys import stdout
from twisted.python.log import startLogging, err
from twisted.internet import reactor, task
from twisted.internet.protocol import Factory, ClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
#from twisted.application.internet import ClientService, backoffPolicy

from twisted.protocols.amp import Integer, Float, String, Boolean, Command
from twisted.protocols import amp

import pygame

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

class GameControl(object):
    def __init__(self):
        pygame.init()
        self.p = None
        self.screen = pygame.display.set_mode((100,100)) #screen required to grab inputs
        pygame.key.set_repeat() # disable repeat
        self.eventloop = task.LoopingCall(f=self.tick)
        self.eventloop.start(1.0/20) # 20 fps should be enough resolution, especially being sent over wireless
    
    def tick(self):
        if self.p: # do nothing until we're connected
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    reactor.stop() 
                # process keys
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        reactor.stop()
                    elif event.key == pygame.K_UP:
                        self.p.callRemote(TiltCommand, speed=45.0)
                    elif event.key == pygame.K_DOWN:
                        self.p.callRemote(TiltCommand, speed=-45.0)
                    elif event.key == pygame.K_LEFT:
                        self.p.callRemote(PanCommand, speed=10.0)
                    elif event.key == pygame.K_RIGHT:
                        self.p.callRemote(PanCommand, speed=-10.0)
                    elif event.key == pygame.K_SPACE:
                        self.p.callRemote(FireCommand)
                elif event.type == pygame.KEYUP: # send STOP commands on release
                    if event.key in (pygame.K_UP, pygame.K_DOWN):
                        self.p.callRemote(StopTiltCommand)
                    elif event.key in ( pygame.K_LEFT, pygame.K_RIGHT):
                        self.p.callRemote(StopPanCommand)
        
    
    def connected(self, protocol):
        print("Connection Established")
        self.p = protocol
    
    def disconnected(self):
        print("Connection lost, reestablishing...")
        self.p = None

class ControllerFactory(ClientFactory):
    protocol = amp.AMP
    def __init__(self):
        self.game = None
        if not self.game:
            self.game = GameControl()
    def startFactory(self):
        ClientFactory.startFactory(self)
    
    def clientConnectionFailed(self, connector, reason):
        self.game.disconnected()
        ClientFactory.clientConnectionFailed(self, connector, reason)
    
    def clientConnectionLost(self, connector, reason):
        self.game.disconnected()
        ClientFactory.clientConnectionLost(self, connector, reason)
    
    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        self.game.connected(p)
        return p

def connect():
    endpoint = TCP4ClientEndpoint(reactor, 'abyll-pi.local', 8750)
    factory = ControllerFactory()
    service = ClientService(endpoint, factory, retryPolicy=backoffPolicy(0.5, 15.0))
    service.startService()
    return service.whenConnected()

def main():
    startLogging(stdout)
    
    d = connect()
    d.addErrback(err, 'connection failed')
    
    reactor.run()
    

if __name__ == "__main__":
    main()
