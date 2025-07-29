# edict/cli.py

import os
import subprocess

def run_edict(input_file, output_file, duration, alias):
	jar_path = os.path.join(os.path.dirname(__file__), 'edict.jar')
	cmd = ["java", "-jar", jar_path, input_file, output_file, str(duration), alias]
	subprocess.run(cmd, check=True)

def main():
	import argparse
	parser = argparse.ArgumentParser(description="Run EDICT simulation.")
	parser.add_argument("--input", required=True)
	parser.add_argument("--output", required=True)
	parser.add_argument("--duration", required=True)
	parser.add_argument("--alias", required=True)
	args = parser.parse_args()

	run_edict(args.input, args.output, args.duration, args.alias)