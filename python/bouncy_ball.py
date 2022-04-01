# -*- coding: utf-8 -*-
"""
________________TITLE________________
PHYS20161 - Assignment 1 - Bouncy Ball
-------------------------------------
This python script evaluates the bouncy ball problem:
A ball starts at a given height and is allowed to fall freely.
It then bounces off the ground with a new velocity given by the coefficient
eta (from energy loss) multiplied by the velocity at contact.
The goal is to find the number of bounces of the ball above
some minimum height and the time taken for that.

User can use this script to solve a single setup of the
problem or multiple setups at once (by inputting many values
at once separated by whitespaces). By default, user will decide
the initial height(s), minimum height(s) and eta coefficient(s).
In the further customisation settings, the user can decide to change the value
of gravitational acceleration, save the results to a csv file,
show the results in a table form instead of a text form and show the plot.

At the end the script shows the calculated values and performs any additional
operations as decided by the user in the customisation settings.

Last Updated: 22/10/21
@author: M. J. Michałowski UID: 10450192
"""

from math import log, floor, sqrt
import re
import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# SI units
GRAVITY_ACCELERATION = 9.81


def user_binary_decision(request, option_true='yes', option_false='no'):
    """
    Presents the user with two options as given by the arguments and then
    asks them to choose their preference. User input can only be one of the
    two options, otherwise the user will be asked to pick an option again.

    Returns a boolean value based on whichever option was chosen.

    :request: string
    :option_true: string
    :option_false: string
    """
    while True:
        user_decision = input(f'{request} [{option_true}/{option_false}]: ')
        if user_decision == option_true:
            print()
            return True
        if user_decision == option_false:
            print()
            return False

        print(f'Sorry, your input was not recognised as a valid option. '
              f'Please type "{option_true}" or "{option_false}" only.')


def numerical_input(variable_information=('name', 'unit'), variable_bounds=None,
                    accept_blank=False, default_value=None, list_length=None):
    """
    Accepts and validates user input based on the provided parameters.
    If the input does not conform to the requirements, the user is asked
    to input it again.

    Returns the validated input cast into a list.

    :variable_information: 2-tuple of strings
    :variable_bounds: list of 2-tuples of floats
    :accept_blank: bool
    :default_value: float
    :list_length: int
    """
    if variable_bounds is None:
        variable_bounds = [(0, np.inf)]
    var_name = variable_information[0]
    var_unit = variable_information[1]

    while True:
        if accept_blank:
            variable_values = input(f'Please enter the {var_name} [{var_unit}] (blank input will '
                                    f'result in a default value of {default_value} being used): ')
            if variable_values == '':
                return default_value

        else:
            variable_values = input(f'Please enter the {var_name} [{var_unit}]: ')

        try:
            variable_values = [float(_) for _ in variable_values.split()]
        except ValueError:
            print('\nOnly floats separated by whitespace are accepted.')
            continue

        if list_length is not None and len(variable_values) != list_length:
            print('\nIncorrect number of values. Please input '
                  f'exactly {list_length} value(s).')
            continue
        if list_length is None and len(variable_values) > 1:
            variable_bounds = [variable_bounds[0] for _ in range(len(variable_values))]

        for i, value in enumerate(variable_values):
            if not variable_bounds[i][0] < value < variable_bounds[i][1]:
                print(f"\nThe value of {value} (index = {i}) in "
                      f"{var_name} is out of bounds. Please input a value between"
                      f" {variable_bounds[i][0]} and {variable_bounds[i][1]}.")
                break
            if i == len(variable_values) - 1:
                return variable_values


def evaluate_bounces(acceleration, eta, initial_height, minimum_height):
    """
    Evaluates the bouncing ball problem analytically based on provided parameters.

    Returns the number of bounces (int) and the time taken for the ball to reach a peak
    just below the minimum height (float).

    :acceleration: float
    :eta: float
    :initial_height: float
    :minimum_height: float
    """

    number_of_bounces = log(minimum_height/initial_height)/log(eta)
    if number_of_bounces == floor(number_of_bounces):
        number_of_bounces = floor(number_of_bounces) - 1
    else:
        number_of_bounces = floor(number_of_bounces)

    time_elapsed = (2*initial_height/acceleration)**0.5
    for i in range(1, number_of_bounces+1):
        time_elapsed += 2 * (2*initial_height*(eta**i)/acceleration)**0.5

    return number_of_bounces, time_elapsed


