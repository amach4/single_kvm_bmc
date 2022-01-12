#!/usr/bin/python3

# # # #
#
# 
# Name: single_kvm_bmc
#
# Author: Andreas Mach
#
# Date: 28-03-2018
#
# Description:
#
# This python script generates a virtual BMC (Baseboard Management Controller) for a KVM domain - based on "ipmi_sim" - IPMI LAN BMC Simulator 
#
# man page: man ipmi_sim
#
#
# # # # 
#
#
# KVM domain setup - add this XML output:
#
#<domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
#
#  <snip>
#
#  <qemu:commandline>
#    <qemu:arg value='-chardev'/>
#    <qemu:arg value='socket,id=ipmi0,host=0.0.0.0,port=60011,reconnect=10'/>
#    <qemu:arg value='-device'/>
#    <qemu:arg value='ipmi-bmc-extern,id=bmc0,chardev=ipmi0'/>
#    <qemu:arg value='-device'/>
#    <qemu:arg value='isa-ipmi-bt,bmc=bmc0'/>
#  </qemu:commandline>
#</domain>
#
#
# # # #
#
#
# usable "ipmitool" commands are - examples:
#
# ipmitool -I lanplus -U root -P hos -H 192.168.8.11 chassis power status
#
# ipmitool -I lanplus -U root -P hos -H 192.168.8.11 chassis power on
#
# ipmitool -I lanplus -U root -P hos -H 192.168.8.11 chassis power off
#
# ipmitool -I lanplus -U root -P hos -H 192.168.8.11 chassis bootdev pxe
#
# ipmitool -I lanplus -U root -P hos -H 192.168.8.11 chassis bootdev disk
#
# ipmitool -I lanplus -U root -P hos -H 192.168.8.11 chassis bootdev cdrom
#
# # # #

from __future__ import print_function
from xml.dom import minidom
import sys
import libvirt
import subprocess
import os
import ipaddress

print()
dom_name = input("  Please enter KVM domain name: ")
domname = dom_name

dom_bmc_ip = input("  Please enter KVM domain BMC IP address: ")
dombmcip = dom_bmc_ip

dom_bmc_user = input("  Please enter KVM domain BMC username: ")
dombmcuser = dom_bmc_user

dom_bmc_pass = input("  Please enter KVM domain BMC user password: ")
dombmcpass = dom_bmc_pass

dom_port = dom_bmc_ip.split('.')[3]
domport = dom_port

# Section 1 - KVM domain verification

# get current KVM domain status 

print()
print("--------------------------------------------------------------------------------------------------------")
print()
print('  KVM domain used BMC settings:')
print()
print('  KVM domain: \t \t ' + domname)
print('  KVM domain BMC IP: \t ' + dombmcip)
print('  KVM domain BMC user: \t ' + dombmcuser)
print('  KVM domain BMC pass: \t ' + dombmcpass)
conn = libvirt.open('qemu:///system')
if conn == None:
  print('  Failed to open connection to qemu:///system', file=sys.stderr)
  exit(1)

dom = conn.lookupByName(domname)
if dom == None:
  print('  Failed to find the domain '+domname, file=sys.stderr)
  exit(1)

flag = dom.isActive()
if flag == True:
  print('  KVM domain status: \t active')
else:
  print('  KVM domain is not active.')
conn.close()


# get current KVM domain id

conn = libvirt.open('qemu:///system')
if conn == None:
  print('  Failed to open connection to qemu:///system', file=sys.stderr)
  exit(1)

dom = conn.lookupByName(domname)
if dom == None:
  print('  Failed to find the domain '+ domname, file=sys.stderr)
  exit(1)

id = dom.ID()
if id == -1:
  print('  KVM domain is not running so has no ID.')
else:
  print('  KVM domain ID: \t ' + str(id))

conn.close()
#  exit(0)


# show used KVM host IP:port

print('  KVM host "ip:port" \t 0.0.0.0:600' + domport)


