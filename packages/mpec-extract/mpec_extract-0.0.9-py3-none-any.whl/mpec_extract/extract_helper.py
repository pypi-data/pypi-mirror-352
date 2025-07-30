"""
Modularized library containing classes and helper functions from the MCT backend which are used for extraction.
Note: it is easier to have both classes and helper functions in the same module to avoid circular imports.
"""

from .extract_enums import *
import pickle
import pandas as pd

# ---------------- Classes from original MCT script (m_cohorts.py) --------------------------------------#
"""
Class for defining generic Monthly output extractions without actually specifiying a month num. 
create_output will create the MonthlyOutput object
"""
class GenericMonth(object):
    def __init__(self, generic_label, identifier, row_offset, col_letter, output_type, apply_disc = False ,enable_disc = True, time_step=MONTH):
        """
        :param str generic_label: the user-specified label that will have month numbers appended to it
        :param bool enable_disc: a bool indicating whether OutputPanel.discount_CB should be enabled for this output at all in the GUI
        :param bool apply_disc: whether the user specified that discounting should be applied in OutputPanel.discount_CB if the combo box is enabled for the output when selected from the dropdown menu
        """
        self.label = generic_label
        self.identifier = identifier
        self.row_offset = row_offset
        self.col_letter = col_letter
        self.output_type = output_type
        self.apply_disc = apply_disc
        self.enable_disc = enable_disc
        self.time_step = time_step
    def create_output(self, label, month_num):
        """
        Generates a MonthlyOutput class object from a GenericMonth object for a specific month number. Used to extract the number alive and transmissions from CohortData.i_outputs
        :param str label: the output label which will have the month number appended to it
        :param int month_num: the month number to extract
        :return: a MonthlyOutput object for the specified month number
        :rtype: MonthlyOutput
        """
        return MonthlyOutput(label, month_num, self.identifier,
                             self.row_offset, self.col_letter, self.output_type,
                             self.apply_disc, self.time_step)

class CohortData(object):
    """
    class for specifying output data in the .out file
    """
    def __init__(self, version, time_step, visible_outputs_overall, visible_outputs_monthly, invisible_outputs):
        """
        :param str version: String for the model version. May be a CEPAC side version,"smoking" for STOP, "cout" for the .cout file, or another model like "cmv" or "match."
        :param visible_outputs_overall: a list of overall Output class objects for the built-in overall output list for this version
        :param visible_outputs_monthly: a list of GenericMonth class objects for the built-in monthly output list for this version
        :param invisible_outputs: a list of outputs that will not be displayed but which will need to be extracted behind the scenes for most tasks (runsize, monthly number alive, monthly primary transmissions). See GenericMonth.create_output
        """
        self.version = version
        self.time_step = time_step
        #dictionary of labels to outputs
        #outputs should only contain Output objects or Generic Month objects since we dont know month num yet
        self.v_outputs_overall = dict([(output.label,output) for output in visible_outputs_overall])
        self.v_outputs_overall_labels = [output.label for output in visible_outputs_overall]
        self.v_outputs_monthly = dict([(output.label,output) for output in visible_outputs_monthly])
        self.v_outputs_monthly_labels = [output.label for output in visible_outputs_monthly]
        self.v_outputs = {OVERALL:self.v_outputs_overall, MONTHLY:self.v_outputs_monthly}
        self.v_outputs_labels = {OVERALL:self.v_outputs_overall_labels, MONTHLY:self.v_outputs_monthly_labels}
        self.i_outputs = dict([(output.label,output) for output in invisible_outputs])


