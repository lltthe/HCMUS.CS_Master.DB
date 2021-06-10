'''
UI layouts and modules.
'''

from hashlib import sha256
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, qApp, QWidget, QVBoxLayout, QLabel, QTabWidget, QGroupBox, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QScrollArea, QSizePolicy, QGridLayout, QTableWidget, QTableWidgetItem, QDateEdit, QCheckBox, QComboBox, QToolBar, QMessageBox, QItemDelegate, QFormLayout
from PyQt5.QtGui import QCloseEvent, QPixmap
from PyQt5.QtCore import Qt, QDate, QSettings, QItemSelectionModel
import qtawesome as qta
from datetime import date, datetime

import db
from log import Logger

class ID:
    WINDOW_MAIN = 'main'
    BUTTON_CREATE_SAMPLE_DATA = 'create-sample-data'

    def __init__(self):
        pass

class MainApp:
    _instance = None
    _dbWrapper = None
    _app = None
    _mainWindow = None
    _logger = None

    _GID = 'global.id'
    _AUTO_CONNECT = 'auto_connect'
    _AUTO_FILL_PASS = 'auto_fill_password'
    _settings = None
    
    _i = 1
    _clients = {}

    def __init__(self):
        if MainApp._instance != None:
            raise Exception('Attempt to construct a singleton class more than one time!')
        MainApp._instance = self
        MainApp._dbWrapper = db.Wrapper()
        MainApp._settings = QSettings('app.ini', QSettings.IniFormat)
        MainApp._app = QApplication(sys.argv)
        MainApp._logger = Logger()
        MainApp._mainWindow = MainWindow()

        autoConnect = MainApp._settings.value(MainApp._AUTO_CONNECT, 0)
        autoConnect = int(autoConnect)
        if autoConnect != 0:
            self._mainWindow._onDBConnect()

    @staticmethod
    def getInstance():
        if MainApp._instance == None:
            MainApp()
        return MainApp._instance

    @staticmethod
    def start() -> None:
        MainApp.getInstance()
        MainApp._mainWindow.show()
        MainApp._logger.window().show()
        sys.exit(MainApp._app.exec_())

    @staticmethod
    def getDB() -> db.Wrapper:
        MainApp.getInstance()
        return MainApp._dbWrapper

    @staticmethod
    def getLogger() -> Logger:
        MainApp.getInstance()
        return MainApp._logger 

    @staticmethod
    def getClientID() -> int:
        j = MainApp._i
        MainApp._i += 1
        return j

    def getGlobalID() -> int:
        res = MainApp._settings.value(MainApp._GID, 0)
        if res == 0:
            res = 1
        else:
            res = int(res)
            res += 1
        MainApp._settings.setValue(MainApp._GID, res)
        MainApp._settings.sync()
        return res

    @staticmethod
    def getClients() -> dict:
        return MainApp._clients

    @staticmethod
    def getSettings() -> QSettings:
        MainApp.getInstance()
        return MainApp._settings

    @staticmethod
    def signalRefresh(key: str, callerId: int) -> None:
        if key in MainApp._clients:
            for i in MainApp._clients[key]:
                if i != callerId:
                    MainApp._clients[key][i].refresh()
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)

        self.setWindowTitle('Demo Program - Advanced DBs Final Project - HCMUS Master K30')
        self.setGeometry(150, 150, 700, 700)
        self.setWindowIcon(qta.icon('fa5s.database'))
        
        self._createElements()
        self.setCentralWidget(self.mainTabGroup)
        self._createActionBindings()

    def _createElements(self):
        self._createMenuBar()
        self.mainTabGroup = MainWindow._MainTabGroup(self)
        self._createStatusBar()

    def _createMenuBar(self):
        menubar = self.menuBar()
        self.menubar = menubar

        appMenu = QMenu('&Application', self)
        self.appMenu = appMenu
        menubar.addMenu(appMenu)
        exitAct = QAction('&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Close all windows and exit the application')
        appMenu.addAction(exitAct)
        self.exitAct = exitAct

    def _createStatusBar(self):
        statusBar = self.statusBar()
        self.statusBar = statusBar
        self.labelBug = QLabel('Using mouse wheel to scroll on Clients frame currently has bugs. Just use the scroll bar!', statusBar)
        statusBar.addPermanentWidget(self.labelBug)

    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        qApp.quit()

    class _MainTabGroup(QTabWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

            self.mainTab = MainWindow._MainTab(self)
            self.addTab(self.mainTab, 'Database Interacting Hub')
            self.advancedTab = MainWindow._AdvancedTab(self)
            self.addTab(self.advancedTab, 'Advanced')
            self.aboutTab = MainWindow._AboutTab(self)
            self.addTab(self.aboutTab, 'About')

            self.setStyleSheet(
                'QTabBar {font-size: 12pt; font-weight:bold}'
                'QTabBar::tab:!selected {font-size: 12pt; font-weight:normal}'
                )

    class _Tab(QWidget):
        def __init__(self, parent=None, layout=None):
            super().__init__(parent)
            if layout == None:
                layout = self._createLayout()
            self.setLayout(layout)
            self.layout = layout
            
        def _createLayout(self):
            return QVBoxLayout(self)

    class _MainTab(_Tab):
        def __init__(self, parent=None):
            super().__init__(parent)

        def _createFrame(self, title, parent=None):
            frame = QGroupBox(title, parent)
            tmpLayout = QVBoxLayout(frame) # intermediate to break the font set
            frame.setLayout(tmpLayout)
            tmpWidget = QWidget(frame)
            tmpLayout.addWidget(tmpWidget)
            innerFrameLayout = QVBoxLayout(tmpWidget)
            tmpWidget.setLayout(innerFrameLayout)
            frame.setStyleSheet('QGroupBox {font-size:11pt; font-weight:bold;}') 
            return frame, innerFrameLayout, tmpWidget

        def _createLayout(self):
            layout = QVBoxLayout(self)
            
            connectionFrame, connectionFrameLayout, tmpWidget = self._createFrame('DBMS &Connections', self)
            layout.addWidget(connectionFrame, stretch=0)
            self.connectionGroup = tmpWidget

            connectionFrameLayout.addWidget(QLabel('File storing DBMS connection information:'))

            connectionInputLayout = QHBoxLayout()
            connectionInput = QLineEdit('db_credentials.json', tmpWidget)
            self.connectionInput = connectionInput
            connectionBrowseButton = QPushButton('Browse...', tmpWidget)
            self.connectionBrowseButton = connectionBrowseButton
            connectionInputLayout.addWidget(connectionInput)
            connectionInputLayout.addWidget(connectionBrowseButton)
            connectionFrameLayout.addLayout(connectionInputLayout)

            connectLayout = QHBoxLayout()
            connectButton = QPushButton('Connect', tmpWidget)
            self.connectButton = connectButton
            connectLayout.addWidget(connectButton, stretch=0, alignment=Qt.AlignLeft)
            connectStatusLabel = QLabel('', tmpWidget)
            self.connectStatusLabel = connectStatusLabel
            connectButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            connectLayout.addWidget(connectStatusLabel, stretch=1, alignment=Qt.AlignLeft)
            connectionFrameLayout.addLayout(connectLayout)
            connectStatusLabel.setMinimumWidth(450)
            connectStatusLabel.hide()

            clientFrame, clientFrameLayout, tmpWidget2 = self._createFrame('&Clients')
            clientFrame.setDisabled(True)
            layout.addWidget(clientFrame, stretch=1)
            self.clientFrame = clientFrame

            scrollArea = QScrollArea(clientFrame)
            scrollArea.setWidget(tmpWidget2)
            scrollArea.setWidgetResizable(True)
            scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scrollArea.setFrameShape(scrollArea.NoFrame)
            scrollArea.setStyleSheet(   'QScrollArea { background: transparent; }'
                                        'QScrollArea > QWidget > { background: transparent; }'
                                    )
            clientFrame.layout().addWidget(scrollArea)
            
            tmpWidget2.setParent(scrollArea)
            QWidget().setLayout(clientFrameLayout) # reparent the layout is necessary to relayout
            clientFrameLayout = QGridLayout(tmpWidget2)
            tmpWidget2.setLayout(clientFrameLayout)


            clientFrameLayout.addWidget(self._createClientGroup(tmpWidget2, 'Human Resource:', qta.icon('fa5s.users')), 0, 0, 1, 6)
            clientHRManageButton = self._createClientButton(tmpWidget2, 'Human Resource Manager', qta.icon('fa5s.users-cog'))
            self.clientHRManageButton = clientHRManageButton
            curRow = clientFrameLayout.rowCount()
            clientFrameLayout.addWidget(clientHRManageButton, curRow, 3, 1, 2, Qt.AlignRight)
            clientFrameLayout.addWidget(self._createDBLogo(tmpWidget2, 'neo4j'), curRow, 5, 1, 1, Qt.AlignLeft)
            curRow = clientFrameLayout.rowCount()
            clientRecruitButton = self._createClientButton(tmpWidget2, 'Recruitment Manager', qta.icon('fa5s.user-plus'))
            clientRecruitButton.setDisabled(True)
            clientFrameLayout.addWidget(QLabel('Upcoming', tmpWidget2), curRow, 5, 1, 1, Qt.AlignLeft)
            self.clientRecruitButton = clientRecruitButton
            clientFrameLayout.addWidget(clientRecruitButton, curRow, 3, 1, 2, Qt.AlignRight)

            clientFrameLayout.addWidget(self._createClientGroup(tmpWidget2, 'Business && Sales:', qta.icon('fa5s.shopping-cart')), clientFrameLayout.rowCount(), 0, 1, 6)
            curRow = clientFrameLayout.rowCount()
            clientBusinessButton = self._createClientButton(tmpWidget2, 'Revenue Manager', qta.icon('fa5s.money-bill'))
            self.clientBusinessButton = clientBusinessButton
            clientFrameLayout.addWidget(clientBusinessButton, curRow, 3, 1, 2, Qt.AlignRight)
            clientBusinessButton.setDisabled(True)
            clientFrameLayout.addWidget(QLabel('Upcoming', tmpWidget2), curRow, 5, 1, 1, Qt.AlignLeft)

            clientFrameLayout.addWidget(self._createClientGroup(tmpWidget2, 'Products:', qta.icon('fa5s.coffee')), clientFrameLayout.rowCount(), 0, 1, 6)
            curRow = clientFrameLayout.rowCount()
            clientProductButton = self._createClientButton(tmpWidget2, 'Product Manager', qta.icon('fa5s.mug-hot'))
            self.clientProductButton = clientProductButton
            clientFrameLayout.addWidget(clientProductButton, curRow, 3, 1, 2, Qt.AlignRight)
            clientFrameLayout.addWidget(self._createDBLogo(tmpWidget2, 'mysql'), curRow, 5, 1, 1, Qt.AlignLeft)
            curRow = clientFrameLayout.rowCount()
            clientNewProductButton = self._createClientButton(tmpWidget2, 'Product Proposal && Reviewer', qta.icon('fa5s.edit'))
            clientNewProductButton.setDisabled(True)
            clientFrameLayout.addWidget(QLabel('Upcoming', tmpWidget2), curRow, 5, 1, 1, Qt.AlignLeft)
            self.clientNewProductButton = clientNewProductButton
            clientFrameLayout.addWidget(clientNewProductButton, curRow, 3, 1, 2, Qt.AlignRight)

            clientFrameLayout.addWidget(self._createClientGroup(tmpWidget2, 'Supply Chains:', qta.icon('fa5s.leaf')), clientFrameLayout.rowCount(), 0, 1, 6)
            curRow = clientFrameLayout.rowCount()
            clientSupButton = self._createClientButton(tmpWidget2, 'Ingredient Manager', qta.icon('fa5s.truck-loading'))
            clientSupButton.setDisabled(True)
            clientFrameLayout.addWidget(QLabel('Upcoming', tmpWidget2), curRow, 5, 1, 1, Qt.AlignLeft)
            self.clientSupButton = clientSupButton
            clientFrameLayout.addWidget(clientSupButton, curRow, 3, 1, 2, Qt.AlignRight)

            clientFrameLayout.addWidget(self._createClientGroup(tmpWidget2, 'Marketing && Public Relation:', qta.icon('fa5s.ad')), clientFrameLayout.rowCount(), 0, 1, 6)
            curRow = clientFrameLayout.rowCount()
            clientFanButton = self._createClientButton(tmpWidget2, 'Fanpage Manager', qta.icon('fa5s.thumbs-up'))
            clientFanButton.setDisabled(True)
            clientFrameLayout.addWidget(QLabel('Upcoming', tmpWidget2), curRow, 5, 1, 1, Qt.AlignLeft)
            self.clientFanButton = clientFanButton
            clientFrameLayout.addWidget(clientFanButton, curRow, 3, 1, 2, Qt.AlignRight)

            clientFrameLayout.addWidget(self._createClientGroup(tmpWidget2, 'Stores && Branches:', qta.icon('fa5s.store')), clientFrameLayout.rowCount(), 0, 1, 6)
            curRow = clientFrameLayout.rowCount()
            clientShopButton = self._createClientButton(tmpWidget2, 'Coffee Shop Manager', qta.icon('fa5s.store-alt'))
            clientShopButton.setDisabled(True)
            clientFrameLayout.addWidget(QLabel('Upcoming', tmpWidget2), curRow, 5, 1, 1, Qt.AlignLeft)
            self.clientShopButton = clientShopButton
            clientFrameLayout.addWidget(clientShopButton, curRow, 3, 1, 2, Qt.AlignRight)

            clientFrameLayout.addWidget(self._createClientGroup(tmpWidget2, 'Customer Membership:', qta.icon('fa5s.address-card')), clientFrameLayout.rowCount(), 0, 1, 6)
            curRow = clientFrameLayout.rowCount()
            clientMemButton = self._createClientButton(tmpWidget2, 'Account Information', qta.icon('fa5s.user-lock'))
            clientFrameLayout.addWidget(self._createDBLogo(tmpWidget2, 'mongo'), curRow, 5, 1, 1, Qt.AlignLeft)
            clientFrameLayout.addWidget(self._createDBLogo(tmpWidget2, 'redis'), curRow, 6, 1, 1, Qt.AlignLeft)
            self.clientMemButton = clientMemButton
            clientFrameLayout.addWidget(clientMemButton, curRow, 3, 1, 2, Qt.AlignRight)
            curRow = clientFrameLayout.rowCount()
            clientLoginButton = self._createClientButton(tmpWidget2, 'Activity Profiler', qta.icon('fa5s.chart-line'))
            clientLoginButton.setDisabled(True)
            clientFrameLayout.addWidget(QLabel('Upcoming', tmpWidget2), curRow, 5, 1, 1, Qt.AlignLeft)
            self.clientLoginButton = clientLoginButton
            clientFrameLayout.addWidget(clientLoginButton, curRow, 3, 1, 2, Qt.AlignRight)

            clientFrameLayout.setRowStretch(clientFrameLayout.rowCount(), 1)
            clientFrameLayout.setColumnStretch(clientFrameLayout.columnCount(), 1)
        
            return layout

        def _createClientGroup(self, parent, label, icon):
            btn = QPushButton(icon, label, parent)
            btn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            btn.setDisabled(True)
            btn.setStyleSheet('QPushButton {font-weight: bold; font-size: 12pt; border: none; color: black; qproperty-iconSize: 36px; }')
            return btn

        def _createClientButton(self, parent, label, icon):
            btn = QPushButton(icon, label, parent)
            btn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            btn.setStyleSheet('QPushButton {font-size: 11pt; qproperty-iconSize:28px; }')
            btn.setFixedWidth(300)
            return btn

        def _createDBLogo(self, parent, key):
            lbl = QLabel(parent)
            pix = QPixmap('assets/db-logos/' + key + '.png')
            pix = pix.scaled(72, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl.setPixmap(pix)
            return lbl

    class _AdvancedTab(_Tab):
        def __init__(self, parent=None):
            super().__init__(parent)

        def _createLayout(self):
            layout = QVBoxLayout(self)
            scrollArea = QScrollArea(self)
            container = QWidget(scrollArea)
            layout.addWidget(scrollArea)
            self.container = container
            scrollArea.setWidgetResizable(True)
            scrollArea.setWidget(container)
            scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            containerLayout = QVBoxLayout(container)
            container.setLayout(containerLayout)

            createDataButton = QPushButton('Create sample data')
            createDataButton.setDisabled(True)
            createDataButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            self.createDataButton = createDataButton
            containerLayout.addWidget(createDataButton)

            showLogButton = QPushButton('Reopen logging window')
            showLogButton.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            self.showLogButton = showLogButton
            containerLayout.addWidget(showLogButton)

            autoConnect = QCheckBox('Auto connect on startup')
            autoConnect.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            self.autoConnect = autoConnect
            containerLayout.addWidget(autoConnect)
            settings = MainApp.getSettings()
            check = settings.value(MainApp._AUTO_CONNECT, 0)
            check = int(check)
            autoConnect.setCheckState(Qt.Checked if check == 1 else Qt.Unchecked)
            autoConnect.stateChanged.connect(self._onAutoConnectStateChanged)

            autoFillPass = QCheckBox('Auto fill member account password')
            autoFillPass.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            self.autoFillPass = autoFillPass
            containerLayout.addWidget(autoFillPass)
            settings = MainApp.getSettings()
            check = settings.value(MainApp._AUTO_FILL_PASS, 0)
            check = int(check)
            autoFillPass.setCheckState(Qt.Checked if check == 1 else Qt.Unchecked)
            autoFillPass.stateChanged.connect(self._onAutoFillPassStateChanged)

            containerLayout.addStretch()
            return layout

        def _onAutoConnectStateChanged(self):
            settings = MainApp.getSettings()
            check = 1 if self.autoConnect.checkState() == Qt.Checked else 0
            settings.setValue(MainApp._AUTO_CONNECT, check)
            settings.sync()

        def _onAutoFillPassStateChanged(self):
            settings = MainApp.getSettings()
            check = 1 if self.autoFillPass.checkState() == Qt.Checked else 0
            settings.setValue(MainApp._AUTO_FILL_PASS, check)
            settings.sync()

    class _AboutTab(_Tab):
        def __init__(self, parent=None):
            super().__init__(parent)

        def _createLayout(self):
            layout = QVBoxLayout(self)
            texts = ['A demo program for the Final Project of Advanced DB course - HCMUS IT Master K30 class, which works with:\n\tMySQL (Relational)\n\tNeo4j (Graph), MongoDB (Document)\n\tRedis (Key-value).\n\n', 'By:\n\t20C11008 - Võ Đăng Khoa\n\t20C11032 - Nguyễn Đình Khải\n\t20C11053 - Lâm Lê Thanh Thế\n\n', 'Contacts - Email: lamlethanhthe@gmail.com','For more info, please check \"README.md\"!']

            for text in texts:
                lbl = QLabel(text, self)
                lbl.setWordWrap(True)
                layout.addWidget(lbl)

            layout.addStretch()

            return layout

    def _createActionBindings(self):
        self.exitAct.triggered.connect(qApp.quit)
        
        mainTab = self.mainTabGroup.mainTab
        mainTab.connectionBrowseButton.clicked.connect(self._onDBFileBrowse)
        mainTab.connectButton.clicked.connect(self._onDBConnect)

        mainTab.clientHRManageButton.clicked.connect(lambda: self._onOpenClient(CLIENTS.HR_MANAGE))
        mainTab.clientProductButton.clicked.connect(lambda: self._onOpenClient(CLIENTS.PRODUCT_MANAGE))
        mainTab.clientMemButton.clicked.connect(lambda: self._onOpenClient(CLIENTS.ACC))

        advancedTab = self.mainTabGroup.advancedTab
        advancedTab.createDataButton.clicked.connect(self._onCreateData)
        advancedTab.showLogButton.clicked.connect(self._showLogWindow)

    def _onDBFileBrowse(self):
        fpath = QFileDialog.getOpenFileName(self, caption='Select a JSON file storing DBMS connection information', directory='./', filter='JSON (*.json)')
        self.mainTabGroup.mainTab.connectionInput.setText(fpath[0])

    def _onDBConnect(self):
        connectButton = self.mainTabGroup.mainTab.connectButton
        connectLabel = self.mainTabGroup.mainTab.connectStatusLabel
        connectInput = self.mainTabGroup.mainTab.connectionInput
        browseButton = self.mainTabGroup.mainTab.connectionBrowseButton
        createDataButton = self.mainTabGroup.advancedTab.createDataButton
        clientFrame = self.mainTabGroup.mainTab.clientFrame
        dbWrapper = MainApp.getDB()
        logger = MainApp.getLogger()
        statusBar = self.statusBar

        statusBar.showMessage('Executing...')
        try:
            if connectButton.text() == 'Connect':
                connectButton.setDisabled(True)
                connectLabel.setText('Connecting...')
                connectLabel.show()
                connectInput.setDisabled(True)
                browseButton.setDisabled(True)
                self.mainTabGroup.mainTab.connectionGroup.repaint()

                dbWrapper.connect(self.mainTabGroup.mainTab.connectionInput.text())
    
                connectLabel.setText('All DBMSs connected. Finding data...')
                logger.log('CONNECTIONS FINISHED: All DBMS connections have been successfully established!')

                # Check for data availability and auto create if needed
                data = dbWrapper.sampleData
                checks = data.checkDataAvailability()

                str1 = 'Found existing databases of: '
                str2 = 'Creating sample data for: '
                allCheck = True
                noCheck = True
                fDict = {'mysql': data.createMySQL, 'neo4j': data.createNeo4j, 'mongo': data.createMongo, 'redis': data.createRedis}
                fList = []
                for i in checks:
                    if not checks[i]:
                        allCheck = False
                        str2 += i + ', '
                        fList.append(fDict[i])
                    else:
                        noCheck = False
                        str1 += i + ', '
                if allCheck:
                    logger.log('ALL DATABASES FOUND!')
                else:
                    if noCheck:
                        logger.log('NO DATABASE FOUND: Creating all 5 sample databases...')
                        connectLabel.setText('No database found. Creating sample databases...')
                    else:
                        resStr = str1[:-2] + '. ' + str2[:-2] + '...'
                        logger.log('SOME DATABASE FOUND: ' + resStr)
                        connectLabel.setText('Some database(s) found. Creating other samples...')

                    connectLabel.repaint()
                    for f in fList:
                        f()
                    logger.log('SAMPLE DATA CREATED!')

                connectLabel.setText('Picking up databases...')
                connectLabel.repaint()
                logger.log('Picking up databases...')
                dbWrapper.pickupDatabase()
                logger.log('ALL DATABASES PICKED UP!')

                connectLabel.setText('Connected')
                createDataButton.setEnabled(True)
                connectButton.setText('Disconnect')
                clientFrame.setEnabled(True)
                connectButton.setEnabled(True)

            else: # Disconnect action
                dbWrapper.disconnect()
                connectLabel.hide()
                connectButton.setText('Connect')
                connectInput.setEnabled(True)
                browseButton.setEnabled(True)
                clientFrame.setDisabled(True)
                createDataButton.setDisabled(True)
                logger.log('CONNECTIONS DROPPED: Disconnected from all DBMSs!')

            statusBar.clearMessage()
            statusBar.showMessage('Done', 3000)

        except Exception as e:
            connectLabel.setText('Something\'s wrong! Please check the logs...')
            connectLabel.show()
            connectInput.setEnabled(True)
            browseButton.setEnabled(True)
            clientFrame.setDisabled(True)
            createDataButton.setDisabled(True)
            connectButton.setText('Connect')
            connectButton.setEnabled(True)
            logger.error(e)

            statusBar.clearMessage()
            statusBar.showMessage('Error', 3000)     

    def _onCreateData(self):
        status = self.statusBar
        try:
            status.showMessage('Executing...')
            dbWrapper = MainApp.getDB()
            logger = MainApp.getLogger()
            logger.log('CREATING sample data...')
            dbWrapper.createSampleData()
            logger.log('SAMPLE DATA CREATED: Initial data for all DBs have been successfully created!')
            status.clearMessage()
            status.showMessage('Done', 3000)

        except Exception as e:
            logger.error(e)
            status.showMessage('Error', 3000)

    def _showLogWindow(self):
        MainApp.getLogger().window().show()

    def _onOpenClient(self, key):
        wid = MainApp.getClientID()
        window = CLIENTS.WINDOWS[key](wid)
        window.show()
        if key not in MainApp.getClients():
            MainApp.getClients()[key] = {wid: window}
        else:
            MainApp.getClients()[key][wid] = window

# =======================================================================

class HRManageWindow(QMainWindow):
    def __init__(self, id):
        super().__init__(parent=None)
        self.id = id
        self.pending = None

        self.setWindowTitle('Client %d - Human Resource Manager' % id)
        self.setWindowIcon(qta.icon('fa5s.users-cog'))
        self.resize(1000, 500)

        self._createTable()
        self._createToolbar()

        MainApp.getLogger().log('[Neo4j] DATA RETRIEVED')
        MainApp.getLogger().log('CLIENT STARTED: Client %s - Human Resource Manager has successfully loaded!' % self.id)

    def _createTable(self):
        table = QTableWidget(self)
        self.table = table
        self.setCentralWidget(table)

        self._getData()

        table.setStyleSheet('QTableWidget::item {margin-top:1px; margin-bottom:1px}')
        table.resizeColumnsToContents()
        for c in range(table.columnCount()):
            table.setColumnWidth(c, table.columnWidth(c) + 8)

        table.itemChanged.connect(self._onTextChanged)

    def _createToolbar(self):
        toolbar = QToolBar(self)
        newAction = QAction(qta.icon('fa5s.user-plus'), '&New', toolbar)
        delAction = QAction(qta.icon('fa5s.user-slash'), '&Delete', toolbar)
        newAction.triggered.connect(self._onCreateNewEmp)
        delAction.triggered.connect(self._onDelEmps)
        newAction.setShortcut('Ctrl+N')
        delAction.setShortcut('Delete')
        toolbar.addAction(newAction)
        toolbar.addAction(delAction)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def _onTextChanged(self, item):
        r = item.row()
        self._updateEmpAtRow(r)

    def _getCell(self, key, dat):
        dbWrapper = MainApp.getDB()

        if key == 'eid':
            eid = QTableWidgetItem(dat)
            eid.setFlags(eid.flags() ^ Qt.ItemIsEditable)
            return eid

        if key == 'name':
            return QTableWidgetItem(dat)

        if key == 'birth':
            birth = dat
            birth = QDate(birth.year, birth.month, birth.day)
            birth = QDateEdit(birth)
            birth.wheelEvent = lambda event: None
            return birth

        if key == 'male':
            male = QWidget()
            layout = QHBoxLayout(male)
            check = QCheckBox(male)
            check.setCheckState(Qt.Checked if dat else Qt.Unchecked)
            layout.addWidget(check)
            male.setLayout(layout)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignCenter)
            return male

        if key == 'job':
            jobs = dbWrapper.getJobs()
            job = QComboBox()
            job.addItems(jobs)
            job.setCurrentText(dat)
            job.wheelEvent = lambda event: None
            return job

        if key == 'dep':
            deps = dbWrapper.getDepartments()
            dep = QComboBox()
            dep.addItems(deps)
            dep.setCurrentText(dat)
            dep.wheelEvent = lambda event: None
            return dep

        if key == 'branch':
            branches = dbWrapper.getBranches()
            branch = QComboBox()
            branch.addItems(branches)
            branch.setCurrentText(dat)
            branch.wheelEvent = lambda event: None
            return branch    

    def _fillRow(self, r, datList):
        '''
        eid name birth male job dep branch
        '''
        keys = ['eid', 'name', 'birth', 'male', 'job', 'dep', 'branch']
        table = self.table
        cells = []
        for c in range(table.columnCount()):
            if c < 2:
                f = table.setItem
            else:
                f = table.setCellWidget
            cell = self._getCell(keys[c], datList[c])
            f(r, c, cell)
            cells.append(cell)
        return cells

    def _connectRow(self, wList):
        '''
        birth male job dep branch
        '''
        fList = [wList[0].dateChanged, wList[1].findChild(QCheckBox).stateChanged, wList[2].currentTextChanged, wList[3].currentTextChanged, wList[4].currentTextChanged]

        for f in fList:
            f.connect(self._onCellWidgetChanged)

    def _getData(self):
        logger = MainApp.getLogger()
        try:
            table = self.table
            dbWrapper = MainApp.getDB()
            dat = dbWrapper.getEmployees()

            table.setRowCount(len(dat))
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(['Mã NV', 'Họ và tên', 'Ngày sinh', 'Nam?', 'Chức vụ', 'Phòng ban', 'Chi nhánh'])

            for r, row in enumerate(dat):
                emp = row['n']
                j = row['j']
                d = row['d']
                b = row['b']

                wList = self._fillRow(r, [emp['id'], emp['name'], emp['birth'], emp['male'], j['name'], d['name'], b['name']])
                self._connectRow(wList[2:])

            self.nameAscending = True
            self.idAscending = False
            table.sortByColumn(1, Qt.AscendingOrder)

            headers = table.horizontalHeader()
            headers.setSortIndicatorShown(True)
            headers.setSortIndicator(1, Qt.AscendingOrder)
            headers.setSectionsClickable(True)
            headers.sectionClicked.connect(self._sortByColumn)

        except Exception as e:
            logger.error(e)

    def _sortByColumn(self, column: int):
        ascending = True
        if column == 0:
            self.idAscending = not self.idAscending
            ascending = self.idAscending
        else:
            self.nameAscending = not self.nameAscending
            ascending = self.nameAscending
        self.table.sortByColumn(column, Qt.AscendingOrder if ascending else Qt.DescendingOrder)

    def _onCellWidgetChanged(self):
        sender = self.sender()
        if type(sender) == QCheckBox:
            sender = sender.parent()
        table = self.table
        index = table.indexAt(sender.pos())
        r = index.row()
        self._updateEmpAtRow(r)
        
    def _updateEmpAtRow(self, r):
        table = self.table

        eid = table.item(r, 0).text()
        name = table.item(r, 1).text()

        if (name.strip() == ''):
            return

        state = table.cellWidget(r, 3).findChild(QCheckBox).checkState()
        male = 'true' if state == Qt.Checked else 'false'
        birth = table.cellWidget(r, 2).date().toString('yyyy-MM-dd')
        job = table.cellWidget(r, 4).currentText()
        dep = table.cellWidget(r, 5).currentText()
        branch = table.cellWidget(r, 6).currentText()

        MainApp.getDB().changeEmp(eid, name, birth, male, job, dep, branch)
        MainApp.getLogger().log('[Neo4j] UPDATED/CREATED Employee %s' % eid)
        MainApp.signalRefresh(CLIENTS.HR_MANAGE, self.id)

        if self.pending != None and self.pending[0] == eid:
            self.pending = None

    def _onCreateNewEmp(self):
        table = self.table
        table.selectionModel().clear()

        if self.pending is None:
            eid = 'EN' + str(MainApp.getGlobalID())

            name = 'Type to edit...'
            birth = date(1990, 1, 1)
            male = True
            job = 'Nhân viên'
            dep = 'Kinh doanh'
            branch = 'The Coffee House 1'

            table.itemChanged.disconnect()
            r = table.rowCount()
            table.insertRow(r)
            wList = self._fillRow(r, [eid, name, birth, male, job, dep, branch])
            self._connectRow(wList[2:])
            table.itemChanged.connect(self._onTextChanged)
            table.setCurrentItem(table.item(r, 1))
        
            self.pending = (eid, r)
        else:
            table.setCurrentItem(table.item(self.pending[1], 1), QItemSelectionModel.Select)
        table.scrollToBottom()
        self.resize(self.width(), self.height() + 1)

    def _onDelEmps(self):
        confirm = self._delConfirm()

        if confirm == QMessageBox.Yes:
            table = self.table
            dbWrapper = MainApp.getDB()
            logger = MainApp.getLogger()
            rs = []
            for i in table.selectionModel().selectedRows():
                r = i.row()
                eid = table.item(r, 0).text()
                rs.append(r)
                dbWrapper.delEmp(eid)
                logger.log('[Neo4j] DELETED Employee %s' % eid)

            rs.sort(reverse=True)
            for r in rs:
                table.removeRow(r)

            MainApp.signalRefresh(CLIENTS.HR_MANAGE, self.id)

    def _delConfirm(self):
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setText('Are you sure you want to delete these employees?')
        dialog.setWindowTitle('Confirm deletion')
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.Yes)
        dialog.setEscapeButton(QMessageBox.No)

        res = dialog.exec_()
        return res

    def refresh(self) -> None:
        self.table = None
        self.pending = None
        self._createTable()

