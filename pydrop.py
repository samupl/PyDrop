#!/usr/bin/env python
# -*- encoding: utf-8 -*

import argparse
import ConfigParser
import traceback
import socket
import sys

# Pydrop local functions and variables
import pydrop
import pydrop.messages
import pydrop.core
import pydrop.variables
from pydrop.binds import binds
import modules
pydrop.variables.binds = binds

# Some local not-important configuration
_NAME       = "PyDrop"
_AUTHOR     = "Jakub 'samu' Szafrański <s@samu.pl>"
_VERSION    = "0.1"


# Get command-line arguments
parser = argparse.ArgumentParser(description="Python IRC Bot")
parser.add_argument("--config", help="users config file")
args = parser.parse_args()

pydrop.messages.pdebug("Starting %s version %s by %s" % (_NAME, _VERSION, _AUTHOR))

# Read the user-specified config file
if args.config == None:
    pydrop.messages.perror("You haven't specified a config file. Use --config <path> to specify it.")
    exit(1)
    
config = ConfigParser.ConfigParser()
try:
    config.readfp(open(args.config))
except:
    pydrop.messages.perror("There was an error while trying to read the config file (%s):" % (args.config))
    pydrop.messages.perror(sys.exc_info()[1])

# Check if user config file has all options that are REQUIRED to launch
# the bot.
pydrop.messages.pdebug("Checking config file integrity...")

_cfgint = {
    'owner': {
                'nick': "You need to specify a bot owner",
                'password': "You need to set a password for bot maintenance",
            },
    'bot': {
                'nick': "You need to set the bots nick",
                'ident': "You need to set the bots ident",
                'name': "You need to set the bots realname",
            },
    'irc': {
                'name': "No network-name specified",
                'server': "No network address specified",
                'channels': "No auto-join channels specified. If you don't want the bot to join any channels on startup, simply put a '' here"
            },
}

_cfgint_ok = True
for intsection in _cfgint:
    for element in _cfgint[intsection]:
        try:
            config.get(intsection, element)
        except:
            pydrop.messages.perror("Config file error: No %s::%s entry: %s." % (intsection, element, _cfgint[intsection][element]))
            _cfgint_ok = False

if not _cfgint_ok:
    pydrop.messages.pwarning("%s could not start, because of the errors above." % (_NAME))
    exit(5)
else:
    pydrop.messages.pdebug("Config file looks OK, proceeding to the actual start")

pydrop.variables.owner              = config.get('owner', 'nick')
pydrop.variables.password           = config.get('owner', 'password')
pydrop.variables.nick               = config.get('bot', 'nick')
pydrop.variables.owner_identified   = False
pydrop.variables.need_reload        = []

_channels = config.get('irc', 'channels').split(",")


pydrop.messages.pdebug("Loading modules...")

try:
    pydrop.variables.mods = config.get('modules', 'list').split(',')
except:
    pydrop.variables.mods = {}

if pydrop.variables.mods[-1:][0].strip() == '' and len(mods) > 1:
    pydrop.variables.mods = mods[:-1]

for m in pydrop.variables.mods:
    try:
        __import__(m)
    except:
        pydrop.messages.perror("Unable to load preloaded module (%s), backtrace below:" % (m))
        for line in traceback.format_exc().splitlines():
            print line
        pydrop.messages.perror(sys.exc_info()[1])
        exit(3)
    
for _bind in pydrop.variables.binds:
    for _mod in pydrop.variables.binds[_bind]:
        try:
            __import__(_mod)
        except:
            pydrop.messages.perror("Unable to load binded module (%s), backtrace below:" % (_mod))
            for line in traceback.format_exc().splitlines():
                print line
            pydrop.messages.perror(sys.exc_info()[1])
            exit(3)

# All tests have been made, now we are actually connecting to IRC and
# loading everything up

# This variable will be shared among every module (or at least it should)
_serverlist = config.get('irc', 'server').split(',')
_sock = pydrop.core.ircConnect(_serverlist, config.get('irc', 'port'))
_flags = None
_registered = False

while 1:
    line = pydrop.core.recvline(_sock)
    if line == False:
        pydrop.messages.perror("Connection to the IRC server has been lost. Reconnecting...")
        _sock = pydrop.core.ircConnect(_serverlist, config.get('irc', 'port'))
        _registered = False

    if not _registered:
        _registered = pydrop.core.botRegister(_sock, config.get('bot', 'nick'), config.get('bot', 'ident'), config.get('bot', 'name'), _flags)

    try:
        _lsplit = line.split(" ")
    except:
        pass
        
    # Send a signal to all registered binds (modules)
    try:
        _ltext = line.split(" :", 1)[1]
    except:
        _ltext = None
    try:
        if _lsplit[1] == "001":
            for c in _channels:
                c = c.strip()
                if c[-1:] == ',':
                    c = c[:-1]
                pydrop.core.ircSend(_sock, "JOIN %s" % (c))
                    
        if _lsplit[1] in pydrop.variables.binds:
            for mod in pydrop.variables.binds[_lsplit[1]]:
                try:
                    if mod not in sys.modules:
                        __import__(mod)
                    if mod in pydrop.variables.need_reload:
                        reload(sys.modules[mod])
                        del pydrop.variables.need_reload[pydrop.variables.need_reload.index(mod)]
                    getattr(sys.modules[mod], 'init')(_sock, _lsplit, _ltext)
                except:
                    pydrop.messages.pwarning("Error in module (%s):" % (mod))
                    for line in traceback.format_exc().splitlines():
                        print line
                    pydrop.messages.pwarning(sys.exc_info()[1])
                    

        if _lsplit[0] == "PING":
            # Reply to the ping (hardcoded)
            _sock.send("PONG %s" % (_lsplit[1]))
            # !! TODO: PING bindings (somebody may want to use them)
            
    except:
        pass
