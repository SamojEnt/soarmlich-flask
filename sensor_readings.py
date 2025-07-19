import os
import struct
import time

# Only import and use serial if NOT running on Render
RUNNING_ON_RENDER = os.getenv("RENDER", "false").lower() == "true"

if not RUNNING_ON_RENDER:
    import serial
    # Initialize serial port for RS485 sensor
    ser3 = serial.Serial(
        port='/dev/ttyAMA2',  # Change this to your RS485 port
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=2
    )

# Function to calculate CRC
def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

# Function to read sensor and return pH (optionally temperature too)
def read_sensor(sensor_name):
    if sensor_name != 'RS485_Sensor':
        return "Invalid sensor"

    if RUNNING_ON_RENDER:
        return "Sensor reading not supported in cloud environment"

    try:
        # Construct Modbus request
        request_data = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x04])
        crc = calculate_crc(request_data)
        request_data += struct.pack('<H', crc)  # CRC in little-endian

        # Send request to sensor
        ser3.write(request_data)
        time.sleep(1)

        # Read response
        data = ser3.read(ser3.in_waiting or 64)
        if len(data) < 11:
            return "Incomplete response"

        # CRC check
        received_crc = struct.unpack('<H', data[-2:])[0]
        received_data = data[:-2]
        calculated_crc = calculate_crc(received_data)

        if received_crc != calculated_crc:
            return "CRC mismatch"

        # Extract 8 bytes of float data
        final_data = data[3:11]
        swapped = bytearray()
        for i in range(0, len(final_data), 4):
            word = final_data[i:i+4]
            swapped += word[2:4] + word[0:2]

        values = struct.unpack('>2f', swapped)
        ph = round(values[0], 2)
        # temp = round(values[1], 2)  # Optional: use if needed

        return ph  # or return {'ph': ph, 'temp': temp} if both needed
    except Exception as e:
        return f"Error: {e}"

# Used by Flask to list sensors
def get_sensor_list():
    return ['RS485_Sensor']

# Optional testing when running directly
if __name__ == "__main__":
    while not RUNNING_ON_RENDER:
        result = read_sensor("RS485_Sensor")
        print("pH:", result)
        time.sleep(2)
