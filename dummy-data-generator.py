#! coding: utf-8
from PIL import Image
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
        self.imageformats = ["png", "jpg", "ico"]
        self.dataformats = ["xls", "csv"]
        self.defaultsettings = [
            {"section":0, "index":1, "key":"filename", "desc": "Default name of files generated", "value": "data"},
            {"section":0, "index":6, "key":"fileformat", "desc":"The format of the file generated", "value":"csv", "acceptedvalues":["csv","xls","png","jpg","ico"]},
            {"section":0, "index":2, "key":"foldername", "desc":"The name of folder where generated files are located (remove the folder name to skip folder creation)", "value":"generated-data"},
            {"section":0, "index":3, "key":"columnfile", "desc":"The name of the json file where the columns are stored (will create the file if not present)", "value":"columns.json"},
            {"section":0, "index":4, "key":"columnfolder", "desc":"The name of the folder where the columns are stored (remove the folder name to skip folder creation)", "value":"columns"},
            {"section":0, "index":24, "key":"presetfile", "desc":"The name of the preset file", "value":""},
            {"section":0, "index":25, "key":"presetfolder", "desc":"The folder where preset files are stored", "value":"presets"},
            {"section":0, "index":13, "key":"sheetname", "desc":"The name of the sheet generated in xls files (defaults to 'sheet' if blank)", "value":""},
            {"section":1, "index":5, "key":"compress", "desc":"Toggle to compress the file after generation y/n", "value":"n", "acceptedvalues":["y","n"]},
            {"section":1, "index":12, "key":"compresstype", "desc":"The type of compression used, if compression is enabled", "value":"gz", "acceptedvalues":["gz", "zip", "tar-gz", "tar-bz2"]},            
            {"section":2, "index":7, "key":"numberofrows", "desc":"The number of rows to generate (will ask at time of generation if blank)", "value":""},                    
            {"section":2, "index":8, "key":"rownumber", "desc":"The index where the script starts from (not inclusive, counts will start at value + 1)", "value":"0"},
            {"section":2, "index":9, "key":"min", "desc":"The minimum value generated with the '?' symbol", "value":"1"},
            {"section":2, "index":10, "key":"max", "desc":"The maximum value generated with the '?' symbol", "value":"1000000"},
            {"section":3, "index":14, "key":"imagemode", "desc":"The way the image is generated", "value":"random", "acceptedvalues":["random","single","row","grid"]}, 
            {"section":3, "index":15, "key":"imageheight", "desc":"The height of the generated image", "value":"100"}, 
            {"section":3, "index":16, "key":"imagewidth", "desc":"The width of the generated image", "value":"100"}, 
            {"section":3, "index":23, "key":"rowheight", "desc":"The pixel height of rows generated in 'row' mode", "value":"1"}, 
            {"section":3, "index":17, "key":"rmin", "desc":"The minimum value for random red intensity", "value":"0"}, 
            {"section":3, "index":18, "key":"rmax", "desc":"The maximum value for random red intensity", "value":"255"},
            {"section":3, "index":19, "key":"gmin", "desc":"The minimum value for random green intensity", "value":"0"}, 
            {"section":3, "index":20, "key":"gmax", "desc":"The maximum value for random green intensity", "value":"255"}, 
            {"section":3, "index":21, "key":"bmin", "desc":"The minimum value for random blue intensity", "value":"0"}, 
            {"section":3, "index":22, "key":"bmax", "desc":"The maximum value for random blue intensity", "value":"255"},
            {"section":3, "index":26, "key":"gridheight", "desc":"The vertical distance between grid lines", "value":"20"},
            {"section":3, "index":27, "key":"gridwidth", "desc":"The horizontal distance between grid lines", "value":"20"},
            {"section":4, "index":11, "key":"logging", "desc":"Enable logging of various events throughout generation (can affect performance) y/n", "value":"n", "acceptedvalues":["y","n"]}
        ]
        self.update_values()

    def update_values(self): # update attribute values
        self.json = self.get_settings()
        self.filename = self.get_setting_value("filename")
        self.foldername = self.get_setting_value("foldername")
        self.columnfile = self.get_setting_value("columnfile")
        self.columnfolder = self.get_setting_value("columnfolder")
        self.presetfile = self.get_setting_value("presetfile")
        self.presetfolder =self.get_setting_value("presetfolder")
        self.compress = self.get_setting_value("compress")
        self.compresstype = self.get_setting_value("compresstype")
        self.fileformat = self.get_setting_value("fileformat")
        self.sheetname = self.get_setting_value("sheetname")
        self.numberofrows = self.get_setting_value("numberofrows")
        self.rownumber = self.get_setting_value("rownumber")
        self.min = self.get_setting_value("min")
        self.max = self.get_setting_value("max")
        self.imagemode = self.get_setting_value("imagemode")
        self.imageheight = self.get_setting_value("imageheight")
        self.imagewidth = self.get_setting_value("imagewidth")
        self.rowheight = self.get_setting_value("rowheight")
        self.rmin = self.get_setting_value("rmin")
        self.rmax = self.get_setting_value("rmax")
        self.gmin = self.get_setting_value("gmin")
        self.gmax = self.get_setting_value("gmax")
        self.bmin = self.get_setting_value("bmin")
        self.bmax = self.get_setting_value("bmax")        
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

