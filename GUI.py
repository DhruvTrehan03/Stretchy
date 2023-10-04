# Load all of the relevant packages


# For communicating with the Keysight SMU; Installation: pip install pyvisa
# Pyvisa requires that LabView VISA lirary is installed on your computer
import pyvisa
import time
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import time

sg.theme("LightBrown1")

# ----- Variables -----
_VARS = {'window': False,
         'fig_agg': False,
         'pltFig': False}
resistances = []
strains = []
stresses = []
counter = 0
Connected = False
data = ''
Applied_Voltage = 0.05 #Voltage that is applied to test material

# ----- Matplotlib Functions -----
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1, padx = 50, pady = 5  )
    return figure_canvas_agg

def makeSynthData():
    x = np.linspace(0,10,10)
    y = x**2
    return (x, y)

def drawChart(data_1, data_2, data_3):
    _VARS['pltFig'] = plt.figure(figsize=(3,3))
    plt.plot(data_1, label = "Strains")
    plt.plot(data_2, label = "Stresses")
    plt.plot(data_3, label = "Resistances")
    _VARS['fig_agg'] = draw_figure(_VARS['window']['-CNVS-'].TKCanvas, _VARS['pltFig'])

def generateLinSweep(points_per_sweep,v_start,v_end,reverse=False):
    sweep = ""
    for i in range(0,points_per_sweep):
        sweep += "{:.3E}".format(round(v_start + (i/points_per_sweep)*(v_end-v_start),5)) + ","
    sweep += "{:.3E}".format(round(v_start + ((i+1)/points_per_sweep)*(v_end-v_start),5))
    if reverse == True:
        sweep += ","
        for j in range(1,points_per_sweep):
            i = points_per_sweep - j 
            sweep += "{:.3E}".format(round(v_start + (i/points_per_sweep)*(v_end-v_start),5)) + ","
        sweep += "{:.3E}".format(round(v_start,5))
    return sweep

def runListSweep(parameters,ch1_list,ch2_list,wait=True):
    
    # parameters format (list of strings, units of seconds, amps, volts):
    # [(0) measurment points,(1) time per point,(2) measurement delay,(3) aquisition time,
    #  (4) gate current range,(5) drain current range,(6) gate points,(7) drain points,
    #  (8) premeasurement voltage hold time]
    
    # Trigger TIM minimum of 2E-5
    # Acquisition time minimum of 8E-6
    
    # acq delay should be on the order of 5E-5 or greater
    # Measurement time + acq delay < trigger interval by at least 1E-5
    inst.write(":sour1:volt:lev:imm " + ch1_list.split(',')[0])
    inst.write(":sour2:volt:lev:imm " + ch2_list.split(',')[0])
    
    inst.write(":outp1 on")
    inst.write(":outp2 on")
    
    if wait == True:
        time.sleep(parameters[8])
    
    # Sets the measurement list of voltages for the gate (channel 1)
    inst.write(":sour1:func:mode volt")
    inst.write(":sour1:volt:mode list")
    inst.write(":sour1:list:volt " + ch1_list)
    # Sets the measurement list of voltages for the drain (channel 2)
    inst.write(":sour2:func:mode volt")
    inst.write(":sour2:volt:mode list")
    inst.write(":sour2:list:volt " + ch2_list)

    # Set range and interval for measurement
    inst.write(":sens1:func \"curr\"")
    inst.write(":sens1:curr:rang:auto off")
    inst.write(":sens1:curr:prot " + parameters[4])
    inst.write(":sens1:curr:rang " + parameters[4])
    inst.write(":sens2:func \"curr\"")
    
    inst.write(":sens2:curr:rang:auto off")
    inst.write(":sens2:curr:rang " + parameters[5])
    inst.write(":sens2:curr:prot " + parameters[5])
    
    # Source output ranging set to fixed mode
    inst.write(":sour1:volt:rang:auto off")
    inst.write(":sour1:volt:rang 2")
    inst.write(":sour2:volt:rang:auto off")
    inst.write(":sour2:volt:rang 2")
    # Mesurement wait time set to OFF
    inst.write(":sens1:wait off")
    inst.write(":sour1:wait off")
    inst.write(":sens2:wait off")
    inst.write(":sour2:wait off")
    
    # Set trigger source to the same mode
    inst.write(":trig1:sour tim")
    inst.write("trig1:tim " + parameters[1])
    inst.write("trig1:acq:coun " + parameters[0])
    inst.write(":trig1:acq:del " + parameters[2])
    inst.write("trig1:tran:coun " + parameters[6])
    inst.write(":trig1:tran:del 0")
    inst.write(":trig2:sour tim")
    inst.write("trig2:tim " + parameters[1])
    inst.write("trig2:acq:coun " + parameters[0])
    inst.write(":trig2:acq:del " + parameters[2])
    inst.write("trig2:tran:coun " + parameters[7])
    inst.write(":trig2:tran:del 0")

    # Measurement interval is set to the same value
    inst.write(":sens1:curr:aper " + parameters[3])
    inst.write(":sens2:curr:aper " + parameters[3])
    
    inst.write(":form:elem:sens curr,time")
    
    # Runs the measurement
    inst.write(":init (@1,2)")
    # Fetches the measurement data
    t1 = time.time()
    data_out = inst.query(":fetc:arr? (@1,2)")
    t2 = time.time()
    #print(t1-t2)
    # Convert string of data to numpy array
    data = np.asarray([float(i) for i in data_out.split(',')])
    # Return the measurement results
    
    #inst.write(":syst:beep 800,0.25")
    
    data = np.reshape(data, (int(parameters[0]),4))
    
    return data

