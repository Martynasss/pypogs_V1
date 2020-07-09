# External imports:
import numpy as np
import serial

class Mirror:
    def __init__(self):
        """Create Mount instance. See class documentation."""
        # Start of constructor
        self._model = None
        self._name = 'MEMS'
        self._is_init = False
        self._minLimit = 10405  # decimal value for MEMS - 30 V
        self._maxLimit = 45090  # decimal value for MEMS - 130 V
        self._identity = 'COM4'
        self._mems_serial_port = None
        self._bias_value = ['M3026011', 'M3125625', 'M3225733', 'M3325625']
        self._prior_values = [26011, 25625, 25733, 25625]
        self._max_step = 1730  # 10V step
        self.initialize()

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
        assert not self.is_init, 'Already initialised'
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
        for var in self._bias_value:
            self.send_command(var)
        print('Bias setted')

        # 3. Enable filter clock ______________________________________________
        filter_ON = 'C001'
        filter_OFF = 'S001'
        self.send_command(filter_ON)
        print('Filter ON')

        # 4. Enable MEMS ______________________________________________

    def deinitialize(self):
        """De-initialise the device and release hardware (serial port). Will stop the mirror if it is moving."""
        assert self.is_init, 'Not initialised'
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
    def is_init(self):
        return self._is_init

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