class Presets():
    def get_presets(self): # gets the columns from the columns json file, if the columns json file is not present, this will create the file
        self.jsonfilename = settings.presetfile

        if settings.presetfolder != "":
            if os.path.exists(settings.presetfolder + "/") == False:
                os.makedirs(settings.presetfolder + "/")

            self.jsonfilename = settings.presetfolder + "/" + settings.presetfile

        if settings.presetfile != "":

            if os.path.exists(self.jsonfilename) == False:
                with open(self.jsonfilename, "w") as jsonfile:
                    data = []
                    for x in range(0, len(settings.json)):
                        if settings.json[x]["key"] != "presetfile" and settings.json[x]["key"] != "presetfolder" and settings.json[x]["key"] != "logging":
                            data.append({"name": settings.json[x]["key"], "value": ""})
                    jsonfile.write(json.dumps(data, indent=4))

            with open(self.jsonfilename) as jsonfile:
                data = json.load(jsonfile)

            self.json = data

            self.apply_preset()

    def update_preset(self): # saves all changes to the column in the columns json file
        with open(self.jsonfilename, "w") as jsonfile:
            jsonfile.write(json.dumps(self.json, indent=4))

        self.get_presets()

    def apply_preset(self):
        for presetsetting in self.json:
            if presetsetting["value"] != "":
                setattr(settings, presetsetting["name"], presetsetting["value"])

presets = Presets()

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

    def create_column(self, name, value):
        self.json.append({"name":name, "value":value})

        self.update_column_data()

        notification = "New column '" + self.json[int(self.get_columns_total() - 1)]["name"] + "' added!"
        return notification

    def generate_columns(self, name, value):
        currentindex = 0
        currentdate = datetime.date.today()
        datestring = ""
        daycode = 0
        multipledates = False
        tempdatecount = ""
        datecount = 1
        currentdatecount = 0
        readformat = False
        formatstring = "%d/%m/%y"

        while True:
            currentindex = currentindex + 1

            if name[currentindex] == "}":

                if tempdatecount != "":
                    datecount = int(tempdatecount)

                if datestring.lower() == "monday":
                    daycode = 0
                elif datestring.lower() == "tuesday":
                    daycode = 1
                elif datestring.lower() == "wednesday":
                    daycode = 2
                elif datestring.lower() == "thursday":
                    daycode = 3
                elif datestring.lower() == "friday":
                    daycode = 4
                elif datestring.lower() == "saturday":
                    daycode = 5
                elif datestring.lower() == "sunday":
                    daycode = 6
                elif datestring.lower() == "day":
                    daycode = datetime.date.today().weekday()
                else:
                    notification = "Invalid day specified."
                    return notification
                    break

                logger.add_log_entry("Datestring is " + datestring + ". Daycode is " + str(daycode) + ". Current date is " + str(currentdate) + ".", True)

                while currentdatecount != datecount:
                    if currentdate.weekday() != daycode and datestring != "day":
                        daysahead = daycode - currentdate.weekday()

                        if daysahead <= 0: # Target day already happened this week
                            daysahead += 7

                        currentdate = currentdate + datetime.timedelta(daysahead)
                        self.json.append({"name":currentdate.strftime(formatstring), "value":value})
                    else:
                        if datestring.lower() != "day":
                            currentdate = currentdate + datetime.timedelta(7)
                        else:
                            currentdate = currentdate + datetime.timedelta(1)

                        self.json.append({"name":currentdate.strftime(formatstring), "value":value})
            
                    currentdatecount += 1
                break

            else:
                if name[currentindex] == "#":
                    readformat = False
                    multipledates = True
                elif name[currentindex] == "!":
                    multipledates = False
                    readformat = True
                    formatstring = ""          
                else:
                    if multipledates:
                        tempdatecount += name[currentindex]
                    elif readformat:
                        formatstring += name[currentindex]  
                    else:
                        datestring = datestring + name[currentindex]

        self.update_column_data()
        notification = "New column '" + self.json[int(self.get_columns_total() - 1)]["name"] + "' added!"
        return notification

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

class MultiValue():
    def __init__(self):
        self.valuelists = {}
        self.valueliststates = {}

    def add_list(self, key):
        if key not in self.valuelists:
            self.valuelists[key] = ValueList()
            self.valueliststates[key] = ""

    def check_list(self, key):
        if key not in self.valuelists:
            return False
        else:
            return True

    def reset_indexes(self):
        for valuelist in self.valuelists:
            self.valuelists[valuelist].reset_index()

