import galaxy
import spreadsheet_interface as spin
import numpy as np
import matplotlib.pyplot as plt
import gc
from astropy.io import fits
from mpl_toolkits.axes_grid1 import make_axes_locatable


# FOLLOWING: Constants
spreadsheet_loc = r"C:\Users\bderi\Box\School\Research Boizelle\ALMA Archive Galaxy Observations with SED Flux Densities"
fits_loc = r"C:\Users\bderi\Box\School\Research Boizelle\FITS"

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


def print_all_seds():
    save_folder = r"C:\Users\bderi\Desktop\Research Boizelle\AutoSED"
    name_list = spin.target_list()
    for i in range(len(name_list)):
        try:
            g = spin.get_set_n(i)
            g.display_sed(savefig=True, savefolder=save_folder)
            del g
            gc.collect()
        except:
            pass


def print_set_of_seds():
    save_folder = r"C:\Users\bderi\Desktop"
    print("\nSelect targets for which to print SEDs:")
    name_list = spin.target_list()
    for i in range(len(name_list)):
        print("\t" + str(i) + ": " + name_list[i])
    selections = input("Enter selection:")
    selections = selections.split(",")
    for i in range(len(selections)):
        selections[i] = int(selections[i])
    xplots = 3
    yplots = 7
    layout_dict = {
        "w_pad": 1,
        "h_pad": 30
    }
    fig, axs = plt.subplots(xplots, yplots, sharex=True, sharey=True, tight_layout=layout_dict, figsize=(11, 5))
    selection_iter = 0
    for h in range(xplots):
        for k in range(yplots):
            g = spin.get_set_n(selections[selection_iter])
            for i in range(len(g.freq_list)):
                if g.straightuptelelist[i] == "ALMA (Nuclear)":
                    axs[h, k].plot(g.freq_list[i], g.flux_list[i], linestyle="None",
                                                    color="rebeccapurple",
                                                    marker="v",
                                                    markersize=4)
                elif g.straightuptelelist[i] == "ALMA (Extended)":
                    axs[h, k].plot(g.freq_list[i], g.flux_list[i], linestyle="None",
                                                    color="rebeccapurple",
                                                    marker="^",
                                                    markersize=5)
                else:  # unique point
                    axs[h, k].plot(g.freq_list[i], g.flux_list[i], linestyle="None",
                                   color="peru",
                                   marker="+",
                                   markersize=4)
            axs[h, k].set_yscale('log')
            axs[h, k].set_xscale('log')
            axs[h, k].set_xlim(5e8, 4e14)
            axs[h, k].set_ylim(2*10**-4, 2000)
            axs[h, k].tick_params(which="both", axis="y", direction="in", pad=5, labelsize=7)
            axs[h, k].tick_params(which="both", axis="x", direction="in", labelsize=7)
            axs[h, k].set_title("   " + g.name, fontdict={"fontsize": 6}, loc="left", y=.8)
            axs[h, k].minorticks_off()
            axs[h, k].set_yticks((10**-2, 1, 10**2))
            axs[h, k].set_yticklabels([-2, 0, 2])
            axs[h, k].set_xticks((10 ** 10, 10 ** 13))
            axs[h, k].set_xticklabels([10, 13])
            if ([h, k] == [0, 0]) or ([h, k] == [0, 1]) or ([h, k] == [0, 2]) or ([h, k] == [0, 3]) or \
                    ([h, k] == [0, 4]) or ([h, k] == [0, 5]) or ([h, k] == [0, 6]) or ([h, k] == [1, 0]) or \
                    ([h, k] == [1, 1]) or ([h, k] == [1, 2]) or ([h, k] == [1, 3]) or ([h, k] == [1, 4]) or \
                    ([h, k] == [1, 5]):
                for axis in ['top', 'bottom', 'left', 'right']:
                    axs[h, k].spines[axis].set_linewidth(3)

            fit_list = spin.read_fits(g.name)
            if fit_list != []:
                for i in range(len(fit_list)):
                    if fit_list[i][0] == 'mod_blackbody':
                        xrange = np.arange(5e8, 4e14, 100000000000)
                        fitplot = g.mod_blackbody_model([fit_list[i][1],
                                                            fit_list[i][2],
                                                            fit_list[i][3]], xrange)
                    elif fit_list[i][0] == 'power_law':
                        xrange = np.arange(5e8, 4e14, 100000000000)
                        fitplot = g.power_law_model([fit_list[i][1], fit_list[i][2]], xrange)
                    axs[h, k].plot(xrange, fitplot, color='black', linestyle=fit_list[i][6])
            selection_iter += 1
    plt.subplots_adjust(bottom=.15, hspace=0, wspace=0, right=.8)
    axs[2, 3].set_xlabel("log$_{10}$ Rest Frequency (Hz)")
    axs[1, 0].set_ylabel("log$_{10}$ Flux Density (Jy)")
    plt.savefig(save_folder + "\\all_seds_w_alma", dpi=500)
    plt.show()
    return None

