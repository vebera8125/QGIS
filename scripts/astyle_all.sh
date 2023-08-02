#!/usr/bin/env bash
###########################################################################
#    astyle-all.sh
#    ---------------------
#    Date                 : August 2008
#    Copyright            : (C) 2008 by Juergen E. Fischer
#    Email                : jef at norbit dot de
###########################################################################
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 2 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
###########################################################################


PATH=$PATH:$(dirname "$0")

set -e

elcr="$(tput el)$(tput cr)"
export elcr

find python src tests -type f -print | while read -r f; do
        if [ -f "$f.astyle" ]; then
		# reformat backup
                cp "$f.astyle" "$f"
                touch -r "$f.astyle" "$f"
        else
		# make backup
                cp "$f" "$f.astyle"
                touch -r "$f" "$f.astyle"
        fi

	echo -ne "Reformatting $f $elcr"
	astyle.sh "$f" || true
done

remove_temporary_files.sh

echo
