import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pandas
import sys
import datetime
from dateutil.relativedelta import relativedelta
import calendar
import logging


# ======================================================================
# IMPORTANT INFORMATION
# ======================================================================
'''
Developer:     David Alt, USAF (david.a.alt2.mil@mail.mil)
Last updated:  5/1/2019

INTENDED USE:
This application generates the Behavioral Health Therapy Dosage report 
for Madigan Army Medical Center Behavioral Health clinics. It is 
intended as a stop-gap measure until the therapy dosage metric is 
more properly integrated in MHS Genesis or HealtheIntent.

It takes the Excel file exported by PI-EDW, processes the data, and 
generates a new Excel file with the metric report and lists of 
patients who didn't meet the metric, by clinic.

WARNING:  I am not a professional programmer. This application contains 
          basic error-checking and is reasonably robust, BUT it
          absolutely requires that the data on the PI-EDW file is on 
          a specific worksheet using specific column names.
          
          The configuration section highlights what these are. Much of 
          the post-processing depends on specific column names. 
          It would likely be easier to update the PI-EDW report to 
          conform than to edit this application, unless the editor has 
          programming experience and is comfortable with python. 

EDITING METRIC PARAMETERS: 
    Any of the options under "METRIC PARAMETERS" can be safely adjusted
    without disrupting the application, for example, updating the list
    of ICD-10 codes or further restricting the active duty category.

    Please contact me with any questions!

    David Alt, Maj, USAF, MC
'''

# ======================================================================
# CONFIGURATION
# ======================================================================

# EXCEL WORKSHEET FROM PI-EDW REPORT
raw_data_worksheet = 'Diagnoses'

expected_cols = [
    'Patient Name, Full', 
    'EDIPI', 
    'Codified Value', 
    'Date of DX', 
    'Formatted Financial Nbr', 
    'Encounter Type', 
    'Person Location- Nurse Unit / Ambulatory (Admit) Display',
    'DX Code', 
    'Diagnosis Code Description'
]

# METRIC PARAMETERS
lookback_months = -6   # number of months to establish new episode
lookforward_days = 90  # number of days in follow-up period
required_follow_up = 3  # number of visits required in follow-up period
tolerance = 4 # number of days for flexibility determining valid lookback dates

depression_ICD10_codes = ['F32.9', 'F32.0', 'F32.1', 'F33.2', 
                          'F32.4', 'F32.2', 'F33.9', 'F33.0',
                          'F33.1', 'F33.2', 'F33.41', 'F33.3',
                          'F32.9']

PTSD_ICD10_codes = ['F43.10', 'F43.11', 'F43.12']

anxiety_ICD10_codes = ['F40.00', 'F40.01', 'F40.02', 'F40.10', 
                       'F40.11', 'F40.8', 'F40.9', 'F41.0', 
                       'F41.1', 'F41.3', 'F41.8', 'F41.9']

