'''
This script is called at the start of every test file to
allow the source files (which are in a different parent
directory) to be imported from the test files.
'''

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
