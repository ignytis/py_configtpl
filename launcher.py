#!/usr/bin/env python

import argparse
import os
import os.path
import sys
import subprocess


parser = argparse.ArgumentParser(prog="configtpl_cli", description="CLI for Configtpl development environment")
parser.add_argument("command")


args = parser.parse_args()
if args.command == "tests:functional":
    print("Functional testing started.")
    root_dir = os.path.join(os.getcwd(), "tests", "functional")
    for (dir, subdirs, files) in os.walk(os.path.join(os.getcwd(), "tests", "functional"), topdown=False):
        if dir == root_dir:  # skip the root directory
            continue

        test_path = os.path.join(dir, "test.py")
        print(f"Running '{test_path}'...")
        try:
            result = subprocess.run([sys.executable, test_path], capture_output=True, text=True, cwd=dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Test case failed with return code {e.returncode}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            exit(-1)

    print("Testing complete.")
else:
    raise ValueError(f"Invalid command: {args.command}")
