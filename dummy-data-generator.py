#! coding: utf-8
import csv, random, time, json, os, sys, platform

class Settings():
    def __init__(self):
        self.update_values()

    def update_values(self):
        self.json = self.get_settings()
        self.filename = self.get_setting_value("filename")
        self.foldername = self.get_setting_value("foldername")
        self.rownumber = self.get_setting_value("rownumber")
        self.columnfile = self.get_setting_value("columnfile") 

    def get_settings(self): # gets the settings from the settings json file, if the settings json file is not present, this will create the file
        if os.path.exists('settings.json') == False:
            with open('settings.json', 'w') as jsonfile:
                settings = [
                    {"key":"filename", "desc": "Default name of files generated", "value": "data.csv"}, 
                    {"key":"foldername", "desc":"Name of folder where generated files are located (remove the folder name to skip folder creation)", "value":"generated-data"},
                    {"key":"rownumber", "desc":"The index where the script starts from (not inclusive, counts will start at value + 1)", "value":"0"},
                    {"key":"columnfile", "desc":"The name of the json file where the columns are stored (will create the file if not present)", "value":"columns.json"}
                ]
                json.dump(settings, jsonfile)

        with open('settings.json') as jsonfile:
            settings = json.load(jsonfile)
        
        return settings

    def get_setting_value(self, value): # gets the settings from the settings json file, if the settings json file is not present, this will create the file
        for x in range (0, len(self.json)):
            if self.json[x]["key"] == value:
                settingvalue = self.json[x]["value"]
        
        return settingvalue

    def update_settings(self): # saves all changes to the settings in the settings json file
        with open('settings.json', "w") as jsonfile:
            json.dump(self.json, jsonfile)

        self.update_values()

settings = Settings()

def clear(platformname = sys.platform): # clear the terminal buffer ~ NOTE: this seems to be quite buggy, need to come back to this
    if platformname == "win32":
        os.system("cls")
    else:
        os.system("clear")

def view_settings(notification = ""): # displays the settings in the terminal, and allows the user to select settings
    option = ""
    while option != "q":
        clear()

        print(notification + "The following settings alter how the test data is generated:\n")

        count = 0

        for y in range (1, len(settings.json) + 1):
            print("---- No." + str(y) + " ----\n" + settings.json[y - 1]["desc"] + ": \n" + settings.json[y - 1]["value"])
            count = y

        option = input("\nEnter the setting number (1 to " + str(len(settings.json)) + ") to edit the setting, or:\nq. Quit\nOption:")

        if option == "q":
            menu()
        elif option.isdigit():
            if int(option) <= count:
                get_one_setting(int(option))
            elif int(option) > count:
                view_settings("No setting with the number " + option + "...\n")
        else:
            view_settings("No setting with the number " + option + "...\n")

def get_one_setting(index): # displays a selected setting in the terminal and provides the user with more options for the particular setting
    option = ""
    notification = ""

    while option != "q" or option != "b":
        clear()

        print("Setting number " + str(index) + ": \n")
        print("----------\nDescription: " + settings.json[index - 1]["desc"])
        print("Value: " + settings.json[index - 1]["value"] + "\n----------")

        option = input(notification + "\n1. Edit setting value\nb. Go back\nq. Quit\nOption:")

        if option == "q":
            menu()
        elif option == "b":
            view_settings()
        elif option == "1":
            settings.json[index - 1]["value"] = input("Enter new setting value:")
            settings.update_settings()
            view_settings("Value for setting " + str(index) + " updated!\n\n")
        else:
            notification = "\nInvalid option...\n"

def get_columns(): # gets the settings from the settings json file, if the settings json file is not present, this will create the file
    jsonfilename = settings.columnfile

    if os.path.exists(jsonfilename) == False:
        with open(jsonfilename, "w") as jsonfile:
            data = [
                {"value": "value 1", "name": "column 1"}, 
                {"value": "value 2", "name": "column 2"}, 
                {"value": "value 3", "name": "column 3"}
            ]

            json.dump(data, jsonfile)

    with open(jsonfilename) as jsonfile:
        data = json.load(jsonfile)
    '''
    for y in range (0, len(data)): # dealing with encoding issues, but this does not address the issue properly
        data[y]["name"] = data[y]["name"].replace("Â", "")
        data[y]["value"] = data[y]["value"].replace("Â", "")
    '''
    return data

