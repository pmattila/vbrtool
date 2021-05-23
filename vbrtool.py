#!/usr/bin/python
#
# vbrtool.py	A tool for viewing and manipulation Mikaro Vbar VBR files.
#
# 		Copyright (C) 2017  Petri Mattila aka. Dr.Rudder
#
#		This program is free software; you can redistribute it and/or
#		modify it under the terms of the GNU General Public License
#		as published by the Free Software Foundation; either version 2
#		of the License, or (at your option) any later version.
#
#		This program is distributed in the hope that it will be useful,
#		but WITHOUT ANY WARRANTY; without even the implied warranty of
#		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#		GNU General Public License for more details.
#
#		You should have received a copy of the GNU General Public License
#		along with this program; if not, write to the Free Software
#		Foundation, Inc., 51 Franklin Street, Fifth Floor, 
#		Boston, MA  02110-1301, USA.
#

import sys
import re
import argparse


## Definitions

Version = '1.0.0'

Usage = '''

VBRTool v%s - A tool for viewing and manipulating Mikado Vbar .vbr files

        Vbrtool is a simple tool written in Python, for working with Mikado .vbr 
        files from VBar v5.3.x, either Mini or full size.

        The tool has three main modes of operation.

	    1. Print parameters
            2. Compare parameters
            3. Copy parameters

        The set of registers operated on is further selected by command line flags.

Print Parameters

        The command line option -P or --print selects print mode. The values of the
	selected registers are printed, for each input file.

Compare parameters

        The command line option -D or --diff compares the register values in the 
        input files, considering only the selected registers. The registers that have
        the same value in _all_ input files are not printed.

Copy parameters

        The command line option -C <vbr-file> or --copy <vbr-file> copies the selected
        registers from <vbr-file> to the other input files. Only the selected registers
        are copied, all other registers stay unchanged.

Selecting Registers

        The tool operates on a (sub)set of Vbar registers, which is selected by one of
        the following options:

           (none)               The default is basic parameters on the settings page

           -a, --all            All known parameters
           -r, --raw            All registers from the input files

           -m, --main           Main rotor expert parameters on the settings page
           -t, --tail           Tail rotor expert parameters on the settings page
           -g, --gov            Governor expoert parameters on the settings page
           -x, --exp            All expert parameters on the settings page

           -ms, --main-setup    Main/swash setup parameters
           -ts, --tail-seutp    Tail setup parameters
           -gs, --gov-setup     Governor setup parameters
           -rs, --rx-setup      Receiver setup parameters
           -s, --setup          All setup parameters

        Only one of these parameters can be used at a time.

Examples

        Print basic settings from all input files:

               > vbrtool.py --print bank0.vbr bank1.vbr

        Print expert settings from all input files:

               > vbrtool.py --print --exp bank0.vbr bank1.vbr

        Print all parameters from all input files:

               > vbrtool.py --print --all bank0.vbr bank1.vbr
 
 
        Compare receiver setup between the input files:

               > vbrtool.py --diff --rx-setup bank0.vbr bank1.vbr
 
        Compare swash setup between the input files:

               > vbrtool.py --diff --main-setup bank0.vbr bank1.vbr

        Compare all registers between the input files:

               > vbrtool.py --diff --raw bank0.vbr bank1.vbr
 
 
        Copy governor settings from bank1 to bank2:

               > vbrtool.py --copy bank1.vbr --gov bank2.vbr

        Copy tail setup from bank0 to bank1 and bank2:

               > vbrtool.py --copy bank0.vbr --tail-setup bank1.vbr bank2.vbr
 
 
Warning

        Not all registers in the vbr file format are fully understood. 
        Although unlikely, it is possible that the tool may misinterpret
	some relevant registers.
 
 
License

        Copyright (C) 2017  Petri Mattila aka. Dr.Rudder

        This program is free software; you can redistribute it and/or
        modify it under the terms of the GNU General Public License
        as published by the Free Software Foundation; either version 2
        of the License, or (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program; if not, write to the Free Software
        Foundation, Inc., 51 Franklin Street, Fifth Floor, 
        Boston, MA  02110-1301, USA.
 
 
Usage:  vbrtool.py [-h|--help] [-V|--version]
                   [-P|--print] [-D|--diff] [-C <file>|--copy <file>] 
                   [-a|--all] [-r|--raw] [-m|--main] [-t|--tail] [-g|--gov] [-x|--exp]
                   [-ms|--main-setup] [-ts|--tail-setup] [-gs|--gov-setup]
                   [-rs|--rx-setup] [-s|--setup]
                   <file> [<file>...]

''' % (Version)


