# ddl_analysis.py

import file_ops
import logging
import re
import os

def capture_information(directory: str, encoding: str):
    """
    Captures data model information from SQL files in the specified directory.
    This function scans the given directory for SQL files that define database
    schemas and tables. It extracts relevant information from these files and
    organizes it into a structured data model (defined in DataModelSchema.json).
    Args:
        directory (str): The path to the directory containing the SQL files.
        encoding (str): The encoding used to read the SQL files.
    Returns:
        dict: A dictionary representing the captured data model information.
    """

    logging.info(f"Capturing data model information from: {directory}")
    
    data_model = {
        "Database": {
            "Name": "",
            "DDL": "",
            "Schemas": []
        }
    }

    data_model = determine_database_name(data_model, directory)
    data_model = determine_tables(data_model, directory)
    data_model = determine_joins(data_model, directory, encoding)

    logging.info(f"Data model information captured")
    return data_model

def determine_database_name(data_model: dict, directory: str):
    
    with os.scandir(directory) as files:
        for file in files:
            if file.is_file():
                file_name = file.name

                if file_name.endswith('.Database.sql'):
                    data_model["Database"]["DDL"] = file_name
                    data_model["Database"]["Name"] = file_name.split('.')[0]
    
    return data_model

def determine_tables(data_model: dict, directory: str):
    
    with os.scandir(directory) as files:
        for file in files:
            if file.is_file():
                file_name = file.name
                
                if file_name.endswith('.Table.sql') and '_' not in file_name:

                    file_name_parts = file_name.split('.')
                    if len(file_name_parts) < 3:
                        logging.info(f"Skipping file with unexpected name format: {file_name}")
                        continue

                    schema_name, table_name, *_ = file_name_parts
                    module_name, entity_name = table_name.split('$')

                    table_info = {
                        "Name": table_name,
                        "Type": "simpleTable",
                        "Module": module_name,
                        "Entity": entity_name,
                        "DDL": file_name,
                        "References": {
                            "Incoming": [],
                            "Outgoing": [],
                        }
                    }

                    add_table_to_schema(data_model, table_info, schema_name)
    
    return data_model

def determine_joins(data_model: dict, directory: str, encoding: str):
    
    with os.scandir(directory) as files:
        for file in files:
            if file.is_file():
                file_name = file.name
                file_path = file.path
                
                if file_name.endswith('.Table.sql') and '_' in file_name:

                    file_name_parts = file_name.split('.')
                    if len(file_name_parts) < 3:
                        logging.info(f"Skipping file with unexpected name format: {file_name}")
                        continue

                    schema_name, table_name, *_ = file_name_parts
                    module_name, entity_name = table_name.split('$')

                    table_info = {
                        "Name": table_name,
                        "Type": "",
                        "Module": module_name,
                        "Entity": entity_name,
                        "DDL": file_name,
                        "ReferencingTable": "",
                        "ReferencedTable": "",
                        "Qualification": ""
                    }

                    if '_' in table_name:
                        table_name_parts = table_name.split('_')
                        
                        table_info["Type"] = "joinTable" if len(table_name_parts) == 2 else "qualifiedJoinTable"
                        
                        if table_info["Type"] == "qualifiedJoinTable":
                            table_info["Qualification"] = table_name_parts[2]
                        else:
                            table_info.pop("Qualification")
                            
                        file_content = file_ops.get_file_content(file_path, encoding)
                        data_model, table_info = update_references(file_content, data_model, table_info)
                        add_table_to_schema(data_model, table_info, schema_name)

    return data_model

def add_table_to_schema(data_model: dict, table_info: dict, schema_name: str):
    schema_exists = next((schema for schema in data_model["Database"]["Schemas"] if schema["Name"] == schema_name), None)
    if schema_exists:
        schema_exists["Tables"].append(table_info)
    else:
        data_model["Database"]["Schemas"].append({
            "Name": schema_name,
            "Tables": [table_info]
        })

def update_references(file_content: list, data_model: dict, table_info: dict):
    if file_content:
        
        column_names = [] 
        for line in file_content:
            match = re.match(r"\s*\[(\w+\$\w+)\]\s+\[\w+\].*", line)
            if match: 
                column_names.append(match.group(1))

        referencing_column = column_names[0]
        referenced_column = column_names[1]

        referencing_table = get_table_info(data_model, referencing_column)
        referenced_table = get_table_info(data_model, referenced_column)

        referencing_table_name = referencing_table["Name"]
        referenced_table_name = referenced_table["Name"]
        
        if "Qualification" in table_info:
            referencing_table_name += (" (" + table_info["Qualification"] + ")")
            referenced_table_name += (" (" + table_info["Qualification"] + ")")

        if referenced_table_name not in referencing_table["References"]["Outgoing"]:
            referencing_table["References"]["Outgoing"].append(referenced_table_name)
        
        if referencing_table_name not in referenced_table["References"]["Incoming"]:
            referenced_table["References"]["Incoming"].append(referencing_table_name)

        table_info["ReferencingTable"] = referencing_table["Name"]
        table_info["ReferencedTable"] = referenced_table["Name"]
    
    return data_model, table_info

def get_table_info(data_model: dict, column: str):
    table_info = None

    for schema in data_model["Database"]["Schemas"]: 
        for table in schema["Tables"]: 
            if column.startswith(table["Name"]):
                table_info = table

    return table_info

def store_intermediate_result(data_model: dict, directory: str, encoding: str):
    """
    Stores the intermediate result of the data model analysis in a JSON file.
    Args:
        data_model (dict): The data model to be stored in the JSON file.
        directory (str): The directory where the JSON file will be saved.
        encoding (str): The encoding to be used for the JSON file.
    Returns:
        str: The path to the output file where the intermediate result is stored.
    """
    output_file_path = os.path.join(directory, "_file-analysis.json")    
    data_model = sort_tables_by_name(data_model)
    data_model = sort_references(data_model)
    file_ops.write_json_to_file(data_model, output_file_path, encoding)
    
    return output_file_path

def sort_tables_by_name(data_model): 
    for schema in data_model["Database"]["Schemas"]: 
        schema["Tables"] = sorted(schema["Tables"], key=lambda table: table["Name"])
    return data_model

def sort_references(data_model): 
    for schema in data_model["Database"]["Schemas"]: 
        for table in schema["Tables"]: 
            if "References" in table: 
                if "Incoming" in table["References"]: 
                    table["References"]["Incoming"] = sorted(table["References"]["Incoming"])
                if "Outgoing" in table["References"]: 
                    table["References"]["Outgoing"] = sorted(table["References"]["Outgoing"])
    return data_model

def store_lineage(directory, table_name, data_model,encoding):
    raw_lineage = trace_lineage(table_name, data_model)
    lineage = '\n'.join(raw_lineage)
    lineage_file_path = os.path.join(directory, "_lineage_"+table_name+".txt")
    file_ops.write_text_to_file(lineage_file_path,encoding,lineage)
    return lineage_file_path

def trace_lineage(table_name, data_model, lineage=None, indent=0):
    if lineage is None:
        lineage = []

    # Add the current table to the lineage
    lineage.append(' ' * indent + '- ' + table_name)

    # Find the table in the dictionary
    for schema in data_model["Database"]["Schemas"]:
        for table in schema["Tables"]:
            if table["Name"] == table_name:
                if "References" in table and "Incoming" in table["References"]:
                    for incoming_table in table["References"]["Incoming"]:
                        # Recur for each incoming reference
                        trace_lineage(incoming_table, data_model, lineage, indent + 4)
                break

    return lineage