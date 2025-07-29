# edict/simulate.py

import subprocess
import os
import shutil
from pathlib import Path

def simulate(input_file, output_file, simulation_duration, alias):
    """
    Runs EDICT simulation.

    Parameters:
    - input_file (str): Path to the input file
    - output_file (str): Path to the output file
    - simulation_duration (str or int): Duration of simulation
    - alias (str): Alias name
    """


    # Run the Java simulator
    jar_path = Path(__file__).parent / "edict.jar"
    if not jar_path.exists():
        raise FileNotFoundError(f"edict.jar not found at {jar_path}")

    java_cmd = [
        "java", "-jar", str(jar_path),
        input_file, output_file, str(simulation_duration), alias
    ]


    subprocess.run(java_cmd, check=True)

    print("EDICT simulation completed.")
