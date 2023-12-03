from machine import Pin, PWM
from machine import ADC, I2C, Timer, reset, SoftSPI
from easy_comms import Easy_comms
import time, neopixel, json
from ssd1306 import SSD1306_I2C

fan1 = PWM(Pin(21))  #left
fan1.freq(25000)
fan1.duty_u16(5000)

fan2 = PWM(Pin(20))  #right
fan2.freq(25000)
fan2.duty_u16(5000)

buck_1 = Pin(18, Pin.OUT)     # Primary +5v
buck_2 = Pin(19, Pin.OUT)     # Secondary +5v

     
buck_1(0)
buck_2(0)

mcu2_en = Pin(22,Pin.OUT, Pin.PULL_DOWN)
mcu2_en(1)

dc_charge_current = 3   # target peak current for automatic charging from XT-60 port
pd_charge_current = 2   # target peak current for automatic charging from type C port

mcu2_on_time = time.ticks_ms()
manual_lfp_current = 2             # step for manual charging
lfp_automatic_charging = True      # False if current is changed or relay is switched manually 

relay1 = Pin(10, Pin.OUT)   # LFP charge
relay2 = Pin(13, Pin.OUT)   # Lipo charging
relay3 = Pin(12, Pin.OUT)   # Direct OUT
relay4 = Pin(11, Pin.OUT)   # USB OUT

relay1(1)           
relay2(1)
relay3(1)
relay4(1)

I2C = I2C(0, scl=Pin(17), sda=Pin(16))
I2C_devices = I2C.scan()
aht10_available = False
oled_available = False
ina1_available = False
ina1_available = False

for device in I2C_devices:
    if device == 56:
        aht10_available = True
        
    if device == 60:
        oled_available = True
        
    if device == 64:
        ina1_available = True
        
    if device == 65:
        ina2_available = True

WIDTH = 128
HEIGHT = 32
if oled_available == True:
    oled = SSD1306_I2C(WIDTH, HEIGHT, I2C)
    oled.fill(0)
    oled.text("HELLO", 40, 10)
    oled.show()

import st7789py as st7789
from fonts import vga1_16x32 as font1
import  ahtx0, _thread, network, socket, framebuf
from ina219 import INA219
from ina219 import DeviceRangeError

np = neopixel.NeoPixel(Pin(7), 19)
for i in range(19):
    np[i] = (0,0,0)
np.write()
led_ = 0     # current led mode 

keyA = Pin(2, Pin.IN, Pin.PULL_UP)
keyB = Pin(3,  Pin.IN, Pin.PULL_UP)
keyX = Pin(4, Pin.IN, Pin.PULL_UP)
keyY = Pin(5, Pin.IN, Pin.PULL_UP)

adc_0 = ADC(0)                    # KEYS ADC
adc_1 = ADC(1)                    # USB-C PD ADC
adc_2 = ADC(2)                    # XT-60 DC ADC
adc_4 = ADC(4)                    # RP2040 temp
keysvalue = adc_0.read_u16()

com1 = Easy_comms(0,9600)
int_pin = Pin(1,Pin.OUT, Pin.PULL_DOWN)

led_w = machine.Pin("LED", machine.Pin.OUT)
led_w.off()

SHUNT_OHMS1 = 0.005  
SHUNT_OHMS2 = 0.05

ina1 = INA219(SHUNT_OHMS1,I2C,address=0x40)
ina1.configure(ina1.RANGE_32V, ina1.GAIN_AUTO)

ina2 = INA219(SHUNT_OHMS2,I2C,address=0x41)
ina2.configure(ina2.RANGE_32V, ina2.GAIN_AUTO)
time.sleep_ms(20)

if aht10_available == True:
    sensor1 = ahtx0.AHT10(I2C)
    temp_bat = sensor1.temperature
    humidity = sensor1.relative_humidity
    print("%.2f" % temp_bat + "C" + " %.2f" % humidity + "H")
else:
    temp_bat = 0
    
wlan = network.WLAN(network.STA_IF)    
status = wlan.ifconfig()
wlan.active(False)

