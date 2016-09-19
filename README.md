#Alien FFMPEG Transcoder Framework for HDHomeRun PRIME#
##THIS SCRIPT IS NOT COMPLETELY FUNCTIONAL JUST YET##

####INTRODUCTION####
Silicon Dust's HD Homerun PRIME is a cable TV tuner-over-IP solution. It's wonderful for watching your cable channels within your own network, but bandwidth constraints make it challenging to use on-the go. Since it lacks an H.264 native transcoder, I am proposing an "alien" transcoder.
Most plugins for media centers like Plex do not support transcoding, or have some complicated setup. Alien FFMPEG Transcoder is my attempt at an elegant solution to use one of the best freely available transcoders (FFMPEG) with the minimal about of supporting applications.
Rather than choosing a better-known PHP/Javascript stack, Python's WSGI appears to provide a path handle operation of FFMPEG/FFServer using a single, short script. Theoretically, this middleware should allow more resources to be used for transcoding purposes.
My hope is to develop the Alien FFMPEG Transcoder to a point that it is the preferred method for other developers to connect with the HD HomeRun.

####HOW IT WORKS####
As a refresher, HD HomeRun PRIME will 'lock' one of its 3 tuners when a client device navigates to the following path:
* http://HDHR_IP:5004/tuner/channels

where:
- HDHR_IP = the IP of the PRIME
- Tuner = a specified tuner (using 'auto' allows the HDHR to choose the tuner itself)
- Channel = the number of the channel (must add a 'v' in front)

FFServer is installed with FFMPEG. Setting it as a service and setting the proper configurations within ffserver.conf allows FFServer to stream HDHR using the following command line syntax:
'ffmpeg -i "http://HDHR_IP:5004/auto/channel" "http://127.0.0.1:8090/tuner1.ffm"'

If FFServer is exposed to the local LAN (in my script, it's on Loopback), browsing the following path shows the associated stream (by resolution):
+ http://ffserver:8090/tuner1_480.ts
+ http://ffserver:8090/tuner1_720.ts
+ http://ffserver:8090/tuner1_1080.ts

####INSTALLATION INSTRUCTIONS####
1. Set up HD HomeRun PRIME on your network. Make sure it works properly first.
2. Follow FFMPEG installation instructions. Set FFServer as a Service, but do not start it yet.
3. Copy ffserver.conf to the proper installation directory described in FFMPEG documentation.
4. Start the FFServer Service.
5. Verify that you can reach http://ffserver:8090/stat.html
6. Set wsgiFFMPEG.py as a service.
7. Navigate to http://ffserver:8050/stat.html (note the port difference)
8. If successful, navigate to a channel by using the syntax http://ffserver:8050/channel (tuner locking is managed by the script)

####Features:####
+ If a user navigates to a channel that is ALREADY BEING VIEWED on a tuner, the script will simply pass that feed and not lock another tuner
+ If all the tuners are in use, the script will pass a video feed showing that all tuners are in use at this time.
