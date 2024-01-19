#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   SPDX-FileCopyrightText: 2022 Victor Fuentes <vmfuentes64@gmail.com>
#   SPDX-FileCopyrightText: 2019 Adriaan de Groot <groot@kde.org>
#   SPDX-License-Identifier: GPL-3.0-or-later
#
#   Calamares is Free Software: see the License-Identifier above.
#

import libcalamares
import os
import subprocess
import re
import shutil

import gettext
_ = gettext.translation("calamares-python",
                        localedir=libcalamares.utils.gettext_path(),
                        languages=libcalamares.utils.gettext_languages(),
                        fallback=True).gettext

def pretty_name():
    return _("Installing NixOS.")

status = pretty_name()

def pretty_status_message():
    return status

def catenate(d, key, *values):
    """
    Sets @p d[key] to the string-concatenation of @p values
    if none of the values are None.
    This can be used to set keys conditionally based on
    the values being found.
    """
    if [v for v in values if v is None]:
        return

    d[key] = "".join(values)

def run():
    """NixOS Configuration."""

    global status
    status = _("Installing NixOS")
    libcalamares.job.setprogress(0.1)

    gs = libcalamares.globalstorage
    root_mount_point = gs.value("rootMountPoint")

    # Mount swap partition
    for part in gs.value("partitions"):
        if part["claimed"] == True and part["fs"] == "linuxswap":
            status = _("Mounting swap")
            libcalamares.job.setprogress(0.2)
            if part["fsName"] == "luks":
                try:
                    libcalamares.utils.host_env_process_output(
                        ["swapon", "/dev/mapper/" + part["luksMapperName"]], None)
                except subprocess.CalledProcessError:
                    libcalamares.utils.error(
                        "Failed to activate swap: " + "/dev/mapper/" + part["luksMapperName"])
                    return (_("swapon failed to activate swap"), _("failed while activating:" + "/dev/mapper/" + part["luksMapperName"]))
            else:
                try:
                    libcalamares.utils.host_env_process_output(
                        ["swapon", part["device"]], None)
                except subprocess.CalledProcessError:
                    libcalamares.utils.error(
                        "Failed to activate swap: " + "/dev/mapper/" + part["device"])
                    return (_("swapon failed to activate swap " + part["device"]), _("failed while activating:" + "/dev/mapper/" + part["device"]))
            break


    status = _("Copying NixOS configuration")
    libcalamares.job.setprogress(0.3)
    nix_cfg_src = "/iso/nix-cfg"

    try:
        for root, dirs, files in os.walk(nix_cfg_src):
            dest = os.path.join(root_mount_point, os.path.relpath(root, nix_cfg_src))

            if not os.path.exists(dest):
                os.makedirs(est)

            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest, file)
                shutil.copy2(src_file, dest_file)

    except Exception as e:
        return (_("nixos-install failed"), _(f"Installation failed to complete, with error: {e}"))

    status = _("Installing NixOS")
    libcalamares.job.setprogress(0.4)

    try:
        output = ""
        proc = subprocess.Popen(["pkexec", "nixos-install", "--no-root-passwd", "--root", root_mount_point], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = proc.stdout.readline().decode("utf-8")
            output += line
            libcalamares.utils.debug("nixos-install: {}".format(line.strip()))
            if not line:
                break
        exit = proc.wait()
        if exit != 0:
            return (_("nixos-install failed"), _(output))
    except:
        return (_("nixos-install failed"), _("Installation failed to complete"))

    return None