def SMU_Res():
    inst.timeout = 120*1e3 
    inst.write("*RST")

    inst.write(":sour:func:mode volt")
    inst.write(":sour:volt " + str(Applied_Voltage))

    inst.write(":sens:func ""curr""")
    inst.write(":sens:curr:rang:auto on")
    inst.write(":sens:curr:nplc 0.1")
    inst.write("sens:curr:prot 0.1")

    inst.write(":outp on")

def SMU_Trans():
    ###     Run TRANSFER curves     ###

    # Settings
    Vg_init = 0.6
    Vg_final = -0.6
    Vd_init = -0.1
    Vd_final = -0.6             # Put same value for Vd_init and Vd_final for 1 measurement
    Vd_step = -0.1              # don't use 0
    time_per_point = 5e-2       # Minimum value of 2e-5
    points_per_sweep = 100
    reverse_sweep = True        
    Ig_range = 1e-5            # Must be 1e-X format, minimum X = 0 maximum X = 7
    Id_range = 1e-2            # Must be 1e-X format, minimum X = 0 maximum X = 7
    t_hold_before_meas = 0.5     

    # ------------------------------------------------------------------------------------------

    # Generate array of gate voltage values based on user input
    Vd_values = np.empty((round((Vd_final-Vd_init)/Vd_step)+1,))
    for i in range(0,len(Vd_values)):
        if Vd_init > Vd_final:
            step = -1*abs(Vd_step)
        else:
            step = abs(Vd_step)
        Vd_values[i] = round(Vd_init + step*i,4)

    # Generate sweep for gate voltage based on user input
    vg_list = generateLinSweep(points_per_sweep,Vg_init,Vg_final,reverse=reverse_sweep)
    vd_list = "{:.1E}".format(Vd_values[0])

    # parameters format (list of strings, units of seconds, amps, volts):
    # [(0) measurment points,(1) time per point,(2) measurement delay,(3) aquisition time,
    #  (4) gate current range,(5) drain current range,(6) gate points,(7) drain points,
    #  (8) pre-measurement voltage hold time]

    parameters = []
    parameters.append("{:.0f}".format(len(vg_list.split(','))))
    parameters.append("{:.1E}".format(time_per_point))
    parameters.append("{:.1E}".format(time_per_point/2))
    parameters.append("{:.1E}".format((time_per_point/2)*0.8))
    parameters.append("{:.0E}".format(Ig_range))
    parameters.append("{:.0E}".format(Id_range))
    parameters.append("{:.0f}".format(len(vg_list.split(','))))
    parameters.append("{:.0f}".format(len(vd_list.split(','))))
    parameters.append(t_hold_before_meas)

    # Create empty array to store output data
    transfer = np.empty((len(Vd_values),int(parameters[0]),4))

    # Run transfer curve for each drain voltage and plot results
    # Run output curve for each gate voltage and plot results
    transfer[0] = runListSweep(parameters,vg_list,vd_list,wait=False)
    print(parameters)
    print(vg_list)
    Vg = np.asarray([float(i) for i in vg_list.split(',')])
    plt.plot(Vg,transfer[0,:,2],label="$V_{DS}$ = " + str(Vd_values[0]))

    for i in range(1,len(transfer)):
        vd_list = "{:.1E}".format(Vd_values[i])
        transfer[i] = runListSweep(parameters,vg_list,vd_list)
        plt.plot(Vg,transfer[i,:,2],label="$V_{DS}$ = " + str(Vd_values[i]))

    plt.gca().invert_yaxis()
    plt.xlabel("$V_{GS}$ (V)")
    plt.ylabel("$I_{DS}$ (A)")
    plt.title("Transfer curves")
    plt.legend()
    plt.plot()

    # Turn SMU output off after all measurements
    inst.write(":outp1 off")
    inst.write(":outp2 off")

def Results(Data):
    Data = Data.split(", ")
    resistances.append(Data[0])
    strains.append(Data[1])
    stresses.append(Data[2])

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.06)
    data =arduino.readline()
    return data.decode('UTF-8')

def Res():
    data_out= inst.query(":meas:curr? (@1)")
    res = Applied_Voltage / float(data_out.strip())
    return res


# ----- Layout Elements -----

Progress_Text = sg.Text("Progress")
Progress = sg.ProgressBar(100, 'horizontal', (50,20), bar_color = '#42f5bf', key = '-PBAR-')