## Register groups

basic_regs  = [ 1091, 72, 41, 33, 30, 40, 35, 79, 50, 80, 71, ]
main_regs   = [ 72, 41, 33, 30, 40, 35, 53, 68, 77, 46, 228 ]
tail_regs   = [ 50, 79, 28, 75, 59, 51, 82, 10, 11, 54, 56, 55, 58, 6, 229, ]
gov_regs    = [ 80, 70, 71, 93, 91, 92, 94, ]
exp_regs    = [ 1091, 72, 41, 33, 30, 40, 35, 53, 68, 77, 46, 228,
		50, 79, 28, 75, 59, 51, 82, 10, 11, 54, 56, 55, 58, 6, 229,
		80, 70, 71, 93, 91, 92, 94, ]

main_setup_regs  = [
    204, 205, 207,
    52, 48,
    221,
    200, 20, 21, 16,
    201, 22, 23, 17,
    202, 24, 25, 18,
    203, 26, 27, 19,
    0, 1, 2, 3,
    36, 37, 38, 39,
]

tail_setup_regs  = [
    223, 222, 206, 5, 7, 8,
]

gov_setup_regs = [ 
    80, 70, 71, 45, 90, 88, 89, 91, 92, 94, 93,
    231, 232,
    83, 84, 85, 86, 87, 2331, 240,
    236, 239, 234, 2341, 2342, 2343,
]

rx_setup_regs = [
    219, 210, 211, 212,
    213, 214, 215, 216,
    236, 239,
]

setup_regs  = [
    219, 210, 211, 212,
    213, 214, 215, 216,
    236, 239,
    204, 205, 207,
    52, 48,
    221,
    200, 20, 21, 16,
    201, 22, 23, 17,
    202, 24, 25, 18,
    203, 26, 27, 19,
    0, 1, 2, 3,
    36, 37, 38, 39,
    223, 222, 206, 5, 7, 8,
    80, 70, 71, 45, 90, 88, 89, 91, 92, 94, 93,
    231, 232,
    83, 84, 85, 86, 87, 2331, 240,
    236, 239, 234, 2341, 2342, 2343,
]

all_regs = [
    1091,
    72, 41, 33, 30, 40, 35, 53, 68, 77, 46, 228,
    50, 79, 28, 75, 59, 51, 82, 10, 11, 54, 56, 55, 58, 6, 229,
    80, 70, 71, 93, 91, 92, 94, 45, 90, 88, 89,
    234, 2341, 2342, 2343,
    231, 232, 2331, 240, 241,
    83, 84, 85, 86, 87,
    219, 210, 211, 212, 213, 214, 215, 216, 236, 239,
    204, 205, 207, 52, 48, 221,
    200, 20, 21, 16,
    201, 22, 23, 17,
    202, 24, 25, 18,
    203, 26, 27, 19,
    0, 1, 2, 3,
    36, 37, 38, 39,
    223, 222, 206, 5, 7, 8,
]


## Known registers

