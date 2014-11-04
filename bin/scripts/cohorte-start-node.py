#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Script for starting COHORTE node.

:author: Bassem Debbabi
:license: Apache Software License 2.0

..

    Copyright 2014 isandlaTech

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from __future__ import print_function

# Documentation strings format
__docformat__ = "restructuredtext en"

# Script module version
__version__ = "1.0.0"

# Standard Library
import argparse
import os
import sys
import shutil
import json

# cohorte scripts
import common

def parse_config_file(config_file):
    """
    Parses the startup configuration file (run.js).
    """
    from pprint import pprint
    data = None
    if os.path.isfile(config_file):
        with open(config_file) as json_data:
            data = json.load(json_data)
    return data


def get_external_config(parsed_conf_file, conf_name):
    """
    Returns the value of the wanted startup configuration. 
    """
    if parsed_conf_file is not None  and conf_name is not None:        
        if "application-id" in parsed_conf_file:
            if conf_name == "application-id":
                return parsed_conf_file["application-id"]
        if "node" in parsed_conf_file:
            if conf_name == "node-name":
                if "name" in parsed_conf_file["node"].keys():
                    return parsed_conf_file["node"]["name"]
            if conf_name == "top-composer":
                if "top-composer" in parsed_conf_file["node"].keys():
                    return parsed_conf_file["node"]["top-composer"]
            elif conf_name == "web-admin":
                if "web-admin" in parsed_conf_file["node"].keys():
                    return parsed_conf_file["node"]["web-admin"]
            elif conf_name == "shell-admin":
                if "shell-admin" in parsed_conf_file["node"].keys():
                    return parsed_conf_file["node"]["shell-admin"]
        if "transport" in parsed_conf_file:
            if conf_name == "transport":
                return parsed_conf_file["transport"]
        if "transport-xmpp" in parsed_conf_file:
            if conf_name == "xmpp-server":
                if "xmpp-server" in parsed_conf_file["transport-xmpp"].keys():
                    return parsed_conf_file["transport-xmpp"]["xmpp-server"]
            elif conf_name == "xmpp-port":
                if "xmpp-port" in parsed_conf_file["transport-xmpp"].keys():
                    return parsed_conf_file["transport-xmpp"]["xmpp-port"]
            elif conf_name == "xmpp-jid":
                if "xmpp-jid" in parsed_conf_file["transport-xmpp"].keys():
                    return parsed_conf_file["transport-xmpp"]["xmpp-jid"]
            elif conf_name == "xmpp-password":
                if "xmpp-password" in parsed_conf_file["transport-xmpp"].keys():
                    return parsed_conf_file["transport-xmpp"]["xmpp-password"]
    return None

def set_configuration_value(argument_value, parsed_conf_value, default_value):
    """
    Returns the value to be affected to a configuration property.
    """
    if argument_value:
        return argument_value
    elif parsed_conf_value is not None:
        return parsed_conf_value
    else:
        return default_value    

