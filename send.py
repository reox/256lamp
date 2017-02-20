import socket
import time
from struct import pack
from PIL import Image
import os
from itertools import chain
import sys


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
    for c, i in enumerate(range(0, 256, 16) + range(8, 256, 16)):
        line = buf[i:i + 8]
        if c % 2 == 1:
            line = line[::-1]
        nbuf += line

    return bytearray([item for sublist in nbuf for item in sublist])


def imageToBuffer(fname):
    im = Image.open(fname)
    pix = list(im.getdata())
    if len(pix[0]) == 4:
        pix = [(g,r,b) for r,g,b,a in pix]
    else:
        pix = [(g,r,b) for r,g,b in pix]

    if len(pix) != 256:
        return bytearray([0] * 768)

    return rearange(pix)


class ArtNet(object):
    def __init__(self, dst="255.255.255.255", port=0x1936, brightness=8, controlb=True):
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

    def send(self, buf):
        # 170 LEDs per universe --> 510 channels
        # need to address 256 leds...

        # Apply brightness:
        if self.controlb:
            buf = bytearray(map(lambda x: x >> self.brightness, buf))

        #               Protocol name                            DMX         Version   Seq   Phy
        hdr = bytearray(['A', 'r', 't', '-', 'N', 'e', 't', 0] + [0, 0x50] + [0, 14])
        self.sock.sendto(hdr + pack(">B", self.seq) + b'\x00' + pack("<H", 0) + pack(">H", 510) + buf[:510], (self.dst, self.port))
        self.seq = (self.seq + 1) % 256
        self.sock.sendto(hdr + pack(">B", self.seq) + b'\x00' + pack("<H", 1) + pack(">H", 258) + buf[510:], (self.dst, self.port))
        self.seq = (self.seq + 1) % 256


# NOTE: Artnet supports only 512 light values per universe.
# Therefore we should in practise use two universes and parse the header...

art = ArtNet(dst="172.16.23.132")
pos = 0
#while True:
#    pos += 1
#    pos = pos % 256
#    a.send(bytearray(map(lambda x: x >> 4, bytearray(wheel(pos) * 256))))
#    time.sleep(0.05)

# for f in os.listdir("foo/assets/minecraft/textures/blocks"):
#     if f.endswith(".png"):
#         try:
#             fname = os.path.join("foo/assets/minecraft/textures/blocks", f)
#             buf = imageToBuffer(fname)
# 
#             art.send(buf)
#             time.sleep(1)
#         except:
#             pass

art.send(imageToBuffer(sys.argv[1]))


x = range(256)
for i in range(256 * 256):
    buf = map(lambda x: wheel(x), x)
    buf = rearange(buf)
    art.send(buf)
    x = map(lambda x: (x+1) % 256, x)
