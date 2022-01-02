import galaxy
import spreadsheet_interface as spin


# FOLLOWING: Constants
spreadsheet_loc = r"C:\Users\bderi\Desktop\Research Boizelle\ALMA Archive Galaxy Observations with SED Flux Densities"

# FOLLOWING: Menu functions

def indiv_target_menu(target, exit_check):
    # Check for condition to exit loop
    if exit_check:
        return None

    print("\nSelect action for " + target.name + ":")
    print("\t0: Display SED\n",
          "\t1: Create new fit\n",
          "\t2: Clear saved fits\n",
          "\t3: List saved fits\n",
          "\t4: Return to main menu\n")
    selection = input("Enter selection:")

    if selection == '0':  # Display SED
        print("\nDisplaying SED for " + target.name + " . . . ")
        target.display_sed()
        indiv_target_menu(target, False)

    elif selection == '1':  # Create new fit
        hold = [0, 0, 0]
        linestyle = 'solid'
        fit_type = 'mod_blackbody'
        print("\nSelect fit type:\n",
              "\t0: Modified blackbody\n",
              "\t1: Power law\n")
        selection = input("Enter selection:")
        if selection == '0':
            fit_type = 'mod_blackbody'
        elif selection == '1':
            fit_type = 'power_law'
        else:
            print("Invalid input -- try again . . . ")
            indiv_target_menu(target, False)
        selection = input("Enter range start, end, then exclusions as a comma separated list:")
        selection = selection.split(',')
        for i in range(len(selection)):
            selection[i] = int(selection[i])
        fit_range = selection
        if fit_type == 'mod_blackbody':
            selection = input("Enter hold values as a comma separated list if applicable:")
            if selection != "":
                selection = selection.split(',')
                for i in range(len(selection)):
                    selection[i] = float(selection[i])
                hold = selection
        selection = input("Enter linestyle if applicable (see matplotlib docs for options):")
        if selection != "":
            linestyle = selection
        print("Subtract out background levels for this fit?\n",
              "\t0: Yes\n",
              "\t1: No")
        selection = input("Enter selection:")
        subtract = False
        if selection == '0':
            subtract = True
        try:
            target.create_fit(fit_range, hold=hold, fit_type=fit_type, linestyle=linestyle, subtract=subtract)
        except:
            print("\n**Could not create fit because of invalid input**")
        indiv_target_menu(target, False)

    elif selection == '2':  # Clear fits
        print("Which fits would you like to clear?:\n",
              "\t0: Modified Blackbody\n",
              "\t1: Power law\n")
        selection = input("Enter selection:")
        if selection == '0':
            target.clear_fits('mod_blackbody')
        elif selection == '1':
            target.clear_fits('power_law')
        else:
            print("Invalid input -- try again . . . ")
            indiv_target_menu(target, False)
        indiv_target_menu(target, False)

    elif selection == '3':  # List saved fits
        print("Saved fits for " + target.name + ":")
        fit_list = spin.read_fits(target.name)
        for i in range(len(fit_list)):
            print(str(i) + ":")
            print("\tType:", fit_list[i][0], "\n",
                  "\tParameters:", fit_list[i][1:4], "\n",
                  "\tRange:", fit_list[i][4:6], "\n",
                  "\tLinestyle:", fit_list[i][6])
        indiv_target_menu(target, False)

    elif selection == '4':  # Return to main menu
        indiv_target_menu(target, True)

    else:  # Any other invalid input
        print("Invalid input -- try again . . . ")
        indiv_target_menu(target, False)


def select_target_menu():
    print("\nSelect target to work with:")
    name_list = spin.target_list()
    for i in range(len(name_list)):
        print("\t" + str(i) + ": " + name_list[i])
    print("\t" + str(len(name_list)) + ": Return to main menu\n")
    selection = input("Enter selection:")
    selection = int(selection)
    if selection == len(name_list):
        return None
    else:
        g = spin.get_set_n(selection)
    indiv_target_menu(g, False)


# FOLLOWING: Main function/menu loop
menu_loop = True
while menu_loop is True:
    print("\nMain Menu:\n",
          "\t0: Select target\n",
          "\t1: Quit\n")
    user_selection = input("Enter selection:")
    if user_selection == '0':
        select_target_menu()
    elif user_selection == '1':
        menu_loop = False
    else:
        print("Invalid input -- quitting program . . . ")
        menu_loop = False
