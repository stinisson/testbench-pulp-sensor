from time import sleep
import random

from commands import SENSOR_COMMANDS
from sensor_message import MessageDecoder, build_message


class SerialMock:

    def __init__(self):
        self.test_cases = [(SENSOR_COMMANDS["COMMAND_MEASURE"], 0xFF),
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


serial = SerialMock()
decoder = MessageDecoder()
while True:
    received = serial.read()
    print("Received message:", received)
    for c in received:
        decoder.append(c)
    message = decoder.get_message()

    if message:
        print("Decoded message:", message)
        command, payload = message[0], message[1]

        if command == SENSOR_COMMANDS['COMMAND_MEASURE']:
            # make measurement, [5, 75)
            edge_position = random.randrange(5, 75)
            print("\nCommand:", SENSOR_COMMANDS.inverse[command])
            print("Payload:", payload)
            sleep(1)
            message = build_message(command, payload)
            serial.write(message)
            print(f"Sent: {message}")

        elif command == SENSOR_COMMANDS['COMMAND_SEND_DATA']:
            # send back measurement result
            print("edge_position:", edge_position)

            print("\nCommand:", SENSOR_COMMANDS.inverse[command])
            print("Payload:", payload)

            base_message = build_message(SENSOR_COMMANDS['COMMAND_FORWARD_DATA'], 100)  # Temp 100 degrees Celsius
            serial.write(base_message)
            # print(f"Sent base message: {base_message}")

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
                        # print(f"Sent paper sensor led on", sensor_led_on)
                        # print(f"Sent paper sensor led off", sensor_led_off)

                    else:
                        sensor_led_on = build_message(SENSOR_COMMANDS['COMMAND_FORWARD_DATA'], 190)
                        sensor_led_off = build_message(SENSOR_COMMANDS['COMMAND_FORWARD_DATA'], 200)
                        serial.write(sensor_led_on)
                        serial.write(sensor_led_off)
                        # print(f"Sent no paper sensor led on", sensor_led_on)
                        # print(f"Sent no paper sensor led off", sensor_led_off)

                sensor_temp = build_message(SENSOR_COMMANDS['COMMAND_FORWARD_DATA'], 100)   # Temp 100 degrees Celsius
                serial.write(sensor_temp)
                #print(f"Sent temp sensor", sensor_temp)

            serial.write(build_message(SENSOR_COMMANDS['COMMAND_SEND_DATA'], 0))
            #print("Sent end message")

        elif command == SENSOR_COMMANDS['COMMAND_PELTIER']:
            print("\nCommand:", SENSOR_COMMANDS.inverse[command])
            print("Payload:", payload)

        elif command == SENSOR_COMMANDS['COMMAND_SET_ANALOG_OUTPUT']:
            print("\nCommand:", SENSOR_COMMANDS.inverse[command])
            print("Payload:", payload)

        elif command == SENSOR_COMMANDS["COMMAND_SHUTDOWN"]:
            print("\nCommand:", SENSOR_COMMANDS.inverse[command])
            print("End")
            break
    print("- " * 65)
