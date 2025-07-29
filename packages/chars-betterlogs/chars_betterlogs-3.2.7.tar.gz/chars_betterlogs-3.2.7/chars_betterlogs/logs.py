from datetime import datetime
from inspect import currentframe, getframeinfo
from io import TextIOWrapper
from .semver import SemVer

# Shortcuts for my Haxe self
false:bool = False
true:bool = True
null:None = None

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

a = 'a'
w = 'w'
r = 'r'

class Logging:

    version:SemVer = SemVer(3, 2, 7)
    filename:str = f'betterLogs_{version.replace('.', '-')}/log.xml'
    allowPrinting:bool = False

    def __init__(self, filename:str, beforeBeginning:str = '', allowPrinting:bool = true):
        self.filename = f'betterLogs_{self.version.toString().replace('.', '-')}/{filename}'
        self._createDir()
        self.allowPrinting = allowPrinting
        self._write(beforeBeginning + f'\n<!-- Log Generator: "Better Logs V{self.version.toString()}" | Better Logs by Char @chargoldenyt on Discord | https://github.com/CharGoldenYT/betterLogs -->\n<!-- START OF LOG -->\n<logFile>\n')
        return

    def _set_filename(self, filename:str):
        oldFile = open(self.filename, r)
        oldFileStr = oldFile.read()
        oldFile.close()
        import os; os.remove(self.filename)

        self.filename = filename

        path = filename.split('/')
        filename = path[path.__len__()-1]
        basePath = ''
        for p in path:
            if (p != filename):
                basePath += p + '/'
                try: os.mkdir(p)
                except: pass
        
        newFile = open(self.filename, w)
        newFile.write(oldFileStr)
        newFile.close()

    def _createDir(self):
        import os
        
        try:
            os.makedirs(f'betterLogs_{self.version.toString().replace('.', '-')}')
        except OSError as e:
            if e.errno != 17:
                print(f'Could not create log directory! "{str(e)}" make sure you have write access')
                exit(1)

    def _write(self, content:str):
        filename = self.filename
        logfile_lock = open(filename, 'a')
        logfile_lock.write(content)
        logfile_lock.close()

    def _levelToString(self, level:str) -> str:
        level = level.lower()

        color = '[MISC    ]'
        if level == 'info':color = '[INFO    ]:'
        if level == 'warn' or level == 'warning':color = '[WARNING ]:'
        if level == 'err' or level == 'error':color = '[ERROR   ]:'
        if level == 'critical':color = '[CRITICAL]:'
        if level == 'fatal':color = '[FATAL   ]:'

        return color

    def log(self, log:str, level:str, includeTimestamp:bool = true, isHeader:bool = false, fileFrom:str = '', pos:int = 0):
        time = str(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
        timeString = '[' + time + ']: '

        color:str = bcolors.HEADER
        
        if not isHeader:
            level = level.lower()
            if level == 'info':color = bcolors.OKBLUE
            if level == 'warn' or level == 'warning':color = bcolors.WARNING
            if level == 'err' or level == 'error':color = bcolors.FAIL
            if level == 'critical':color = bcolors.FAIL
            if level == 'fatal':color = bcolors.FAIL

        if not includeTimestamp:
            timeString = ''

        fileString = ''

        if fileFrom != '':
            fileString = fileFrom + ':' + str(pos) + ':'

        logString = self._levelToString(level) + timeString + f"'{fileString + log}'".replace('"', "'").replace('<', "[").replace('>', ']')

        if self.allowPrinting: print(color + logString)

        self._write('   <log value="' + logString.replace(fileString, '') + '" />\n')

    def log_header(self, log:str, level:str, includeTimestamps:bool = true,  fileFrom:str = '', pos:int = 0):
        self.log(log, level, includeTimestamps, true, fileFrom, pos)

    def log_info(self, log:str, includeTimestamps:bool = true, fileFrom:str = '', pos:int = 0):
        self.log_header(log, 'info', includeTimestamps, fileFrom, pos)

    def log_error(self, log:str, includeTimestamps:bool = true, fileFrom:str = '', pos:int = 0):
        self.log(log, 'error', includeTimestamps, false, fileFrom, pos)

    def log_err(self, log:str, includeTimestamps:bool = true, fileFrom:str = '', pos:int = 0):
        print(bcolors.WARNING + '[WARNING ]:betterLogs.py:80:log_err() is deprecated! use log_error() instead')
        self.log_error(log, includeTimestamps, fileFrom, pos)

    def log_warning(self, log:str, includeTimestamps:bool = true, fileFrom:str = '', pos:int = 0):
        self.log(log, 'warn', includeTimestamps, false, fileFrom, pos)

    def log_warn(self, log:str, includeTimestamps:bool = true, fileFrom:str = '', pos:int = 0):
        print(bcolors.WARNING + '[WARNING ]:betterLogs.py:87:log_warn() is deprecated! use log_warning() instead')
        self.log_warning(log, includeTimestamps, fileFrom, pos)

    def log_critical(self, log:str, includeTimestamps:bool = true, fileFrom:str = '', pos:int = 0):
        self.log(log, 'critical', includeTimestamps, false, fileFrom, pos)

    def log_fatal(self, log:str, includeTimestamps:bool = true, fileFrom:str = '', pos:int = 0):
        self.log(log, 'fatal', includeTimestamps, false, fileFrom, pos)

    def close(self):
        self._write('</logFile>\n<!--  END OF LOG  -->')