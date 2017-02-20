Used:
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
