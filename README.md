# Smart-Bat

![PXL_20231012_155246602 NIGHT~2](https://github.com/supreeet/Smart-Bat/assets/117578605/c3b0216e-6c81-44da-8e9c-a7f24dcf5ddc)

# Design
## Body
- 3d printed PLA body
- 8 threaded inserts to hold battery pack, components module in place
- reinforcing carbon fibre rods glued with 2 part epoxy on bottom and back panel
- top cover is laser cut acrylic sheet held with 8 m3 screws (cover screw mounts are not visible in the following picture)
![PXL_20230427_144759748](https://github.com/supreeet/Smart-Bat/assets/117578605/0d0594ba-5732-4e7c-8b5e-9874ee02e547)

Features:
- 12.8v nominal 153 Watt hour lithium iron phosphate battery pack
- 0.96 inch 128x32 monochrome OLED ('SSD1306'), 1.3 inch 240x240 RGB LCD ('ST7789'), 1x joystick and 4x buttons for easy interaction
- Raspberry Pi Pico W microcontroller board with wifi and bluetooth
- 2x USB-C and 2x USB-A output port capable of outputting 72 Watts, supports PD, PPS, QC fast charging protocols
- 10w Qi wireless charger
- USB-C connector paired with CH224k USB-C sink controller and XT-60 connector for power input at upto 75w
- 19 addressable RGB lights ('WS2812b')
- TEMT6000 abient light sensor for automatic LCD brightness adjustment
- 1x XT-60 for direct battery voltage output at upto 256 Watts
- 1x XT-60 for charging external 4s lithium ion battery at upto 33 Watts
- 2x PWM controlled BLDC cooling fans
