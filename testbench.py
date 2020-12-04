# import serial

# port = serial.Serial("/dev/serial0", baudrate=57600, timeout=1.0)
# byte_cnt = port.write("Hello".encode())
# rcv = port.read(byte_cnt)
# print(rcv)

class SerialMock:

    def read(self):
        return build_message(1, 0x7D)

    def write(self):
        pass


# data is a string
def crc(data):
    def subCrc(char, old_crc):
        new_crc = old_crc ^ ord(char)
        for i in range(0, 8):
            if new_crc & 0x01:
                new_crc = (new_crc // 2) ^ 0x8C
            else:
                new_crc //= 2
        return new_crc

    mycrc = 0
    for char in data:
        mycrc = subCrc(char, mycrc)
    return mycrc


def build_message(command, payload):
    byte_1 = ((command & 0xF) << 4) | ((payload & 0x0300) >> 8)
    byte_2 = payload & 0xFF
    byte_crc = crc([chr(byte_1), chr(byte_2)])

    IPA_START = 0x12
    IPA_ESCAPE = 0x7D
    IPA_XOR = 0x20

    message = chr(IPA_START)
    for byte in [byte_1, byte_2, byte_crc]:
        if byte in [IPA_ESCAPE, IPA_START]:
            message += chr(IPA_ESCAPE)
            message += chr(byte ^ IPA_XOR)
        else:
            message += chr(byte)
    message += chr(IPA_START)
    return message


serial = SerialMock()
res = serial.read()
for r in res:
    print(f"0x{ord(r):02X}")