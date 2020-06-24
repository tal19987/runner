1. You need to install this non-python dependencies in order to run the script: <br/>
   strace <br/>
2. Here are some links to the resources i've used: <br/>
    a. Multiprocess Docs page (https://docs.python.org/3/library/multiprocessing.html) <br/>
    b. Psutil Docs page (https://psutil.readthedocs.io/en/latest/) <br/>
    c. Argparse Docs page (https://docs.python.org/3/library/argparse.html) <br/>
    d. Argparse examples (https://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/argparse/index.html)<br/>
    e. Python catch sigint (https://www.devdungeon.com/content/python-catch-sigint-ctrl-c)<br/>
3. I had a few challenges: <br/>
   The **first** one was to understand how to get all the data when the option --sys-trace appears. <br/>
   What this option does is to create some files that contains some data that is being collected **during** the command execution. <br/>
   Eventually, I realised I need to run all the functions in parallel and only if the user mention an option, the logs will be created<br/>
   with the data that the functions creates. <br/>

   The **second** one was how to allow the option --call-trace with --log-trace.<br/>
   The problem was that for the --call-trace option, I used the 'strace' command which outputs all the information to stderr.<br/>
   How am I suppose so save the output (stdout) of --log-trace option if all the output is send to stderr (because of the 'strace' command)?<br/>
   At the end, I realized that this two options can't be together so I disallowed the user to do that.<br/>

   The **third** and quite fun challange was to print, no matter what happens, the summary.<br/>
   I used the module 'signal' to make sure CTRL+C and kill signals will be handled. But, I didn't know how to send the return-code list to the "print_summary" function.<br/>
   That's because that the function- "signal_handler" doesn't get the return-code list. After a while I came to conclusion that I simply can't do it.<br/>
   I can't send the return-code list to the "signal_handler" function and than pass this list to the "print_summary" function.
   This is why i used a global var named- "get_exit_codes" (which is the return-code list).
   By that, I don't need to worry about passing the list between the functions.
   