# Section 2 - set file and folder names
# "ipmi_sim" config filename
dncon = domname + "-bmc.conf"
 
# systemd filename
dnser = domname + "-bmc.service"
 
# if it exists delete previous KVM domain folder and "ipmi_sim" config files
domdir = "/etc/ipmi/" + domname
if os.path.isdir(domdir):
  subprocess.call(['rm', '-rf', '/etc/ipmi/' + domname])

# create directory for each node in "/etc/ipmi/"
path = '/etc/ipmi/' + domname

#os.makedirs( path,0o755, exist_ok=True)
os.makedirs( path,0o755)


# Section 3 - create "ipmi_sim" configuration files
# create sensor file: "/tmp/file1.ipm"

f = open('/tmp/file1.ipm','w')
f.write('30\n')
f.close

# create "ipmi_sim_chassiscontrol" config file - example: "/etc/ipmi/hos-n1/ipmi_sim_chassiscontrol"

f = open('/etc/ipmi/' + domname + '/ipmi_sim_chassiscontrol','w')
f.write('#!/bin/sh\n')
f.write('#set -x\n')
f.write('#\n')
f.write('# An example script for handling external power control.\n')
f.write('\n')
f.write('# It\'s parameters are:\n')
f.write('#\n')
f.write('#  ipmi_sim_chassiscontrol <device> get [parm [parm ...]]\n')
f.write('#  ipmi_sim_chassiscontrol <device> set [parm val [parm val ...]]\n')
f.write('#\n')
f.write('# where <device> is the particular target to reset and parm is either\n')
f.write('# "power", "reset", or "boot".\n')
f.write('#\n')
f.write('# The output of the "get" is "<parm>:<value>" for each listed parm,\n')
f.write('# and only power is listed, you cannot fetch reset.\n')
f.write('# The output of the "set" is empty on success.  Error output goes to\n')
f.write('# standard out (so it can be captured in the simulator) and the program\n')
f.write('# returns an error.\n')
f.write('#\n')
f.write('# The values for power and reset are either "1" or "0".  Note that\n')
f.write('# reset does a pulse, it does not set the reset line level.\n')
f.write('#\n')
f.write('# The value for boot is either "none", "pxe" or "default".\n')
f.write('\n')
f.write('#echo "$*" >> /root/vbmc-qemu/workspace/f63b94c8-dfab-4399-872f-958c4c33e984--0/operate.record\n')
f.write('#prog=$0\n')
f.write('\n')
f.write('device=$1\n')
f.write('if [ "x$device" = "x" ]; then\n')
f.write('    echo "No device given"\n')
f.write('    exit 1;\n')
f.write('fi\n')
f.write('shift\n')
f.write('\n')
f.write('op=$1\n')
f.write('if [ "x$op" = "x" ]; then\n')
f.write('    echo "No operation given"\n')
f.write('    exit 1\n')
f.write('fi\n')
f.write('shift\n')
f.write('\n')
f.write('\n')
f.write('do_get() {\n')
f.write('    while [ "x$1" != "x" ]; do\n')
f.write('	case $1 in\n')
f.write('	    power)\n')
f.write('\n')
f.write('		# get current KVM domain power state\n')
f.write('\n')
f.write("		dom_power_state=$(virsh domstate " + domname + ")\n")
f.write('		if [ "x$dom_power_state" != "xrunning" ]\n')
f.write('		then\n')
f.write('		    order=${order:-nd}\n')
f.write('		    power=${power:-off}\n')
f.write('		    bootdev=${bootdev:-pxe}\n')
f.write('		else\n')
f.write('		    order=${order:-nd}\n')
f.write('		    power=${power:-on}\n')
f.write('		    bootdev=${bootdev:-pxe}\n')
f.write('		fi\n')
f.write('		echo $order\n')
f.write('		echo $power\n')
f.write('		echo $bootdev\n')
f.write('\n')
f.write('		gen_cmd() {\n')
f.write('		    local order=$1\n')
f.write('		    local power=$2\n')
f.write('		    local bootdev=$3\n')
f.write('		}\n')
f.write('\n')
f.write('\n')
f.write('		shift $((OPTIND-1))\n')
f.write('\n')
f.write('		gen_cmd $order $power $bootdev\n')
f.write('\n')
f.write('		# needed to parse "val" to "ipmi_sim"\n')
f.write('\n')
f.write('		if [ "x$power" == "xoff" ]; then\n')
f.write('		    val=0\n')
f.write('                    echo "Power off"\n')
f.write('		else\n')
f.write('		    val=1\n')
f.write('                    echo "Power on"\n')
f.write('		fi\n')
f.write('\n')
f.write('		;;\n')
f.write('\n')
f.write('	    boot)\n')
f.write('		val=default\n')
f.write('		if [ "$val" == "pxe" ]; then\n')
f.write('	            val="pxe"\n')
f.write('		elif [ "$val" == "disk" ]; then\n')
f.write('	            val="default"\n')
f.write('		else\n')
f.write('		val="none"\n')
f.write('		fi\n')
f.write('		\n')
f.write('		;;\n')
f.write('\n')
f.write('	    # Note that reset has no get\n')
f.write('\n')
f.write('	    *)\n')
f.write('		echo "Invalid parameter: $power"\n')
f.write('		exit 1\n')
f.write('		;;\n')
f.write('	esac\n')
f.write('\n')
f.write('	echo "$1:$val"\n')
f.write('	shift\n')
f.write('    done\n')
f.write('}\n')
f.write('\n')
f.write('do_set() {\n')
f.write('    while [ "x$1" != "x" ]; do\n')
f.write('	parm="$1"\n')
f.write('	shift\n')
f.write('	if [ "x$1" = "x" ]; then\n')
f.write('	    echo "No value present for parameter $parm"\n')
f.write('	    exit 1\n')
f.write('	fi\n')
f.write('	val="$1"\n')
f.write('	shift\n')
f.write('\n')
f.write('	case $parm in\n')
f.write('	    power)\n')
f.write('                case $val in\n')
f.write('                0) # power off\n')
f.write('                echo "Power off"\n')
f.write('\n')
f.write('		# get current KVM domain power state\n')
f.write('\n')
f.write("		dom_power_state=$(virsh domstate " + domname + ")\n")
f.write('                if [ "x$dom_power_state" != "xrunning" ]\n')
f.write('                then\n')
f.write('                    order=${order:-nd}\n')
f.write('                    power=${power:-off}\n')
f.write('                    bootdev=${bootdev:-pxe}\n')
f.write('                else\n')
f.write('                    order=${order:-nd}\n')
f.write('                    power=${power:-on}\n')
f.write('                    bootdev=${bootdev:-pxe}\n')
f.write('                fi\n')
f.write('\n')
f.write('		# destroy KVM domain\n')
f.write('                # needed to parse "val" to "ipmi_sim"\n')
f.write('\n')
f.write('                if [ "x$power" == "xoff" ]; then\n')
f.write('                    val=0\n')
f.write('                    echo -e "KVM domain: ...already destroyed."\n')
f.write('                else\n')
f.write('                    val=1\n')
f.write('                    virsh destroy ' + domname + '\n')
f.write('                    echo -e "KVM domain: virsh destroy ' + domname + '"\n')
f.write('                fi\n')
f.write('\n')
f.write('                ;;\n')
f.write('\n')
f.write('                1) # power on\n')
f.write('                echo "Power on"\n')
f.write('                \n')
f.write('		# get current KVM domain power state\n')
f.write('\n')
f.write("		dom_power_state=$(virsh domstate " + domname + ")\n")
f.write('                if [ "x$dom_power_state" != "xrunning" ]\n')
f.write('                then\n')
f.write('                    order=${order:-nd}\n')
f.write('                    power=${power:-off}\n')
f.write('                    bootdev=${bootdev:-pxe}\n')
f.write('                else\n')
f.write('                    order=${order:-nd}\n')
f.write('                    power=${power:-on}\n')
f.write('                    bootdev=${bootdev:-pxe}\n')
f.write('                fi\n')
f.write('		\n')
f.write('               # start KVM domain\n')
f.write('               # needed to parse "val" to "ipmi_sim"\n')
f.write('\n')
f.write('                if [ "x$power" == "xoff" ]; then\n')
f.write('                    val=0\n')
f.write('                    virsh start ' + domname + '\n')
f.write('                    echo -e "KVM domain: virsh start ' + domname + '"\n')
f.write('                else\n')
f.write('                    val=1\n')
f.write('                    echo -e "KVM domain: ...already started."\n')
f.write('                fi\n')
f.write('\n')
f.write('               ;;\n')
f.write('        esac\n')
f.write('	       ;;\n')
f.write('\n')
f.write('#	    shutdown)\n')
f.write('#        \n')
f.write('#        case $val in\n')
f.write('#            1) # power soft\n')
f.write('#            echo "Soft shutdown"\n')
f.write('#            pkill -F $qemu_pidfile\n')
f.write('#            /etc/ipmi/hos-n6/ipmi_sim_vmstatus -p off $status_file\n')
f.write('#            ;;\n')
f.write('#        esac\n')
f.write('#		;;\n')
f.write('\n')
f.write('           # reset KVM domain\n')
f.write('\n')
f.write('           reset)\n')
f.write('\n')
f.write('                echo "Power reset"\n')
f.write('                virsh reset  ' + domname + '\n')
f.write('                echo -e "KVM domain: virsh reset ' + domname + '"\n')
f.write('		;;\n')
f.write('\n')
f.write('	    boot)\n')
f.write('		case $val in\n')
f.write('		    none)\n')
f.write('			;;\n')
f.write('		    pxe)\n')
f.write('			virt-xml ' + domname + ' --edit --boot network,hd,cdrom\n')
f.write('			echo "KVM domain: ...network boot enabled."\n')
f.write('			;;\n')
f.write('	            disk)\n')
f.write('			virt-xml ' + domname + ' --edit --boot hd,network,cdrom\n')
f.write('			echo "KVM domain: ...disk boot enabled."\n')
f.write('			;;\n')
f.write('	            cdrom)\n')
f.write('			virt-xml ' + domname + ' --edit --boot cdrom,hd,network\n')
f.write('			echo "KVM domain: ...cdrom boot enabled."\n')
f.write('			;;\n')
f.write('		    bios)\n')
f.write('		        ;;\n')
f.write('		    default)\n')
f.write('			virt-xml ' + domname + ' --edit --boot hd,network,cdrom\n')
f.write('			echo "KVM domain: ...default disk boot enabled."\n')
f.write('         		;;\n')
f.write('		    *)\n')
f.write('			echo "Invalid boot value: $val"\n')
f.write('			exit 1\n')
f.write('			;;\n')
f.write('		esac\n')
f.write('		;;\n')
f.write('\n')
f.write('            identify)\n')
f.write('		interval=$val\n')
f.write('		force=$1\n')
f.write('		shift\n')
f.write('		;;\n')
f.write('\n')
f.write('	    *)\n')
f.write('		echo "Invalid parameter: $parm"\n')
f.write('		exit 1\n')
f.write('		;;\n')
f.write('	esac\n')
f.write('    done\n')
f.write('}\n')
f.write('\n')
f.write('do_check() {\n')
f.write('    # Check is not supported for chassis control\n')
f.write('    exit 1\n')
f.write('}\n')
f.write('\n')
f.write('\n')
f.write('case $op in\n')
f.write('    get)\n')
f.write('	do_get $@\n')
f.write('	;;\n')
f.write('    set)\n')
f.write('	do_set $@\n')
f.write('	;;\n')
f.write('\n')
f.write('    check)\n')
f.write('	do_check $@\n')
f.write('	;;\n')
f.write('\n')
f.write('*)\n')
f.write('	echo "Unknown operation: $op"\n')
f.write('	exit 1\n')
f.write('esac\n')
f.write('\n')
f.close()

