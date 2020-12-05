from time import sleep

from commands import SENSOR_COMMANDS
from sensor_message import MessageDecoder, build_message

# print(SENSOR_COMMANDS['COMMAND_SEND_DATA'])
# print(SENSOR_COMMANDS.inverse[0])


class SerialMock:
    def read(self):
        return build_message(0, 832)

    def write(self, command, payload):
        # serial mock sending to IPA (command, payload)
        build_message(command, payload)


serial = SerialMock()
decoder = MessageDecoder()
while True:
    received = serial.read()
    print("\n\nReceived message:", received)
    for c in received:
        decoder.append(c)
    message = decoder.get_message()

    if message:
        print("Decoded message:", message)
        command, payload = message[0], message[1]

        if command == SENSOR_COMMANDS['COMMAND_MEASURE']:
            print("\nCommand:", command, SENSOR_COMMANDS.inverse[0])
            print("Payload:", payload)
            sleep(1)
            serial.write(command, payload)
            print(f"Sent: {command, payload}")

        if command == SENSOR_COMMANDS["COMMAND_SHUTDOWN"]:
            print("End")
            break
