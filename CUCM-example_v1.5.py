#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      J0277261
#
# Created:     05/11/2012
# Copyright:   (c) J0277261 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import callmanager
import argparse

def main():
    parser=argparse.ArgumentParser(description="Extracts data from Cisco Callmanager and saves to a CSV file. \
                                    The actual query is defined in cucm.cfg")
    parser.add_argument("-c", "--config", help="Enter a different config file name - if it doesn't exist it will be created with default values")
    parser.set_defaults(config="cucm.cfg")
    args=parser.parse_args()

    config = readConfigFile(args.config)
    service=config['server']
    export_file=config['export_file_path']
    query=config['query'].replace("\n"," ")
    password=config['password'].decode('base64')

    cm=callmanager.callmanager(service,query)
    cm.setCredentials(password)
    cm.getCMData()
    cm.parseET()
    print cm
    cm.writeCSV('cucm-oo.csv')


def initConfigFile(cfgfilepath='CUCM.cfg'):
    import ConfigParser, getpass

    server = "https://callmanager:8443/axl/"

    query = "SELECT d.name, d.description, tp.name as devicetype, \
            n.dnorpattern AS dn, part.name as partname, css.name AS cssname, \
            pug.name AS pickupgroup, n.alertingname, \
            vm.name as vmprofile, n.cfaptvoicemailenabled, n.cfbintvoicemailenabled, \
            n.cfnavoicemailenabled, \
            user.firstname, user.lastname, user.userid \
            FROM device AS d \
            INNER JOIN devicenumplanmap AS dmap ON dmap.fkdevice=d.pkid \
            INNER JOIN numplan AS n ON dmap.fknumplan=n.pkid \
            LEFT JOIN voicemessagingprofile AS vm ON n.fkvoicemessagingprofile=vm.pkid \
            LEFT JOIN routepartition AS part ON n.fkroutepartition=part.pkid \
            LEFT JOIN callingsearchspace AS css ON n.fkcallingsearchspace_sharedlineappear=css.pkid \
            LEFT JOIN typeproduct AS tp ON d.tkproduct=tp.enum \
            LEFT JOIN pickupgrouplinemap AS pu ON n.pkid=pu.fknumplan_line \
            LEFT JOIN pickupgroup AS pug ON pu.fkpickupgroup=pug.pkid \
            LEFT JOIN enduser AS user ON n.dnorpattern=user.telephonenumber \
            WHERE d.tkclass=1 \
            ORDER BY d.name"

    filepath='callmanager.csv'
    password=getpass.getpass('Please enter the callmanager password: ')

    config=ConfigParser.RawConfigParser()
    config.add_section('SQL')
    config.set('SQL','query',query)
    config.add_section('config')
    config.set('config','export_file_path',filepath)
    config.set('config','server', server)
    config.set('config','password',password.encode('base64'))
    with open(cfgfilepath, 'wb') as configfile:
        config.write(configfile)

def readConfigFile(cfgfile='CUCM.cfg'):
    import ConfigParser
    config=ConfigParser.RawConfigParser()
    try:
        open(cfgfile,'r')
    except:
        initConfigFile(cfgfile)

    config.read(cfgfile)

    cfg=dict()

    cfg['password']=config.get('config','password')
    cfg['server']=config.get('config','server')
    cfg['export_file_path']=config.get('config','export_file_path')
    cfg['query']=config.get('SQL', 'query')
    return cfg




    pass

if __name__ == '__main__':
    main()
