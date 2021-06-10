'''
Logging module, both to UI and file.
'''

import logging
import logging.handlers
from os import mkdir
from os.path import isdir, isfile
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout
from PyQt5.QtGui import QCloseEvent

PATH_LOG_FOLDER = './logs'
PATH_LOG = PATH_LOG_FOLDER + '/log.txt'

class Logger():
    '''
    Should be used only (but implicitly) with a started QApplication and a parent QMainWindow
    '''

    def __init__(self):
        self.uiHandler = Logger._UILogHandler()
        self.fileHandler = self._createFileHandler()
        self._setLogFormats()
        logging.getLogger().addHandler(self.uiHandler)
        logging.getLogger().addHandler(self.fileHandler)

    def window(self) -> QWidget:
        return self.uiHandler.window

    def _setLogFormats(self):
        SEPARATOR = '-' * 100
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s\n' + SEPARATOR)
        self.uiHandler.setFormatter(formatter)
        self.fileHandler.setFormatter(formatter)
        logging.getLogger().setLevel(logging.INFO)

    def log(self, msg: str) -> None:
        logging.info(msg)
        self.uiHandler.window.repaint()

    def error(self, e: Exception) -> None:
        logging.exception(e)
        self.uiHandler.window.repaint()

    class _UILogHandler(logging.Handler, QObject):
        _appendText = pyqtSignal(str)

        def __init__(self):
            super().__init__()
            QObject.__init__(self)
            self.window = Logger._UILogHandler._LogWindow()
            self._createBindings()

        class _LogWindow(QWidget):
            def __init__(self):
                super().__init__(parent=None)
                self.setGeometry(980, 700, 900, 300)
                self.setWindowTitle('Logging')
                layout = QVBoxLayout(self)
                logArea = QPlainTextEdit(self)
                logArea.setReadOnly(True)
                layout.addWidget(logArea)
                self.setLayout(layout)
                self.logArea = logArea

            def closeEvent(self, event: QCloseEvent) -> None:
                self.hide()
                event.ignore()            

        def _createBindings(self):
            self._appendText.connect(self.window.logArea.appendPlainText)

        def emit(self, record):
            msg = self.format(record)
            self._appendText.emit(msg)

    def _createFileHandler(self):
        if not isdir(PATH_LOG_FOLDER):
            mkdir(PATH_LOG_FOLDER)

        handler = logging.handlers.RotatingFileHandler(PATH_LOG, delay=True, backupCount=10)
        if isfile(PATH_LOG):
            handler.doRollover()

        return handler