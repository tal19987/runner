from subprocess import run, PIPE

import runner


def test_should_create_a_simple_log_file():
    runner.create_logs("simplelog",0,"testfile")
    number_of_files = run("grep testfile simplelog0.log",shell=True)
    assert number_of_files.returncode == 0


def test_should_run_cmd_n_times_not_successfully_and_fail():
    runner.get_exit_codes = []
    total_exit_codes_number = runner.start_runner(
        'false', 4, 2, False, False, False)  # Suppose to be 2
    assert len(total_exit_codes_number) == 2


def test_should_run_cmd_n_times_succefully():
    runner.get_exit_codes = []
    total_exit_codes_number = runner.start_runner(
        'true', 3, 0, False, False, False)  # Suppose to be 3
    assert len(total_exit_codes_number) == 3


def test_should_create_sys_trace_files_when_cmd_fails():
    runner.get_exit_codes = []
    # Suppose to create 4 files
    runner.start_runner('false', 3, 1, True, False, False)
    number_of_files = run(
        "find . -name 'sys_*.log' | wc -l", shell=True, stdout=PIPE)
    assert int(number_of_files.stdout) == 4


def test_should_create_call_trace_files_when_cmd_fails():
    runner.get_exit_codes = []
    # Suppose to create 2 files
    runner.start_runner('false', 3, 2, False, True, False)
    number_of_files = run(
        "find . -name 'calltrace*.log' | wc -l", shell=True, stdout=PIPE)
    assert int(number_of_files.stdout) == 2


def test_should_create_log_trace_files_when_cmd_fails():
    runner.get_exit_codes = []
    runner.start_runner('false', 4, 1, False, False,
                        True)  # Suppose to create 1 file
    number_of_files = run(
        "find . -name 'logtrace*.log' | wc -l", shell=True, stdout=PIPE)
    assert int(number_of_files.stdout) == 1

