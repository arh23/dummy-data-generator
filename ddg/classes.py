from PIL import Image
import subprocess, csv, xlwt, random, time, json, os, sys, platform, datetime, gzip, zipfile, tarfile, shutil, math, traceback

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
            {"section":3, "index":28, "key":"gridbgmode", "desc":"The way the background of the image is generated", "value":"single", "acceptedvalues":["random","single","row"]},
            {"section":3, "index":29, "key":"gridbgred", "desc":"The maximum value for random red intensity (for grid image backgrounds)", "value":"255"},
            {"section":3, "index":30, "key":"gridbggreen", "desc":"The maximum value for random green intensity (for grid image backgrounds)", "value":"255"}, 
            {"section":3, "index":31, "key":"gridbgblue", "desc":"The maximum value for random blue intensity (for grid image backgrounds)", "value":"255"},
            {"section":3, "index":32, "key":"gridborders", "desc":"Enable the increase of image height and width to include the border edges of the grid", "value":"n", "acceptedvalues":["y","n"]},                                    
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
        self.gridheight = self.get_setting_value("gridheight")
        self.gridwidth = self.get_setting_value("gridwidth")
        self.gridbgmode = self.get_setting_value("gridbgmode")
        self.gridbgred = self.get_setting_value("gridbgred")   
        self.gridbggreen = self.get_setting_value("gridbggreen")
        self.gridbgblue = self.get_setting_value("gridbgblue")
        self.gridborders = self.get_setting_value("gridborders")                          
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

    def add_log_entry(self, value, write = False, addspace = True): # adds a new log entry
        now = datetime.datetime.now()
        if self.get_logging_state():
            self.log.append("[" + str('%02d' % now.hour) + ":" + str('%02d' % now.minute) + ":" + str('%02d' % now.second) + "] " + value)
            if write == True:
                self.write_log(addspace)

    def write_log(self, addspace = True): # writes the current log array into the log file and clears the log array
        now = datetime.datetime.now()
        logname = "logs/log-" + str('%02d' % now.day) + "-" + str('%02d' % now.month) + "-" + str('%02d' % now.year) + ".txt"

        if os.path.exists("logs/") == False:
            os.makedirs("logs/")

        with open(logname, 'a') as logfile:
            for x in range (0, len(self.log)):
                logfile.write(self.log[x] + "\n" if addspace == True else self.log[x])

        self.log = []

logger = Logger()

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

class Generator():

    def get_filename(self): # generate the name of the file, based on the current settings 'filename' value
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

    def get_values(self, value, rownumber): # reads the value for each column, and processes it into dummy data to add to the csv
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
                                tempstring = self.get_values(tempstring, rownumber)
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

    def create_file(self, notification = ""): # creates and writes the file
        try:
            file = self.get_filename()
            folder = settings.foldername

            if folder != "":
                if os.path.exists(folder + "/") == False:
                    os.makedirs(folder + "/")

            timetaken = self.write_file(file)

            if settings.compress == "y":
                self.compress_file(file)
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
            return "\n" + message + "\n"

        except FileNotFoundError as err:
            settings.foldername = file[0:file.rfind("/")]
            settings.filename = settings.filename[settings.filename.rfind("/") + 1:len(settings.filename)]

            self.create_file()
        except Exception as err:
            logger.add_log_entry("ERROR - " + str(err) + ":\n" + str(traceback.format_exc()), True, False)
            
            try:
                os.remove(file)
                logger.add_log_entry("Deleting file '" + file + "'...", True)
            except Exception:
                pass

            return "\nAn error occurred during file creation: " + "\n" + str(traceback.format_exc())


    def write_file(self, file):
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

                    print("Writing column headers...")
                    writer.writerows([headers])

                    values = []

                    logger.add_log_entry("Generating values from: " + str(columns.json))
                    for z in range (1, int(settings.numberofrows) + 1):
                        if (z % 100) == 0:
                            print("Generating values... \n" + str(z) + " rows out of " + settings.numberofrows + " generated.")
                        for x in range (0, columns.get_columns_total()):
                            values.append(self.get_values(columns.json[x]["value"], int(settings.rownumber) + z))
                            currentcolumn += 1

                        writer.writerows([values])

                        values = []

            elif settings.fileformat == "xls":
                book = xlwt.Workbook()
                sheetname = (settings.sheetname if settings.sheetname != "" else "sheet")
                sheet = book.add_sheet(sheetname)

                logger.add_log_entry("Writing headers into xls file.")

                print("Writing column headers...")
                for y in range (0, columns.get_columns_total()):
                    sheet.write(0, y, columns.json[y]["name"])

                logger.add_log_entry("Generating values from: " + str(columns.json))
                for z in range (1, int(settings.numberofrows) + 1):
                    if (z % 100) == 0:
                        print("Generating values... \n" + str(z) + " rows out of " + settings.numberofrows + " generated.")
                    for x in range (0, columns.get_columns_total()):
                        sheet.write(z, x, self.get_values(columns.json[x]["value"], int(settings.rownumber) + z))

                logger.add_log_entry("Writing xls file.")
                book.save(file)

            elif settings.fileformat in settings.imageformats:
                imagegenerator.generate_image(file)

            return (time.time() - starttime)
        
        except ValueError as err:
            try:
                logger.add_log_entry("Deleting file '" + file + "'...", True)
                os.remove(file)
            except Exception:
                pass

            if settings.fileformat not in settings.imageformats:
                logger.add_log_entry("ERROR - Invalid value specified for column " + str(currentcolumn + 1) + " - " + str(columns.json[currentcolumn]) +", took %.2f seconds before failing." % (time.time() - starttime), True)
                return "\nAn error occurred during file generation: Invalid value specified for column " + str(currentcolumn + 1) + " - " + str(columns.json[currentcolumn]) + "\nTook %.2f seconds before failing.\n" % (time.time() - starttime)   
            else:
                logger.add_log_entry("ERROR - " + str(err) + ", took %.2f seconds before failing." % (time.time() - starttime), True)
                return "\nAn error occurred during image generation: " + str(err) + "\nTook %.2f seconds before failing.\n" % (time.time() - starttime)

    def compress_file(self, file): # compress the generated file, if compression is enabled
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

