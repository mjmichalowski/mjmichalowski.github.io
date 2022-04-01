# -*- coding: utf-8 -*-
"""
________________TITLE________________
               Z-Boson
-------------------------------------
This Python script accepts decay data for reactions (assumed to be
described by a first-order Feynman diagram) in which Z Boson is
the propagator. It then performs a chi squared minimisation to obtain
the parameters for the fit to Breit-Wigner relation. By default,
the free parameters are mass and width of Z Boson, thus the partial
widths for the two vertices are set to the value for electron-positron
annihilation/creation. However, the user can choose to treat this value as
a free parameter or keep it fixed for the annihilation vertex but
consider a new creation vertex with different partial width that will
be treated as a free parameter. The default data files used by this script are:
'z_boson_data_1.csv' and 'z_boson_data_2.csv' which contain measured data for the
default case. If the user wants to consider new decay products, a different
data file has to be provided.

Having performed the minimisation, the script displays and saves the best fit plot
alongside its residues plot. Furthermore, in the default case it also displays and
saves the chi squared surface plot against the two free parameters. All plots are
saved in folder named 'SavedFigures' in the same directory as this script.

Finally, it displays the numerical values and uncertainties for mass, width and
lifetime of z boson, reduced chi squared, partial width for electron-positron (if selected)
and partial width for new decay products (if selected).

The script operates via a graphical user interface in which all options are shown
to the user at once and from which the analysis can be performed multiple
times without the program closing.


Last Updated: 14/12/21
@author: M. J. Michałowski
"""

from re import match
import sys
from os import mkdir
from os.path import exists
from tkinter import Button, Label, Entry, StringVar, Radiobutton, BooleanVar, Tk
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilenames
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as so


FILE_NAMES = ['z_boson_data_1.csv', 'z_boson_data_2.csv']
GAMMA_EE = 0.08391  # GeV
H_BAR = 6.582119569 * 10**(-25)  # GeV*s
M_Z0 = 91.179  # GeV/c^2  --  initial guess
GAMMA_Z0 = 2.510  # GeV  --  initial guess
CONVERSION_FACTOR = 3.894 * 10**5  # nb


def read_data(file_names):
    """
    Responsible for importing, combining and validating the data. It ignores
    lines in the provided files which contain non-numerical entries,
    error values of 0 or less and energy and cross section values of less
    than 0. It produced a message which notifies a user how many of the requested
    files have been imported successfully.

    :param file_names: list of pathname-strings

    :return: combined data as np.array
    """

    output_array = []
    successful_file_imports = len(file_names)
    for file_name in file_names:
        try:
            with open(file_name, 'r') as file:
                for line in file:
                    try:
                        if match('.*nan.*', line):
                            continue
                        line = [float(entry) for entry in line.split(',')]
                        if line[2] <= 0 or line[1] < 0 or line[0] < 0:
                            continue
                        output_array.append(line)
                    except ValueError:
                        pass
        except FileNotFoundError:
            successful_file_imports -= 1

    message = f'{successful_file_imports}/{len(file_names)} files have been imported successfully.'
    output_array.sort(key=lambda l: l[0])
    return np.array(output_array), message


def initial_filter(data):
    """
    Performs initial filtering of the data, aiming to delete extreme outliers.
    It operates by assuming the cross section values are distributed normally
    and then deletes all data points whose cross section is more than 5 standard
    deviations away from the mean.

    :param data: np.array containing the unfiltered data

    :return: np.array containing the filtered data
    """

    mean = np.average(data[:, 1])
    sigma = np.std(data[:, 1])
    new_data = []
    for entry in data:
        if np.abs(mean - entry[1]) < 5*sigma:
            new_data.append(entry)
    return np.array(new_data)


