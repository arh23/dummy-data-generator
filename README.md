# dummy-data-generator

Generate multiple rows of dummy/test data using template values.

## Documentation

This documentation will guide you through the different operators and functionality of the pattern system.

### Usage

#### Columns

*Dummy data generator* generates multiple rows of test/fake data in a csv file based on a defined template. These values (specifically grouped as *columns*) can be found in the *columns.json* file created after the script has been run for the first time. 

The columns can be modified through the script or via a text editor. You can use various placeholders to generate random or incremental data, for example, see the following column values:

- *example string* - this will generate as fixed text in each row.

- *test value +* - this will generate with an incremental count, represented by the plus sign, so the first row will be *test value 1* and row twenty will be *test value 20*.

- *test value (50,100)* - this will generate with a random number, where the range of this random number is set in the brackets, so a row may generate as *test value 63*. There are also some different behaviours with number ranges:
    - *(\*0.01,0.99)* - this will generate a random decimal with unlimited decimal places between 0.01 and 0.99 for each row.
    - *(£10,1000)* - this will generate a random number between 10 and 1000 with two decimal places, for example, 278.56.
    - *(3%20.5,30.5)* - this will generate a random number between 20.5 and 30.5 with 3 decimal places. The number of decimal places needs to be before the percentage sign.
    - *(-4,2)* - this will generate a number between -4 and 2 with no decimals.

Columns can also be added and deleted via the script.

#### Settings

A settings file (*settings.json*) is also created when the script has been run for the first time. Currently, the following can be changed via the settings:

- Default name of files generated - set to "data.csv" by default. If left blank, there will be a prompt to enter a file name before a file is generated.

- Name of folder where generated files are located - set to "generated-data" by default. If left blank, the files will generate in the same location as the script.

- Index value where the script starts counting from when creating rows - set to 0 by default. The value is not inclusive, counts will start at value + 1.

- Name of the JSON file being used to load the columns - set to "columns.json" by default. If the file does not exist, it will be created with default columns.

You can modify the settings from within the script, or directly via the JSON file.

Both JSON files are generated in the same directory as the script. 

### Requirements

- Python (written and tested with Python 3.5.4)
