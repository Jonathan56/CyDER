from __future__ import division
import source.monitor as m
from pyfmi import load_fmu
import matplotlib.pyplot as plt
import progressbar


class Master(object):
    """docstring for Master."""

    def __init__(self, number_of_feeder):
        # Simulation parameters
        self.feeder_path_to_configurations = None
        self.timestep = None
        self.times = None
        self.cymdist_fmu_path = './static/fmus/CYMDIST.fmu'
        self.griddyn_fmu_path = './static/fmus/griddyn14bus.fmu'
        self.save_to_file = 0
        self.feeder_voltage_reference = None
        self.monitoring = True
        self.monitoring_class = None

        # Simulation variables
        self.feeders = None
        self.feeder_input_valref = None
        self.feeder_output_valref = None
        self.transmission_input_valref = None
        self.transmission_output_valref = None
        self.transmission = None
        self.feeder_result = None
        self.transmission_result = None

        # CONSTANT
        self.feeder_input_names = ['VMAG_A', 'VMAG_B', 'VMAG_C', 'VANG_A', 'VANG_B', 'VANG_C']
        self.feeder_output_names = ['IA', 'IB', 'IC', 'IAngleA', 'IAngleB', 'IAngleC']
        self.transmission_input_names = None
        self.transmission_output_names = None
        if number_of_feeder == 1:
            self.transmission_input_names = ['Bus11_IA', 'Bus11_IB', 'Bus11_IC',
                           'Bus11_IAngleA', 'Bus11_IAngleB', 'Bus11_IAngleC']
            self.transmission_output_names = ['Bus11_VA', 'Bus11_VB', 'Bus11_VC',
                    'Bus11_VAngleA', 'Bus11_VAngleB', 'Bus11_VAngleC']
            self.multiplier = ['multiplier']
        elif number_of_feeder == 2:
            self.transmission_input_names = ['Bus10_IA', 'Bus10_IB', 'Bus10_IC',
                                   'Bus10_IAngleA', 'Bus10_IAngleB', 'Bus10_IAngleC',
                                   'Bus11_IA', 'Bus11_IB', 'Bus11_IC',
                                   'Bus11_IAngleA', 'Bus11_IAngleB', 'Bus11_IAngleC']
            self.transmission_output_names = ['Bus10_VA', 'Bus10_VB', 'Bus10_VC',
                                    'Bus10_VAngleA', 'Bus10_VAngleB', 'Bus10_VAngleC',
                                    'Bus11_VA', 'Bus11_VB', 'Bus11_VC',
                                    'Bus11_VAngleA', 'Bus11_VAngleB', 'Bus11_VAngleC']
            self.multiplier = ['multiplier10', 'multiplier11']
    def _initialize_feeders(self):
        """Initiliaze feeders"""
        # Initiliaze parameters
        feeder_configurations_bytes = []
        self.feeders = []
        self.feeder_input_valref = []
        self.feeder_output_valref = []
        self.feeder_result = []

        # Loop for each feeder model
        for feeder_conf in self.feeder_path_to_configurations:
            # Ask Thierry about this??
            feeder_configurations_bytes.append(bytes(feeder_conf, 'utf-8'))

            # Load FMUs
            self.feeders.append(load_fmu(self.cymdist_fmu_path, log_level=7))

            # Setup experiment
            self.feeders[-1].setup_experiment(
                start_time=self.times[0], stop_time=self.times[-1])

            # Create lists to hold value references
            self.feeder_input_valref.append([])
            self.feeder_output_valref.append([])

            # Get the value references of cymdist inputs
            for elem in self.feeder_input_names:
                self.feeder_input_valref[-1].append(self.feeders[-1].get_variable_valueref(elem))

            # Get the value references of cymdist outputs
            for elem in self.feeder_output_names:
                self.feeder_output_valref[-1].append(self.feeders[-1].get_variable_valueref(elem))

            # Set flag
            self.feeders[-1].set("_saveToFile", self.save_to_file)

            # Set configuration file
            ref = self.feeders[-1].get_variable_valueref("_configurationFileName")
            self.feeders[-1].set_string([ref], [feeder_configurations_bytes[-1]])

            # Initialize the FMUs
            self.feeders[-1].initialize()

            # Call event update prior to entering continuous mode.
            self.feeders[-1].event_update()
            self.feeders[-1].enter_continuous_time_mode()

            # Create holder for output variables
            self.feeder_result.append({name: [] for name in self.feeder_output_names})

    def _initialize_transmission(self):
        """Initialize transmission"""
        # Load GridDyn Fmu
        self.transmission = load_fmu(self.griddyn_fmu_path, log_level=7)

        # Set up experiment
        self.transmission.setup_experiment(start_time=self.times[0], stop_time=self.times[-1])

        # Create holders for the value reference
        self.transmission_input_valref = []
        self.transmission_output_valref = []

        # Get the value references of griddyn inputs
        for elem in self.transmission_input_names:
            self.transmission_input_valref.append(
                self.transmission.get_variable_valueref(elem))

        # Get the value references of griddyn outputs
        for elem in self.transmission_output_names:
            self.transmission_output_valref.append(
                self.transmission.get_variable_valueref(elem))


        # Set the value of the multiplier
        for multiplier in self.multiplier:
            self.transmission.set(multiplier, 3.0)

        # Create holder for output variables
        self.transmission_result = {name: [] for name in self.transmission_output_names}

        # Initialize
        self.transmission.initialize()

    def solve(self):
        """Launch a PyFMI simulation"""
        # Initialize feeders
        self._initialize_feeders()

        # Initialize transmission
        self._initialize_transmission()

        # Initialize monitoring
        if self.monitoring:
            monitor = self.monitoring_class()

        print('')
        print('Cosimulation in progress...')
        progress = progressbar.ProgressBar(widgets=['progress: ',
                                                    progressbar.Percentage(),
                                                    progressbar.Bar()],
                                           maxval=len(self.times)).start()

        # Co-simulation loop
        for iteration, time in enumerate(self.times):
            # Set feeder voltage reference and do step
            output_values_accross_all_feeders = []
            for index in range(0, len(self.feeders)):
                self.feeders[index].time = time
                self.feeders[index].set_real(
                    self.feeder_input_valref[index],
                    [self.feeder_voltage_reference[index]])

                # Save feeder results
                output_values = list(
                    self.feeders[index].get_real(self.feeder_output_valref[index]))
                for name, value in zip(self.feeder_output_names, output_values):
                    self.feeder_result[index][name].append(value)

                # Save values for transmission
                output_values_accross_all_feeders.extend(output_values)

            # Set transmission current and do step
            self.transmission.set_real(
                self.transmission_input_valref,
                output_values_accross_all_feeders)
            self.transmission.do_step(
                current_t=time, step_size=self.timestep, new_step=0)

            # Save transmission results
            output_values = list(
                self.transmission.get_real(self.transmission_output_valref))
            for name, value in zip(self.transmission_output_names, output_values):
                self.transmission_result[name].append(value)

            # Monitor progress
            if self.monitoring:
                monitor.update(self)

            # Update progress bar
            progress.update(iteration)
        progress.finish()

        # Close all FMUs
        for index in range(0, len(self.feeders)):
            self.feeders[index].terminate()
        self.transmission.terminate()

        # Close any plot
        import pdb; pdb.set_trace()
        plt.close()
