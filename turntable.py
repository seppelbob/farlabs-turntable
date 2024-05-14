from subprocess import call
import datetime, time, serial, sys, os, string
import BaseHTTPServer
import SocketServer
import threading


HOST_NAME = os.getenv('COMPUTERNAME') + '.ltu.edu.au'
PORT_NUMBER = 1131


allowed_clients = ['203.101.228.254']

running = 1
currentGeigerCounts = 0 # this is written to in a separate thread, so read-only!


def checkClient(handler, ipString):
    if ipString in allowed_clients:
        return 1    
    if ipString.split('.')[0:3] == ['131','172','133']: # Allow local subnet        
        return 1        
    handler.send_error(401)
    return 0
    
        
def geigerReader():
    global currentGeigerCounts
    while running:
        serRead = geigerCom.readline()
        if serRead != '':
            currentGeigerCounts = serRead       
    geigerCom.close()

def Activity(experiment): 
    # writes total number of instructions sent during a booking period to file "user_instructions.csv"#
    # .csv format: experiment,starttime,endtime,number #
    # eg: tt1,2020-05-26 22:47:00,2020-05-26 22:59:01,11 #

    current_activity = datetime.datetime.now().replace(microsecond=0)
    filename = "user_instructions.csv"

    try:
        file = open(filename,"r")
        data = file.readlines()
        last_line = data[len(data)-1] # read the last line of data
        checkpoint_activity = datetime.datetime.strptime(last_line[last_line.find('20'):last_line.find('20')+18],'%Y-%m-%d %H:%M:%S') # read the last starttime
	block_activity = int(last_line[last_line.find('20')+40:])
        file.close()
    except:
        checkpoint_activity = datetime.datetime(2010,1,1,1,1) #initialise
        block_activity = 0 #initialise

    n1 = 30 - current_activity.minute
    n2 = 30 - checkpoint_activity.minute
    if n1*n2 <= 0 or current_activity-checkpoint_activity > datetime.timedelta(minutes=30):
        #add time to sheet as start time
        file = open(filename,"a+")
        file.write(experiment+ "," + str(current_activity) +","+ str(current_activity) + ",1\n")
        file.close()
    else:
        block_activity = block_activity+1
        file = open(filename,"r")
        data = file.readlines()
        file.close()
        data[len(data)-1] = experiment + "," + str(checkpoint_activity) + "," +str(current_activity) + "," + str(block_activity) + "\n"
        file = open(filename,"w")
        file.writelines(data)
        file.close()

def trayControl(path):	
    serialCommand = ""	
    if path == "/srcalpha":
        serialCommand = 's13'
    elif path == "/srcbeta":
        serialCommand = 's15'
    elif path == "/srcgamma":
        serialCommand = 's17'
    elif path == "/srcunknown":
        serialCommand = 's19'
    elif path == "/absnone":
        serialCommand = 's32'
    elif path == "/absplastic":
        serialCommand = 's33'
    elif path == "/absthinal":
        serialCommand = 's35'
    elif path == "/absthickal":
        serialCommand = 's37'
    elif path == "/abslead":
        serialCommand = 's39'
    if len(serialCommand) != 0:
        print serialCommand
        turntableCom.write(serialCommand)
	Activity("tt1") #run the script to write people's activity to file


class ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass


class Web(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_HEAD(self, code, type):
        self.send_response(code)
        self.send_header("Content-type", type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
    
    def do_POST(self):
        """Respond to a POST request."""

        if not checkClient(self, self.client_address[0]):
            return

        if self.path.endswith("/geigerCounts"):
            self.do_HEAD(200, "text/plain")            
            self.wfile.write(str(currentGeigerCounts)) 
            #print str(currentGeigerCounts)       
        else: 
            self.do_HEAD(200, "text/plain")
            trayControl(self.path)					


if __name__ == '__main__':

    turntableCom = 1 # slider is built-in com port unless specified
    geigerCom = -1

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            parts = arg.split("=")
            if len(parts) == 2:
                if parts[0] == "turntable":                    
                    turntableCom = int(parts[1])
                elif parts[0] == "geiger":                                    
                    geigerCom = int(parts[1])                    
            else:
                print "Invalid option: " + arg
                exit()
            
    if turntableCom <= 0:
        print "Invalid turntable com port: " + str(turntableCom) +  " (set using argument turntable=port)"
        exit()
        
    if geigerCom <= 0:
        print "Invalid geiger com port: " + str(geigerCom) + " (set using argument geiger=port)"
        exit()
        
    turntableCom = serial.Serial(0, 9600)  # open com 1 for source/absorber trays
    print "Turntable: " + str(turntableCom)
    geigerCom = serial.Serial(geigerCom, 9600)	 # open com 4 for geiger counter
    print "Geiger: " + str(geigerCom)

    # Start the geiger reader in another thread
    t = threading.Thread(target=geigerReader)
    t.start()

    # Start the server in the main thread
    server_class = ThreadedHTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), Web)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()	
    turntableCom.close()
    running = 0 # this will tell the geiger reader thread to terminate	
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)