def main(args=None):
    """
    main script
    """
    if not args:
        args = sys.argv[1:]

    # Test if the COHORTE_HOME environment variable is set. If not exit
    COHORTE_HOME = os.environ.get('COHORTE_HOME')
    if not COHORTE_HOME:
        print("[ERROR] environment variable COHORTE_HOME not set")
        return 1
    else:
        print("[INFO] COHORTE_HOME: " + COHORTE_HOME)

    # Define arguments
    parser = argparse.ArgumentParser(description="Starting a COHORTE Node")

    
    group = parser.add_argument_group("Mandatory arguments")
    
    group.add_argument("-a","--app-id", action="store", 
                       dest="application_id", help="Application's ID")

    group = parser.add_argument_group("Config",
                                      "Startup configuration options")
    
    group.add_argument("--use-config", action="store", default="run.js",
                        dest="config_file", help="Configuration file to use for starting cohorte node. By default the run.js file is used if available")
    
    group.add_argument("--update-config", action="store_true", default=False,
                        dest="update_config_file", help="Update startup configuration file with provided options")
    
    group.add_argument("--show-config", action="store_true", default=False,
                        dest="show_config_file", help="Show startup configuration file content")
    
    group.add_argument("-b", "--base", action="store", default=None,
                       dest="base_absolute_path", help="absolute file path of the node's directory")
    
    group = parser.add_argument_group("Node",
                                      "Information about the node to start")

    group.add_argument("-n", "--node", action="store",
                       dest="node_name", help="Node name")

    group.add_argument("--top-composer", action="store_true",
                       dest="is_top_composer", help="Flag indicating that this node is a Top Composer")
    
    group.add_argument("--web-admin", action="store", type=int,
                       dest="web_admin_port", help="Node web admin port")
    
    group.add_argument("--shell-admin", action="store", type=int,
                       dest="shell_admin_port", help="Node remote shell port")
    
    group = parser.add_argument_group("Transport",
                                      "Information about the transport protocols to use")

    group.add_argument("--transport", action="store",
                       dest="transport_modes", help="Transport mode (http and/or xmpp - seperated by comma)")
    
    group.add_argument("--xmpp-server", action="store",
                       dest="xmpp_server", help="XMPP server")
    
    group.add_argument("--xmpp-port", action="store", type=int,
                       dest="xmpp_port", help="XMPP server port")
    
    group.add_argument("--xmpp-jid", action="store",
                       dest="xmpp_jid", help="XMPP jid")
    
    group.add_argument("--xmpp-password", action="store",
                       dest="xmpp_password", help="XMPP Room")

    
    # Parse arguments
    args, boot_args = parser.parse_known_args(args)
    COHORTE_BASE = args.base_absolute_path
    NODE_NAME = "node"
    TRANSPORT_MODES = []
    WEB_ADMIN_PORT = 0
    SHELL_ADMIN_PORT = 0   
    IS_TOP_COMPOSER = None
    APPLICATION_ID = None

    if args.show_config_file == True:
        # show the content of the startup configuration file and exit.
        content = parse_config_file(args.config_file)
        if content:
            content = json.dumps(content, sort_keys=False,
                                indent=4, separators=(',', ': '))
            print(content)
        else:
            print("[INFO] there is no startup configuration file! Use '--config' option to refer to your config file")
        return 0


    # Check if the user has provided the --base option (Node's full path)    
    if not COHORTE_BASE:
        print("[ERROR] the absolute path to the node's directory to execute is required. use --base option")
        return 1
    else:
        os.environ["COHORTE_BASE"] = COHORTE_BASE
        print("[INFO] COHORTE_BASE: " + os.environ['COHORTE_BASE'])

    # export python path
    added_paths = [value
                   for value in (os.environ.get('PYTHONPATH'),
                                 os.path.join(args.base_absolute_path, 'repo'),
                                 os.path.join(COHORTE_HOME, 'repo'))
                   if value is not None]
    os.environ['PYTHONPATH'] = os.pathsep.join(added_paths)

    # Change our path
    sys.path = added_paths + sys.path
    print("[INFO] PYTHONPATH:", os.environ['PYTHONPATH'])

    external_config = None
    # Parse config file
    if args.config_file:                
        external_config = parse_config_file(args.config_file)
        if external_config:
            print('[INFO] using startup configuration provided in "'+args.config_file+'" file')
    
    # export Node name 
    NODE_NAME = set_configuration_value(args.node_name, get_external_config(external_config, "node-name"), 
                                        os.path.basename(os.path.normpath(COHORTE_BASE)))    
    os.environ['COHORTE_NODE_NAME'] = NODE_NAME
    print("[INFO] COHORTE_NODE_NAME: " + os.environ.get('COHORTE_NODE_NAME'))

    # export Cohorte Root
    os.environ['COHORTE_ROOT'] = os.environ.get('COHORTE_HOME')
    print("[INFO] COHORTE_ROOT: " + os.environ.get('COHORTE_ROOT'))

    # configure application id
    APPLICATION_ID = set_configuration_value(args.application_id, get_external_config(external_config, "application-id"), 
                                        None) 
    if not APPLICATION_ID:
        print("[ERROR] no application ID is given!")
        print("        You should provide a correct application ID managed by a COHORTE Top Composer!")
        print("        use '--app' option to provide the application's ID or update your startup configuration file.")
        return 1
    else:
        common.generate_boot_common(COHORTE_BASE, APPLICATION_ID)

    # Node log file
    LOG_DIR = os.path.join(COHORTE_BASE, 'var')
    os.environ['COHORTE_LOGFILE'] = os.path.join(LOG_DIR, 'forker.log')
    print("[INFO] COHORTE_LOGFILE: " + os.environ.get('COHORTE_LOGFILE'))

    WEB_ADMIN_PORT = set_configuration_value(args.web_admin_port, 
                                            get_external_config(external_config, "web-admin"),
                                            0)
    SHELL_ADMIN_PORT = set_configuration_value(args.shell_admin_port, 
                                            get_external_config(external_config, "shell-admin"),
                                            0)
    # Generate webadmin and shell configs of the cohorte (main) isolate of this node
    common.generate_boot_forker(COHORTE_BASE, WEB_ADMIN_PORT, SHELL_ADMIN_PORT)
    print("[INFO] starting node '" + NODE_NAME + "' [web-admin port '"
            +str(WEB_ADMIN_PORT)+"' | shell-admin port '"+str(SHELL_ADMIN_PORT)+"']");

    # Log
    try:
        shutil.rmtree(os.path.join(COHORTE_BASE, 'var'))
    except:
        pass
    if not os.path.exists(os.path.join(COHORTE_BASE, 'var')):
        os.makedirs(os.path.join(COHORTE_BASE, 'var'))

    # transport mode   
    process = None
    xmpp_log_file = None
 
    tmodes = None
    if args.transport_modes:
        tmodes = args.transport_modes.split(",")                    
    TRANSPORT_MODES = set_configuration_value(tmodes, 
                                            get_external_config(external_config, "transport"),
                                            ["http"])

    print("[INFO] using transport modes: "+",".join(TRANSPORT_MODES))
    
    if "xmpp" in TRANSPORT_MODES:
        XMPP_SERVER = set_configuration_value(args.xmpp_server, get_external_config(external_config, "xmpp-server"), "")
        XMPP_PORT = set_configuration_value(args.xmpp_port, get_external_config(external_config, "xmpp-port"), 5222)
        XMPP_JID = set_configuration_value(args.xmpp_jid, get_external_config(external_config, "xmpp-jid"), "")
        XMPP_PASS = set_configuration_value(args.xmpp_password, get_external_config(external_config, "xmpp-password"), "")

        print("[INFO] connecting into the XMPP server with the following configuration...")
        print("""
            - xmpp server: {server}
            - xmpp port: {port}
            - xmpp jid: {jid}
            - xmpp password: *
            - xmpp room name: {room_name}
            - xmpp room jid: {room_jid}
            - xmpp key: {key}
            """.format(server=XMPP_SERVER, port=XMPP_PORT, jid=XMPP_JID, room_name="cohorte", 
                room_jid="cohorte@conference."+XMPP_SERVER, key="42"))
        SUCCESSED_RENDEZ_VOUS = "Bite my shiny, metal a**!"
        FAILED_RENDZ_VOUS = "I'm so embarrassed right now. (XMPP connect failed)"
        xmpp_log_file = open(os.path.join(LOG_DIR, 'xmpp_bot.log'), "w")        
        # start en XMPP mode
        from subprocess import Popen, PIPE, STDOUT 
        # 1) start bot
        process = Popen(["python3", "-u", "-m","herald.transports.xmpp.monitor",
            "--jid", XMPP_JID, 
            "--password", XMPP_PASS,
            "-r", "cohorte",
            "-p", str(XMPP_PORT),
            "-s", XMPP_SERVER], stdout=PIPE, stderr=xmpp_log_file, bufsize=1)          
        from pelix.utilities import to_str, to_bytes
        try:
            for line in iter(process.stdout.readline, to_bytes('')):
                #print(line)
                line = to_str(line)
                if SUCCESSED_RENDEZ_VOUS in line:
                    print("[INFO] COHORTE is correctly connected to the XMPP server.")
                    break  
                if FAILED_RENDZ_VOUS in line:
                    print("[ERROR] can not connect to the XMPP server. Check 'var/xmpp_bot.log' file for more information")   
                    raise IOError("Error connecting XMPP bot") 
        except (IOError,KeyboardInterrupt) as e:
            if process:
                process.terminate()
                if not xmpp_log_file:
                    xmpp_log_file.close()
            return 1    

        # 2) create conf/herald configs for node
        room_jid = "cohorte@conference."+XMPP_SERVER
        common.generate_herald_xmpp_conf(COHORTE_BASE, XMPP_SERVER, XMPP_PORT, XMPP_JID, room_jid, "42")
        # all-xmpp.js
        # 
    else:
        # remove 'conf/herald' folder
        try:
            shutil.rmtree(os.path.join(COHORTE_BASE, 'conf', 'herald'))
        except:
            pass

    # Starting Cohorte
    import subprocess
    print("[INFO] ************* STARTING COHORTE ****************")
    #print("[INFO] boot_args: " , boot_args) 
    if "-t" not in boot_args:
        IS_TOP_COMPOSER = set_configuration_value(args.is_top_composer, 
                                                get_external_config(external_config, "top-composer"),
                                                False)
        if IS_TOP_COMPOSER == True:
            boot_args.append("-t")        
    else:
        IS_TOP_COMPOSER = True

    if IS_TOP_COMPOSER == True:
        print("[INFO] starting as TOP COMPOSER!")
    else:
        print("[INFO] starting as a simple node!")
    
    # update configuration if not exists
    if args.update_config_file:
        if args.update_config_file == True:
            CONFIG_FILE = args.config_file
            configuration = {}
            configuration["application-id"] = APPLICATION_ID
            configuration["node"] = {}
            configuration["node"]["name"] = NODE_NAME
            configuration["node"]["top-composer"] = IS_TOP_COMPOSER
            configuration["node"]["web-admin"] = WEB_ADMIN_PORT
            configuration["node"]["shell-admin"] = SHELL_ADMIN_PORT
            configuration["transport"] = TRANSPORT_MODES
            if "xmpp" in TRANSPORT_MODES:
                configuration["transport-xmpp"] = {}
                configuration["transport-xmpp"]["xmpp-server"] = XMPP_SERVER
                configuration["transport-xmpp"]["xmpp-port"] = XMPP_PORT
                configuration["transport-xmpp"]["xmpp-jid"] = XMPP_JID
                configuration["transport-xmpp"]["xmpp-password"] = XMPP_PASS
            common.update_startup_file(CONFIG_FILE, configuration)
            

    # starting cohorte isolate
    status = subprocess.call("python3" + " -m cohorte.boot.boot " + " ".join(boot_args), shell=True)
    
    #xmpp_log_file.flush()
    # terminate XMPP bot if stoped
    if process:
        process.terminate()
        if not xmpp_log_file:
            xmpp_log_file.close()
    return 0
    #import cohorte.boot.boot
   
    #return cohorte.boot.boot.main(boot_args)

if __name__ == "__main__":
    sys.exit(main())