# create "ipmi_sim" conf file - example: /etc/ipmi/hos-n1/hos-n1-bmc.conf

f = open("/etc/ipmi/" + domname + "/" + dncon,"w")
f.write('name \"ipmisim1\"\n')
f.write('set_working_mc 0x20\n')
f.write(' startlan 1\n')
f.write('   addr ' + dombmcip + ' ' +  '623\n')
f.write('   priv_limit admin\n')
f.write('   allowed_auths_callback none md2 md5 straight\n')
f.write('   allowed_auths_user none md2 md5 straight\n')
f.write('   allowed_auths_operator none md2 md5 straight\n')
f.write('   allowed_auths_admin none md2 md5 straight\n')
f.write('   guid "I_am_BMC"\n')
f.write(' endlan\n')
f.write(' chassis_control "/etc/ipmi/' + domname + '/ipmi_sim_chassiscontrol 0x20"\n')
f.write(' serial 15 0.0.0.0 600' + domport + ' codec VM\n')
f.write(' startnow false\n')
f.write(' user 1 true  ""        "test"  user    10       none md2 md5 straight\n')
f.write(' user 2 true  "ipmiusr" "test"  admin   10       none md2 md5 straight\n')
f.write(' user 3 true   "' + dombmcuser + '" "' +  dombmcpass + '"  admin   10       none md2 md5 straight\n')
f.close()


