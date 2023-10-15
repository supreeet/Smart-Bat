from easy_comms import Easy_comms
import time
from machine import Pin, reset, ADC, PWM, Timer
import json, neopixel, _thread, random

int_pin = Pin(0,Pin.IN,Pin.PULL_DOWN)
led1 = Pin(25,Pin.OUT)

ldr_adc = ADC(2)
ambient_light = ldr_adc.read_u16()

lcd_brightness = PWM(Pin(22))
lcd_brightness.freq(25000)
lcd_brightness.duty_u16(3000)

buzzer = PWM(Pin(3))
buzzer.freq(3000)
buzzer.duty_u16(65535)

com1 = Easy_comms(0,9600)

ex_opto1 = Pin(20, Pin.OUT) 
ex_opto2 = Pin(21, Pin.OUT)
ex_opto1(0)
ex_opto2(0)

opto1 = Pin(6, Pin.OUT)
opto2 = Pin(5, Pin.OUT)
opto3 = Pin(4, Pin.OUT)
opto4 = Pin(2, Pin.OUT)

opto1(0)
opto2(1)
opto3(1)
opto4(1)

def lcd_bright(source):
    global ambient_light  
    sample_brightness = [ldr_adc.read_u16() for _ in range(10)]
    ambient_light = (int(sum(sample_brightness)/10))
    lcd_brightness.duty_u16(ambient_light)
    
lcd_bright(0)
brightness_adj = Timer(period=100, mode=Timer.PERIODIC, callback=lcd_bright)


def led1blink():
    led1(1)
    time.sleep_ms(20)
    led1(0)

buzz = 0
led1blink()
#def callback(int_pin):
#global buzz
while True:
    message = com1.read()
    if message is not None:
        print(f'message: {message}')
        try:
            command = json.loads(message)
            print(f'json: {command}')
            led1blink()
            if command["A"] == "L1":
                opto1(0)
                opto2(1)
                opto3(1)
                opto4(1)
                
            if command['A'] == 'L2':
                opto2(0)
                opto1(1)
                opto3(1)
                opto4(1)
                
            if command['A'] == 'L3':
                opto3(0)
                opto1(1)
                opto2(1)
                opto4(1)
                
            if command['A'] == 'L4':
                opto4(0)
                opto1(1)
                opto2(1)
                opto3(1)
                
            if command['A'] == 'OC_OFF':
                ex_opto1(0)
                
            if command['A'] == 'OC_ON':
                ex_opto1(1)
                
            if command['A'] == 'buzz_1':
                buzz = 1
               
                
            if command['A'] == 'buzz_2':
                buzz = 2
                
                      
            if command['A'] == 'SHUTDOWN':
                print("shutting down")
                         
            if command['A'] == 'RESET':
                machine.reset()
                
        except Exception as e:
            pass
        led1blink()
        
#int_pin.irq(trigger=Pin.IRQ_RISING, handler=callback)


    