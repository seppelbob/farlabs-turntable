import subprocess as proc
import time, datetime, sys

child = None
starts = 0
reconnect = True

def restart(exe):
    global starts, child
    print "(Re)starting ffmpeg..."
    starts = starts + 1
    child = proc.Popen(exe, stderr=proc.PIPE)
    print "Started child (", starts, ")"

def monitor(line):
    if line.find("bitrate=") > -1:
	try:
        	bitrate = int(float(line.split("bitrate=")[1].split("kbits/s")[0]))
	except ValueError:
		bitrate=1
        print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), " Current Bitrate: ", bitrate
        if bitrate == 0:
            child.kill()
            
if __name__ == '__main__':    

   
    camType = sys.argv[1]
    camServer = sys.argv[2]
    camSlug = sys.argv[3]

    camServer += camSlug    

    exe = 'ffmpeg -f dshow -i video="' + camType + '" -f mpegts -codec:v mpeg1video -vf "crop=1440:1080:240:0" -b 0 ' + camServer
    print(exe)
   

    buf = ""
    while reconnect == True:
	print exe
        restart(exe)

        while child.returncode == None:
            child.poll()
            log = child.stderr.read(100)
            buf = buf + log            
            lines = buf.split("frame=")
            if len(lines) > 1:
                monitor(lines[-2])
                buf = lines[-1]

        print "ffmpeg process stopped...waiting 10 seconds"
        time.sleep(10)




