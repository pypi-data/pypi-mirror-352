# manman
GUI for deployment and monitoring of servers and applications
related to specific apparatuses.<br>
```
usage: python -m manman [-h] [-c CONFIGDIR] [-t INTERVAL] [-v] [apparatus ...]
positional arguments:
  apparatus             Path of apparatus config files, can include wildcards.
                        If None, then an interactive dialog will be opened to
                        select files. (default: None)
options:
  -c CONFIGDIR, --configDir CONFIGDIR
                        Root directory of config files, one config file per
                        apparatus, if None, then ./config directory will be
                        used (default: None)
  -C, --condensed       Condensed arrangement of tables: no headers, narrow
                        columns (default: False)
  -t INTERVAL, --interval INTERVAL
                        Interval in seconds of periodic checking. If 0 then no
                        checking (default: 10.0)
  -z ZOOMIN, --zoomin ZOOMIN
                        Scale the application window by a factor, it must
                        be >= 1 (default: None)
```
## Control of all applications in a table
The action cell in top row of the table executes table-wide commands: **Check All, Start All, Stop All**
It also has commands to
- delete current tab (Delete),
- edit the table (Edit),
- condense and expannd table arrangement (Condense and Uncondense).

## Configuration
The following actions are defined in the combobox, related to the application:
  - **Check**
  - **Start**
  - **Stop**
  - **Command**: will display the command for starting the manager

Definition of actions, associated with an apparatus, are defined in the 
startup dictionary of the python scripts, code-named as apparatus_NAME.py. See examples in the config directory.

Supported keys are:
  - **'cmd'**: command which will be used to start and stop the manager,
  - **'cd'**:   directory (if needed), from where to run the cmd,
  - **'process'**: used for checking/stopping the manager to identify 
     the manager's process. If cmd properly identifies the 
     manager, then this key is not necessary,
  - **'shell'**: some managers require shell=True option for subprocess.Popen()
  - **'help'**: it will be used as a tooltip,

## Demo
  - **python -m manman config/apparatus_*.py**<br>
Control all apparatuses, defined in the ./config directory.
Each apparatus will be controlled in a separate tab.
  - **python -m manman -c config apparatus_test.py apparatus_TST.py**<br>
Control two apparatuses from the ./config directory
  - **python -m manman -c config**<br>
Interacively select apparatuses from the ./config directory<br>
![manman](docs/manman.png)