ssid1 = 'ssid1'
password1 = 'password1'
ssid2 = 'ssid2'
password2 = 'password2'

def wifi_on():
    wlan.active(True)
    
    search_item1 = b'ssid1'
    search_item2 = b'ssid2'
    data = wlan.scan()
    print(search_item1,data)
    found = False
    for item in data:
        if search_item1 in item:
            wifi_found = search_item1
            print( wifi_found + " found")
            found = True
            break
        if search_item2 in item:
            wifi_found = search_item2
            print( wifi_found + " found")
            found = True
            break
            
    if found:
        if wifi_found == search_item1:
            print(ssid1)
            wlan.connect(ssid1, password1)
        else:
            print(ssid2)
            wlan.connect(ssid2, password2)
    else:
        wlan.active(False)
        return
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        print('network connection failed')
        wlan.active(False)
        return
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print('listening on', addr)
#wifi_on()
    
def wifi_off():
    wlan.disconnect()
    wlan.active(False)
    print("wifi off")
    
def vin_check():
    global pd_vin, dc_vin, vin
    
    sample_pd = [adc_1.read_u16() for _ in range(20)]
    sample_dc = [adc_2.read_u16() for _ in range(20)]
    
    pd_vin = ((int(sum(sample_pd)/20))*3.3/65535)*70
    dc_vin = ((int(sum(sample_dc)/20))*3.3/65535)*70
    
    if dc_vin > pd_vin:
        vin = dc_vin
    else:
        vin = pd_vin
    if vin < 3.5:
        vin = 0

    #print("%.1f" % pd_vin, "%.1f" % dc_vin)

def ina_measure():
    global v1, v2, i_mA_1, p_mW_1, i_mA_2, p_mW_2, socp, chargep
    v1 = ina1.voltage()
    v2 = ina2.voltage()
    try:
        i_mA_1 = ina1.current()
        p_mW_1 = ina1.power()
        i_mA_2 = abs(ina2.current())
        p_mW_2 = ina2.power()
        socp = p_mW_1/10/3600
        
    except DeviceRangeError as e:
        print(e)
ina_measure()

full_battery_capacity = 148000    # in Wh
with open("soc.txt", "r") as file:
    soc = float(str(file.read()))
    print("%.1f" % (soc/(full_battery_capacity/100)) + '%')

if v1 < 11:
    soc = 0
    with open("soc.txt", "w") as file:
        file.write(str(soc))
        
last_soc_save = time.ticks_ms()


def lfpcharging(x):
    global lfpspeed
    lfpspeed = x
    if x == 1:                                 #slowest
        command = {'A': 'L1'}         
        com1.send(str(json.dumps(command)))
    if x == 2:
        command = {'A': 'L2'}
        com1.send(str(json.dumps(command)))
    if x == 3:
        command = {'A': 'L3'}
        com1.send(str(json.dumps(command)))
    if x == 4:                                 #fastest
        command = {'A': 'L4'}
        com1.send(str(json.dumps(command)))
lfpspeed = 1


softstart_last_step_time = time.ticks_ms()
softstart_step = 1
softstart_flag = False
softstart_stage = 1

