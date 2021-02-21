# CO<sub>2</sub> Logger

Simple CO<sub>2</sub> logger written in MicroPython that broadcasts CO<sub>2</sub>, temperature and humidity measurements over mqtt (e.g. to HomeAssistant). It also features a display to show the measurments and a buzzer to signal acoustically when a CO<sub>2</sub> threshold ist exceeded.

## Bill of materials

| Qty  | Name / Description                     |
| ---- | -------------------------------------- |
| 1    | LOLIN D1 mini (or similar esp8266 MCU) |
| 1    | Sensirion SCD30 CO<sub>2</sub> sensor  |
| 1    | 0.66" OLED display (64x48 pixel)       |
| 1    | 5V active buzzer                       |
| 1    | 4 pin micro push button                |

## Assembled Logger with display

![back](https://github.com/crehmann/CO2Logger/raw/main/assets/IMG_1424.jpg)

![front](https://github.com/crehmann/CO2Logger/raw/main/assets/IMG_1425.jpg)

<center>(the mesh comes from an old kitchen sieve)</center>
