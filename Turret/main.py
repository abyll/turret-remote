#Turret controller - Kivy app
#Copyright 2017 - Abyll Breil
from __future__ import unicode_literals

from sys import stdout
from twisted.python.log import startLogging, err
from twisted.internet.protocol import Factory
from kivy.support import install_twisted_reactor
install_twisted_reactor()
#from twisted.application.internet import ClientService, backoffPolicy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.storage.dictstore import DictStore
from controller import *

__version__ = "0.0.4"

class ControlScreen(FloatLayout):
    def __init__(self, app, *args, **kwargs):
        self.app = app
        super(ControlScreen, self).__init__(*args, **kwargs)
        self.protocol = None

    def TiltUp(self):
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
    
    def open_settings(self):
        self.app.open_settings()

class KivyControllerFactory(Factory):
    protocol = TurretControlProtocol
    def __init__(self, app):
        self.controller = app

    def startFactory(self):
        Factory.startFactory(self)
        
    def connectionMade(self):
        pass

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
        self.connect()
        self.screen = ControlScreen(self)
        return self.screen
        
    def connect(self):
        factory, dest, port = KivyControllerFactory(self), self.config.get("Connection", "server"), int(self.config.get("Connection", "port"))
        self.endpoint = TCP4ClientEndpoint(reactor, dest, port)
        # self.service = ClientService(endpoint, factory, retryPolicy=backoffPolicy(0.5, 15.0))
        # self.service.startService()
        # d = self.service.whenConnected()
        d = self.endpoint.connect(factory)
        d.addErrback(err, 'connection failed')
        return d
    
    def disconnect(self):
        print("Disconnecting intentionally")
        if self.screen.protocol: #Can't disconnect if we're not connected.
            return self.screen.protocol.disconnect()
    
    def connected(self, server):
        print("Connection Established %s" %server)
        self.screen.protocol = server
        self.keepalive = Clock.schedule_interval(lambda dt: server.callRemote(KeepalivePing), int(self.config.get("Connection", "keepalive"))) # once per second
        
    def disconnected(self):
        print("Connection lost, reestablishing...")
        self.keepalive.cancel()
        self.screen.protocol = None

    def build_config(self, config):
        config.setdefaults('Connection', {
            'server': '192.168.43.160',
            'port': 8750,
            'keepalive': 3
        })

    def build_settings(self, settings):
        settings.add_json_panel('SentryMote', self.config, data="""[
        { "type": "title",
          "title": "SentryMote" },

        { "type": "string",
          "title": "Server",
          "desc": "Select IP or hostname of turret",
          "section": "Connection",
          "key": "server"},

        { "type": "numeric",
          "title": "Port",
          "desc": "server port",
          "section": "Connection",
          "key": "port" }
        ]""")

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            disconnect = self.disconnect()
            if disconnect:
                disconnect.addCallback(self.connect)
            else: # We didnt have to wait; we may already have been disconnected.
                self.connect()
            

def main():
    startLogging(stdout)
    
    controller = ControlApp()
    controller.run()
    

if __name__ == "__main__":
    main()