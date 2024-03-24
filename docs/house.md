# House Module for Linguflex

The House module for Linguflex is a sophisticated smart home solution that manages and controls various Tuya smart devices such as bulbs and outlets. It offers the capability to remotely control these devices, set bulb colors, and monitor their status, ensuring a seamless smart home experience.

## Contents

- [Functionality](#functionality)
- [Examples](#examples)
- [Installation](#installation)
- [Configuration](#configuration)
- [Connecting Devices to Tuya Cloud](#connecting-devices-to-tuya-cloud)
- [Fetching Device Parameters](#fetching-device-parameters)

## Functionality

The House module handles:
- Turning on/off smart bulbs and outlets.
- Setting colors for smart bulbs using hex color codes.
- Retrieving the current status and color of smart bulbs.
- Directly controlling Tuya smart devices over the local network without relying on internet-based cloud services.

## Examples

- "Turn on the lights in the living room."
- "Set the bulb color in the bedroom to #FF4500."
- "Get the status of the ventilator outlet."

## Installation

Before using the House module, ensure that Python is installed on your system along with the required dependencies. Clone the Linguflex repository and navigate to the House module directory.

### Dependencies

The module requires the `tinytuya` package for interacting with Tuya devices. Install it using pip:

```bash
pip install tinytuya
```

## Configuration

### smart_home_devices.json

This file is essential for configuring your Tuya smart devices. Here's how to set it up:

1. **Create a JSON file named `smart_home_devices.json` in the `lingu/config` directory.**

2. **Add your Tuya devices in the following format:**
   ```json
   [
       {
           "type": "Bulb",
           "name": "<Name of the Device>",
           "id": "<Device ID>",
           "ip": "<IP Address>",
           "key": "<Local Key>",
           "version": "<Version>"
       },
       {
           "type": "Outlet",
           "name": "<Name of the Device>",
           ...
       }
       // Add more devices as needed
   ]
   ```

### Connecting Devices to Tuya Cloud

To control your Tuya devices locally, you first need to connect them to the Tuya cloud:

1. Create a [Tuya Account](https://iot.tuya.com/) and log in.
2. Create a cloud project, give a name and select "smart home" under industry and development method and select the data center for your region.
3. Add the Device Status Notification API to the project
4. After creating the project the next page should be "Overview" Tab from the "Cloud" menu. Remember Access ID/Client ID and Access Secret/Client Secret.
5. From the tab bar where also "Overview" is located click on the right on "Devices"
6. On the bar one line below that click "Link Tuya App Account", then click "Add App Account"
7. Scan the displayed QR Code with your Tuya Application (Smart-Life App etc, there are many; the option for that is often under "profile" and sometimes a button on the top)
8. Change the permissions to "Read, write and Manage"
9. Now the devices will show up in the Tuya cloud.

### Fetching Device Parameters

1. Open a console and run
```bash
python -m tinytuya
```
2. Copy the output of the console into a text editor. 
3. Then run
```bash
python -m tinytuya wizard
```
4. When asked "Enter API Key from tuya.com" enter the Access ID/Client ID from point 4. of the "Connect devices to tuya cloud" section
5. When asked "Enter API Secret from tuya.com" enter the Access Secret/Client Secret from point 4. of the "Connect devices to tuya cloud" section 
6. When asked "Enter any Device ID" enter "scan"
7. Enter region of tuya cloud project
8. Copy the output of the console into a text editor. 
9. Search in the output for the values "id", "key", "version" and the ip adress of the devices you want to add from the output. 
10. Store these values into config/smart_home_devices.json

### Final Steps

Once the `smart_home_devices.json` is configured, restart the Linguflex application. Your House module should now be able to communicate with the specified Tuya smart devices on your local network.