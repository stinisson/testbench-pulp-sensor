from commands import IPA_START, IPA_ESCAPE, IPA_XOR, SENSOR_COMMANDS

# Receive data and decode message
class MessageDecoder:
    def __init__(self):
        self.clear()

    def clear(self):
        self.buff = ""
        self.escape = False
        self.latest_message = None

    def get_message(self):
        message = self.latest_message
        self.latest_message = None
        return message

    def append(self, c):
        # if start or end of message
        if ord(c) == IPA_START:
            if len(self.buff) > 0:
                self._decode_message()
            self.buff = ""
            self.escape = False
        elif self.escape:
            self.buff += chr(ord(c) ^ IPA_XOR)
            self.escape = False
        elif ord(c) == IPA_ESCAPE:
            self.escape = True
        else:
            self.buff += c

    def _decode_message(self):
        # Check length
        if len(self.buff) < 3:
            print("decode_message message too short")
            return

        # Check crc
        if ord(self.buff[-1]) != crc(self.buff[:-1]):
            print("decode_message bad crc")
            return

        command = (ord(self.buff[0]) & 0xF0) >> 4
        payload = (((ord(self.buff[0])) & 0x03) << 8) + ord(self.buff[1])
        self.latest_message = (command, payload)


# Send data and build message
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
