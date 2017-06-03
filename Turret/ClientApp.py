#Turret controller - Kivy app
#Copyright 2017 - Abyll Breil
from __future__ import unicode_literals

from sys import stdout
from twisted.python.log import startLogging, err
from twisted.internet.protocol import Factory
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from controller import *

import argparse
def parse_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()

class ControlScreen(FloatLayout):
    def __init__(self, *args, **kwargs):
        super(ControlScreen, self).__init__(*args, **kwargs)
        self.protocol = None

    def TiltUp(self):
        print("Up %s" %(self.protocol!=None))
        if self.protocol:
            self.protocol.callRemote(TiltCommand, speed=45.0)
    
    def TiltDown(self):
        if self.protocol:
            self.protocol.callRemote(TiltCommand, speed=-45.0)
    
    def StopTilt(self):
        if self.protocol:
            self.protocol.callRemote(StopTiltCommand)
    
    def PanLeft(self):
        if self.protocol:
            self.protocol.callRemote(PanCommand, speed=10.0)

    def PanRight(self):
        if self.protocol:
            self.protocol.callRemote(PanCommand, speed=-10.0)

    def StopPan(self):
        if self.protocol:
            self.protocol.callRemote(StopPanCommand)
    
    def Fire(self):
        if self.protocol:
            self.protocol.callRemote(FireCommand)

class KivyControllerFactory(Factory):
    protocol = TurretControlProtocol
    def __init__(self, app):
        print("Initialized")
        self.controller = app

    def startFactory(self):
        Factory.startFactory(self)
        
    def connectionMade(self):
        print("Connection made")

    def connectionLost(self, reason):
        print("Lost because %s" %reason)
        self.controller.disconnected()
    
    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        self.controller.connected(p)
        return p

class ControlApp(App):
    def build(self):
        self.keepalive = None
        d = connect(KivyControllerFactory(self))
        d.addErrback(err, 'connection failed')
        self.screen = ControlScreen()
        return self.screen
    
    def connected(self, server):
        print("Connection Established %s" %server)
        self.screen.protocol = server
        self.keepalive = Clock.schedule_interval(lambda dt: server.callRemote(KeepalivePing), 1) # once per second
        
    def disconnected(self):
        print("Connection lost, reestablishing...")
        self.keepalive.cancel()
        self.screen.protocol = None

def main():
    startLogging(stdout)

    args = parse_args()
    
    controller = ControlApp()
    controller.run()
    

if __name__ == "__main__":
    main()