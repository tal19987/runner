import argparse
import subprocess


def multiple_command(number, command, failed):
    return_codes = 0
    for i in range(number):
        if subprocess.run(command.split()) != 0:
            return_codes += 1
            if return_codes == failed:
                print(f'Command failed for {failed} times. Giving up...ed')
                break


parser = argparse.ArgumentParser(description='Outputs a summery of execution of any command',
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('COMMAND', help='The command you wish to run')
parser.add_argument('-c', metavar='NUM', type=int,
                    help='Number of times to run the given command')
parser.add_argument('--failed-count', type=int, default=-1,
                    help='Number of allowed failed command invocation attempts before giving up')
parser.add_argument('--sys-trace', metavar='',
                    help='Creates a log for:\n'
                         '  - Disk IO\n  - Memory Usage\n  - CPU & Process info\n  - Network info'
                    )
parser.add_argument('--call-trace', metavar='',
                    help='For each failed execution, add also a log with '
                         'all the system calls ran by the command')

parser.add_argument('--log-trace', metavar='',
                    help='For each failed execution, add also the command output logs')

parser.add_argument('--debug', metavar='',
                    help='Debug mode')

args = parser.parse_args()

if args.failed_count:
    if not args.c:
        parser.error('--failed-count must be used with \'-c\'')
    else:
        if args.failed_count > args.c:
            parser.error('--failed-count value must be equal to or smaller then \'-c\' value')
        else:
            multiple_command(args.c, args.COMMAND, args.failed_count)

