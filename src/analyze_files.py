import os
import json
import re
import argparse

def parse_file_content(filepath, entity_name):
    with open(filepath, 'r') as file:
        content = file.readlines()

    found_create = False
    for line in content:
        if 'CREATE TABLE' in line:
            found_create = True
        elif found_create and '[' in line and ']' in line:
            match = re.search(r'\[(.*)\]\s+\[.*\]\s+NOT NULL', line)
            if match:
                parts = match.group(1).split('$')
                if parts[1].startswith(entity_name):
                    return parts[0], parts[1].replace(entity_name, '')
    return None, None

def main(directory):
    data_model = {
        "Database": {
            "Filename": "",
            "Name": "",
            "Schemas": []
        }
    }

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if filename.endswith('.Database.sql'):
            data_model["Database"]["Filename"] = filename
            data_model["Database"]["Name"] = filename.split('.')[0]
        
        elif filename.endswith('.Table.sql'):
            schema_name = filename.split('.')[0]
            module_name = filename.split('.')[1].split('$')[0]
            table_name = filename.split('.')[1]
            entity_name = table_name.split('$')[1]

            table_info = {
                "Filename": filename,
                "Name": table_name,
                "Module": module_name,
                "Entity": entity_name,
                "ReferencingEntity": {},
                "ReferencedEntity": {},
                "Qualification": ""
            }

            if '_' in table_name:
                parts = table_name.split('$')[1].split('_')
                table_info["Type"] = "joinTable" if len(parts) == 2 else "qualifiedJoinTable"
                table_info["ReferencingEntity"]["Entity"] = parts[0]
                table_info["ReferencedEntity"]["Entity"] = parts[1]
                
                if len(parts) == 3:
                    table_info["Qualification"] = parts[2]
                
                ref_module, ref_field = parse_file_content(filepath, parts[0])
                if ref_module:
                    table_info["ReferencingEntity"]["Module"] = ref_module
                    table_info["ReferencingEntity"]["Field"] = ref_field
                
                ref_module, ref_field = parse_file_content(filepath, parts[1])
                if ref_module:
                    table_info["ReferencedEntity"]["Module"] = ref_module
                    table_info["ReferencedEntity"]["Field"] = ref_field

            else:
                table_info["Type"] = "simpleTable"

            schema_exists = next((schema for schema in data_model["Database"]["Schemas"] if schema["Name"] == schema_name), None)
            if schema_exists:
                schema_exists["Tables"].append(table_info)
            else:
                data_model["Database"]["Schemas"].append({
                    "Name": schema_name,
                    "Tables": [table_info]
                })

    output_file = os.path.join(directory, "_file-analysis.json")
    with open(output_file, 'w') as outfile:
        json.dump(data_model, outfile, indent=4)

    print(f"Data model analysis written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze SQL scripts and generate data model JSON.")
    parser.add_argument("directory", help="Directory containing the SQL scripts.")
    args = parser.parse_args()
    main(args.directory)
