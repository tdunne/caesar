#!/usr/bin/env python
''''
xkcd.py - caesar xkcd Module
Copyright 2014, Tim Dunne
https://github.com/tdunne/caesar
Licensed under the Eiffel Forum License 2.

Michael Yanovich originally wrote an xkcd module for his fork of phenny, jenni - https://github.com/myano/jenni
I took the idea and rewrote the module. Credits to myano for inspiration

http://inamidst.com/phenny/
'''
import json
import random
import web
def xkcd(caesar, input):
	'''get information from xkcd.com'''
	try:
		xkcd = web.get("https://xkcd.com/info.0.json")
	except:
		caesar.reply("Failed to query xkcd, try again later")

	try:
		info = json.loads(xkcd)
	except:
		caesar.reply("Failed to query xkcd, try again later")
	num = info['num']

	'''go to a specified xkcd'''
	comic = input.group(2)
	if comic: # If there is a second piece of input, the user is entering a specific xkcd to go to
		if comic > num: # If the number input is greater than the latest xkcd comic's number, the comic does not exist
			comic = int(comic)
			num = int(num)
			caesar.say("Invalid xkcd!") # therefore is invalid
		caesar.say("https://xkcd.com/%s/" % comic)

	if not comic: # If there is not a second piece of input, generate a random xkcd for the user
		'''return a random xkcd'''
		caesar.say("https://xkcd.com/%s/" % random.randint(0, num))

xkcd.commands = ['xkcd']
xkcd.priority = 'low'

if __name__ == '__main__':
    print __doc__.strip()