def softstart():
    global pd_vin, dc_vin, lfpspeed, softstart_step, softstart_last_step_time, softstart_flag, softstart_stage, target_current
    if softstart_stage == 1:
        if time.ticks_diff(time.ticks_ms(), softstart_last_step_time)>500:
            if softstart_step == 1:
                command = {'A': 'OC_OFF'}         
                com1.send(str(json.dumps(command)))
                softstart_step = 2
                softstart_last_step_time = time.ticks_ms()
                return
        
            if softstart_step == 2:
                lfpcharging(1)
                softstart_step = 3
                softstart_last_step_time = time.ticks_ms()
                return
            
            if softstart_step == 3:
                relay1(0)
                softstart_step = 4
                softstart_last_step_time = time.ticks_ms()
                return
            
            if softstart_step == 4:
                command = {'A': 'OC_ON'}         
                com1.send(str(json.dumps(command)))
                softstart_step = 1
                softstart_stage = 2
                softstart_last_step_time = time.ticks_ms()
                return
        
    elif softstart_stage == 2:
        if time.ticks_diff(time.ticks_ms(), softstart_last_step_time)>1000:
            battery_percent = 100*(soc/full_battery_capacity)
            if pd_vin > dc_vin:
                if pd_charge_current == 1:
                    target_current = 1
                    
                if pd_charge_current == 2:
                    target_current = 2
                    
                if pd_charge_current == 3:  
                    if 20 < battery_percent < 80:   
                        target_current = 3
                    else:
                        target_current = 2
                
                if pd_charge_current == 4:
                    if 10 < battery_current < 90:
                        target_current = 4
                    else:
                        target_current = 3

            else:
                if dc_charge_current == 1:
                    target_current = 1
                    
                if dc_charge_current == 2:
                    target_current = 2

                if dc_charge_current == 3:
                    if 10 < battery_percent < 90:   
                        target_current = 3
                    else:
                        target_current = 2
            
                if dc_charge_current == 4:
                    if 20 < battery_current < 80:
                        target_current = 4
                    else:
                        target_current = 3

            if lfpspeed == target_current:
                return
            
            if lfpspeed < target_current:
                lfpcharging(lfpspeed + 1)
                
            if lfpspeed > target_current:
                lfpcharging(lfpspeed - 1)
            
            softstart_last_step_time = time.ticks_ms()
            
                
                
   
def charging_check():
    global v1, v2, soc, auto_current_set, softstart_flag, last_event_time, softstart_step, softstart_stage

    # LFP
    if lfp_automatic_charging == True:
        if relay1()==0:    # turn off charging
            if vin < 14:
                last_event_time = time.ticks_ms()
                softstart_flag = False
                softstart_step = 1
                softstart_stage = 1
                softstart_last_step_time = time.ticks_ms()
                relay1(1)
                mcu2_en(1)
    
    
        if relay1()==1 and softstart_flag == False:  # turn on charging
            if soc < full_battery_capacity*0.98:
                if vin > 14:
                    if mcu2_en()==1:
                        mcu2_en(0)
                        time.sleep_ms(300)
                    softstart_flag = True
                    print("charging")
                    
                    
                    
    if relay1() == 0:    # battery fully charged
        if v1 > 14.3:        
            if relay1() == 0:
                if v1 > 14.3:
                    if i_mA_1 < 50:
                        soc = full_battery_capacity
                        print("battery fully charged")
                        relay1(1)
                        command = {'A': 'OC_OFF'}         
                        com1.send(str(json.dumps(command)))
                        softstart_last_step_time = time.ticks_ms()
                        softstart_flag = False
                        softstart_stage = 1
                        softstart_step = 1
        

    # Lipo
    if relay2()==0:
        if v2 > 16.65:
            time.sleep_ms(10)
            v2 = ina2.voltage()
            if v2 > 16.6:
                if i_mA_2 < 100:
                    print("lipo charged")
                    relay2(1)

