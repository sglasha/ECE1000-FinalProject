# ECE 1000 Plant Watering Project
# Simon Glashauser scglashaus42@tntech.edu, scglasha@gmail.com
# Some code was made by following through this guide https://www.instructables.com/Automatic-Raspberry-Pico-W-Watering-System/

# Import Component Needs
from machine import Pin,I2C,ADC
import utime
import gc

# Variables
calibratewet = 1000 # ADC value for a very wet thing
calibratedry = 100000 # ADC value for a very dry thing
checkin = 5 # Time interval (seconds) for each cycle of monitoring loop
# PID Parameters
# Description Stolen From Reddit: In terms of steering a ship:
# Kp is steering harder the further off course you are,
# Ki is steering into the wind to targetact a drift
# Kd is slowing the turn as you approach your course
Kp=2   # Proportional term - Basic steering (This is the first parameter you should tune for a particular setup)
Ki=0   # Integral term - Compensate for heat loss by vessel
Kd=0  # Derivative term - to prevent overshoot due to inertia - if it is zooming towards setpoint this
      # will cancel out the proportional term due to the large negative gradient
target=6 # Target Wetness For Plant

# Initialise Pins
relaypin = Pin(13, mode = Pin.OUT)
wetness = machine.ADC(27)
# Initialise 
gc.enable() # Garbage collection enabled
integral = 0
lastupdate = utime.time()  
lasterror = 0
output=0
offstate=True
# PID infinite loop 
while True:
    try:
        # Get wetness
        imwet = wetness.read_u16()
        howdry = min(10,max(0,10*(imwet-calibratedry)/(calibratewet-calibratedry))) # linear relationship between ADC and wetness, clamped between 0, 10
        now = utime.time()
        dt= now-lastupdate
        if  offstate == False and dt > checkin * round(output)/100 :
            relaypin = Pin(13, mode = Pin.OUT, value =0 )
            offstate= True
            utime.sleep(.1)
        if dt > checkin:
            print("WETNESS",howdry)
            error=target-howdry
            integral = integral + dt * error
            derivative = (error - lasterror)/dt
            output = Kp * error + Ki * integral + Kd * derivative
            print(str(output)+"= Kp term: "+str(Kp*error)+" + Ki term:" + str(Ki*integral) + "+ Kd term: " + str(Kd*derivative))
            output = max(min(100, output), 0) # Clamp output between 0 and 100
            print("OUTPUT ",output)
            if output>0:  
                relaypin.value(0)
                offstate = False
            else:
                relaypin.value(1)
                offstate = True
            utime.sleep(.1)
            lastupdate = now
            lasterror = error  
    except Exception as e:
        print('error encountered:'+str(e))
        utime.sleep(checkin)
