# datamodel_parser.py

import ddl_analysis
import file_ops
import logging

def main(directory: str, encoding: str, table_name: str):

    if file_ops.is_valid_directory(directory):

        data_model = ddl_analysis.capture_information(directory, encoding)
        output_file_path = ddl_analysis.store_intermediate_result(data_model, directory, encoding)
        logging.info(f"Intermediate result stored in {output_file_path}")
        lineage_file_path = ddl_analysis.store_lineage(directory, table_name, data_model, encoding)
        logging.info(f"Lineage stored in {lineage_file_path}")

        # TODO: Implement the remaining steps of the analysis process
        # - generate a data model JSON file with the complete lineage information
        # - store the final data model JSON file in the same directory as the intermediate result
        # - log the path to the final data model JSON file
        # - produce a summary of the analysis results, illustrating the lineage of each entity
        # - log the summary of the analysis results
        # - extend the argument parser to include the option to provide a single entity for the analysis process (i.e.: would produce a summary of the lineage of that entity only)
        # - create unit tests for the functions in this script



