n = 16 * 16

ws2812.init(ws2812.MODE_SINGLE)

-- black screen
buf = ws2812.newBuffer(n, 3)
buf:fill(23,23,23)
ws2812.write(buf)


s = net.createServer(net.UDP)
s:on("receive",function(s,c)
    universe = struct.unpack(">H", string.sub(c, 14, 16))
    if universe == 0 then
        buf:replace(string.sub(c, 19))
    elseif universe == 1 then
        buf:replace(string.sub(c, 19), 171)
    end

    ws2812.write(buf)
end)
s:listen(6454)