valuedict = MultiValue()

class ImageGenerator():
    def __init__(self):
        self.pixels = []
        self.red = 0
        self.green = 0
        self.blue = 0

    def generate_grid_image(self):
        self.red = int(settings.rmax)
        self.green = int(settings.gmax)
        self.blue = int(settings.bmax)

        for x in range (0, int(settings.imageheight)): # rows

            for y in range (0, int(settings.imagewidth)): # columns
                if x % (int(settings.gridheight) + 1) == 0: # if row mod grid height
                    self.pixels.append((self.red, self.green, self.blue))                               
                else:
                    if y % (int(settings.gridwidth) + 1) == 0:
                        self.pixels.append((self.red, self.green, self.blue))
                    else:
                        self.pixels.append((255, 255, 255))

    def generate_single_image(self):
        self.red = int(settings.rmax)
        self.green = int(settings.gmax)
        self.blue = int(settings.bmax)

        for x in range (0, int(settings.imageheight)):
            for y in range (0, int(settings.imagewidth)):
                self.pixels.append((self.red, self.green, self.blue))

    def generate_row_image(self):
        for x in range (0, int(settings.imageheight)):
            if x % int(settings.rowheight) == 0:
                self.red = random.randint(int(settings.rmin), int(settings.rmax))
                self.green = random.randint(int(settings.gmin), int(settings.gmax))
                self.blue = random.randint(int(settings.bmin), int(settings.bmax))

            for y in range (0, int(settings.imagewidth)):
                self.pixels.append((self.red, self.green, self.blue))

    def generate_random_image(self):
        for x in range (0, int(settings.imageheight)):
            for y in range (0, int(settings.imagewidth)):
                    self.pixels.append(
                        (
                            (random.randint(int(settings.rmin), int(settings.rmax))),
                            (random.randint(int(settings.gmin), int(settings.gmax))),
                            (random.randint(int(settings.bmin), int(settings.bmax)))
                        )
                    )
                  
    def generate_image(self, file):
        img = Image.new('RGB', (int(settings.imagewidth), int(settings.imageheight)))

        if settings.imagemode == "single":
            self.generate_single_image()
        elif settings.imagemode == "row":
            self.generate_row_image()
        elif settings.imagemode == "random":
            self.generate_random_image()
        elif settings.imagemode == "grid":
            self.generate_grid_image()

        logger.add_log_entry("RGB values generated: " + str(self.pixels[:10]) + (", " + str((len(self.pixels) - 10)) + " more RGB values." if int(len(self.pixels)) > 10 else ""), True)

        img.putdata(self.pixels)
        img.save(file)

        self.pixels = []
        self.red = 0
        self.green = 0
        self.blue = 0

imageGenerator = ImageGenerator()

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
        print("2. File compression settings")
        print("3. Data generation settings")
        print("4. Image generation settings")  
        print("5. Logging settings")  

        option = input(notification + "\nEnter the section number (1 to 3) to view the settings for that section, or:\nq. Quit\n\nOption:")

        if option == "q":
            menu()
        elif option.isdigit():
            if int(option) <= 5:
                view_setting_group(int(option) - 1)
            elif int(option) > 5:
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
                view_files_list("", "settings")
            if settings.json[selectedindex]["key"] == "presetfile":
                view_files_list("", "settings", "preset")
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

