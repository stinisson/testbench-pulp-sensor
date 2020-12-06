from time import sleep
import serial

from commands import SENSOR_COMMANDS
from sensor_message import MessageDecoder, build_message


class SerialMock:
    def __init__(self):
        self.test_cases = [(SENSOR_COMMANDS["COMMAND_MEASURE"], 0xFF),
                           (SENSOR_COMMANDS["COMMAND_SEND_DATA"], 0),
                           (SENSOR_COMMANDS["COMMAND_MEASURE"], 0xFF),
                           (SENSOR_COMMANDS["COMMAND_SEND_DATA"], 0),
                           (SENSOR_COMMANDS["COMMAND_PELTIER"], 0),             # 0/1
                           (SENSOR_COMMANDS["COMMAND_SET_ANALOG_OUTPUT"], 0),   # 0-1023
                           (SENSOR_COMMANDS["COMMAND_SHUTDOWN"], 0)]
        self.state = 0

    def read(self):
        print("Test case", self.state + 1)
        command, payload = self.test_cases[self.state]
        self.state += 1
        return build_message(command, payload)

    def write(self, message):
        # serial mock sending to IPA (command, payload)
        return len(message)


serial = serial.Serial("/dev/serial0", baudrate=57600, timeout=1.0)
decoder = MessageDecoder()

edge_position = 4
while True:
    try:
        received = serial.read()
    except:
        continue

    for c in received:
        decoder.append(chr(c))
    message = decoder.get_message()

    if message:
        print("Decoded message:", message)
        command, payload = message[0], message[1]

        if command == SENSOR_COMMANDS['COMMAND_MEASURE']:
            # make measurement, [5, 75)
            edge_position += 1
            if edge_position == 75:
                edge_position = 0
            print("\nCommand:", SENSOR_COMMANDS.inverse[command])
            print("Payload:", payload)
            sleep(0.5)
            message = build_message(command, payload)
            serial.write(message)
            print(f"Sent: {message}")

        elif command == SENSOR_COMMANDS['COMMAND_SEND_DATA']:
            # send back measurement result
            print("edge_position:", edge_position)

            print("\nCommand:", SENSOR_COMMANDS.inverse[command])
            print("Payload:", payload)

            base_message = build_message(SENSOR_COMMANDS['COMMAND_FORWARD_DATA'], 100)  # Temp
            serial.write(base_message)

            is_paper = False
            for i in range(5):
                for j in range(16):
                    if i * 16 + j == edge_position:
                        is_paper = True
                    if is_paper:
                        sensor_led_on = build_message(SENSOR_COMMANDS['COMMAND_FORWARD_DATA'], 50)
                        sensor_led_off = build_message(SENSOR_COMMANDS['COMMAND_FORWARD_DATA'], 200)
                        serial.write(sensor_led_on)
                        serial.write(sensor_led_off)
                    else:
                        sensor_led_on = build_message(SENSOR_COMMANDS['COMMAND_FORWARD_DATA'], 190)
                        sensor_led_off = build_message(SENSOR_COMMANDS['COMMAND_FORWARD_DATA'], 200)
                        serial.write(sensor_led_on)
                        serial.write(sensor_led_off)

                sensor_temp = build_message(SENSOR_COMMANDS['COMMAND_FORWARD_DATA'], 100)   # Temp displ. in I/O status
                serial.write(sensor_temp)

            serial.write(build_message(SENSOR_COMMANDS['COMMAND_SEND_DATA'], 0))

        elif command == SENSOR_COMMANDS['COMMAND_PELTIER']:
            print("\nCommand:", SENSOR_COMMANDS.inverse[command])
            print("Payload:", payload)

        elif command == SENSOR_COMMANDS['COMMAND_SET_ANALOG_OUTPUT']:
            print("\nCommand:", SENSOR_COMMANDS.inverse[command])
            print("Payload:", payload)

        elif command == SENSOR_COMMANDS["COMMAND_SHUTDOWN"]:
            print("End")
            break
        print("- " * 40)
