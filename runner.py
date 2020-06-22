import argparse
import subprocess
import psutil
from multiprocessing import Process, Queue
from collections import Counter

def create_logs(file_name, file_number, data):
    with open(f"{file_name}{file_number}.log",'w') as f:
        f.write(data)


def get_network_usage(q):
    data = psutil.net_io_counters()
    q.put(str(data))


def get_cpu_usage(q):
    data = psutil.cpu_times()
    q.put(str(data))


def get_disk_io(q):
    data = psutil.disk_io_counters()
    q.put(str(data))


def get_memory(q):
    data = psutil.virtual_memory()
    q.put(str(data))


def run_command(command,q):
    data = subprocess.run(command.split())
    q.put(data.returncode)


def main_command(command, number_of_runs, failed_count, systrace):
    return_codes_error = 0
    json_of_functions = {
        get_disk_io : "q1",
        get_memory : "q2",
        get_cpu_usage : "q3",
        get_network_usage : "q4"
    }

    json_of_files = {
        "diskio" : "q1",
        "memory" : "q2",
        "cpu_usage" : "q3",
        "network" : "q4"
    }

    queues = {}
    exit_codes = []

    for i in range(0, 5):
        queues[f"q{i}"] = Queue()

    for i in range(number_of_runs):
        processes = []

        if return_codes_error == failed_count and failed_count != 0:
            print(f"The command have reached it's maximum attempts to run ({failed_count} times)")
            break

        processes.append(Process(target=run_command, args=(command, queues["q0"],)))

        for function_name , queue in json_of_functions.items():
            processes.append(Process(target=function_name,args=(queues[queue],)))

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        # Adds the exit code of the command to and array
        exit_codes.append(queues["q0"].get())


        # Gets the last exit code of the command
        if exit_codes[len(exit_codes) -1] != 0:
            if systrace:
                for file , queue in json_of_files.items():
                    create_logs(file, return_codes_error, queues[queue].get())
            return_codes_error += 1


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
    parser.error('--failed-count value must be equal or higher than -c value (default is 1)')

main_command(args.COMMAND, args.c, args.failed_count, args.sys_trace)