def sed_w_alma():
    save_folder = r"C:\Users\bderi\Desktop\ALMA Images with SEDs"
    asec_spacing = 6
    ext_flux_spacing = .0002
    nuc_flux_spacing = .005

    # Get user input for which target to display
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

    # Put SED on the top
    fig, axs = plt.subplots(2, 3)
    axs[0, 0] = plt.subplot2grid((3, 2), (0, 0), colspan=3)
    axs[0, 0] = g.display_sed(give_as_subplot=True, scaling=.7)

    # Put the images on the bottom
    file1_name = fits_loc + "\\" + g.name.replace(" ", "") + r"ALMANuclearNat.fits"
    cont_map = fits.open(file1_name)
    try:
        file2_name = fits_loc + "\\" + g.name.replace(" ", "") + r"ALMAExtendedLowerNat.fits"
        file3_name = fits_loc + "\\" + g.name.replace(" ", "") + r"ALMAExtendedUpperNat.fits"
        lower_sub_map = fits.open(file2_name)
        upper_sub_map = fits.open(file3_name)
    except:
        file2_name = fits_loc + "\\" + g.name.replace(" ", "") + r"ALMAExtendedNoiseNat.fits"
        file3_name = file2_name
        lower_sub_map = fits.open(file2_name)
        upper_sub_map = fits.open(file3_name)

    colormap = "pink"

    image_size = np.round((3600 * (cont_map[0].header['CDELT2'] * len(cont_map[0].data[0][0]))), 2)  # In arc seconds
    firstfig = axs[1, 0].imshow(cont_map[0].data[0][0], cmap=colormap,
                             extent=(image_size / 2, -image_size / 2, -image_size / 2, image_size / 2))
    secondfig = axs[1, 1].imshow(lower_sub_map[0].data[0][0], cmap=colormap,
                              extent=(image_size / 2, -image_size / 2, -image_size / 2, image_size / 2))
    thirdfig = axs[1, 2].imshow(upper_sub_map[0].data[0][0], cmap=colormap,
                             extent=(image_size / 2, -image_size / 2, -image_size / 2, image_size / 2))

    plt.setp(axs[1, 0], ylabel=r"$\Delta$ decl. (arcsec)")
    plt.setp(axs[1, 1], xlabel=r"$\Delta$ R.A. (arcsec)")

    d1 = make_axes_locatable(axs[1, 0])
    axs[1, 0].set_xticks((-asec_spacing, 0, asec_spacing))
    axs[1, 0].set_yticks((-asec_spacing, 0, asec_spacing))
    cax1 = d1.append_axes("top", size="10%", pad=0.3)
    cbar1 = plt.colorbar(firstfig, cax=cax1, orientation="horizontal", ticks=(0, nuc_flux_spacing, 2*nuc_flux_spacing, 3*nuc_flux_spacing, 4*nuc_flux_spacing))
    cbar1.ax.tick_params(top=True, bottom=False, pad=-30)
    cbar1.ax.set_xlabel("Flux (mJy/beam)", fontdict={'fontsize': 8.5})
    cbar1.ax.set_xticklabels(['0', 1000*nuc_flux_spacing, 2*1000*nuc_flux_spacing, 3*1000*nuc_flux_spacing, 4*1000*nuc_flux_spacing])

    d2 = make_axes_locatable(axs[1, 1])
    axs[1, 1].set_xticks((-asec_spacing, 0, asec_spacing))
    axs[1, 1].set_yticks((-asec_spacing, 0, asec_spacing))
    cax2 = d2.append_axes("top", size="10%", pad=0.3)
    cbar2 = plt.colorbar(secondfig, cax=cax2, orientation="horizontal", ticks=(-2*ext_flux_spacing, -ext_flux_spacing, 0, ext_flux_spacing, 2*ext_flux_spacing))
    cbar2.ax.tick_params(top=True, bottom=False, pad=-30)
    cbar2.ax.set_xlabel("Flux (mJy/beam)", fontdict={'fontsize': 8.5})
    cbar2.ax.set_xticklabels([-2*ext_flux_spacing*1000, -ext_flux_spacing*1000, '0.0', ext_flux_spacing*1000, 2*ext_flux_spacing*1000])

    d3 = make_axes_locatable(axs[1, 2])
    axs[1, 2].set_xticks((-asec_spacing, 0, asec_spacing))
    axs[1, 2].set_yticks((-asec_spacing, 0, asec_spacing))
    cax3 = d3.append_axes("top", size="10%", pad=0.3)
    cbar3 = plt.colorbar(thirdfig, cax=cax3, orientation="horizontal", ticks=(-2*ext_flux_spacing, -ext_flux_spacing, 0, ext_flux_spacing, 2*ext_flux_spacing))
    cbar3.ax.tick_params(top=True, bottom=False, pad=-30)
    cbar3.ax.set_xlabel("Flux (mJy/beam)", fontdict={'fontsize': 8.5})
    cbar3.ax.set_xticklabels([-2*ext_flux_spacing*1000, -ext_flux_spacing*1000, '0.0', ext_flux_spacing*1000, 2*ext_flux_spacing*1000])

    plt.savefig(save_folder + "\\" + g.name.replace(" ", "") + "_sed_w_alma_images", dpi=500)
    plt.show()


# FOLLOWING: Main function/menu loop
menu_loop = True
while menu_loop is True:
    print("\nMain Menu:\n",
          "\t0: Select target\n",
          "\t1: Print all SEDs\n",
          "\t2: Print set of SEDs\n",
          "\t3: Print SED next to ALMA images\n"
          "\t4: Quit\n")
    user_selection = input("Enter selection:")
    if user_selection == '0':
        select_target_menu()
    elif user_selection == '1':
        print("Printing all SEDs.  This could take a few minutes . . . ")
        print_all_seds()
        menu_loop = False
    elif user_selection == '2':
        print_set_of_seds()
        menu_loop = False
    elif user_selection == '3':
        sed_w_alma()
        menu_loop = False
    elif user_selection == '4':
        menu_loop = False
    else:
        print("Invalid input -- quitting program . . . ")
        menu_loop = False

# Set 1: ic1531, ngc612, pks718, ngc3100, eso443, ngc3557, ic4296, ngc7075, ic1459
# Set 2: ngc4945, ngc1399, ngc4594, ngc4751, ngc6861, ngc1600

# 40, 41, 45, 37, 5, 42, 43, 62, 48, 63, 64, 4, 65, 47, 28, 7, 10, 15, 18, 16, 20
