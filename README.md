# raspberry_python_wifi
Scan and connect to a wifi hot spot using Python on a Raspberry pi (or over Linux distri)

This is a simple librarie to find the best hotspots that is a list and to connect to any hotspot using WPA security

It's using Linux cli via popen commands (so it is not compatible with Microsoft OS)

It just needs sys, os, functools ans time libraries

You can use it with "import" or executing it to make some tests

- Usage 1 : You have 3 Hot post : SSID1, SSID2 and SSID3 and you want to known wich is actually offering the best quality (with a minimum quality of 10 %)
            BESTWIFI=ChooseWifiHotSpot("wlan0",10,mywifihotspot=['SSID1','SSID2','SSID3'])
            BESTWIFI will be a string containing SSID with best quality

- USage 2 : connecting to a hotspot using WPA that you know SSID and Passphrase :
            IP=ConnectWifi("FR","wlan0","MY_SSID","MY_PASSPHRASE")
            The librarie will execute severals commands lines printing them at each step
            It will make a wpa_supplicant.conf file, ask to connect to the hotspot cia wpa_cli
            Check that the connexion is successfull  using wpa_state (and wiating while wpa_state is "SCANNING") util success or getting a timeout
            Then get check that you got an ipv4 and print it
  


