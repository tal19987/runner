import pytest
import runner
from subprocess import run, PIPE


def test_should_run_cmd_n_times_not_successfully_and_fail():
    runner.get_exit_codes = []
    total_exit_codes_number = runner.start_runner('ls /test123', 4, 2, False, False, False)  # Suppose to be 2
    assert len(total_exit_codes_number) == 2


def test_should_run_cmd_n_times_succefully():
    runner.get_exit_codes = []
    total_exit_codes_number = runner.start_runner('ls', 3, 0, False, False, False) # Suppose to be 3
    assert len(total_exit_codes_number) == 3

def test_should_create_sys_trace_files():
    runner.get_exit_codes = []
    runner.start_runner('ls /test123', 3, 1, True, False, False)  # Suppose to be 4 files
    number_of_files =  run("find . -name \*.log | wc -l", shell=True, stdout=PIPE)
    assert int(number_of_files.stdout) == 4