class Text(object):
    """
    Class representing the contents of a cohort/run output file.
    Texts are characterized by
        Whole unedited text
        Text broken into chunks by sections based on headers

    Attributes:
        self.whole: list where each element is a line from the file (each element would be a string)
        self.sections: dict whose keys are section headers in the output file, and whose values are a subset of self.whole
            i.e. each key-value pair contains a "chunk" of output lines corresponding to each section.
        self.id_indices: dict whose keys are text identifiers, and whose values are the line number where this text
            identifier can be found within the section "chunk"

    E.g.

    for an output file: "cepac_run_120.OUT"), the text from this file is stored line by line in self.whole.
    Then, when I want to extract a TB-related output, our section header will be "TB SUMMARY OUTPUTS". Which should
    evetually be found in self.sections, so I could search: self.sections["TB SUMMARY OUTPUTS"] and would get a smaller list
    of the lines found only in that section.

    Then I want to search specifically for an output relative to the text identifier: "Num on TB treatment"
    This should eventualy be found in self.id_indices, so I would search: self.id_indices["Num on TB treatment"] and that
    would return the line number (or element) within self.sections["TB SUMMARY OUTPUTS"] where "Num on TB treatment" is
    located. Let's say it's 12.

    So finally, I could say self.sections["TB SUMMARY OUTPUTS"][12 + row_offset] --> gives me the line that I specifed for
    extractions.
    """

    def __init__(self, whole):
        self.whole = whole
        self.sections = {}
        self.id_indices = {}


class Cohort(object):
    """
    Class for specifing characteristics of each individual cohort(run)
    Cohorts are characterized by
        Run Size
        Intended Population Size
        Time of Entry
    """

    def __init__(self, filepath, popsize, label, interactions, cohort_data, month_of_entry=0):
        """
        :param str filepath: the path to the output (.out, .smout, or .cout) file we are extracting from
        :param float popsize: intended population size if weighting, None if simple extraction
        :param str label: label for the file, can be "" if we are not weighting outputs
        :param str interactions: interactions to be applied, can be "" or "None"; interactions are loaded from a file rather than directly from the GUI so they are always "" when doing simple GUI-based extractions
        :param CohortData cohort_data: data loaded from MainFrame.curr_data_file (the .out_data template from this model version)
        :param int month_of_entry: for time-varying weighting, defaults to 0
        """
        self.filepath = filepath
        self.label = label
        # user input intended population size of run
        self.popsize = popsize
        # Text object holding CEPAC output file and sections defined by output headers
        self.text = Text([])
        # dictionary of Output objects to output values
        self.output_values = {}
        self.interactions = interactions
        # Month the cohort enters (0 for prevalent cohort).
        # If this value is not 0 can only specify monthly outcomes
        self.month_of_entry = month_of_entry
        self.cohort_data = cohort_data

    def get_runsize(self, text, version=CEPAC):
        """
        Gets the runsize from the output file text (not a filepath)
        Calls extract_output using CohortData.i_outputs for prevalent HIV+ and HIV- if CEPAC, or Runsize if STOP
        :return: an int representing the run size
        :rtype: int
        """
        if self.cohort_data.version in ["50d", "50d_yr", "50c", "45c"]:
            # create Output to get # of prevalent HIV+ and HIV- patients
            hivpos_output = self.cohort_data.i_outputs["HIV+ Prev"]
            hivneg_output = self.cohort_data.i_outputs["HIV- Prev"]

            num_pos = int(hivpos_output.extract_output(text))
            num_neg = int(hivneg_output.extract_output(text))

            return num_pos + num_neg

        else:
            runsize_output = self.cohort_data.i_outputs["Runsize"]
            return int(runsize_output.extract_output(text))

    def extract_output_values(self, text, outputs):
        """
        Gets output values from the text of the output file
        Adds the values to Cohort.output_values dictionary
        :param Text text: the Text object containing the run results
        :param Output outputs: a list of Output class objects

        """
        for output in outputs:
            # pass in month of entry for monthly inputs
            if type(output).__name__ in {"MonthlyOutput", "MonthlyInteractionOutput"}:
                extracted_value = output.extract_output(text, self.month_of_entry, interactions=self.interactions)
            else:
                extracted_value = output.extract_output(text, interactions=self.interactions)
            try:
                extracted_value = clean_output(extracted_value)
            except TypeError:
                extracted_value = None
            self.output_values[output] = extracted_value

    def __repr__(self):
        """
        What happens when you print the object instance.
        :return: path to output (.out or .smout) file
        """
        str_to_print = "\nCohort Instance Attributes\n"
        str_to_print += f"Filepath: {self.filepath}\n"
        str_to_print += f"Label: {self.label}\n"
        str_to_print += f"Model Type (cohort data.version): {self.cohort_data.version}\n"
        str_to_print += f"Label: {self.label}\n"
        str_to_print += f"Pop Size (None if no weighting): {self.popsize}\n"
        str_to_print += f"Mth of Entry (0 if no weighting): {self.month_of_entry}\n"
        str_to_print += f"Interactions (None if no interactions): {self.interactions}\n"
        str_to_print += (f"Note there are also other attributes: self.text, self.output_values; "
                         f"and the rest of self.cohort_data\n")
        return str_to_print


