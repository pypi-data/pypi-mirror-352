"""
Enums for extract_library.py
"""

CEPAC, SMOKING, COUT = (0, 1, 2)  # type of output file (.out, .smout, .cout)
COLUMN, ROW = (0,1)  # Column vs Row orientation
OVERALL, MONTHLY = (0, 1)  # Types of output
DEFAULT_OFFSET = 495  # default maximum lines in each output file section
MONTH, STOP_MONTH, WEEK, YEAR, NO_LONGIT = (0, 1, 2, 3, 4)

TOTAL_MORT_INCL, AVG_MORT_INCL, AVG_MORT_EXCL, MORT_INCL_STD_DEV, MORT_EXCL_STD_DEV = (0, 1, 2, 3, 4)
OUTPUT_TYPE_STRINGS = ("Total Outcome", "Mean Mort Inclusive", "Mean Mort Exclusive", "Std Dev Overall", "Std Dev Monthly")
OVERALL_OUTPUT_TYPES = (TOTAL_MORT_INCL, AVG_MORT_INCL, MORT_INCL_STD_DEV)
MONTHLY_OUTPUT_TYPES = (TOTAL_MORT_INCL, AVG_MORT_EXCL, MORT_EXCL_STD_DEV)