#SMU Connection Window
Layout0 = [[sg.Text("Which port is the SMU connected to?"),
            sg.Combo(values = '', enable_events = True, key = "-CMB1-", size = (60,50))],
           [sg.Button("Skip to Data Recieving", enable_events=True, key ="-BTN4-")]]
#Arduino Connection Window
Layout1 = [[sg.Text("What COM Port is the Arduino Connected to"), 
            sg.Input("8", size = (20,50), key = '-INP1-')],
           [sg.Button("Connect", enable_events= True, key = '-BTN2-')]]
#Input to arduino window
Layout2 = [[sg.Text("Input"), 
            sg.Input("F100, D1000, B100", size  = (20,50), key = '-INP2-'),
            sg.Text("How Many Data Points?"),
            sg.Input("50", enable_events = True, key='-INP3-'),
            sg.Button('Send', enable_events=True, key = '-BTN3-')]]
#Data Recieving Window
Layout3 = [[sg.Text("Sending", enable_events = True, key = '-RTXT1-')],
            [sg.Text("Progress", enable_events = True, key = '-PTXT-')],
            [sg.ProgressBar(100, 'horizontal', (50,20), bar_color = '#42f5bf', key = '-PBAR-')]]



# ----- Full Layout -----
full_layout = [[sg.Column(Layout0, visible = True,  key = '-COL0-')], 
               [sg.Column(Layout1, visible = False, key = '-COL1-')], 
               [sg.Column(Layout2, visible=False, key = '-COL2-')], 
               [sg.Column(Layout3, visible=False, key = '-COL3-')], 
               [sg.Button("Close", enable_events= True, key = '-BTN0-')]]

# ----- Window Creation -----
_VARS['window'] = sg.Window(title = "Demo", layout = full_layout, margins = (50,50), finalize=True)
#drawChart(strains, stresses, resistances)

# ----- Event loop -----

while True:
    event, values = _VARS['window'].read(timeout=50)
    rm = pyvisa.ResourceManager()
    _VARS['window']['-CMB1-'].update(values = rm.list_resources())
    if Connected == True: #Read Arduino Data if connected
        data =arduino.readline().strip().decode('UTF-8')
        time.sleep(0.05) 
    if str(counter) == values['-INP3-']:#Once you get the required amount of data from the arduino stop everything and plot graphs
        plt.plot(np.array(strains)/25 - 1, 'r', label = 'Strains')
        plt.legend()
        plt.show()
        plt.plot(np.array(stresses), 'g', label = 'Stresses')
        plt.legend()
        plt.show()
        plt.plot(np.array(resistances), 'b', label = 'Resistances')
        plt.legend()
        plt.show()
        break
    elif event == "-CMB1-":
        print(values['-CMB1-'])
        _VARS['window'][f'-COL0-'].update(visible = False)
        _VARS['window'][f'-COL1-'].update(visible = True)
        inst = rm.open_resource(values['-CMB1-'])
        print(inst.query("*IDN?"))
    elif event == "-BTN0-" or event == sg.WIN_CLOSED: #Ending app loop
        break
    elif event == '-BTN2-': #Connect to arduino
         arduino = serial.Serial(port = "COM"+values['-INP1-'], baudrate=115200,  timeout=0)
         time.sleep(2)
         Connected = True
         _VARS['window'][f'-COL1-'].update(visible = False)
         _VARS['window'][f'-COL2-'].update(visible = True)
    elif event == '-BTN3-': #Send commands to arduino
         _VARS['window']['-RTXT1-'].update("Should Be Sending")
         print("T" + values['-INP3-'] + ", " + values['-INP2-'] + "*")
         arduino.write(bytes("T" + values['-INP3-'] + ", " + values['-INP2-'] + "*", 'utf-8'))
         SMU_Res()
         time.sleep(0.05)
         #SMU_Trans()
         _VARS['window'][f'-COL2-'].update(visible = False)
         _VARS['window'][f'-COL3-'].update(visible = True)
         _VARS['window']['-PBAR-'].update(current_count = 0, max = values['-INP3-'])
    elif event == "-BTN4-": #Jump to recieveing data without sending commands
         arduino = serial.Serial(port = "COM"+values['-INP1-'], baudrate=115200,  timeout=0)
         time.sleep(2)
         Connected = True
         _VARS['window'][f'-COL0-'].update(visible = False)
         _VARS['window'][f'-COL3-'].update(visible = True)
         _VARS['window']['-PBAR-'].update(current_count = 0, max = values['-INP3-'])
    if data.strip() != '': #If valid data recieved in the Serial Channel, save it and add it to the corresponding list
         _VARS['window']['-RTXT1-'].update(data.strip())
         data = data.split(", ")
         strains.append(50- (float(data[0]) *50)/1023)
         stresses.append(float(data[1]))
         resistances.append(Res())
         time.sleep(0.05)
         counter += 1
         _VARS['window']['-PTXT-'].update(counter)
         _VARS['window']['-PBAR-'].update(current_count = counter)

_VARS['window'].close()