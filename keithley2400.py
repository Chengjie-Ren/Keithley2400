#Keithley 2400
#This script enables to communicate with the keithley 2400 and 2401 instruments
#Configurations as voltmeter only and as a voltage current source/current sensing available
#Measurement function also provided
#gpib/rs232 com possible


import visa
import time
import numpy

class Keithley2400:

    def __init__(self):
        self.port = 'Com20'
        self.gpib_port = 25
        self.data_entry = 5
        self.trigger_count = 1
        self.delay = 5
        self.nplc = 1
        self.rm = None
        self.inst = None
          
    def open_com(self):
        self.rm = visa.ResourceManager();
        address = 'GPIB0::' + str(self.gpib_port) + '::INSTR'
        self.inst = self.rm.open_resource(address)
        print 'Com open'

    def close_com(self):
        #Set instrument in local mode
        res = self.send_cmd("SYST:LOC")
        time.sleep(1)
        #Close instrument connection
        self.inst.close()
        #Close visa session
        res = self.rm.close()
        return res
        
    def send_query(self, command):
        out = self.inst.query(command, self.delay);
        res = self.inst.query("SYSTem:ERRor?");
        return out

    def send_cmd(self, command):
        res = self.inst.write(command);
        return res

    def config_voltmeter(self):
        res = self.send_cmd("*RST")
        res = self.send_cmd(":SOUR:FUNC CURR")
        res = self.send_cmd(":SOUR:CURR:MODE FIX")
        res = self.send_cmd(":SOUR:CURR:RANGE:AUTO ON")
        res = self.send_cmd(":SOUR:CURR:LEV 0")
        res = self.send_cmd(":SENS:FUNC \"VOLT\"")
        res = self.send_cmd(":SENS:VOLT:PROT 10")
        res = self.send_cmd(":SENS:VOLT:RANG 10")
        res = self.send_cmd(":SENS:VOLT:NPLC " + str(self.nplc))
        res = self.send_cmd(":TRIG:COUN " + str(self.trigger_count))
        return res

    def config_source_meter(self,volt_source_range,volt_limit,curr_sense_range,curr_limit):
        res = self.send_cmd("*RST")
        res = self.send_cmd(":SOUR:FUNC VOLT")
        res = self.send_cmd(":SOUR:VOLT:MODE FIX")
        res = self.send_cmd(":SENS:VOLT:PROT 10")
        res = self.send_cmd(":SOUR:VOLT:RANG " + str(volt_source_range))
        res = self.send_cmd(":SOUR:VOLT:LEV 0")
        res = self.send_cmd(":SENS:FUNC \"CURR\"")
        res = self.send_cmd(":SENS:CURR:PROT " + str(curr_limit))
        res = self.send_cmd(":SENS:CURR:RANG " + str(curr_sense_range))
        res = self.send_cmd(":TRIG:COUN "+str(self.trigger_count))
        return res

    def setsource_volt(self, voltage):
        res = self.send_cmd(":SOUR:VOLT:LEV " + str(voltage))
        print 'Voltage set'
        return res

    def remote_sensing(self, mode):
        if mode=='on':
            res = self.send_cmd(":SYST:RSEN ON")
        else:
            res = self.send_cmd(":SYST:RSEN OFF")
        return res

    def config_sourcemeter_cur(self):
        res = self.send_cmd("*RST")
        res = self.send_cmd(":SOUR:FUNC CURR")
        res = self.send_cmd(":SOUR:CURR:MODE FIX")
        res = self.send_cmd(":SOUR:CURR:RANG 100e-6")
        res = self.send_cmd(":SOUR:CURR:LEV 0")
        res = self.send_cmd(":SENS:FUNC \"CURR\"")
        res = self.send_cmd(":SENS:CURR:PROT 100e-3")
        res = self.send_cmd(":SENS:CURR:RANG 100e-6")
        res = self.send_cmd(":TRIG:COUN " + str(10))
        return res

    def setsource_cur(self, current):
        res = self.send_cmd(":SOUR:CURR:LEV " + str(current))
        return res

    def output_enable(self, state):
        if state=='on':
            mes = ':OUTP ON'
            print 'Source on'
        else:
            mes = ':OUTP OFF'
            print 'Source off'
        res = self.send_cmd(mes)
        return res

    def measure(self):
        try:
            print('Measuring')
            out = self.send_query("READ?")
        except visa.VisaIOError:
            print('The keithley instrument could not complete the read command')
            
        rawdata = numpy.array(out.split(','))
        float_arr = numpy.vectorize(float)
        data = float_arr(rawdata)
        #The assumption here is that the volt and current  are the first 2 columns
        return data

#returned string format
#You can amend it using :FORM:DATA: and :FORM:ELEM See Ch18-48
#+2.000812E+00,+9.910000E+37,+9.910000E+37,+7.408841E+03,+1.946000E+04
#volt, curr,res,time,status


    
    
