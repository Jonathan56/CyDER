#######################################################
# Script with unit tests for SimulatorToFMU
#
# TSNouidui@lbl.gov                          2016-09-06
#######################################################
import unittest
import os
import sys
import platform
import subprocess
import shutil
from datetime import datetime
from time import sleep
import matplotlib.pyplot as plt

# Appending parser_path to the system path os required to be able
# to find the SimulatorToFMU model from this directory
script_path = os.path.dirname(os.path.realpath(__file__))
parser_path = os.path.abspath(os.path.join(script_path, '..', 'parser'))
sys.path.append(parser_path)


def run_simulator ():

    '''
    Function for running an OPAL-RT FMU exported with JModelica 2.0 using PyFMI.

    '''

    try:
        from pyfmi import load_fmu
    except BaseException:
        print ('PyFMI not installed. Script will not be be run.')
        return

    fmu_path = 'Simulator.fmu'
    # Parameters which will be arguments of the function

    #step_size = 1.0
	
    sim_tim=[]
    sim_res=[]
	# Create the simulation grid
    time_grid=[0,1,2,3,4]
    start_time = time_grid[0]
    stop_time = time_grid[-1]
	# Create the on/off control sequence
    con_sig=[0,1,0,1,0]

    print ('Starting the simulation')
    start = datetime.now()

    simulator_input_valref = []
    simulator_output_valref = []

    sim_mod = load_fmu(fmu_path, log_level=7)

    sim_mod.setup_experiment(
        start_time=start_time, stop_time=stop_time)

    # Define the inputs
    simulator_input_names = ['LBNL_test1_sc_console_port1']
    simulator_input_values = [0.0]
    #simulator_input_values = [1.0]
    simulator_output_names = ['LBNL_test1_Sm_master_port1_1_', 'LBNL_test1_Sm_master_port1_2_',
    'LBNL_test1_Sm_master_port1_3_','LBNL_test1_Sm_master_port1_4_','LBNL_test1_Sm_master_port1_5_',
    'LBNL_test1_Sm_master_port1_6_','LBNL_test1_Sm_master_port1_7_','LBNL_test1_Sm_master_port1_8_',
    'LBNL_test1_Sm_master_port1_9_']
    # This could be set if the FMU is exported using Dymola. Using JModelica, the configuration
    # file path will be encoded in the FMU itself. This is a known limitation of JModelica

    # Get the value references of simulator inputs
    for elem in simulator_input_names:
        simulator_input_valref.append(
            sim_mod.get_variable_valueref(elem))

    # Get the value references of simulator outputs
    for elem in simulator_output_names:
        simulator_output_valref.append(
            sim_mod.get_variable_valueref(elem))

    # Set the flag to save the results
    sim_mod.set('_saveToFile', 0)

    # Get value reference of the configuration file
    #config_con_val_ref = sim_mod.get_variable_valueref("_configurationFileName")

    # Set the configuration file
    #sim_mod.set_string([config_con_val_ref], [config_file])

    # Initialize the FMUs
    sim_mod.initialize()
    print ("===========Initialization is completed")

    # Call event update prior to entering continuous mode.
    #sim_mod.event_update()
    #sim_mod.enter_continuous_time_mode()

    import numpy as np
    for c, val in enumerate(time_grid, 1):
    #for tim in np.arange(start_time, stop_time, step_size):
        # Enter continuous time mode
        print ("Set values at time={!s}".format(val))
        sim_mod.time = val
        sim_tim.append(val)
        sim_mod.set_real(simulator_input_valref, [con_sig[c-1]])
        LBNL_test1_Sm_master_port1_9_=sim_mod.get_real([sim_mod.get_variable_valueref('LBNL_test1_Sm_master_port1_9_')])

        print ("The value of the signal='LBNL_test1_Sm_master_port1_9' is ={!s}".format(LBNL_test1_Sm_master_port1_9_))
        sim_res.append(LBNL_test1_Sm_master_port1_9_[0])
    end = datetime.now()
    print(
        'Ran a single Opal-RT simulation with FMU={!s} in {!s} seconds.'.format(
            fmu_path, (end - start).total_seconds()))

    # Terminate FMUs
    sim_mod.terminate()
    print ("These are the output results={!s} for simulation time={!s}".format(sim_res, sim_tim))
    fil=open("simResults.txt", "w")
    fil.write(str(sim_res))
    fil.close()
    plt.plot(sim_tim, sim_res)
    plt.show()

if __name__ == "__main__":
    # Check command line options
    # The OPAL-RT model is running with a time factor of 1
    # The time factor is set in the model directly
    run_simulator()
