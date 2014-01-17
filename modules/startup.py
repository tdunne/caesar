#!/usr/bin/env python
"""
startup.py - Phenny Startup Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import threading, time

def setup(caesar): 
   print("Setting up caesar")
   # by clsn
   caesar.data = {}
   refresh_delay = 300.0

   if hasattr(caesar.config, 'refresh_delay'):
      try: refresh_delay = float(caesar.config.refresh_delay)
      except: pass

      def close():
         print "Nobody PONGed our PING, restarting"
         caesar.handle_close()
      
      def pingloop():
         timer = threading.Timer(refresh_delay, close, ())
         caesar.data['startup.setup.timer'] = timer
         caesar.data['startup.setup.timer'].start()
         # print "PING!"
         caesar.write(('PING', caesar.config.host))
      caesar.data['startup.setup.pingloop'] = pingloop

      def pong(caesar, input):
         try:
            # print "PONG!"
            caesar.data['startup.setup.timer'].cancel()
            time.sleep(refresh_delay + 60.0)
            pingloop()
         except: pass
      pong.event = 'PONG'
      pong.thread = True
      pong.rule = r'.*'
      caesar.variables['pong'] = pong

def startup(caesar, input): 
   import time

   # Start the ping loop. Has to be done after USER on e.g. quakenet
   if caesar.data.get('startup.setup.pingloop'):
      caesar.data['startup.setup.pingloop']()

   if hasattr(caesar.config, 'serverpass'): 
      caesar.write(('PASS', caesar.config.serverpass))

   if hasattr(caesar.config, 'password'): 
      caesar.msg('NickServ', 'IDENTIFY %s' % caesar.config.password)
      time.sleep(5)

   # Cf. http://swhack.com/logs/2005-12-05#T19-32-36
   for channel in caesar.channels: 
      caesar.write(('JOIN', channel))
      time.sleep(0.5)
startup.rule = r'(.*)'
startup.event = '251'
startup.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
