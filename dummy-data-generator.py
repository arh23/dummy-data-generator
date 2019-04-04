#! coding: utf-8
import subprocess, csv, xlwt, random, time, json, os, sys, platform, datetime, gzip, zipfile, tarfile, shutil

class Logger():
    def __init__(self):
        self.log = []

    def get_logging_state(self): # checks settings if logging is enabled, if it cannot check settings, logging will be disabled
        try:
            if settings.log == "y":
                return True
            else:
                return False
        except:
            return False

    def add_log_entry(self, value, write = False): # adds a new log entry
        now = datetime.datetime.now()
        if self.get_logging_state():
            self.log.append("[" + str('%02d' % now.hour) + ":" + str('%02d' % now.minute) + ":" + str('%02d' % now.second) + "] " + value)
            if write == True:
                self.write_log()

    def write_log(self): # writes the current log array into the log file and clears the log array
        now = datetime.datetime.now()
        logname = "logs/log-" + str('%02d' % now.day) + "-" + str('%02d' % now.month) + "-" + str('%02d' % now.year) + ".txt"

        if os.path.exists("logs/") == False:
            os.makedirs("logs/")

        with open(logname, 'a') as logfile:
            for x in range (0, len(self.log)):
                logfile.write(self.log[x] + "\n")

        self.log = []

logger = Logger()

class Settings():
    def __init__(self):
        self.defaultsettings = [
            {"section":0, "index":1, "key":"filename", "desc": "Default name of files generated", "value": "data"}, 
            {"section":0, "index":2, "key":"foldername", "desc":"The name of folder where generated files are located (remove the folder name to skip folder creation)", "value":"generated-data"},
            {"section":0, "index":3, "key":"columnfile", "desc":"The name of the json file where the columns are stored (will create the file if not present)", "value":"columns.json"},
            {"section":0, "index":4, "key":"columnfolder", "desc":"The name of the folder where the columns are stored (remove the folder name to skip folder creation)", "value":"columns"},
            {"section":0, "index":5, "key":"compress", "desc":"Toggle to compress the file after generation y/n", "value":"n", "acceptedvalues":["y","n"]},
            {"section":0, "index":12, "key":"compresstype", "desc":"The type of compression used, if compression is enabled", "value":"gz", "acceptedvalues":["gz", "zip", "tar-gz", "tar-bz2"]},            
            {"section":0, "index":6, "key":"fileformat", "desc":"The format of the file generated (csv or xls)", "value":"csv", "acceptedvalues":["csv","xls"]},
            {"section":0, "index":13, "key":"sheetname", "desc":"The name of the sheet generated in xls files (defaults to 'sheet' if blank)", "value":""},            
            {"section":1, "index":7, "key":"numberofrows", "desc":"The number of rows to generate (will ask at time of generation if blank)", "value":""},                    
            {"section":1, "index":8, "key":"rownumber", "desc":"The index where the script starts from (not inclusive, counts will start at value + 1)", "value":"0"},
            {"section":1, "index":9, "key":"min", "desc":"The minimum value generated with the '?' symbol", "value":"1"},
            {"section":1, "index":10, "key":"max", "desc":"The maximum value generated with the '?' symbol", "value":"1000000"},
            {"section":2, "index":11, "key":"logging", "desc":"Enable logging of various events throughout generation (can affect performance) y/n", "value":"n", "acceptedvalues":["y","n"]}
        ]
        self.update_values()

    def update_values(self): # update attribute values
        self.json = self.get_settings()
        self.filename = self.get_setting_value("filename")
        self.foldername = self.get_setting_value("foldername")
        self.columnfile = self.get_setting_value("columnfile")
        self.columnfolder = self.get_setting_value("columnfolder")
        self.compress = self.get_setting_value("compress")
        self.compresstype = self.get_setting_value("compresstype")
        self.fileformat = self.get_setting_value("fileformat")
        self.sheetname = self.get_setting_value("sheetname")
        self.numberofrows = self.get_setting_value("numberofrows")
        self.rownumber = self.get_setting_value("rownumber")
        self.min = self.get_setting_value("min")
        self.max = self.get_setting_value("max")
        self.log = self.get_setting_value("logging")

    def get_settings(self): # gets the settings from the settings json file, if the settings json file is not present, this will create the file
        if os.path.exists('settings.json') == False:
            with open('settings.json', 'w') as jsonfile:
                json.dump(self.defaultsettings, jsonfile)

        with open('settings.json') as jsonfile:
            settings = json.load(jsonfile)
        
        return settings

    def get_setting_value(self, value): # gets the settings from the settings json file, if the settings json file is not present, this will create the file
        try:
            for x in range (0, len(self.json)):
                if self.json[x]["key"] == value:
                    settingvalue = self.json[x]["value"]
            
            return settingvalue
        except UnboundLocalError:
            print("ERROR - could not load setting for '" + value + "', updating current settings file.")

            index = 0

            while True:
                try:
                    if self.defaultsettings[index]["key"] == value:
                        self.json.append(self.defaultsettings[index])
                        self.update_settings()
                        break
                    else:
                        index = index + 1
                except IndexError:
                    print("ERROR - unknown setting specified in code!\n")
                    break

    def get_setting_value_by_index(self, value): # gets a setting value for the provided index
        for x in range (0, len(self.json)):
            if self.json[x]["index"] == value:
                settingvalue = self.json[x]["value"]
        
        return settingvalue

    def get_all_values(self): # gets all setting values
        settingvalues = [None] * (len(self.json) + 1)

        for setting in self.json:
            if int(setting["index"]) > len(self.json):
                settingvalues[len(self.json) - 1] = setting["value"]                    
            else:
                settingvalues[int(setting["index"])] = setting["value"]        

        return settingvalues

    def update_settings(self): # saves all changes to the settings in the settings json file
        with open('settings.json', "w") as jsonfile:
            jsonfile.write(json.dumps(self.json, indent=4))

        self.update_values()

    def update_settings_file(self): # updates settings (excluding values), adds new settings, and removes old/removed settings from settings.json
        values = self.get_all_values()
        self.json = self.defaultsettings
        count = 0

        for setting in self.json:
            try:
                self.json[count]["value"] = values[int(setting["index"])]
            except IndexError:
                if len(self.json) > len(values):
                    while len(self.json) > len(values):
                        values.insert(len(values), self.get_setting_value_by_index(len(values)))

            count += 1

        self.update_settings()

