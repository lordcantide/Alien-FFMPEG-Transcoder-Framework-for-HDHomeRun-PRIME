import subprocess
import re
from cgi import escape
from wsgiref.simple_server import make_server
import urllib2
import os
from multiprocessing import Process, Pipe
from time import sleep

#parsing the following command:
#ffmpeg -i "http://sonnytv.local:5004/auto/v1007" "http://127.0.0.1:8090/tuner1.ffm"
#Configuration Variables
WSGI_HOST = '172.16.5.35' #DEFAULT: 127.0.0.1 . Change this ONLY if you want to expose WSGI beyond FFServer (security?)
WSGI_PORT = 8051
FFS_Transcode = '127.0.0.1' #I don't know why you would change this, but here it is.
FFS_VIEW = '172.16.5.35'
FFS_PORT = '8090'
HDHR_IP = 'sonnytv.local'
tuner = 'tuner' #HDHR Tuners. There are 3 tuners on a HDHR PRIME. FFServer makes 1 feed for each tuner.
#^Need to create routine to identify busy tuners. If they are all busy, feed a "All tuners Busy"


def index(environ, start_response):
    #This function will be mounted on "/" and display for diagnostic purposes.
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''<H1>HDHomeRun WSGI FFMPEG Transcoder.</H1>
    <H2>Use syntax <I>http://%(WSGI_HOST)s:%(WSGI_PORT)s/[tuner]/[channel]</I></H2>
    <H2>The local FFServer will transcode through: <I>http://%(FFS_Transcode)s:%(FFS_PORT)s/[tuner.ffm]</I></H2>
    <H2>To view the transcoder: <I>http://%(FFS_VIEW)s:%(FFS_PORT)s/[tuner_resolution.ts]</I></H2>
    <P>FFserver Viewer resolutions are 480, 720, 1080</P>
    ''' % {'WSGI_HOST': WSGI_HOST,'WSGI_PORT': WSGI_PORT,'FFS_Transcode': FFS_Transcode,'FFS_PORT': FFS_PORT,'FFS_VIEW': FFS_VIEW}]

def ffbroker(environ, start_response):
    #Get the Channel from the url if it was specified there. To do: limit input validation to 4 digit ####
    args = environ['myapp.url_args']
    if args:
        channel = escape(args[0])
        '''quality = escape(args[1])''' #url should be ./channel/quality  <-not captured yet
    else:
        channel = 'null value'
    #Step 1: Check for any FFServer feed playing this HDHR channel. If there is, attach Response to that FFServer feed.
    #Step 2: Check if there is an open feed to run HDHR Channel. If there is not, redirect feed image to a "all tuners in use image"
    #Step 3: Initialize FFMPEG call to FFServer.
    subprocess.call(['ffmpeg','-i','http://'+HDHR_IP+':5004/auto/v'+channel,'http://'+FFS_Transcode+':'+FFS_PORT+'/'+tuner'.ffm'])

    '''Step 4: Show stream (Based on feed). If all connected browsers disconnect from stream, kill FFMPEG subprocess.'''
    #This should work as soon as I figure out how to run the subprocess AND run response below...and MIME
    #localpath = 'http://'+FFS_Transcode+':'+FFS_PORT+'/'+tuner+'_'+quality'+'.ts'
    #print localpath
    #response = urllib2.urlopen(localpath)
    ##I hand-jammed the response code to make it length >=4 characters. I couldn't figure out how to get extended status code. Pretty stupid.
    #start_response(str(response.code)+" OK", [('Content-Type', response.headers.get('Content-Type', 'text/plain')), ('Access-Control-Allow-Origin', '*')])
    #return [response.read()]
    """Next 3 lines are placeholder until work above...works"""
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''ffmpeg -i "http://%(HDHR_IP)s/:5004/%(tuner)s/v%(channel)s" "http://%(FFS_Transcode)s:%(FFS_PORT)s/%(tuner)s.ffm"
    #''' % {'HDHR_IP': HDHR_IP,'tuner': tuner,'channel': channel,'FFS_Transcode': FFS_Transcode,'FFS_PORT': FFS_PORT,'tuner': tuner}]

def not_found(environ, start_response):
    """Called if no URL matches."""
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Incorrect Syntax']

def ffstatus(environ, start_response):
    """Called for FFServer Status Page"""
    localpath = 'http://'+FFS_Transcode+':'+FFS_PORT+'/stat.html' #Can this be used for both status AND Channel selection?
    print localpath
    response = urllib2.urlopen(localpath)
    #I hand-jammed the response code to make it length >=4 characters. I couldn't figure out how to get extended status code. Pretty stupid.
    start_response(str(response.code)+" OK", [('Content-Type', response.headers.get('Content-Type', 'text/plain')), ('Access-Control-Allow-Origin', '*')])
    return [response.read()]

# map urls to functions
urls = [
    (r'^$', index),
    (r'stat.html/?$', ffstatus),
    (r'tuner/?$', ffbroker),
    (r'tuner/(.+)$', ffbroker)
]

def application(environ, start_response):
    """
    The main WSGI application. Dispatch the current request to
    the functions from above and store the regular expression
    captures in the WSGI environment as  `myapp.url_args` so that
    the functions from above can access the url placeholders.

    If nothing matches call the `not_found` function.
    """
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            environ['myapp.url_args'] = match.groups()
            return callback(environ, start_response)
    return not_found(environ, start_response)

srv = make_server(WSGI_HOST, WSGI_PORT, application)
srv.serve_forever()
