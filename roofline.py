#!/usr/bin/python3

"""
Roofline analysis tool. This tool implements the roofline methodology
as described in:

  "Cache-aware Roofline model: Upgrading the Loft",
  IEEE Computer Architecture Letters, January 2014

This implementation Copyright (C) ARM Ltd. 2019-2014.  All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Original Author: Andrea Brunato andrea.brunato@arm.com
Author: Eric Van Hensbergen <eric.vanhensbergen@arm.com>
"""

import argparse
import sys
import csv
import os
import math
import time
import statistics as st
import json
import subprocess as sp
from shutil import copyfile, move
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree
from time import gmtime, strftime
from decimal import Decimal

example_string = "roofline.py {record} <target_application>"
target_app_args = None
roofline_tool_dir = os.path.dirname(os.path.abspath(__file__)) + "/"
cwd = os.getcwd() + "/"

drrun = roofline_tool_dir + "/dynamorio/build/bin64/drrun "

def run_client(app, options=[""]):
    "Run the roofline client on the target app with the given options"
    client_cmd = drrun + " -c {}/client/build/libroofline.so ".format(
        roofline_tool_dir) + " ".join(options) + " -- " + app
    print(client_cmd)
    sp.call(client_cmd, shell=True)

def run_roofline_client(args, app, out_dir=None):
    "Run the DynamoRIO client multiple times to gather all needed performance data"

    options = ["--output_folder " + out_dir if out_dir else ".",
               "--roi_start {}".format(args.roi_start) if args.roi_start else "",
               "--roi_end {}".format(args.roi_end) if args.roi_end else "",
               "--label_roi" if args.label_roi else "",
               "--read_bytes_only" if args.read_bytes_only else "",
               "--write_bytes_only" if args.write_bytes_only else "",
               "--trace_f {}".format(args.trace_f) if args.trace_f else "",
               "--calls_as_separate_roi" if args.calls_as_separate_roi else ""]

    options.append("--dump_csv")

    if args.flops_only:
        run_client(app, options=options)
        sys.exit()

    if args.time_only:
        options.append("--time_run")
        run_client(app, options=options)
        sys.exit()

    # Memory and FP Run
    run_client(app, options=options)

    # TODO: Wrap this in an appropriate function
    # Time Run: add the appropriate flag to communicate this to the DynamoRIO client
    options.append("--time_run")

    run_client(app, options)

def get_time_info(app, settings):
    "Gather timing information for the given binary and environment settings."
    start = time.time()
    if settings:
        sp.call("./{}".format(app), shell=True)
    else:
        sp.call("{} ./{}".format(settings, app), shell=True)
    end = time.time()
    return end - start

def record(args):
    "Use the Roofline client to record the target app performance"
    # Build up the command for running the target application with its arguments

    global target_app_args
    if target_app_args:
        target_app_args = " ".join(target_app_args)
        app_with_flags = args.target_app + " " + target_app_args
    else:
        app_with_flags = args.target_app

    # If the app is run as "./<app>", remove the initial ./
    if app_with_flags[0:2] == "./":
        app_with_flags = app_with_flags[2:]

    # Check out the output directory does not already exists
    out_dir = args.output if args.output else app_with_flags.replace(
        " ", "_") + strftime("%Y-%m-%d_%H:%M:%S", gmtime())
    out_dir = cwd + out_dir + "/"

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    else:
        print("You've specified an already existing output directory. Please specify a different destination\n")
        sys.exit()


    # Run the Roofline client on the target application
    run_roofline_client(args, app=app_with_flags, out_dir=out_dir)


def main():
    #record_parser = argparse.ArgumentParser(
    #    prog='roofline', description="Roofline Tool. Example usage: \n" + example_string)
    record_parser = argparse.ArgumentParser(prog='roofline', description='Record the specified application in its execution. Please make sure to define the Region of Interest for your program.'
                                          'You can specify a region of interest in 3 different ways:\n\n -> Recompiling the target application using the provided include file\n'
                                          '-> Designating functions already present in your app as delimiters by specifying --roi_start <Function Name> --roi_end <Function Name>\n'
                                          '-> Designating a whole function body as a roi, by specifying --trace_f <Function Name>\n')
    record_parser.add_argument('target_app')
    record_parser.add_argument(
        '--output', '-o', help='Output file name for saving the gathered performance information')
    record_parser.add_argument(
        '--roi_start', help='Specify the function name inside the binary which delimits the beginning of the Region of Interest (ROI)')
    record_parser.add_argument(
        '--roi_end', help='Specify the function name inside the binary which delimits the end of the Region of Interest (ROI)')
    record_parser.add_argument(
        '--label_roi', help='First argument of roi_start function is a string label', action='store_true')
    record_parser.add_argument(
        '--trace_f', help='Specify the function name whose whole execution will be taken into account as a Region of Interest')
    record_parser.add_argument(
        '--calls_as_separate_roi', help='To be used only after specifying --trace_f, takes into account each function execution as a different ROI', action='store_true')
    record_parser.add_argument(
        '--time_only', help='Run the roofline client to get timing information only', action='store_true')
    record_parser.add_argument(
        '--read_bytes_only', help='Take into account only bytes which are being read', action='store_true')
    record_parser.add_argument(
        '--write_bytes_only', help='Take into account only bytes which are being written', action='store_true')
    record_parser.add_argument(
        '--flops_only', help='Run the roofline client to get flops and bytes information only', action='store_true')
    record_parser.set_defaults(func=record)

    # Get option flags for the target application
    global target_app_args
    args, target_app_args = record_parser.parse_known_args()

    # Call the function corresponding to the given action {record, report}
    args.func(args)


if __name__ == '__main__':
    sys.exit(main())