def view_files_list(notification = "", prevstate = "menu", mode = "column"): # displays the column files in the terminal, and allows the user to select a file to use
    option = ""
    while option != "q":
        clear()

        subnotif = "\n"

        if mode == "column":
            print("The following column files are located in the '" + settings.columnfolder + "' folder: \n\nCurrent columns file: " + settings.columnfile + "\n")

            if settings.columnfolder == "":
                settings.columnfolder = "."

            files = os.listdir(settings.columnfolder)
        elif mode == "preset":
            print("The following preset files are located in the '" + settings.presetfolder + "' folder: \n" + ("\nCurrent preset file: " + settings.presetfile + "\n" if settings.presetfile != "" else ""))

            if settings.presetfolder == "":
                settings.presetfolder = "."

            files = os.listdir(settings.presetfolder)

        fileslist = []

        if mode == "preset":
            fileslist.append("<None>")

        for names in files:
            if names.endswith(".json"):
                fileslist.append(names)
        
        for y in range (0, len(fileslist)):
            print(str(y + 1) + ". " + fileslist[y])

        if mode == "column":
            if len(fileslist) == 1:
                option = input(notification + "\n+. Add a column file\nx. Delete a column file\nd. Duplicate the current column file\nq. Quit\n\nOption:")
            else:
                option = input(notification + "\nEnter a file number (1 to " + str(len(fileslist)) + ") to select the column for use, or:\n+. Add a column file\nx. Delete a column file\nd. Duplicate the current column file\nq. Quit\n\nOption:")
        elif mode == "preset":
            if len(fileslist) == 1:
                option = input(notification + "\n+. Add a preset file\nx. Delete a preset file\nd. Duplicate the current preset file\nq. Quit\n\nOption:")
            else:
                option = input(notification + "\nEnter a file number (1 to " + str(len(fileslist)) + ") to select the preset for use, or:\n+. Add a preset file\nx. Delete a preset file\nd. Duplicate the current preset file\nq. Quit\n\nOption:")

        if option == "q":
            if prevstate == "menu":
                menu()
            elif prevstate == "settings":
                view_settings()
            else:
                menu()
        elif option == "+":
            if mode == "column":
                newfilename = input("\nEnter the name of the new column file (excluding file extension): ")

                for y in range (0, len(settings.json)):
                    if settings.json[y]["key"] == "columnfile":
                        settings.json[y]["value"] = newfilename + ".json"

                settings.update_settings()
                columns.get_columns()
                notification = "\nCreated and selected new column file " + newfilename + ".json...\n"
            elif mode == "preset":
                newfilename = input("\nEnter the name of the new preset file (excluding file extension): ")

                for y in range (0, len(settings.json)):
                    if settings.json[y]["key"] == "presetfile":
                        settings.json[y]["value"] = newfilename + ".json"

                settings.update_settings()
                presets.get_presets()
                notification = "\nCreated and selected new preset file " + newfilename + ".json...\n"
        elif option == "x" and len(fileslist) > 1:
            deletefilename = input("\nEnter the name of the file to be deleted (excluding file extension): ") + ".json"

            if mode == "column":
                deletepath = settings.columnfolder + "/" + deletefilename
            elif mode == "preset":
                deletepath = settings.presetfolder + "/" + deletefilename     
                               
            if os.path.exists(deletepath):
                os.remove(deletepath)

                if mode == "column":
                    if settings.columnfile == deletefilename:
                        for y in range (0, len(settings.json)):
                            if settings.json[y]["key"] == "columnfile":
                                settings.json[y]["value"] = "columns.json"
                                settings.update_settings()
                                subnotif = "Reverted column file to 'columns.json' as the deleted file was the selected columns file!\n"

                    columns.get_columns()
                    notification = "\nDeleted column file " + deletefilename + "... " + subnotif

                elif mode == "preset":
                    if settings.presetfile == deletefilename:
                        for y in range (0, len(settings.json)):
                            if settings.json[y]["key"] == "presetfile":
                                settings.json[y]["value"] = ""
                                settings.update_settings()
                                subnotif = "No preset file is selected as the deleted file was the selected preset file!\n"

                    presets.get_presets()
                    notification = "\nDeleted preset file " + deletefilename + "... " + subnotif                        
            else:
                notification = "\nFile " + deletefilename + " does not exist... " + subnotif
        elif option == "x" and len(fileslist) <= 1:
            if mode == "column":
                notification = "\nCannot delete files when only one exists...\n"
            elif mode == "preset":
                notification = "\nNo files to delete...\n"                
        elif option == "d":
            originallocation = ""
            duplicatelocation = ""
            duplicatename = ""

            if mode == "preset" and settings.presetfile == "":
                notification = "\nNo preset file selected.\n"
            else:
                if input("\nAre you sure you want to duplicate the currently selected " +  ("column" if mode == "column" else "preset") + " file? y/n: ") == "y":
                    if mode == "column":
                            duplicatename = input("Enter name for duplicated file (do not include extension): ") + ".json"

                            originallocation = settings.columnfolder + "/" + settings.columnfile
                            duplicatelocation = settings.columnfolder + "/" + duplicatename
                    elif mode == "preset":
                            duplicatename = input("Enter name for duplicated file (do not include extension): ") + ".json"

                            originallocation = settings.presetfolder + "/" + settings.presetfile
                            duplicatelocation = settings.presetfolder + "/" + duplicatename

                    try:
                        shutil.copy(originallocation, duplicatelocation)

                        for y in range (0, len(settings.json)):
                            if mode == "column" and settings.json[y]["key"] == "columnfile":
                                settings.json[y]["value"] = duplicatename
                                settings.update_settings()
                                notification = "\nSelected the new duplicate column file, " + duplicatename + "...\n"

                            elif mode == "preset" and settings.json[y]["key"] == "presetfile":
                                settings.json[y]["value"] = duplicatename
                                settings.update_settings()
                                notification = "\nSelected the new duplicate preset file, " + duplicatename + "...\n"

                    except shutil.SameFileError:
                        notification = "\nColumn file with the name '" + duplicatename +"' already exists.\n"
                    except Exception:
                        notification = "\nAn unknown error occurred when duplicating the file.\n"
        elif option.isdigit():
            if int(option) <= len(fileslist):
                for y in range (0, len(settings.json)):
                    if mode == "column" and settings.json[y]["key"] == "columnfile":
                        settings.json[y]["value"] = fileslist[int(option) - 1]
                        settings.update_settings()
                        notification = "\nSelected column file " + option + ", " + fileslist[int(option) - 1] + "...\n"

                    elif mode == "preset" and settings.json[y]["key"] == "presetfile":
                        if fileslist[int(option) - 1] == "<None>":
                            settings.json[y]["value"] = ""
                        else:
                            settings.json[y]["value"] = fileslist[int(option) - 1]

                        settings.update_settings()
                        notification = "\nSelected preset file " + option + ", " + fileslist[int(option) - 1] + "...\n"

            elif int(option) > len(fileslist):
                notification = "\nNo file " + option + "...\n"
        else:
            if len(fileslist) <= 1:
                notification = "\nThe only available file has already been selected...\n"
            else:
                notification = "\nInvalid column file or option...\n"