start2 = time.ticks_ms()
def joystick_check():
    global lfpspeed, shutdown, start2, led_, fan_1_extra, fan_2_extra, lfp_automatic_charging, manual_lfp_current, softstart_flag, softstart_stage, softstart_step, last_event_time
    keysvalue = adc_0.read_u16()
    if 14500 < keysvalue < 16000:     # Up
        delta2 = time.ticks_diff(time.ticks_ms(), start2)
        if delta2 > 200:
            led_w.on()
            time.sleep_ms(25)
            led_w.off()
            if led_==0:
                for i in range(19):
                    np[i] = (10,8,3)
                np.write()
                led_=1
                
            elif led_==1:
                for i in range(19):
                    np[i] = (120,108,55)
                np.write()
                led_=2    
                
            elif led_==2:
                for i in range(19):
                    np[i] = (253, 240, 135)
                np.write()
                led_=3
            elif led_ == 3:
                led_ = 4
            
            else:
                for i in range(19):
                    np[i] = (0,0,0)
                np.write()
                led_=0
        start2 = time.ticks_ms()
        
    if 29200 < keysvalue < 30500:     # Down
        delta2 = time.ticks_diff(time.ticks_ms(), start2)
        if delta2 < 200:
            return
        last_event_time = time.ticks_ms()
        if mcu2_en()==1:
            mcu2_en(0)
            time.sleep_ms(100)
            start2 = time.ticks_ms()
            return
        if lfp_automatic_charging == True:
            relay1(1)
            softstart_flag = False
            softstart_stage = 1
            softstart_step = 1
            lfp_automatic_charging = False
        
        if mcu2_en()==0 :
            led_w.on()
            time.sleep_ms(30)
            led_w.off()
            
            if manual_lfp_current == 1:
                command = {'A': 'OC_OFF'}         
                com1.send(str(json.dumps(command)))
                start2 = time.ticks_ms()
                manual_lfp_current = 2

            elif manual_lfp_current == 2:
                lfpcharging(1)
                start2 = time.ticks_ms()
                manual_lfp_current = 3

            elif manual_lfp_current == 3:
                command = {'A': 'OC_ON'}         
                com1.send(str(json.dumps(command)))
                start2 = time.ticks_ms()
                manual_lfp_current = 4

            else:
                lfpcharging(manual_lfp_current - 2)
                start2 = time.ticks_ms()
                
                if manual_lfp_current == 6:
                    manual_lfp_current = 1
                else:
                    manual_lfp_current = manual_lfp_current + 1
                        
            start2 = time.ticks_ms()
        
    if 37900 < keysvalue < 39000:     # Left
        delta2 = time.ticks_diff(time.ticks_ms(), start2)
        if delta2 > 200:
            led_w.on()
            time.sleep_ms(25)
            led_w.off()
            
            print("LEFT")
            if fan_1_extra == 0:
                fan_1_extra = 2
            elif fan_1_extra == 2:
                fan_1_extra = 4
            elif fan_1_extra == 4:
                fan_1_extra = 6
            else:
                fan_1_extra = 0
        start2 = time.ticks_ms()
    
    if 23500 < keysvalue < 24500:    # Right
        delta2 = time.ticks_diff(time.ticks_ms(), start2)
        if delta2 > 200:
            led_w.on()
            time.sleep_ms(25)
            led_w.off()
            
            print("RIGHT")
            if fan_2_extra == 0:
                fan_2_extra = 2
            elif fan_2_extra == 2:
                fan_2_extra = 4
            elif fan_2_extra == 4:
                fan_2_extra = 6
            else:
                fan_2_extra = 0
                
        start2 = time.ticks_ms()
    
    if 8000 < keysvalue < 9000:       # ctrl
        delta2 = time.ticks_diff(time.ticks_ms(), start2)
        if delta2 > 200:
            print("CTRL")
        start2 = time.ticks_ms()
        

lipo_soc = 0        
x_5 = 0    
def soc_calculation(source):
    global soc, v1, i_mA_1, i_A_1, p_mW_1, p_W_1, v2, i_mA_2, i_A_2, p_mW_2, p_W_2, lipo_safe, lipo_soc, x_5, last_soc_save
    joystick_check()
    
    i_A_1 = i_mA_1/1000
    i_A_2 = i_mA_2/1000
    p_W_1 = p_mW_1/1000
    p_W_2 = p_mW_2/1000
    
    if x_5 == 5:
        x_5 = 0
        
        ina_measure()
        lipo_soc = lipo_soc + (p_mW_2/10/3600)
                           
        if i_mA_1>0.02:
            soc = soc + 0.932*socp
            
        if i_mA_1<-0.02:
            soc = soc - socp    
    x_5 = x_5 + 1
    
    if time.ticks_diff(time.ticks_ms(), last_soc_save)>300000:
        with open("soc.txt", "w") as file:
            file.write(str(soc))
        last_soc_save = time.ticks_ms()
        
soc_timer = Timer(period=20, mode=Timer.PERIODIC, callback=soc_calculation)

