import pandas as pd
from .extract_helper import *
import os

def extract_end_to_end(data_fpath, desired_outputs_fpath, outfiles_dir, extract_out_fpath, monthly=False, overall=False,
                       save_as_csv=None):
    # ------------------------------------------ Extract Data file --------------------------------------------#
    data = import_data_file(data_fpath)

    # ------------------------------------ Create Cohorts Objects --------------------------------------------- #
    # ------------------------ Get all the filepaths of the output files to extract from  --------------------- #
    outfiles_list = []
    for root, dirs, files in os.walk(os.path.abspath(outfiles_dir)):
        for file in files:
            outfiles_list.append(os.path.join(root, file))

    cohorts_list = [Cohort(filepath, None, filepath, None, data) for filepath in outfiles_list]

    # ------------------------------------ Create Outputs Objects ---------------------------------------- #
    # ---------------------- Reading in the outputs that the user wants to extract ----------------------- #

    df_desired_outputs = pd.read_csv(desired_outputs_fpath)
    df_desired_outputs = clean_outputs_df(df_desired_outputs)

    # TODO schema verification for the df/input excel sheet
    outputs_list = []
    for row in df_desired_outputs.itertuples():
        if row.Output == OVERALL:
            outputs_list.append(
                Output(row.Label, row.Section, row.TextID, int(row.RowOffset), row.ColLetter, TOTAL_MORT_INCL))

        if row.Output == MONTHLY:
            month_nums = parse_month(row.Months)  # get individual month nums from the months expression
            for m in month_nums:  # create MonthlyOutput object for each month
                outputs_list.append(
                    MonthlyOutput(row.Label, m, row.TextID, int(row.RowOffset), row.ColLetter, TOTAL_MORT_INCL))

    # ------------------------------------ Create MultiCohort Object ---------------------------------------- #
    # --------------------------------- Set up the extraction task & extract! ------------------------------- #
    extract_task = MultiCohort(cohorts_list, outputs_list, data)
    # extract_task.write_extracted_outputs(extract_out_fpath, COLUMN)
    extract_task.extract_outputs()
    if overall:
        df_out = extract_task.write_overall_outputs_to_df(save_as_csv=save_as_csv)
        return df_out
    if monthly:
        df_out_monthly = extract_task.write_monthly_outputs_to_dict()
        return df_out_monthly

    # TODO incorporate invisible outputs like monthly num alive
    # TODO test against the MCT GUI results

