# Python's default importable logging lib doesn't QUITE work how i want it to, so i made a version that actually properly saves logs to a file while allowing for colors!
from datetime import datetime
from inspect import currentframe, getframeinfo
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

version = '2h'

def create_logFile(filename:str, beforeBeginning:str = ''):

    print('This is the classic version of betterLogs made for KrillYouBot, please use logs.Logging.')
    r'''Creates a log file with a given filename, and writes a header to it'''

    try:
        logging = open(filename, 'a')
        if beforeBeginning != '': beforeBeginning = beforeBeginning + '\n'
        logging.write(beforeBeginning + f'<!-- Log Generator: "Better Logs V{version}" | Better Logs by Char @annyconducter on Discord | https://github.com/CharGoldenYT/betterLogs -->\n<!-- START OF LOG -->\n'); logging.close()
    except Exception as e:
       frameinfo = getframeinfo(currentframe()); print('[' + str(frameinfo.filename) + '] [' + str(frameinfo.lineno) + '] Error with file"' + filename + '": "' + str(e) + '"')

def log(filename:str, log:str = None, level:str = '', showTime:bool = True, isHeader:bool = False, doPrinting:bool = True, file:str = '', pos:int = 0):
    print('This is the classic version of betterLogs made for KrillYouBot, please use logs.Logging.')

    r'''This Function writes a log with the given level and string to write to the given file.

    filename:String | Self explanatory

    log:String | The log youd wish to write to a file

    level:String | What should appear before the time string (e.g. '[WARN]:')

    showTime:Bool | Whether to show the timestamp before the written log

    isHeader:Bool | Whether, if printing, to override the level color with the header tag

    doPrinting:Bool | Whether to also print the log.'''

    if not log == None:
        time = str(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
        timeString = '[' + time + ']: '

        color = ''
        if level == '[INFO]:':color = bcolors.OKBLUE
        if level == '[WARN]:':color = bcolors.WARNING
        if level == '[ERR]:':color = bcolors.FAIL
        if level == '[CRITICAL]:':color = bcolors.FAIL
        if level == '[FATAL]:':color = bcolors.FAIL
        if isHeader:color = bcolors.HEADER

        if not showTime: timeString = ''

        fileString = ''
        if file != '':
            fileString = file + ':' + str(pos)
        logString = level + timeString + fileString + log

        if doPrinting: print(color + logString + bcolors.OKBLUE)

        if logString.__contains__('(Session ID:'):logString = logString.split('(')
        if isinstance(logString, list):logString = logString[0]

        try:
            logging = open(filename, 'a'); logging.write(logString + '\n'); logging.close()
        except Exception as e:
            frameinfo = getframeinfo(currentframe());print('[' + str(frameinfo.filename) + '] [' + str(frameinfo.lineno) + '] Error with file"' + filename + '": "' + str(e) + '"')
    
    if log == None:
        print('NOT ENOUGH ARGUMENTS! forgot to put a log file!')

def log_info(filename:str, v:any = None, showTime:bool = True, isHeader:bool = False, doPrinting:bool = True, file:str = '', pos:int = 0):
    print('This is the classic version of betterLogs made for KrillYouBot, please use logs.Logging.')

    r'''Redirect function to log() as a shortcut to not have to write the level each time.
    
    Refer to log() for the variable purposes'''
    if v == None:
        print('NOT ENOUGH ARGUMENTS! forgot to put a log file!')
        return

    v = str(v)
    log(filename, v, '[INFO]:', showTime, isHeader, doPrinting, file, pos)

def log_warning(filename:str, v:any = None, showTime:bool = True, isHeader:bool = False, doPrinting:bool = True, file:str = '', pos:int = 0):
    print('This is the classic version of betterLogs made for KrillYouBot, please use logs.Logging.')

    r'''Redirect function to log() as a shortcut to not have to write the level each time.
    
    Refer to log() for the variable purposes'''
    if v == None:
        print('NOT ENOUGH ARGUMENTS! forgot to put a log file!')
        return

    v = str(v)
    log(filename, v, '[WARN]:', showTime, isHeader, doPrinting, file, pos)

def log_warn(filename:str, v:any = None, showTime:bool = True, isHeader:bool = False, doPrinting:bool = True, file:str = '', pos:int = 0):
    print('This is the classic version of betterLogs made for KrillYouBot, please use logs.Logging.')

    r'''Redirect function to log_warning() as a shortcut'''

    log_warning(filename, v, showTime, isHeader, doPrinting, file, pos)

def log_error(filename:str, v:any = None, showTime:bool = True, isHeader:bool = False, doPrinting:bool = True, file:str = '', pos:int = 0):
    print('This is the classic version of betterLogs made for KrillYouBot, please use logs.Logging.')

    r'''Redirect function to log() as a shortcut to not have to write the level each time.
    
    Refer to log() for the variable purposes'''
    if v == None:
        print('NOT ENOUGH ARGUMENTS! forgot to put a log file!')
        return

    v = str(v)
    log(filename, v, '[ERR]:', showTime, isHeader, doPrinting, file, pos)

def log_err(filename:str, v:any = None, showTime:bool = True, isHeader:bool = False, doPrinting:bool = True, file:str = '', pos:int = 0):
    print('This is the classic version of betterLogs made for KrillYouBot, please use logs.Logging.')

    r'''Redirect function to log_error() as a shortcut'''

    log_error(filename, v, showTime, isHeader, doPrinting, file, pos)

def log_critical(filename:str, v:any = None, showTime:bool = True, isHeader:bool = False, doPrinting:bool = True, file:str = '', pos:int = 0):
    print('This is the classic version of betterLogs made for KrillYouBot, please use logs.Logging.')

    r'''Redirect function to log() as a shortcut to not have to write the level each time.
    
    Refer to log() for the variable purposes'''
    if v == None:
        print('NOT ENOUGH ARGUMENTS! forgot to put a log file!')
        return

    v = str(v)
    log(filename, v, '[CRITICAL]:', showTime, isHeader, doPrinting, file, pos)

def log_fatal(filename:str, v:any = None, showTime:bool = True, isHeader:bool = False, doPrinting:bool = True, file:str = '', pos:int = 0):
    print('This is the classic version of betterLogs made for KrillYouBot, please use logs.Logging.')

    r'''Redirect function to log() as a shortcut to not have to write the level each time.
    
    Refer to log() for the variable purposes'''
    if v == None:
        print('NOT ENOUGH ARGUMENTS! forgot to put a log file!')
        return

    v = str(v)
    log(filename, v, '[FATAL]:', showTime, isHeader, doPrinting, file, pos)

def end_log(filename:str):
    print('This is the classic version of betterLogs made for KrillYouBot, please use logs.Logging.')
    try:
        logging = open(filename, 'a'); logging.write('<!--  END OF LOG  -->'); logging.close()
    except Exception as e:
        frameinfo = getframeinfo(currentframe()); print('[' + str(frameinfo.filename) + '] [' + str(frameinfo.lineno) + '] Error with file"' + filename + '": "' + str(e) + '"')
    