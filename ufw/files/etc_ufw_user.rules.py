#!/usr/bin/env python3

import ufw
from ufw.backend_iptables import UFWBackendIptables
from ufw.frontend import parse_command
import gettext
import shlex
import sys

# Install gettext as _() used in objects
gettext.install(ufw.common.programName, **{})

# Init backend object with dryrun flag - output will be redirected to stdout
backend = UFWBackendIptables(dryrun=True, rootdir=None, datadir=None)

# Clear rules read on object init
backend.rules = []
backend.rules6 = []

# Remember errors in loop
errors = False

# Read rules src file and append rules in backend object
with open("/etc/ufw/user.rules.src") as rules_file:
    for rule in rules_file:
        # Bad src rules shouldn't break whole firewall
        try:
            parser = parse_command(shlex.split(rule.strip()))
            if parser.data["iptype"] == "v4":
                backend.rules.append(parser.data["rule"])
            if parser.data["iptype"] == "v6":
                backend.rules6.append(parser.data["rule"])
            if parser.data["iptype"] == "both":
                backend.rules.append(parser.data["rule"])
                backend.rules6.append(parser.data["rule"])
        # Print to stderr bad rules
        except:
            errors = True
            print(rule.strip(), file=sys.stderr)

# Print one of needed files to stdout depending on argv[1]
if sys.argv[1] == "v4":
    backend._write_rules(v6=False)
if sys.argv[1] == "v6":
    backend._write_rules(v6=True)

# Exit 1 on bad rules
if errors:
    sys.exit(1)