def filter_data(data, func, popt, gamma_ee_unknown=False):
    """
    Performs a more specific filtering of the data based on the predicted
    distribution the data points are supposed to follow. For each point,
    it calculates the predicted cross section for its energy and then
    removes this point if it lies further away than 4 sigma
    from that prediction.

    :param data: np.array of unfiltered data
    :param func: the expected distribution function
    :param popt: np.array of the values of free parameters after initial fitting
    :param gamma_ee_unknown: False by default, True if partial width for electron-positron
                             is to be treated a free parameter

    :return: np.array of filtered data, list of outlier points
    """

    if len(popt) == 2:
        deviation_array = np.abs(data[:, 1] - func(data[:, 0], popt[0], popt[1]))
    elif len(popt) == 3 and gamma_ee_unknown:
        deviation_array = np.abs(data[:, 1] - func(data[:, 0], popt[0], popt[1], popt[2], popt[2]))
    else:
        deviation_array = np.abs(data[:, 1] - func(data[:, 0], popt[0], popt[1], popt[2]))

    mean = np.average(deviation_array)
    sigma = np.std(deviation_array)
    z_scores = (deviation_array - mean)/sigma
    new_data = []
    outliers = []
    for z_score, entry in zip(z_scores, data):
        if z_score < 4:
            new_data.append(entry)
        else:
            outliers.append(entry)

    return np.array(new_data), outliers


def cross_section(energy, m_z=M_Z0, gamma_z=GAMMA_Z0,
                  gamma_vertex_1=GAMMA_EE, gamma_vertex_2=GAMMA_EE):
    """
    The distribution function that the data is expected to follow.
    It is commonly known as the Breit-Wigner expression.

    :param energy: np.array of energy values
    :param m_z: float - mass of Z Boson
    :param gamma_z: float - width of Z Boson
    :param gamma_vertex_1: float - partial width of the first vertex
    :param gamma_vertex_2: float - partial width of the second vertex

    :return: np.array of predicted cross section values at energies provided
    """

    return ((12*np.pi) / (m_z**2)) * gamma_vertex_1 * gamma_vertex_2 * CONVERSION_FACTOR * \
           (energy**2 / ((energy**2 - m_z**2)**2 + (gamma_z*m_z)**2))


def chi_square(data, popt, gamma_ee_unknown, func=cross_section):
    """
    The chi squared function.

    :param data: np.array of data
    :param popt: np.arrays of floats - values of the fitted parameters
    :param gamma_ee_unknown: True if partial width for electron-positron is unknown,
                             False otherwise
    :param func: the predicted distribution function

    :return: float - chi squared value of the fit
    """
    observed = data[:, 1]
    error = data[:, 2]
    if len(popt) == 2:
        predicted = func(data[:, 0], popt[0], popt[1])
    elif len(popt) == 3 and gamma_ee_unknown:
        predicted = func(data[:, 0], popt[0], popt[1], popt[2], popt[2])
    else:
        predicted = func(data[:, 0], popt[0], popt[1], popt[2])

    return np.sum((observed - predicted)**2 / error**2)


