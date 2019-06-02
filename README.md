# dummy-data-generator

Generate multiple rows of dummy/test data using template values. Can also be used to generate test images.

## Documentation

This documentation will guide you through the different operators and functionality of the pattern system.

### Setup

Before use, setup dummy-data-generator by executing the following command from within the directory *dummy-data-generator.py* is located:

```
pip install -r requirements.txt
```

### Usage

#### Columns

*Dummy data generator* generates multiple rows of test/fake data in a csv file based on a defined template. These values (specifically grouped as *columns*) can be found in the *columns.json* file created after the script has been run for the first time. 

The columns can be modified through the script or via a text editor. 

##### Column values

You can use various placeholders to generate random or incremental data, for example, see the following column values:

- *example string* - this will generate as fixed text in each row.

- *test value +* - this will generate with an incremental count, represented by the plus sign, so the first row will be *test value 1* and row twenty will be *test value 20*.

- *test value ?* - this will generate with a random value, represented by the question mark, an example row would be *test value 374*. The ranged used to generate the random value can be changed via the settings.

- *test value (50,100)* - this will generate with a random number, where the range of this random number is set in the brackets, so a row may generate as *test value 63*. There are also some different behaviours with number ranges:
    - *(\*0.01,0.99)* - this will generate a random decimal with unlimited decimal places between 0.01 and 0.99 for each row.
    - *(£10,1000)* - this will generate a random number between 10 and 1000 with two decimal places, for example, 278.56.
    - *(3%20.5,30.5)* - this will generate a random number between 20.5 and 30.5 with 3 decimal places. The number of decimal places needs to be before the percentage sign.
    - *(-4,2)* - this will generate a number between -4 and 2 with no decimals.

- *test value [1|2|3]* - this will generate fixed text with a random value picked from within the square brackets, and separated by a vertical bar.

- *test value [1,2,3]* - this will generate fixed text with a value selected from within the square brackets. The commas separate the values, and represent that this is "ordered", meaning that "1" will be picked first, then "2" etc. Once the end of the list is reached, it will loop back to the start.

- *test value [(10,20)|(80,100)|(200,300)]* - this will generate fixed text with a random value that has been generated using the specified ranges. The values are generated from the specified ranges, and are then selected at random.

- *test value [(10,20),(80,100),(200,300)]* - this will generate fixed text with a range value selected from within the square brackets. As per the above, the values are generated from the specified ranges, and are then selected in order. 

Columns can also be added and deleted via the script.

#### Example row

You can view an example row (at any number) for the currently selected column file. This will allow you to view what the rows generated will contain. You can change the row number with the + or - keys, or enter a row number to jump to.

#### Images

The script can also be used to generate test images. These images are generated using RGB values, and are generated based on a number of generation modes, including:

- *random* - every pixel is a random colour, based on the minimum and maximum red, green and blue values specified in the settings.

- *single* - every pixel is the same colour, based on the maximum red, green and blue values only.

- *row* - generates rows of the same colour, based on the minimum and maximum red, green and blue values, and the row height, all of which are specified in the settings.

Resolution, as well as image file formats can be set in settings. See the settings section for supported formats.

#### File

The user is able to specify the file name, and can opt to have the file compressed after generation.

##### File name

Generated file names can be fixed text, or can use the following values (within curly brackets):

- Individual time values - *h*, *m*, *s* - hour, minute, second respectively.

- Individual date values - *d*, *M*, *y* - day, month, year respectively.

- Whole time value - *T* - formatted as *hour-minute-second*.

- Whole date value - *D* - formated as *day-month-year*.

- Random value - *?* - uses the min and max values set in the settings.

- Number of rows - *#* - uses the number of rows specified in the settings or by the user at time of generation.

Time values are generated as the file name is created (so, at the begining of generation).

##### File compression

Files can be generated and compressed. This must be enabled in the settings. At this time, the script will only compress to *.gz*. The file is deleted after compression, leaving only the compressed file.

#### Settings

A settings file (*settings.json*) is also created when the script has been run for the first time. Currently, the following can be changed via the settings:

- Default name of files generated - set to *data.csv* by default. If left blank, there will be a prompt to enter a file name before a file is generated.

- Name of folder where generated files are located - set to *generated-data* by default. If left blank, the files will generate in the same location as the script.

- Name of the JSON file being used to load the columns - set to *columns.json* by default. If the file does not exist, it will be created with default columns.

- Name of the folder where the columns are stored - set to *columns* by default. If left blank, the script will create and/or use the columns file in the same location as the script.

- Allow the script to compress the file after generation - set to "n" by default.

- Type of file compression if the compression is toggled. Can compress to *gz*, *zip*, *tar-gz* and *tar-bz2*.

- Format of the file being generated - set to "csv" by default. Can accept either *xls*, *csv*, *png*, *jpg* or *ico* at this time.

- Name of the sheet created in *xls* files - defaults to *sheet* if blank.

- The number of rows to generate - this value is unset by default. The script will ask the user to input the desired number of rows before generation per generation, if unset.

- Index value where the script starts counting from when creating rows - set to 0 by default. The value is not inclusive, counts will start at value + 1.

- The minimum and maximum values generated when using the "?" placeholder for the column value - default minimum is 1 and default maximum is 1,000,000.

- The way in which image files are generated. Accepts either *random*, *single* or *row* - set to *random* by default.

- The width and height of the image in pixels - both of which are set to 100px by default.

- The height of rows generated in *row* mode, in pixels - set to 1px by default

- The minimum and maximum red, green, and blue values to use when generating colours - the minimum is set to 0, and maximum set to 255, by default. When using *single* mode, only the maximum values are used.

- Allow the script to create a log, containing details of the generation - disabled by default. The log is created in the "log" directory in the same location of execution.

You can modify the settings from within the script, or directly via the JSON file.

Both JSON files are generated in the same directory as the script. 

### Requirements

- Python (written and tested with Python 3.5.4)
- xlwt
- Pillow