active_duty = ['USA ACTIVE DUTY OFFICER','USA ACTIVE DUTY ENLISTED',
               'USA AD RES OFFICER','USA AD RES ENLISTED',
               'USA RES-30 DAYS OR LESS, NOT IN LOD','USA AD RECRUIT',
               'USA CADET','USA NG OFFICER','USA NG ENLISTED',
               'USA NG-30 DAYS OR LESS, NOT IN LOD','USA RES INACT DUTY TRG OFFICER',
               'USA RES INACT DUTY TRG ENLISTED',
               'USA RES INACT DUTY TRG - NOT IN LOD','USA NG INACT DUTY TRG OFF',
               'USA NG INACT DUTY TRG ENL','USA NG INACT DUTY TRG - NOT IN LOD',
               'NOAA ACTIVE DUTY','USCG ACTIVE DUTY','USCG AD RES','USCG AD RECRUIT',
               'USCG ACADEMY CADET','USCG RES INACT DUTY TRG','USAF ACTIVE DUTY',
               'USAF AD RES','USAF RES-30 DAYS OR LESS,NOT IN LOD','USAF AD RECRUIT',
               'USAF ACADEMY CADET','USAF NG','USAF NG-30 DAYS OR LESS, NOT IN LOD',
               'USAF RES INACT DUTY TRG','USAF RES INACT DTY TRG - NOT IN LOD',
               'USAF NG INACT DUTY TRG','USAF NG INACT DUTY TRG - NOT IN LOD',
               'AD INTEG DISABILITY EVAL SYS MBR','USMC ACTIVE DUTY',
               'USMC AD RES','USMC RES-30 DAYS OR LESS,NOT IN LOD',
               'USMC AD RECRUIT','USMC RES INACT DUTY TRG',
               'USMC RES INACT DTY TRG - NOT IN LOD','USN ACTIVE DUTY',
               'USN AD RES','USN RES-30 DAYS OR LESS, NOT IN LOD',
               'USN AD RECRUIT','USN ACADEMY CADET','USN RES INACT DUTY TRG',
               'USN RES INACT DUTY TRG - NOT IN LOD','USPHS ACTIVE DUTY',
               'USPHS AD RES','USPHS RES INACT DUTY TRG','NATO RECIP AGREE - SR',
               'NATO RECIP AGREE - FLEX','NON-NATO RECIP AGREE']

# PANDAS - Disable the SettingWithCopy warning
pandas.options.mode.chained_assignment = None  # default='warn'

# LOGGING
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('BHTD')
log.setLevel(logging.DEBUG)


# ======================================================================
# FUNCTIONS FOR DATA VALIDATION
# ======================================================================
def validate_data_format(data_file):
    # 1) Has the proper extension (*.xlsx)?
    file_ext = os.path.splitext(data_file)[1]
    if file_ext != '.xlsx':
        tk.messagebox.showerror(
            'Invalid extension',
            'Raw data file must have a *.xslx extension.'
        )
        log.error('Invalid extension. Expecting \'*.xlsx\'')
        return False
    log.info(f'Validated file extension ({file_ext})')

    # 2) Data on the first sheet ("Diagnoses")?
    first_sheet = pandas.ExcelFile(data_file).sheet_names[0]
    if first_sheet != raw_data_worksheet:
        tk.messagebox.showerror(
            'Invalid worksheet name',
            f'Raw data worksheet must be named {raw_data_worksheet}.'
        )
        log.error(f'Invalid worksheet name. Expecting \'{raw_data_worksheet}\'')
        return False
    log.info(f'Validated worksheet name ({first_sheet})')
    
    # 3) Has the expected columns?
    df = pandas.read_excel(data_file, sheet_name=raw_data_worksheet)
    actual_cols = df.columns.tolist()
    if actual_cols != expected_cols:
        tk.messagebox.showerror(
            'Invalid column names',
            f'Raw data must have contain the following columns:\n {expected_cols}'
        )
        log.error(f'Invalid columns in worksheet. Expecting {expected_cols}')
        return False
    log.info(f'Validated column list')
    
    # Passed all the tests
    log.info('Passed all file validation checks')
    return True


def validate_observation_date(selected_month, selected_year, raw_df):    
    log.info(f'Selected date:  {selected_year}-{selected_month}')

    # Determine maximum date range
    dates = get_date_range(raw_df, 'Date of DX')

    # Pad the date range for running reports missing only a few days data
    tolerance_range = (
        (dates[0] + relativedelta(days=-tolerance)),
        (dates[1] + relativedelta(days=tolerance))
    )

    # Determine eligible months for analysis
    valid_dates = get_valid_observation_dates(dates[0], dates[1])
    
    # Check if there is at least six months of data before selected month
    #selected_year = int(selected_year)
    selected_start_date = datetime.datetime(year=int(selected_year), month=selected_month, day=1)
    required_look_back = (selected_start_date + relativedelta(months=-6)).date()
    if required_look_back < tolerance_range[0]:
        tk.messagebox.showerror(
            'Invalid range',
            f'Not enough look-back data for selected period (need at least {-lookback_months} months).'
        )
        log.error(f'Not enough look-back data for selected period (need at least {-lookback_months} months)')
        return False

    # Check that requested period is within range
    if selected_start_date.date() > dates[1]:
        tk.messagebox.showerror(
            'Invalid range',
            f'Selected period falls outside available range (must be before {dates[1]}).'
        )
        log.error(f'Selected period falls outside available range (must be before {dates[1]})')
        return False

    return True # all conditions met
    

