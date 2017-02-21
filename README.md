## Software
```
NodeMCU custom build by frightanic.com
        branch: master
        commit: b96e31477ca1e207aa1c0cdc334539b1f7d3a7f0
        SSL: false
        modules: file,gpio,net,node,struct,tmr,uart,wifi,ws2812
 build  built on: 2017-02-19 19:16
 powered by Lua 5.1.4 on SDK 2.0.0(656edbf)
```

Upload `init.lua`, `lampe.lua`, create `credentials.lua` (for your wifi).

Use `send.py` to send ARTnet stuff.
Beware: the protocol handling is a little bit fake, as we do not actually parse the whole protocol but make some assumptions...

## Android
I did not found good Apps for controlling the Device using Android, only [Artnetcontroller](https://sites.google.com/site/artnetcontroller/) seems to work quite fine, but has a super-complicated UI... (It can probably do much more stuff than needed.)

The idea is to have each pixel configureable by using the Universes 0 and 1 (0 --> LEDs 1 ... 170, 1 --> LEDs 171 ... 256) and provide an extra universe 2, where a single RGB value is send to the lamp and filled for all LEDs.
With this setting, one can use ArtNetController app, use 3 channels in universe 2 and set the whished color for the whole lamp.

## Schematic

Connect `GPIO0` to `DIN` of the LED panel and connect the `GND` of the data cable of the leds with the `GND` of the ESP.

## TODO

* If the LEDs are not connected while the ESP boots up, it will be in a boot loop because `GPIO0` is also used as the Flash enable pin...
* the ESP has only 3.3V TTL, where the WS2812 uses 5V TTL... A logic level converter would probably be nice
* More ArtNet protocol parsing. Do not rely on "we will send it correctly"... The ESP crashes if something is no bueno.
* Fix wifi startup / LED initialization: It is probably good to initialize the LEDs as early as possible and restore the last state or something.
* If you want to use QLC+, there might be some problems with addressing the Panels correctly... Maybe it is a good idea to address each single 8x8 panel by a single universe.
