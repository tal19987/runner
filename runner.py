import argparse
import subprocess
import psutil
from multiprocessing import Process, Queue


def create_cpu_usage_log(file_number,data):
    filename = 'cpu' + str(file_number) + '.log'
    with open(filename,'w') as f:
        f.write(data)


def create_memory_log(file_number,data):
    filename = 'memory' + str(file_number) + '.log'
    with open(filename,'w') as f:
        f.write(data)


def create_disk_io_log(file_number,data):
    filename = 'diskio' + str(file_number) + '.log'
    with open(filename, 'w') as f:
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


def main_command(command, number, failed, systrace):
    return_codes_error = 0
    q1 = Queue()
    q2 = Queue()
    q3 = Queue()
    q4 = Queue()
    q5 = Queue()
    for i in range(number):
        if return_codes_error == failed and failed != 0:
            print(f'Command failed for {failed} times. Giving up...')
            break
        p1 = Process(target=run_command,args=(command,q1))
        p2 = Process(target=get_disk_io, args=(q2,))
        p3 = Process(target=get_memory,args=(q3,))
        p4 = Process(target=get_cpu_usage, args=(q4,))
        p5 = Process(target=get_network_usage, args=(q5,))

        p1.start()
        p2.start()
        p3.start()
        p4.start()
        p5.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()
        p5.join()

        print (q1)
        if q1.get() != 0:
            if systrace:
                create_disk_io_log(return_codes_error,q2.get())
                create_memory_log(return_codes_error,q3.get())
                create_cpu_usage_log(return_codes_error,q4.get())
                # create cpu
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
parser.add_argument('--call-trace', metavar='', nargs='?',
                    help='For each failed execution, add also a log with '
                         'all the system calls ran by the command')

parser.add_argument('--log-trace', metavar='', nargs='?',
                    help='For each failed execution, add also the command output logs')

parser.add_argument('--debug', metavar='', nargs='?',
                    help='Debug mode')

args = parser.parse_args()

if args.failed_count > args.c:
    parser.error('--failed-count value must be equal or higher than -c value (default is 1)')
main_command(args.COMMAND, args.c, args.failed_count, args.sys_trace)
