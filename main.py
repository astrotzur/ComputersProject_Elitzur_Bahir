# This program returns the best linear fit coefficients for a data set.
# The linear function is of the form y = ax + b where y is the dependent
# variable and x is the independent one.
# The printout is the value of 'a' +- the error of 'a' and the same for
# the 'b' coefficient on the next line.
# The next two lines are χ² and χ²reduced
# Also a plot of the data points (error bars included) and the fitted line
# is created as an SVG file named 'linear_fit.svg'

import numpy as np
import matplotlib.pyplot as plt


def tablemaker(arr):
    # receives a list of lines that correspond to the data set
    # checks data for validity (returns error string if necessary)
    # returns a 2D list of te form [['dx',...],['dy',...],['x',...],['y',...]]
    arr = list(map(str.split, arr))
    if len(set(map(len, arr))) != 1:
        return 'Input file error: Data lists are not the same length.'

    # ↓ Checking whether the received data is in rows or in columns
    column = (set(arr[0]) == {'x', 'y', 'dx', 'dy'})
    rows_num = len(arr[0]) if column else len(arr)
    columns_num = len(arr) if column else len(arr[0])

    # ↓ Creating a 2D list to store the data in rows
    result = [[0] * columns_num for i in range(rows_num)]
    for i in range(rows_num):
        for j in range(columns_num):
            val = arr[j][i] if column else arr[i][j]  # Transposing if needed
            if j > 0: val = float(val)
            if ((j > 0) and (val <= 0)) and ('d' in result[i][0]):
                return 'Input file error: Not all uncertainties are positive.'
            result[i][j] = val
    result.sort()
    return result


def fit_linear(filename):
    file_pointer = open(filename, 'r')
    data = file_pointer.read()

    # Creating a list with ['x axis:name[unit]','y axis:name[unit]']
    labels_arr = data.strip().split('\n')[-2:]
    labels_arr.sort()

    data = data.strip().lower().split('\n')
    table = tablemaker(data[:data.index('')])
    if 'str' in str(type(table)):
        return table    # Abortion due to an error during table creation
    N = len(table[0]) - 1   # N is the amount of data points
    dx, dy, x, y = table[0][1:], table[1][1:], table[2][1:], table[3][1:]

    # Formulae taken from Bevington and Robinson Ch. 6 (p. 114) ─────────────┐
    # dy is the sigma (the y uncertainty)
    sum_x2_s2 = sum([(x[i] / dy[i]) ** 2 for i in range(N)])
    sum_1_s2 = sum([(1 / dy[i]) ** 2 for i in range(N)])
    sum_x_s2 = sum([(x[i] / (dy[i] ** 2)) for i in range(N)])
    sum_y_s2 = sum([(y[i] / (dy[i] ** 2)) for i in range(N)])
    sum_xy_s2 = sum([(x[i] * y[i] / (dy[i] ** 2)) for i in range(N)])
    delta = sum_1_s2 * sum_x2_s2 - sum_x_s2 ** 2
    a = round((sum_1_s2 * sum_xy_s2 - sum_x_s2 * sum_y_s2) / delta, 15)
    b = round((sum_x2_s2 * sum_y_s2 - sum_x_s2 * sum_xy_s2) / delta, 15)
    da = round((sum_1_s2 / delta) ** 0.5, 17)
    db = round((sum_x2_s2 / delta) ** 0.5, 17)
    chi2 = round(sum([((y[i] - b - a * x[i])/dy[i])**2 for i in range(N)]),15)
    chi2_red = round(chi2 / (N - 2), 15)
    # ───────────────────────────────────────────────────────────────────────┘

    # Plot creation section ─────────────────────────────────────────────────┐
    x, y = np.array(x), np.array(y)
    yerr, xerr = np.array(dy), np.array(dx)
    plt.figure()
    plt.errorbar(x, y, yerr, xerr, fmt='b,')
    plt.xlabel(labels_arr[0][labels_arr[0].index(':') + 2:])
    plt.ylabel(labels_arr[1][labels_arr[1].index(':') + 2:])
    plt.plot(x, (a * x + b), 'r')
    plt.savefig(fname='linear_fit.svg')
    # ───────────────────────────────────────────────────────────────────────┘

    result = 'a = {} +- {}\n\nb = {} +- {}\n\n'.format(a, da, b, db)
    result += 'chi2 = {}\n\nchi2_reduced  = {}'.format(chi2, chi2_red)
    return result

# for local testing purposes
# print(fit_linear('/Users/astro/PycharmProjects/test01/input.txt'))
