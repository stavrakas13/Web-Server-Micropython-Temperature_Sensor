#By Omiros Sarris & Stavros Mitropoulos

import machine
import onewire
import ds18x20
import time
import utime
import uasyncio
import network
import esp
import gc
import socket
import sys
import json


gc.collect()
count=0 #how many measurements


ssid = 'NetworkToConnect'            # Add your network name here 
password = 'PasswordOfTheNetwork'	 # Add the passowrd of your network here

temperatures=[]
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)
measurements = []
max_temp=float('-inf')
avr_temp=0
current_time = utime.time()
current_local_time = utime.localtime(current_time)
year, month, day, hour, minute, second, weekday, yearday = current_local_time
            
def save_measurements_to_json():
    try:
        with open('measurements.json', 'w') as f:
            json.dump(measurements, f)
        print("Measurements saved to JSON file.")
        #measurements.clear()
    except Exception as e:
        print("Failed to save measurements:", e)

def find_max_temp_for_date(day, month, year):
    try:
        with open('measurements.json', 'r') as f:
            measurements = json.load(f)
            global max_temp
            for measurement in measurements:
                if (measurement["day"] == day and
                    measurement["month"] == month and
                    measurement["year"] == year):
                    temp = measurement["temperature"]
                    if max_temp is None or temp > max_temp:
                        max_temp = temp
            if max_temp is not None:
                print(f"Maximum temperature for {day}/{month}/{year} is {max_temp} Celsius.")
            else:
                print(f"No measurements found for {day}/{month}/{year}.")
    except Exception as e:
        print("Failed to load measurements:", e)

def find_avg_temp_for_date(day, month, year):
    try:
        global avr_temp
        with open('measurements.json', 'r') as f:
            measurements = json.load(f)
            temp_sum = 0
            count = 0
            global avr_temp
            for measurement in measurements:
                if (measurement["day"] == day and
                    measurement["month"] == month and
                    measurement["year"] == year):
                    temp_sum += measurement["temperature"]
                    count += 1
            if count > 0:
                avr_temp = temp_sum / count
                print(f"Average temperature for {day}/{month}/{year} is {avr_temp} Celsius.")
            else:
                print(f"No measurements found for {day}/{month}/{year}.")
    except Exception as e:
        print("Failed to load measurements:", e)
        
def delete_measurements_for_yearday(yearday):
    try:
        with open('measurements.json', 'r') as f:
            measurements = json.load(f)
        filtered_measurements = [measurement for measurement in measurements if measurement["yearday"] != yearday]
        with open('measurements.json', 'w') as f:
            json.dump(filtered_measurements, f)
        print(f"Measurements for yearday {yearday} deleted successfully.")
    except Exception as e:
        print("Failed to delete measurements:", e)
    
def connect_to_wifi(timeout=30):
    start_time = time.time()
    while not station.isconnected() and time.time() - start_time < timeout:
        time.sleep(1)
    if station.isconnected():
        print('Connected to WiFi')
        print(station.ifconfig())
    else:
        print('Failed to connect to WiFi')

connect_to_wifi()

ds_pin = machine.Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
temp5 = ds_sensor.scan()

print('Found DS devices:', temp5)


def check_duplicate(data_list, new_data):
    for data in data_list:
        if all(data[key] == new_data[key] for key in new_data):
            return True  
    return False

def get_temp():
    global temperatures
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    temp_reading = ds_sensor.read_temp(temp5[0])
    temperatures.append(temp_reading)
    measurement_data = {
        "temperature": temp_reading,
        "year": year,
        "month": month,
        "day": day,
        "hours": hour,
        "minutes": minute,
        "seconds": second,
        "yearday": yearday
    }
    
    if not check_duplicate(measurements, measurement_data):
        measurements.append(measurement_data)
    return temp_reading

temp=get_temp()



def web_page():
    global count
    current_time = utime.time()
    current_local_time = utime.localtime(current_time)
    year, month, day, hour, minute, second, weekday, yearday = current_local_time
    current_temp = get_temp()  # Retrieve temperature separately
    #count=count+1
    find_max_temp_for_date(day, month, year)
    find_avg_temp_for_date(day, month, year)
    #save_average_temp(avg_temp)  # Save average temperature
     html = """<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="refresh" content="1"> <!-- Auto-refresh every 1 second -->
            <title>Temperature Monitor</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #f0f0f0;
                }}
                .container {{
                    text-align: center;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    background-color: #fff;
                }}
                h1 {{
                    margin-top: 0;
                    color: #333;
                }}
                p {{
                    margin: 10px 0;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Temperature Monitor</h1>
                <p>Temperature: {temp} Celsius</p>
                <p>Current date: {day}/{month}/{year}</p>
                <p>Current time: {hour}:{minute}:{second}</p>
                <p>Max temperature today: {max_temp} | Today's Average: {avr_temp}</p>
                <h2>Fetch New Temperature</h2>
            <form action="./value">
                <input type="submit" value="Fetch Temp" />
            </form>
            <p>Fetched value: {temp}</p>
            <p>
            <h2>History</h2>
            <form action="./history">
                <input type="submit" history="Fetch History" />
            </form>
            </p>
        </body>
        </html>""".format(temp=current_temp, day=day, month=month, year=year, hour=hour, minute=minute, second=second, max_temp=max_temp, avr_temp=avr_temp)
    return html

# Function to generate HTML page showing all data from JSON
def web_page2():
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Temperature Data</title>
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>Temperature Data</h1>
    <table>
        <tr>
            <th>Temperature</th>
            <th>Year</th>
            <th>Month</th>
            <th>Day</th>
            <th>Yearday</th>
        </tr>"""
    
    # Assuming measurements is a list of dictionaries
    for measurement in measurements:
        html += f"""<tr>
                    <td>{measurement["temperature"]} Celsius</td>
                    <td>{measurement["year"]}</td>
                     <td>{measurement["month"]}</td>
                    <td>{measurement["day"]}</td>
                     <td>{measurement["yearday"]}</td>
                 </tr>"""
    
    html += """
    </table>
    <div>
        <form action="./value">
            <input type="submit" value="Fetch Temp" />
        </form>
        <p>Fetched value: {}</p>
    </div>
</body>
</html>""".format(temp)  # Assuming temp is defined somewhere

    return html


# uasynchronous functio to handle client's requests
async def handle_client(reader, writer):
    global response
    global state
    print("Client connected")
    request_line = await reader.readline()
    print('Request:', request_line)
    
    # Skip HTTP request headers
    while await reader.readline() != b"\r\n":
        pass
    
    request = str(request_line, 'utf-8').split()[1]
    print('Request:', request)
    
    if request == '/value?':
        global temp
        temp=get_temp()
        utime.sleep_ms(300)
        save_measurements_to_json()
        response=web_page()
    # Generate HTML response
    
    if request == '/history?':
        response= web_page2()
        
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()
    print('Client Disconnected')



async def main():
    global response
    print('Setting up server')
    response = web_page()
    server = uasyncio.start_server(handle_client, "0.0.0.0", 80)
    uasyncio.create_task(server)
    uasyncio.create_task(get_temp())
    while True:
        await uasyncio.sleep(5)
        delete_measurements_for_yearday(yearday-10)
        print('This message will be printed every 5 seconds')
        

# Create an Event Loop
loop = uasyncio.get_event_loop()
# Create a task to run the main function
loop.create_task(main())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    print('Error occured: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')