def view_json(notification = "", mode = "column"): # displays the columns in the terminal, and allows the user to select columns
    if mode == "preset" and settings.presetfile == "":
        menu("\nNo preset file selected...\n")
    else:
        option = ""
        while option != "q":
            clear()

            count = 0

            if mode == "column":
                print("The following columns and values are currently defined:\n")

                for y in range (1, columns.get_columns_total() + 1):
                    print(str(y) + ". " + columns.json[y - 1]["name"] + " - " + columns.json[y - 1]["value"])
                    count = y

                option = input("\n" + notification + "\nEnter a number (1 to " + str(columns.get_columns_total()) + ") to edit the column, or:\n+. Add a column\nx. Delete a column\nq. Quit\n\nOption:")

            elif mode == "preset":
                print("The following presets are currently defined:\n")

                for y in range (1, len(presets.json) + 1):
                    print(str(y) + ". " + presets.json[y - 1]["name"] + " - " + (presets.json[y - 1]["value"] if presets.json[y - 1]["value"] != "" else "<No value>"))
                    count = y

                option = input("\n" + notification + "\nEnter a number (1 to " + str(len(presets.json)) + ") to edit the preset, or:\nq. Quit\n\nOption:")

            if option == "q":
                menu()
            elif option.isdigit():
                if int(option) <= count:
                    if mode == "column":
                        view_one_column(int(option))
                    elif mode == "preset":
                        acceptedvalues = []

                        for values in settings.json:
                            if values["key"] == presets.json[int(option) - 1]["name"] and "acceptedvalues" in values:
                                acceptedvalues = values["acceptedvalues"]

                        inputvalue = input("\nEnter a new preset setting value for setting number " + str(option) + ": ")
                        
                        if len(acceptedvalues) != 0 and inputvalue not in acceptedvalues and inputvalue != "":
                            notification = "Value is not valid for current setting, valid values are " + str(acceptedvalues) + ".\n"
                        else:
                            presets.json[int(option) - 1]["value"] = inputvalue
                            notification = "Preset setting updated.\n"                            

                        presets.update_preset()
                elif int(option) > count:
                    if mode == "column":
                        notification = "No column " + option + "...\n"
                    elif mode == "preset":
                        notification = "No preset " + option + "...\n"
            elif mode == "column" and option == "+":
                columnname = input("\nEnter the name of the new column: ")
                columnvalue = input("Enter the value of the new column: ")

                if columnname[0] == "{": 
                    notification = columns.generate_columns(columnname, columnvalue) + "\n"
                else:
                    notification = columns.create_column(columnname, columnvalue) + "\n"

                logger.add_log_entry(notification, True)
            elif mode == "column" and option == "x":
                index = int(input("\nEnter the column number you want to delete: ")) - 1
                confirm = input("Are you sure you want to delete column " + str(index + 1) + "? y/n\n")

                if confirm == "y":
                    notification = "Column '" + columns.json[index]["name"] + "' deleted!\n"
                    logger.add_log_entry("Column '" + columns.json[index]["name"] + "' deleted!", True)

                    columns.json.pop(index)
                    columns.update_column_data()
                else:
                    notification = "Column NOT deleted!\n"
            else:
                notification = "Invalid " + mode + " or option...\n"

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
            view_json()
        elif option == "1":
            columns.json[index - 1]["name"] = input("\nEnter new column name:")
            columns.update_column_data()
            view_json("\nColumn name for column " + str(index) + " updated!\n")
        elif option == "2":
            print("\nView the documentation for the possible column values and placeholders that can be used.\n")
            columns.json[index - 1]["value"] = input("Enter new column value:")
            columns.update_column_data()

            message = "Column value for column " + str(index) + " updated!"
            logger.add_log_entry(message, True)
            view_json("\n" + message + "\n")
        elif option == "x":
            confirm = input("\nAre you sure you want to delete column " + str(index) + "? y/n\n")

            if confirm == "y":
                message = "Column '" + columns.json[index - 1]["name"] + "' deleted!"

                columns.json.pop(index - 1)
                columns.update_column_data()

                logger.add_log_entry(message, True)
                view_json("\n" + message + "\n")
            else:
                view_json("\nColumn '" + columns.json[index - 1]["name"] + "' NOT deleted!\n")
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
            if valuedict.check_list(value) == False:
                valuedict.add_list(value)
                valuedict.valueliststates[value] = "ordered"
                values = []
                tempstring = ""
                randomlist = False
                orderedlist = True
                innervalue = False
                multivalue = False
                multivaluenumber = ""
                countvalue = False

                while True:
                    currentindex = currentindex + 1

                    if value[currentindex] == "|" or (value[currentindex] == "," and innervalue == False):
                        if multivalue == False:
                            values.append(tempstring)
                        elif multivalue == True:
                            for count in range (1, int(multivaluenumber) + 1):
                                values.append(tempstring)
                            multivalue = False
                            multivaluenumber = ""

                        tempstring = ""

                        if value[currentindex] == "|":
                            randomlist = True
                            orderedlist = False
                        elif value[currentindex] == ",":
                            randomlist = False
                            orderedlist = True                        

                    elif value[currentindex] == "#":
                        multivalue = True

                    elif value[currentindex] == "+":
                        countvalue = True

                    elif value[currentindex] == "]":
                        if multivalue == False:
                            if countvalue:
                                for count in range (1, int(tempstring) + 1):
                                    values.append(str(count))
                            else:
                                values.append(tempstring)
                        elif multivalue == True:
                            if countvalue:
                                for count in range (1, int(tempstring) + 1):
                                    for innercount in range (1, int(multivaluenumber) + 1):
                                        values.append(str(count))
                            else:
                                for count in range (1, int(multivaluenumber) + 1):
                                    values.append(tempstring)
                            multivalue = False
                            multivaluenumber = ""

                        valuedict.valuelists[value].set_list(values)
                        #logger.add_log_entry(str(valuedict.valuelists[value].list), True)
                        values = []

                        if randomlist:
                            valuedict.valueliststates[value] = "random"
                            output = output + valuedict.valuelists[value].get_random_list_value()
                        elif orderedlist:
                            valuedict.valueliststates[value] = "ordered"
                            output = output + valuedict.valuelists[value].get_next_list_value()

                        break
                    
                    else:
                        if multivalue == True:
                            multivaluenumber = multivaluenumber + value[currentindex]                       
                        else:
                            tempstring = tempstring + value[currentindex]

                        if value[currentindex] == "(":
                            innervalue = True
                        if value[currentindex] == ")":
                            tempstring = get_values(tempstring, rownumber)
                            innervalue = False
            elif valuedict.check_list(value):
                if valuedict.valueliststates[value] == "random":
                    output = output + valuedict.valuelists[value].get_random_list_value()
                elif valuedict.valueliststates[value] == "ordered":
                    output = output + valuedict.valuelists[value].get_next_list_value()

                while True:
                    if value[currentindex] != "]":
                        currentindex = currentindex + 1
                    else:
                        break

        elif value[currentindex] == "+":
            output = output + str(rownumber)
        elif value[currentindex] == "?":
            output = output + str(random.randint(int(settings.min), int(settings.max)))
        else:
            output = output + value[currentindex]
        currentindex = currentindex + 1
    return output

