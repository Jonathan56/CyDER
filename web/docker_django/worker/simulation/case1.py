from __future__ import division
import argparse
import sys
import functions as func
import pdb
import numpy as np

# Retrieve model name
try:
    parser = argparse.ArgumentParser(description='Need model filename')
    # Create args and parse them
    arg_names = ['filename']
    for arg_name in arg_names:
        parser.add_argument(arg_name)
    args = parser.parse_args()
    model_filename = str(args.filename)
except:
    sys.exit('Error: could not retrieve argument')

# Create time and model name vectors
nb_simulation = 30
sec_per_sim = 5
rad = np.linspace(0, 2*np.pi, num=nb_simulation)
times = np.linspace(0, len(rad) * sec_per_sim, len(rad)).tolist()
model_names = [model_filename] * len(times)

# Generate the load profile
load_profile = [value if value < 1.3 else 1.3 for value in np.sin(rad) / 2 + 1]

# Generate the pv profile
pv_profile = np.array([value for value in np.sin(np.flipud(rad)) + 1])
pv_profile = np.array([value if value < 1 else 1 for value in pv_profile])
noise = np.random.normal(0, 0.05, len(pv_profile))
pv_profile += noise
pv_profile = np.array([value if value > 0 else 0 for value in pv_profile])
pv_profile = np.array([value if value < 1 else 1 for value in pv_profile])

# Initiate the configuration file
print('Creating a configuration file...')
configuration = func.initialize_configuration(times, model_names)

# Shift load and pv in the configuration file
configuration = func.shift_load_and_pv(load_profile, pv_profile, configuration)

# Create the configuration file
configuration_filename = func.create_configuration_file(configuration)
print('Configuration file created: ' + configuration_filename.split('//')[-1])

start_time = times[0]
end_time = times[-1]
save_to_file = 0
result = func.simulate_cymdist_gridyn_fmus(configuration_filename, start_time, end_time, sec_per_sim, save_to_file)
