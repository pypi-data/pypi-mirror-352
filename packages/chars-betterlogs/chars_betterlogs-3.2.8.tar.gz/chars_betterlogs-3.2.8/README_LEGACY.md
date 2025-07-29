# Better Logs

Made to replace Python's importable Logging lib because it didnt work how i wanted it to, and kept not actually writing logs to a file

# USAGE

Simply put "betterLogs.py" in the directory where your other python scripts are and do 
```python
from betterLogs import *
``` 
to import all log functions

The name of the repo has been changed to allow for making a git submodule that can be imported by Python directly, if made a git submodule:

```python
from betterLogs.betterLogs import *
```

`log(): This Function writes a log with the given level and string to write to the given file.`

`filename:String | Self explanatory`

`log:String | The log youd wish to write to a file`

`level:String | What should appear before the time string (e.g. '[WARN]:')`

`showTime:Bool | Whether to show the timestamp before the written log`

`isHeader:Bool | Whether, if printing, to override the level color with the header tag`

`doPrinting:Bool | Whether to also print the log.`

`log_<level (e.g. log_warn)>(): Redirect function to log() and adds [<LEVEL>]: to the beginning of the log`

`Same inputs as log() but without "level:String"`
