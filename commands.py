from bidict import bidict

SENSOR_COMMANDS = bidict({"COMMAND_MEASURE": 0,
                          "COMMAND_SEND_DATA": 1,
                          "COMMAND_PELTIER": 2,
                          "COMMAND_FORWARD_DATA": 3,
                          "COMMAND_SET_ANALOG_OUTPUT": 4})

IPA_START = 0x12
IPA_ESCAPE = 0x7D
IPA_XOR = 0x20

print(SENSOR_COMMANDS['COMMAND_MEASURE'])
print(SENSOR_COMMANDS.inverse[0])