# Section 4 - create systemd unit file
# create systemd unit file - example: /etc/systemd/system/hos-n1-bmc.service

# stop systemd service - bash command: systemctl stop hos-n1-bmc.service 
subprocess.call(['systemctl', 'stop', dnser])

f = open("/etc/systemd/system/" + dnser,"w")
f.write('[Unit]\n')
f.write('Description=ipmi_sim BMC ' + dombmcip + '\n')
f.write('After=network-online.target\n')
f.write('\n')
f.write('[Service]\n')
f.write('WorkingDirectory=/tmp\n')
f.write('Type=simple\n')
f.write('ExecStart=/usr/bin/ipmi_sim -n -c /etc/ipmi/' + domname + '/' + domname + '-bmc.conf\n')
f.write('KillMode=process\n')
f.write('\n')
f.write('[Install]\n')
f.write('WantedBy=multi-user.target\n')
f.close()

# systemctl enable hos-n1-bmc.service
subprocess.call(['systemctl', 'enable', dnser])

# systemctl start hos-n1-bmc.service
subprocess.call(['systemctl', 'start', dnser])


# set file permissions
# chmod 644 /etc/systemd/system/hos-n1-bmc.service

subprocess.call(['chmod', '744', '/etc/ipmi/' + domname + '/ipmi_sim_chassiscontrol'])
subprocess.call(['chmod', '644', '/etc/systemd/system/'+ dnser])


print()
print("--------------------------------------------------------------------------------------------------------")
print()
print('  Configuration files successfully created and stored in \"/etc/ipmi/' + domname + '"' )
print()
print("--------------------------------------------------------------------------------------------------------")
print()
print("  !! IMPORTANT !! make sure your KVM domain XML includes the following lines: ")
print()
print("<domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>")
print()
print("   <snip\>")
print()
print("  <qemu:commandline>")
print("    <qemu:arg value='-chardev'/>")
print("    <qemu:arg value='socket,id=ipmi0,host=0.0.0.0,port=600" + domport + ",reconnect=10'/>")
print("    <qemu:arg value='-device'/>")
print("    <qemu:arg value='ipmi-bmc-extern,id=bmc0,chardev=ipmi0'/>")
print("    <qemu:arg value='-device'/>")
print("    <qemu:arg value='isa-ipmi-bt,bmc=bmc0'/>")
print("  </qemu:commandline>")
print("</domain>")
print("--------------------------------------------------------------------------------------------------------")
print()
