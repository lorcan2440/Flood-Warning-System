#!/bin/bash

# use: $ ./runtasks.sh

for py_file in $(find 'tasks' -name '*.py')
do
    python $py_file
done