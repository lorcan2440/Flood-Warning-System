'''
This script is called at the start of every test and task
file to allow the source files (which are in a different
parent directory) to be imported from the test files.
'''

from os.path import dirname, realpath
import sys

sys.path.append(dirname(dirname(realpath(__file__))))