settings = Settings()

class Columns():
    def get_columns(self): # gets the columns from the columns json file, if the columns json file is not present, this will create the file
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
                jsonfile.write(json.dumps(data, indent=4))

        with open(self.jsonfilename) as jsonfile:
            data = json.load(jsonfile)

        self.json = data

    def update_column_data(self): # saves all changes to the column in the columns json file
        with open(self.jsonfilename, "w") as jsonfile:
            jsonfile.write(json.dumps(self.json, indent=4))

        logger.add_log_entry("Updated columns - " + str(self.json))
        self.get_columns()

    def get_columns_total(self): # returns number of different columns in the column json data
        return len(self.json)

columns = Columns()

class ValueList():
    def __init__(self):
        self.listindex = -1

    def set_list(self, listvalue): # sets the the list and listlength of the current ValueList instance, based on the list set for listvalue
        self.list = listvalue
        self.listlength = len(listvalue)

    def get_next_list_value(self): # increments the list pointer by one and returns the next value in the list
        self.listindex = self.listindex + 1

        if self.listindex < self.listlength:
            return self.list[self.listindex]
        else:
            self.listindex = -1
            return self.get_next_list_value()

    def get_random_list_value(self): # selects a random value from the current list
        return self.list[random.randint(0, self.listlength - 1)]

    def reset_index(self): # resets the index, to correctly count from the start of the current list again
        self.listindex = -1

valuelist = ValueList()

def clear(platformname = sys.platform): # clear the terminal buffer ~ NOTE: this seems to be quite buggy, need to come back to this
    if platformname == "win32":
        os.system("cls")
    else:
        os.system("clear")

def view_settings(notification = ""): # displays setting sections in the terminal, and allows the user to select which section to view
    settings.update_values()

    option = ""
    while option != "q":
        clear()

        print("The following settings alter how the test data is generated:\n")

        print("1. File and folder settings")
        print("2. Data generation settings")
        print("3. Logging settings")  

        option = input(notification + "\nEnter the section number (1 to 3) to view the settings for that section, or:\nq. Quit\n\nOption:")

        if option == "q":
            menu()
        elif option.isdigit():
            if int(option) <= 3:
                view_setting_group(int(option) - 1)
            elif int(option) > 3:
                view_settings("\nNo section with the number " + option + "...\n")
        else:
            view_settings("\nInvalid option...\n")