regdes = { 
     0:  'Servo #1 subtrim',
     1:  'Servo #2 subtrim',
     2:  'Servo #3 subtrim',
     3:  'Servo #4 subtrim',
     5:  'Tail servo subtrim',
     6:  'Tail Optimization #2',
     7:  'Tail servo limit #1',
     8:  'Tail servo limit #2',
    10:  'Tail Rotor Stop Gain A',
    11:  'Tail Rotor Stop Gain B',
    16:  'Servo #1 collective mix',
    17:  'Servo #2 collective mix',
    18:  'Servo #3 collective mix',
    19:  'Servo #4 collective mix',
    20:  'Servo #1 coord X',
    21:  'Servo #1 coord Y',
    22:  'Servo #2 coord X',
    23:  'Servo #2 coord Y',
    24:  'Servo #3 coord X',
    25:  'Servo #3 coord Y',
    26:  'Servo #4 coord X',
    27:  'Servo #4 coord Y',
    28:  'Tail Rotor acceleration',
    30:  'Elevator agility',
    33:  'Main Roto Gyro Gain',
    35:  'Collective agility (?)',
    36:  'Elevator subtrim @max',
    37:  'Aileron subtrim @max',
    38:  'Elevator subtrim @min',
    39:  'Aileron subtrim @min',
    40:  'Aileron agility',
    41:  'Main Rotor Style Adjust',
    45:  'Governor I-gain',
    46:  'Main Rotor expo',
    47:  'Tail Rotor expo',
    48:  'Cyclic ring',
    50:  'Tail Rotor Master Gain',
    51:  'Tail Rotor I-gain',
    52:  'Cyclic throw',
    53:  'Elevator precomp',
    54:  'Tail Collective precomp',
    55:  'Tail Collective zeroing',
    56:  'Tail Cyclic precomp',
    57:  'Microheli (?)',
    58:  'Tail Optimisation #1',
    59:  'Tail Rotor P-gain',
    68:  'Paddle simulator',
    69:  'Pitch pump gain (D)',
    70:  'Governor speed',
    71:  'Governor gain',
    72:  'Main Rotor Style',
    75:  'Tail Rotor deadband',
    77:  'Main Rotor deadband',
    79:  'Tail Rotor yaw rate',
    80:  'Governor type',
    82:  'Tail Rotor I-decay',
    83:  'Throttle curve @ -100%',
    84:  'Throttle curve @ -50%',
    85:  'Throttle curve @ 0%',
    86:  'Throttle curve @ 50%',
    87:  'Throttle curve @ 100%',
    88:  'Governor P-limit',
    89:  'Governor %-limit',
    90:  'Governor D-gain',
    91:  'Governor collective reduce',
    92:  'Governor cyclic add',
    93:  'Governor runup speed limit',
    94:  'Governor collective dynamic',
    
    109: 'Firmware version',

    141: 'Bank',
    
    200: 'Servo #1 flags',
    201: 'Servo #2 flags',
    202: 'Servo #3 flags',
    203: 'Servo #4 flags',
    204: 'Pitch sensor flags',
    205: 'Roll sensor flags',
    206: 'Tail servo flags',
    207: 'Tail sensor flags',
    
    210: 'Collective Input Ch',
    211: 'Aileron Input Ch',
    212: 'Elevator Input Ch',
    213: 'Rudder Input Ch',
    214: 'Throttle Input Ch',
    215: 'AUX/Gyro Input Ch',
    216: 'AUX2 Input Ch',

    219: 'Receiver type',
    221: 'Main servo rate',
    222: 'Tail servo rate',
    223: 'Tail servo type',
    224: 'Tail ???',
    
    228: 'Main Rotor Optimization',
    229: 'Tail Rotor Optimization',
    
    231: 'Governor off limit',
    232: 'Governor max limit',
    233: 'Governor Gearing ratio xx.x00',
    234: 'Governor flags',
    235: 'Governor Gearing ratio 00.0xx',
    236: 'Governor Input Ch',
    239: 'Governor Preset Ch',
    240: 'Governor RPM Sensor mult',
    241: 'Governor ESC test mode',

    499: 'Firmware patch level',

    1091: 'Firmware full version',

    2331: 'Governor Gearing ratio',
    2341: 'Governor Autorot Bailout',
    2342: 'Governor Idle during Bailout',
    2343: 'Governor Output Ch',
}

def reg_desc(reg):
    if reg in regdes:
        return regdes[reg]
    else:
        return '<unknown>'

def reg_num(reg):
    if reg < 1000:
        return str(reg)
    else:
        return ' * '

def basename(name):
    return name[name.rfind('/')+1:]

def pm(pos):
    if pos:
        return '+'
    else:
        return '-'

def yesno(yes):
    if yes:
        return 'Yes'
    else:
        return 'No'


def format_gov_type(file,reg,val):
    if val == -1:
        return 'disabled'
    elif val == 2:
        return 'expert/fixed/off'
    elif val == 4:
        return 'expert/collective-output'
    elif val == 5:
        return 'expert/throttle curve only'
    elif val == 7:
        return 'nitro'
    elif val == 8:
        return 'elec'
    elif val == 10:
        return 'expert/fixed/on'
    else:
        return '<undef>'

def format_gov_flags(file,reg,val):
    return 'Digi{} Rev{}'.format(
	pm(val&0x40),
        pm(val&0x01))

def format_gov_output(file,reg,val):
    if val == 0:
        return 'servo'
    elif val == 1:
        return 'ch4'
    elif val == 2:
        return 'esc'
    elif val == 3:
        return 'none'

