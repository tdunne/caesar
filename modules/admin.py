#!/usr/bin/env python
"""
admin.py - Phenny Admin Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny

Beefed up by Tim Dunne, https://github.com/tdunne/caesar
Also licensed under the Eiffel Forum License 2.
"""

def join(caesar, input): 
   """Join the specified channel. This is an admin-only command."""
   # Can only be done in privmsg by an admin
   if input.sender.startswith('#'): return
   if input.admin: 
      channel, key = input.group(1), input.group(2)
      if not key: 
         caesar.write(['JOIN'], channel)
      else: caesar.write(['JOIN', channel, key])
join.rule = r'\.join (#\S+)(?: *(\S+))?'
join.priority = 'low'
join.example = '.join #example or .join #example key'

def part(caesar, input): 
   """Part the specified channel. This is an admin-only command."""
   # Can only be done in privmsg by an admin
   if input.sender.startswith('#'): return
   if input.admin: 
      caesar.write(['PART'], input.group(2))
part.commands = ['part']
part.priority = 'low'
part.example = '.part #example'

def quit(caesar, input): 
   """Quit from the server. This is an owner-only command."""
   # Can only be done in privmsg by the owner
   if input.sender.startswith('#'): return
   if input.owner: 
      caesar.write(['QUIT'])
      __import__('os')._exit(0)
quit.commands = ['quit']
quit.priority = 'low'

def msg(caesar, input): 
   # Can only be done in privmsg by an admin
   if input.sender.startswith('#'): return
   a, b = input.group(2), input.group(3)
   if (not a) or (not b): return
   if input.admin: 
      caesar.msg(a, b)
msg.rule = (['msg'], r'(#?\S+) (.+)')
msg.priority = 'low'

def me(caesar, input): 
   # Can only be done in privmsg by an admin
   if input.sender.startswith('#'): return
   if input.admin: 
      msg = '\x01ACTION %s\x01' % input.group(3)
      caesar.msg(input.group(2) or input.sender, msg)
me.rule = (['me'], r'(#?\S+) (.+)')
me.priority = 'low'

'''
All functions below here are the work of Tim Dunne.
Licensed under the Eiffel Forum License 2.
'''
def op(caesar, input):
	'''Op the specified user. Admin-only command'''
	# Syntax !op nick #channel
	nick = input.group(2)
	channel = input.sender
	if not nick: # if no nick is entered, caesar will op the person who used the command
		nick = input.nick 
	if input.admin:
		caesar.write(['MODE', channel, '+o', nick])
op.commands = ['op']
op.priority = 'low'
op.example = '!op nick #channel'	
	
def deop(caesar, input):
	'''Deop the specified user. Admin-only command'''
	# Syntax !deop nick #channel
	nick = input.group(2)
	channel = input.sender
	if not nick: # if no nick is entered, caesar will deop the person who used the command...
		nick = input.nick 
	if input.admin:	
		caesar.write(['MODE', channel, '-o', nick])
deop.commands = ['deop']
deop.priority = 'low'
deop.example = '!deop nick #channel'	

def autovoice(caesar, input):
	'''Autovoices any nick which joins any channel caesar has op in.'''
	nick = input.nick
	channel = caesar.config.autovoicechan
	caesar.write(['MODE', channel, '+v', nick])
autovoice.event = 'JOIN'
autovoice.priority = 'low'
autovoice.rule = r'.*'

def changenick(caesar, input):
	'''Changes the bot's nick. Owner-only command'''
	# Syntax !nick newnick
	if input.owner:
		nick = input.group(2)
		caesar.write(['NICK', nick])
changenick.commands = ['nick']
changenick.example = '!nick newnick'

def voice(caesar, input):
	'''Voice the specified nick. Admin-only command'''
	# Syntax !voice nick #channel
	nick = input.group(2)
	channel = input.sender
	if not nick: # if no nick is entered, caesar will voice the person who used the command
		nick = input.nick 
	if input.admin:
		caesar.write(['MODE', channel, '+v', nick])
voice.commands = ['voice']
voice.priority = 'low'
voice.example = '!voice nick'

if __name__ == '__main__': 
   print __doc__.strip()
