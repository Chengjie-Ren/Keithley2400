from keithley2400 import Keithley2400
from datetime import datetime
import numpy
import schedule
import time
import sys
import winsound
import math

amb = []
def save_data(data, file_name, map_temp):
    tempo = datetime.today() # get timestamp
    data_str = str(tempo) # save to string
    
    i = 0
    while i < 2: # loop through data
        data_str = data_str + ',' + str(data[i]) # append string
        i += 1
    pwr = data[0] * data[1]
    res = data[0] / data[1]
    data_str = data_str + ',' + str(res) + ',' + str(pwr) # add resistance & power
    if map_temp == True:
        print(amb)
        if amb is not []:
            #data_str = data_str + ',' + str(temp_cal(amb[0][0], amb[0][1], data[1], data[0]))
            t = temp_TCR_cal(res)
            data_str = data_str + ',' + str(t)
            if t>350:
                print('Temperature too high')
                raise ValueError
        else:
            #print('vamb and iamb not set')
            exit_handler()
    data_str = data_str + '\n' # add new line
    print(data_str) # print data string

    f = open(file_name,'a') # open file           
    f.write(data_str) # write data
    f.close() # close file

#Function to calculate TCRs from resistance
def temp_TCR_cal(R_heated, res_heater=36, res_track_on=9, res_track_off=3+2.5):
    res_heat = res_heater + res_track_on/3
    res_non_heat = res_track_on*2/3 + res_track_off
    R_heated = R_heated - res_non_heat
    TCR1 = -4.478e-3 * res_heat/340 + 3.7765e-3
    TCR2 = 0.4e-6
    T_heat = (-TCR1 + math.sqrt(TCR1**2 - 4*TCR2*(1-R_heated/res_heat)))/(2*TCR2)+25
    return T_heat
#Function to caculate temperature 
def  temp_cal(vamb,iamb,i,v):
    #TCR values - 113C CVD
    tcr1=2.05e-3
    tcr2=3.00e-7
    trh=0.766
    trm=0.928
    #Ambient temperature (C)
    tamb=25
    
    Rm0=vamb/iamb
    Rh0=Rm0*trh
    vcalc=i*(Rh0+(v/i-Rm0)*trm) 
    c=1-((vcalc/i)/Rh0)
    t=((-tcr1+math.sqrt(tcr1*tcr1-4*tcr2*c))/2/tcr2) + tamb
    return t


def save_header(header_str, file_name):
    print('header saved', header_str)
    f = open(file_name,'w')
    f.write(header_str)
    f.close()

def exit_handler():
    sourceMeter.output_enable('off') # disable output
    sourceMeter.close_com # close come
    sys.exit() # exit program
    sys.exit()

def capture(file_name, low_cur_limit, low_current, map_temp = False):
    data = sourceMeter.measure() # measure
    if data[1] < low_cur_limit: # exit if current lower than limit
        winsound.Beep(1000, 1000)
        #exit_handler()
    if abs(data[1] -low_current) < low_current and len(amb) < 1:
        vamb, iamb = data[0], data[1]
        amb.append((vamb,iamb))
        print('vamb and iamb set')
        print(vamb, iamb)
    #print("data: " + str(data[0]) + ' ' + str(data[1]))
    save_data(data, file_name, map_temp) # save data
        
if __name__=="__main__" :
    #file_name = 'logfile_CCS_83_F_H10133#06_East_Chip1-5.csv' # log file name
    file_name = 'IV-characteristics-Flusor_sensor_with_double_hole.csv' # log file name
    low_voltage = 0.05 # low voltage.
    low_current = 0.001
    low_volt_source_range = 0.2 # low voltage range
    low_volt_limit = 0.2 # low voltage limit
    low_curr_limit = 1e-3 # low current limit 
    low_curr_sense_range = 0.01 # low current range 
        
    high_volt_source_range = 10 # high voltage range
    high_volt_limit = 10 # high voltage limit
    high_curr_limit = 0.015 # high current limit 
    high_curr_sense_range = 1 # high current range
     
    low_voltage_limit = 2.8
    voltage_step = 0.05
    current_step = 0.001 #set the current step for sweeping
    
    voltage_array = numpy.arange(low_voltage_limit,high_volt_limit,voltage_step) #voltage array
    current_array = numpy.arange(low_curr_limit,high_curr_limit,current_step) #current array
    
    low_curr_limit = 0.01 # low current limit
    open_curr_limit = 0.0001 # open circuit current limit
    
    header_str = 'Timestamp,V[V],I[A],R[Ohms],W[W],T[°C]\n' # header string
    on_delay = 0.5 # on time delay
    off_delay = 0.5 # off time delay
                                     
    sourceMeter = Keithley2400() # create instance 
    sourceMeter.open_com() # open come

    save_header(header_str,file_name) # save header

    # Low voltage measurement
    #sourceMeter.config_source_meter(low_volt_source_range,low_volt_limit,low_curr_sense_range,low_curr_limit) # configure source meter

    #set the parameters for current source configuration
    volt_sense_prot = 1.5
    volt_sense_range = 1.5
    cur_source_range = 10e-3
    sourceMeter.config_sourcemeter_cur(volt_sense_prot, volt_sense_range, cur_source_range)
    sourceMeter.remote_sensing('off') # remote sensing
    
    #sourceMeter.setsource_volt(low_voltage) # set voltage

    
   
    sourceMeter.setsource_cur(low_current) #set low current
    sourceMeter.output_enable('on') # enable output
    time.sleep(2) # delay
    
    #data = sourceMeter.measure() # measure
    #save_data(data, file_name) # save data
    
    capture(file_name, open_curr_limit,low_current, map_temp = True) # capture data
        
    # High voltage measurement
    #sourceMeter.config_source_meter(high_volt_source_range,high_volt_limit,high_curr_sense_range,high_curr_limit) # configure source meter
    '''        
    for set_voltage in voltage_array: # loop through voltages
        print('Setting voltage = ' + str(set_voltage)) # print voltage
        sourceMeter.setsource_volt(set_voltage) # set voltage
        sourceMeter.output_enable('on') # enable output
        time.sleep(on_delay) # delay
        capture(file_name, open_curr_limit) # capture data
        #sourceMeter.output_enable('off') # disable output
        #time.sleep(off_delay) # delay
    
    '''
    for set_current in current_array: # loop through current
        print('Setting current = ' + str(set_current)) # print current
        sourceMeter.setsource_cur(set_current) # set current
        sourceMeter.output_enable('on') # enable output
        time.sleep(on_delay) # delay
        capture(file_name, open_curr_limit, low_current, map_temp = True) # capture data
        #sourceMeter.output_enable('off') # disable output
        #time.sleep(off_delay) # delay

    # Turn off com port and source after finished
    sourceMeter.output_enable('off')
    sourceMeter.close_com()
    
        
    
    