def view_setting_group(section, notification = ""): # displays all the settings in the section, "section" is defined in settings.json
    clear()
    groupedsettings = []

    print("The following settings alter how the test data is generated:\n")

    count = 0

    for y in range (0, len(settings.json)):
        if settings.json[y]["section"] == section:
            count += 1
            groupedsettings.append(settings.json[y])
            print(str(count) + ". " + settings.json[y]["desc"] + (": \n   " if (count < 10) else ": \n    ") + (settings.json[y]["value"] if settings.json[y]["value"] != "" else "<no value>"))

    option = input(notification + "\nEnter the setting number" + ("" if len(groupedsettings) == 1 else " (1 to " + str(len(groupedsettings)) + ")") + " to edit the setting, or:\nq. Quit\n\nOption:")

    if option == "q":
        view_settings()
    elif option.isdigit():
        if int(option) <= len(groupedsettings):
            view_one_setting(groupedsettings[int(option) - 1]["index"])
        elif int(option) > len(groupedsettings):
            view_setting_group(section, "\nNo setting with the number " + option + "...\n")
    else:
        view_setting_group(section, "\nInvalid option...\n")

def view_one_setting(index): # displays a selected setting in the terminal and provides the user with more options for the particular setting
    option = ""
    notification = ""
    selectedindex = 0

    for y in range (0, len(settings.json)):
        if settings.json[y]["index"] == index:
            selectedindex = y

    while option != "q" or option != "b":
        clear()

        print("Setting " + str(selectedindex + 1) + ", index " + str(index) + ": \n")
        print("----------\nDescription: " + settings.json[selectedindex]["desc"])
        print("Value: " + (settings.json[selectedindex]["value"] if settings.json[selectedindex]["value"] != "" else "<no value>") + "\n----------")

        if "acceptedvalues" in settings.json[selectedindex]:
            print("\nThe following values are accepted for this setting:")
            for acceptedvalue in settings.json[selectedindex]["acceptedvalues"]:
                print(" - " + acceptedvalue)

        option = input(notification + "\n1. Edit setting value\nb. Go back\nq. Quit\n\nOption:")

        if option == "q":
            menu()
        elif option == "b":
            view_setting_group(settings.json[selectedindex]["section"])
        elif option == "1":
            if settings.json[selectedindex]["key"] == "columnfile":
                view_column_files("", "settings")
            else:
                inputvalue = input("\nEnter new setting value:")
                if "acceptedvalues" in settings.json[selectedindex]:
                    if inputvalue in settings.json[selectedindex]["acceptedvalues"]:
                        settings.json[selectedindex]["value"] = inputvalue
                        settings.update_settings()

                        view_setting_group(settings.json[selectedindex]["section"], "\nValue updated!\n")
                    else:
                        notification = "\nInvalid value...\nMust be one of the following: " + str(settings.json[selectedindex]["acceptedvalues"]) + "\n"
                else:
                    settings.json[selectedindex]["value"] = inputvalue
                    settings.update_settings()

                    logger.add_log_entry("Value for setting '" + settings.json[selectedindex]["key"] + "' updated!", True)
                    view_setting_group(settings.json[selectedindex]["section"], "\nValue updated!\n")
        else:
            notification = "\nInvalid option...\n"

