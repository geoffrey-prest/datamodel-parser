# datamodel-parser
A tool to visualize a database whose data model lacks any constraints (i.e.: primary or foreign keys). This tool is born from the need to trace data in a database that is generated and managed by a low-code platform. This tool functions on a given folder that contains SQL scripts that have been generated bu Microsoft SSMS.

The general operation of this tool is as follows:
- get an understanding of the entities and relationships that are defined in the SQL scripts
- present that information in a manner that is useful (still to be determined).

At present, the goal of this tool is to analyze all SQL scripts in a given directory (provided as a command-line argument) and to produce a JSON file (named `_file-analysis.json` in the given directory) that adheres to the [`DataModelSchema`](src/DataModelSchema.json); for example:

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
                        "ReferencingEntity": {
                            "Module": "referencing_module_name",
                            "Entity": "referencing_entity_name",
                            "Field": "referencing_field_name"
                        },
                        "ReferencedEntity": {
                            "Module": "referenced_module_name",
                            "Entity": "referenced_entity_name",
                            "Field": "referenced_field_name"
                        },
                        "Qualification": "qualification"
                    }
                ]
            }
        ]
    }
}
```
# Value determination

Subsequent sections will specify how each value from the example above is determined while analyzing each file in the given directory.

## Database definition
- the current file's name ends with `.Database.sql`.
- `database_file_name` is the current file's name.
- `database_name` is the first portion of the file name up to and excluding the first dot (`.`) character.

## Table definitions
- the current file's name ends with `.Table.sql`.
- `table_file_name` is the current file's name.
- `schema_name` is the first portion of `table_file_name` up to and excluding the first dot (`.`) character.
- `module_name` is the portion of `table_file_name` after the first dot (`.`) character up to and excluding the dollar sign (`$`) character.
- `table_type`:
    - `simpleTable`
        - `table_file_name` contains no underscore (`_`) characters after the dollar sign (`$`) character.
        - `entity_name` is the portion of `table_file_name` after the dollar sign (`$`) character up to and excluding `.Table.sql`.
        - `referencing_module_name`, `referencing_entity_name`, and `referencing_field_name` are never present.
        - `referenced_module_name`, `referenced_entity_name`, and `referenced_field_name` are never present.
    - `joinTable`
        - `table_file_name` contains a single underscore (`_`) after the dollar sign (`$`) character.
        - `referencing_entity_name` is the portion of `table_file_name` after the dollar sign (`$`) character up to and excluding the underscore (`_`) character.
        - `referenced_entity_name` is the portion of `table_file_name` after that underscore (`_`) character up to and excluding `.Table.sql`.
        - `referencing_module_name` and `referencing_field_name` are determined by [Parsing the content of the file](parsing-the-content-of-the-file).
        - `referenced_module_name` and `referenced_field_name` are determined by [Parsing the content of the file](parsing-the-content-of-the-file).
    - `qualifiedJoinTable`
        - `table_file_name` contains two underscore (`_`) characters after the dollar sign (`$`) character.
        - `referencing_entity_name` is the portion of `table_file_name` after the dollar sign (`$`) character up to and excluding the first underscore (`_`) character.
        - `referenced_entity_name` is the portion of `table_file_name` after that underscore (`_`) character up to and excluding the second underscore (`_`) character.
        - `referencing_module_name` and `referencing_field_name` are determined by [Parsing the content of the file](parsing-the-content-of-the-file).
        - `referenced_module_name` and `referenced_field_name` are determined by [Parsing the content of the file](parsing-the-content-of-the-file).
        -`qualification` is the portion of `table_file_name` after that second underscore (`_`) character up to and excluding `.Table.sql`.

## Parsing the content of the file
The following operation is performed for all `joinTable` and `qualifiedJoinTable` tables, and is the same for both referencing and referenced entities.

The general structure of a join table's SQL file is as follows:

```sql
USE [ABC]

/``` Object:  Table [dbo].[modulefour$entitysix_entityfive]    Script Date: 12/12/2016 12:00:00 ```/
SET ANSI_NULLS ON

CREATE TABLE [dbo].[modulefour$entitysix_entityfive] ( 
    [modulefour$entitysixid] [bigint] NOT NULL,
    [modulethree$entityfiveid] [bigint] NOT NULL
) 
```

The referencing and referenced table identifiers are the target of this operation and can be loosely defined as the first string, contained within square brackets, on each line following the line that contains `CREATE TABLE`. Continuing with the example script above, we would have the following if we were to strip out all lines from the script that did not interest us.

```sql
    [modulefour$entitysixid] [bigint] NOT NULL,
    [modulethree$entityfiveid] [bigint] NOT NULL
```

Using the `referencing_entity_name` and `referenced_entity_name` values determined previously, we can identify the module and field names.

For example, based on the above lines, if `referencing_entity_name` is equal to `entityfive`, then `referencing_module_name` is `modulefour` and `referencing_field_name` is `id`.

## Example DDL
The `doc/example/DDL` folder contains example files that represent a generalized structure of the files that would be produced by SSMS if all DDL scripts were to be generated. These files are not complete nor functional; they mearly provide what the tool will require to work. The structure of the example database is as follows:

![Example ERD](doc/example/example-erd.drawio.svg)

Also present in this folder is the output of the tool based on the example DDL (see: [doc/example/DDL/_file-analysis.json](doc/example/DDL/_file-analysis.json)).
