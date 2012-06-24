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
from pydrop.binds import binds
import modules

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
                'channel': "No auto-join channels specified. If you don't want the bot to join any channels on startup, simply put a '' here"
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

pydrop.messages.pdebug("Loading modules...")

for _bind in binds:
    for _mod in binds[_bind]:
        try:
            __import__(_mod)
        except:
            pydrop.messages.perror("Unable to load module (), stacktrace below:")
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
    _lsplit = line.split(" ")
    if not _registered:
        _registered = pydrop.core.botRegister(_sock, config.get('bot', 'nick'), config.get('bot', 'ident'), config.get('bot', 'name'), _flags)

    print _lsplit
    # [':xa!~xa@staff.netadmin', 'PRIVMSG', '#main', ':zuo', 'zuo', 'zuo\r']
    # Send a signal to all registered binds (modules)
    try:
        _ltext = line.split(" :", 1)[1]
    except:
        _ltext = None
    if _lsplit[1] in binds:
        for mod in binds[_lsplit[1]]:
                getattr(sys.modules[mod], 'init')(_lsplit, _ltext)

    
    if _lsplit[0] == "PING":
        # Reply to the ping (hardcoded)
        _sock.send("PONG %s" % (_lsplit[1]))
        # !! TODO: PING bindings (somebody may want to use them)