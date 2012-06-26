# -*- encoding: utf-8 -*

import sys
import socket

import pydrop
import pydrop.messages

def ircConnect(serverlist, port):
    port = int(port)
    for server in serverlist:
        server = server.strip()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pydrop.messages.pdebug("Connecting to %s:%s..." % (server, port))
        try:
            s.connect( (server, port) )
        except:
            pydrop.messages.perror("Unable to connect to %s:%s [%s]" % (server, port, sys.exc_info()[1]))
            s = False
        if s != False:
            pydrop.messages.pdebug("Connected! Registering the socket globally and proceeding to client-server communication.")
            return s

def ircSend(sock, content):
    try:
        sock.send("%s\r\n" % (content))
    except:
        return False
    return True

def botRegister(sock, nick, ident, realname, flags):
    try:
        ircSend(sock, "NICK %s" % (nick))
        ircSend(sock, "USER %s \"\" \"\" :%s" % (ident, realname))
    except:
        return False
    return True

def recvline(s):
    ret = ''
    while True:
        c = s.recv(1)
        if c == "\n":
            break
        elif c == '':
            return False
            break
        else:
            ret += c
            
    return ret

def unpackUserHost(text):
    sp1 = text.split("!")
    user = sp1[0][1:]
    ident, host = sp1[1].split("@")
    return (user, ident, host)
    
    
