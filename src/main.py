# main.py

import datamodel_parser
import argparse
import logging

# Configure the logging module to display the time, log level, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# This block ensures that the script runs only if it is executed directly, not when imported as a module.
if __name__ == "__main__":
    
    # Create an argument parser to handle command-line arguments
    parser = argparse.ArgumentParser(description="This script analyzes SQL scripts and generates a data model JSON file.")
    parser.add_argument("directory", help="The path to the directory containing the SQL scripts to be analyzed. (e.g., 'C:\\path\\to\\directory' or '/path/to/directory')")
    parser.add_argument("encoding", help="The character encoding used in the SQL script files. (e.g., 'utf-8')")
    parser.add_argument("table", help="The name of the table for lineage output. (e.g., 'modulethree$entityfive')")
    args = parser.parse_args()

    # Call the main function with the provided directory and encoding
    datamodel_parser.main(args.directory, args.encoding, args.table)