def display_table_results(table):
    """
    Takes a pandas dataframe of results as an input and formats it before
    displaying it to the user.

    :table: pandas dataframe
    """
    pd.set_option('display.max_columns', None)
    column_formatting = {'Time [s]': '{:0.2f}', 'Number of Bounces': '{:0.0f}'}
    for column, formatting in column_formatting.items():
        table[column] = table[column].map(lambda _: formatting.format(_))

    print(table)


def save_to_csv(table):
    """
    Asks the user for the desired csv file name to which the results
    will be saved and validates that this name is allowed and not already
    in use in the same directory as this script.

    Given a validated file name it saves the provided pandas dataframe
    of results as {user_file_name}.csv.

    :table: pandas dataframe
    """
    allowed_file_name = r"[\w]+$"
    while True:
        while True:
            user_file_name = input('Please enter the name for the csv file:')
            if not re.match(allowed_file_name, user_file_name):
                print('The name is invalid. Please enter a valid file name.')
            else:
                break
        try:
            with open(f'{user_file_name}.csv', 'x') as new_file:
                table.to_csv(new_file)
            break
        except FileExistsError:
            print('Sorry, the chosen file name is already used. Choose a different one.')


def customise_settings():
    """
    The function runs when user selects to customise the output of this
    script further. It allows them to choose to change the value of gravitational
    acceleration, save results to a csv file, display results as a table instead of
    text and display the plot.

    Returns four boolean values which correspond to the decision of the user
    regarding each customisation option.
    """
    gravity_acceleration = numerical_input(('gravitational acceleration', 'm/s^2'),
                                           accept_blank=True, list_length=1,
                                           default_value=[GRAVITY_ACCELERATION])
    print()

    display_plot = user_binary_decision(request='Would you like to display the plot of ball motion?'
                                                ' (if solving for multiple setups only'
                                                ' the first one will be shown)')

    display_text_results = user_binary_decision(request='Would you like to display the '
                                                        'results in a text form or in '
                                                        'a table?',
                                                option_true='text', option_false='table')

    save_results_to_csv = user_binary_decision(request="Would you like to save the "
                                                       "result(s) to a csv file?")

    return gravity_acceleration, display_plot, display_text_results, save_results_to_csv


def show_plot(number_of_bounces, eta_coefficient, acceleration,
              max_height, min_height):
    """
    Displays the plot of the motion of the ball based on input parameters.
    The last displayed peak is just below the minimum height. Offers user the
    choice to display a higher resolution plot and/or save the plot to
    a png file (in which case the user inputs a file name which is then
    validated before saving).

    :number_of_bounces: int
    :eta_coefficient: float
    :acceleration: float
    :max_height: float
    :min_height: float
    """
    time_step = 1 / (50 * acceleration)
    time_of_bounce = [sqrt(2 * max_height / acceleration)]
    time = np.arange(0, time_of_bounce[0] + time_step, time_step)
    height_path = -0.5 * acceleration * time**2 + max_height

    for i in range(1, int(number_of_bounces)+2):
        time_of_bounce.append(sqrt(2 * (eta_coefficient**i) * max_height / acceleration))
        time_temporary = np.arange(-time_of_bounce[i], time_of_bounce[i] + time_step, time_step)

        height_path_temporary = (-0.5 * acceleration * time_temporary**2) \
                                + (max_height * eta_coefficient**i)
        time_temporary = time_temporary + time_of_bounce[0] \
                         + 2*sum(time_of_bounce[1:i]) + time_of_bounce[i]

        time = np.concatenate((time, time_temporary), axis=None)
        height_path = np.concatenate((height_path, height_path_temporary), axis=None)

    display_higher_resolution = user_binary_decision(request='Do you want to display a'
                                                             ' higher resolution plot'
                                                             ' (may take longer to display)?',
                                                     option_true='yes',
                                                     option_false='no')
    if display_higher_resolution:
        plt.figure(dpi=1200)
    else:
        plt.figure()

    plt.rcParams["font.family"] = 'times new roman'
    plt.plot(time, height_path, color='black', label='Height over time')
    plt.title("Ball motion")
    plt.xlabel("Time [s]")
    plt.ylabel("Height [m]")
    plt.axhline(min_height, ls='--', linewidth=0.8, color='red', label='Minimum height')
    plt.xlim([0, time[-1]])
    plt.ylim([0, max_height])
    plt.legend()
    if min_height <= max_height/500:
        plt.figtext(s='Note: minimum height is much less than initial height', x=0.01, y=0.97)

    save_plot = user_binary_decision(request='Do you want to save the plot as png file?',
                                     option_true='yes',
                                     option_false='no')
    if save_plot:
        allowed_file_name = r"[\w]+$"
        while True:
            user_file_name = input('Please enter the name for the png file:')
            if not re.match(allowed_file_name, user_file_name):
                print('The name is invalid. Please enter a valid file name.')
            elif os.path.isfile(f'./{user_file_name}.png'):
                print('Sorry, the chosen name is already in use. Please'
                      ' enter a different name.')
            else:
                break
        print("Saving the plot...\n")
        plt.savefig(f'{user_file_name}.png', dpi=1200)

    print("Displaying the plot...\n")
    plt.show()


