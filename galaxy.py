import matplotlib.pyplot as plt
from kapteyn import kmpfit
import numpy as np
import spreadsheet_interface as spin
from matplotlib.patches import Rectangle
import gc

# FOLLOWING: Conversion functions

def wl_to_freq(wavelength):
    return 299792458/wavelength


def freq_to_wl(freq):
    return 299792458/freq


class Galaxy:

    # Point types for different telescopes, read from spreadsheet "Point Styles"
    type_list = spin.get_point_styles()[2]
    color_list = spin.get_point_styles()[1]
    telescope_name_list = spin.get_point_styles()[0]

    def __init__(self, name, freq_list, telescope_list, flux_list, unc_upper_list, unc_lower_list, z, distance):
        self.name = name
        self.freq_list = freq_list
        self.temp_freq_list = freq_list  # For use with exclusions
        self.straightuptelelist = telescope_list
        self.telescope_list = telescope_list
        self.flux_list = flux_list
        self.temp_flux_list = flux_list  # For use with exclusions
        self.telescope_list, self.point_types, self.point_colors = self.make_other_lists()
        self.error_lists = [unc_lower_list, unc_upper_list]
        self.z = z
        self.distance = distance
        self.fit_with_error_blackbody = True
        self.fit_with_error_powerlaw = True
        self.hold = [0, 0, 0]
        self.holdkey = 'none'

    def make_other_lists(self):
        # This function is only for the class to call on itself.  It orders all the lists, and changes the telescope
        # list to say 'other' if it's not included in telescope_name_list.

        types = []
        colors = []
        ordered_tele = []

        for i in range(len(self.telescope_list)):
            switch = False
            j = 0
            while not switch:
                if self.telescope_list[i] == self.telescope_name_list[j]:
                    types.append(self.type_list[j])
                    colors.append(self.color_list[j])
                    ordered_tele.append(self.telescope_name_list[j])
                    switch = True
                elif j == (len(self.telescope_name_list) - 1):
                    types.append(self.type_list[j])
                    colors.append(self.color_list[j])
                    ordered_tele.append('Other')
                    switch = True
                j += 1

        return ordered_tele, types, colors

    def clear_fits(self, fit_type):
        # Clears saved fits of a certain type

        spin.clear_fits(self.name, fit_type)

    def create_fit(self, fit_range, hold=[0, 0, 0], fit_type='mod_blackbody', linestyle='solid', subtract=False):
        # This function creates a new fit given a range (where elements 0 and 1 are the start and end,
        # then any after are to be excluded.  Hold can be passed as a 1x3 array, where any non-zero values are
        # parameters to be held.
        # fit_type options: 'mod_blackbody', 'power_law'

        # If subtract==True, then before creating the fit, subtract out the previously created fits.
        if subtract is True:
            for i in range(len(self.flux_list)):
                self.flux_list[i] = self.flux_list[i] - self.sum_function(spin.read_fits(self.name), self.freq_list[i])

        self.hold = hold

        self.temp_freq_list = self.freq_list.copy()
        self.temp_flux_list = self.flux_list.copy()
        num_exclusions = 0
        if len(fit_range) > 2:
            num_exclusions = len(fit_range) - 2
            for i in range(num_exclusions):
                self.temp_freq_list.pop(fit_range[2] - i)
                self.temp_flux_list.pop(fit_range[2] - i)
                fit_range.pop(2)
                fit_range[1] -= 1

        if fit_type == 'mod_blackbody':
            dust_temp_param, dust_mass_param, beta_param = self.fit_set_mod_blackbody(fit_range[0], fit_range[1])
            fit_range[1] += num_exclusions
            spin.new_fit(self.name, fit_type, [dust_temp_param, dust_mass_param, beta_param], fit_range, linestyle)
        elif fit_type == 'power_law':
            a_param, alpha_param = self.fit_set_power_law(fit_range[0], fit_range[1])
            fit_range[1] += num_exclusions
            spin.new_fit(self.name, fit_type, [a_param, alpha_param], fit_range, linestyle)

    def give_subplot(self):
        # This function just plots all the points, along with any saved fits.

        # Make point list
        pointlist = []
        for i in range(len(self.telescope_name_list)):
            pointlist.append(None)

        # Plot each value, adding unique telescopes to point list (for legend)
        previous_points = []
        legend_counter = 0
        unique_tele_list = []
        for i in range(len(self.freq_list)):
            if any(ele == self.point_types[i] for ele in previous_points):
                plt.plot(self.freq_list[i], self.flux_list[i], color=self.point_colors[i], marker=self.point_types[i],
                         markersize=7)
            else:
                pointlist[legend_counter], = plt.plot(self.freq_list[i], self.flux_list[i], color=self.point_colors[i],
                                                      marker=self.point_types[i], linestyle='None', markersize=7)  # 9
                previous_points.append(self.point_types[i])
                unique_tele_list.append(self.telescope_list[i])
                legend_counter += 1

        # Title plot, create legend, error bars, etc.
        plt.title('SED for ' + self.name, fontsize=15)  # 20
        plt.yscale('log')
        plt.xscale('log')
        plt.xlabel('Rest Frequency (Hz)', fontsize=10)  # 15
        plt.ylabel('Flux Density (Jy)', fontsize=10)  # 15
        plt.legend(pointlist, unique_tele_list, fontsize=10, bbox_to_anchor=(1, 1),
                   loc='upper left')  # fsize 15 Put kwargs (bbox_to_anchor=(1, 1), loc='upper left') to put legend outside
        for i in range(len(self.freq_list)):  # Plot error bars ELSE upper limits if 0 given as upper error
            if (self.error_lists[1][i] == 'Limit') or (self.error_lists[1][i] == 'limit'):
                plt.errorbar(self.freq_list[i], self.flux_list[i], yerr=self.flux_list[i] / 5, fmt='none',
                             ecolor='black', uplims=self.flux_list[i])
            elif (self.error_lists[0][i] == 'Limit') or (self.error_lists[0][i] == 'limit'):
                plt.errorbar(self.freq_list[i], self.flux_list[i], yerr=self.flux_list[i] / 5, fmt='none',
                             ecolor='black', lolims=self.flux_list[i])
            else:
                plt.errorbar(self.freq_list[i], self.flux_list[i], yerr=self.error_lists[0][i], fmt='none',
                             ecolor='black')
        x_lower = np.min(self.freq_list) / 2
        x_upper = 2 * 10 ** 14
        y_lower = np.min(self.flux_list) / 2
        y_upper = np.max(self.flux_list) * 1.5

        # Plot all the fits from the parameters in the spreadsheet
        fit_list = spin.read_fits(self.name)
        if fit_list != []:
            for i in range(len(fit_list)):
                if fit_list[i][0] == 'mod_blackbody':
                    xrange = np.arange(x_lower, 10 ** 14, 1000000000)
                    fitplot = self.mod_blackbody_model([fit_list[i][1],
                                                        fit_list[i][2],
                                                        fit_list[i][3]], xrange)
                elif fit_list[i][0] == 'power_law':
                    xrange = np.arange(10 ** 11, 3 * 10 ** 14, 1000000000)
                    fitplot = self.power_law_model([fit_list[i][1], fit_list[i][2]], xrange)
                plt.plot(xrange, fitplot, color='black', linestyle=fit_list[i][6])

        # Plot the sum of all fits
        if fit_list != []:
            xrange = np.arange(x_lower, x_upper, 1000000000)
            fitplot = self.sum_function(fit_list, xrange)
            plt.plot(xrange, fitplot, color='black', linestyle='solid', alpha=.5)

        # Make axes
        axes = plt.gca()
        axes.set_xlim(x_lower, x_upper)
        axes.set_aspect(1)
        axes.tick_params(labelsize=10)
        x_axis_wl = axes.secondary_xaxis('top', functions=(freq_to_wl, wl_to_freq))
        x_axis_wl.tick_params(labelsize=10)
        x_axis_wl.set_xlabel("Rest Wavelength", fontsize=10)
        x_axis_wl.get_xaxis().set_tick_params(which='minor', size=0)
        x_axis_wl.get_xaxis().set_tick_params(which='minor', width=0)
        axes.set_ylim(y_lower, y_upper)
        # This code throws an error, but it works, so . . .
        labels = ['.1 \u03bcm', '1 \u03bcm', '10 \u03bcm', '100 \u03bcm', '1 mm', '1 cm', '10 cm', '1 m']
        x_axis_wl.set_xticklabels(labels)

        # Draw PAH emission reference lines as tall, thin, boxes
        pah_freqs = [3.89 * 10 ** 13, 2.65 * 10 ** 13, 2.36 * 10 ** 13, 4.84 * 10 ** 13, 3.49 * 10 ** 13]
        for i in range(len(pah_freqs)):
            box_width = pah_freqs[i] / 10
            left_side = pah_freqs[i] - (box_width * (np.sqrt(10)) / 10)
            axes.add_patch(Rectangle((left_side, 0), box_width, 100, facecolor='lightgray'))

        plt.tight_layout(h_pad=1.8)
        return plt

    def display_sed(self, savefig=False, savefolder=""):
        # This function just plots all the points, along with any saved fits.

        # Make point list
        pointlist = []
        for i in range(len(self.telescope_name_list)):
            pointlist.append(None)

        # Plot each value, adding unique telescopes to point list (for legend)
        previous_points = []
        legend_counter = 0
        unique_tele_list = []
        for i in range(len(self.freq_list)):
            if any(ele == self.point_types[i] for ele in previous_points):
                plt.plot(self.freq_list[i], self.flux_list[i], color=self.point_colors[i], marker=self.point_types[i], markersize=7)
            else:
                pointlist[legend_counter], = plt.plot(self.freq_list[i], self.flux_list[i], color=self.point_colors[i],
                                                      marker=self.point_types[i], linestyle='None', markersize=7) # 9
                previous_points.append(self.point_types[i])
                unique_tele_list.append(self.telescope_list[i])
                legend_counter += 1

        # Title plot, create legend, error bars, etc.
        plt.title('SED for ' + self.name, fontsize=15) # 20
        plt.yscale('log')
        plt.xscale('log')
        plt.xlabel('Rest Frequency (Hz)', fontsize=10) # 15
        plt.ylabel('Flux Density (Jy)', fontsize=10) # 15
        plt.legend(pointlist, unique_tele_list, fontsize=10, bbox_to_anchor=(1, 1), loc='upper left')  # fsize 15 Put kwargs (bbox_to_anchor=(1, 1), loc='upper left') to put legend outside
        for i in range(len(self.freq_list)):  # Plot error bars ELSE upper limits if 0 given as upper error
            if (self.error_lists[1][i] == 'Limit') or (self.error_lists[1][i] == 'limit'):
                plt.errorbar(self.freq_list[i], self.flux_list[i], yerr=self.flux_list[i]/5, fmt='none', ecolor='black', uplims=self.flux_list[i])
            elif (self.error_lists[0][i] == 'Limit') or (self.error_lists[0][i] == 'limit'):
                plt.errorbar(self.freq_list[i], self.flux_list[i], yerr=self.flux_list[i]/5, fmt='none', ecolor='black', lolims=self.flux_list[i])
            else:
                plt.errorbar(self.freq_list[i], self.flux_list[i], yerr=self.error_lists[0][i], fmt='none', ecolor='black')
        x_lower = np.min(self.freq_list)/2
        x_upper = 2*10**14
        y_lower = np.min(self.flux_list)/2
        y_upper = np.max(self.flux_list)*1.5

        # Plot all the fits from the parameters in the spreadsheet
        fit_list = spin.read_fits(self.name)
        if fit_list != []:
            for i in range(len(fit_list)):
                if fit_list[i][0] == 'mod_blackbody':
                    xrange = np.arange(x_lower, 10**14, 1000000000)
                    fitplot = self.mod_blackbody_model([fit_list[i][1],
                                                        fit_list[i][2],
                                                        fit_list[i][3]], xrange)
                elif fit_list[i][0] == 'power_law':
                    xrange = np.arange(10**11, 3*10**14, 1000000000)
                    fitplot = self.power_law_model([fit_list[i][1], fit_list[i][2]], xrange)
                plt.plot(xrange, fitplot, color='black', linestyle=fit_list[i][6])

        # Plot the sum of all fits
        if fit_list != []:
            xrange = np.arange(x_lower, x_upper, 1000000000)
            fitplot = self.sum_function(fit_list, xrange)
            plt.plot(xrange, fitplot, color='black', linestyle='solid', alpha=.5)

        # Make axes
        axes = plt.gca()
        axes.set_xlim(x_lower, x_upper)
        axes.set_aspect(1)
        axes.tick_params(labelsize=10)
        x_axis_wl = axes.secondary_xaxis('top', functions=(freq_to_wl, wl_to_freq))
        x_axis_wl.tick_params(labelsize=10)
        x_axis_wl.set_xlabel("Rest Wavelength", fontsize=10)
        x_axis_wl.get_xaxis().set_tick_params(which='minor', size=0)
        x_axis_wl.get_xaxis().set_tick_params(which='minor', width=0)
        axes.set_ylim(y_lower, y_upper)
        # This code throws an error, but it works, so . . .
        labels = ['.1 \u03bcm', '1 \u03bcm', '10 \u03bcm', '100 \u03bcm', '1 mm', '1 cm', '10 cm', '1 m']
        x_axis_wl.set_xticklabels(labels)

        # Draw PAH emission reference lines as tall, thin, boxes
        pah_freqs = [3.89*10**13, 2.65*10**13, 2.36*10**13, 4.84*10**13, 3.49*10**13]
        for i in range(len(pah_freqs)):
            box_width = pah_freqs[i]/10
            left_side = pah_freqs[i] - (box_width * (np.sqrt(10))/10)
            axes.add_patch(Rectangle((left_side, 0), box_width, 100, facecolor='lightgray'))

        plt.tight_layout(h_pad=1.8)
        if savefig:
            plt.savefig(savefolder + "\\sed_" + self.name)
            plt.clf()
            return None
        plt.show()

    # FOLLOWING: Chi-square fitting functions

    def fit_set_mod_blackbody(self, start_index, end_index):
        # This function uses mod_blackbody_model to find the chi-square best fit parameters for a given range.

        freq_to_fit = self.temp_freq_list[start_index:end_index]
        flux_to_fit = self.temp_flux_list[start_index:end_index]
        p1hold = 0
        p2hold = 0
        p3hold = 0

        # If some parameters are held, modify initial parameters accordingly
        p0 = [25, 10 ** 6, 1.8]
        if self.hold[0] != 0:
            p1hold = self.hold[0]
            self.holdkey = 'dust_temp'
            del p0[0]
        if self.hold[1] != 0:
            p2hold = self.hold[1]
            if self.holdkey == 'none':
                self.holdkey = 'dust_mass'
                del p0[1]
            else:
                self.holdkey = self.holdkey + ', dust_mass'
                del p0[0]
        if self.hold[2] != 0:
            p3hold = self.hold[2]
            if self.holdkey == 'none':
                self.holdkey = 'beta'
                del p0[2]
            else:
                self.holdkey = self.holdkey + ', beta'
                del p0[1]

        try:
            fitobj = kmpfit.simplefit(self.mod_blackbody_model, p0, freq_to_fit, flux_to_fit,
                                      err=self.error_lists[0][start_index:end_index])
        except:
            if self.fit_with_error_blackbody:
                print("WARNING: Could not fit with error.")
                self.fit_with_error_blackbody = False
            fitobj = kmpfit.simplefit(self.mod_blackbody_model, p0, freq_to_fit, flux_to_fit)

        # Set parameters to return depending on held parameters
        counter = 0
        return_params = [0]
        if self.hold[0] != 0:
            return_params[0] = p1hold
        else:
            return_params[0] = fitobj.params[counter]
            counter += 1
        if self.hold[1] != 0:
            return_params.append(p2hold)
        else:
            return_params.append(fitobj.params[counter])
            counter += 1
        if self.hold[2] != 0:
            return_params.append(p3hold)
        else:
            return_params.append(fitobj.params[counter])

        return return_params

    def fit_set_power_law(self, start_index, end_index):
        # This function uses a power_law to find the chi-square best fit parameters for a given range.

        freq_to_fit = self.temp_freq_list[start_index:end_index]
        flux_to_fit = self.temp_flux_list[start_index:end_index]
        p0 = (0, 2)

        try:
            fitobj = kmpfit.simplefit(self.power_law_model, p0, freq_to_fit, flux_to_fit,
                                      err=self.error_lists[0][start_index:end_index])
        except:
            if self.fit_with_error_powerlaw:
                print("WARNING: Could not fit with error.")
                self.fit_with_error_powerlaw = False
            fitobj = kmpfit.simplefit(self.power_law_model, p0, freq_to_fit, flux_to_fit)
        return fitobj.params

    # FOLLOWING: Function models

    def mod_blackbody_model(self, p, freq):
        # Constants for use in model
        h = 6.626 * 10**(-34)
        k = 1.38 * 10**(-23)
        kappa_0 = .192
        nu_0 = 856.6

        # Determines if different parameters are to be held constant in the fitting
        dust_temp = 0
        dust_mass = 0
        beta = 0
        if len(p) == 3:
            dust_temp, dust_mass, beta = p
        elif len(p) == 2:
            if self.holdkey == 'beta':
                dust_temp, dust_mass = p
                beta = self.hold[2]
            elif self.holdkey == 'dust_mass':
                dust_temp, beta = p
                dust_mass = self.hold[1]
            elif self.holdkey == 'dust_temp':
                dust_mass, beta = p
                dust_temp = self.hold[0]
        else:
            if self.holdkey == 'dust_mass, beta':
                dust_temp = p
                beta = self.hold[2]
                dust_mass = self.hold[1]
            elif self.holdkey == 'dust_temp, beta':
                dust_mass = p
                dust_temp = self.hold[0]
                beta = self.hold[2]
            elif self.holdkey == 'dust_temp, dust_mass':
                beta = p
                dust_temp = self.hold[0]
                dust_mass = self.hold[1]

        snu = .00182917 * kappa_0 * (((freq/(10**9))/nu_0)**(beta+3)) * (dust_mass/(self.distance**2)) * (1/(np.exp((h*freq)/(k*dust_temp))-1))
        return snu * (1 + self.z)

    def power_law_model(self, p, freq):
        a, alpha = p
        snu = a*(freq**alpha)
        return snu

    def sum_function(self, fit_list, freq):
        # Takes an array 'fit_list' that is a list of all the saved fits.  Returns the sum of all these.

        sum_list = []

        for i in range(len(fit_list)):
            if fit_list[i][0] == 'mod_blackbody':
                sum_list.append(self.mod_blackbody_model([fit_list[i][1], fit_list[i][2], fit_list[i][3]], freq))
            elif fit_list[i][0] == 'power_law':
                sum_list.append(self.power_law_model([fit_list[i][1], fit_list[i][2]], freq))

        sum_func = 0
        for i in range(len(sum_list)):
            sum_func += sum_list[i]

        return sum_func
