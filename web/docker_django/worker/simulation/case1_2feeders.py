from __future__ import division
import argparse
import sys
import functions as func
import pdb
import numpy as np
import datetime

# Retrieve model name
try:
    parser = argparse.ArgumentParser(description='Need model filename')
    # Create args and parse them
    arg_names = ['filename1', 'filename2']
    for arg_name in arg_names:
        parser.add_argument(arg_name)
    args = parser.parse_args()
    model_filename1 = str(args.filename1)
    model_filename2 = str(args.filename2)
except:
    sys.exit('Error: could not retrieve argument')

# Create time and model name vectors
nb_simulation = 30
sec_per_sim = 5
rad = np.linspace(0, 2*np.pi, num=nb_simulation)
times = np.linspace(0, len(rad) * sec_per_sim, len(rad)).tolist()

# Get time x label
now = datetime.datetime.now()
start = now.replace(hour=19, minute=00, second=00, microsecond=0)
time_labels = [start + datetime.timedelta(seconds=5 * index) for index in range(0, len(times))]
time_labels = [value.time() for value in time_labels]

# model name vector
model_names1 = [model_filename1] * len(times)
model_names2 = [model_filename2] * len(times)

# Generate the load profile
load_profile = [value if value < 1.3 else 1.3 for value in np.sin(rad) / 2 + 1]

# Generate the pv profile
pv_profile = np.array([value for value in np.sin(np.flipud(rad)) + 1])
pv_profile = np.array([value if value < 1 else 1 for value in pv_profile])
noise = np.random.normal(0, 0.05, len(pv_profile))
pv_profile += noise
pv_profile = np.array([value if value > 0 else 0 for value in pv_profile])
pv_profile = np.array([value if value < 1 else 1 for value in pv_profile])
input_profiles = [{'x': time_labels, 'y': load_profile, 'label': 'load profile'},
                  {'x': time_labels, 'y': pv_profile, 'label': 'pv profile'}]

# Initiate the configuration file
print('Creating a configuration file...')
parent_folder = 'D://Users//Jonathan//Documents//GitHub//PGE_Models_DO_NOT_SHARE//'
configuration = func.initialize_configuration(times, parent_folder, model_names1)

# Shift load and pv in the configuration file
configuration = func.shift_load_and_pv(load_profile, pv_profile, configuration)

# Create the configuration file
output_folder = 'D://Users//Jonathan//Documents//GitHub//configuration_files//'
configuration_filename1 = func.create_configuration_file(configuration, output_folder)
print('Configuration file created: ' + configuration_filename1.split('//')[-1])

# Initiate the configuration file
print('Creating a configuration file...')
parent_folder = 'D://Users//Jonathan//Documents//GitHub//PGE_Models_DO_NOT_SHARE//'
configuration = func.initialize_configuration(times, parent_folder, model_names2)

# Shift load and pv in the configuration file
configuration = func.shift_load_and_pv(load_profile, pv_profile, configuration)

# Create the configuration file
output_folder = 'D://Users//Jonathan//Documents//GitHub//configuration_files//'
configuration_filename2 = func.create_configuration_file(configuration, output_folder)
print('Configuration file created: ' + configuration_filename2.split('//')[-1])

start_time = times[0]
end_time = times[-1]
save_to_file = 0
result = func.simulate_2cymdist_gridyn_fmus(
    configuration_filename1, configuration_filename2, start_time, end_time, sec_per_sim, save_to_file, input_profiles, time_labels)