tft = st7789.ST7789(SoftSPI(polarity=1, sck=Pin(14), mosi=Pin(15), miso = Pin(6)), 240,240,reset=Pin(8, Pin.OUT),dc=Pin(9, Pin.OUT),rotation=1)

green_1 = st7789.color565(0, 255, 0)
orange_1 = st7789.color565(220, 255, 0)
red_1 = st7789.color565(255, 0, 0)
cyan_1 = st7789.color565(0, 255, 255)
golden_1 = st7789.color565(200, 200, 0)
white_1 = st7789.color565(255, 255, 255)

def key_A_handler():
    global shutdown
    shutdown = True

def key_B_handler():
    pass

def key_X_handler():
    pass

def key_Y_handler():
    pass

button_debounce_timer = time.ticks_ms()
def keyA_callback(pin):
    global button_debounce_timer, last_event_time
    last_event_time = time.ticks_ms()
    if time.ticks_diff(time.ticks_ms(), button_debounce_timer) < 200:
        return
    key_A_handler()
    
keyA.irq(trigger=Pin.IRQ_FALLING, handler=keyA_callback)

def keyB_callback(pin):
    global button_debounce_timer, last_event_time
    last_event_time = time.ticks_ms()
    if time.ticks_diff(time.ticks_ms(), button_debounce_timer) < 200:
        return
    time.sleep_ms(5)
    button_time = time.ticks_ms()
    while True:
        x = time.ticks_diff(time.ticks_ms(), button_time)
        if x > 4000:
            return
        if keyB()==1:
            break
    if x < 2:
        return
    
    if wlan.active()==False:
        wifi_on()
    else:
        wifi_off()
        
    key_B_handler()
    button_debounce_timer = time.ticks_ms()
    
keyB.irq(trigger=Pin.IRQ_FALLING, handler=keyB_callback)
 
def keyX_callback(pin):
    global button_debounce_timer, last_event_time, lfp_automatic_charging
    last_event_time = time.ticks_ms()
    if time.ticks_diff(time.ticks_ms(), button_debounce_timer) < 200:
        return
    time.sleep_ms(5)
    button_time = time.ticks_ms()
    lipo_flag = False
    while True:
        x = time.ticks_diff(time.ticks_ms(), button_time)
        if x > 4000:
            if relay2() == 0:
                relay2(1)
            return
        
        if lipo_flag==False:
            if x > 1000:
                print("LFP")
                lfp_automatic_charging = False
                if relay1() == 1:
                    relay1(0)
                elif relay1() == 0:
                    relay1(1)
                lipo_flag = True
                
        if keyX()==1:
            break
        
    if x < 2:
        return
    
    if x < 1000:
        print("Lipo")
        if relay2() == 1:
            relay2(0)
        elif relay2() == 0:
            relay2(1)         
    button_debounce_timer = time.ticks_ms()
    
keyX.irq(trigger=Pin.IRQ_FALLING, handler=keyX_callback)
def keyY_callback(pin):
    global button_debounce_timer, last_event_time
    last_event_time = time.ticks_ms()
    if time.ticks_diff(time.ticks_ms(), button_debounce_timer) < 200:
        return
    time.sleep_ms(5)
    button_time = time.ticks_ms()
    dc_flag = False
    while True:
        x = time.ticks_diff(time.ticks_ms(), button_time)
        if x > 4000:
            if relay3() == 0:
                relay3(1)
            return
        
        if dc_flag==False:
            if x > 1000:
                print("DC")
                if relay3() == 1:
                    relay3(0)
                elif relay3() == 0:
                    relay3(1)
                dc_flag = True
                
        if keyY()==1:
            break
    
    if x < 2:
        return
    
    if x < 1000:
        print("usb")
        if relay4() == 1:
            relay4(0)
        elif relay4() == 0:
            relay4(1)
            
    button_debounce_timer = time.ticks_ms()
    
keyY.irq(trigger=Pin.IRQ_FALLING, handler=keyY_callback)

fan_1_extra = 0
fan_2_extra = 0

