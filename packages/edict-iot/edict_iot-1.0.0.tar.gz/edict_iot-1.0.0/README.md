# EDICT

EDICT is a simulation tool for evaluating the performance of Edge interactions in IoT-enhanced environments.
It generates a performance metrics dataset as a CSV file by relying on queueing network models.


## Installation 
EDICT can be installed with the following command
```
$ pip install edict-iot
```

## Using EDICT

EDICT can be run either through the CLI, or can be called within your Python modules.
Running EDICT requires 4 arguments:
- an input file, which contains the IoT system specification. Note that the input file should be located in a subdirectory called `files`.
- an output file, which refers to the output dataset where response time metrics will be saved. This dataset will contain aggregated results for all simulation runs.
- a duration (in seconds), which refers for how long the simulation should be run for. We recommend running the simulation for a duration of 3 to 5 minutes to achieve confidence levels higher than 95%.
- an alias to identify the simulation. This alias will also be used to identify the simulation in the output file.

To run EDICT using the CLI, you can run the following command:

```
$ edict --input files/input_file.json --output output_file.csv --duration duration --alias alias
```

You can also import EDICT in your Python code and call the `simulate` function with the same arguments, as follows:

```
import edict

edict.simulate(input_file=input_file, output_file=output_file, simulation_duration=duration, alias=alias)
```

EDICT will generate 2 CSV files containing performanc metrics:
- A CSV file of the form `alias_input_file.csv`, located in the `files` directory. This file contains response time, throughput, and drop rate metrics per subscription. For each simulation, an individual file will be created.
- A CSV file of the form `output_file.csv`. This file will contain aggregated response time results for all simulations that you run and that have `output_file.csv` as their output file. This file can be used for performance optimization approaches, for instance.

For more information about EDICT, please check https://github.com/houssamhh/edict.

