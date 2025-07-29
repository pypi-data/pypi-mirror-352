from mlpLogger import MLPLogger
def test_basic_logger_initialization():
   logger = MLPLogger()
   assert logger is not None
   assert logger.logfilename.endswith(".log")