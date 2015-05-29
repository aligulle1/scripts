# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 marcin.bojara@gmail.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# ActionsAPI Modules
from pisi.actionsapi import get
from pisi.actionsapi import cmaketools
from pisi.actionsapi import shelltools

def configure(parameters = "", installPrefix = "/%s" % get.defaultprefixDIR(), sourceDir = ".."):
    ''' parameters -DLIB_INSTALL_DIR="target_dir" -DSOMETHING_USEFUL=1'''

    config_params = {
                     "-DCMAKE_BUILD_TYPE": "Release",
                     "-DLIB_INSTALL_DIR": "lib",
                     "-DLIBEXEC_INSTALL_DIR": "libexec",
                     "-DSYSCONF_INSTALL_DIR": "/etc",
                     "-DPYTHON_EXECUTABLE": "/usr/bin/python3",
                     "-DPLUGIN_INSTALL_DIR": "/usr/lib/qt5/plugins",
                     "-DECM_MKSPECS_INSTALL_DIR": "/usr/lib/qt5/mkspecs/modules",
                     "-DKDE_INSTALL_USE_QT_SYS_PATHS": "ON",
                     "-DBUILD_TESTING": "OFF"
                     }

    shelltools.makedirs("build")
    shelltools.cd("build")

    cmaketools.configure("%s %s" % ("".join(['%s="%s"' % (k, v) for k, v in config_params.items() if not "%s=" % k in parameters]), parameters),
                         installPrefix,
                         sourceDir)

    shelltools.cd("..")

def make(parameters = ""):
    cmaketools.make("-C build %s" % parameters)

def install(parameters = "", argument = "install"):
    cmaketools.install("-C build %s" % parameters, argument)