def view_column_files(notification = "", prevstate = "menu"): # displays the column files in the terminal, and allows the user to select a file to use
    option = ""
    while option != "q":
        clear()

        subnotif = "\n"

        print("The following column files are located in the '" + settings.columnfolder + "' folder: \n\nCurrent columns file: " + settings.columnfile + "\n")

        if settings.columnfolder == "":
            settings.columnfolder = "."

        files = os.listdir(settings.columnfolder)

        fileslist = []
        for names in files:
            if names.endswith(".json"):
                fileslist.append(names)
        
        for y in range (0, len(fileslist)):
            print(str(y + 1) + ". " + fileslist[y])

        if len(fileslist) == 1:
            option = input(notification + "\nEnter q to quit.\n\nOption:")

            if option == "q":
                if prevstate == "menu":
                    menu()
                elif prevstate == "settings":
                    view_settings()
                else:
                    menu()
            else:
                notification = "\nThe only available column file has already been selected...\n"
        else:
            option = input(notification + "\nEnter a file number (1 to " + str(len(fileslist)) + ") to select the column for use, or:\n+. Add a column file\nx. Delete a column file\nq. Quit\n\nOption:")

            if option == "q":
                if prevstate == "menu":
                    menu()
                elif prevstate == "settings":
                    view_settings()
                else:
                    menu()
            elif option == "+":
                columnfilename = input("\nEnter the name of the new column file (excluding file extension): ")

                for y in range (0, len(settings.json)):
                    if settings.json[y]["key"] == "columnfile":
                        settings.json[y]["value"] = columnfilename + ".json"
                        settings.update_settings()

                settings.update_settings()
                columns.get_columns()
                notification = "\nCreated and selected new column file " + columnfilename + ".json...\n"
            elif option == "x":
                columnfilename = input("\nEnter the name of the column file to be deleted (excluding file extension): ") + ".json"

                if os.path.exists(settings.columnfolder + "/" + columnfilename):
                    os.remove(settings.columnfolder + "/" + columnfilename)

                    if settings.columnfile == columnfilename:
                        for y in range (0, len(settings.json)):
                            if settings.json[y]["key"] == "columnfile":
                                settings.json[y]["value"] = "columns.json"
                                settings.update_settings()
                                subnotif = "Reverted column file to 'columns.json' as deleted file was the selected columns file!\n"

                    columns.get_columns()
                    notification = "\nDeleted column file " + columnfilename + "... " + subnotif
                else:
                    notification = "\nFile " + columnfilename + " does not exist... " + subnotif
            elif option.isdigit():
                if int(option) <= len(fileslist):
                    for y in range (0, len(settings.json)):
                        if settings.json[y]["key"] == "columnfile":
                            settings.json[y]["value"] = fileslist[int(option) - 1]
                            settings.update_settings()
                            notification = "\nSelected column file " + option + ", " + fileslist[int(option) - 1] + "...\n"

                elif int(option) > len(fileslist):
                    notification = "\nNo column file " + option + "...\n"
            else:
                notification = "\nInvalid column file or option...\n"

def view_columns(notification = ""): # displays the columns in the terminal, and allows the user to select columns
    option = ""
    while option != "q":
        clear()

        print("The following columns and values are currently defined:\n")

        count = 0

        for y in range (1, columns.get_columns_total() + 1):
            print(str(y) + ". " + columns.json[y - 1]["name"] + " - " + columns.json[y - 1]["value"])
            count = y

        option = input(notification + "\nEnter a column number (1 to " + str(columns.get_columns_total()) + ") to edit the column, or:\n+. Add a column\nx. Delete a column\nq. Quit\n\nOption:")

        if option == "q":
            menu()
        elif option.isdigit():
            if int(option) <= count:
                view_one_column(int(option))
            elif int(option) > count:
                notification = "\nNo column " + option + "...\n"
        elif option == "+":
            columns.json.append({"name":input("\nEnter the name of the new column: "), "value":input("Enter the value of the new column: ")})

            columns.update_column_data()

            notification = "\nNew column '" + columns.json[int(columns.get_columns_total() - 1)]["name"] + "' added!\n"
            logger.add_log_entry("New column '" + columns.json[int(columns.get_columns_total() - 1)]["name"] + "' added!", True)
        elif option == "x":
            index = int(input("\nEnter the column number you want to delete: ")) - 1
            confirm = input("Are you sure you want to delete column " + str(index + 1) + "? y/n\n")

            if confirm == "y":
                notification = "\nColumn '" + columns.json[index]["name"] + "' deleted!\n"
                logger.add_log_entry("Column '" + columns.json[index]["name"] + "' deleted!", True)

                columns.json.pop(index)
                columns.update_column_data()
            else:
                notification = "\nColumn NOT deleted!\n"
        else:
            notification = "\nInvalid column or option...\n"

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
            view_columns("\nColumn name for column " + str(index) + " updated!\n")
        elif option == "2":
            print("\nView the documentation for the possible column values and placeholders that can be used.\n")
            columns.json[index - 1]["value"] = input("Enter new column value:")
            columns.update_column_data()

            message = "Column value for column " + str(index) + " updated!"
            logger.add_log_entry(message, True)
            view_columns("\n" + message + "\n")
        elif option == "x":
            confirm = input("\nAre you sure you want to delete column " + str(index) + "? y/n\n")

            if confirm == "y":
                message = "Column '" + columns.json[index - 1]["name"] + "' deleted!"

                columns.json.pop(index - 1)
                columns.update_column_data()

                logger.add_log_entry(message, True)
                view_columns("\n" + message + "\n")
            else:
                view_columns("\nColumn '" + columns.json[index - 1]["name"] + "' NOT deleted!\n")
        else:
            notification = "\nInvalid option...\n"

