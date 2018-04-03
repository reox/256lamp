#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2017 Sebastian Bachmann
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import socket
import time
from struct import pack
from PIL import Image
import os
from itertools import chain
import sys
from colortemp import colortemp


def wheel(pos):
    pos = 255 - pos
    if pos < 85:
        return [(255 - pos * 3) & 0xFF, 0, (pos * 3) & 0xFF]
    elif pos < 170:
        pos -= 85
        return [0, (pos * 3) & 0xFF, (255 - pos * 3) & 0xff]
    else:
        pos -= 170
        return [(pos * 3) & 0xff, (255 - pos * 3) & 0xff, 0]


def rearange(buf):
    """
    Rearanges the buffer from an x,y image to the actual pixel position
    """

    # buf will be an bytearray with length x*y and contains tuple with 3 items

    # Need to put all columns from 8 to 15 at the end
    #
    # And swap every second line
    nbuf = []
    for c, i in enumerate(list(range(0, 256, 16)) + list(range(8, 256, 16))):
        line = buf[i:i + 8]
        if c % 2 == 1:
            line = line[::-1]
        nbuf += line

    return bytearray([item for sublist in nbuf for item in sublist])


def imageToBuffer(fname):
    im = Image.open(fname)
    pix = list(im.getdata())
    if len(pix[0]) == 4:
        pix = [(b,g,r) for r,g,b,a in pix]
    else:
        pix = [(b,g,r) for r,g,b in pix]

    if len(pix) != 256:
        return bytearray([0] * 768)

    return rearange(pix)


class ArtNet(object):
    def __init__(self, dst="255.255.255.255", port=0x1936, brightness=6, controlb=True):
        """
            Brightness: parameter from 0 to 8. 0 ...  always off, 8 ... full brightness
            controlb: if brightness should be controlled
        """
        self.seq = 0
        self.dst = dst
        self.port = port
        self.brightness = 8 - brightness
        self.controlb = controlb
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

        #                    Protocol name               DMX         Version   Seq   Phy
        self.hdr = bytearray(b'Art-Net\x00') + bytearray([0, 0x50] + [0, 14])

    def _send(self, universe, buf):
        self.sock.sendto(self.hdr + pack(">B", self.seq) + b'\x00' + pack("<H", universe) + pack(">H", len(buf)) + buf, (self.dst, self.port))
        self.seq = (self.seq + 1) % 256

    def send(self, buf):
        # 170 LEDs per universe --> 510 channels
        # need to address 256 leds...

        # Apply brightness:
        if self.controlb:
            buf = bytearray(map(lambda x: x >> self.brightness, buf))

        self._send(0, buf[:510])
        self._send(1, buf[510:])

    def sendSingle(self, r, g, b):
        """
            Sends a single RGB color for all LEDs
            using Universe 2 - which maps a single value to all LEDs

            WS2812 are BGR
        """
        self._send(2, bytearray([b, g, r]))



if __name__ == "__main__":
    # NOTE: Artnet supports only 512 light values per universe.
    # Therefore we should in practise use two universes and parse the header...

    art = ArtNet(dst="172.16.23.132", controlb=False)
    pos = 0
    #while True:
    #   pos += 1
    #   pos = pos % 256
    #   a.send(bytearray(map(lambda x: x >> 4, bytearray(wheel(pos) * 256))))
    #   time.sleep(0.05)

    for f in os.listdir("foo/assets/minecraft/textures/blocks"):
        if f.endswith(".png"):
            try:
                fname = os.path.join("foo/assets/minecraft/textures/blocks", f)
                buf = imageToBuffer(fname)
    
                art.send(buf)
                time.sleep(1)
            except:
                pass
    
    art.send(imageToBuffer(sys.argv[1]))
    

    art.sendSingle(0x7F, 0xFF, 0x00)

    time.sleep(10)

    for i in range(2000, 10000, 100):
        print("Sending {}: {}".format(i, colortemp(i)))
        art.sendSingle(*colortemp(i))
        time.sleep(0.05)

    time.sleep(10)


    x = range(256)
    for i in range(256 * 256):
        buf = list(map(lambda x: wheel(x), x))
        buf = rearange(buf)
        art.send(buf)
        time.sleep(0.05)
        x = map(lambda x: (x+1) % 256, x)
