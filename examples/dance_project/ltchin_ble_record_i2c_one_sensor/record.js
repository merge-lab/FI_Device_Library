// PARAMS TO CHANGE
// Sensor 0 = Below Knee, Sensor 1 = Above Knee
const CSV_HEADINGS = "Browser Timestamp,Sensor Number,Pressure,Temperature,Trigger Pin,ESP32 Timestamp" // Expecting CSV format
const MOVING_WINDOW = 100;

const BLE_SERVICE_UUID = '19b10000-e8f2-537e-4f6c-d104768a1214';
const SENSOR_CHAR_UUID = 'e858b1fa-9491-4e09-91cf-499653f5f258';


/**********************************************************************************
 * DOM ELEMENTS
 *********************************************************************************/

var fileName = "Untitled" // Will auto add timestamp
document.getElementById("tellUserTheName").innerHTML = fileName;

const connectButton = document.getElementById('connectBleButton');
const disconnectButton = document.getElementById('disconnectBleButton');
const onButton = document.getElementById('onButton');
const offButton = document.getElementById('offButton');
const retrievedValue = document.getElementById('valueContainer');
const latestValueSent = document.getElementById('valueSent');
const bleStateContainer = document.getElementById('bleState');
const timestampContainer = document.getElementById('timestamp');

// Connect Button (search for BLE Devices only if BLE is available)
connectButton.addEventListener('click', (event) => {
    if (isWebBluetoothEnabled()){
        connectToDevice();
    }
    clearData();
    clearGraph();
});

// Disconnect Button
disconnectButton.addEventListener('click', disconnectDevice);

// Rename Button
function rename() {
    fileName = document.getElementById("inputFileName").value;
    document.getElementById("tellUserTheName").innerHTML = fileName;
}

/**********************************************************************************
 * BLUETOOTH ELEMENTS
 *********************************************************************************/

var BLE = new p5ble(); // relies on p5.ble.min.js in the same folder to save it
var sensorCharacteristic = null;

// Check if BLE is available in your Browser
function isWebBluetoothEnabled() {
    if (!navigator.bluetooth) {
        console.log('Web Bluetooth API is not available in this browser!');
        bleStateContainer.innerHTML = "Web Bluetooth API is not available in this browser/device!";
        return false
    }
    console.log('Web Bluetooth API supported in this browser.');
    return true
}

// Connect to BLE Device and Enable Notifications
function connectToDevice(){
    BLE.connect(BLE_SERVICE_UUID, gotCharacteristics)
    bleStateContainer.innerHTML = 'Connected to device';
    bleStateContainer.style.color = "#24af37";
}

function disconnectDevice() {
    saveData()
    BLE.stopNotifications(sensorCharacteristic);
    BLE.disconnect()
    bleStateContainer.innerHTML = "Device disconnected";
    bleStateContainer.style.color = "#d13a30";
}

function gotCharacteristics(error, characteristics) {
    console.log(characteristics);
    // Order is defined by how initiated in the ESP32 code
    sensorCharacteristic = characteristics[0];

    console.log("About to start notifications");
    BLE.startNotifications(sensorCharacteristic, handleNotifications, 'string')

    // Options: 'unit8', 'uint16', 'uint32', 'int8', 'int16', 'int32', 'float32', 'float64', 'string'
    // BLE.read(sensorCharacteristic, 'string', gotValue);
}

// function gotValue(error, value) {
//     if (error) console.log("error: ", error);
//     console.log("Characteristic value changed: ", value);
//     retrievedValue.innerHTML = value;

//     // Poll again for value
//     BLE.read(sensorCharacteristic, 'string', gotValue);
// }

/**********************************************************************************
 * DATA HANDLING
 *********************************************************************************/

function clearData() {
    csv = "data:text/csv;charset=utf-8," + CSV_HEADINGS + "\n";
}

function handleNotifications(data) {
    let csvLine = '';
    // Expecting tuple data so will trim the opening and ending parentheses
    values = data.substring(1,data.length-1).split(',');
    retrievedValue.innerHTML = values;
    timestampContainer.innerHTML = new Date().toLocaleString('en-US');
    // console.log(values)
    plotData(values)

    // if (isRecording) {
    csvLine += Date.now();
    values.forEach((value, index) => {
        csvLine += ',' + value;
    });
    // }\
    csvLine += "\n";
    csv += csvLine;
}

function saveData() {
    var uri = encodeURI(csv);
    var link = document.createElement('a');
    if (typeof link.download === 'string') {
        link.href = uri;
        link.download = fileName + "_" + timestamp();

        //Firefox requires the link to be in the body
        document.body.appendChild(link);

        //simulate click
        link.click();

        //remove the link when done
        document.body.removeChild(link);
    } else {
        window.open(uri);
    }
}


// I hate timestamps
function timestamp() {
    const now = new Date();
    const year = String(now.getFullYear()).slice(-2);
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    return `${year}${month}${day}_${hours}${minutes}${seconds}`;
}

/**********************************************************************************
 * GRAPHING
 *********************************************************************************/

const ctx = document.getElementById('myChart');

var s1 = {
  label: 'Sensor 0',
  borderColor: 'blue',
  borderWidth: 2,
  tension: 0.1,
  yAxisID: 'Pressure'
};

var chart = new Chart(ctx, {
    type: 'scatter',
    data: { datasets: [s1]},
    options: {
        responsive: true,
        scales: {
            x: {
                title: {
                    display: true,
                    text: "UNIX Time (ns)"
                }
            },
            Pressure: {
                title: {
                    display: true,
                    text: "in. H2O"
                },
                position: 'left',
                suggestedMax: 0.3,
                suggestedMin: -0.1
            }
        }
    }
});

function plotData(values) {
    // Making some assumptions about the format of the dataset
    // Specifically:
    // [sensor num, pressure, temp, trigger, esp32 timestamp]

    series = values[0];
    pressure = values[1];
    esp32_time = values[4];
    trigger = values[3];

    chart.data.datasets[series].data.push({x: esp32_time, y: pressure});

    if (chart.data.datasets[series].data.length > MOVING_WINDOW) {
        chart.data.datasets[series].data.shift();
    }

    chart.update('none');
}

function clearGraph() {
    // Reset the datasets' data to empty arrays
    chart.data.datasets = [
        {
            label: 'Sensor 0',
            borderColor: 'blue',
            borderWidth: 2,
            tension: 0.1,
            yAxisID: 'Pressure',
            data: []  // Clear data for Sensor 0
        }
    ];

    // Update the chart to apply changes
    chart.update();
}
