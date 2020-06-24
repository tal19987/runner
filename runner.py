#!/usr/bin/env python3

import argparse
from subprocess import PIPE, run
from multiprocessing import Process, Queue
from collections import Counter
import pdb
import sys
import signal

import psutil

get_exit_codes = []


# Defines what parameters/options the runner.py can get
def build_parser():
    parser = argparse.ArgumentParser(description='Outputs a summery of execution of any command',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('COMMAND', help='The command you wish to run')
    parser.add_argument('-c', metavar='NUM', type=int, default=1,
                        help='Number of times to run the given command')
    parser.add_argument('--failed-count', type=int, default=0,
                        help='Number of allowed failed command invocation attempts before giving up')
    parser.add_argument('--sys-trace', action='store_const', metavar='', const="True",
                        help='Creates a log for:\n'
                             '  - Disk IO\n  - Memory Usage\n  - CPU & Process info\n  - Network info'
                        )
    parser.add_argument('--call-trace', action='store_const', metavar='', const="True",
                        help='For each failed execution, add also a log with '
                             'all the system calls ran by the command')

    parser.add_argument('--log-trace', action='store_const', metavar='', const="True",
                        help='For each failed execution, add also the command output logs')

    parser.add_argument('--debug', action='store_const', metavar='', const="True",
                        help='Debug mode')
    args = parser.parse_args()

    if args.failed_count > args.c:
        parser.error(
            '--failed-count value must be equal or lower than -c value (default is 1)')

    if args.call_trace and args.log_trace:
        parser.error("--call-trace can't be used with --log-trace")

    return args


# Creates the logs when command fails
# Function gets: string (basic file name), integer (number of the log), string (data object)
def create_logs(file_name, file_number, data):
    with open(f"{file_name}{file_number}.log", 'w') as f:
        f.write(data)


# Gets the stats about network
# Function gets: Queue (object that saves the data)
def get_network_usage(q):
    data = psutil.net_io_counters()
    q.put(str(data))


# Gets the stats about cpu usage
# Function gets: Queue (object that saves the data)
def get_cpu_usage(q):
    data = psutil.cpu_times()
    q.put(str(data))


# Gets the stats about disk i/o
# Function gets: Queue (object that saves the data)
def get_disk_io(q):
    data = psutil.disk_io_counters()
    q.put(str(data))


# Gets the stats about memory
# Function gets: Queue (object that saves the data)
def get_memory(q):
    data = psutil.virtual_memory()
    q.put(str(data))


# Runs the command
# Function gets: string (a command), boolean (creating the call trace logs (True or None), Queue (object that saves the data)
def run_command(command, isCallTrace, q):
    if isCallTrace:
        exec_command = f"strace -c {command}"
    else:
        exec_command = command
    data = run(exec_command.split(), stdout=PIPE, stderr=PIPE)
    q.put(data)


# Creates files and gets return codes
# Function gets: a string (command), integer (how many times the command should run), integer (after how many times the command will stop running),
#                boolean (creating the sys trace logs (True of None)), boolean (creating the call trace logs (True or None)),
#                boolean (creating the log trace logs (True or None))
def start_runner(command, number_of_runs, failed_count, systrace, calltrace, logtrace):
    # Defining variables
    counter_returned_error_code = 0
    queues = {}
    returned_objects = []
    global get_exit_codes

    # Dict of function for sys-trace
    json_of_systrace_functions = {
        get_disk_io: "q1",
        get_memory: "q2",
        get_cpu_usage: "q3",
        get_network_usage: "q4"
    }

    # Json for creating the sys-trace files
    json_of_systrace_files = {
        "sys_diskio": "q1",
        "sys_memory": "q2",
        "sys_cpu_usage": "q3",
        "sys_network": "q4"
    }

    # Initiating the Queue objects
    for i in range(0, 5):
        queues[f"q{i}"] = Queue()

    for i in range(number_of_runs):
        get_strace_output = ""
        processes = []
        get_log_stderr_stdout = {}

        if counter_returned_error_code == failed_count and failed_count != 0:
            print(
                f"The command have reached it's maximum attempts to run ({failed_count} times)")
            break

        processes.append(Process(target=run_command, args=(
            command, calltrace, queues["q0"],)))

        for function_name, queue in json_of_systrace_functions.items():
            processes.append(
                Process(target=function_name, args=(queues[queue],)))

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        # Adds the return object of the command to an array
        returned_objects.append(queues["q0"].get())

        # Adds the exit code of the command to an array
        get_exit_codes.append(
            returned_objects[len(returned_objects) - 1].returncode)

        if calltrace:
            get_strace_output = str(
                returned_objects[len(returned_objects) - 1].stderr.decode())

        if logtrace:
            get_log_stderr_stdout["stderr"] = returned_objects[len(
                returned_objects) - 1].stderr.decode()
            get_log_stderr_stdout["stdout"] = returned_objects[len(
                returned_objects) - 1].stdout.decode()

        # Gets the last exit code of the command
        if get_exit_codes[len(get_exit_codes) - 1] != 0:
            if systrace:
                for file, queue in json_of_systrace_files.items():
                    create_logs(file, counter_returned_error_code,
                                queues[queue].get())

            if calltrace:
                create_logs("calltrace", counter_returned_error_code,
                            get_strace_output)

            if logtrace:
                stderr, stdout = get_log_stderr_stdout["stderr"], get_log_stderr_stdout["stdout"]
                create_logs("logtrace", counter_returned_error_code,
                            f"stdout is: {stdout}\nstderr is: {stderr}")

            counter_returned_error_code += 1

    # For unit-testing purposes
    return get_exit_codes


# Creates the output for the user
def print_summary():
    global get_exit_codes
    exit_codes_fixed = Counter(get_exit_codes)
    number, count = exit_codes_fixed.most_common(1)[0]
    print(
        f"The most common exit code is- {number} which appears {count} times")

    for number, count in exit_codes_fixed.items():
        print(f"The exit code {number} appears {count} times")


# Handling signals
def signal_handler(signal_recieved, frame):
    print(f"Program was interrupted by signal number {signal_recieved}")
    print_summary()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    args = build_parser()
    if args.debug:
        pdb.set_trace()
        start_runner(args.COMMAND, args.c, args.failed_count,
                     args.sys_trace, args.call_trace, args.log_trace)
    else:
        start_runner(args.COMMAND, args.c, args.failed_count,
                     args.sys_trace, args.call_trace, args.log_trace)
    print_summary()