# ======================================================================
# FUNCTIONS FOR DATA PROCESSING
# ======================================================================

# Return the date range from a given column in a pandas dataframe
def get_date_range(df, col):
    min = df[col].min().to_pydatetime().date()
    max = df[col].max().to_pydatetime().date()
    return [min, max]


def add_months(date, num_months):
    month = date.month - 1 + num_months
    year = date.year + month // 12
    month = month % 12 + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def get_lookback_date(date):
    return add_months(date, lookback_months)


def get_lookforward_date(date):
    return date + datetime.timedelta(days=lookforward_days)


def get_valid_observation_dates(min, max):
    earliest = add_months(min, 6)
    latest = max - datetime.timedelta(days=lookforward_days)
    return [earliest, latest]


def get_observation_months(min, max):
    valid_dates = get_valid_observation_dates(min, max)
    return pandas.date_range(valid_dates[0], valid_dates[1], freq='M').strftime('%B-%Y').tolist()


def set_observation_period(month, year):
    if (month >= 1 & month <=12):
        if month == 1:
            start_day = '1/1/'
            end_day = '1/31/'

        elif month == 2:
            start_day = '2/1/'
            end_day = '2/28/'

        elif month == 3:
            start_day = '3/1/'
            end_day = '3/31/'

        elif month == 4:
            start_day = '4/1/'
            end_day = '4/30/'

        elif month == 5:
            start_day = '5/1/'
            end_day = '5/31/'

        elif month == 6:
            start_day = '6/1/'
            end_day = '6/30/'

        elif month == 7:
            start_day = '7/1/'
            end_day = '7/31/'

        elif month == 8:
            start_day = '8/1/'
            end_day = '8/31/'

        elif month == 9:
            start_day = '9/1/'
            end_day = '9/30/'

        elif month == 10:
            start_day = '10/1/'
            end_day = '10/31/'

        elif month == 11:
            start_day = '11/1/'
            end_day = '11/30/'

        elif month == 12:
            start_day = '12/1/'
            end_day = '12/31/'
            
        start_day += year
        end_day += year
        return (start_day, end_day)

    else:
        log.error('Invalid month')
        sys.exit()


def get_lookback_count(row, raw):
    patient = row['EDIPI']
    category = row['DX Category']
    index_date = row['Date of DX']
    lookback_date = pandas.Timestamp(row['Lookback Date']) # conversion for futureproofing
    filter = (raw['EDIPI'] == patient) & \
        (raw['DX Category'] == category) & \
        (raw['Date of DX'] < index_date) & \
        (raw['Date of DX'] >= lookback_date)
    return len(raw[filter])


def get_lookforward_count(row, raw):
    patient = row['EDIPI']
    category = row['DX Category']
    index_date = row['Date of DX']
    lookforward_date = index_date + datetime.timedelta(days=90)
    filter = (raw['EDIPI'] == patient) & \
        (raw['DX Category'] == category) & \
        (raw['Date of DX'] > index_date) & \
        (raw['Date of DX'] <= lookforward_date)
    return len(raw[filter])


def categorize_dx(dx):
    if dx in depression_ICD10_codes:
        return 'depression'
    elif dx in PTSD_ICD10_codes:
        return 'PTSD'
    elif dx in anxiety_ICD10_codes:
        return 'anxiety'
    else:
        return 'error'


def get_clinic(location):
    return location.split('-', 1)[1]


def get_dmis(location):
    return location.split('-', 1)[0]


def is_active_duty(patcat):
    if any(x in patcat for x in active_duty):
        return True
    else:
        return False


def met_therapy_dosage(num_visits):
    if num_visits >= required_follow_up:
        return 1
    else:
        return 0