def get_demo_rows(notification = "", rownumber = None): # generates and prints one row to the terminal, using the currently selected columns file
    try:
        clear()
        currentcolumn = 0

        maxheaderlength = 0
        maxvaluelength = 0
        maxvaluecolumnlength = 0

        if rownumber == None:
            rownumber = int(settings.rownumber)

        print("The following is an example of what can be generated for row " + str(rownumber + 1) +":\n")

        headers = ["COLUMN NAME", ""]
        
        for y in range (0, columns.get_columns_total()):
            headers.append(columns.json[y]["name"])

        values = ["GENERATED VALUE", ""]

        for z in range (1, 2):
            for x in range (0, columns.get_columns_total()):
                values.append(get_values(columns.json[x]["value"], int(rownumber) + z))

                currentcolumn += 1

        colvalues = ["COLUMN VALUE", ""]

        for x in range (0, columns.get_columns_total()):
            colvalues.append(columns.json[x]["value"])

        for z in range (0, len(headers)):
            if len(headers[z]) > int(maxheaderlength):
                maxheaderlength = len(headers[z])

            if len(values[z]) > int(maxvaluelength):
                maxvaluelength = len(values[z])

            if len(colvalues[z]) > int(maxvaluecolumnlength):
                maxvaluecolumnlength = len(colvalues[z])

        border = ""
        for bordercount in range (0, maxheaderlength + 2):
            border += "-"

        headers[1] = border

        border = ""
        for bordercount in range (0, maxvaluelength + 4):
            border += "-"

        values[1] = border

        border = ""
        for bordercount in range (0, maxvaluecolumnlength + 4):
            border += "-"

        colvalues[1] = border

        for z in range (0, len(headers)):
            if len(headers[z]) < maxheaderlength:
                while len(headers[z]) < maxheaderlength:
                    headers[z] = headers[z] + " "

            if len(values[z]) < maxvaluelength:
                while len(values[z]) < maxvaluelength:
                    values[z] = values[z] + " "

            if len(colvalues[z]) < maxvaluecolumnlength:
                while len(colvalues[z]) < maxvaluecolumnlength:
                    colvalues[z] = colvalues[z] + " "

            if z == 1:
                print(headers[z] + "+" + values[z] + "+" + colvalues[z])
            else:           
                print(headers[z] + "  |  " + values[z] + "  |  " + colvalues[z])

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
    except ValueError as err:
        logger.add_log_entry(str(err), True)
        menu("\nAn error occurred during generation of example data: Invalid value specified for column " + str(currentcolumn + 1) + " - " + str(columns.json[currentcolumn]) + "\n")     