class Output(object):
    """
    Class for defining outcomes of interest to pull from output files

    Outcomes are found in the output file by
        Monthly/Overall
        Section Header/Month Header
        Identifier (text to search for within Section) (If identifier is empty will default to Section Header)
        Row Offset (from identifier)
        Column (as a letter)

    output type can be
        Total Mortality inclusive (total costs total deaths etc)
        Average Mortality inclusive (avg costs, avg life months etc)
        Monthly Mortality exclusive (monthly mean cd4)
    """

    def __init__(self, label, header, identifier, row_offset, col_letter, output_type):
        """
        :param label: a string label for the output in the MCT output table
        :param header: the section header in the .out or .smout file
        :param identifier: the unique text identifier for locating this output
        :param row_offset: the number of rows the output is below the identifier
        :param col_letter: the Column letter of the output
        :param output_type: the output type (total mort exclusive, average mort inclusive, monthly mort exclusive)
        """
        self.label = label
        self.header = header
        self.identifier = identifier
        self.row_offset = row_offset
        # convert column to number
        self.col_letter = col_letter
        self.col_num = get_col(col_letter)
        self.output_type = output_type

    def extract_output(self, text, header=None, interactions=[], max_offset=495):
        """
        extract_output pulls the value from the text of the output file
        It takes a string (the text containing the value) as input and not a filepath

        #  TODO i thought text was a Text() object, not a string?

        :param: text is the output file text being searched
        :param: header is the section header, defaults to None
        :param: interactions is the list of interactions, defaulting to an empty list
        :return: the extracted value if found

        Overloaded in the MonthlyOutput class to adjust params, then the  InteractionOutput, and MonthlyInteractionOutput class overloads call the other two, respectively
        """

        if header is None:
            header = self.header
        try:
            # first, get the section corresponding to the header; if not in text.sections yet, find the header line and
            # save it to text.sections

            if header in text.sections.keys():
                value = text.sections[header]  # the "chunk" (list) of lines under and including the given header
            else:
                wholeText = text.whole
                for line in wholeText:  # searches whole text line by line to find the header line; breaks once found
                    if header in line:
                        value = wholeText[wholeText.index(line):wholeText.index(line) + max_offset]
                        text.sections[header] = value
                        break

            # NOTE: same text identifier should not be used in different sections within the same task
            # I do not think it's worth the efficiency cost of handling that in the code

            # second, get the line corresponding to the text identifier string; if not in text.sections yet, find the
            # line containing the identifier and save it to text.identifier
            if self.identifier in text.id_indices.keys():
                index = text.id_indices[self.identifier]
                value = value[index + self.row_offset]
            else:
                for line in value:  # searches "chunk" (list) line by line to find the identifier line; breaks once found
                    if self.identifier in line:
                        index = value.index(line)
                        text.id_indices[self.identifier] = index
                        value = value[index + self.row_offset]
                        break

            # now value is a line, no longer a "chunk" (list) of lines ; todo - maybe have a diff name for clarity?
            value = value.split("\t", self.col_num + 1)[self.col_num]  # extract value at specified column in the line
        except IndexError:
            # TODO continue to think about how to handle issue of large monthly sections
            text.sections.pop(header)
            # raise keyword sends the IndexError to MonthlyOutput.extract_output function so we can increase the MonthlyOutput.max_monthly_offset class variable and try again
            raise
        except:
            # error during extraction
            return None
        else:
            return value

    def __repr__(self):
        """
        :return: output label (the string printed to the MCT .extract_out file)
        """
        str_to_print = "\nOutput Instance Attributes\n"
        str_to_print += f"Label: {self.label}\n"
        str_to_print += f"Output Type: {self.output_type}\n"
        str_to_print += f"Section Header (None if monthly): {self.header}\n"
        str_to_print += f"Identifier: {self.identifier}\n"
        str_to_print += f"Row Offset: {self.row_offset}\n"
        str_to_print += f"Col Letter: {self.col_letter}\n"
        str_to_print += f"Col Number (not passed at init): {self.col_num}\n"
        return str_to_print


