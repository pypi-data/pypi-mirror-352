import sys
import os

# Add the src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from mpec_extract import *

if __name__ == "__main__":

    import pandas as pd

    data_filepath = r"C:\Users\livia\OneDrive - Mass General Brigham\Documents\extract_backend\tests\50d_new.out_data"
    desired_outputs_path = r"C:\Users\livia\OneDrive - Mass General Brigham\Documents\mct\csv_validation_extraction_table_20plus.csv"
    all_outfiles_dir = r"C:\Users\livia\OneDrive - Mass General Brigham\Documents\mct\Outfiles"
    extract_out_file_path = r"C:\Users\livia\OneDrive - Mass General Brigham\Documents\mct\TEST_MCT_OUT.extract_out"

    extract_end_to_end(data_filepath, desired_outputs_path, all_outfiles_dir, extract_out_file_path, overall=True,
                       save_as_csv='./df_to_csv_overall_python.csv')
    mth_out = extract_end_to_end(data_filepath, desired_outputs_path, all_outfiles_dir, extract_out_file_path,
                                 monthly=True, save_as_csv=None)


    def write_single_output_to_csv(result, output_label, filepath):
        rows = []
        for month, run_dict in result.get(output_label, {}).items():
            for run_name, value in run_dict.items():
                rows.append({
                    "run_name": run_name,
                    "month": month,
                    "value": value
                })

        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)


    write_single_output_to_csv(mth_out, "CHRM7_Death", "./dict_to_csv_mth_python.csv")
