from flask import Flask
import RPi.GPIO as GPIO
import os
import configparser
import threading
import time

# Get the full path to the configuration file
config_file_path = os.path.join('/home/pi/CarInspection', 'config.ini')

# Initialize the configparser
config = configparser.ConfigParser()

# Read the configuration file
config.read(config_file_path)

# Access configuration settings
server_port = config.getint('Settings', 'server_port')
alarm_gpio = config.getint('Settings', 'alarm_gpio')
button_gpio = config.getint('Settings', 'button_gpio')
gate_gpio = config.getint('Settings', 'gate_gpio')

# Create a Flask application instance
app = Flask(__name__)

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setup(alarm_gpio, GPIO.OUT)  # Alarm GPIO pin setup
GPIO.setup(button_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button GPIO pin setup with internal pull-up
GPIO.setup(gate_gpio, GPIO.OUT)  # Gate GPIO pin setup

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Raspberry Pi HTTP Server</title>
    </head>
    <body>
        <h1>Welcome to my Raspberry Pi HTTP Server</h1>
        <a href="/activate">Activate</a>
        <br>
        <a href="/deactivate">Deactivate</a>
        <br>
        <a href="/open">Open</a>
    </body>
    </html>
    '''

@app.route('/activate')
def activate_gpio():
    GPIO.output(alarm_gpio, GPIO.HIGH)  # Activate the alarm
    return 'GPIO activated'

@app.route('/deactivate')
def deactivate_gpio():
    GPIO.output(alarm_gpio, GPIO.LOW)  # Deactivate the alarm
    return 'GPIO deactivated'

@app.route('/open')
def open_gate():
    GPIO.output(gate_gpio, GPIO.HIGH)  # Open the gate
    time.sleep(2)
    GPIO.output(gate_gpio, GPIO.LOW)  # Close the gate
    return 'Open gate'

def button_monitor():
    while True:
        if GPIO.input(button_gpio) == GPIO.LOW:  # Button pressed
            GPIO.output(alarm_gpio, GPIO.LOW)  # Deactivate the alarm
            print("Button pressed")
        time.sleep(0.5)  # Small delay to debounce the button

if __name__ == '__main__':
    # Start the button monitoring thread
    button_thread = threading.Thread(target=button_monitor)
    button_thread.daemon = True  # Allow the thread to exit when the main program exits
    button_thread.start()

    # Run the Flask web server
    app.run(host='0.0.0.0', port=server_port)