def get_filename(): # generate the name of the file, based on the current settings 'filename' value
    currentindex = 0
    filename = ""
    file = settings.filename

    if file == "":
        file = input("Enter a name for the file (do not include the format of the file): ")

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

    if settings.fileformat == "":
        settings.fileformat = "csv"

    filename = filename + "." + settings.fileformat

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
                        valueformat = "%.0f"
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
                        output = output + valuelist.get_random_list_value()
                    elif orderedlist:
                        output = output + valuelist.get_next_list_value()

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

def get_demo_rows(notification = "", rownumber = None):
    clear()

    if rownumber == None:
        rownumber = int(settings.rownumber)

    headers = ["COLUMN NAME", ""]
    maxheaderlength = 0

    print("The following is an example of what can be generated for row " + str(rownumber + 1) +":\n")

    for y in range (0, columns.get_columns_total()):
        headers.append(columns.json[y]["name"])
        if len(columns.json[y]["name"]) > int(maxheaderlength):
            maxheaderlength = len(columns.json[y]["name"])

    values = ["VALUE", ""]
    border = ""

    for bordercount in range (0, maxheaderlength + 2):
        border += "-"

    headers[1] = border
    values[1] = border

    for z in range (1, 2):
        for x in range (0, columns.get_columns_total()):
            values.append(get_values(columns.json[x]["value"], int(rownumber) + z))

    for z in range (0, len(headers)):
        if len(headers[z]) < maxheaderlength:
            while len(headers[z]) < maxheaderlength:
                headers[z] = headers[z] + " "

        if z == 1:
            print(headers[z] + "+" + values[z])
        else:           
            print(headers[z] + "  |  " + values[z])

    option = input(notification + "\nEnter a number to view the example at that row, or: \n+. Increase row number\n-. Decrease row number\nq. Quit\n\nOption:")

    if option == "q":
        menu()
    elif option == "+":
        get_demo_rows("", rownumber + 1)
    elif option == "-":
        get_demo_rows("", rownumber - 1)
    elif option.isdigit():
        get_demo_rows("", int(option) - 1)
    else:
        get_demo_rows("", rownumber) 

def create_file(notification = ""): # creates and writes the file
    try:
        clear()
        
        currentcolumn = 0

        if settings.numberofrows == "":
            settings.numberofrows = input(notification + "Enter the number of rows to generate (or enter 'q' or 'b' to go back to the menu): ")

        rows = settings.numberofrows
        file = get_filename()
        folder = settings.foldername
        rownumber = settings.rownumber

        if rows == "q" or rows == "b":
            menu()
        elif rows.isdigit() == False and (rows != 'q' or rows != 'b'):
            settings.numberofrows = ""
            create_file("Please enter a number...\n\n")

        if folder != "":
            if os.path.exists(folder + "/") == False:
                os.makedirs(folder + "/")

        logger.add_log_entry("Creating file...")
        print("Creating file...")

        starttime = time.time()

        if settings.fileformat == "csv":
            with open(file, 'w') as currentfile:
                writer = csv.writer(currentfile, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_ALL)
                
                headers = []

                for y in range (0, columns.get_columns_total()):
                    headers.append(columns.json[y]["name"])

                logger.add_log_entry("Writing headers: " + str([headers]))
                writer.writerows([headers])

                values = []

                logger.add_log_entry("Generating values from: " + str(columns.json))
                for z in range (1, int(rows) + 1):
                    for x in range (0, columns.get_columns_total()):
                        values.append(get_values(columns.json[x]["value"], int(rownumber) + z))

                    writer.writerows([values])

                    values = []

        elif settings.fileformat == "xls":
            book = xlwt.Workbook()
            sheetname = (settings.sheetname if settings.sheetname != "" else "sheet")
            sheet = book.add_sheet(sheetname)

            for y in range (0, columns.get_columns_total()):
                sheet.write(0, y, columns.json[y]["name"])

            for z in range (1, int(rows) + 1):
                for x in range (0, columns.get_columns_total()):
                    sheet.write(z, x, get_values(columns.json[x]["value"], int(rownumber) + z))

            logger.add_log_entry("Writing xls file.")
            book.save(file)

        if settings.compress == "y":
            compress_file(file)
            message = "Took %.2f seconds" % (time.time() - starttime) + " to generate " + "{0:,}".format(int(rows)) + " rows and compress '" + file + "." + settings.compresstype.replace("-",".") + "'..."
        else:
            message = "Took %.2f seconds" % (time.time() - starttime) + " to generate " + "{0:,}".format(int(rows)) + " rows in '" + file + "'..."

        logger.add_log_entry(message, True)
        menu("\n" + message + "\n")
    except ValueError as err:
        logger.add_log_entry("ERROR - Invalid value specified for column " + str(currentcolumn) + " - " + str(columns.json[currentcolumn - 1]) +", took %.2f seconds before failing." % (time.time() - starttime), True)
        
        os.remove(file)
        logger.add_log_entry("Deleting file '" + file + "'...", True)

        menu("\nAn error occurred: Invalid value specified for column " + str(currentcolumn) + " - " + str(columns.json[currentcolumn - 1]) + "\nTook %.2f seconds before failing.\n" % (time.time() - starttime)) 
    except FileNotFoundError as err:
        settings.foldername = file[0:file.rfind("/")]
        settings.filename = settings.filename[settings.filename.rfind("/") + 1:len(settings.filename)]

        create_file()
    except Exception as err:
        logger.add_log_entry("ERROR - " + str(err) + "\nTook %.2f seconds before failing." % (time.time() - starttime), True)
        
        os.remove(file)
        logger.add_log_entry("Deleting file '" + file + "'...", True)
        
        menu("\nAn error occurred: " + str(err) + "\nTook %.2f seconds before failing.\n" % (time.time() - starttime)) 

