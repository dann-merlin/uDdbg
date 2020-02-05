#############################################################################
#
#    Copyright (C) 2019
#    Giovanni -iGio90- Rocca, Vincenzo -rEDSAMK- Greco
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>
#
#############################################################################
#
# Unicorn DOPE Debugger
#
# Runtime bridge for unicorn emulator providing additional api to play with
# Enjoy, have fun and contribute
#
# Github: https://github.com/iGio90/uDdbg
# Twitter: https://twitter.com/iGio90
#
#############################################################################

import random
import struct

import fcntl
import inquirer

import os

import termios
from termcolor import colored
from unicorn import *
import capstone
from unicorn import unicorn_const
import re


def titlify(text):
    """
    Print a title.
    Thanks -> https://github.com/hugsy/gef/blob/master/gef.py#L815
    """
    cols = get_terminal_size()[1]
    nb = (cols - len(text) - 4) // 2
    msg = [white_bold("-" * nb + '[ '),
           green_bold(text),
           white_bold(' ]' + "-" * nb)]
    return "".join(msg)


def get_terminal_size():
    """Return the current terminal size."""
    try:
        cmd = struct.unpack("hh", fcntl.ioctl(1, termios.TIOCGWINSZ, "1234"))
        tty_rows, tty_columns = int(cmd[0]), int(cmd[1])
        return tty_rows, tty_columns
    except Exception as ex:
        return 80, 120

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear' if 'unix' else "clear && printf '\e[3J'")


def get_banner():
    # Feel free to add yours ^^
    b_arr = [
        '202f4040252e202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a202020202f40402a20202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a202020202020254020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a262e2020202020252c2020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202e2a2f2c2020200d0a402c2020202020202e202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202a2f2825404040402e0d0a402820202020202020202a2e202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202a232e202020202020202e2a2a2c2e2c40400d0a404020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202840402a202020202020202c404040404026404040400d0a2f402620202020202020202040402e2020202020202020202020202020202020202020202020202020202020202020202020202020202e4040402e20202020202020204040402c20202020202023400d0a202840402e2020202020202020404028202020202020202020202020202020202020202020202020202020202020202020202020202340402320202020202020202e402520202020202020202020200d0a20202e404025202020202020202028404020202020202020202020202020202020202020202020202020202020202020202020202c40404020202020202020202e26202020202020202020202020200d0a2020202023402320202020202020202e40402c2020202020202020202020202020202020202020202020202020202020202020202a40402620202020202020202c20202020202020202020202020200d0a20202020202e402e20202020202020202026402520202020202020202020202020202020202020202020202020202020202020202e40402620202020202020202020202020202020202020202020200d0a2020202020202c2e20202020202020202020404040202020202020202020202020202020202020202020202020202020202020202e40402620202020202020202020202020202020202020202020200d0a2020202020202020202020202020202020202540402a20202020202020202020202020202020202020202020202020202020202e4040402020202020202020202020202020202020202020202020200d0a2020202020202020202020202020202020204040402c2020202020202020202020202020202020202020202020202020202f4040402c202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202c40402620202020202020202020202020202020202020202020202020202040402f20202020202a402020202020202020202020202020202020202020200d0a20202020202020202c2c202020202020202340402c2020202020202020202020202020202020202020202020202020264020202020202040402c2020202020202020202020202020202020202020200d0a20202020202020202c28202020202020202640262e2020202020202020202020202020202020202020202020202020402a2020202020404040202020202020202020202020202020202020202020200d0a202020202020202020402a2020202020202640402e20202020202020202020202020202020202020202020202020202f20202020202e404040202020202020202020202020202020202020202020200d0a2020202020202020202e402620202020202c40402320202020202020202020202020202020202020202020202020202020202020202e4040402e2020202020202020202020202020202020202020200d0a202020202020202020202c4040402c2020202840402e202020202020202020202020202020202020202020202020202020202020202c404040282020202020202020202020202020202020202020200d0a202020202020202020202020234040402520202640402020202020202020202020202020202020202020202020202020202020202025404040282020202020202020202020202020202020202020200d0a202020202020202020202020202025404040282f4040402f202020202020202020202020202020202020202020202020202020202840404026202020202020202020202020202020202020202020200d0a202020202020202020202020202020202640404040404040262020202e2a282526404040262a2c202020202640252f2c23404040402c20202020202020202020202020202020202020202020200d0a202020202020202020202020202020202040404040404040402a2028404040404040404040404040404026202e40404040404040402f202020202020202020202020202020202020202020202020200d0a202020202020202020202020202020204040404040404040402c20284040404040404040404040404040262020264040404040404025202020202020202020202020202020202020202020202020200d0a202020202020202020202020202020202026404040404040402c20202f40404040404040404040404025202020404040404040402320202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020254040404040402a2020202f40404040404040402a2020202e40404040404028202020202020202020202020202020202020202020202020202020200d0a202020202020202020202020202c4040282020202f40404040404040262c2020202a26262c2020202a2640404040404040282020202540402e202020202020202020202020202020202020202020200d0a2020202020202020202020202540402620202026404040404040404040404040402e20202c4040404040404040404040404025202020404040232020202020202020202020202020202020202020200d0a2020202020202020202020264040402e2020254040404040404040404040404040402a2a4040404040404040404040404040402320202c4040402320202020202020202020202020202020202020200d0a20202020202020202020264040402c202026404040404040404040404040404040404040404040404040404040404040404040402320202a40404040202020202020202020202020202020202020200d0a2020202020202020202840404040262020202c4040404040404040404040404040404040404040404040404040404040404026202020204040404040252020202020202020202020202020202020200d0a2020202020202020204040404040404020202c40404040404040404040404040404040404040404040404040404040404040402e202e404040404040402c20202020202020202020202020202020200d0a20202020202020202a40404040404020202c4040404040404040404040404040404040404040404040404040404040404040404020202e4040404040402820202020202020202020202020202020200d0a20202020202020202a40404040402c202026404040404040404040404040404040404040404040404040404040404040404040402f20202f40404040402320202020202020202020202020202020200d0a20202020202020202e404040404020202026404040404040404040404040404040404040404040404040404040404040404040402f20202e40404040402a20202020202020202020202020202020200d0a20202020202020202025404040402c20202c404040404040404040264040404040404040404040404040254040404040404040402020202f40404040402020202020202020202020202020202020200d0a2020202020202020202040404040402020202020202020202e2c202020202c40404040404040252e202020202e2020202020202020202e40404040402e2020202020202020202020202020202020200d0a202020202020202020202026404020202e40404040404040262a2640402a202e40404040402520202a4040252f264040404040402320202e40402520202020202020202020202020202020202020200d0a20202020202020202020202023282020252f2c2e2e2e2a234040404040402020404040404025202a404040404040232a2e2e2e2a232f202025282020202020202020202020202020202020202020200d0a2020202020202020202020202020202020202a2a2a2e202020202e2640402020404040404023202a40402620202020202e2a2a2c2020202020202020202020202020202020202020202020202020200d0a202020202020202020202020202020202640404040404040402f202020262020264040404028202a262020202f404040404040404028202020202020202020202020202020202020202020202020200d0a2020202020202020202020282620202c4040404040404040404040252020202020202020202020202020254040404040404040404040202020402a20202020202020202020202020202020202020200d0a202020202020202020202640402e2020404040404040404040404040402e202026404040402320202e4040404040404040404040402320202f404026202020202020202020202020202020202020200d0a2020202020202020202a404040402e202028404040404040404040404026202023404040402f202e2640404040404040404040402c202028404040402f2020202020202020202020202020202020200d0a2020202020202020202e4040404040402a202020202e2a282325262640402020234040404028202c404026262523282a2e2020202e234040404040402e2020202020202020202020202020202020200d0a20202020202020202020202340404040404040404025232f2f2a2a202020202040404040402520202020202f28282325264040404040404040402c20202020202020202020202020202020202020200d0a202020202020202020202020202020202c2f2326404040404040252a2c2020202020202020202020202e2c2840404040402f2c20202020202020202020202020202020202020202020202020200d0a202020202020202020202020202020202020202020202020202020282640402e2a2f2020252e2c4040262f2020202020202020202020202020202020202020202020202020202020202020202020200d0a2020202020202020202020202020202020202020202020202e4040404040402c4040202040262f4040404040262e2020202020202020202020202020202020202020202020202020202020202020200d0a202020202020202020202020202020202020202020232e202a404040404040404040404040404040404040404025202e232020202020202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202a402e20202f4040404040404040404040404040404040402620202e262a20202020202020202020202020202020202020202020202020202020200d0a2020202020202020202020202020202020202020202026402c202e4040404040404040404040404040404028202e4040202020202020202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202023402f202e26404040404040404040404028202a40232020202020202020202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202e40402f2a282020202e2c2a2a2c2e202020282a2a40402e20202020202020202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202020202a4040402e404025202e4040262e4040402a20202020202020202020202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202020202028252e254040402f264040402a2e25232020202020202020202020202020202020202020202020202020202020202020202020200d0a',
        '0d0a0d0a202f24242020202f242420202020202020202020202f242420202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c20242420207c202424202020202020202020207c5f5f2f20202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c20242420207c202424202f2424242424242420202f242420202f2424242424242420202f2424242424242020202f24242424242420202f2424242424242420202020202020202020202020202020200d0a7c20242420207c2024247c2024245f5f202024247c202424202f24245f5f5f5f5f2f202f24245f5f20202424202f24245f5f202024247c2024245f5f20202424202020202020202020202020202020200d0a7c20242420207c2024247c20242420205c2024247c2024247c2024242020202020207c20242420205c2024247c20242420205c5f5f2f7c20242420205c202424202020202020202020202020202020200d0a7c20242420207c2024247c20242420207c2024247c2024247c2024242020202020207c20242420207c2024247c2024242020202020207c20242420207c202424202020202020202020202020202020200d0a7c20202424242424242f7c20242420207c2024247c2024247c2020242424242424247c20202424242424242f7c2024242020202020207c20242420207c202424202020202020202020202020202020200d0a205c5f5f5f5f5f5f2f207c5f5f2f20207c5f5f2f7c5f5f2f205c5f5f5f5f5f5f5f2f205c5f5f5f5f5f5f2f207c5f5f2f2020202020207c5f5f2f20207c5f5f2f202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a202f242424242424242020202f24242424242420202f2424242424242420202f2424242424242424202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c2024245f5f20202424202f24245f5f202024247c2024245f5f202024247c2024245f5f5f5f5f2f202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c20242420205c2024247c20242420205c2024247c20242420205c2024247c202424202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c20242420207c2024247c20242420207c2024247c20242424242424242f7c202424242424202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c20242420207c2024247c20242420207c2024247c2024245f5f5f5f2f207c2024245f5f2f202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c20242420207c2024247c20242420207c2024247c2024242020202020207c202424202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c20242424242424242f7c20202424242424242f7c2024242020202020207c202424242424242424202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c5f5f5f5f5f5f5f2f20205c5f5f5f5f5f5f2f207c5f5f2f2020202020207c5f5f5f5f5f5f5f5f2f202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a202f242424242424242020202020202020202020202f242420202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c2024245f5f20202424202020202020202020207c20242420202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020202020200d0a7c20242420205c20242420202f242424242424207c202424242424242420202f24242020202f242420202f2424242424242020202f2424242424242020202f2424242424242020202f242424242424200d0a7c20242420207c202424202f24245f5f202024247c2024245f5f202024247c20242420207c202424202f24245f5f20202424202f24245f5f20202424202f24245f5f20202424202f24245f5f202024240d0a7c20242420207c2024247c2024242424242424247c20242420205c2024247c20242420207c2024247c20242420205c2024247c20242420205c2024247c2024242424242424247c20242420205c5f5f2f0d0a7c20242420207c2024247c2024245f5f5f5f5f2f7c20242420207c2024247c20242420207c2024247c20242420207c2024247c20242420207c2024247c2024245f5f5f5f5f2f7c2024242020202020200d0a7c20242424242424242f7c2020242424242424247c20242424242424242f7c20202424242424242f7c2020242424242424247c2020242424242424247c2020242424242424247c2024242020202020200d0a7c5f5f5f5f5f5f5f2f20205c5f5f5f5f5f5f5f2f7c5f5f5f5f5f5f5f2f20205c5f5f5f5f5f5f2f20205c5f5f5f5f20202424205c5f5f5f5f20202424205c5f5f5f5f5f5f5f2f7c5f5f2f2020202020200d0a20202020202020202020202020202020202020202020202020202020202020202020202020202020202f242420205c202424202f242420205c20242420202020202020202020202020202020202020200d0a202020202020202020202020202020202020202020202020202020202020202020202020202020207c20202424242424242f7c20202424242424242f20202020202020202020202020202020202020200d0a20202020202020202020202020202020202020202020202020202020202020202020202020202020205c5f5f5f5f5f5f2f20205c5f5f5f5f5f5f2f202020202020202020202020202020202020202020'
    ]
    return bytearray.fromhex(random.choice(b_arr)).decode('iso-8859-1')


def error_format(command, text):
    return colored("ERR", 'red', attrs=['bold', 'underline']) + "(" + \
           colored(command, 'white', attrs=['bold', 'underline']) + "): " + text


def white_bold(text):
    return colored(text, attrs=['bold', 'dark'])


def white_bold_underline(text):
    return colored(text, attrs=['dark', 'bold', 'underline'])


def green_bold(text):
    return colored(text, 'green', attrs=['bold', 'dark'])


def red_bold(text):
    return colored(text, 'red', attrs=['bold', 'dark'])


def get_arch_consts(arch):
    if arch == UC_ARCH_ARM:
        return arm_const
    elif arch == UC_ARCH_ARM64:
        return arm64_const
    elif arch == UC_ARCH_M68K:
        return m68k_const
    elif arch == UC_ARCH_MIPS:
        return mips_const
    elif arch == UC_ARCH_SPARC:
        return sparc_const
    elif arch == UC_ARCH_X86:
        return x86_const


def get_reg_tag(arch):
    if arch == UC_ARCH_ARM:
        return "UC_ARM_REG_"
    elif arch == UC_ARCH_ARM64:
        return "UC_ARM64_REG_"
    elif arch == UC_ARCH_M68K:
        return "UC_M68K_REG_"
    elif arch == UC_ARCH_MIPS:
        return "UC_MIPS_REG_"
    elif arch == UC_ARCH_SPARC:
        return "UC_SPARC_REG_"
    elif arch == UC_ARCH_X86:
        return "UC_X86_REG_"


def prompt_list(items, key, hint):
    base_path = [
        inquirer.List(key,
                      message=hint,
                      choices=items)]
    r = inquirer.prompt(base_path)
    return r[key]


def prompt_arch():
    items = [k for k, v in unicorn_const.__dict__.items() if not k.startswith("__") and k.startswith("UC_ARCH")]
    return prompt_list(items, 'arch', 'Select arch')


def prompt_mode():
    items = [k for k, v in unicorn_const.__dict__.items() if not k.startswith("__") and k.startswith("UC_MODE")]
    return prompt_list(items, 'mode', 'Select mode')


def prompt_cs_arch():
    items = [k for k, v in capstone.__dict__.items() if not k.startswith("__") and k.startswith("CS_ARCH")]
    return prompt_list(items, 'arch', 'Select arch')


def prompt_cs_mode():
    items = [k for k, v in capstone.__dict__.items() if not k.startswith("__") and k.startswith("CS_MODE")]
    return prompt_list(items, 'mode', 'Select mode')


def check_args(pattern, args):
    """
    check that args array matches the pattern type and args len
    :param pattern: string with args type pattern. [int|str|hex], Ex. int int hex.
    :param args: args array to check
    :return:
    """
    # get the pattern array
    p_arr = pattern.split(' ')
    args_effective_len = 0

    for i, p in enumerate(p_arr):
        if indexof(p, '@') == -1:
            args_effective_len += 1

    # if args len doesn't match with the pattern
    if len(args) < args_effective_len or len(args) > len(p_arr):
        return False, "args len doesn't match"

    # int str hex
    for i, arg in enumerate(args):
        if arg == '':
            return False, "arg " + str(i) + " is empty"

        # if we have optional args
        if indexof(p_arr[i], '@') != -1:
            p_arr[i] = p_arr[i][1:]

        # select the right regex for the pattern
        if p_arr[i] == "int":
            reg = r"\d+"
        elif p_arr[i] == "str":
            reg = r".+"
        elif p_arr[i] == "hex":
            reg = r"0x\d+"
        elif p_arr[i] == "hexsum":
            reg = r"0x\d+\+0x\d+"
        elif p_arr[i] == "intsum":
            reg = r"\d+\+\d+"
        else:
            return False, "pattern " + str(i) + " wrong type"

        if re.match(reg, arg) is None:
            return False, "arg " + str(i) + " should be " + p_arr[i] + " type"

    return True, None


def indexof(str, str_search):
    try:
        if str.index(str_search):
            return str.index(str_search)
    except Exception:
        return -1


def u_eval(core_instance, val):
    val = str(val)
    r = r"([$@][a-z0-9]+)(\W|$)"
    m = re.finditer(r, val)
    for n, match in enumerate(m):
        if len(match.groups()) > 0:
            v = match.group(1)
            if v.startswith("$"):
                rv = core_instance.get_module('registers_module').read_register(v[1:].upper())
                if rv:
                    val = val.replace(v, str(rv))
    return int(eval(val))