def create_file(notification = ""): # creates and writes the file
    try:
        clear()

        if settings.fileformat in settings.dataformats:
            if settings.numberofrows == "":
                settings.numberofrows = input(notification + "Enter the number of rows to generate (or enter 'q' or 'b' to go back to the menu): ")
                clear()

            if settings.numberofrows == "q" or settings.numberofrows == "b":
                menu()
            elif settings.numberofrows.isdigit() == False and (settings.numberofrows != 'q' or settings.numberofrows != 'b'):
                settings.numberofrows = ""
                create_file("Please enter a number...\n\n")

        file = get_filename()
        folder = settings.foldername

        if folder != "":
            if os.path.exists(folder + "/") == False:
                os.makedirs(folder + "/")

        timetaken = write_file(file)

        if settings.compress == "y":
            compress_file(file)
            if settings.fileformat in settings.imageformats:
                message = ("Took %.4f seconds" if timetaken < 0.01 else "Took %.2f seconds") % timetaken + " to generate and compress '" + file + "." + settings.compresstype.replace("-",".") + "'..."                
            else:
                message = ("Took %.4f seconds" if timetaken < 0.01 else "Took %.2f seconds") % timetaken + " to generate " + "{0:,}".format(int(settings.numberofrows)) + " rows and compress '" + file + "." + settings.compresstype.replace("-",".") + "'..."
        else:
            if settings.fileformat in settings.imageformats:
                message = ("Took %.4f seconds" if timetaken < 0.01 else "Took %.2f seconds") % timetaken + " to generate '" + file + "'..."                
            else:
                message = ("Took %.4f seconds" if timetaken < 0.01 else "Took %.2f seconds") % timetaken + " to generate " + "{0:,}".format(int(settings.numberofrows)) + " rows in '" + file + "'..."

        logger.add_log_entry(message, True)
        menu("\n" + message + "\n")

    except FileNotFoundError as err:
        settings.foldername = file[0:file.rfind("/")]
        settings.filename = settings.filename[settings.filename.rfind("/") + 1:len(settings.filename)]

        create_file()
    except Exception as err:
        logger.add_log_entry("ERROR - " + str(err))
        
        try:
            os.remove(file)
            logger.add_log_entry("Deleting file '" + file + "'...", True)
        except Exception:
            pass

        menu("\nAn error occurred during file creation: " + str(err) + "\n") 

