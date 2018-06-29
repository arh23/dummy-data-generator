#! coding: utf-8
import csv, random, time, json, os, sys, platform, datetime, gzip, shutil

class Settings():
    def __init__(self):
        self.update_values()

    def update_values(self): # update attribute values
        self.json = self.get_settings()
        self.filename = self.get_setting_value("filename")
        self.foldername = self.get_setting_value("foldername")
        self.columnfile = self.get_setting_value("columnfile")
        self.columnfolder = self.get_setting_value("columnfolder")
        self.compress = self.get_setting_value("compress")
        self.numberofrows = self.get_setting_value("numberofrows")
        self.rownumber = self.get_setting_value("rownumber")
        self.min = self.get_setting_value("min")
        self.max = self.get_setting_value("max")

    def get_settings(self): # gets the settings from the settings json file, if the settings json file is not present, this will create the file
        if os.path.exists('settings.json') == False:
            with open('settings.json', 'w') as jsonfile:
                settings = [
                    {"section":0, "key":"filename", "desc": "Default name of files generated", "value": "data.csv"}, 
                    {"section":0, "key":"foldername", "desc":"The name of folder where generated files are located (remove the folder name to skip folder creation)", "value":"generated-data"},
                    {"section":0, "key":"columnfile", "desc":"The name of the json file where the columns are stored (will create the file if not present)", "value":"columns.json"},
                    {"section":0, "key":"columnfolder", "desc":"The name of the folder where the columns are stored (remove the folder name to skip folder creation)", "value":"columns"},
                    {"section":0, "key":"compress", "desc":"Toggle to compress the file after generation (compresses to .gz) y/n", "value":"n"},
                    {"section":1, "key":"numberofrows", "desc":"The number of rows to generate (will ask at time of generation if blank)", "value":""},                    
                    {"section":1, "key":"rownumber", "desc":"The index where the script starts from (not inclusive, counts will start at value + 1)", "value":"0"},
                    {"section":1, "key":"min", "desc":"The minimum value generated with the '?' symbol", "value":"1"},
                    {"section":1, "key":"max", "desc":"The maximum value generated with the '?' symbol", "value":"1000000"}
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

class Columns():
    def get_columns(self): # gets the settings from the settings json file, if the settings json file is not present, this will create the file
        self.jsonfilename = settings.columnfile

        if settings.columnfolder != "":
            if os.path.exists(settings.columnfolder + "/") == False:
                os.makedirs(settings.columnfolder + "/")

            self.jsonfilename = settings.columnfolder + "/" + settings.columnfile

        if os.path.exists(self.jsonfilename) == False:
            with open(self.jsonfilename, "w") as jsonfile:
                data = [
                    {"value": "value 1", "name": "column 1"}, 
                    {"value": "value 2", "name": "column 2"}, 
                    {"value": "value 3", "name": "column 3"}
                ]
                json.dump(data, jsonfile)

        with open(self.jsonfilename) as jsonfile:
            data = json.load(jsonfile)

        self.json = data

    def update_column_data(self): # saves all changes to the column in the columns json file
        with open(self.jsonfilename, "w") as jsonfile:
            json.dump(self.json, jsonfile)

        self.get_columns()

    def get_columns_total(self): # returns number of different columns in the column json data
        return len(self.json)

columns = Columns()

class ValueList():
    def __init__(self):
        self.listindex = -1

    def set_list(self, listvalue): # gets the settings from the settings json file, if the settings json file is not present, this will create the file
        self.list = listvalue
        self.listlength = len(listvalue)

    def get_next_list_value(self):
        self.listindex = self.listindex + 1

        if self.listindex < self.listlength:
            return self.list[self.listindex]
        else:
            self.listindex = -1
            return self.get_next_list_value()

    def get_random_list_value(self):
        return self.list[random.randint(0, self.listlength - 1)]

    def reset_index(self):
        self.listindex = -1

valuelist = ValueList()

def clear(platformname = sys.platform): # clear the terminal buffer ~ NOTE: this seems to be quite buggy, need to come back to this
    if platformname == "win32":
        os.system("cls")
    else:
        os.system("clear")

def view_settings(notification = ""): # displays the settings in the terminal, and allows the user to select settings
    settings.update_values()

    option = ""
    while option != "q":
        clear()

        print(notification + "The following settings alter how the test data is generated:\n")

        print("File and folder settings -\n")
        for y in range (0, len(settings.json)):
            if settings.json[y]["section"] == 0:
                print(str(y + 1) + ". " + settings.json[y]["desc"] + ": \n   " + (settings.json[y]["value"] if settings.json[y]["value"] != "" else "<no value>"))

        print("\nData generation settings -\n")
        for y in range (0, len(settings.json)):
            if settings.json[y]["section"] == 1:
                print(str(y + 1) + ". " + settings.json[y]["desc"] + ": \n   " + (settings.json[y]["value"] if settings.json[y]["value"] != "" else "<no value>"))

        option = input("\nEnter the setting number (1 to " + str(len(settings.json)) + ") to edit the setting, or:\nq. Quit\n\nOption:")

        if option == "q":
            menu()
        elif option.isdigit():
            if int(option) <= len(settings.json):
                view_one_setting(int(option))
            elif int(option) > len(settings.json):
                view_settings("No setting with the number " + option + "...\n")
        else:
            view_settings("No setting with the number " + option + "...\n")

def view_one_setting(index): # displays a selected setting in the terminal and provides the user with more options for the particular setting
    option = ""
    notification = ""

    while option != "q" or option != "b":
        clear()

        print("Setting number " + str(index) + ": \n")
        print("----------\nDescription: " + settings.json[index - 1]["desc"])
        print("Value: " + (settings.json[index - 1]["value"] if settings.json[index - 1]["value"] != "" else "<no value>") + "\n----------")

        option = input(notification + "\n1. Edit setting value\nb. Go back\nq. Quit\n\nOption:")

        if option == "q":
            menu()
        elif option == "b":
            view_settings()
        elif option == "1":
            settings.json[index - 1]["value"] = input("\nEnter new setting value:")
            settings.update_settings()
            view_settings("Value for setting " + str(index) + " updated!\n\n")
        else:
            notification = "\nInvalid option...\n"

def view_columns(notification = ""): # displays the columns in the terminal, and allows the user to select columns
    option = ""
    while option != "q":
        clear()

        print(notification + "The following columns and values are currently defined:\n")

        count = 0

        for y in range (1, columns.get_columns_total() + 1):
            print(str(y) + ". " + columns.json[y - 1]["name"] + " - " + columns.json[y - 1]["value"])
            count = y

        option = input("\nEnter a column number (1 to " + str(columns.get_columns_total()) + ") to edit the column, or:\n+. Add a column\nx. Delete a column\nq. Quit\n\nOption:")

        if option == "q":
            menu()
        elif option.isdigit():
            if int(option) <= count:
                view_one_column(int(option))
            elif int(option) > count:
                notification = "No column " + option + "...\n"
        elif option == "+":
            columns.json.append({"name":input("\nEnter the name of the new column: "), "value":input("Enter the value of the new column: ")})

            columns.update_column_data()

            notification = "New column " + str(int(columns.get_columns_total())) + " added!\n\n"
        elif option == "x":
            index = int(input("\nEnter the column number you want to delete: ")) - 1
            confirm = input("Are you sure you want to delete column " + str(index + 1) + "? y/n\n")

            if confirm == "y":
                columns.json.pop(index)
                columns.update_column_data()

                notification = "Column deleted!\n\n"
            else:
                notification = "Column NOT deleted!\n\n"
        else:
            notification = "No column " + option + "...\n"

def view_one_column(index): # displays a selected column in the terminal and provides the user with more options for the particular column
    option = ""
    notification = ""

    while option != "q" or option != "b":
        clear()

        print("The column name and value for column number " + str(index) + ": \n")
        print("----------\nColumn name: " + columns.json[index - 1]["name"])
        print("Column value: " + columns.json[index - 1]["value"] + "\n----------")

        option = input(notification + "\n1. Edit column name\n2. Edit column value\nx. Delete column\nb. Go back\nq. Quit\n\nOption:")

        if option == "q":
            menu()
        elif option == "b":
            view_columns()
        elif option == "1":
            columns.json[index - 1]["name"] = input("\nEnter new column name:")
            columns.update_column_data()
            view_columns("Column name for column " + str(index) + " updated!\n\n")
        elif option == "2":
            print("\nView the documentation for the possible column values and placeholders that can be used.\n")
            columns.json[index - 1]["value"] = input("Enter new column value:")
            columns.update_column_data()
            view_columns("Column value for column " + str(index) + " updated!\n\n")
        elif option == "x":
            confirm = input("\nAre you sure you want to delete column " + str(index) + "? y/n\n")

            if confirm == "y":
                columns.json.pop(index)
                columns.update_column_data()

                view_columns("Column " + str(index) + " deleted!\n\n")
            else:
                view_columns("Column " + str(index) + " NOT deleted!\n\n")
        else:
            notification = "\nInvalid option...\n"

def get_filename():
    currentindex = 0
    filename = ""
    file = settings.filename

    if file == "":
        file = input("Enter a name for the file (do not include .csv): ") + ".csv"

    now = datetime.datetime.now()

    while currentindex < len(file):
        if file[currentindex] == "{":
            while True:
                currentindex = currentindex + 1
                
                if file[currentindex] == "h":
                    filename = filename + str('%02d' % now.hour)
                elif file[currentindex] == "m":
                    filename = filename + str('%02d' % now.minute)
                elif file[currentindex] == "s":
                    filename = filename + str('%02d' % now.second)
                elif file[currentindex] == "d":
                    filename = filename + str('%02d' % now.day)
                elif file[currentindex] == "M":
                    filename = filename + str('%02d' % now.month)
                elif file[currentindex] == "y":
                    filename = filename + str(now.year)
                elif file[currentindex] == "D":
                    filename = filename + str('%02d' % now.day) + "-" + str('%02d' % now.month) + "-" + str(now.year)
                elif file[currentindex] == "T":
                    filename = filename + str('%02d' % now.hour) + "-" + str('%02d' % now.minute) + "-" + str('%02d' % now.second)
                elif file[currentindex] == "?":
                    filename = filename + str(random.randint(int(settings.min), int(settings.max)))
                elif file[currentindex] == "#":
                    filename = filename + str(settings.numberofrows)
                elif file[currentindex] == "}":
                    break
                else:
                    filename = filename + file[currentindex]
        else:
            filename = filename + file[currentindex]

        currentindex = currentindex + 1

    if settings.foldername != "":
        filename = settings.foldername + "/" + filename

    return filename

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
            randomlist = False
            orderedlist = False

            while True:
                currentindex = currentindex + 1

                if value[currentindex] == "|" or value[currentindex] == ",":
                    values.append(tempstring)
                    tempstring = ""

                    if value[currentindex] == "|":
                        randomlist = True
                        orderedlist = False
                    elif value[currentindex] == ",":
                        randomlist = False
                        orderedlist = True                        

                elif value[currentindex] == "]":
                    values.append(tempstring)
                    valuelist.set_list(values)
                    values = []

                    if randomlist:
                        output = valuelist.get_random_list_value()
                    elif orderedlist:
                        output = valuelist.get_next_list_value()

                    break
                    
                else:
                    tempstring = tempstring + value[currentindex]

        elif value[currentindex] == "+":
            output = output + str(rownumber)
        elif value[currentindex] == "?":
            output = output + str(random.randint(int(settings.min), int(settings.max)))
        else:
            output = output + value[currentindex]
        currentindex = currentindex + 1
    return output

def create_file(notification = ""): # creates and writes the file
    clear()
    
    if settings.numberofrows == "":
        settings.numberofrows = input(notification + "Enter the number of rows to generate (or enter 'q' or 'b' to go back to the menu): ")

    rows = settings.numberofrows
    file = get_filename()
    folder = settings.foldername
    rownumber = settings.rownumber

    if rows == "q" or rows == "b":
        menu()
    elif rows.isdigit() == False and (rows != 'q' or rows != 'b'):
        create_file("Please enter a number...\n\n")

    if folder != "":
        if os.path.exists(folder + "/") == False:
            os.makedirs(folder + "/")

    print("Creating file...")

    starttime = time.time()

    with open(file, 'w') as currentfile:
        writer = csv.writer(currentfile, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_ALL)
        
        headers = []

        for y in range (0, columns.get_columns_total()):
            headers.append(columns.json[y]["name"])

        writer.writerows([headers])

        values = []

        for z in range (1, int(rows) + 1):
            for x in range (0, columns.get_columns_total()):
                values.append(get_values(columns.json[x]["value"], int(rownumber) + z))

            writer.writerows([values])

            values = []


    if settings.compress == "y":
        print("\nCompressing generated file...")

        with open(file, 'rb') as currentfile:
            with gzip.open(file + '.gz', 'wb') as compressedfile:
                shutil.copyfileobj(currentfile, compressedfile)

        os.remove(file)

        menu("\nTook %.2f seconds" % (time.time() - starttime) + " to generate " + "{0:,}".format(int(rows)) + " rows and compress '" + file + ".gz'...\n")
    else:
        menu("\nTook %.2f seconds" % (time.time() - starttime) + " to generate " + "{0:,}".format(int(rows)) + " rows in '" + file + "'...\n")
             

def menu(notification = ""): # main menu, first thing the user will see
    clear()

    filename = settings.filename 
    columnfile = settings.columnfile

    if (settings.foldername != ""):
        filename = settings.foldername + "/" + settings.filename 

    if (settings.columnfolder != ""):
        columnfile = settings.columnfolder + "/" + settings.columnfile

    columns.get_columns()
    valuelist.reset_index()

    print("Dummy data generator v" + version + "\nAndrew H 2018\n\nCurrent file name: " + filename + "\nCurrent column file: " + columnfile + "\n" + notification)

    print("1. Generate file")
    print("2. Add and edit columns")
    print("3. Settings")
    print("q. Quit")

    option = input("\nEnter option: ")

    if option == "1":
        create_file()
    if option == "2":
        view_columns()
    if option == "3":
        view_settings()
    elif option == "q":
        exit()
    else:
        menu("\nInvalid option...\n")

version = "0.6.0"

menu()