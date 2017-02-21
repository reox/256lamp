n = 16 * 16

ws2812.init(ws2812.MODE_SINGLE)

-- white screen
buf = ws2812.newBuffer(n, 3)
buf:fill(23,23,23)
ws2812.write(buf)


s = net.createServer(net.UDP)
s:on("receive",function(s,c)
    -- check for actual Art-Net\0 string:
    if string.sub(c, 1, 7) == "Art-Net" then
        -- thats interesting: we pack with LE and must unpack BE?
        universe = struct.unpack(">H", string.sub(c, 14, 16))
        -- length = struct.unpack("<H", string.sub(c, 16, 18))
        if universe == 0 then
            buf:replace(string.sub(c, 19))
        elseif universe == 1 then
            buf:replace(string.sub(c, 19), 171)
        elseif universe == 2 then
            -- "fake" zone, where we take only three lamps and replicate for all leds
            g,r,b = struct.unpack("BBB", string.sub(c, 19, 21))
            buf:fill(g,r,b)
        end

        ws2812.write(buf)
    end
end)
s:listen(6454)