# =======================================================================

class ProductManageWindow(QMainWindow):
    def __init__(self, id):
        super().__init__(parent=None)
        self.id = id
        self.pending = None

        self.setWindowTitle('Client %d - Product Manager' % id)
        self.setWindowIcon(qta.icon('fa5s.mug-hot'))
        self.resize(950, 600)

        self._createFilterBoxes()
        self._createTable()
        self._createToolbar()

        MainApp.getLogger().log('[MySQL] DATA RETRIEVED')
        MainApp.getLogger().log('CLIENT STARTED: Client %s - Product Manager has successfully loaded!' % self.id)

    def _createFilterBoxes(self):
        widget = QWidget(self)
        self.centralWidget = widget
        layout = QVBoxLayout(widget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        filtersWidget = QWidget(widget)
        filtersLayout = QHBoxLayout(filtersWidget)
        layout.addWidget(filtersWidget)
        filtersWidget.setLayout(filtersLayout)

        filtersLayout.addWidget(QLabel('Filter by'))
        filtersLayout.addWidget(QLabel('Product Type:'))
        filterType = QComboBox()
        self.typeFilterBox = filterType
        types = MainApp.getDB().getProductTypes()
        types.insert(0, 'All')
        filterType.addItems(types)
        filtersLayout.addWidget(filterType)
        filtersLayout.addStretch()

        filterType.currentTextChanged.connect(self._filterByType)

    def _createTable(self):
        table = QTableWidget(self)
        self.table = table
        self.centralWidget.layout().addWidget(table)

        self._getData()

        table.setStyleSheet('QTableWidget::item {margin-top:1px; margin-bottom:1px}')
        table.resizeColumnsToContents()
        for c in range(table.columnCount()):
            table.setColumnWidth(c, table.columnWidth(c) + 8)

        table.itemChanged.connect(self._onTextChanged)
        table.setItemDelegateForColumn(4, MoneyDelegate())
        table.setColumnWidth(4, table.columnWidth(4) + 50)

    def _createToolbar(self):
        toolbar = QToolBar(self)
        newAction = QAction(qta.icon('fa5s.plus'), '&New', toolbar)
        delAction = QAction(qta.icon('fa5s.trash'), '&Delete', toolbar)
        newAction.triggered.connect(self._onCreateNewProd)
        delAction.triggered.connect(self._onDelProds)
        newAction.setShortcut('Ctrl+N')
        delAction.setShortcut('Delete')
        toolbar.addAction(newAction)
        toolbar.addAction(delAction)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def _onTextChanged(self, item):
        r = item.row()
        self._updateProdAtRow(r)

    def _getCell(self, key, dat):
        dbWrapper = MainApp.getDB()

        if key == 'id':
            pid = QTableWidgetItem(str(dat))
            pid.setFlags(pid.flags() ^ Qt.ItemIsEditable)
            return pid

        if key == 'name':
            return QTableWidgetItem(dat)

        if key == 'on':
            on = QWidget()
            layout = QHBoxLayout(on)
            check = QCheckBox(on)
            check.setCheckState(Qt.Checked if dat else Qt.Unchecked)
            layout.addWidget(check)
            on.setLayout(layout)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignCenter)
            return on

        if key == 'from':
            sfrom = dat
            sfrom = QDate(sfrom.year, sfrom.month, sfrom.day)
            sfrom = QDateEdit(sfrom)
            sfrom.wheelEvent = lambda event: None
            return sfrom    

        if key == 'price':
            return QTableWidgetItem(str(int(dat)))

        if key == 'type':
            types = dbWrapper.getProductTypes()
            ptype = QComboBox()
            ptype.addItems(types)
            ptype.setCurrentText(dat)
            ptype.wheelEvent = lambda event: None
            return ptype 

    def _fillRow(self, r, datList):
        '''
        id name on from price type
        '''
        keys = ['id', 'name', 'on', 'from', 'price', 'type']
        table = self.table
        cells = []
        for c in range(table.columnCount()):
            if c == 0 or c == 1 or c == 4:
                f = table.setItem
            else:
                f = table.setCellWidget
            cell = self._getCell(keys[c], datList[c])
            f(r, c, cell)
            cells.append(cell)
        return cells

    def _connectRow(self, wList):
        '''
        on from type
        '''
        fList = [wList[0].findChild(QCheckBox).stateChanged, wList[1].dateChanged, wList[2].currentTextChanged]

        for f in fList:
            f.connect(self._onCellWidgetChanged)

    def _getData(self):
        logger = MainApp.getLogger()
        try:
            table = self.table
            dbWrapper = MainApp.getDB()
            dat = dbWrapper.getProducts()

            table.setRowCount(len(dat))
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(['Mã SP', 'Tên SP', 'Đang kinh doanh?', 'Kinh doanh từ', 'Giá', 'Loại SP'])

            for r, row in enumerate(dat):
                wList = self._fillRow(r, row)
                self._connectRow([wList[2], wList[3], wList[5]])

            self.nameAscending = False
            self.idAscending = True
            self.priceAscending = False
            table.sortByColumn(0, Qt.AscendingOrder)

            headers = table.horizontalHeader()
            headers.setSortIndicatorShown(True)
            headers.setSortIndicator(0, Qt.AscendingOrder)
            headers.setSectionsClickable(True)
            headers.sectionClicked.connect(self._sortByColumn)

        except Exception as e:
            logger.error(e)

    def _sortByColumn(self, column: int):
        ascending = True
        if column == 0:
            self.idAscending = not self.idAscending
            ascending = self.idAscending
        elif column == 1:
            self.nameAscending = not self.nameAscending
            ascending = self.nameAscending
        else:
            self.priceAscending = not self.priceAscending
            ascending = self.priceAscending
        self.table.sortByColumn(column, Qt.AscendingOrder if ascending else Qt.DescendingOrder)

    def _onCellWidgetChanged(self):
        sender = self.sender()
        if type(sender) == QCheckBox:
            sender = sender.parent()
        table = self.table
        index = table.indexAt(sender.pos())
        r = index.row()
        self._updateProdAtRow(r)
        
    def _updateProdAtRow(self, r):
        table = self.table

        pid = table.item(r, 0).text()
        name = table.item(r, 1).text()

        if (name.strip() == ''):
            return

        state = table.cellWidget(r, 2).findChild(QCheckBox).checkState()
        on = 1 if state == Qt.Checked else 0
        sfrom = table.cellWidget(r, 3).date().toString('yyyy-MM-dd')
        price = table.item(r, 4).text()
        ptype = table.cellWidget(r, 5).currentText()

        MainApp.getDB().changeProd(pid, name, on, sfrom, price, ptype)
        MainApp.getLogger().log('[MySQL] UPDATED/CREATED Product %s' % pid)
        MainApp.signalRefresh(CLIENTS.PRODUCT_MANAGE, self.id)

        if self.pending != None and self.pending[0] == pid:
            self.pending = None

    def _onCreateNewProd(self):
        table = self.table
        table.selectionModel().clear()

        if self.pending is None:
            pid = MainApp.getDB().getNewProdID()

            name = 'Type to edit...'
            on = 1
            sfrom = date(2014, 1, 1)
            price = 50000

            ptype = self.typeFilterBox.currentText()
            if ptype == 'All':
                ptype = 'Cà phê'

            table.itemChanged.disconnect()
            r = table.rowCount()
            table.insertRow(r)
            wList = self._fillRow(r, [pid, name, on, sfrom, price, ptype])
            self._connectRow([wList[2], wList[3], wList[5]])
            table.itemChanged.connect(self._onTextChanged)
            table.setCurrentItem(table.item(r, 1))
        
            self.pending = (pid, r)
        else:
            table.setCurrentItem(table.item(self.pending[1], 1), QItemSelectionModel.Select)
        table.scrollToBottom()
        self.resize(self.width(), self.height() + 1)

    def _onDelProds(self):
        confirm = self._delConfirm()

        if confirm == QMessageBox.Yes:
            table = self.table
            dbWrapper = MainApp.getDB()
            logger = MainApp.getLogger()
            rs = []
            for i in table.selectionModel().selectedRows():
                r = i.row()
                pid = table.item(r, 0).text()
                rs.append(r)
                dbWrapper.delProd(pid)
                logger.log('[MySQL] DELETED Product %s' % pid)

            rs.sort(reverse=True)
            for r in rs:
                table.removeRow(r)

            MainApp.signalRefresh(CLIENTS.PRODUCT_MANAGE, self.id)

    def _delConfirm(self):
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setText('Are you sure you want to delete these products?')
        dialog.setWindowTitle('Confirm deletion')
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.Yes)
        dialog.setEscapeButton(QMessageBox.No)

        res = dialog.exec_()
        return res

    def _filterByType(self):
        t = self.typeFilterBox.currentText()
        table = self.table

        for r in range(table.rowCount()):
            if t == 'All' or table.cellWidget(r, 5).currentText() == t:
                table.setRowHidden(r, False)
            else:
                table.setRowHidden(r, True)
        pass

    def refresh(self) -> None:
        self.table.setParent(None)
        self.table = None
        self.pending = None
        self._createTable()
        self._filterByType()

