import PySimpleGUI as sg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import time
sg.theme("TealMono")

#arduino_port = input("What port is the Arduino connected to? ")
arduino = serial.Serial(port = "COM10", baudrate=9600,  timeout=0)
time.sleep(2)



# ----- Variables -----
_VARS = {'window': False,
         'fig_agg': False,
         'pltFig': False}

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

def drawChart():
    _VARS['pltFig'] = plt.figure(figsize=(3,3))
    data = makeSynthData()
    plt.plot(data[0], data[1], '.k')
    _VARS['fig_agg'] = draw_figure(_VARS['window']['-CNVS-'].TKCanvas, _VARS['pltFig'])

# ----- Layout Elements -----
Rawtext1 = sg.Text("Raw Text", enable_events = True, key = '-RTXT1-')
Rawtext2 = sg.Text("LED STATUS", enable_events = True, key = '-RTXT2-')
Input = sg.Text("Input"), sg.Input("Input Here", (20,50))
Slider = sg.Text("Slider"), sg.Slider((0,100), 0, 0.1, orientation='horizontal', enable_events = True, key = '-SL-')
Combo = sg.Text("Combo"), sg.Combo(("#42f5bf", "red", "white"), "#42f5bf", (20,50), enable_events = True, key = '-CMB-')
Checkbox = sg.Text("Checkbox"), sg.Checkbox("Default Checked", True)
Radio1 = sg.Radio("LED On", 1 , False, enable_events = True, key = '-LEDH-')
Radio2 = sg.Radio("LED Off", 1 , False, enable_events = True, key = '-LEDL-')
Spin = sg.Text("Spin"), sg.Spin(("1", "2", "3", "4", "5", "6",), 1, (100,50))
Image = sg.Text("Image"), sg.Image('Logo.png', expand_x=True, expand_y=True )
Progress = sg.Text("Progress"), sg.ProgressBar(100, 'horizontal', (50,50), bar_color = '#42f5bf', key = '-PBAR-')
Button = sg.Button('Close', enable_events=True, key = '-BTN-')
Canvas = sg.Canvas(key = '-CNVS-', size = (2,2))
Tab1 = sg.Tab('Tab 1', [Slider, Combo, [Rawtext1], Progress])
Tab2 = sg.Tab('Tab 2', [Input, Checkbox, Spin])
Tab3 = sg.Tab('Tab 3', [[Canvas]])
Tab4 = sg.Tab('Tab 4', [[Rawtext2], [Radio1], [Radio2]])


# ----- Full Layout -----
full_layout = [[sg.TabGroup([[Tab1, Tab2, Tab3, Tab4]])],
               [Button],                  
]

# ----- Window Creation -----
_VARS['window'] = sg.Window(title = "Demo", layout = full_layout, margins = (50,50), finalize=True)
drawChart()

# ----- Event loop -----
while True:
    event, values = _VARS['window'].read()
    print(event)
    if event == '-SL-':
         _VARS['window']['-PBAR-'].update(values['-SL-'])
         _VARS['window']['-RTXT1-'].update(int(values['-SL-']))
    elif event == '-CMB-':
         _VARS['window']['-PBAR-'].update(bar_color = values['-CMB-'])
    elif event == '-LEDH-':
        arduino.write(str.encode('1'))
        time.sleep(1)
        msg = arduino.readline().decode()
        time.sleep(1)
        _VARS['window']['-RTXT2-'].update(msg)
    elif event == '-LEDL-':
        arduino.write(str.encode('0'))
        time.sleep(1)
        msg = arduino.readline().decode()
        time.sleep(1)
        _VARS['window']['-RTXT2-'].update(msg)
    elif event == "-BTN-" or event == sg.WIN_CLOSED:
        break

_VARS['window'].close()