class MonthlyOutput(Output):
    """
    Class for representing Monthly outputs

    Monthly outputs have a month associated with them as well as an output type
    """
    max_monthly_offset = DEFAULT_OFFSET

    def __init__(self, label, month_num, identifier,
                 row_offset, col_letter, output_type,
                 apply_disc=False, time_step=MONTH):
        # month in overall multi cohort time.  This is not the month of extraction for time shifted cohorts
        self.month_num = month_num
        # whether or not discounting applies to this output
        self.apply_disc = apply_disc
        # section header is dynamically created before extraction to account for time shifted cohorts
        section_header = None
        super(MonthlyOutput, self).__init__(label, section_header, identifier,
                                            row_offset, col_letter, output_type)
        self.time_step = time_step

    def get_num_alive(self, text, cohort_data, months_shifted=0):
        """
        gets the number of people alive in that month - it must be able to extract that value regardless of whether the user has selected it
        :return: int for the extracted number alive or None if invalid month
        """
        month_of_extraction = self.month_num - months_shifted

        if month_of_extraction < 0:
            return None
        output = cohort_data.i_outputs["Num Alive Time"].create_output("Num Alive Time", month_of_extraction)
        num_alive = output.extract_output(text)
        if num_alive is not None:
            return int(num_alive)
        else:
            return num_alive

    def extract_output(self, text, months_shifted=0, interactions=[]):
        """
        Extraction for monthly outputs
        See versions in the Output, InteractionOutput, and MonthlyInteractionOutput classes

        :param: text is the output file text being searched
        :param: months_shifted int used for time varying weighting, defaults to 0
        :param: interactions is the list of interactions, defaulting to an empty list
        :return: the extracted value if found

        The MonthlyInteractionOutput overload calls this function to apply the interactions after getting them
        """
        month_of_extraction = self.month_num - months_shifted

        if month_of_extraction < 0:
            return None
        time_str = \
            ("COHORT SUMMARY FOR MONTH", "Cohort Summary for Month", "COHORT SUMMARY FOR WEEK",
             "COHORT SUMMARY FOR YEAR")[
                self.time_step]
        section_header = f"{time_str} {month_of_extraction}"

        try:
            extracted_value = super(MonthlyOutput, self).extract_output(text, section_header,
                                                                        max_offset=self.max_monthly_offset)
        except IndexError:
            MonthlyOutput.max_monthly_offset += 25
            extracted_value = super(MonthlyOutput, self).extract_output(text, section_header,
                                                                        max_offset=self.max_monthly_offset)

        return extracted_value

    def __repr__(self):
        """
        :return: output label (the string printed to the MCT .extract_out file)
        """
        str_to_print = "\nMonthly Output Instance Attributes\n"
        str_to_print += f"Label: {self.label}\n"
        str_to_print += f"Output Type: {self.output_type}\n"
        str_to_print += f"Section Header (None if monthly): {self.header}\n"
        str_to_print += f"Identifier: {self.identifier}\n"
        str_to_print += f"Row Offset: {self.row_offset}\n"
        str_to_print += f"Col Letter: {self.col_letter}\n"
        str_to_print += f"Col Number (not passed at init): {self.col_num}\n"

        str_to_print += f"Month number: {self.month_num}\n"
        str_to_print += f"Time step: {self.time_step}\n"
        str_to_print += f"Apply disc? {self.apply_disc}\n"

        return str_to_print