# ======================================================================
# FUNCTIONS FOR REPORTING
# ======================================================================
def get_report_date():
    return cohort_start + ' - ' + cohort_end


def get_report_by_site(cohort):
    df = cohort.groupby(['DMIS', 'Clinic', 'DX Category']).agg({'Met Therapy Dosage':['sum', 'count']})
    df.columns = ['Met Therapy Goal','Cases']
    df['Met Therapy Goal'] = df['Met Therapy Goal'].astype(int)
    df['Percent'] = df['Met Therapy Goal']/df['Cases']
    return df


def get_pivot_by_site(cohort):
    df = get_report_by_site(cohort)
    
    table = pandas.pivot_table(df, values=['Cases', 'Met Therapy Goal'], index=['DMIS', 'Clinic'], columns=['DX Category'], aggfunc=sum, fill_value=0)

    table[('Metric', 'PTSD')] = table[('Met Therapy Goal', 'PTSD')] / table[('Cases', 'PTSD')]
    table[('Metric', 'anxiety')] = table[('Met Therapy Goal', 'anxiety')] / table[('Cases', 'anxiety')]
    table[('Metric', 'depression')] = table[('Met Therapy Goal', 'depression')] / table[('Cases', 'depression')]
    table = table.fillna(0)
    return table



# ======================================================================
# APPLICATION / GUI
# ======================================================================
class BHTDApp():

    def __init__(self):
        self.work_dir = os.getcwd()
        self.file_loaded = False
        self.data_processed = False

        # setup the root window        
        self.master = tk.Tk()
        self.master.wm_title('BH Therapy Dosage')
        self.master.geometry('340x500')
        
        # This prevents the window from being made smaller than the starting geometry
        self.master.update_idletasks()
        self.master.after_idle(lambda: self.master.minsize(self.master.winfo_width(), self.master.winfo_height()))

        # setup the gui and start the UI loop
        self.setup_gui(self.master)
        self.master.mainloop()


    def reset_all(self):
        # reset variables
        self.raw = None
        self.cohort_start = None
        self.cohort_end = None
        self.cohort = None
        self.report = None
        log.info('Variables cleared')

        # reset GUI elements
        self.month_list.selection_clear(0, tk.END)
        self.year_list.selection_clear(0, tk.END)
        self.data_status.configure(text='Status:  no data file loaded')
        self.data_status.update()
        self.processed_status.configure(text='Status:  unprocessed')
        self.processed_status.update()

        self.process_btn.config(state=tk.DISABLED)
        self.export_report_btn.config(state=tk.DISABLED)

        log.info('GUI elements reset')


    ###### GUI SETUP ######
    def setup_gui(self, master):
        master.grid_columnconfigure(0, minsize=50, weight=0)
        master.grid_columnconfigure(1, minsize=150, weight=1)
        master.grid_rowconfigure(5, weight=1)

        tk.Label(master, text='1', font=('Helvetica', 30)).grid(row=0, column=0)
        tk.Label(master, text='2', font=('Helvetica', 30)).grid(row=1, column=0)
        tk.Label(master, text='3', font=('Helvetica', 30)).grid(row=2, column=0)
        tk.Label(master, text='4', font=('Helvetica', 30)).grid(row=4, column=0)

        # Row 0 (load data file)
        load_frame = tk.Frame(master)

        self.load_btn = tk.Button(load_frame, text='Load data file', command=self.on_load_data)
        self.load_btn.pack(anchor=tk.W)

        self.data_status = ttk.Label(load_frame, text='Status:  no data file loaded')
        self.data_status.pack(fill=tk.X)
        
        load_frame.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=10, pady=10)

        # Row 1 (select dates)
        select_frame_outer = tk.Frame(master)
        
        ttk.Label(select_frame_outer, text='Select observation period:').pack(anchor=tk.W)

        select_frame_inner = tk.Frame(select_frame_outer)
        select_frame_inner.pack(fill=tk.X)
        
        self.month_list = tk.Listbox(select_frame_inner, height=12, width=12)
        self.month_list.configure(exportselection=False) # prevents listbox from losing selection
        self.month_list.pack(side=tk.LEFT)
        for i in range(1, 13):
            self.month_list.insert(tk.END, calendar.month_name[i])

        self.year_list = tk.Listbox(select_frame_inner, height=12, width=6)
        self.year_list.configure(exportselection=False) # prevents listbox from losing selection
        self.year_list.pack()
        for i in range(2018,2030): 
            self.year_list.insert(tk.END, i)

        select_frame_outer.grid(row=1, column=1, sticky=tk.W+tk.E, padx=10, pady=10)

        # Rows 2-3 (process data)
        self.process_btn = tk.Button(master, text='Process data', command=self.on_process_data)
        self.process_btn.grid(row=2, column=1, sticky=tk.W, padx=10)
        self.process_btn.config(state=tk.DISABLED)

        self.processed_status = ttk.Label(master, text='Status:  unprocessed')
        self.processed_status.grid(row=3, column=1, columnspan=2, sticky=tk.W+tk.E, padx=10)

        # Row 4 (report buttons)
        self.export_report_btn = tk.Button(master, text='Export report', command=self.on_export_report)
        self.export_report_btn.grid(row=4, column=1, sticky=tk.W, padx=10)
        self.export_report_btn.config(state=tk.DISABLED)
        

    ###### BUTTON FUNCTIONS ######
    def on_load_data(self):
        # Launch an Open File dialog
        try:
            result = tk.filedialog.askopenfilename(
                initialdir=os.getcwd(), 
                filetypes=[('Excel files', '*.xlsx')],
                title='Select data file')
            if result is None: # nothing selected; cancel
                return
        except:
            print(f'Unexpected error:  {sys.exc_info()[0]}')

        else: # data file is selected
            self.reset_all() # wipe everything clean
            self.data_status.configure(text='Status:  Loading data ...')
            self.data_status.update()

            if validate_data_format(result):
                # Create a dataframe from the raw data
                self.raw = pandas.read_excel(result, sheet_name=raw_data_worksheet)
                                
                # Determine maximum date range
                dates = get_date_range(self.raw, 'Date of DX')
                log.info(f'Total data range:  {dates[0]} to {dates[1]}')

                # Determine eligible months for analysis
                valid_dates = get_valid_observation_dates(dates[0], dates[1])
                log.info(f'Observation range:  {valid_dates[0]} to {valid_dates[1]}')
                
                # Determine tolerance range
                tolerance_range = (
                    (dates[0] + relativedelta(days=-tolerance)),
                    (dates[1] + relativedelta(days=tolerance))
                )
                log.info(f'Tolerance range:  {tolerance_range[0]} to {tolerance_range[1]}')

                # Update GUI with date information
                self.process_btn.config(state=tk.NORMAL)
                
                status = f'Status:  File loaded\n\n' + \
                    f'Total data range:     {dates[0]} to {dates[1]}\n' + \
                    f'Tolerance range:    {tolerance_range[0]} to {tolerance_range[1]}\n' + \
                    f'Observation range:  {valid_dates[0]} to {valid_dates[1]}'
                self.data_status.configure(text=status)
                self.data_status.update()
            
            else: # invalid data format
                error_msg = ('Unable to process the loaded file. Possible reasons include wrong file type'
                            ', incorrect worksheet name (should be \'Diagnoses\'), or mislabeled columns.')
                tk.messagebox.showerror('Invalid file', error_msg)
                log.error(f'Invalid file. {error_msg}')
                self.reset_all()


    def on_process_data(self):
        # if either listbox doesn't have something selected ...
        if (not self.month_list.curselection() or
            not self.year_list.curselection()
        ):
            tk.messagebox.showwarning(
                'Invalid selection',
                'You must select both a month and a year.'
            )
            log.error('Nothing selected in one or both listboxes')

        else: # something selected in both listboxes
            month = self.month_list.curselection()[0] + 1 # +1 to offset 0-based index
            year = str(self.year_list.get(self.year_list.curselection()[0]))
            
            if validate_observation_date(month, year, self.raw):
                self.processed_status.configure(text=f'Status:  processing data for {month}/{year} ...')
                self.processed_status.update()

                log.info(f'Total encounters:  {len(self.raw)}')

                # Set the start and end dates for the observation period
                self.cohort_start, self.cohort_end = set_observation_period(month, year)
                
                # Add the diagnosis category column to the raw data
                self.raw['DX Category'] = self.raw['DX Code'].apply(categorize_dx)

                # Add the Active Duty column to the raw data
                self.raw['Active Duty'] = self.raw['Codified Value'].apply(is_active_duty)

                # Add the DMIS (facility) column to the raw data
                self.raw['DMIS'] = self.raw['Person Location- Nurse Unit / Ambulatory (Admit) Display'].apply(get_dmis)

                # Add the clinic column to the raw data
                self.raw['Clinic'] = self.raw['Person Location- Nurse Unit / Ambulatory (Admit) Display'].apply(get_clinic)

                # Make a new dataframe with just active duty
                active_duty = self.raw[self.raw['Active Duty'] == True]
                log.info(f'Active duty encounters:  {len(active_duty)}')

                # Extract possible candidates (i.e., patients in observation window)
                possible_candidates = active_duty[(active_duty['Date of DX'] > self.cohort_start) & 
                    (active_duty['Date of DX'] < self.cohort_end)]
                log.info(f'Possible candidates in observation period:  {len(possible_candidates)}')

                # Group by patient and diagnosis category
                grp_by_pt = possible_candidates.groupby(['EDIPI', 'DX Category'])

                # Create a list of the first encounter for each patient-diagnosis group
                first_visits = []

                for key, group in grp_by_pt:
                    earliest = group['Date of DX'].min()
                    
                    for idx, row in group.iterrows():
                        if row['Date of DX'] == earliest:
                            name = row['Patient Name, Full']
                            EDIPI = row['EDIPI']
                            date = row['Date of DX']
                            FIN = row['Formatted Financial Nbr']
                            enc_type = row['Encounter Type']
                            facility = row['Person Location- Nurse Unit / Ambulatory (Admit) Display']
                            dx_code = row['DX Code']
                            dx = row['Diagnosis Code Description']
                            dx_category = row['DX Category']
                            active_duty = row['Active Duty']
                            dmis = row['DMIS']
                            clinic = row['Clinic']
                        
                            first_visits.append([name, EDIPI, date, FIN, enc_type, facility, dx_code, dx, dx_category, active_duty, dmis, clinic])
                            
                # Create a new dataframe with the refined candidate list
                cols = ['Patient Name, Full',
                        'EDIPI',
                        'Date of DX',
                        'FIN',
                        'Encounter Type',
                        'Person Location- Nurse Unit / Ambulatory (Admit) Display',
                        'DX Code',
                        'Diagnosis Code Description',
                        'DX Category',
                        'Active Duty',
                        'DMIS',
                        'Clinic']

                # candidates lists the first encounter for each diagnostic category in the observation period.
                candidates = pandas.DataFrame(columns=cols, data=first_visits)

                # Add a column showing lookback date to candidates
                candidates['Lookback Date'] = candidates['Date of DX'].apply(get_lookback_date)

                # Add a column with number of visits in the lookback period
                candidates['Lookback Count'] = candidates.apply(lambda row: get_lookback_count(row, self.raw), axis=1)

                # Add a column for whether the case counts as a new episode
                candidates['New Episode'] = candidates['Lookback Count'].apply(lambda x: x == 0)

                # Create the final cohort of index visits by keeping only new episodes of care
                self.cohort = candidates[candidates['New Episode'] == True]
                log.info(f'Cohort cases:  {len(self.cohort)}')
                
                # Add a column with number of visits in the 90 days after the index visit
                self.cohort['Lookforward Count'] = self.cohort.apply(lambda row: get_lookforward_count(row, self.raw), axis=1)

                # Add a column if met therapy dosage (>= 3); success is 1 (for True), failure is 0 (for False)
                self.cohort['Met Therapy Dosage'] = self.cohort['Lookforward Count'].apply(met_therapy_dosage)

                # Get the initial report
                sub_report = get_pivot_by_site(self.cohort)

                # Add totals columns 
                sub_report['Cases', 'all'] = sub_report['Cases', 'PTSD'] + sub_report['Cases', 'anxiety'] + sub_report['Cases', 'depression']
                sub_report['Met Therapy Goal', 'all'] = sub_report['Met Therapy Goal', 'PTSD'] + sub_report['Met Therapy Goal', 'anxiety'] + sub_report['Met Therapy Goal', 'depression']
                sub_report['Metric', 'all'] = sub_report['Met Therapy Goal', 'all'] / sub_report['Cases', 'all']

                # Reorder the columns
                col_order = [('Met Therapy Goal', 'anxiety'), ('Met Therapy Goal', 'depression'), ('Met Therapy Goal', 'PTSD'), ('Met Therapy Goal', 'all'),
                            ('Cases', 'anxiety'), ('Cases', 'depression'), ('Cases', 'PTSD'), ('Cases', 'all'),
                            ('Metric', 'anxiety'), ('Metric', 'depression'), ('Metric', 'PTSD'), ('Metric', 'all')]

                # Generate the final report
                self.report = pandas.DataFrame(sub_report, columns=col_order)

                # Update the process data status label and enable the export report button
                self.processed_status.configure(text=f'Status:  data for {month}/{year} ready for export')
                self.processed_status.update()
                self.export_report_btn.config(state=tk.NORMAL)
            
            else:
                pass # by default returns to selection; errors show in validation method

            

    def on_export_report(self):
        # Setup the output filename
        tokens = self.cohort_start.split('/')
        default_report_name = 'BH Therapy Dosage (' + tokens[2] + '-' + tokens[0] + ').xlsx'
        report_name = filedialog.asksaveasfilename(
            title='Export report ...',
            defaultextension='.xlsx',
            filetypes=[('Excel files', '*.xlsx')],
            initialfile=default_report_name
        )

        # Output the report and patient lists to Excel
        with pandas.ExcelWriter(report_name, datetime_format='M/d/yyyy') as writer:
            self.report.to_excel(writer, sheet_name='Report', startrow=3, startcol=0)
            worksheet = writer.sheets['Report']
            worksheet.write(0,0,'Start: ')
            worksheet.write(0,1, self.cohort_start)
            worksheet.write(1,0,'End: ')
            worksheet.write(1,1, self.cohort_end)
            
            clinics = list(self.report.index.values)  # get a list of all the clinics in the report
            for clinic in clinics:
                # replace special characters from clinic name with spaces
                sheet = clinic[1].translate ({ord(c): ' ' for c in '[]:*?/\\'})
                
                # display only patients who did NOT meet the threshold for the given clinic,
                #   and remove unnecessary columns
                filter = (self.cohort['Clinic'] == clinic[1]) & (self.cohort['Met Therapy Dosage'] == 0)
                cols = ['Patient Name, Full', 'EDIPI', 'DX Category', 'Date of DX', 'Lookforward Count']
                patients = pandas.DataFrame(self.cohort[filter], columns=cols)
                patients.rename(columns={'Lookforward Count':'F/U Visits'}, inplace=True)
                
                # send the patient list to Excel
                patients.sort_values('Patient Name, Full').to_excel(writer, sheet_name=sheet, index=False)
                
                # Adjust the starting width of all the columns for readability
                clinic_sheet = writer.sheets[sheet]
                for idx, col in enumerate(patients):  # loop through all columns
                    series = patients[col]
                    max_len = max((
                        series.astype(str).map(len).max(),  # len of largest item
                        len(str(series.name))  # len of column name/header
                        )) + 1  # adding a little extra space
                    clinic_sheet.set_column(idx, idx, max_len)  # set column width
            
        log.info(f'Successfully exported as:  {report_name}')
        self.processed_status.configure(text='Status:  exported')
        self.processed_status.update()

        

if __name__ == '__main__':
    bhtd = BHTDApp()