def get_column_data(notification = ""): # displays the columns in the terminal, and allows the user to select columns
    option = ""
    while option != "q":
        data = get_columns()

        clear()

        print(notification + "The following columns and values are currently defined:\n")

        count = 0

        for y in range (1, len(data) + 1):
            print(str(y) + ". " + data[y - 1]["name"] + " - " + data[y - 1]["value"])
            count = y

        option = input("\nEnter a column number (1 to " + str(len(data)) + ") to edit the column, or:\n+. Add a column\nx. Delete a column\nq. Quit\nOption:")

        if option == "q":
            menu()
        elif option.isdigit():
            if int(option) <= count:
                get_one_column(data, int(option))
            elif int(option) > count:
                get_column_data("No column " + option + "...\n")
        elif option == "+":
            add_column()
            get_column_data("New column " + str(int(len(data) + 1)) + " added!\n\n")
        elif option == "x":
            delete_column(int(input("Enter the column number you want to delete: ")) - 1)
            notification = "Column deleted!\n\n"
        else:
            get_column_data("No column " + option + "...\n")

def add_column(): # adds a column to the column data list and updates the file
    data = get_columns()
    index = len(data)

    data.append({"name":input("Enter the name of the new column: "), "value":input("Enter the value of the new column: ")})

    update_column_data(data)

def delete_column(index): # deletes a column from the column data list and updates the file
    data = get_columns()

    confirm = input("Are you sure you want to delete column " + str(index + 1) + "? y/n\n")

    if confirm == "y":
        data.pop(index)
        update_column_data(data)

def get_one_column(data, index): # displays a selected column in the terminal and provides the user with more options for the particular column
    option = ""
    notification = ""

    while option != "q" or option != "b":
        clear()

        print("The column name and value for column number " + str(index) + ": \n")
        print("----------\nColumn name: " + data[index - 1]["name"])
        print("Column value: " + data[index - 1]["value"] + "\n----------")

        option = input(notification + "\n1. Edit column name\n2. Edit column value\nx. Delete column\nb. Go back\nq. Quit\nOption:")

        if option == "q":
            menu()
        elif option == "b":
            get_column_data()
        elif option == "1":
            data[index - 1]["name"] = input("Enter new column name:")
            update_column_data(data)
            get_column_data("Column name for column " + str(index) + " updated!\n\n")
        elif option == "2":
            data[index - 1]["value"] = input("Enter new column value:")
            update_column_data(data)
            get_column_data("Column value for column " + str(index) + " updated!\n\n")
        elif option == "x":
            delete_column(index - 1)
            get_column_data("Column " + str(index) + " deleted!\n\n")
        else:
            notification = "\nInvalid option...\n"

def update_column_data(data): # saves all changes to the column in the columns json file
    jsonfilename = settings.columnfile

    with open(jsonfilename, "w") as jsonfile:
        json.dump(data, jsonfile)

