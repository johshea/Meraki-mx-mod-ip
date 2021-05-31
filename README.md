# Meraki-mx-mod-ip
#this script is a prototype, and very specific. As always it should be executed on aproduction env only after thourough testing.
#This script functions as a way to modify the gateway vlan of a templated network to a non .1 value. Includes for a dryrunmode that does not modify
#the dashboard
#Full Mode (will read data from dashboard and commit changes)
# usage python3 main.py -k <api key> -o <specific org name> -m full
#
#Dry Run Mode (will read data from dashboard but only simulate the results)
#usage python3 main.py -k <api key> -o <specific org name> -m dryrun
