# datamodel-parser
A tool to visualize a database whose data model lacks any constraints (i.e.: primary or foreign keys). This tool is born from the need to trace data in a database that is generated and managed by a low-code platform. This tool functions on a given folder that contains SQL scripts that have been generated bu Microsoft SSMS.

## Database definition
- file name ends with `.Database.sql`
- the first portion of the file name, up to and excluding the first dot (`.`) character, is the name of the database.

## Table definitions
types:
    - simpleTable
    - joinTable
    - qualifiedJoinTable

# All types:
- file name ends with `.Table.sql`
- the first portion of the file name, up to and excluding the first dot (`.`) character, is the name of the schema.
- the portion of the file name, preceding the dollar sign (`$`) character and following the dot (`.`) character, is the module name.

# simpleTable type:
- the portion of the file name following the dollar sign (`$`) character is the entity name.

# joinTable type:
- the file name contains a single underscore following the dollar sign (`$`) character.
- the portion of the file name between the dollar sign (`$`) and underscore (`_`) characters is the referencing entity.
- the portion of the file name following the underscore (`_`) character is the referenced entity.

# qualifiedJoinType:
- the file name contains a two underscore (`_`) characters following the dollar sign (`$`) character.
- the portion of the file name between the dollar sign (`$`) and underscore (`_`) characters is the referencing entity.
- the portion of the file name between the two underscore (`_`) characters is the referenced entity.
- the portion of the file name after the last underscore (`_`) character is the qualification.

## Output
This tool will output the result of its analysis to a JSON file, named `_file-analysis.json` in the given directory

## JSON structure
The structure of the output file will be as follows:

```json
{
    "Database": {
        "Filename": "database_file_name",
        "Name": "database_name",
        "Schemas": [
            {
                "Name": "schema_name",
                "Tables": [
                    {
                        "Filename": "table_file_name",
                        "Type": "table_type",
                        "Name": "table_name",
                        "Module": "module_name",
                        "Entity": "entity_name",
                        "ReferencingEntity": "referencing_entity",
                        "ReferencedEntity": "referenced_entity",
                        "Qualification": "qualification"
                    }
                ]
            }
        ]
    }
}
```

## Example DDL
The `doc/example/DDL` folder contains example files that represent a generalized structure of the files that would be produced by SSMS if all DDL scripts were to be generated. These files are not complete nor functional; they mearly provide what the tool will require to work.

