#!/bin/sh

PATH=/home/deltawoot/.local/bin:/usr/bin:/usr/sbin:/bin:/sbin:${PATH}
chown -R deltawoot: /home/deltawoot/files
exec runuser -u deltawoot "$@"
