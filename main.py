#this script is a prototype, and very specific. As always it should be executed on aproduction env only after thourough testing.
#This script functions as a way to modify the gateway vlan of a templated network to a non .1 value. Includes for a dryrunmode that does not modify
#the dashboard
#Full Mode (will read data from dashboard and commit changes)
# usage python3 main.py -k <api key> -o <specific org name> -m full
#
#Dry Run Mode (will read data from dashboard but only simulate the results)
#usage python3 main.py -k <api key> -o <specific org name> -m dryrun
#Meraki as code

import requests
import datetime
import time
import sys
import getopt

#Modify submitted Ip address to requirments
def modip(vlan, address):
    #Ignore Vlan1
    if vlan != 1:

      if vlan == 20:
          addr = address.split('.')
          paddr = addr.pop()
          paddr = int(paddr)+49
          paddr = str(paddr)
          addr.append(paddr)
          modaddress = '.'.join(addr)
          # test return value
          #print(modaddress)
          return(modaddress)

      #modify /28
      elif vlan == 70 or vlan == 50 or vlan == 42 or vlan == 41 or vlan == 30:
          addr = address.split('.')
          paddr = addr.pop()
          paddr = int(paddr) + 13
          paddr = str(paddr)
          addr.append(paddr)
          modaddress = '.'.join(addr)
          # test return value
          #print(modaddress)
          return (modaddress)

      #modify /27
      elif vlan == 10 or vlan == 40 or vlan == 60:
          addr = address.split('.')
          paddr = addr.pop()
          paddr = int(paddr) + 29
          paddr = str(paddr)
          addr.append(paddr)
          modaddress = '.'.join(addr)
          # test return value
          # print(maddr)
          return (modaddress)

      else:
         print('an Unknown Vlan Id has been encountered')
         return

    return


def main(argv):
    global arg_apikey
    global m_baseUrl

    arg_apikey = None
    arg_orgname = None
    arg_mode = None

    try:
        opts, args = getopt.getopt(argv, 'k:o:m:')
    except getopt.GetoptError:
        sys.exit(0)

    for opt, arg in opts:
        if opt == '-k':
            arg_apikey = arg
        elif opt == '-o':
            arg_orgname = arg
        elif opt == '-m':
            arg_mode = arg

    #print(arg_apikey)
    #print(arg_orgname)
    print("Mode is" + " " +arg_mode)





    if arg_apikey is None or arg_orgname is None or arg_mode is None:
        print('Please specify the required values!')
        sys.exit(0)

    if arg_mode != 'full' and arg_mode != 'dryrun':
        print("Please select a valid run mode (full or dryrun)")
        sys.exit(0)


    # set needed vlaues from env_vars
    m_headers = {'X-Cisco-Meraki-API-Key': arg_apikey}
    m_baseUrl = 'https://api.meraki.com/api/v1'

    timenow = datetime.datetime.now()

    #create log file
    f = open(arg_orgname + '_' 'modip' + '_' + str(timenow) + '.txt', 'w+' )

    # get orgid for specified org name
    org_response = requests.request("GET", f'{m_baseUrl}/organizations/', headers=m_headers)
    org = org_response.json()
    for row in org:
        if row['name'] == arg_orgname:
            orgid = row['id']
            print("Org" + " " + row['name'] + " " + "found.")
        else:
            print("Exception: This Org does not match:" + ' ' + row['name'] + ' ' + 'Is not the orginization specified!')

    # get network Ids from ORG
    net_response = requests.request("GET", f'{m_baseUrl}/organizations/{orgid}/networks/', headers=m_headers)
    if 'json' in net_response.headers.get('Content-Type'):
        networks = net_response.json()
        # test return data
        # print(networks)

    # get vlans
    for network in (network for network in networks if 'mod' in network['tags']):
    #for network in (network for network in networks if network['tags'] == ['mod']):
        vlan_response = requests.request("GET", f'{m_baseUrl}/networks/{network["id"]}/appliance/vlans',
                                         headers=m_headers)
        f.write("#########################\n" + "Network ID: " + network['id'] + "\n" + "Name: " + network['name'] + "\n")

        if 'json' in vlan_response.headers.get('Content-Type'):
            vlans = vlan_response.json()

            # test return data
            print(vlans)

            # pull vlan and applianceip association
            for i in range(len(vlans)):
                print(vlans[i]['id'])
                modaddress = modip(vlans[i]['id'], vlans[i]['applianceIp'])
                print(modaddress)

                payload = {
                    "applianceIp": modaddress
                    }
                #print(payload)  # print output for debug or live monitoring
                if arg_mode == 'full':
                      mod_response = requests.request("PUT", f'{m_baseUrl}/networks/{network["id"]}/appliance/vlans/{vlans[i]["id"]}', headers=m_headers, data=payload)
                      print(mod_response.text.encode('utf8'))

                elif arg_mode == 'dryrun':
                    print("Dryrun only, vlan data not committed")



                #Write the set to the log
                f.write('Vlan ID:' + str(vlans[i]["id"]) + '\n' + 'IP Gateway:' + str(modaddress) + '\n')

                time.sleep(2)  # Sleep for 2 seconds to let the API catch up

        f.write("#########################\n\n")


    time.sleep(2) #Sleep for 2 seconds to let the API catch up
    # it is done
    f.close()
    if arg_mode == 'full':
        print("\nNetwork Gateways updated!\n")
    elif arg_mode == 'dryrun':
        print("\nDryrun complete! Review data for accuracy\n")
    sys.exit(0)


if __name__ == '__main__':
    main(sys.argv[1:])