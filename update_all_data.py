"""Update all output data files: municipal, regional, national, and sector emissions."""
# -*- coding: utf-8 -*-
import subprocess
import sys


STEPS = [
    ("Municipality data",          ["generate_data.py"]),
    ("Regional data",              ["generate_data.py", "--regions"]),
    ("National data",              ["generate_data.py", "--national"]),
    ("Municipality sector emissions", ["sector_emissions.py"]),
    ("Regional sector emissions",  ["sector_emissions.py", "--regions"]),
    ("National sector emissions",  ["sector_emissions.py", "--national"]),
]


def run_step(label, args):
    """Run a single data-generation script, stopping on failure."""
    print(f"\n=== {label} ===")
    result = subprocess.run([sys.executable] + args, check=False)
    if result.returncode != 0:
        print(f"ERROR: '{' '.join(args)}' exited with code {result.returncode}.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    for description, script_args in STEPS:
        run_step(description, script_args)

    print("\nAll data files updated.")
