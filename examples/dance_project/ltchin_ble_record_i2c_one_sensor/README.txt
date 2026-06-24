Open main.html for the javascript version or ble_i2c_client_CU_onesensor.py for the Python version.


# File description:
* main.html -- the main GUI to open in a browser
* record.js -- the actual logic to connect to the ESP32 and graph data in main.html
* p5.ble.js and p5.ble.min.js -- a WebBluetooth library (https://itpnyu.github.io/p5ble-website/) . A bit black box so would be open to using a different library
* chart.js -- library we use to generate the graph (https://www.chartjs.org/)

* ble_i2c_client_CU_onesensor.py -- a Python version to connect to the ESP32 instead. Relies on bleak (https://github.com/hbldh/bleak) which relies on your Windows computer having the correct drivers setup (WinRT). I found this much flakier than the web version 


# Important Windows Configuration

https://www.reddit.com/r/ZephyrusG14/comments/xa7co7/fixed_bluetooth_devices_randomly_disconnect_and/

^^ Windows 11 will shut down the Bluetooth Radio to save power
You need to turn off the setting so that you can reliably connect to the peripheral device

``` If you're on Windows 11 and also dealing with this, the fix is easy:

Open Device Manager
Expand the "Bluetooth" entry & find your adapter (e.g. "MediaTek Bluetooth Adapter")
Right-click on your adapter (e.g. "MediaTek Bluetooth Adapter") select "Properties" and click the "Power Management" tab
De-select "Allow the computer to turn off this device to save power" & click "OK"
OPTIONAL:

Open Services
Find Bluetooth Support Service
Make sure the Startup type is Automatic```