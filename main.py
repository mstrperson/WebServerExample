from http.server import BaseHTTPRequestHandler, HTTPServer
from time import sleep
import threading
import serial
import json
from datetime import datetime
import serial.tools.list_ports

# Get all the devices that show up in your computer.  (there's more than just the Arduino here.)
ports = serial.tools.list_ports.comports()

# look through all the ports....
for p in ports:
    # This identifies the particular Arduino that we have in our kit.  Other Arduinos might not work with this.
    if "Generic CDC" in p.description:
        sPort = p.device
        print(p.description + " on " + p.device)

# try to connect to the thing I identified as an arduino
try:
    ser = serial.Serial(sPort, 9600)
# if I can't connect to it because it isn't there, or because it didn't repsond....
except:
    print("failed to connect serial")
    exit(1)

# Base HTTP settings
hostname = "localhost"  # localhost (or 127.0.0.1) means "this computer"
port = 8080             # different from standard internet port, which is port 80.  8080 is alternate standard.

# some default data to have before the program reads /actual data/ from the Arduino.
data = json.loads('{"temp":-1.0,"hum":-1.0,"hId":-1.0}')

# This is the code that defines what the Web Page will look like!
class WebServer(BaseHTTPRequestHandler):
    pageTitle = "The Coolest Room Temperature Monitor Ever"

    # particularly, this method is what runs when you open your web browser and go to 'http://localhost:8080'
    def do_GET(self):
        # Stuff that makes HTTP work
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Actual Content of the WebPage
        global data     # this accesses the json data defined later in the program.

        # This is the HTML that gets served to the web browser.
        self.wfile.write(bytes("<html><head><title>" + self.pageTitle + "</title></head><body>", "utf-8"))
        self.wfile.write(bytes("<header>" + datetime.now().strftime("%H:%M:%S") + "</header>", "utf-8"))
        self.wfile.write(bytes("<table><tr><th>Tempearture</th><th>Humidity</th><th>Heat Index</th></tr>", "utf-8"))
        # the data[] json object is constantly updated by the remaining Arduino code, so this web page will always have
        # the most up to date values for each of the variable!
        self.wfile.write(bytes("<tr><td>" + str(data["temp"]) + "</td><td>" + str(data["hum"]) +
                               "</td><td>" + str(data["hId"]) + "</td>", "utf-8"))
        self.wfile.write(bytes("</table></body></html>", "utf-8"))

# end of class WebServer

# Create an instance of the WebServer.
webserver = HTTPServer((hostname, port), WebServer)

# I need this to be able to run the webserver in parallel with the update code that connects to the Arduino.
def run():
    print("starting webserver")
    webserver.serve_forever()
# end run()

# create a Thread which runs the webserver.
webServerThread = threading.Thread(target=run)
# start the thread and run the webserver.
# this is so that the webserver.serve_forever() can run forever without blocking my code here
webServerThread.start()

# Now back to the Arduino code.
print("Webserver Running...")

# this loop runs forever (just like webserver.serve_forever()
# the print statements are just for debugging purposes and you can comment them out if you don't want them there~
while True:
    print(datetime.now())
    print("waiting for update")
    while not ser.inWaiting():
        sleep(0.02)  # wait 20ms

    # read new data from the Arduino
    jsonData = ser.readline()
    print(jsonData)

    # this line updates the data which is used by the WebServer to put live data in the web page!
    data = json.loads(jsonData)
    print("__________________________")

# THE END!