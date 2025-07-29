__find_tnr() {
    TNR_PATH=$(which tnr)
    if [ -z "$TNR_PATH" ]; then
        TNR_PATH=$(find ~/.local/bin /usr/local/bin -name tnr -type f -print -quit 2>/dev/null)
    fi
    echo "$TNR_PATH"
}

__define_tnr_activated() {
    tnr() {
        if [ -z "${__TNR_BINARY_PATH}" ]; then
            export __TNR_BINARY_PATH=$(__find_tnr)
        fi
        "$__TNR_BINARY_PATH" "$@"
        
        # If device command was successful
        if [ "$1" = "device" ] && [ $? -eq 0 ]; then
            PS1="(⚡$($__TNR_BINARY_PATH device --raw)) $__DEFAULT_PS1"
        elif [ "$1" = "deactivate" ]; then
            PS1="$__DEFAULT_PS1"
            unset LD_PRELOAD
            __define_tnr_deactivated
        fi
    }
}

__define_tnr_deactivated() {
    tnr() {
        if [ -z "${__TNR_BINARY_PATH}" ]; then
            export __TNR_BINARY_PATH=$(__find_tnr)
        fi
        if [ "$1" = "activate" ]; then
            # TODO: Prompt user to login if not already logged in (right now it silently waits)
            output=$($__TNR_BINARY_PATH creds)
            exit_code=$?

            if [ $exit_code -eq 0 ]; then
                export __DEFAULT_PS1=$PS1
                device=$($__TNR_BINARY_PATH device --raw)
                PS1="(⚡$device) $__DEFAULT_PS1"
                export LD_PRELOAD=`readlink -f ~/.thunder/libthunder.so`
                __define_tnr_activated
            else 
                echo "Error activating tnr environment: $output"
            fi
        else
            # Forward the command to the actual tnr binary for all other cases
            "$__TNR_BINARY_PATH" "$@"
        fi
    }
}

__tnr_setup() {
    if [ -z "${__TNR_BINARY_PATH}" ]; then
        export __TNR_BINARY_PATH=$(__find_tnr)
    fi

    if [ -z "${__DEFAULT_PS1}" ]; then
        export __DEFAULT_PS1=$PS1
    fi

    if [[ ! "$LD_PRELOAD" =~ "libthunder.so" ]]; then
        # We aren't running in a thunder shell
        __define_tnr_deactivated
    else
        PS1="(⚡$($__TNR_BINARY_PATH device --raw)) $__DEFAULT_PS1"
        __define_tnr_activated
    fi
}

__tnr_setup