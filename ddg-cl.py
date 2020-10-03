#! coding: utf-8
#!/usr/bin/env python

import subprocess, csv, xlwt, random, time, json, os, sys, platform, datetime, gzip, zipfile, tarfile, shutil, math, traceback
from ddg.classes import settings, logger, presets, columns, valuedict, generator, imagegenerator

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
        print("5. Application settings")  

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
            print("The following column files are located in the '{0}' folder: \n\nCurrent columns file: {1}\n".format(settings.get_columns_path(), settings.columnfile))

            if settings.columnfolder == "":
                settings.columnfolder = "."

            files = os.listdir(settings.get_columns_path())
        elif mode == "preset":
            print("The following preset files are located in the '{0}' folder: \n{1}".format(settings.get_presets_path(), ("\nCurrent preset file: {0}\n".format((settings.presetfile if settings.presetfile != "" else "")))))

            if settings.presetfolder == "":
                settings.presetfolder = "."

            files = os.listdir(settings.get_presets_path())

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
                deletepath = "{0}{1}{2}".format(settings.get_columns_path(), os.path.sep, deletefilename)
            elif mode == "preset":
                deletepath = "{0}{1}{2}".format(settings.get_presets_path(), os.path.sep, deletefilename)   
                               
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

                            originallocation = "{0}{1}{2}".format(settings.get_columns_path(), os.path.sep, settings.columnfile)
                            duplicatelocation = "{0}{1}{2}".format(settings.get_columns_path(), os.path.sep, duplicatename)
                    elif mode == "preset":
                            duplicatename = input("Enter name for duplicated file (do not include extension): ") + ".json"

                            originallocation = "{0}{1}{2}".format(settings.get_columns_path(), os.path.sep, settings.presetfile)
                            duplicatelocation = "{0}{1}{2}".format(settings.get_columns_path(), os.path.sep, duplicatename)

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

def view_json(notification = "\n", mode = "column"): # displays the columns in the terminal, and allows the user to select columns
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

                option = input("\n" + notification + "Enter a number (1 to " + str(columns.get_columns_total()) + ") to edit the column, or:\n+. Add a column\nx. Delete a column\nq. Quit\n\nOption:")

            elif mode == "preset":
                print("The following presets are currently defined:\n")

                for y in range (1, len(presets.json) + 1):
                    print(str(y) + ". " + presets.json[y - 1]["name"] + " - " + (presets.json[y - 1]["value"] if presets.json[y - 1]["value"] != "" else "<No value>"))
                    count = y

                option = input("\n" + notification + "Enter a number (1 to " + str(len(presets.json)) + ") to edit the preset, or:\nq. Quit\n\nOption:")

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
                            notification = "Value is not valid for current setting, valid values are " + str(acceptedvalues) + ".\n\n"
                        else:
                            presets.json[int(option) - 1]["value"] = inputvalue
                            notification = "Preset setting updated.\n\n"                            

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
                    notification = columns.generate_columns(columnname, columnvalue) + "\n\n"
                else:
                    notification = columns.create_column(columnname, columnvalue) + "\n\n"

                logger.add_log_entry(notification, True)
            elif mode == "column" and option == "x":
                index = int(input("\nEnter the column number you want to delete: ")) - 1
                confirm = input("Are you sure you want to delete column " + str(index + 1) + "? y/n\n\n")

                if confirm == "y":
                    notification = "Column '" + columns.json[index]["name"] + "' deleted!\n"
                    logger.add_log_entry("Column '" + columns.json[index]["name"] + "' deleted!", True)

                    columns.json.pop(index)
                    columns.update_column_data()
                else:
                    notification = "Column NOT deleted!\n\n"
            else:
                notification = "Invalid " + mode + " or option...\n\n"

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
                values.append(generator.get_values(columns.json[x]["value"], int(rownumber) + z))

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

def create_file(notification = ""):
    clear()
    if settings.fileformat in settings.dataformats:
        if settings.numberofrows == "":
            settings.numberofrows = input(notification + "Enter the number of rows to generate (or enter 'q' or 'b' to go back to the menu): ")
            clear()

        if settings.filename == "":
            settings.filename = input("Enter a name for the file (do not include the format of the file): ")

        if settings.numberofrows == "q" or settings.numberofrows == "b":
            menu()
        elif settings.numberofrows.isdigit() == False and (settings.numberofrows != 'q' or settings.numberofrows != 'b'):
            settings.numberofrows = ""
            create_file("Please enter a number...\n\n")

    notification = generator.create_file()
    menu(notification)

def menu(notification = ""): # main menu, first thing the user will see
    clear()

    settings.update_settings_file()
    settings.update_values()
    presets.get_presets()

    columns.get_columns()
    valuedict.reset_indexes()

    if settings.presetfile != "":
        presetmodstring = ""

        for presetsetting in presets.json:
            if presetsetting["value"] != "":
                presetmodstring += "\n - {0}".format(presetsetting["name"])

        if presetmodstring == "":
            presetmodstring += "<None>"

    columnfile = os.path.join(settings.get_columns_path(), settings.columnfile)
    presetfile = os.path.join(settings.get_presets_path(), settings.presetfile)

    if (settings.foldername != ""):
        if settings.filename != "":
            filename = "{0}{1}{2}.{3}{4}".format(
                settings.get_file_path(), 
                os.path.sep, 
                settings.filename, 
                (settings.fileformat if settings.fileformat != "" else "csv"), 
                (".{}".format(settings.compresstype.replace("-",".")) if settings.compress else "")
            )
        else:
            filename = "{0}{1}<filename not specified>".format(settings.get_file_path(), os.path.sep)

    version = "v0.9.0-{0}".format(str(subprocess.check_output(["git", "rev-parse", "HEAD"]).decode('ascii').strip())[:7])
    print("Dummy data generator {0}\nAndrew H 2020\n".format(version) +
    ("\nCurrent preset file: {0}\nThe selected preset file modifies the following settings: {1}".format(presetfile, presetmodstring) if settings.presetfile != "" else "") +
    "\nCurrent file name: {0}".format(filename) + 
    ("\nCurrent column file: {0}".format(columnfile) if settings.fileformat not in settings.imageformats else "") +
    ("\nCSV File encoding: {0}".format(settings.encodingtype) if settings.encoding else "") + 
    ("\nImage resolution: {0} x {1}".format(settings.imagewidth, settings.imageheight) if settings.fileformat in settings.imageformats else "") +
    (", grid borders enabled (image resolution may change)" if settings.imagemode == "grid" and settings.gridborders else "") + 
    ("\nImage generation mode: {0}".format(settings.imagemode) if settings.fileformat in settings.imageformats else "") +
    ("\n - Red: ({0},{1}), Green: ({2},{3}), Blue: ({4},{5})".format(settings.rmin, settings.rmax, settings.gmin, settings.gmax, settings.bmin, settings.bmax) if settings.fileformat in settings.imageformats and settings.imagemode == "random" else "" ) +
    ("\n - Red: {0}, Green: {1}, Blue: {2}".format(settings.rmax, settings.gmax, settings.bmax) if settings.fileformat in settings.imageformats and settings.imagemode == "single" else "") +
    ("\n - Red: ({0},{1}), Green: ({2},{3}), Blue: ({4},{5})\n - Row Height: {6}".format(settings.rmin, settings.rmax, settings.gmin, settings.gmax, settings.bmin, settings.bmax, settings.rowheight) if settings.fileformat in settings.imageformats and settings.imagemode == "row" else "" ) +
    ("\nLogging enabled" if settings.log else "\n") + notification)

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

settings.update_settings_file()
menu()