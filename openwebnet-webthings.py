from __future__ import division
from webthing import (Action, Event, Property, MultipleThings, Thing, Value,
                      WebThingServer)
from threading import Thread
from reopenwebnet.client import CommandClient
from reopenwebnet.eventclient import EventClient
import tornado.ioloop
import logging
import time
import sys
import uuid
import yaml

class OpenWebNetObserver:
    def __init__(self, host, port, password):
        def handle_connect():
            print("Event client connected")

        def handle_event(msg):
            self.handle_event(msg)

        self.event_client = EventClient(host, port, password, handle_connect, handle_event)
        self.event_client.start()

        self.listeners = {}
        
    def add_listener(self, who, where, listener):
        key = (who,where)
        self.listeners[key] = listener

    def handle_event(self, messages):
        for msg in messages:
            if not msg.startswith("*") or not msg.endswith("##"):
                # does not look like a status message
                continue

            parts = msg[1:-2].split("*")
            if len(parts) != 3:
                # also does not look like a status message
                continue
            
            who,what,where = parts
            key = (who,where)

            if key in self.listeners:
                self.listeners[key](what)

def make_light(client, observer, light):
    thing = Thing(light['name'], ['OnOffSwitch', 'Light'], 'A web connected lamp')

    def update_on(on):
        client.normal_request(1, light['address'], 1 if on else 0)

    value = Value(False, update_on)
    ioloop = tornado.ioloop.IOLoop.instance()

    def update_handler(what):
        ioloop.add_callback(lambda : value.notify_of_external_update(what != '0'))

    observer.add_listener('1', str(light['address']), update_handler)

    thing.add_property(
        Property(thing,
                 'on',
                 value,
                 metadata={
                     '@type': 'OnOffProperty',
                     'title': 'On/Off',
                     'type': 'boolean',
                     'description': 'Whether the lamp is turned on',
                 }))

    return thing


def make_lights(client, observer, lights):
    return [make_light(client, observer, light) for light in lights]


def make_things(config):
    gw = config['gateway']
    client = CommandClient(gw['host'], gw['port'], gw['password'])
    observer = OpenWebNetObserver(gw['host'], gw['port'], gw['password'])

    return make_lights(client, observer, config['lights'])


def run_server(config):
    things = make_things(config)

    port = 8888
    server = WebThingServer(MultipleThings(things, 'OpenWebNet'), port=port)
    try:
        print('starting the server on port %d'%(port,))
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    #logging.basicConfig(
    #    level=10,
    #    format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    #)
    if len(sys.argv) < 2:
        print("Usage: python %s <configfile.yaml>"%(sys.argv[0],))
        sys.exit(1)

    config_file = sys.argv[1]
    config = yaml.load(open(config_file))
    run_server(config)