class MoneyDelegate(QItemDelegate):
    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent=parent)

    def paint(self, painter, option, index):
        value = index.model().data(index, Qt.EditRole)
        try:
            number = int(value)
            painter.drawText(option.rect, Qt.AlignLeft, '{:,} VNĐ'.format(number))
        except Exception as e:
            QItemDelegate.paint(self, painter, option, index)
            MainApp.getLogger().error(e)

# =======================================================================

class MemberInfo(QMainWindow):
    def __init__(self, id):
        super().__init__(parent=None)
        self.id = id

        self.setWindowTitle('Client %d - Member Account Info' % id)
        self.setWindowIcon(qta.icon('fa5s.user-lock'))

        self.loginWidget = self.mainWidget = None
        self._autoLogin = True
        self.dat = {}

        self._createLoginWidget()
        self._createStatusBar()

        MainApp.getLogger().log('[MongoDB] DATA RETRIEVED')
        MainApp.getLogger().log('CLIENT STARTED: Client %s - Member Account Info has successfully loaded!' % self.id)

    def _createStatusBar(self):
        self.status = self.statusBar()

    def _createLoginWidget(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        self.resize(500, 300)
        self.repaint()
        self.loginWidget = widget

        layout = QGridLayout()
        widget.setLayout(layout)

        labelName = QLabel('Username:')
        editName = QLineEdit()
        self.editName = editName
        editName.returnPressed.connect(self._login)
        layout.addWidget(labelName, 1, 1)
        layout.addWidget(editName, 1, 2)

        labelPass = QLabel('Password:')
        editPass = QLineEdit()
        self.editPass = editPass
        editPass.setEchoMode(QLineEdit.Password)
        editPass.returnPressed.connect(self._login)
        layout.addWidget(labelPass, 2, 1)
        layout.addWidget(editPass, 2, 2)

        loginButton = QPushButton('Login')
        loginButton.setIcon(qta.icon('fa5s.sign-in-alt'))
        loginButton.clicked.connect(self._login)
        layout.addWidget(loginButton, 3, 1, 1, 2)

        newAccButton = QPushButton('Create New Account')
        newAccButton.setIcon(qta.icon('fa5s.plus-square'))
        newAccButton.clicked.connect(self._onNewAccCreate)
        layout.addWidget(newAccButton, 4, 1, 1, 2)

        loginStatus = QLabel('')
        self.loginStatus = loginStatus
        layout.addWidget(loginStatus, 5, 1, 1, 2)
        loginStatus.hide()

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 0)
        layout.setRowStretch(3, 0)
        layout.setRowStretch(4, 0)
        layout.setRowStretch(5, 0)
        layout.setRowStretch(6, 1)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 0)
        layout.setColumnStretch(3, 1)

        settings = MainApp.getSettings()
        fill = settings.value(MainApp._AUTO_FILL_PASS, 0)
        fill = int(fill)
        if fill != 0:
            editName.setText('Doraemon')
            editPass.setText('lltt')
            if self._autoLogin:
                self._login()

    def _createMainWidget(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        self.resize(500, 350)
        self.mainWidget = widget
        dat = self.dat

        layout = QVBoxLayout(widget)
        widget.setLayout(layout)

        topLayout = QGridLayout()
        layout.addLayout(topLayout)
        self.topLayout = topLayout

        avatar = self._getAva()
        self.avatar = avatar
        topLayout.addWidget(avatar, 0, 0, 3, 1)

        tmp = QLabel('ID:', widget)
        tmp.setStyleSheet('QLabel {font-size: 16pt; font-weight: bold}')
        topLayout.addWidget(tmp, 0, 1, Qt.AlignRight)
        idLabel = QLabel(widget)
        idLabel.setStyleSheet('QLabel {font-size: 16pt}')
        self.idLabel = idLabel
        idLabel.setText(dat['id'])
        topLayout.addWidget(idLabel, 0, 2, Qt.AlignLeft)

        topLayout.addWidget(QLabel('Membership:', widget), 1, 1, Qt.AlignRight)
        levelLabel = QLabel(widget)
        self.levelLabel = levelLabel
        levelLabel.setText(dat['level'])
        topLayout.addWidget(levelLabel, 1, 2, Qt.AlignLeft)

        changeAvaButton = QPushButton('Change avatar', widget)
        self.changeAvaButton = changeAvaButton
        changeAvaButton.clicked.connect(self._onAvatarChange)
        topLayout.addWidget(changeAvaButton, 2, 1)

        topLayout.setColumnStretch(3, 1)

        botLayout = QFormLayout()
        self.botLayout = botLayout
        layout.addLayout(botLayout)
       
        editUsername = QLineEdit(dat['username'], widget)
        self.editUsername = editUsername
        botLayout.addRow(QLabel('Username:'), editUsername)

        editPass = QLineEdit(widget)
        self.editPass = editPass
        botLayout.addRow(QLabel('New Password:'), editPass)
        editPass.setEchoMode(QLineEdit.Password)
        editPass.textChanged.connect(self._onNewPassTyped)
        editPass.setText('')

        confirmPass = QLineEdit(widget)
        self.confirmPass = confirmPass
        botLayout.addRow(QLabel('Confirm Password:'), confirmPass)
        confirmPass.setEchoMode(QLineEdit.Password)
        confirmPass.setText('')
        confirmPass.setDisabled(True)

        editFullname = QLineEdit(dat['fullname'], widget)
        self.editFullname = editFullname
        botLayout.addRow(QLabel('Full Name:'), editFullname)

        birth = dat['birth']
        editBirth = QDateEdit(QDate(birth.year, birth.month, birth.day), widget)
        self.editBirth = editBirth
        botLayout.addRow(QLabel('Birthday:'), editBirth)

        editPhone = QLineEdit(dat['phone'], widget)
        self.editPhone = editPhone
        botLayout.addRow(QLabel('Phone:'), editPhone)

        editEmail = QLineEdit(dat['email'], widget)
        self.editEmail = editEmail
        botLayout.addRow(QLabel('Email:'), editEmail)

        editAddress = QLineEdit(dat['address'], widget)
        self.editAddress = editAddress
        botLayout.addRow(QLabel('Address:'), editAddress)

        botLayout.setVerticalSpacing(10)

        fLayout = QHBoxLayout()
        fLayout.addStretch()
        layout.addLayout(fLayout)

        saveButton = QPushButton('Save', widget)
        self.saveButton = saveButton
        saveButton.setIcon(qta.icon('fa5s.sync-alt'))
        saveButton.clicked.connect(self._onSave)
        fLayout.addWidget(saveButton)

        logoutButton = QPushButton('Logout', widget)
        self.logoutButton = logoutButton
        logoutButton.setIcon(qta.icon('fa5s.sign-out-alt'))
        logoutButton.clicked.connect(self._logout)
        fLayout.addWidget(logoutButton)

        layout.addStretch()

    def _switchWidget(self, login=False):
        if not login:
            self.loginWidget.setParent(None)
            self.loginWidget = None
            self._createMainWidget()
        else:
            self.mainWidget.setParent(None)
            self.mainWidget = None
            self._createLoginWidget()

    def _login(self):
        logger = MainApp.getLogger()
        try:
            acc = self.editName.text()
            pw = self.editPass.text()
            res, dat = MainApp.getDB().memLogin(acc, pw)
            
            if res == db.LOGIN_RESULT.SUCC:
                logger.log('[MongoDB] LOGIN AUTHORIZED for user %s' % acc)
                self.dat = dat
                self._switchWidget()
            
            elif res == db.LOGIN_RESULT.NOT_FOUND:
                logger.log('[MongoDB] User does not exist!')
                self.loginStatus.show()
                self.loginStatus.setText('! Username does not exist')

            else: # wrong pass
                logger.log('[MongoDB] Wrong password!')
                self.loginStatus.show()
                self.loginStatus.setText('! Wrong password')

        except Exception as e:
            logger.error(e)

    def _logout(self):
        self._autoLogin = False
        self._switchWidget(True)

    def _getAva(self, path=None):
        try:
            if path is None:
                path = MainApp.getDB().getMemAvatarPath(self.dat['id'])
            lbl = QLabel(self)
            pix = QPixmap(path)
            self.dat['ava'] = path
            pix = pix.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl.setPixmap(pix)
            return lbl

        except Exception as e:
            MainApp.getLogger().error(e)

    def _onNewPassTyped(self):
        npw = self.editPass.text()
        if npw is None or npw.strip() == '':
            self.confirmPass.setDisabled(True)
        else:
            self.confirmPass.setEnabled(True)

    def _onAvatarChange(self):
        fpath = QFileDialog.getOpenFileName(self, caption='Select a new avatar image', directory='./assets/avatars', filter='Images (*.png *jpg *.jpeg *.jfif)')
        
        fpath = fpath[0]
        lbl = self._getAva(fpath)
        self.topLayout.removeWidget(self.avatar)
        self.avatar.setParent(None)
        self.avatar = None
        self.avatar = lbl
        self.topLayout.addWidget(lbl, 0, 0, 3, 1)
        self.repaint()
        self.dat['ava'] = fpath

    def _onSave(self):
        try:
            dat = self.dat

            npw = self.editPass.text()
            cpw = self.confirmPass.text()
            update = False

            if npw is None or npw.strip() == '':
                if dat['password'] == '': # pass not set
                    dialog = QMessageBox(self)
                    dialog.setIcon(QMessageBox.Critical)
                    dialog.setText('You need to set a password!')
                    dialog.setWindowTitle('Password not set')
                    dialog.setStandardButtons(QMessageBox.Ok)
                    dialog.setDefaultButton(QMessageBox.Ok)
                    dialog.setEscapeButton(QMessageBox.Ok)
                    dialog.exec_()
                    return

                else: # no change pass
                    update = True               
                    
            elif npw == cpw: # change & correct
                update = True
                dat['password'] = sha256(bytes(npw, encoding='UTF-8')).hexdigest()
            else: # change & wrong
                dialog = QMessageBox(self)
                dialog.setIcon(QMessageBox.Critical)
                dialog.setText('New password and confirmation not matched, please check again!')
                dialog.setWindowTitle('Unable to change password')
                dialog.setStandardButtons(QMessageBox.Ok)
                dialog.setDefaultButton(QMessageBox.Ok)
                dialog.setEscapeButton(QMessageBox.Ok)
                dialog.exec_()
                return

            if update:
                dat['username'] = self.editUsername.text()
                dat['fullname'] = self.editFullname.text()
                dat['phone'] = self.editPhone.text()
                dat['email'] = self.editEmail.text()
                dat['address'] = self.editAddress.text()
                tmp = self.editBirth.date()
                dat['birth'] = datetime(tmp.year(), tmp.month(), tmp.day())
                MainApp.getDB().saveMemInfo(dat)
                self.editPass.setText('')
                self.confirmPass.setDisabled(True)

                MainApp.getLogger().log('[MongoDB][Redis] Updated info of user %s' % dat['id'])
                self.status.showMessage('Saved', 3000)

        except Exception as e:
            MainApp.getLogger().error(e)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.loginWidget is None:
            self._logout()
            event.ignore()
        else:
            super().closeEvent(event)

    def _onNewAccCreate(self):
        nid = 'TCHMN0000' + str(MainApp.getGlobalID()) + 'S'
        dat = {'id': nid, 'password': '', 'username': nid, 'fullname': '', 'birth': datetime.now(), 'phone': '', 'email': '', 'address': '', 'level': 'Standard'}
        self.dat = dat 
        self._switchWidget()

# =======================================================================
        
class CLIENTS:
    HR_MANAGE = 'hr-manage'
    PRODUCT_MANAGE = 'prod-manage'
    ACC = 'mem-acc'

    WINDOWS = {HR_MANAGE: HRManageWindow, PRODUCT_MANAGE: ProductManageWindow, ACC: MemberInfo}