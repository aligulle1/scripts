#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Pisilinux system for creation, deletion and cleaning of volatile and temporary files.
"""

import os
import re
import sys
import shutil

from pwd import getpwnam
from grp import getgrnam

DEFAULT_CONFIG_DIRS = ["/etc/tmpfiles.d", "/run/tmpfiles.d", "/usr/lib/tmpfiles.d"]

def read_file(path):
    with open(path) as f:
        return f.read().strip()

def write_file(path, content, mode = "w"):
    open(path, mode).write(content)

def create(type, path, mode, uid, gid, age, arg):
    if type == "L":
        if not os.path.islink(path): os.symlink(arg, path)
        return
    elif type == "D":
        if os.path.isdir(path): shutil.rmtree(path)
        elif os.path.islink(path): os.remove(path)
    elif type == "c":
        arg = arg.split(":")
        os.mknod(path, mode, os.makedev(arg[0], arg[1]))
    if type.lower() == "d":
        if not os.path.isdir(path): os.makedirs(path, mode)
        os.chown(path, uid, gid)
    elif type in ["f", "F", "w"]:
        if not os.path.isfile(path) and type == "w": return
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
            os.chown(os.path.dirname(path), uid, gid)
        write_file(path, arg, mode = "a" if type == "f" else "w")
        os.chown(path, uid, gid)

USAGE = """\
%s PATH(S)  
\tparsing specified .conf files.
%s
\tparsing .conf files in:
\t%s
""" % (sys.argv[0], sys.argv[0], "; ".join(DEFAULT_CONFIG_DIRS))
    
def usage():
    print USAGE
    sys.exit(0)

if __name__ == "__main__":
    if ("-h" or "--help") in sys.argv: usage()

    config_files = {}
    errors = []

    def add_config_file(head, tail):
        try:
            config_files[head].append(tail)
        except KeyError:
            config_files[head] = [tail]

    if sys.argv[1:]:
        for arg in sys.argv[1:]:
            (head, tail) = os.path.split(arg)
            if not tail.endswith(".conf"): errors.append("%s is not .conf file" % tail)
            elif not head: errors.append("Full path is needed for %s args." % sys.argv[0])
            elif not os.path.isdir(head): errors.append("Path %s not exists." % head)
            elif not os.path.isfile(arg): errors.append("File %s not exists." % arg)
            add_config_file(head, tail)
    else:
        all_files_names = []
        for head in DEFAULT_CONFIG_DIRS:
            if not os.path.isdir(head): continue
            for tail in os.listdir(head):
                # only .conf files and don't override (previous paths have higer priority)
                if not tail.endswith(".conf") or tail in all_files_names: continue
                all_files_names.append(tail)
                add_config_file(head, tail)

    for d, fs in config_files.items():
        for f in fs:
            conf = read_file(os.path.join(d, f))
            # parse config file
            for line in [l for l in conf.split("\n") if l and not (l.startswith("#") or l.isspace())]:
                cerr = len(errors)
                fields = line.split()
                if len(fields) < 3: errors.append("%s is invalid .conf file. Not enough args in line: %s" % (os.path.join(d, f), line))
                else: 
                    if len(fields) < 4 or fields[3] == "-": fields[3] = "root"
                    if len(fields) < 5 or fields[4] == "-": fields[4] = "root"
                if len(fields) < 7: fields.extend(["",] * (7 - len(fields)))
                elif len(fields) > 7: fields = fields[0:6] + [re.sub(".*?(%s)\s*$" % "\s+".join(fields[6:]), "\\1", line)]
                if fields[0] == "c" and not re.search("\d+:\d+", fields[6]): errors.append("%s - wrong argument for type 'c' in file: %s" % (fields[6], os.path.join(d, f)))
                for n, i in enumerate(fields):
                    if i == "-": fields[n] = ""
                if not fields[0] in ["c", "d", "D", "f", "F", "L", "w"]: errors.append("%s - wrong type in file: %s" % (fields[0], os.path.join(d, f)))
                elif fields[0] == "L":
                    if not fields[6]: errors.append("Wrong specified in file: %s" % os.path.join(d, f))
                    elif not os.path.exists(fields[6]): errors.append("%s - wrong path in file: %s" % (fields[6], os.path.join(d, f)))
                elif fields[0] in ["f", "F", "w"] and os.path.isdir(fields[1]): errors.append("Cannot write to file. %s is directory." % fields[1]) 
                else:
                    if not fields[2]: errors.append("No mode specified in file: %s" % os.path.join(d, f))
                    elif not re.search("^\d{3,4}$", fields[2]): errors.append("%s - wrong mode in file: %s" % (fields[2], os.path.join(d, f)))
                    else: fields[2] = int(fields[2], 8)
                    try:
                        fields[3] = getpwnam(fields[3]).pw_uid
                    except KeyError:
                        errors.append("User %s not exists (%s)" % (fields[3], os.path.join(d, f)))
                    try:
                        fields[4] = getgrnam(fields[4]).gr_gid
                    except KeyError:
                        errors.append("Group %s not exists (%s)" % (fields[4], os.path.join(d, f)))
                # 
                if len(errors) == cerr: create(*fields)

    print "\n".join(errors)