generator = Generator()

class ImageGenerator():
    def __init__(self):
        self.pixels = []
        self.red = 0
        self.green = 0
        self.blue = 0

    def calculate_borders(self): # ensures the whole grid fits the image, so the borders of the image are grid lines
        gridlinesize = 1 # replace with setting variable when implemented
        modifyheight = True
        modifywidth = True

        multiplier = 0

        while modifyheight == True and multiplier < int(settings.imageheight): # determine if current image height can fit all the grid blocks
            multiplier += 1
            if (int(settings.gridheight) * multiplier) + (multiplier * gridlinesize) + gridlinesize == int(settings.imageheight):
                logger.add_log_entry("Current image height does not require modification. Grid block image height multiplier: " + str(multiplier), True)
                modifyheight = False

        multiplier = 0

        while modifywidth == True and multiplier < int(settings.imagewidth): # determine if current image width can fit all the grid blocks
            multiplier += 1
            if (int(settings.gridwidth) * multiplier) + (multiplier * gridlinesize) + gridlinesize == int(settings.imagewidth):
                logger.add_log_entry("Current image width does not require modification. Grid block image width multiplier: " + str(multiplier), True)
                modifywidth = False

        if modifyheight: # if current height is not suitable, calculate the next nearest suitable height based on number of grid blocks along the y axis of the image
            heightmultiplier = round(int(settings.imageheight) / int(settings.gridheight))
            calculatedheight = (int(settings.gridheight) * heightmultiplier) + (heightmultiplier * gridlinesize) + gridlinesize
            settings.imageheight = calculatedheight
            logger.add_log_entry("Image height is now " + str(settings.imageheight), True)

        if modifywidth: # if current width is not suitable, calculate the next nearest suitable width based on number of grid blocks along the x axis of the image
            widthmultiplier = round(int(settings.imagewidth) / int(settings.gridwidth))
            calculatedwidth = (int(settings.gridwidth) * widthmultiplier) + (widthmultiplier * gridlinesize) + gridlinesize
            settings.imagewidth = calculatedwidth
            logger.add_log_entry("Image width is now " + str(settings.imagewidth), True)


    def generate_grid_image(self):
        self.red = int(settings.rmax)
        self.green = int(settings.gmax)
        self.blue = int(settings.bmax)

        rowcolour = ""

        for x in range (0, int(settings.imageheight)): # rows
            for y in range (0, int(settings.imagewidth)): # columns 
                if x % (int(settings.gridheight) + 1) == 0: # if row mod grid height
                    self.pixels.append((self.red, self.green, self.blue))
                    if settings.gridbgmode == "row":
                        rowcolour = (
                            random.randint(0, int(settings.gridbgred)), 
                            random.randint(0, int(settings.gridbggreen)), 
                            random.randint(0, int(settings.gridbgblue))
                        )                            
                else:
                    if y % (int(settings.gridwidth) + 1) == 0:
                        self.pixels.append((self.red, self.green, self.blue))
                    else:
                        if settings.gridbgmode == "row":
                            self.pixels.append(rowcolour)
                        elif settings.gridbgmode == "single":
                            self.pixels.append((int(settings.gridbgred), int(settings.gridbggreen), int(settings.gridbgblue)))
                        elif settings.gridbgmode == "random":
                            self.pixels.append((random.randint(0, int(settings.gridbgred)), random.randint(0, int(settings.gridbggreen)), random.randint(0, int(settings.gridbgblue))))                           
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
        if settings.gridborders == "y" and settings.imagemode == "grid":
            self.calculate_borders()  

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

imagegenerator = ImageGenerator()