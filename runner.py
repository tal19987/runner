import argparse
from subprocess import PIPE, run
import psutil
from multiprocessing import Process, Queue
from collections import Counter


def create_logs(file_name, file_number, data):
    with open(f"{file_name}{file_number}.log",'w') as f:
        f.write(data)


def get_network_usage(q):
    data = psutil.net_io_counters()
    q.put(str(data))


def get_strace_otput(pid,q):
    data = run(['strace', '-p', f"{pid}"])
    q.put(data)


def get_cpu_usage(q):
    data = psutil.cpu_times()
    q.put(str(data))


def get_disk_io(q):
    data = psutil.disk_io_counters()
    q.put(str(data))


def get_memory(q):
    data = psutil.virtual_memory()
    q.put(str(data))


def run_command(command, isCallTrace, q):
    if isCallTrace:
        exec_command = f"strace -c {command}"
    else:
        exec_command = command
    data = run(exec_command.split(),stdout=PIPE,stderr=PIPE)
    q.put(data)


def main_command(command, number_of_runs, failed_count, systrace, calltrace, logtrace):

    # Defining variables
    counter_returned_error_code = 0
    queues = {}
    returned_objects = []
    get_exit_codes = []

    json_of_systrace_functions = {
        get_disk_io : "q1",
        get_memory : "q2",
        get_cpu_usage : "q3",
        get_network_usage : "q4"
    }

    json_of_systrace_files = {
        "diskio" : "q1",
        "memory" : "q2",
        "cpu_usage" : "q3",
        "network" : "q4"
    }

    for i in range(0, 6):
        queues[f"q{i}"] = Queue()

    # Starting the main functions
    for i in range(number_of_runs):
        get_strace_output = ""
        processes = []
        get_log_stderr_stdout = {}

        if counter_returned_error_code == failed_count and failed_count != 0:
            print(f"The command have reached it's maximum attempts to run ({failed_count} times)")
            break

        processes.append(Process(target=run_command, args=(command, calltrace, queues["q0"],)))

        for function_name , queue in json_of_systrace_functions.items():
            processes.append(Process(target=function_name,args=(queues[queue],)))

        for process in processes:
            process.start()

        for process in processes:
            process.join()

        # Adds the exit code of the command to an array
        returned_objects.append(queues["q0"].get())

        get_exit_codes.append(returned_objects[len(returned_objects) -1].returncode)

        if calltrace:
            get_strace_output = str(returned_objects[len(returned_objects) -1].stderr.decode())

        if logtrace:
            get_log_stderr_stdout["stderr"] = returned_objects[len(returned_objects) -1].stderr.decode()
            get_log_stderr_stdout["stdout"] = returned_objects[len(returned_objects) - 1].stdout.decode()

        # Gets the last exit code of the command
        if get_exit_codes[len(get_exit_codes) -1] != 0:
            if systrace:
                for file , queue in json_of_systrace_files.items():
                    create_logs(file, counter_returned_error_code, queues[queue].get())
            if calltrace:
                create_logs("calltrace", counter_returned_error_code, get_strace_output)
            if logtrace:
                stderr , stdout = get_log_stderr_stdout["stderr"] , get_log_stderr_stdout["stdout"]
                create_logs("logtrace", counter_returned_error_code, f"stdout is: {stdout}\nstderr is: {stderr}")
            counter_returned_error_code += 1
    return get_exit_codes

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
    parser.error('--failed-count value must be equal or lower than -c value (default is 1)')
if args.call_trace and args.log_trace:
    parser.error("--call-trace can't be used with --log-trace")
elif args.call_trace:
    main_command(args.COMMAND, args.c, args.failed_count, args.sys_trace, args.call_trace, False)
elif args.log_trace:
    main_command(args.COMMAND, args.c, args.failed_count, args.sys_trace, False, args.log_trace)
exit_codes = main_command(args.COMMAND, args.c, args.failed_count, args.sys_trace,args.call_trace, args.log_trace)
exit_codes_fixed = Counter(exit_codes)
number, count = Counter(exit_codes_fixed).most_common(1)[0]
print(f"The most common exit code is- {number} which appears {count} times")

for number , count in Counter(exit_codes_fixed).items():
    print(f"The exit code {number} appears {count} times")