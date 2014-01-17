#!/usr/bin/env python
"""
remind.py - Phenny Reminder Module
Copyright 2011, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import os, re, time, threading

def filename(self): 
   name = self.nick + '-' + self.config.host + '.reminders.db'
   return os.path.join(os.path.expanduser('~/.caesar'), name)

def load_database(name): 
   data = {}
   if os.path.isfile(name): 
      f = open(name, 'rb')
      for line in f: 
         unixtime, channel, nick, message = line.split('\t')
         message = message.rstrip('\n')
         t = int(unixtime)
         reminder = (channel, nick, message)
         try: data[t].append(reminder)
         except KeyError: data[t] = [reminder]
      f.close()
   return data

def dump_database(name, data): 
   f = open(name, 'wb')
   for unixtime, reminders in data.iteritems(): 
      for channel, nick, message in reminders: 
         f.write('%s\t%s\t%s\t%s\n' % (unixtime, channel, nick, message))
   f.close()

def setup(caesar): 
   caesar.rfn = filename(caesar)

   # caesar.sending.acquire()
   caesar.rdb = load_database(caesar.rfn)
   # caesar.sending.release()

   def monitor(caesar): 
      time.sleep(5)
      while True: 
         now = int(time.time())
         unixtimes = [int(key) for key in caesar.rdb]
         oldtimes = [t for t in unixtimes if t <= now]
         if oldtimes: 
            for oldtime in oldtimes: 
               for (channel, nick, message) in caesar.rdb[oldtime]: 
                  if message: 
                     caesar.msg(channel, nick + ': ' + message)
                  else: caesar.msg(channel, nick + '!')
               del caesar.rdb[oldtime]

            # caesar.sending.acquire()
            dump_database(caesar.rfn, caesar.rdb)
            # caesar.sending.release()
         time.sleep(2.5)

   targs = (caesar,)
   t = threading.Thread(target=monitor, args=targs)
   t.start()

scaling = {
   'years': 365.25 * 24 * 3600, 
   'year': 365.25 * 24 * 3600, 
   'yrs': 365.25 * 24 * 3600, 
   'y': 365.25 * 24 * 3600, 

   'months': 29.53059 * 24 * 3600, 
   'month': 29.53059 * 24 * 3600, 
   'mo': 29.53059 * 24 * 3600, 

   'weeks': 7 * 24 * 3600, 
   'week': 7 * 24 * 3600, 
   'wks': 7 * 24 * 3600, 
   'wk': 7 * 24 * 3600, 
   'w': 7 * 24 * 3600, 

   'days': 24 * 3600, 
   'day': 24 * 3600, 
   'd': 24 * 3600, 

   'hours': 3600, 
   'hour': 3600, 
   'hrs': 3600, 
   'hr': 3600, 
   'h': 3600, 

   'minutes': 60, 
   'minute': 60, 
   'mins': 60, 
   'min': 60, 
   'm': 60, 

   'seconds': 1, 
   'second': 1, 
   'secs': 1, 
   'sec': 1, 
   's': 1
}

periods = '|'.join(scaling.keys())
p_command = r'\.in ([0-9]+(?:\.[0-9]+)?)\s?((?:%s)\b)?:?\s?(.*)' % periods
r_command = re.compile(p_command)

def remind(caesar, input): 
   m = r_command.match(input.bytes)
   if not m: 
      return caesar.reply("Sorry, didn't understand the input.")
   length, scale, message = m.groups()

   length = float(length)
   factor = scaling.get(scale, 60)
   duration = length * factor

   if duration % 1: 
      duration = int(duration) + 1
   else: duration = int(duration)

   t = int(time.time()) + duration
   reminder = (input.sender, input.nick, message)

   try: caesar.rdb[t].append(reminder)
   except KeyError: caesar.rdb[t] = [reminder]

   dump_database(caesar.rfn, caesar.rdb)

   if duration >= 60: 
      w = ''
      if duration >= 3600 * 12: 
         w += time.strftime(' on %d %b %Y', time.gmtime(t))
      w += time.strftime(' at %H:%MZ', time.gmtime(t))
      caesar.reply('Okay, will remind%s' % w)
   else: caesar.reply('Okay, will remind in %s secs' % duration)
remind.commands = ['in']

r_time = re.compile(r'^([0-9]{2}[:.][0-9]{2})')
r_zone = re.compile(r'( ?([A-Za-z]+|[+-]\d\d?))')

import calendar
from clock import TimeZones

def at(caesar, input):
   bytes = input[4:]

   m = r_time.match(bytes)
   if not m: 
      return caesar.reply("Sorry, didn't understand the time spec.")
   t = m.group(1).replace('.', ':')
   bytes = bytes[len(t):]

   m = r_zone.match(bytes)
   if not m: 
      return caesar.reply("Sorry, didn't understand the zone spec.")
   z = m.group(2)
   bytes = bytes[len(m.group(1)):].strip().encode("utf-8")

   if z.startswith('+') or z.startswith('-'):
      tz = int(z)

   if TimeZones.has_key(z):
      tz = TimeZones[z]
   else: return caesar.reply("Sorry, didn't understand the time zone.")

   d = time.strftime("%Y-%m-%d", time.gmtime())
   d = time.strptime(("%s %s" % (d, t)).encode("utf-8"), "%Y-%m-%d %H:%M")

   d = int(calendar.timegm(d) - (3600 * tz))
   duration = int((d - time.time()) / 60)

   if duration < 1:
      return caesar.reply("Sorry, that date is this minute or in the past. And only times in the same day are supported!")

   # caesar.say("%s %s %s" % (t, tz, d))

   reminder = (input.sender, input.nick, bytes)
   # caesar.say(str((d, reminder)))
   try: caesar.rdb[d].append(reminder)
   except KeyError: caesar.rdb[d] = [reminder]

   caesar.sending.acquire()
   dump_database(caesar.rfn, caesar.rdb)
   caesar.sending.release()

   caesar.reply("Reminding at %s %s - in %s minute(s)" % (t, z, duration))
at.commands = ['at']

if __name__ == '__main__': 
   print __doc__.strip()
