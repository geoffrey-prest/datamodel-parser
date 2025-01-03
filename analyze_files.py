import os
import sys
import argparse
import json
from collections import defaultdict

def analyze_files(folder):
    print(f"Analyzing SQL files in {folder}")
    analysis_result = defaultdict(lambda: {"Filename": "", "Name": "", "Schemas": defaultdict(lambda: {"Name": "", "Tables": []})})

    for filename in os.listdir(folder):
        if filename.endswith('.Database.sql'):
            db_name = filename.split('.')[0]
            analysis_result[db_name]["Filename"] = filename
            analysis_result[db_name]["Name"] = db_name
        elif filename.endswith('.Table.sql'):
            filename_without_suffix = filename.replace('.Table.sql', '')
            filename_split_on_dot = filename_without_suffix.split('.')
            filename_split_on_dollar = filename_without_suffix.split('$')
            schema_name = filename_split_on_dot[0]
            table_name = filename_split_on_dot[1]
            module_name = filename_split_on_dollar[0].split('.')[1]
            if '$' in filename:
                parts = filename_split_on_dollar[1].split('_')
                if len(parts) == 1:
                    table_type = "simpleTable"
                    entity_name = parts[0]
                elif len(parts) == 2:
                    table_type = "joinTable"
                    referencing_entity = parts[0]
                    referenced_entity = parts[1]
                elif len(parts) == 3:
                    table_type = "qualifiedJoinTable"
                    referencing_entity = parts[0]
                    referenced_entity = parts[1]
                    qualification = parts[2]

                table_info = {
                    "Filename": filename,
                    "Type": table_type,                                   
                    "Name": table_name,
                    "Module": module_name,
                    "Entity": entity_name if len(parts) == 1 else None,
                    "ReferencingEntity": referencing_entity if table_type != "simpleTable" else None,
                    "ReferencedEntity": referenced_entity if table_type != "simpleTable" else None,
                    "Qualification": qualification if table_type == "qualifiedJoinTable" else None,
                }
                analysis_result[db_name]["Schemas"][schema_name]["Name"] = schema_name
                analysis_result[db_name]["Schemas"][schema_name]["Tables"].append(table_info)

    # Convert defaultdict to regular dict for JSON serialization
    analysis_result = {db: {"Filename": info["Filename"], "Name": info["Name"], "Schemas": list(schemas.values())} for db, info in analysis_result.items() for schemas in [info["Schemas"]]}

    output_file = os.path.join(folder, '_file-analysis.json')
    with open(output_file, 'w') as f:
        json.dump(analysis_result, f, indent=4)

    print(f"Analysis result saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze SQL file names in a folder.')
    parser.add_argument('folder', type=str, help='The folder containing the SQL files')
    args = parser.parse_args()
    
    if not os.path.isdir(args.folder):
        print(f"Error: {args.folder} is not a valid directory")
        sys.exit(1)
    
    analyze_files(args.folder)