def main():
    """
    Executes the main body of the script.

    It is contained in a function so that it only executes if
    the script is run directly and not if it is imported.
    """
    customisation_status = user_binary_decision(request='Would you like to see the '
                                                        'customisation options?',)
    print("Make sure that inputs for variables are floats.\n")
    if customisation_status:
        custom_settings = customise_settings()
        gravity_acceleration = custom_settings[0][0]
        display_plot = custom_settings[1]
        display_text_results = custom_settings[2]
        save_results_to_csv = custom_settings[3]
    else:
        gravity_acceleration = GRAVITY_ACCELERATION
        display_plot = False
        display_text_results = True
        save_results_to_csv = False

    print('If you want to input values for multiple setups at once '
          'please ensure they are separated by whitespaces. '
          '(eg.: 12 1300 14 205)\n')
    initial_heights = numerical_input(('initial height(s)', 'm'))
    list_length = len(initial_heights)

    print("\nThe minimum height(s) should be bigger than 0 and less than"
          " the corresponding initial height(s).")
    minimum_height_bounds = [(0, initial_heights[i]) for i in range(list_length)]
    minimum_heights = numerical_input(('minimum height(s)', 'm'),
                                      minimum_height_bounds, list_length=list_length)

    print("\nThe eta coefficient(s) should be bigger than 0 and less than 1.\n")
    eta_bounds = [(0, 1) for _ in range(len(initial_heights))]
    eta_coefficients = numerical_input(('eta coefficient(s)', 'dimensionless'),
                                       eta_bounds, list_length=list_length)
    print()

    table_of_results = pd.DataFrame(columns=['Initial Height [m]', 'Minimum Height [m]', 'Eta',
                                             'Number of Bounces', 'Time [s]'])
    for i in range(list_length):
        number_of_bounces, time_elapsed = evaluate_bounces(acceleration=gravity_acceleration,
                                                           eta=eta_coefficients[i],
                                                           initial_height=initial_heights[i],
                                                           minimum_height=minimum_heights[i])

        table_of_results.loc[i] = [initial_heights[i], minimum_heights[i], eta_coefficients[i],
                                   number_of_bounces, time_elapsed]
        if display_text_results:
            print(f'Initial Height = {initial_heights[i]}m ; Minimum Height = {minimum_heights[i]}m'
                  f' ; Eta = {eta_coefficients[i]}')
            print(f'The ball will bounce {number_of_bounces} times in {time_elapsed:0.2f}s.\n')

    if not display_text_results:
        display_table_results(table_of_results)

    if save_results_to_csv:
        save_to_csv(table_of_results)

    if display_plot:
        print("Generating the plot... (this can take a long time "
              "if the numbers involved are large)")
        show_plot(number_of_bounces=table_of_results.at[0, 'Number of Bounces'],
                  eta_coefficient=table_of_results.at[0, 'Eta'],
                  acceleration=gravity_acceleration,
                  max_height=table_of_results.at[0, 'Initial Height [m]'],
                  min_height=table_of_results.at[0, 'Minimum Height [m]'])

    sys.exit()


if __name__ == '__main__':
    main()