def compress_file(file): # compress the generated file, if compression is enabled
    try:
        logger.add_log_entry("Compressing generated file...")
        print("\nCompressing generated file...")

        with open(file, 'rb') as currentfile:
            if settings.compresstype == "gz":
                with gzip.open(file + '.gz', 'wb') as compressedfile:
                    shutil.copyfileobj(currentfile, compressedfile)
            elif settings.compresstype == "zip":
                with zipfile.ZipFile(file + '.zip', 'w') as compressedfile:
                    compressedfile.write(file)
            elif settings.compresstype == "tar-gz":
                with tarfile.open(file + '.tar.gz', 'w:gz') as compressedfile:
                    compressedfile.add(file)
            elif settings.compresstype == "tar-bz2":
                with tarfile.open(file + '.tar.bz2', 'w:bz2') as compressedfile:
                    compressedfile.add(file)

        os.remove(file)
    except Exception as err:
        logger.add_log_entry("ERROR - " + str(err) + "\n", True)
        menu("\nAn error occurred during compression: " + str(err) + "\n")

def menu(notification = ""): # main menu, first thing the user will see
    clear()

    settings.update_values()

    filename = settings.filename 
    columnfile = settings.columnfile

    if (settings.foldername != ""):
        if settings.filename != "":
            filename = settings.foldername + "/" + settings.filename + ("." + settings.fileformat if settings.fileformat != "" else ".csv") + ("." + settings.compresstype.replace("-",".") if settings.compress == "y" else "")
        else:
            filename = settings.foldername + "/<file name not specified>"

    if (settings.columnfolder != ""):
        columnfile = settings.columnfolder + "/" + settings.columnfile

    columns.get_columns()
    valuelist.reset_index()

    print("Dummy data generator " + version + "\nAndrew H 2018\n\nCurrent file name: " + filename + "\nCurrent column file: " + columnfile + "\n" + ("Logging enabled\n" if settings.log == "y" else "") + notification)

    print("1. Generate file")
    print("2. View example row")
    print("3. Add and edit columns")
    print("4. View column files")
    print("5. Settings")
    print("q. Quit")

    option = input("\nEnter option: ")

    if option == "1":
        create_file()
    elif option == "2":
        get_demo_rows()
    elif option == "3":
        view_columns()
    elif option == "4":
        view_column_files()
    elif option == "5":
        view_settings()
    elif option == "q":
        exit()
    else:
        menu("\nInvalid option...\n")

version = "v0.8.0-" + str(subprocess.check_output(["git", "rev-parse", "HEAD"]).decode('ascii').strip())[:7]

settings.update_settings_file()
menu()