Web Server with MicroPython for Temperature Sensor

This project demonstrates how to build a Web Server with MicroPython on an ESP8266/ESP32 board to read temperature data from a DS18x20 temperature sensor and serve it through a web interface. The server allows users to monitor temperature readings in real-time, store them in JSON format, and retrieve historical data.
Features

    MicroPython Web Server: A simple HTTP web server running on ESP8266/ESP32, serving dynamic temperature data.
    Temperature Sensor Integration: Reads temperature data using a DS18x20 sensor (compatible with DHT11, DHT22 sensors).
    Real-time Temperature Display: Shows live temperature and humidity data through a browser interface.
    Data Logging: Saves temperature measurements to a JSON file, supporting data retrieval and analysis.
    Data History: Displays historical temperature data in a tabular format.
    Data Analysis: Calculates and displays the maximum and average temperature for the current day.
    Web Interface: Simple, responsive HTML interface for monitoring and fetching data.

Hardware Requirements

    Microcontroller: ESP8266 or ESP32 (or any other MicroPython-compatible device)
    Temperature Sensor: DS18x20 (DHT11/DHT22 sensors can also be used)
    Wires: Jumper wires for sensor connection
    Power Supply: USB or battery-powered microcontroller

Software Requirements

    MicroPython: The firmware should be installed on the ESP8266 or ESP32.
    uPyCraft or Thonny IDE: Use these to upload the MicroPython script to the device.
    Wi-Fi Network: Ensure the device can connect to a Wi-Fi network.
