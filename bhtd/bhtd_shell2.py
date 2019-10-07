import sys
from PySide2.QtCore import QDate, Signal, Slot, QObject
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QFileDialog, QErrorMessage, QMessageBox, QLabel
import calendar
import logging
import pandas as pd
import bhtd as bh

# Python environment requires: python3, pandas, xlrd

# UI components: dateEdit, load_file_btn, save_report_btn, menubar, statusbar

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s'
)
log = logging.getLogger('UI')


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
    
    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class SmartBool(QObject):
    valueChanged = Signal(bool)         # Signal to be emitted when value changes.

    def __init__(self, value=False):
        super(SmartBool, self).__init__()   # Call QObject contructor.
        self.__value = value                # False initialized by default.

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if self.__value != value:
            self.__value = value
            self.valueChanged.emit(value)   # value changed; emit signal.


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.file_loaded = SmartBool(False)

        # load the ui file
        self.ui = QUiLoader().load('bhtd_shell2.ui')

        # add the log viewer
        self.log_display = QTextEditLogger(self)
        self.log_display.setFormatter(logging.Formatter('%(levelname)s:  %(message)s'))
        log.addHandler(self.log_display)
        bh.log.addHandler(self.log_display) # pipe the log from the BHTD module to display
        self.ui.horizontalLayout.addWidget(self.log_display.widget)

        # set the default report date to four months before current date
        now = QDate.currentDate()
        default_report_date = now.addMonths(-8) # should be 4
        self.ui.dateEdit.setDate(default_report_date)
        
        # add the range display label
        self.range_label = QLabel()
        self.ui.verticalLayout_2.addWidget(self.range_label)

        # set the save_report_btn's initial state to disabled
        self.ui.save_report_btn.setEnabled(False)
        
        # connect signals/slots
        self.ui.load_file_btn.clicked.connect(self.on_load_file_btn_click)
        self.ui.save_report_btn.clicked.connect(self.on_save_report_btn_click)
        self.file_loaded.valueChanged.connect(self.on_file_loaded_changed)

        # welcome message
        self.log_display.widget.appendPlainText('Welcome to the Behavioral Health Therapy Dosage Reporting Tool!')
        self.log_display.widget.appendPlainText('Please load the therapy dosage report from PI-EDW.')
        self.log_display.widget.appendPlainText('Note: This program will permit generating reports with incomplete follow-up data.\n')

    def on_file_loaded_changed(self):
        self.ui.save_report_btn.setEnabled(self.file_loaded.value)

    def on_load_file_btn_click(self):
        self.ui.statusbar.showMessage('Loading file ...')
        
        file_name = QFileDialog.getOpenFileName(self)[0]
        if file_name and bh.validate_raw_data(file_name):
            self.file_loaded.value = True
            self.raw = bh.load_raw_data(file_name)
            self.dates = bh.get_date_range(self.raw, 'Date of DX')
            self.valid_dates = bh.validate_observation_dates(self.dates[0], self.dates[1])
            valid_start = self.valid_dates[0].strftime('%B %Y')
            valid_end = self.valid_dates[1].strftime('%B %Y')

            self.range_label.setText(f'Valid observation range:\n{valid_start} through {valid_end}')
                
            log.info(f'Opened  {file_name}')
            log.info(f'PI-EDW file contains encounters from:  {self.dates[0].date()} to {self.dates[1].date()}')
            log.info(f'Valid observation range:  {valid_start} through {valid_end}\n')
            
        elif file_name and not bh.validate_raw_data(file_name):
            self.file_loaded.value = False
            self.raw = None
            self.dates = None
            self.valid_dates = None
            self.range_label.setText('')
            
            QMessageBox.about(self, 'Error', 'Invalid data file. Program reset.')
        
        else: # user cancelled; do nothing
            pass

        self.ui.statusbar.showMessage(f'File loaded:  {self.file_loaded.value}')
        
    
    def on_save_report_btn_click(self):
        if not self.file_loaded.value:
            return

        else:
            date = self.ui.dateEdit.date() # needs to be converted to pd.Timestamp
            observation_period = pd.Timestamp(f'{date.year()}-{date.month()}-{date.day()}')
            if bh.date_in_range(
                observation_period, self.valid_dates[0], self.dates[1] # allows reports w/incomplete F/U
            ):
                log.info('Requested report falls within the valid observation range.')
                cohort = bh.prepare_cohort(self.raw, observation_period)
                
                #log.info(f'Cohort for {display_date}:  {len(cohort)}')
            else:
                log.error('Requested report falls outside the valid observation range.')
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Window()
    main_window.ui.show() # you have to show ui, not the window itself
    sys.exit(app.exec_())