def fan_speed_update():
    global fan_1_extra, fan_2_extra
    
    if relay2()==1:
        fan_1_counter = fan_1_extra
    else:
        fan_1_counter = fan_1_extra + 3
        
    if relay1()==1:
        fan_2_counter = fan_2_extra
    else:
        fan_2_counter = fan_2_extra + lfpspeed
           
    if fan_1_counter != 0:
        if fan_1_counter == 1:
            fan1.duty_u16(7000)
        if fan_1_counter == 2:
            fan1.duty_u16(14000)
        if fan_1_counter == 3:
            fan1.duty_u16(22000)
        if fan_1_counter == 4:
            fan1.duty_u16(30000)
        if fan_1_counter > 4:
            fan1.duty_u16(65000)
    else:
        fan1.duty_u16(0)
        
    if fan_2_counter != 0:
        if fan_2_counter == 1:
            fan2.duty_u16(7000)
        if fan_2_counter == 2:
            fan2.duty_u16(14000) 
        if fan_2_counter == 3:
            fan2.duty_u16(22000)
        if fan_2_counter == 4:
            fan2.duty_u16(30000)
            
        if fan_2_counter > 4:
            fan2.duty_u16(65000)
    else:
        fan2.duty_u16(0)
       
       
    if fan_1_counter==0 and fan_2_counter==0:
        buck_2(0)
    else:
        buck_2(1)

last_event_time = time.ticks_ms()
def automatic_shutdown():
    global last_event_time, shutdown, led_, soc
    if relay1()==1 and relay2()==1 and relay3()==1 and relay4()==1:
        if led_ == 0:
            if soc > 44400:
                if time.ticks_diff(time.ticks_ms(), last_event_time) > 120000:
                    shutdown = True
            else:
                if time.ticks_diff(time.ticks_ms(), last_event_time) > 30000:
                    shutdown = True

