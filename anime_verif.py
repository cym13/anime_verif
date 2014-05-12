#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Cédric Picard
#
# LICENSE
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# END_OF_LICENSE
#

"""
Check size anomalies and episode numbers sequence.

Usage: anime_verif.py [-a N] [-s|-n] DIRECTORY

Options:
    -a, --accuracy N    Do not show files whose size deviation is less than N
                        times the standart deviation. Default is 3.
    -s, --size          Check size only
    -n, --numbers       Check episode numbers only

If -s and -n are missing or if -s and -n are used together, size and numbers
are both checked.
"""

import os
import math
import re
from docopt import docopt

def extract_numbers(filename):
    """
    Extract the numbers present in `filename'..
    """
    numbers = re.compile(r'[0-9]+')
    return [ int(x) for x in numbers.findall(filename)  ]

def size_check(size_list, file_list, accuracy):
    """
    Detect 0-sized files and size anomalies.
    """

    if 0 in size_list:
        print('Presence of files of size 0')
        return False

    # Smooth data to the MB order
    size_list = [ math.floor(x / 1024**2) for x in size_list ]

    # Set the average size and the variance for statistical size study
    average_size = sum(size_list) / len(size_list)
    var = sum({(x - average_size) ** 2 for x in size_list}) / len(size_list)

    # Detect size anomalies
    file_token = 0
    for size in size_list:
        if (size - average_size) ** 2 > accuracy * var and size < average_size:
            print('Size anomaly detected: ' + \
                    file_list[file_token].encode('utf-8'))
            return False

        file_token += 1

    # If the directory passed all size tests:
    return True


def ep_numbers_check(file_list):
    """
    Check that all episode numbers are following each other.
    Rely on alphanumeric naming order.
    """
    file_list.sort()

    for index in range(1, len(file_list)):
        prev_numbers = extract_numbers(file_list[index - 1])

        follow = False
        for each in extract_numbers(file_list[index]):
            if (each - 1) in prev_numbers:
                follow = True

        if not follow:
            return False

    return True


if __name__ == '__main__':
    arguments = docopt(__doc__)
    # Set default options
    if arguments['--accuracy']:
        accuracy = float(arguments['--accuracy'])
    else:
        accuracy = 5

    if not arguments['--size'] and not arguments['--numbers']:
        arguments['--size']    = True
        arguments['--numbers'] = True

    target_dir = arguments['DIRECTORY'].decode('utf-8')

    if not os.path.isdir(target_dir):
        print('This is not a directory: ' + target_dir.encode('utf-8'))
        os.sys.exit(1)
    os.chdir(target_dir)

    size_list = []
    file_list = []
    for each in os.listdir('.'):
        if os.path.isfile(each.decode('utf-8')):
            size_list.append(os.path.getsize(each.decode('utf-8')))
            file_list.append(each.decode('utf-8'))

    if size_list == []:
        print('No file found in directory: ' + target_dir.encode('utf-8'))
        os.sys.exit(1)

    if arguments['--size'] and not size_check(size_list, file_list, accuracy):
        os.sys.exit(1)

    if arguments['--numbers'] and not ep_numbers_check(file_list):
        print('Some episodes may be missing:' + target_dir.encode('utf-8'))
        os.sys.exit(1)
