#!/usr/bin/env python3
"""
Simple UART test for PomeloCore
Sends commands and displays responses
"""
import serial
import time
import sys

def test_uart(port='/dev/ttyUSB0', baudrate=921600):
    print(f"Opening {port} at {baudrate} baud...")

    try:
        ser = serial.Serial(port, baudrate, timeout=2)
        time.sleep(0.1)  # Wait for port to open

        # Flush any existing data
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        print("Connected! Sending commands...\n")

        # Test commands
        commands = ['s', 'c', 'm']

        for cmd in commands:
            print(f"--- Sending: '{cmd}' ---")
            ser.write(f"{cmd}\n".encode())
            time.sleep(0.5)  # Wait for response

            # Read response
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                print(f"Response:\n{response}\n")
            else:
                print("No response received\n")

        ser.close()
        print("Test complete!")

    except serial.SerialException as e:
        print(f"Error: {e}")
        return False
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        if 'ser' in locals() and ser.is_open:
            ser.close()
        return False

    return True

if __name__ == "__main__":
    # Try both possible ports
    ports_to_try = ['/dev/ttyUSB0', '/dev/ttyACM0']

    for port in ports_to_try:
        print(f"\n{'='*60}")
        print(f"Testing {port}")
        print('='*60)
        try:
            if test_uart(port):
                break
        except Exception as e:
            print(f"Failed: {e}")
            continue
