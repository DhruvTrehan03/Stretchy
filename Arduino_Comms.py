import serial
import time
import matplotlib.pyplot as plt
strains = []
stresses = []
resistances = []

#arduino_port = input("What port is the Arduino connected to? ")
arduino = serial.Serial(port = "COM8", baudrate=115200,  timeout=0)
time.sleep(2)

Input = "F100, D1000, B100, B100, D1000, B100, F200, D1000*"
def write(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)


print("Start")
write(Input)

# while True and len(strains)<50:
#     data =arduino.readline().strip().decode('UTF-8')
#     time.sleep(0.05)
#     type(data)
#     if data.strip() != '':
#         data = data.split(", ")
#         print(data)
#         strains.append(float(data[0]))
#         stresses.append(float(data[1]))
# plt.plot(strains, 'r', label = 'Strains')
# plt.plot(stresses, 'g', label = 'Stresses')
# plt.legend()
# plt.show()
# plt.plot(strains, stresses, label = 'Stresses')

# plt.legend()
# plt.show()


        