def check_numerical_input(value):
    """
    Used to check for validity of the inputs in the graphical interface.

    :param value: string - user's input

    :return: True if 'value' can be converted to float, False otherwise
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def fit_to_data(data, different_decay, gamma_ee_unknown, custom_gamma=0.01, func=cross_section):
    """
    The core component of the script. Employs scipy.curve_fit to minimise chi squared
    value and thus find the optimal parameter values. The function has three distinct
    branches which analyse the default and optional scenarios.

    :param data: np.array of data
    :param different_decay: True if option to analyse new decay products was selected,
                            False otherwise
    :param gamma_ee_unknown: True if option to treat partial width of electron-positron
                             as a free parameter was selected, False otherwise
    :param custom_gamma: float - user's guess for the optional partial widths
    :param func: the predicted distribution function

    :return: np.array of data, np.array of parameters, np.array of covariance matrix
             and gamma_ee_unknown
    """
    data = initial_filter(data)
    popt, pcov = [], []

    if different_decay:
        gamma_decay = custom_gamma
        outliers = True
        while outliers:
            popt, pcov = so.curve_fit(lambda x, a, b, c: func(x, a, b, c, GAMMA_EE),
                                      data[:, 0], data[:, 1], p0=[91.179, 2.510, gamma_decay],
                                      sigma=data[:, 2])[:2]
            data, outliers = filter_data(data, func, popt)

    elif gamma_ee_unknown:
        gamma_ee = custom_gamma
        outliers = True
        while outliers:
            popt, pcov = so.curve_fit(lambda x, a, b, c: func(x, a, b, c, c),
                                      data[:, 0], data[:, 1], p0=[91.179, 2.510, gamma_ee],
                                      sigma=data[:, 2])[:2]
            data, outliers = filter_data(data, func, popt, gamma_ee_unknown)

    else:
        outliers = True
        while outliers:
            popt, pcov = so.curve_fit(lambda x, a, b: func(x, a, b, GAMMA_EE, GAMMA_EE), data[:, 0],
                                      data[:, 1], p0=[91.179, 2.510], sigma=data[:, 2])[:2]
            data, outliers = filter_data(data, func, popt)

    return data, popt, pcov, gamma_ee_unknown


def plot_parameter_surface(data, popt, pcov):
    """
    In the default settings of the script, this function plots the 3D surface
    of chi squared against the two free parameters in the vicinity of the minimum.
    It is meant to provide a visual confirmation for the values of the fitted parameters.
    Saves the plot in 'SavedFigures' folder.

    :param data: np.array of data
    :param popt: np.array of fitted parameters
    :param pcov: np.array of covariance matrix

    :return: None
    """

    delta_m_z = 1.5 * pcov[0, 0]**0.5
    delta_gamma_z = 1.5 * pcov[1, 1]**0.5
    m_z_array = np.linspace(popt[0]-delta_m_z, popt[0]+delta_m_z, 100)
    gamma_z_array = np.linspace(popt[1]-delta_gamma_z, popt[1]+delta_gamma_z, 100)
    min_chi_squared = chi_square(data, popt, gamma_ee_unknown=False)

    m_z_values = []
    gamma_z_values = []
    chi_square_values = []
    for m_z in m_z_array:
        for gamma_z in gamma_z_array:
            m_z_values.append(m_z)
            gamma_z_values.append(gamma_z)
            chi_square_values.append(chi_square(data, [m_z, gamma_z], gamma_ee_unknown=False))

    m_z_values = np.array(m_z_values)
    gamma_z_values = np.array(gamma_z_values)
    chi_square_values = np.array(chi_square_values)

    fig_3d = plt.figure()
    plt.rcParams["font.family"] = 'times new roman'
    ax_3d = fig_3d.gca(projection='3d')
    ax_3d.set_title('Chi squared surface')
    ax_3d.set_zlabel('chi squared')
    ax_3d.plot_trisurf(m_z_values, gamma_z_values, chi_square_values,
                       linewidth=0.2, antialiased=True)
    ax_3d.set_xlabel('mass of z boson')
    ax_3d.set_ylabel('width of z boson')

    i = 1
    while True:
        folder = "SavedFigures"
        try:
            mkdir(folder)
        except FileExistsError:
            pass
        fig_name = f'ZBoson_chi_square_surface({i}).png'
        if not exists(f'{folder}/{fig_name}'):
            plt.savefig(f'{folder}/{fig_name}', dpi=300)
            break
        i += 1
    plt.show()


def plot_fit(data, popt, func=cross_section, gamma_ee_unknown=False):
    """
    Plots and saves the best fit line alongside the data points.
    Also displays the residuals of the fit. Plots are saved in the
    'SavedFigures' folder in the same directory as the script.

    :param data: np.array of data
    :param popt: np.array of fitted parameters
    :param func: the expected distribution function
    :param gamma_ee_unknown: True if option to treat partial width of electron-positron
                             as a free parameter was selected, False otherwise

    :return: None
    """

    energy_space = np.linspace(data[0, 0], data[-1, 0], 1000)
    if len(popt) == 2:
        mode = 'default'
        y_fit = func(energy_space, popt[0], popt[1])
        y_residuals = data[:, 1] - func(data[:, 0], popt[0], popt[1])
    elif len(popt) == 3 and gamma_ee_unknown:
        mode = 'gamma_ee_unknown'
        y_fit = func(energy_space, popt[0], popt[1], popt[2], popt[2])
        y_residuals = data[:, 1] - func(data[:, 0], popt[0], popt[1], popt[2], popt[2])
    else:
        mode = 'different_decay'
        y_fit = func(energy_space, popt[0], popt[1], popt[2])
        y_residuals = data[:, 1] - func(data[:, 0], popt[0], popt[1], popt[2])

    # _, [ax1, ax2] = plt.subplots(nrows=2, ncols=1, figsize=(8, 9))
    fig = plt.figure(figsize=(8, 9))
    grid_spec = plt.GridSpec(3, 3, figure=fig, hspace=0)
    ax1 = fig.add_subplot(grid_spec[0:2, :])
    ax2 = fig.add_subplot(grid_spec[2, :])
    plt.rcParams["font.family"] = 'times new roman'

    ax1.set_title('Cross section best fit to filtered data', y=1.08)
    ax1.set_ylabel('Cross section (nb)')
    ax1.set_xticks([])
    ax1.errorbar(data[:, 0], data[:, 1], yerr=data[:, 2], fmt='.',
                 capsize=2, elinewidth=0.3, label='filtered data')
    ax1.plot(energy_space, y_fit, label='Breit-Wigner fit', color='orange')
    ax1.legend()

    ax2.set_xlabel('Energy (GeV)')
    ax2.set_ylabel('Residuals (nb)')
    ax2.errorbar(x=data[:, 0], y=y_residuals, yerr=data[:, 2], fmt='.',
                 capsize=2, elinewidth=0.3, label='residuals')
    ax2.hlines(y=0, xmin=data[0, 0], xmax=data[-1, 0], colors='orange')
    ax2.legend()

    i = 1
    while True:
        folder = "SavedFigures"
        try:
            mkdir(folder)
        except FileExistsError:
            pass
        fig_name = f'ZBoson_fit_plot_{mode}({i}).png'
        if not exists(f'{folder}/{fig_name}'):
            plt.savefig(f'{folder}/{fig_name}', dpi=300)
            break
        i += 1
    plt.show()


def collect_results(popt, pcov, chi_squared_red, gamma_ee_unknown):
    """
    Calculates and formats the output values before saving them to a
    message to be displayed to the user in the graphical interface.

    :param popt: np.array of fitted parameters
    :param pcov: np.array of covariance matrix
    :param chi_squared_red: float - minimised value of chi squared
    :param gamma_ee_unknown: True if option to treat partial width of electron-positron
                             as a free parameter was selected, False otherwise

    :return: string - message containing the final results in the correct format
    """

    m_z = popt[0]
    sigma_m_z = pcov[0, 0] ** 0.5
    gamma_z = popt[1]
    sigma_gamma_z = pcov[1, 1] ** 0.5
    tau = H_BAR / gamma_z
    sigma_tau = sigma_gamma_z * (tau/gamma_z)

    message = ''
    message += f'Mass of Z Boson = {m_z:.3e} +/- {sigma_m_z:.1e} GeV/c^2\n\n'
    message += f'Width of Z Boson = {gamma_z:.3e} +/- {sigma_gamma_z:.1e} GeV\n\n'
    if len(popt) == 3 and gamma_ee_unknown:
        gamma_ee = popt[2]
        sigma_gamma_ee = pcov[2, 2] ** 0.5
        message += f'Partial width for electron-positron = {gamma_ee:.3e} +/- ' \
                   f'{sigma_gamma_ee:.1e} GeV\n\n'
    elif len(popt) == 3:
        gamma_pp = popt[2]
        sigma_gamma_pp = pcov[2, 2] ** 0.5
        message += f'Partial width for new decay = {gamma_pp:.3e} +/- {sigma_gamma_pp:.1e} GeV\n\n'
    message += f'Lifetime of Z Boson = {tau:.2e} +/- {sigma_tau:.1e} s\n\n'
    message += f'Reduced chi squared = {chi_squared_red:.3f}'

    return message


def run_analysis(data, different_decay, gamma_ee_unknown, custom_gamma=0.01):
    """
    Function which is called in the main loop of the script to conduct the analysis
    by running the previously defined functions in the right order.

    :param data: np.array of data
    :param different_decay: True if option to analyse new decay products was selected,
                            False otherwise
    :param gamma_ee_unknown: True if option to treat partial width of electron-positron
                             as a free parameter was selected, False otherwise
    :param custom_gamma: float - user's guess for the optional partial widths

    :return: the formatted message from the collect_results function
    """
    if custom_gamma is None:
        data, popt, pcov, gamma_ee_unknown = fit_to_data(data, different_decay, gamma_ee_unknown)
    else:
        data, popt, pcov, gamma_ee_unknown = fit_to_data(data, different_decay,
                                                         gamma_ee_unknown, float(custom_gamma))
    chi_squared_red = chi_square(data, popt, gamma_ee_unknown)/(len(data) - len(popt))
    message = collect_results(popt, pcov, chi_squared_red, gamma_ee_unknown)
    plot_fit(data, popt, gamma_ee_unknown=gamma_ee_unknown)
    if len(popt) == 2:
        plot_parameter_surface(data, popt, pcov)

    return message


def main():
    """
    The main loop of the script.

    :return: 0
    """
    window = Tk()

    class InputWindow:
        """
        Class defining the behaviour and appearance of the graphical interface.
        """

        def __init__(self, win):
            self.emphasis = ('default', '14', 'bold')
            self.files_selected_msg = Label(win, text="Files selected!")
            self.files = []
            self.data = []
            self.sel_1 = StringVar()
            self.selection_1 = Label(win, text="Please select the files to be used.",
                                     font=self.emphasis)
            self.selection_1.place(x=30, y=50)
            self.sel_1.set("Use default files")
            self.file_options = ("Use default files", "Choose different files")
            self.file_choice = Combobox(win, values=self.file_options, state='readonly')
            self.file_choice.bind('<<ComboboxSelected>>', self.allow_file_input)
            self.file_choice.place(x=30, y=80)
            self.files_selected = StringVar()
            self.input_files = Button(text="Choose files...", state='disabled',
                                      command=self.get_files)
            self.input_files.place(x=300, y=80)

            self.ask_new_decay = StringVar()
            self.selection_2 = Label(win, text="Do you want to consider a a different process in"
                                               "which the electron and positron decay via the"
                                               "Z-boson into new particles? (requires new data"
                                               "file(s))", font=self.emphasis)
            self.selection_2.place(x=30, y=120)
            self.sel_2 = BooleanVar()
            self.sel_2.set(False)
            self.sel_2_true = Radiobutton(win, text="Consider a new decay", value=True,
                                          variable=self.sel_2, command=self.allow_gamma_pp)
            self.sel_2_false = Radiobutton(win, text="Use the default setup", value=False,
                                           variable=self.sel_2, command=self.allow_gamma_pp)
            self.sel_2_true.place(x=30, y=150)
            self.sel_2_false.place(x=400, y=150)
            self.sel_2_valid = Label(text='valid input', fg='green')
            self.sel_2_invalid = Label(text='invalid input', fg='red')
            self.gamma_pp_label = Label(win, text="Enter your guess for gamma_decay here [GeV]:")
            self.gamma_pp_label.place(x=30, y=180)
            self.gamma_pp = StringVar()
            self.gamma_pp_input = Entry(textvariable=self.gamma_pp, state='disabled')
            self.gamma_pp_input.place(x=330, y=180)

            self.selection_3 = Label(win, text="Do you want to treat gamma_ee as a free "
                                               "parameter? (only possible if 'different "
                                               "decay product' option was NOT selected)",
                                     font=self.emphasis)
            self.selection_3.place(x=30, y=220)
            self.sel_3 = BooleanVar()
            self.sel_3.set(False)
            self.sel_3_true = Radiobutton(win, text="Treat gamma_ee as free parameter",
                                          variable=self.sel_3, value=True,
                                          command=self.allow_gamma_ee)
            self.sel_3_false = Radiobutton(win, text="Use the default value (0.08391 GeV)",
                                           variable=self.sel_3, value=False,
                                           command=self.allow_gamma_ee)
            self.sel_3_true.place(x=30, y=250)
            self.sel_3_false.place(x=400, y=250)
            self.sel_3_valid = Label(text='valid input', fg='green')
            self.sel_3_invalid = Label(text='invalid input', fg='red')
            self.gamma_ee_label = Label(win, text="Enter your guess for gamma_ee here [GeV]:")
            self.gamma_ee_label.place(x=30, y=280)
            self.gamma_ee = StringVar()
            self.gamma_ee_input = Entry(textvariable=self.gamma_ee, state='disabled')
            self.gamma_ee_input.place(x=330, y=280)

            self.confirm_button = Button(win, text="Confirm Selection",
                                         command=self.confirm_selection)
            self.confirm_button.place(x=30, y=350)

            self.default_button = Button(win, text="Use default settings",
                                         command=self.run_default)
            self.default_button.place(x=150, y=350)

            self.exit_button = Button(win, text="Exit", command=self.exit_program)
            self.exit_button.place(x=282, y=350)

            self.program_information = Label(win, text="Program's current status:",
                                             font=self.emphasis)
            self.program_information.place(x=30, y=420)

            self.messages = []
            self.displayed_messages = []
            self.message_counter = 0
            self.display_message('The program has started.')
            self.output_area = Label(text='Fitting results:', font=self.emphasis)
            self.output_area.place(x=500, y=420)
            self.output = Label(text='')
            self.output.place(x=500, y=450)

        def display_message(self, message):
            """
            Displays a message to the user.

            :param message: string - the message to be displayed

            :return: None
            """
            self.messages.insert(0, message)
            self.displayed_messages.insert(0, Label(text=f'[{self.message_counter}]  {message}'))
            self.message_counter += 1
            while len(self.displayed_messages) > 6:
                self.displayed_messages[-1].place(x=0, y=-150)
                del self.displayed_messages[-1]
            for i in range(len(self.displayed_messages)):
                self.displayed_messages[i].place(x=30, y=450+(40*i))

        def confirm_selection(self):
            """
            Checks whether the provided settings are correct and then runs the
            analysis according to them.

            :return: None
            """
            correct = True
            if self.sel_2.get():
                self.sel_3_valid.place(x=-100, y=180)
                self.sel_3_invalid.place(x=-100, y=180)
                correct = check_numerical_input(self.gamma_pp.get())
                if correct:
                    self.sel_2_valid.place(x=550, y=180)
                    self.sel_2_invalid.place(x=-100, y=180)
                    self.display_message('Running the script...')
                    self.data, message = read_data(self.files)
                    self.display_message(message)
                    output = run_analysis(self.data, self.sel_2.get(), self.sel_3.get(),
                                          self.gamma_pp.get())
                    self.show_output(output)
                else:
                    self.display_message('Invalid input provided.')
                    self.sel_2_valid.place(x=-100, y=180)
                    self.sel_2_invalid.place(x=550, y=180)
            elif self.sel_3.get():
                self.sel_2_valid.place(x=-100, y=180)
                self.sel_2_invalid.place(x=-100, y=180)
                correct = check_numerical_input(self.gamma_ee.get())
                if correct:
                    self.sel_3_valid.place(x=550, y=280)
                    self.sel_3_invalid.place(x=-100, y=280)
                    self.display_message('Running the script...')
                    if self.sel_1.get() == "Use default files":
                        self.data, message = read_data(FILE_NAMES)
                    else:
                        self.data, message = read_data(self.files)
                    self.display_message(message)
                    output = run_analysis(self.data, self.sel_2.get(), self.sel_3.get(),
                                          self.gamma_ee.get())
                    self.show_output(output)
                else:
                    self.display_message('Invalid input provided.')
                    self.sel_3_valid.place(x=-100, y=280)
                    self.sel_3_invalid.place(x=550, y=280)

        def get_files(self):
            """
            Uses the default file explorer to allow the user to pick the data files
            and then passes them on to read_data function before assigning the data
            to a variable.

            :return: None
            """
            self.files = askopenfilenames()
            try:
                self.data, message = read_data(self.files)
                self.display_message(message)
                self.files_selected_msg.place(x=400, y=80)
            except IndexError:
                self.display_message('The selected files are not compatible with the script.')

        def allow_file_input(self, event):
            """
            Disables or enables the option to choose files other than the default based
            on user's choices.

            :return: None
            """
            choice = self.file_choice.get()
            if choice == "Choose different files":
                self.input_files = Button(text="Choose files...", state='normal',
                                          command=self.get_files)
                self.input_files.place(x=300, y=80)
            else:
                self.input_files = Button(text="Choose files...", state='disabled',
                                          command=self.get_files)
                self.input_files.place(x=300, y=80)
                self.sel_2_true.deselect()
                self.sel_2_false.select()
                self.gamma_pp_input = Entry(textvariable=self.gamma_pp, state='disabled')
                self.gamma_pp_input.place(x=330, y=180)

        def allow_gamma_pp(self):
            """
            Disables or enables the entry box for the guess of the partial width for a new decay if
            the user chooses this option. Additionally, forces the user to choose new files
            as required for this analysis to run correctly.

            :return: None
            """
            choice = self.sel_2.get()
            if choice:
                self.gamma_pp_input = Entry(textvariable=self.gamma_pp, state='normal')
                self.gamma_pp_input.place(x=330, y=180)
                self.sel_3_true.deselect()
                self.sel_3_false.select()
                self.gamma_ee_input = Entry(textvariable=self.gamma_ee, state='disabled')
                self.gamma_ee_input.place(x=330, y=280)
                self.file_choice.set("Choose different files")
                self.input_files = Button(text="Choose files...", state='normal',
                                          command=self.get_files)
                self.input_files.place(x=300, y=80)
            else:
                self.gamma_pp_input = Entry(textvariable=self.gamma_pp, state='disabled')
                self.gamma_pp_input.place(x=330, y=180)

        def allow_gamma_ee(self):
            """
            Disables or enables the entry box for the guess of the partial width for
            electron-positron. Does not allow the box to be enabled if the option
            "new decay products" is selected.

            :return: None
            """
            choice = self.sel_3.get()
            different_decay = self.sel_2.get()
            if choice and not different_decay:
                self.gamma_ee_input = Entry(textvariable=self.gamma_ee, state='normal')
                self.gamma_ee_input.place(x=330, y=280)
            else:
                self.gamma_ee_input = Entry(textvariable=self.gamma_ee, state='disabled')
                self.gamma_ee_input.place(x=330, y=280)
                self.sel_3_false.select()
                self.sel_3_true.deselect()

        def run_default(self):
            """
            Runs the analysis with the default settings.

            :return: None
            """
            self.display_message('Running the script...')
            self.data, message = read_data(FILE_NAMES)
            self.display_message(message)
            output = run_analysis(self.data, False, False)
            self.show_output(output)

        def show_output(self, output):
            """
            Displays the formatted message with the numerical results of the analysis.

            :param output: string - the results of analysis

            :return: None
            """
            self.display_message('The plots have been saved in the same directory as the script.')
            self.output = Label(text=output, justify='left')
            self.output.place(x=500, y=450)

        def exit_program(self):
            """
            Allows the user to exit the program.

            :return: 0
            """
            self.display_message('The program is closing...')
            sys.exit(0)

    _ = InputWindow(window)
    window.title('Z Boson Settings')
    window.geometry("1100x700+100+100")

    window.mainloop()


if __name__ == "__main__":
    main()
