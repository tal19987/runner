1. You need to install this non-python dependencies in order to run the script: <br/>
   strace <br/>
2. Here are some links to the resources i've used: <br/>
    a. Multiprocess Docs page (https://docs.python.org/3/library/multiprocessing.html) <br/>
    b. Psutil Docs page (https://psutil.readthedocs.io/en/latest/) <br/>
    c. Argparse Docs page (https://docs.python.org/3/library/argparse.html) <br/>
    d. Argparse examples (https://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/argparse/index.html)
    e. Python catch sigint (https://www.devdungeon.com/content/python-catch-sigint-ctrl-c)
3. I had a few challenges: <br/>
   The first one was to understand how to get all the data when the option --sys-trace appears. <br/>
   What this option means is that it creates some files that gets data **during** the command execution. <br/>
   Eventually, I realised I need to run all the functions parallel and only if the user mention an option, the logs will be created<br/>
   with the data that the paralleled functions will create. <br/><br/> 
   The second one was how to allow the option --call-trace with --log-trace<br/>
   The problem was that for the --call-trace option, I used the 'strace' command which outputs all the information to stderr.<br/>
   How am I suppose so save the output (stdout) for --log-trace if all the output is send to stderr?<br/>
   At the end, I realized that this two options can't be together.
   The third and quit fun was to print, no matter what happens, the summary.<br/>
   I used the module 'signal' to make sure CTRL+C and kill will be handled but i didn't know how to send the return-code array to the print summary function,<br/>
   because the function- signal_handler will have to get the return-code list and pass it the the print-summary,<br/>
   but how do I pass the return-code list the the signal-handler function?
   The answer- I can't.<br/>
   This is why i used a global var named- get_exit_codes (which is a list).
   By that, I don't need to worry about passing the list between the functions.
   
