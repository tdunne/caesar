#!/usr/bin/env python
''''
services.py - caesar IRC Services Module
Copyright 2014, Tim Dunne
https://github.com/tdunne/caesar
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
'''

def nickservreg(caesar, input):
	'''register the bot's nickname with NickServ'''
	# Must be done through privmsg with owner
	email = caesar.config.email
	password = caesar.config.nickservpass
	if input.sender.startswith('#'): return
	if input.owner:
		caesar.write(['PRIVMSG', 'NICKSERV', 'REGISTER', password, email])
nickservreg.commands = ['nsregister'] # Should only have to be used once. Syntax: !nsregister
nickservreg.priority = 'medium'

def nslogin(caesar, input):
	'''log in to NickServ'''
	# Admin only command
	password = caesar.config.nickservpass
	if input.admin:
		caesar.write(['PRIVMSG', 'NICKSERV', 'IDENTIFY', password])
nslogin.commands = ['nslogin'] # Syntax !nslogin
nslogin.priority = 'medium'

def nsupdate(caesar, input):
	'''Update caesar's NickServ status'''
	# Admin-only command
	if input.admin:
		caesar.write(['PRIVMSG', 'NICKSERV', 'UPDATE'])
nsupdate.commands = ['nsupdate'] # Syntax !nsupdate
nsupdate.priority = 'medium'

def hostservrequest(caesar, input):
	'''request a vhost'''
	vhost = caesar.config.vhost
	if input.sender.startswith('#'): return # Must be done through privmsg and...
	if input.owner: # ...by the owner
		caesar.write(['PRIVMSG', 'HOSTSERV', 'REQUEST', vhost])
hostservrequest.commands = ['vhost'] # Syntax !vhost
hostservrequest.priority = 'medium'

def cslogin(caesar, input):
	'''log into a channel through ChanServ'''
		channel = caesar.config.cschannel
		password = caesar.config.chanservpass
		if input.sender.startswith('#'): return # Must be done through privmsg and...
		if input.owner: # ...by the owner
			caesar.write(['PRIVMSG', 'CHANSERV', 'IDENTIFY', channel, password])
cslogin.commands = ['cslogin'] # Syntax !cslogin
cslogin.priority = 'medium'

if __name__ == '__main__': 
	print __doc__.strip()
		