class MultiCohort(object):
    def __init__(self, cohorts, outputs, cohort_data, disc_rate=0):
        """
        Class for specifing multiple cohorts
        :param cohorts: a list of Cohort objects, to be unpacked into a tuple at init
        :param outputs: a list of Output objects, to be unpacked into a tuple at init
        :param cohort_data: CohortData unpickled from the .out_data file
        :param float disc_rate: value entered in PopulationPanel.disc_rate_tc for applying discounting in time varying weighting tasks, casted to float and defaulting to 0
        """
        # cohorts is a tuple of Cohort objects
        self.cohorts = (*cohorts,)
        # outputs is a tuple of Output objects
        self.outputs = (*outputs,)
        self.runsizes = {}
        # num_alive_mth is a dictionary of (cohort, MonthlyOutput) to num alive
        self.num_alive_mth = {}
        # dictionary of combined output values from each cohort
        self.combined_outputs = {}
        # Data about cohort outputs for a particular version of CEPAC
        self.cohort_data = cohort_data
        # yearly discount rate to apply to undiscounted outputs.  If the run is already discounted 0 should be used
        self.disc_rate = disc_rate

    def write_overall_outputs_to_df(self, save_as_csv=None, version=CEPAC):

        # exclude any monthly outputs
        overall_outputs = [output for output in self.outputs if not isinstance(output, MonthlyOutput)]
        output_labels = [output.label for output in overall_outputs]

        # create dict of {cohort/runfile label -> output value}, prepping for making it into a df
        data = {}
        for cohort in self.cohorts:
            data[cohort.label] = [cohort.output_values[output] for output in overall_outputs]

        # df where the cohort/runs are each one row, and the outputs are each one column
        df = pd.DataFrame(data, index=output_labels).T

        # Add Run Size as a new column
        df["Run Size"] = [self.runsizes.get(cohort, None) for cohort in self.cohorts]

        df = df.reset_index().rename(columns={"index": "run_name"})

        if save_as_csv is not None:
            df.to_csv(save_as_csv, index=False)
        return df

    def write_monthly_outputs_to_dict(self, version=CEPAC):
        self.extract_outputs(version)

        monthly_outputs = [output for output in self.outputs if isinstance(output, MonthlyOutput)]

        from collections import defaultdict

        result = {}  # will be a nested dict; {output label -> {month -> output value}}

        for output in monthly_outputs:
            for cohort in self.cohorts:
                run_name = cohort.label
                label = output.label
                month = output.month_num
                value = cohort.output_values[output]

                if label not in result:
                    result[label] = {}

                if month not in result[label]:
                    result[label][month] = {}

                result[label][month][run_name] = value

        return result

    def write_extracted_outputs(self, output_filepath, orientation, version=CEPAC):
        """
        extracts outputs and writes them
        does not weight or combine outputs
        Calls MultiCohort.extract_outputs
        :param: output_filepath the path to the MCT output (.extract_out) file name, which is contained in the parent folder of all output files from the ExtractPanel.on_extract_only DirDialog path

        """
        # read all files
        self.extract_outputs(version=version)

        # write output file
        with open(output_filepath, 'w') as fout:
            # header
            print("Writing results")
            if orientation == COLUMN:
                for cohort in self.cohorts:
                    fout.write("\t{0}".format(cohort.label))
                fout.write("\nRun Size")
                for cohort in self.cohorts:
                    fout.write("\t{0}".format(self.runsizes[cohort]))
                for output in self.outputs:
                    fout.write("\n{0}".format(output.label))
                    for cohort in self.cohorts:
                        fout.write("\t{0}".format(cohort.output_values[output]))
            else:
                fout.write("\tRun Size")
                for output in self.outputs:
                    fout.write("\t{0}".format(output.label))

                # data rows
                for cohort in self.cohorts:
                    fout.write("\n{0}".format(cohort.label))
                    fout.write("\t{0}".format(self.runsizes[cohort]))
                    for output in self.outputs:
                        fout.write("\t{0}".format(cohort.output_values[output]))

            if MonthlyOutput.max_monthly_offset > DEFAULT_OFFSET:
                fout.write(
                    f"\n\nPLEASE NOTE: Section size was increased to {MonthlyOutput.max_monthly_offset} for some monthly outputs during extraction.\nPlease report this value and your task details to the Programming Team.")

    def write_combined_outputs(self, output_filepath, orientation, batchfile=None, version=CEPAC):
        """
        extract outputs, calculate weighted outputs, and print out in file
        batchfile is an opened file object for appending batch outputs
        """
        # read all files
        self.extract_outputs(version)

        # weight each output
        print("Weighting outputs")
        for output in self.outputs:
            combined_output = self.aggregate_output(output)
            # apply discounting if applicable
            if (type(output).__name__ in {"MonthlyOutput",
                                          "MonthlyInteractionOutput"}) and output.apply_disc and combined_output is not None:
                combined_output *= 1 / (1 + self.disc_rate) ** (output.month_num / 12.0)
            self.combined_outputs[output] = combined_output
        # write output file
        with open(output_filepath, 'w') as fout:
            print("Writing results")
            if orientation == COLUMN and not batchfile:
                # header
                fout.write("\tCombined (discounted if enabled)")
                for cohort in self.cohorts:
                    fout.write("\t{0}".format(cohort.label))
                fout.write("\nRun Size\t")
                for cohort in self.cohorts:
                    fout.write("\t{0}".format(self.runsizes[cohort]))
                fout.write("\nIntended Pop Size\t")
                for cohort in self.cohorts:
                    fout.write("\t{0}".format(cohort.popsize))
                # weighted outputs
                for output in self.outputs:
                    fout.write("\n{0}".format(output.label))
                    fout.write("\t{0}".format(self.combined_outputs[output]))
                    for cohort in self.cohorts:
                        fout.write("\t{0}".format(cohort.output_values[output]))

            else:
                # header
                fout.write("\tRun Size\tIntended Pop Size")
                for output in self.outputs:
                    fout.write("\t{0}".format(output.label))

                # weighted row
                fout.write("\nCombined (discounted if enabled)")
                fout.write("\t\t")
                for output in self.outputs:
                    fout.write("\t{0}".format(self.combined_outputs[output]))

                # write to batch file
                if batchfile:
                    batchfile.write("\n{0}".format(output_filepath))
                    for output in self.outputs:
                        batchfile.write("\t{0}".format(self.combined_outputs[output]))
                    for cohort in self.cohorts:
                        batchfile.write("\t{0}".format(cohort.popsize))

                # data rows
                for cohort in self.cohorts:
                    fout.write("\n{0}".format(cohort.label))
                    fout.write("\t{0}\t{1}".format(self.runsizes[cohort], cohort.popsize))
                    for output in self.outputs:
                        fout.write("\t{0}".format(cohort.output_values[output]))

            if MonthlyOutput.max_monthly_offset > DEFAULT_OFFSET:
                fout.write(
                    f"\n\nPLEASE NOTE: Section size was increased to {MonthlyOutput.max_monthly_offset} for some monthly outputs during extraction.\nPlease report this value and your task details to the Programming Team.")

    def extract_outputs(self, version=CEPAC):
        """
        read and extract outputs as well as runsize from all cohorts
        Loops through the cohorts and calls Cohort.extract_output_values and Cohort.get_runsize on each of them.
        Loops through the output list and calls get_num_alive from either the MonthlyOutput or MonthlyInteractionOutput class on any monthly outputs that are specified
        """
        n = len(self.cohorts)
        text = None
        previous = None
        for i, cohort in enumerate(self.cohorts):
            print(f"{i + 1}/{n} Reading: {cohort.filepath}")
            # store most recent read file
            if cohort.filepath != previous:
                with open(cohort.filepath) as f_cohort:
                    text = Text(list(f_cohort))  # text is a list where each element is a line from the file
                previous = cohort.filepath
            cohort.text = text
            self.runsizes[cohort] = cohort.get_runsize(cohort.text, version)

            cohort.extract_output_values(cohort.text, self.outputs)
            for output in self.outputs:
                # use type to get around pickling errors and type
                if type(output).__name__ in {"MonthlyOutput", "MonthlyInteractionOutput"}:
                    self.num_alive_mth[(cohort, output)] = output.get_num_alive(text, self.cohort_data,
                                                                                cohort.month_of_entry)

    def aggregate_output(self, output):
        """
        combines the values of this outcome found in different cohorts into
        a single aggregate value
        """
        valid_cohorts = [cohort for cohort in self.cohorts if cohort.output_values[output] is not None]
        if not valid_cohorts:
            return None
        if output.output_type == TOTAL_MORT_INCL:
            # total mortality inclusive outcome
            try:
                value = sum([cohort.popsize / float(self.runsizes[cohort]) * cohort.output_values[output]
                             for cohort in valid_cohorts])
            except:
                value = None
            return value
        if output.output_type == AVG_MORT_INCL:
            # Averaged mortality inclusive outcomes
            try:
                popsum = sum([cohort.popsize for cohort in valid_cohorts])
                value = sum([cohort.popsize / float(popsum) * cohort.output_values[output]
                             for cohort in valid_cohorts])
            except:
                value = None
            return value
        if output.output_type == AVG_MORT_EXCL:
            # Monthly averaged mortality exclusive outcomes
            try:
                intended_alive = [self.num_alive_mth[(cohort, output)] / float(self.runsizes[cohort]) * cohort.popsize
                                  for cohort in valid_cohorts]
                weights = [p / float(sum(intended_alive)) for p in intended_alive]
                value = sum([weights[i] * cohort.output_values[output]
                             for i, cohort in enumerate(valid_cohorts)])
            except:
                value = None
            return value
        if output.output_type == MORT_INCL_STD_DEV:
            # overall mortality inclusive standard deviation
            try:
                popsum = sum([cohort.popsize for cohort in valid_cohorts])

                weights = [cohort.popsize / float(popsum) for cohort in valid_cohorts]

                value = sum([(weights[i] * cohort.output_values[output]) ** 2
                             for i, cohort in enumerate(valid_cohorts)])

                value = sqrt(value)
            except:
                value = None
            return value
        if output.output_type == MORT_EXCL_STD_DEV:
            # monthly mortality exclusive std dev
            try:
                intended_alive = [self.num_alive_mth[(cohort, output)] / float(self.runsizes[cohort]) * cohort.popsize
                                  for cohort in valid_cohorts]
                weights = [p / float(sum(intended_alive)) for p in intended_alive]
                value = sum([(weights[i] * cohort.output_values[output]) ** 2
                             for i, cohort in enumerate(valid_cohorts)])
                value = sqrt(value)
            except:
                value = None
            return value

    def __getitem__(self, key):
        return self.cohorts[key]



