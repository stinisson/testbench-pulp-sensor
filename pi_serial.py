import serial

port = serial.Serial("/dev/serial0", baudrate=57600, timeout=1.0)
byte_cnt = port.write("Hello".encode())
rcv = port.read(byte_cnt)
print(rcv)
