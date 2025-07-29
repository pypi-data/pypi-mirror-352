from datetime import datetime
import logging
import ecs_logging
import socket

class MLPLogger():
    """
    A class to setup mlp logging
    ----------
    Attributes
    ----------
    logfilename(str):
        filepath of logfilename

    Methods
    -------
    derive_meanlagcnt():
        derives the meanlagcnt for a given 
    """

    def __init__(self, **kwargs):
        # logfilename = 
        # self.logfilename = logfilename
        logfile = "//caant.co.i.caa.ca/fs/VS_DATA/Yogesh Raheja/Logs/MLPLogger/mlpLogger.log"
        self._logfilename = self.createDailyLogfileName(logfile)
        self.mlpLoggerExtras = {'mlpLoggerExtras.hostname': socket.gethostname(), 'mlpLoggerExtras.scriptRunID': self.createScriptRunID(), 'callingClass': {type(self).__name__}}

        self.mlplogger = logging.getLogger("mlplogger")
        self.mlplogger.setLevel(logging.INFO)

        # Add an ECS formatter to the Handler
        handler = logging.FileHandler(self._logfilename)
        handler.setFormatter(ecs_logging.StdlibFormatter())
        self.mlplogger.addHandler(handler)
        self.logger = self.mlplogger

    @property
    def logfilename(self):
        print(f"Getter method called. logfile: {self._logfilename}")
        return self._logfilename

    @logfilename.setter
    def logfilename(self, value):
        self._logfilename = self.createDailyLogfileName(value)
        self.mlplogger = logging.getLogger("mlplogger")
        self.mlplogger.setLevel(logging.INFO)

        # Add an ECS formatter to the Handler
        self.mlplogger.handlers.clear()                         # Clear existing handlers
        handler = logging.FileHandler(self._logfilename)
        handler.setFormatter(ecs_logging.StdlibFormatter())
        self.mlplogger.addHandler(handler)
        self.logger = self.mlplogger
        print(f"MLPLogger: Setter method called. logfilename set to: {self._logfilename}")

    def createDailyLogfileName(self, logfile):
        currentUTCFormatted = datetime.utcnow().strftime('%Y%m%d')
        logfile = logfile.replace('.log', f'_{currentUTCFormatted}.log')
        return logfile

    def createScriptRunID(self, scriptname=""):
        dateString = datetime.now()
        dateString = dateString.strftime("%Y%m%d%H%M%S")
        if scriptname:
            return f"""{scriptname}_{dateString}"""
        else:
            return f"""{dateString}"""

    def logSuccess(self, logExtrasIn):
        logExtrasIn['mlpLoggerExtras.runScriptOutcome'] = 'success'
        return logExtrasIn