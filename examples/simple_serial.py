import collections
import tkinter as tk
import tkinter.ttk as ttk
import serial
import matplotlib.pyplot as plt

import numpy as np

import sys
sys.path.append('..')
import time
import pypogs
from pathlib import Path
from threading import Thread, Event

import cProfile

LARGE_FONT = ("Verdana", 18)
small_FONT = ("Verdana", 12)


class first_program(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = StartPage(container, self)

        self.frames[StartPage] = frame

        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        err_integral = np.array([0, 0], dtype='float64')
        print(err_integral[0])

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


def qf(quickPrint):
    print(quickPrint)


class StartPage(ttk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Loop management
        self._stop_loop = False
        self._plot_loop = True
        self._thread = None
        self.tt = None
        self.cam = None
        self.mems = None

        self._x_diff_mV = 0
        self._y_diff_mV = 0
        self._step_mV = 1000

        self._thread_plot = Thread(target=self.timer_callback, name='Worker')
        self._thread_plot.start()

        label = tk.Label(self, text="**Simple serial write app**", fg='blue', font=small_FONT)
        label.grid(row=0, column=0)

        # Create button1 for connect to serial
        label = tk.Label(self, text="Connect COM port:", font=small_FONT) \
            .grid(row=2, column=0)
        ttk.Button(self, text='Connect COM', command=self.button1_callback, width=20) \
            .grid(row=2, column=2)

        # Create buttons for init
        ttk.Button(self, text='Full_reset', command=self.button7_callback, width=12) \
            .grid(row=3, column=3)

        # Create buttons for sending channels
        label = tk.Label(self, text="| WRITE to DAC channels |", font=small_FONT) \
            .grid(row=5, column=3)
        ttk.Button(self, text='Channel_A', command=self.button2_callback, width=12) \
            .grid(row=6, column=1)
        ttk.Button(self, text='Channel_B', command=self.button3_callback, width=12) \
            .grid(row=6, column=2)
        ttk.Button(self, text='Channel_C', command=self.button4_callback, width=12) \
            .grid(row=6, column=3)
        ttk.Button(self, text='Channel_D', command=self.button5_callback, width=12) \
            .grid(row=6, column=4)
        ttk.Button(self, text='BIAS', command=self.button6_callback, width=12) \
            .grid(row=6, column=7)

        # Buttons for Filter clock and ENABLE
        self.button_fc = ttk.Button(self, text='Filter_cl_Disable', command=self.button8_callback, width=15)
        self.button_fc.grid(row=3, column=4)

        self.button_en = ttk.Button(self, text='Driver_Disable', command=self.button9_callback, width=15)
        self.button_en.grid(row=3, column=5)

        # Create User input box
        self.user_spinbox1 = ttk.Spinbox(self, from_=0, to=65536, width=10)
        self.user_spinbox1.grid(row=7, column=1)
        self.user_spinbox1.delete(0, 'end')
        self.user_spinbox1.insert(0, '1')  # Set default 1#
        # Create User input box
        self.user_spinbox2 = ttk.Spinbox(self, from_=0, to=65536, width=10)
        self.user_spinbox2.grid(row=7, column=2)
        self.user_spinbox2.delete(0, 'end')
        self.user_spinbox2.insert(0, '1')  # Set default 1#
        # Create User input box
        self.user_spinbox3 = ttk.Spinbox(self, from_=0, to=65536, width=10)
        self.user_spinbox3.grid(row=7, column=3)
        self.user_spinbox3.delete(0, 'end')
        self.user_spinbox3.insert(0, '1')  # Set default 1#
        # Create User input box
        self.user_spinbox4 = ttk.Spinbox(self, from_=0, to=65536, width=10)
        self.user_spinbox4.grid(row=7, column=4)
        self.user_spinbox4.delete(0, 'end')
        self.user_spinbox4.insert(0, '1')  # Set default 1#
        # Create User input box
        self.user_spinbox5 = ttk.Spinbox(self, from_=0, to=65536, width=10)
        self.user_spinbox5.grid(row=7, column=7)
        self.user_spinbox5.delete(0, 'end')
        self.user_spinbox5.insert(0, '32000')  # Set default 1#
        #
        # New buttons for X and Y
        ttk.Button(self, text='X_diff mV', command=self.X_callback, width=12) \
            .grid(row=9, column=3)
        ttk.Button(self, text='Y_diff mV', command=self.Y_callback, width=12) \
            .grid(row=9, column=4)
        # Create User input box
        self.user_spinbox6 = ttk.Spinbox(self, from_=0, to=65536, width=10)
        self.user_spinbox6.grid(row=10, column=3)
        self.user_spinbox6.delete(0, 'end')
        self.user_spinbox6.insert(0, '1')  # Set default 1#
        # Create User input box
        self.user_spinbox7 = ttk.Spinbox(self, from_=0, to=65536, width=10)
        self.user_spinbox7.grid(row=10, column=4)
        self.user_spinbox7.delete(0, 'end')
        self.user_spinbox7.insert(0, '1')  # Set default 1#

        # #Create label
        label2 = tk.Label(self, text="Output_window:", font=small_FONT) \
            .grid(row=8, column=0)
        #
        # Create program output label
        self.label3 = tk.Label(self, text="", bg="White", font=small_FONT, width=22)
        self.label3.grid(row=9, column=0)

        # New button for user
        ttk.Button(self, text='Init tracking', command=self.user_callback, width=12) \
            .grid(row=11, column=1)
        # button for user start stop
        ttk.Button(self, text='Start/Stop', command=self.start_stop_callback, width=12) \
            .grid(row=11, column=2)

    # Method to connect to COM port
    def button1_callback(self):
        # Creates mems object and initialize
        self.mems = Mirror()

    # Methods for sending commands
    def button2_callback(self):
        value = int(self.user_spinbox1.get())
        value = 'M30' + str(value)
        self.label3['text'] = value
        self.mems.send_command(value)

    def button3_callback(self):
        value = int(self.user_spinbox2.get())
        value = 'M31' + str(value)
        self.label3['text'] = value
        self.mems.send_command(value)

    def button4_callback(self):
        value = int(self.user_spinbox3.get())
        value = 'M32' + str(value)
        self.label3['text'] = value
        self.mems.send_command(value)

    def button5_callback(self):
        value = int(self.user_spinbox4.get())
        value = 'M33' + str(value)
        self.label3['text'] = value
        self.mems.send_command(value)

    def button6_callback(self):
        value = int(self.user_spinbox5.get())
        value = 'M27' + str(value)
        self.label3['text'] = value
        self.mems.send_command(value)

    def button7_callback(self):
        # 1. SPI sequence Full reset first to make sure disable
        self.mems.disable_mems()
        value = ['M500001', 'M700001', 'M400015', 'M600000']
        for var in value:
            self.send_command(var)
        print('Full reset')

    def button8_callback(self):
        filter_ON = 'C001'
        filter_OFF = 'S001'
        if self.button_fc.cget('text') == 'Filter_cl_Disable':
            self.button_fc.configure(text='Filter_cl_Enable')
            self.mems.send_command(filter_ON)
            self.label3['text'] = filter_ON
            print('MEMS Filter ON')
        else:
            self.button_fc.configure(text='Filter_cl_Disable')
            self.mems.send_command(filter_OFF)
            self.label3['text'] = filter_OFF
            print('MEMS Filter OFF')

    def button9_callback(self):
        if self.button_en.cget('text') == 'Driver_Enable':
            self.button_en.configure(text='Driver_Disable')
            self.mems.set_BIAS()
            self.mems.disable_mems()
        else:
            self.button_en.configure(text='Driver_Enable')
            self.mems.enable_mems()
            self.label3['text'] = 'D001'

    def X_callback(self):
        Vdiff_mV = self.user_spinbox6.get()
        self.mems.send_X(Vdiff_mV)

    def Y_callback(self):
        Vdiff_mV = self.user_spinbox7.get()
        self.mems.send_Y(Vdiff_mV)

    def user_callback(self):
        self.Init_camera()

    def Init_camera(self):
        try:
            # Create a camera instance (see pypogs.camera.Camera)
            self.cam = pypogs.Camera(model='ptgrey', identity='18285284', name='CoarseCam')

            # COARSE/STAR
            self.cam.exposure_time = 4  # 450
            self.cam.gain = 0
            self.cam.frame_rate = 4
            self.cam.binning = 2
            self.cam.plate_scale = 20.3
            self.cam.start()
            # img = cam.get_latest_image()

            # Create a TrackingThread instance
            self.tt = pypogs.TrackingThread(camera=self.cam, name='CoarseTrackThread')

            self.tt.goal_x_y = [0, 0]  # goal is center of image
            self.tt.spot_tracker.image_th = 2000
            self.tt.spot_tracker.max_search_radius = 500
            self.tt.spot_tracker.min_search_radius = 100
            self.tt.spot_tracker.crop = (256, 256)
            self.tt.spot_tracker.spot_min_sum = 500
            self.tt.spot_tracker.bg_subtract_mode = 'local_median'
            self.tt.spot_tracker.sigma_mode = 'local_median_abs'
            self.tt.spot_tracker.fails_to_drop = 10
            self.tt.spot_tracker.smoothing_parameter = 8
            self.tt.spot_tracker.rmse_smoothing_parameter = 8
            self.tt.feedforward_threshold = 10

            # (Optional) set up a directory for image saving at .5 Hz
            self.tt.image_folder = Path('./tracking_images')
            self.tt.img_save_frequency = 0.5
            print("Camera and tracking thread works")
        except BaseException:
            print("Camera and tracking error")

    def start_stop_callback(self):
        if not self._stop_loop:
            self._stop_loop = True
            self.tt.start()
            self._thread = Thread(target=self._run, name='Worker')
            self._thread.start()
            print("Thread started")
        else:
            self._stop_loop = False
            self._plot_loop = False
            self.tt.stop()
            self.cam.deinitialize()
            print("Thread Stopped")

    def timer_callback(self):
        # Method for plotting
        data_list = collections.deque(maxlen=100)
        time.sleep(1)
        while self._plot_loop:
            time.sleep(1)
            new_var = self._x_diff_mV
            if new_var is not None:
                data_list.append(new_var)
                plt.clf()
                plt.plot(data_list)
                plt.ylabel('X_diff')
                plt.show(block=False)
                plt.pause(0.001)

    # _______________________________________MAIN LOOP________________________________________
    def _run(self):

        while self._stop_loop:  # While the variable is true
            time.sleep(0.1)
            # Get position of track
            print(self.tt.spot_tracker.track_x_y)
            (star_x, star_y) = self.tt.spot_tracker.track_x_y
            if star_x is not None:
                print(  (int)(star_x / self.cam.plate_scale), (int)(star_y / self.cam.plate_scale))

                error_x = star_x / self.cam.plate_scale
                error_y = star_x / self.cam.plate_scale
                # Calculate input for driver___________________________
                if error_x > 1:  # Tild right
                    self._x_diff_mV = self._x_diff_mV - self._step_mV
                elif error_x < 0:  # Tild left
                    self._x_diff_mV = self._x_diff_mV + self._step_mV

                # Send values for mirror_______________________________
                self.mems.send_X(self._x_diff_mV)


class Mirror:
    def __init__(self):
        """Create Mount instance. See class documentation."""
        # Start of constructor
        self._model = None
        self._name = 'MEMS'
        self._is_init = False
        self._minLimit = 10405  # decimal value for MEMS - 30 V
        self._maxLimit = 45090  # decimal value for MEMS - 130 V
        self._identity = 'COM3'
        self._mems_serial_port = None
        self._bias_value = ['M3026011', 'M3125625', 'M3225733', 'M3325625']
        self._prior_values = [26011, 25625, 25733, 25625]
        self._max_step = 1730  # 10V step
        self.initialize()

        self._x_diff_mV = 0
        self._y_diff_mV = 0
        self._step_mV = 0

        # Try to get Python to clean up the object properly
        import atexit, weakref
        atexit.register(weakref.ref(self.__del__))

    def __del__(self):
        """Destructor, try to disconnect MEMS."""
        try:
            self.deinitialize()
            print('MEMS deinit')
        except:
            pass

    def initialize(self):
        """Initialise (make ready to start) the device. The model and identity must be defined."""
        assert not self._is_init, 'Already initialised'
        try:
            self._mems_serial_port = serial.Serial(self.identity, 9600, parity=serial.PARITY_NONE,
                                                   stopbits=serial.STOPBITS_ONE, timeout=3.5, write_timeout=3.5)
        except serial.SerialException:
            print('Failed to open MEMS port')
        self._mems_serial_port.flush()
        self._is_init = True

        # 1. SPI sequence Full reset first to make sure disable_____________________________________________
        self.disable_mems()
        value = ['M500001', 'M700001', 'M400015', 'M600000']
        for var in value:
            self.send_command(var)
        print('Full reset')

        # 2. Send Vbias ______________________________________________
        self.set_BIAS()

        # 3. Enable filter clock ______________________________________________
        filter_ON = 'C001'
        filter_OFF = 'S001'
        self.send_command(filter_ON)
        print('Filter ON')

        # 4. Enable MEMS ______________________________________________

    def deinitialize(self):
        """De-initialise the device and release hardware (serial port). Will stop the mirror if it is moving."""
        assert self._is_init, 'Not initialised'
        try:
            self.stop()
        except:
            print('MEMS did not stop')
        self._mems_serial_port.close()
        self._mems_serial_port = None
        self._is_init = False
        print('MEMS deinitialised')

    @property
    def identity(self):
        return self._identity

    @property
    def x_diff_mV(self):
        return self._x_diff_mV

    @property
    def y_diff_mV(self):
        return self._y_diff_mV

    @property
    def step_mV(self):
        return self._step_mV

    def stop(self):
        """Stop moving. Turn off """
        # 1. Send BIAS to return to original position
        # 2. Disable MEMS by sending digital low to PIN5 on J1. Warning
        # DO NOT UNPLUG or disable input SPI port prior this step
        for var in self._bias_value:
            self.send_command(var)
        self.disable_mems()

    def disable_mems(self):
        """Disable MEMS driver Pin5"""
        off = 'D001'
        self.send_command(off)
        print('MEMS DISABLE')

    def enable_mems(self):
        """Enable MEMS driver Pin5"""
        enable = 'E001'
        self.send_command(enable)
        print('MEMS ENABLE')

    def set_BIAS(self):
        for var in self._bias_value:
            self.send_command(var)
        print('Bias setted')

    def send_X(self, value):
        """Send Vdiff values to A and B channels"""
        Vdiff_mV = int(value)
        bias_X = (int)(self._bias_value[0][3:8])
        bias_Xn = (int)(self._bias_value[1][3:8])
        # Vdiff convertion to decimal values
        value_X_dec = bias_X + (int)((Vdiff_mV / 2) * 0.346)
        value_nX_dec = bias_Xn - (int)((Vdiff_mV / 2) * 0.346)
        # Check limits
        if (self._minLimit < value_X_dec < self._maxLimit and
                self._minLimit < value_nX_dec < self._maxLimit):
            # Check step size
            if (abs(self._prior_values[0] - value_X_dec) < self._max_step and
                    abs(self._prior_values[1] - value_nX_dec) < self._max_step):
                # Save last values
                self._prior_values[0] = value_X_dec
                self._prior_values[1] = value_nX_dec
                # send X positive channel
                value_X_dec = 'M30' + str(value_X_dec)
                self.send_command(value_X_dec)
                # send Xminus channel
                value_nX_dec = 'M31' + str(value_nX_dec)
                self.send_command(value_nX_dec)
            else:
                print('ERROR: Step size to BIG')
        else:
            print('ERROR: Voltage limit exceeded')

    def send_Y(self, value):
        """Send Vdiff values to C and D channels"""
        Vdiff_mV = int(value)
        bias_Y = (int)(self._bias_value[2][3:8])
        bias_Yn = (int)(self._bias_value[3][3:8])
        # Vdiff convertion to decimal values
        value_Y_dec = bias_Y + (int)((Vdiff_mV / 2) * 0.346)
        value_nY_dec = bias_Yn - (int)((Vdiff_mV / 2) * 0.346)
        # Check limits
        if (self._minLimit < value_Y_dec < self._maxLimit and
                self._minLimit < value_nY_dec < self._maxLimit):
            # Check step size
            if (abs(self._prior_values[0] - value_Y_dec) < self._max_step and
                    abs(self._prior_values[1] - value_nY_dec) < self._max_step):
                # Save last values
                self._prior_values[2] = value_Y_dec
                self._prior_values[3] = value_nY_dec
                # send X positive channel
                value_Y_dec = 'M32' + str(value_Y_dec)
                self.send_command(value_Y_dec)
                # send Xminus channel
                value_nY_dec = 'M33' + str(value_nY_dec)
                self.send_command(value_nY_dec)
            else:
                print('ERROR: Step size to BIG')
        else:
            print('ERROR: Voltage limit exceeded')

    def send_command(self, command):
        """Send value to MEMS. With protections """
        # Check command legitimacy and send via serial
        try:
            # 1. Check length. Min 4 char - Max 8
            if 3 < len(command) < 9:
                # 2. Check if first letter is correct, only: M D E S C
                fc = command[0]  # first character
                if fc == 'D' or fc == 'E' or fc == 'S' or fc == 'C':
                    self._mems_serial_port.write((command + '\n').encode('ASCII'))
                # 2.5. Special case - full reset sequence
                elif fc == 'M' and not command[1] == '3':
                    self._mems_serial_port.write((command + '\n').encode('ASCII'))
                # 3. If letter M, then check is the decimal value in range
                elif fc == 'M':
                    var_string = command[3:len(command)]
                    if var_string.isdigit():
                        var_int = int(var_string)
                        if self._minLimit < var_int < self._maxLimit:
                            self._mems_serial_port.write((command + '\n').encode('ASCII'))
                        else:
                            print('Voltage out of limit')
                    else:
                        print('Command is not a number')
                else:
                    print('Command first char ir not correct')
            else:
                print('Command wrong length')
        except:
            print('Wrong command format for MEMS')


app = first_program()
app.mainloop()
