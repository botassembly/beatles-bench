# Jev header probe, 2026-09-23

Three live calls to Jev with one bench request (`body.json`), sent with curl under the ThinkThen spending guard at a load average near 440. `headers*.txt` hold the response headers, `resp*.json` the bodies, and `timing*.txt` curl's DNS, connect, TLS, first-byte, and total times. `x-envoy-upstream-service-time` is Jev's server time in milliseconds: 762, 997, and 65. The network added about 140 ms to each call.