def format_gov_speed(file,reg,val):
    return "{}rpm".format(val * 50)

def format_gov_channel(file,reg,val):
    if val == -1:
        return 'internal'
    elif (val > -1) & (val < 12):
        return 'ch{}'.format(val+1)
    else:
        return '<unknown>'

def format_gov_gearing(file,reg,val):
    return '%.3f' % (val)

def format_servo_flags(file,reg,val):
    return 'Rev{} Geo:{}'.format(pm(val&0x01), (val>>1)&0x0F)

def format_sensor_flags(file,reg,val):
    return 'Rev{}'.format(pm(val&0x01))

def format_tail_flags(file,reg,val):
    return 'RevIN{} RevRD{}'.format(pm(val&0x01), pm(val&0x02))

def format_receiver_type(file,reg,val):
    if val == 0:
        return 'Separate PPM'
    elif val == 1:
        return 'Spektrum SAT'
    elif val == 2:
        return 'CPPM'
    elif val == 6:
        return 'SBUS'
    elif val == 7:
        return 'Spektrum HiRes'
    elif val == 8:
        return 'UDI'
    elif val == 9:
        return 'Spektrum Digital'
    elif val == 10:
        return 'Spektrum DSM-X 11ms'
    elif val == 11:
        return 'Spektrum DSM-X 22ms'
    else:
        return '<invalid>'

