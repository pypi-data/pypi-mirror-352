#!/bin/bash

prepend_path() {
    local path="$1"
    if ! echo $PATH | tr ':' '\n' | grep -x $path > /dev/null; then
        export PATH=$path:$PATH
    fi
}

prepend_python_path() {
    local path="$1"
    if ! echo $PYTHONPATH | tr ':' '\n' | grep -x $path > /dev/null; then
        export PYTHONPATH=$path:$PYTHONPATH
    fi
}

prepend_module_path() {
    local path="$1"
    if ! echo $MODULEPATH | tr ':' '\n' | grep -x $path > /dev/null; then
        module use $path
    fi
}

load_module() {
    local name="$1"
    if ! echo $LOADEDMODULES | tr ':' '\n' | grep -x $name > /dev/null; then
        module load $name
    fi
}

get_script_dir() {
    cd "$(dirname "${BASH_SOURCE[1]}")" && pwd
}
