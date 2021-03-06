-- MIT License
--
-- Copyright (c) 2017 Sebastian Bachmann
--
-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-- SOFTWARE.

n = 16 * 16

ws2812.init(ws2812.MODE_SINGLE)

-- white screen
buf = ws2812.newBuffer(n, 3)
buf:fill(0,0,0)
ws2812.write(buf)
-- should be blue
buf:fill(255,0,0)
ws2812.write(buf)

-- should be green
buf:fill(0,255,0)
ws2812.write(buf)

-- should be red
buf:fill(0,0,255)
ws2812.write(buf)

-- should be white
buf:fill(23,23,23)
ws2812.write(buf)

s = net.createServer(net.UDP)
s:on("receive",function(s,c)
    -- in lua: sub(c, start, end) counts from 1 and includes char at end!
    -- check for actual Art-Net\0 string:
    if string.sub(c, 1, 7) == "Art-Net" then
        universe = struct.unpack("<H", string.sub(c, 15, 16))
        -- length = struct.unpack(">H", string.sub(c, 17, 18))
        if universe == 0 then
            buf:replace(string.sub(c, 19))
        elseif universe == 1 then
            buf:replace(string.sub(c, 19), 171)
        elseif universe == 2 then
            -- "fake" zone, where we take only three lamps and replicate for all leds
            b, g, r = struct.unpack("BBB", string.sub(c, 19, 21))
            buf:fill(b, g, r)
        end

        ws2812.write(buf)
    end
end)
s:listen(6454)
