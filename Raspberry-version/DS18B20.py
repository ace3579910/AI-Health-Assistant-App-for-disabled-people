#!/usr/bin/env python3
import time
import glob

# SETTINGS
base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')
DROP_THRESHOLD = 2.0        # degrees C: ignore readings that are this much lower than last valid
READ_INTERVAL = 2.0         # seconds between reads

if not device_folders:
    raise SystemExit("No DS18B20 sensor found under /sys/bus/w1/devices/")

device_file = device_folders[0] + '/w1_slave'

def read_raw():
    with open(device_file, 'r') as f:
        return f.read().splitlines()

def read_temp_c():
    lines = read_raw()
    # wait until CRC is OK
    if lines[0].strip()[-3:] != 'YES':
        return None
    # parse temperature after 't='
    temp_str = lines[1].split('t=')[-1]
    temp_c = float(temp_str) / 1000.0
    return temp_c

def format_output(temp_c):
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    s = f"Temperature: {temp_c:.3f} °C / {temp_f:.3f} °F"
    if 35.0 < temp_c < 38.0:
        s += "  -> Normal body temperature"
    elif temp_c >= 38.0:
        s += "  -> Fever detected!"
    else:
        s += "  -> Below normal (sensor may not be in contact)"
    return s

if __name__ == "__main__":
    last_valid_temp = None
    try:
        while True:
            temp_c = read_temp_c()
            if temp_c is None:
                print("Could not read temperature (CRC not OK). Retrying...")
            else:
                if last_valid_temp is None:
                    # first valid reading — accept it
                    last_valid_temp = temp_c
                    print(format_output(temp_c))
                else:
                    # If new reading is suspiciously lower than last valid by DROP_THRESHOLD, ignore it
                    if (last_valid_temp - temp_c) >= DROP_THRESHOLD:
                        print(f"Ignored sudden drop: measured {temp_c:.3f} °C but last valid was {last_valid_temp:.3f} °C "
                              f"(drop >= {DROP_THRESHOLD} °C).")
                        # Optionally you can keep printing last valid value or just skip
                        print("Using last valid value -> " + format_output(last_valid_temp))
                    else:
                        # Accept reading (including small drops/increases)
                        last_valid_temp = temp_c
                        print(format_output(temp_c))
            time.sleep(READ_INTERVAL)
    except KeyboardInterrupt:
        print("\nExiting.")
