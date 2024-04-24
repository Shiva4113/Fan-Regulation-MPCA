from app import sendVals
import serial
import time
import os

arduino_port = 'COM69'
baud_rate = 9600
# vals = [3,5,7,9]

def read_file_content():
    file_path = "arduino_command.txt"
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            print(f"Content of {file_path}: {content}")
    except FileNotFoundError:   
        print(f"File {file_path} not found.")

    return int(content)

vals = read_file_content()
vals = [vals,vals,vals,vals,vals]
os.remove('./arduino_command.txt')
ser = serial.Serial(arduino_port, baud_rate)
def send_values_to_arduino():
    # values_to_send = [5,4,3,2] # Example values to send
    values_to_send = vals
    for value in values_to_send:
        ser.write(value.to_bytes(1, byteorder='little')) # Send the value as a single byte
        print(f"Sent Value: {value}")
        time.sleep(1) # Wait for 1 second before sending the next value

send_values_to_arduino()

ser.close()
