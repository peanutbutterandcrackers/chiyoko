#!/bin/bash

usage () {
	cat <<- _EOF_
		chiyoko installation script: usage: INSTALL.sh [-h|-g|-l]
		-h, --help   -> Display this help and exit
		-g, --global -> Install globally, requires super-user privileges
		-l, --local  -> Install locally, doesn't require elevated privileges
	_EOF_
}

check_PATH () {
	# checks whether or not ~/.local/bin
	# is in the PATH variable or not
	echo $PATH | grep --silent $HOME/\.local/bin 
	if [ $? -ne 0 ]; then
		{ echo -n "export PATH='"
		  echo -n $HOME/.local/bin: ;
		  echo $PATH\' ;
		} >> ~/.profile 
		source ~/.profile
	fi
}

local_install () {
	# will reside in ~/.local/bin
	check_PATH
	mkdir -p ~/.local/bin
	cp -a $(dirname $0)/chiyoko.py ~/.local/bin/chiyoko
	echo "Completed local installation successfully."
}

global_install () {
	# will reside in /usr/local/bin
	# requires superuser privileges
	if [ $(id -u) -eq 0 ]; then
		cp $(dirname $0)/chiyoko.py /usr/local/bin/chiyoko
		chmod 755 /usr/local/bin/chiyoko
		chown root: /usr/local/bin/chiyoko
		[[ $? -eq 0 ]] && echo "Global Installation successful."
	else
		echo "Error: Requires Super User Privileges for global installation."
		echo "Try local installation instead, or use sudo, or ask your sysadmin."
		echo "Exiting."
		exit 1
	fi
}

if [[ -z "$1" ]]; then
	usage
	exit
fi

while [[ -n "$1" ]]; do
	case $1 in 
		-h | --help )	usage
		            	exit
						;;
		-g | --global )	global_install
		              	exit
						;;
		-l | --local )	local_install
		                exit
						;;
		* )            	usage
		                exit 1
	esac			
	shift
done