def format_servo_rate(file,reg,val):
    if val > 0:
        return '{}Hz'.format(1000//val)
    else:
        return '<invalid>'

def format_servo_type(file,reg,val):
    if val == 0:
        return '1520us'
    elif val == 1:
        return '760us'
    elif val == 2:
        return '960us'
    else:
        return '<invalid>'

def format_main_style(file,reg,val):
    if val == 2:
        return 'Vivid'
    elif val == 3:
        return 'Medium'
    elif val == 4:
        return 'Precise'
    elif val == 5:
        return 'Mechanical'
    else:
        return '<invalid>'

def format_cyclic_throw(file,reg,val):
    return str(59+(val-38)*61//39)

def format_yaw_rate(file,reg,val):
    return str(40+(val-19)*81//39)

def format_main_adj(file,reg,val):
    return str(120-((val+30)*80//70))

def format_yesno(file,reg,val):
    return yesno(val)

def format_double(file,reg,val):
    return str(2*val)

def format_double_neg(file,reg,val):
    return str(-2*val)

def format_ch(file,reg,val):
    return 'ch{}'.format(val+1)


reg_format = {
      7: format_double,
      8: format_double,
     30: format_double,
     33: format_double,
     35: format_double,
     40: format_double,
     41: format_main_adj,
     52: format_cyclic_throw,
     70: format_gov_speed,
     72: format_main_style,
     79: format_yaw_rate,
     80: format_gov_type,
     89: format_double_neg,
    200: format_servo_flags,
    201: format_servo_flags,
    202: format_servo_flags,
    203: format_servo_flags,
    204: format_sensor_flags,
    205: format_sensor_flags,
    206: format_tail_flags,
    207: format_sensor_flags,
    210: format_ch,
    211: format_ch,
    212: format_ch,
    213: format_ch,
    214: format_ch,
    215: format_ch,
    216: format_ch,
    219: format_receiver_type,
    221: format_servo_rate,
    222: format_servo_rate,
    223: format_servo_type,
    228: format_yesno,
    229: format_yesno,
    231: format_double_neg,
    232: format_double,
    234: format_gov_flags,
    236: format_gov_channel,
    239: format_gov_channel,
    241: format_yesno,
   2331: format_gov_gearing,
   2341: format_yesno,
   2342: format_yesno,
   2343: format_gov_output,
}

def format_reg(file,reg):
    if reg in values[file]:
        if reg in reg_format:
            return '%s [%s]' % (reg_format[reg](file,reg,values[file][reg]), values[file][reg])
        else:
            return str(values[file][reg])
    else:
        return '<absent>'

def print_reg_for_each_file(reg):
    str = "[%+3s] %-30s" % (reg_num(reg), reg_desc(reg))
    for file in files:
        str += " %-20s" % (format_reg(file,reg))
    print(str)

def convert_regs(file,regs):
    regs[1091] = '%d.%d.%d' % ((regs[109] >> 4) & 0x0F,(regs[109] >> 0) & 0x0F, regs[499])
    regs[2331] = 0.1 * regs[233] + 0.001 * regs[235]
    regs[2341] = ((regs[234] & 0x08) >> 3)
    regs[2342] = ((regs[234] & 0x20) >> 5)
    regs[2343] = ((regs[234] & 0x06) >> 1)
    return regs

def read_vbr(name):
    vbr_regs = {}
    parser = re.compile(r'<VALUE Register="([-]?[0-9]+)" Value="([-]?[0-9]+)"/>')
    file = open(name)
    for line in file:
        res = parser.search(line)
        if res:
            reg = int(res.group(1))
            val = int(res.group(2))
            vbr_regs[reg] = val
            def_regs[reg] = True
    file.close()
    return convert_regs(name,vbr_regs)

def write_vbr(name,regs):
    file = open(name, "w")
    file.write('<REGISTER>\n')
    for reg in sorted(regs):
        if reg < 1000:
            file.write('    <VALUE Register="%s" Value="%s"/>\n' % (reg,regs[reg]))
    file.write('</REGISTER>\n')
    file.close()



## Commands

def print_version():
    print('VBRTool version %s' % (Version))

def print_names():
    str = "      %-30s" % ('Input files')
    for file in files:
        str += " %-20s" % (basename(file))
    print(str)
    print('=' * len(str))

def print_regs(regs):
    print_names()
    for reg in regs:
        print_reg_for_each_file(reg)
        
def diff_regs(regs):
    print_names()
    for reg in regs:
        val = None
        for file in files:
            if val == None:
                if reg in values[file]:
                    val = values[file][reg]
            elif val != values[file][reg]:
                print_reg_for_each_file(reg)
                break

def copy_regs(src,regs):
    for reg in regs:
        if reg in src:
            for name in files:
                values[name][reg] = src[reg]
    for name in files:
        write_vbr(name, values[name])


##
## Main program
##

values = {}
raw_regs = []
def_regs = {}

regs = basic_regs


## Parse command line

parser = argparse.ArgumentParser(usage=Usage)

parser.add_argument("-V", "--version", action="store_true", help="Print VBRTool version")
parser.add_argument("-P", "--print", action="store_true", help="Print parameters [default]")
parser.add_argument("-D", "--diff",  action="store_true", help="Compare parameters")
parser.add_argument("-C", "--copy",  nargs=1, help="Copy parameters")

parser.add_argument("-a", "--all", action="store_true", help="All known parameters")
parser.add_argument("-r", "--raw", action="store_true", help="All input registers")

parser.add_argument("-m", "--main", action="store_true", help="Main rotor settings")
parser.add_argument("-t", "--tail", action="store_true", help="Tail rotor settings")
parser.add_argument("-g", "--gov", action="store_true", help="Governor settings")
parser.add_argument("-x", "--exp", action="store_true", help="Expert settings")

parser.add_argument("-ms", "--main-setup", action="store_true", help="Main rotor / swash setup")
parser.add_argument("-ts", "--tail-setup", action="store_true", help="Tail rotor setup")
parser.add_argument("-gs", "--gov-setup", action="store_true", help="Governor setup")
parser.add_argument("-rs", "--rx-setup", action="store_true", help="Receiver setup")
parser.add_argument("-s",  "--setup", action="store_true", help="All setup parameters")

parser.add_argument("files", nargs='*', help="Input files")

args = parser.parse_args()

files = args.files


## Actions

if args.version:
    print_version()
    exit(0)

if not files:
    parser.print_help()
    exit(0)

for name in files:
    values[name] = read_vbr(name)

raw_regs = sorted(def_regs)

if args.copy:
    source = read_vbr(args.copy[0])

if args.all:
    regs = all_regs
elif args.raw:
    regs = raw_regs
elif args.main:
    regs = main_regs
elif args.tail:
    regs = tail_regs
elif args.gov:
    regs = gov_regs
elif args.exp:
    regs = exp_regs

elif args.main_setup:
    regs = main_setup_regs
elif args.tail_setup:
    regs = tail_setup_regs
elif args.gov_setup:
    regs = gov_setup_regs
elif args.rx_setup:
    regs = rx_setup_regs
elif args.setup:
    regs = setup_regs

if args.copy:
    copy_regs(source,regs)
elif args.diff:
    diff_regs(regs)
else:
    print_regs(regs)


## EOF
