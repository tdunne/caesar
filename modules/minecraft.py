#!/usr/bin/env python
'''
mcstatus.py - caesar MinecraftStatus Module
Copyright 2014, Tim Dunne
https://github.com/tdunne/caesar
Licensed under the Eiffel Forum License 2.

Utilises Dinnerbone's mcstatus - https://github.com/Dinnerbone/mcstatus/

Credits and my thanks for the inspiration to rakiru - https://github.com/rakiru/

http://inamidst.com/phenny/
'''

import socket
import struct

port = 25565

def mcstatus(caesar, input):
    '''.mcstatus - Get info of the Minecraft server'''
    server = input.group(2)
    try:
        query = MinecraftQuery(server, port)
        status = query.get_status()
        caesar.say("[ %s ] - %s/%s players online" % (status["motd"],
                                                      status["numplayers"],
                                                      status["maxplayers"]))
    except:
        caesar.say("Failed to query server - try again later")

mcstatus.commands = ["mcstatus"] # Syntax !mcstatus
mcstatus.priority = 'low'

def players(caesar, input):    
    server = input.group(2)
    try:
        query = MinecraftQuery(server, port)
        status = query.get_rules()
        caesar.say("Players: %s " % ", ".join(status["players"]))
    except:
        caesar.say("Failed to query server - try again later")

players.commands = ["players"] # Syntax !players
players.priority = 'low'

def version(caesar, input):    
    server = input.group(2)
    try:
        query = MinecraftQuery(server, port)
        status = query.get_rules()
        caesar.say("Minecraft version: %s Bukkit version: %s" % (status["version"],
                                                             str(status["software"])))
    except:
        caesar.say("Failed to query server - try again later")

version.commands = ["version"] # Syntax !version
version.priority = 'low'

def plugins(caesar, input):
    '''!plugins - Returns a list of plugins'''   
    server = input.group(2)
    try:
        query = MinecraftQuery(server, port)
        status = query.get_rules()
        caesar.say("Plugins: [ %s ]" % ", ".join(status["plugins"]))
    except:
        caesar.say("Failed to query server - try again later")

plugins.commands = ["plugins"] # Syntax !plugins
plugins.priority = 'low'

'''All MinecraftQuery stuff (everything below here) from https://github.com/Dinnerbone/mcstatus'''
class MinecraftQuery:
    MAGIC_PREFIX = '\xFE\xFD'
    PACKET_TYPE_CHALLENGE = 9
    PACKET_TYPE_QUERY = 0
    HUMAN_READABLE_NAMES = dict(
        game_id     = "Game Name",
        gametype    = "Game Type",
        motd        = "Message of the Day",
        hostname    = "Server Address",
        hostport    = "Server Port",
        map         = "Main World Name",
        maxplayers  = "Maximum Players",
        numplayers  = "Players Online",
        players     = "List of Players",
        plugins     = "List of Plugins",
        raw_plugins = "Raw Plugin Info",
        software    = "Server Software",
        version     = "Game Version",
        )

    def __init__(self, host, port, timeout=10, id=0, retries=2):
        self.addr = (host, port)
        self.id = id
        self.id_packed = struct.pack('>l', id)
        self.challenge_packed = struct.pack('>l', 0)
        self.retries = 0
        self.max_retries = retries

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)

    def send_raw(self, data):
        self.socket.sendto(self.MAGIC_PREFIX + data, self.addr)

    def send_packet(self, type, data=''):
        self.send_raw(struct.pack('>B', type) + self.id_packed + self.challenge_packed + data)

    def read_packet(self):
        buff = self.socket.recvfrom(1460)[0]
        type = struct.unpack('>B', buff[0])[0]
        id = struct.unpack('>l', buff[1:5])[0]
        return type, id, buff[5:]

    def handshake(self, bypass_retries=False):
        self.send_packet(self.PACKET_TYPE_CHALLENGE)

        try:
            type, id, buff = self.read_packet()
        except:
            if not bypass_retries:
                self.retries += 1

            if self.retries < self.max_retries:
                self.handshake(bypass_retries=bypass_retries)
                return
            else:
                raise

        self.challenge = int(buff[:-1])
        self.challenge_packed = struct.pack('>l', self.challenge)

    def get_status(self):
        if not hasattr(self, 'challenge'):
            self.handshake()

        self.send_packet(self.PACKET_TYPE_QUERY)

        try:
            type, id, buff = self.read_packet()
        except:
            self.handshake()
            return self.get_status()

        data = {}

        data['motd'], data['gametype'], data['map'], data['numplayers'], data['maxplayers'], buff = buff.split('\x00', 5)
        data['hostport'] = struct.unpack('<h', buff[:2])[0]
        buff = buff[2:]
        data['hostname'] = buff[:-1]

        for key in ('numplayers', 'maxplayers'):
            try:
                data[key] = int(data[key])
            except:
                pass

        return data

    def get_rules(self):
        if not hasattr(self, 'challenge'):
            self.handshake()

        self.send_packet(self.PACKET_TYPE_QUERY, self.id_packed)

        try:
            type, id, buff = self.read_packet()
        except:
            self.retries += 1
            if self.retries < self.max_retries:
                self.handshake(bypass_retries=True)
                return self.get_rules()
            else:
                raise

        data = {}

        buff = buff[11:] # splitnum + 2 ints
        items, players = buff.split('\x00\x00\x01player_\x00\x00') # Shamefully stole from https://github.com/barneygale/MCQuery

        if items[:8] == 'hostname':
            items = 'motd' + items[8:]

        items = items.split('\x00')
        data = dict(zip(items[::2], items[1::2]))

        players = players[:-2]

        if players:
            data['players'] = players.split('\x00')
        else:
            data['players'] = []

        for key in ('numplayers', 'maxplayers', 'hostport'):
            try:
                data[key] = int(data[key])
            except:
                pass

        data['raw_plugins'] = data['plugins']
        data['software'], data['plugins'] = self.parse_plugins(data['raw_plugins'])

        return data

    def parse_plugins(self, raw):
        parts = raw.split(':', 1)
        server = parts[0].strip()
        plugins = []

        if len(parts) == 2:
            plugins = parts[1].split(';')
            plugins = map(lambda s: s.strip(), plugins)

        return server, plugins