tft_3_time = time.ticks_ms()
tft_3_part = 1
lcd_refresh_part = 1
def display():
    global lcd_refresh_part, tft_3_time, tft_3_part
    
    if i_mA_1 > 0:
        ind_pwr_1 = ("+")
    else:
        ind_pwr_1 = ("-")
    if p_mW_1 < 100:
        z4 = str(ind_pwr_1 + "%.0f" % p_mW_1 + "mW")
    else:
        z4 = str(ind_pwr_1 + "%.1f" % p_W_1 + "W")
        
    if i_mA_2 > 99:
        a20 = str("%.1f" % i_A_2 + "A ")   
    elif i_mA_2 < 100:
        a20 = str("%.0f" % i_mA_2 + "mA  ")
        
    lipo_wh = str("%.1f" % (lipo_soc/1000) + "Wh")


    #lcd
    if lcd_refresh_part == 1:
        if soc > 118400:
            tft.text(font1, battery_percent + " ", 5, 5, green_1)
        if 118400 > soc > 44400:
            tft.text(font1, battery_percent + " ", 5, 5, orange_1)
        if soc < 44400:
            tft.text(font1, battery_percent + " ", 5, 5, red_1)
        
        if temp_bat < 45:
            tft.text(font1, str(" %.0f" % temp_bat + "C "), 125, 5, cyan_1)
        else:
            tft.text(font1, str(" %.0f" % temp_bat + "C "), 125, 5, orange_1)

    if lcd_refresh_part == 2:
        if lfp_automatic_charging == False:
            tft_B2 = "M" + str(lfpspeed)
        else:
            if pd_vin > dc_vin and relay1()==0:
                tft_B2 = "A" + str(pd_charge_current)
            else:
                tft_B2 = "A" + str(dc_charge_current)
        
        tft.text(font1, tft_B2,145,38, golden_1)
        
        if vin > 3:
            if pd_vin > dc_vin:
                tft.text(font1, str("PD: " + "%.0f" % vin), 10, 38, golden_1)
            else:
                tft.text(font1, str("DC: " + "%.0f" % vin), 10, 38, golden_1)
        else:
            tft.text(font1, str("VIN:0"), 10, 38, golden_1)
        tft.hline(0, 75, 240, white_1)   
        
    if lcd_refresh_part == 3:
        if v2 > 3:
            if time.ticks_diff(time.ticks_ms(), tft_3_time)>5000:
                if tft_3_part == 1:
                    tft_3_part = 2
                else:
                    tft_3_part = 1
                tft_3_time = time.ticks_ms()
                
            if tft_3_part == 1:
                tft.text(font1, str("%.1fv  " %  v2 + a20), 13, 85, orange_1)
                tft_3_part = 2
            else:
                tft.text(font1, str("%.0fWh  " % lipo_soc + "%.1fW " % p_W_2), 13, 85, orange_1)
                tft_3_part = 1
                
                
    if lcd_refresh_part == 4:
        if buck_2()==1:
            #fan 1
            if fan_1_extra < 1:
                tft_f1 = '0%'
                
            if 0 < fan_1_extra < 3:
                tft_f1 = '30%'
                
            if 2 < fan_1_extra < 5:
                tft_f1 = '70%'
                
            if 4 < fan_1_extra:
                tft_f1 = '100%'
            
            #fan 2
            if fan_2_extra < 1:
                tft_f2 = '0%'
                
            if 0 < fan_2_extra < 3:
                tft_f2 = '30%'
                
            if 2 < fan_2_extra < 5:
                tft_f2 = '70%'
                
            if 4 < fan_2_extra:
                tft_f2 = '100%'
                
            tft.text(font1, str('F1:' + tft_f1 + ' 2:' + tft_f2 + '  '), 10, 120, cyan_1)
        else:
            tft.text(font1, str('               '), 0, 120, cyan_1)
    if lcd_refresh_part == 5:
        pass
    
    if lcd_refresh_part == 6:
        if wlan.active() == True:
            if wlan.status() == 3:
                tft.text(font1, str(status[0]), 5, 165)
        else:
            tft.text(font1, str("               "), 5, 200)
            
        tft.hline(0, 160, 240, white_1)
        
    if lcd_refresh_part < 6:
        lcd_refresh_part += 1
    else:
        lcd_refresh_part = 1
    
    
    #oled
    if oled_available == True:
        oled.fill(0)
        # Row 1
        if pd_vin > dc_vin:
            oled.text(str("PD: " + "%.0f" % vin), 0, 0)
        else:
            oled.text(str("DC: " + "%.0f" % vin), 0, 0)
        
        # Row 2
        oled.text(battery_percent, 0, 10)
        oled.text(str("%.1f" % v1 + "v"), 45, 10)
        oled.text(z4, 65, 0)
        oled.text(str("%.0f" % temp_bat + "C"), 90, 10)
        
        if v2 > 3:
            oled.text("%.1f" % v2 + "v", 0, 20)
            oled.text(a20, 45, 20)
            oled.text(lipo_wh, 90, 20)
        else:
            oled.text("             " , 0, 20)
        oled.show()
       


shutdown = False  
while True:
    if softstart_flag == True:
        softstart()
        
    fan_speed_update()
    vin_check()
    charging_check()
    
    battery_percent = str("%.1f" % (soc/full_battery_capacity*100) + "%")
    if aht10_available == True:
        temp_bat = sensor1.temperature
        if temp_bat > 65:
            shutdown = True
    
    display()   
    
    #automatic_shutdown()
    if shutdown == True:
        print("shutting down")
        break
    

keyA.irq(handler=None)
keyB.irq(handler=None)
keyX.irq(handler=None)
keyY.irq(handler=None)

relay1(1)
time.sleep_ms(20)
relay2(1)
time.sleep_ms(20)
relay3(1)
time.sleep_ms(20)
relay4(1)

soc_timer.deinit()
buck_2(0)
mcu2_en(1)

with open("soc.txt", "w") as file:
    file.write(str(soc))
    print("soc saved")
time.sleep_ms(200)
buck_1(1)
time.sleep_ms(100)
if oled_available == True:
    oled.fill(0)
    oled.text("OFF", 35, 13)
    oled.text(battery_percent, 35, 0)
    oled.show()

while True:
    vin_check()
    if keyA()==0:
       time.sleep_ms(20)
       if keyA()==0:
           machine.reset()
    time.sleep_ms(20)
