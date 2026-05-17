#!/bin/sh
set -eu
service nginx start
exec su -s /bin/sh appuser -c "cd /backend && exec ./run.sh"
