#! /usr/bin/python

""" Modifed to submit JSON events rather than raw
    January 2019
"""

""" Based on the demonstration app provided by rsyslog  
    Copyright (c) 2016 Ryan Faircloth
    Output module for Splunk HTTP Event Collector
"""
"""A skeleton for a python rsyslog output plugin
   Copyright (C) 2014 by Adiscon GmbH
   This file is part of rsyslog.
  
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
   
         http://www.apache.org/licenses/LICENSE-2.0
         -or-
         see COPYING.ASL20 in the source distribution
   
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

# System modules
import os
import sys
import Queue
import threading 
import time

import argparse
import select

import requests
import urllib
import json
import socket
import uuid

import logging

_LOG_LEVEL_STRINGS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

# max nbr of messages that are processed within one wbatch

def _log_level_string_to_int(log_level_string):
    if not log_level_string in _LOG_LEVEL_STRINGS:
        message = 'invalid choice: {0} (choose from {1})'.format(log_level_string, _LOG_LEVEL_STRINGS)
        raise argparse.ArgumentTypeError(message)

    log_level_int = getattr(logging, log_level_string, logging.INFO)
    # check the logging log_level_choices have not changed from our expected values
    assert isinstance(log_level_int, int)

    return log_level_int



# skeleton config parameters
pollPeriod = 0.2 # the number of seconds between polling for new messages
host=socket.gethostname()

parser = argparse.ArgumentParser()
parser.add_argument("token", help="http event collector token")
parser.add_argument("server", help="http event collector  fqdn")
parser.add_argument('--port', help="port",default='8088')
parser.add_argument('--ssl', help="use ssl",action='store_true',default=False)
parser.add_argument('--ssl_noverify', help="disable ssl validation",action='store_false',default=True)

#parser.add_argument('--source',default="hec:syslog:" + host)
#parser.add_argument('--sourcetype',default="syslog")
#parser.add_argument('--index',default="main")
#parser.add_argument('--host',default=host)
parser.add_argument('--maxBatch',help="max number of records allowed in one batch of requests for hec",default=10,type=int)
parser.add_argument('--maxQueue',help="max number of records to be read from rsyslog queued for transfer",default=5000,type=int)
parser.add_argument('--maxThreads',help="max number of threads for work",default=10,type=int)


parser.add_argument('--nopost', help="don't ppost for debug reasonse",action='store_false')

parser.add_argument('--log_dir',help="log directory",default="/var/log",type=str )

parser.add_argument('--log-level',
                    default='CRITICAL',
                    dest='log_level',
                    type=_log_level_string_to_int,
                    nargs='?',
                    help='Set the logging output level. {0}'.format(_LOG_LEVEL_STRINGS))

args = parser.parse_args()


# create logger with 'spam_application'
logger = logging.getLogger('omsplunkhec')
logger.setLevel(args.log_level)

fi = logging.FileHandler(os.path.join(args.log_dir,'omsplunkhec.log'))
fi.setLevel(args.log_level)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fi.setFormatter(formatter)
logger.addHandler(fi)



def onReceive(threadID, mq, tq, evt):
	"""This is the entry point where actual work needs to be done. It receives
	   a list with all messages pulled from rsyslog. The list is of variable
	   length, but contains all messages that are currently available. It is
	   suggest NOT to use any further buffering, as we do not know when the
	   next message will arrive. It may be in a nanosecond from now, but it
	   may also be in three hours...
	"""

	with requests.Session() as s:

		session_id = str(uuid.uuid1())
		headers = {'Authorization':'Splunk '+args.token, 'X-Splunk-Request-Channel':session_id}
		if args.ssl:
			protocol = 'https'
		else:
			protocol = 'http'

		server_uri = '%s://%s:%s/services/collector/event' % (protocol, args.server, args.port)

		logger.info('TheadID %s' % (threadID))
		logger.info('server_uri= %s' % (server_uri))
		#print server_uri + " token=" + args.token
		#print '%s: starting, control state %s' % (threadID, evt.is_set())
		while not evt.is_set() or not mq.empty():
			c=0
			data = []
			sl=0
			while sl<2 and c < args.maxBatch:
				try:
					m = mq.get(True, 1)
					logger.debug('m= %s' % (m))
					#m_split = m.split(' ', 4)
					#m_python = {
						#'event': m,
						#'host': m_split[2],
						#'index': args.index,
						#'source': args.source,
						#'sourcetype': args.sourcetype,
						#'time': m_split[1], # HEC requires epoch format
					#}
					#logger.debug('m_python= %s' % (m_python))
					#m_json = json.dumps(m_python)
					#logger.debug('m_json= %s' % (m))
					c = c+1
					data.append(m)
					mq.task_done()
				except Queue.Empty:
					sl=sl+1
					logger.debug("empty queue sleeping")
					time.sleep(3)
			#Place one event int the batch
			if c>0:
				logger.info("sending %s" %(c))
				d = "".join(data)
				if args.nopost:
					r = s.post(server_uri,data=d,headers=headers, verify=args.ssl_noverify)
					if r.status_code==200:
						logger.debug("r.status_code=%s" % (r.status_code))
						logger.debug("r=%s" % (r.text))
					else:
						logger.warning("r.status_code=%s" % (r.status_code))
						logger.warning("r=%s" % (r.text))

			else:
				logger.info("sending 0")
		z = tq.get()
		#print '%s: Flushed Batch' % threadID
		tq.task_done()


"""
-------------------------------------------------------
This is plumbing that DOES NOT need to be CHANGED
-------------------------------------------------------
Implementor's note: Python seems to very agressively
buffer stdouot. The end result was that rsyslog does not
receive the script's messages in a timely manner (sometimes
even never, probably due to races). To prevent this, we
flush stdout after we have done processing. This is especially
important once we get to the point where the plugin does
two-way conversations with rsyslog. Do NOT change this!
See also: https://github.com/rsyslog/rsyslog/issues/22
"""

stop_event = threading.Event()
#stop_event.set()
maxAtOnce = args.maxBatch
msgQueue=Queue.Queue(maxsize=args.maxQueue)
threadQueue = Queue.Queue(maxsize=args.maxThreads)


for i in range(args.maxThreads):
	threadQueue.put(i)
	worker = threading.Thread(target=onReceive, args=(i, msgQueue, threadQueue, stop_event))
    	worker.setDaemon(True)
	worker.start()

while not stop_event.is_set():
	while not stop_event.is_set() and sys.stdin in select.select([sys.stdin], [], [], pollPeriod)[0]:
		line = sys.stdin.readline()
		if line:
			msgQueue.put(line)
		else: # an empty line means stdin has been closed
			logger.info('end of stdin')
			stop_event.set()
			msgQueue.join()
			logger.info('msgQueue joined')

logger.info('waiting for thread shutdown')
threadQueue.join()

sys.stdout.flush() # very important, Python buffers far too much!