def write_file(file):
    currentcolumn = 0
    try:
        logger.add_log_entry("Generating file...")
        print("Generating file...")

        starttime = time.time()

        if settings.fileformat == "csv":
            with open(file, 'w') as currentfile:
                writer = csv.writer(currentfile, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_ALL)
                
                headers = []

                for y in range (0, columns.get_columns_total()):
                    headers.append(columns.json[y]["name"])

                logger.add_log_entry("Writing headers: " + str([headers]))
                clear()
                print("Writing column headers...")
                writer.writerows([headers])

                values = []

                logger.add_log_entry("Generating values from: " + str(columns.json))
                for z in range (1, int(settings.numberofrows) + 1):
                    if (z % 100) == 0:
                        clear()
                        print("Generating values... \n" + str(z) + " rows out of " + settings.numberofrows + " generated.")
                    for x in range (0, columns.get_columns_total()):
                        values.append(get_values(columns.json[x]["value"], int(settings.rownumber) + z))
                        currentcolumn += 1

                    writer.writerows([values])

                    values = []

        elif settings.fileformat == "xls":
            book = xlwt.Workbook()
            sheetname = (settings.sheetname if settings.sheetname != "" else "sheet")
            sheet = book.add_sheet(sheetname)

            logger.add_log_entry("Writing headers into xls file.")
            clear()
            print("Writing column headers...")
            for y in range (0, columns.get_columns_total()):
                sheet.write(0, y, columns.json[y]["name"])

            logger.add_log_entry("Generating values from: " + str(columns.json))
            for z in range (1, int(settings.numberofrows) + 1):
                if (z % 100) == 0:
                    clear()
                    print("Generating values... \n" + str(z) + " rows out of " + settings.numberofrows + " generated.")
                for x in range (0, columns.get_columns_total()):
                    sheet.write(z, x, get_values(columns.json[x]["value"], int(settings.rownumber) + z))

            logger.add_log_entry("Writing xls file.")
            book.save(file)

        elif settings.fileformat in settings.imageformats:
            imageGenerator.generate_image(file)

        return (time.time() - starttime)
    
    except ValueError as err:
        try:
            logger.add_log_entry("Deleting file '" + file + "'...", True)
            os.remove(file)
        except Exception:
            pass

        if settings.fileformat not in settings.imageformats:
            logger.add_log_entry("ERROR - Invalid value specified for column " + str(currentcolumn + 1) + " - " + str(columns.json[currentcolumn]) +", took %.2f seconds before failing." % (time.time() - starttime), True)
            menu("\nAn error occurred during file generation: Invalid value specified for column " + str(currentcolumn + 1) + " - " + str(columns.json[currentcolumn]) + "\nTook %.2f seconds before failing.\n" % (time.time() - starttime))     
        else:
            logger.add_log_entry("ERROR - " + str(err) + ", took %.2f seconds before failing." % (time.time() - starttime), True)
            menu("\nAn error occurred during image generation: " + str(err) + "\nTook %.2f seconds before failing.\n" % (time.time() - starttime))

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
    presets.get_presets()

    if settings.presetfile != "":
        presetmodstring = ": "

        for presetsetting in presets.json:
            if presetsetting["value"] != "":
                presetmodstring += "\n - " + presetsetting["name"]

        if presetmodstring == ": ":
            presetmodstring += "<None>"

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
    valuedict.reset_indexes()

    print("Dummy data generator " + version + "\nAndrew H 2018\n" +
        ("\nCurrent preset file: " + settings.presetfolder + "/" + settings.presetfile + "\nThe selected preset file modifies the following settings" + presetmodstring if settings.presetfile != "" else "") +
        "\nCurrent file name: " + filename + 
        ("\nCurrent column file: " + columnfile if settings.fileformat not in settings.imageformats else "") +
        ("\nImage resolution: " + settings.imagewidth + " x " + settings.imageheight if settings.fileformat in settings.imageformats else "") + 
        ("\nImage generation mode: " + settings.imagemode if settings.fileformat in settings.imageformats else "") +
        ("\n - Red: (" + settings.rmin + "," + settings.rmax + "), Green: (" + settings.gmin + "," + settings.gmax + "), Blue: (" + settings.bmin + "," + settings.bmax + ")" if settings.fileformat in settings.imageformats and settings.imagemode == "random" else "" ) +
        ("\n - Red: " + settings.rmax + ", Green: " + settings.gmax + ", Blue: " + settings.bmax + "" if settings.fileformat in settings.imageformats and settings.imagemode == "single" else "" ) +
        ("\n - Red: (" + settings.rmin + "," + settings.rmax + "), Green: (" + settings.gmin + "," + settings.gmax + "), Blue: (" + settings.bmin + "," + settings.bmax + ")\n - Row height: " + settings.rowheight if settings.fileformat in settings.imageformats and settings.imagemode == "row" else "" ) +
        ("\nLogging enabled\n" if settings.log == "y" else "\n") + notification)

    print("1. Generate file")
    if settings.fileformat not in settings.imageformats:
        print("2. View example row")
        print("3. View column files")
        print("4. Add and edit columns")
    print("5. View preset files")
    print("6. Edit preset")
    print("7. Settings")
    print("q. Quit")

    option = input("\nEnter option: ")

    if option == "1":
        create_file()
    elif option == "2" and settings.fileformat in settings.dataformats:
        get_demo_rows()
    elif option == "3" and settings.fileformat in settings.dataformats:
        view_files_list()
    elif option == "4" and settings.fileformat in settings.dataformats:
        view_json()
    elif option == "5":
        view_files_list("", "menu", "preset")
    elif option == "6":
        view_json("", "preset")
    elif option == "7":
        view_settings()
    elif option == "q":
        exit()
    else:
        menu("\nInvalid option...\n")

clear()
print("Loading...")

version = "v0.9.0-" + str(subprocess.check_output(["git", "rev-parse", "HEAD"]).decode('ascii').strip())[:7]

settings.update_settings_file()
menu()