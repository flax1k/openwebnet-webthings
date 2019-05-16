from __future__ import division
from webthing import (Action, Event, Property, MultipleThings, Thing, Value,
                      WebThingServer)
from reopenwebnet.client import CommandClient
import logging
import time
import sys
import uuid
import yaml

def make_light(client, light):
    thing = Thing(light['name'], ['OnOffSwitch', 'Light'], 'A web connected lamp')

    def update_on(on):
        print("light on ", on)
        client.normal_request(1, light['address'], 1 if on else 0)

    thing.add_property(
        Property(thing,
                 'on',
                 Value(False, update_on),
                 metadata={
                     '@type': 'OnOffProperty',
                     'title': 'On/Off',
                     'type': 'boolean',
                     'description': 'Whether the lamp is turned on',
                 }))

    return thing


def make_lights(client, lights):
    return [make_light(client, light) for light in lights]


def make_things(config):
    gw = config['gateway']
    client = CommandClient(gw['host'], gw['port'], gw['password'])

    return make_lights(client, config['lights'])


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
