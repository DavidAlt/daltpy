import logging
import os
import pandas as pd

# LOGGING
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s'
)
log = logging.getLogger('DATA')

# PANDAS - Disable the SettingWithCopy warning
pd.options.mode.chained_assignment = None  # default='warn'

# ======================================================================
# CONFIG
# ======================================================================
data_worksheet = 'Diagnoses'
expected_cols = [
    'Patient Name, Full', 
    'EDIPI', 
    'Codified Value', 
    'Date of DX', 
    'Formatted Financial Nbr', 
    'Encounter Type', 
    'Person Location- Nurse Unit / Ambulatory (Admit) Display',
    'DX Code', 
    'Diagnosis Code Description']

lookback_months = 6   # number of months to establish new episode
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
#pandas.options.mode.chained_assignment = None  # default='warn'



# ======================================================================
# FUNCTIONS
# ======================================================================

# Excel validation functions
def validate_raw_data(file):
    if is_xlsx(file):
        return has_worksheet(file) and has_columns(file)
    else:
        return False

def is_xlsx(file):
    return (os.path.splitext(file)[1] == '.xlsx')

def has_worksheet(file):
    return (data_worksheet in pd.ExcelFile(file).sheet_names)

def has_columns(file):
    actual_cols = pd.read_excel(file, sheet_name=data_worksheet).columns.tolist()
    return (actual_cols == expected_cols)


# Loads the PI-EDW raw data into a dataframe
def load_raw_data(xlsx_file):
    df = pd.read_excel(xlsx_file, sheet_name=data_worksheet)
    return df


# Return the date range in a dataframe column (as pd.Timestamp)
def get_date_range(df, col):
    min = df[col].min()
    max = df[col].max()
    return [min, max]    

def get_lookback_date(date):
    return (date - pd.DateOffset(months=lookback_months))

def get_lookforward_date(date):
    return (date + pd.DateOffset(days=lookforward_days))

def get_observation_dates(min, max):
    earliest = min + pd.DateOffset(months=lookback_months)
    latest = max - pd.DateOffset(days=lookforward_days)
    return earliest, latest

def transform_observation_dates(min, max):
    # start date is too late (incomplete month); go to next month
    if min.day > tolerance:
        min = min + pd.DateOffset(months=1)
    # end date is too early (incomplete month); go to previous month
    if max.day <= (max + pd.tseries.offsets.MonthEnd(0)).day - tolerance:
        max = max - pd.DateOffset(months=1)
    # now that we have valid months, set dates to first/last of month
    min = pd.Timestamp(f'{min.year}-{min.month}-01')
    max = max + pd.tseries.offsets.MonthEnd(0)
    return (min, max)

def validate_observation_dates(min, max):
    min, max = get_observation_dates(min, max)
    min, max = transform_observation_dates(min, max)
    return min, max

def date_in_range(date, min, max):
    return (min <= date <= max)

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
            
        start_day += str(year)
        end_day += str(year)

        start = pd.Timestamp(start_day)
        end = pd.Timestamp(end_day)
        return (start, end)

    else:
        log.error('Invalid month')
        sys.exit()


# Data processing functions
def categorize_dx(dx):
    if dx in depression_ICD10_codes:
        return 'depression'
    elif dx in PTSD_ICD10_codes:
        return 'PTSD'
    elif dx in anxiety_ICD10_codes:
        return 'anxiety'
    else:
        return 'error'

def is_active_duty(patcat):
    if any(x in patcat for x in active_duty):
        return True
    else:
        return False

def get_dmis(location):
    return location.split('-', 1)[0]

def get_clinic(location):
    return location.split('-', 1)[1]

def get_lookback_count(row, raw_df):
    patient = row['EDIPI']
    category = row['DX Category']
    index_date = row['Date of DX']
    lookback_date = row['Lookback Date']
    filter = (raw_df['EDIPI'] == patient) & \
        (raw_df['DX Category'] == category) & \
        (raw_df['Date of DX'] < index_date) & \
        (raw_df['Date of DX'] >= lookback_date)
    return len(raw_df[filter])

def get_lookforward_count(row, raw_df):
    patient = row['EDIPI']
    category = row['DX Category']
    index_date = row['Date of DX']
    lookforward_date = get_lookforward_date(index_date)
    filter = (raw_df['EDIPI'] == patient) & \
        (raw_df['DX Category'] == category) & \
        (raw_df['Date of DX'] > index_date) & \
        (raw_df['Date of DX'] <= lookforward_date)
    return len(raw_df[filter])

def met_therapy_dosage(num_visits):
    if num_visits >= required_follow_up:
        return 1
    else:
        return 0

def get_candidates(raw_df, date):
    log.info(f'Encounters in raw data (total):  {len(raw_df)}')
    # Set the start and end dates for the observation period
    cohort_start, cohort_end = set_observation_period(date.month, date.year)
    
    # Add the diagnosis category column to the raw data
    raw_df['DX Category'] = raw_df['DX Code'].apply(categorize_dx)

    # Add the Active Duty column to the raw data
    raw_df['Active Duty'] = raw_df['Codified Value'].apply(is_active_duty)

    # Add the DMIS (facility) column to the raw data
    raw_df['DMIS'] = raw_df['Person Location- Nurse Unit / Ambulatory (Admit) Display'].apply(get_dmis)

    # Add the clinic column to the raw data
    raw_df['Clinic'] = raw_df['Person Location- Nurse Unit / Ambulatory (Admit) Display'].apply(get_clinic)

    # Make a new dataframe with just active duty
    active_duty = raw_df[raw_df['Active Duty'] == True]
    log.info(f'Active duty encounters (total):  {len(active_duty)}')

    # Extract possible candidates (i.e., patients in observation window)
    possible_candidates = active_duty[(active_duty['Date of DX'] > cohort_start) & 
        (active_duty['Date of DX'] < cohort_end)]
    log.info(f'Active duty encounters (observation period):  {len(possible_candidates)}')

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
    candidates = pd.DataFrame(columns=cols, data=first_visits)
    log.info(f'First-only active duty encounters (observation period):  {len(candidates)}')
    return candidates


def prepare_cohort(raw_df, observation_period):
    candidates = get_candidates(raw_df, observation_period)

    # Add a column showing lookback date to candidates
    candidates['Lookback Date'] = candidates['Date of DX'].apply(get_lookback_date)

    # Add a column with number of visits in the lookback period
    candidates['Lookback Count'] = candidates.apply(lambda row: get_lookback_count(row, raw_df), axis=1)

    # Add a column for whether the case counts as a new episode
    candidates['New Episode'] = candidates['Lookback Count'].apply(lambda x: x == 0)

    # Create the final cohort of index visits by keeping only new episodes of care
    cohort = candidates[candidates['New Episode'] == True]
    
    display_date = observation_period.strftime('%B %Y')
    log.info(f'New treatment episodes (observation period):  {len(cohort)}\n')
    log.info(f'Final cohort for {display_date}:  {len(cohort)} eligible encounters')
    
    # Add a column with number of visits in the 90 days after the index visit
    cohort['Lookforward Count'] = cohort.apply(lambda row: get_lookforward_count(row, raw_df), axis=1)

    # Add a column if met therapy dosage (>= 3); success is 1 (for True), failure is 0 (for False)
    cohort['Met Therapy Dosage'] = cohort['Lookforward Count'].apply(met_therapy_dosage)

    return cohort