def get_values(value, rownumber): # reads the value for each column, and processes it into dummy data to add to the csv
    currentindex = 0
    output = ""
    randomvalue = False
    firstrangevalue = ""
    secondrangevalue = ""
    secondvalue = False
    valueformat = "%.0f"
    isdecimal = False

    while currentindex < len(value):
        if value[currentindex] == "(":
            while True:
                currentindex = currentindex + 1
                if value[currentindex].isdigit() == True and secondvalue == False:
                    firstrangevalue = firstrangevalue + value[currentindex]
                elif value[currentindex].isdigit() == True and secondvalue == True:
                    secondrangevalue = secondrangevalue + value[currentindex]
                elif value[currentindex] == ",":
                    secondvalue = True
                elif value[currentindex] == ".":
                    isdecimal = True
                    if secondvalue == False:
                        firstrangevalue = firstrangevalue + "."
                    else:
                        secondrangevalue = secondrangevalue + "."
                elif value[currentindex] == "-":
                    isdecimal = True
                    if secondvalue == False:
                        firstrangevalue = firstrangevalue + "-"
                    else:
                        secondrangevalue = secondrangevalue + "-"
                elif value[currentindex] == "£":
                    valueformat = "%.2f"
                elif value[currentindex] == "*":
                    valueformat = ""
                elif value[currentindex] == "%" and secondvalue == False:
                    valueformat = "%." + firstrangevalue + "f"
                    firstrangevalue = ""
                elif value[currentindex] == ")":
                    generatedvalue = ""

                    if isdecimal == True:
                        generatedvalue = random.uniform(float(firstrangevalue), float(secondrangevalue))
                    else:
                        generatedvalue = random.uniform(int(firstrangevalue), int(secondrangevalue))

                    if valueformat != "":
                        output = output + str(valueformat % generatedvalue)
                    else:
                        output = output + str(generatedvalue)

                    firstrangevalue = ""
                    secondrangevalue = ""
                    secondvalue = False
                    break
        elif value[currentindex] == "[":
            values = []
            tempstring = ""
            while True:
                currentindex = currentindex + 1

                if value[currentindex] == "|":
                    values.append(tempstring)
                    tempstring = ""
                elif value[currentindex] == "]":
                    values.append(tempstring)
                    output = values[random.randint(0,len(values) - 1)]
                    values = []
                    break
                else:
                    tempstring = tempstring + value[currentindex]

        elif value[currentindex] == "+":
            output = output + str(rownumber)
        else:
            output = output + value[currentindex]
        currentindex = currentindex + 1
    return output

def create_file(notification = ""): # creates and writes the file
    clear()

    file = settings.filename
    folder = settings.foldername
    columns = get_columns()
    rownumber = settings.rownumber

    if file == "":
        file = input("Enter a name for the file (do not include .csv): ") + ".csv"

    rows = input(notification + "Enter the number of rows to generate (or enter 'q' or 'b' to go back to the menu): ")

    if rows == "q" or rows == "b":
        menu()
    elif rows.isdigit() == False and (rows != 'q' or rows != 'b'):
        create_file("Please enter a number...\n\n")

    if folder != "":
        if os.path.exists(folder + "/") == False:
            os.makedirs(folder + "/")

        file = folder + "/" + file

    print("\nCreating file...")

    starttime = time.time()

    with open(file, 'w') as myfile:
        writer = csv.writer(myfile, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_ALL)
        
        headers = []

        for y in range (0, len(columns)):
            headers.append(columns[y]["name"])

        writer.writerows([headers])

        values = []

        for z in range (1, int(rows) + 1):
            for x in range (0, len(columns)):
                values.append(get_values(columns[x]["value"], int(rownumber) + z))

            writer.writerows([values])

            values = []

    menu("\nTook %.2f seconds" % (time.time() - starttime) + " to generate " + "{0:,}".format(int(rows)) + " rows in '" + file + "'...\n")         

def menu(notification = ""): # main menu, first thing the user will see
    clear()

    filename = settings.filename
    foldername = settings.foldername
    rownumber = settings.rownumber
    columnfile = settings.columnfile

    get_columns()

    print("Dummy data generator v" + version + "\nAndrew H 2018\n\nCurrent file name: " + filename + "\nCurrent column file: " + columnfile + "\n" + notification)

    print("1. Generate file")
    print("2. Add and edit columns")
    print("3. Settings")
    print("q. Quit")

    selection = input("\nEnter option: ")

    if selection == "1":
        create_file()
    if selection == "2":
        get_column_data()
    if selection == "3":
        view_settings()
    elif selection == "q":
        exit()
    else:
        menu("\nInvalid option...\n")

version = "0.4.0"

menu()