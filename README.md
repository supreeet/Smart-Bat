# Smart-Bat

![PXL_20231012_155246602 NIGHT~2](https://github.com/supreeet/Smart-Bat/assets/117578605/c3b0216e-6c81-44da-8e9c-a7f24dcf5ddc)

# Design
Features:
- Lithium-ion battery pack capable of charging a regular phone 12x times
- can charge 5x devices and 1x 4s lithium battery simultaneously 
- USB-C and DC input port, can be fully charged in less than 3 hours
- coloured LCD with automatic brightness adjustment
- joystick and buttons for easy interaction
- can be wirelessly controlled with a phone or laptop via browser
- 3 lamp modes with different intensities
- over-temperature, over-current, short-circuit, over-voltage, under-voltage protection


Specs:
- 12.8v 153 Watt hour lithium iron phosphate ('LiFePo4') battery pack
- Raspberry Pi Pico W microcontroller board with wifi and bluetooth
- 2x USB-C and 2x USB-A ports capable of outputting 72 Watts combined, supports PD, PPS, QC fast charging protocols
- 10 Watt Qi wireless charger
- USB-C connector paired with CH224k PD sink controller and XT-60 connector for 16-40v input at upto 75 Watts
- 19 addressable RGB lights ('WS2812b')
- 1x XT-60 for direct battery voltage output at upto 256 Watts
- 1x XT-60 for charging external 4s lithium ion battery at upto 33 Watts
- 2x 5v cooling fans
- 4 automatic input charging modes 

![PXL_20230528_164307744](https://github.com/supreeet/Smart-Bat/assets/117578605/83f174b7-149f-46f5-9416-b6dc13038b5f)


## Body
- 3d printed PLA body, the front and back being seperate 3d prints
- 8 threaded inserts to hold battery pack, components module in place
- reinforcing carbon fibre rods glued with 2 part epoxy on bottom 
- top cover is laser cut acrylic sheet held with 8 m3 screws

![PXL_20230427_144759748](https://github.com/supreeet/Smart-Bat/assets/117578605/0d0594ba-5732-4e7c-8b5e-9874ee02e547)


## Components module
The components module consists of two voltage/current sensors from Texas Instruments ('INA219'), digital potentiometer, two dc-dc voltage regulators, 4x 20A Relays with a covering pcb on top 

![PXL_20230902_114550286](https://github.com/supreeet/Smart-Bat/assets/117578605/beb3b379-55a5-48b5-94d1-038cded38f5b)


## PCB
The [pcb](https://github.com/supreeet/Smart-Bat/tree/a5d27a213e3fed6b2bf3b1258488c426cedcd1ec/pcb) includes:
- Raspberry Pi Pico and Pico W
- 2x 5v dc-dc regulators
- 2x 4 pin fan connector
- monochrome OLED display
- CH224K USB-C sink controller

- 3x voltage divider circuits for ADC conversion
- 5x PNP transistor


## Display

![PXL_20231009_084727147 MP](https://github.com/supreeet/Smart-Bat/assets/117578605/2555a323-54d2-4e25-9476-a658eb287023)
- 0.96 inch 128x32 monochrome OLED ('SSD1306')

![PXL_20231016_141914945](https://github.com/supreeet/Smart-Bat/assets/117578605/89fad8a6-ba0c-4199-91aa-79aecf7d10f0)
- 1.3 inch 240x240 RGB LCD ('ST7789')