# ---------------- Functions moved from original MCT script (m_cohorts.py) ------------------------------------------#

def get_col(col_letter):
    """
    converts column letter to number A =0, AA = 26 etc
    Function doesn't check whether input is valid
    """
    col_num = 0
    for letter in col_letter:
        col_num = col_num*26 + (ord(letter.lower()) - 96)
    col_num -= 1
    return col_num


def parse_month(text, as_string=False):
    """
    parses month nums and gives a list of months
    input can be a comma separated list with dash to represent a range
    :param text: the text from the input box
    :param as_string: a bool indicating whether to return the list as strings (to autofill more GUI boxes) or integers (for extraction)
    :return: a list of month numbers
    :rtype: list
    """
    regions = text.split(",")
    months = []
    for region in regions:
        if "-" in region:
            l_bound, u_bound = region.split("-")
            l_bound = int(l_bound)
            u_bound = int(u_bound)
            months.extend(range(l_bound, u_bound+1))
        else:
            months.append(int(region))
    if as_string:
        return list(map(str, months))
    return months


def import_data_file(filepath):
    """
    imports data (.out_data) file
    :param str filepath: the path to the .out_data file
    :return: unpickled data file
    :rtype: CohortData
    """

    with open(filepath, "rb") as fdata:
        print(filepath)
        cohort_data = pickle.load(fdata)
        return cohort_data


def clean_output(text):
    """
    Tries to convert to float and if not possible tries to remove chars that are not numbers
    :param str text: the text version of the value in the output file or user entry
    :return: a float version of the cleaned text
    :rtype: float
    """
    try:
        return float(text)
    except ValueError:
        new_text = ""
        for letter in text:
            if letter in (".","0","1","2","3","4","5","6","7","8","9"):
                new_text+=letter
        return float(new_text)


# ---------------- New functions created for  extraction library purposes ------------------------------------------#


def clean_outputs_df(df):

    # Remove any leading or trailing whitespace
    columns = ["Output", "Label", "Section", "TextID", "ColLetter", "Months"]
    for col in columns:
        df[col] = df[col].str.strip()

    # Keep only rows where output type is Overall or Monthly (mostly to get rid of blank rows)
    df = df[df['Output'].isin(["Overall", "Monthly"])].copy()

    # Map string values to integers
    df['Output'] = df['Output'].map({"Overall": OVERALL, "Monthly": MONTHLY})

    return df
