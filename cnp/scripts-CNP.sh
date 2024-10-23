
# let nm connect a predefined connection, here it's Ad Hoc connection
sudo nmcli c up ARC-test2

# add neighbor information
sudo ip neig add fe80::4140:2d2f:ff09:d36c lladdr 00:c3:16:a1:df:0a dev wlan1