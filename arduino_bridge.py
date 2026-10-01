import serial
import requests
import re
import time

SERIAL_PORT = "COM5"
BAUD_RATE = 9600

API_URL = "http://127.0.0.1:8000/bins/arduino"

BIN_ID = 1

arduino = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=1
)

time.sleep(2)

print("Arduino connected")

while True:

    line = arduino.readline().decode(
        "utf-8",
        errors="ignore"
    ).strip()

    if "Garbage Level:" in line:

        match = re.search(
            r"Garbage Level:\s*([\d.]+)",
            line
        )

        if match:

            fill_level = int(float(match.group(1)))

            print(
                "Garbage Level:",
                fill_level,
                "%"
            )

            response = requests.post(
                API_URL,
                params={
                    "bin_id": BIN_ID,
                    "fill_level": fill_level
                }
            )

            print(
                "FastAPI:",
                response.json()
            )

            print("--------------------")