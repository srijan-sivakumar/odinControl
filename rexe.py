from os import path
import concurrent.futures
import argparse
import logging
import logging.handlers
import paramiko
import yaml


logger = logging.getLogger(__name__)

def set_logging_options(log_file_path, log_file_level):
    """
    This function is for configuring the logger
    """
    global logger
    valid_log_level = ['I', 'D', 'W', 'E', 'C']
    log_level_dict = {'I':logging.INFO, 'D':logging.DEBUG, 'W':logging.WARNING,
            'E':logging.ERROR, 'C':logging.CRITICAL}
    log_format = logging.Formatter("[%(asctime)s] %(levelname)s "
                                   "[%(module)s - %(lineno)s:%(funcName)s] "
                                   "- %(message)s")
    if log_file_level not in valid_log_level:
        print("Invalid log level given, Taking Log Level as Info.")
        log_file_level = 'I'
    logger.setLevel(log_level_dict[log_file_level])
    log_file_handler = logging.handlers.WatchedFileHandler(log_file_path)
    log_file_handler.setFormatter(log_format)
    logger.addHandler(log_file_handler)

def is_file_accessible(path, mode='rw+'):
    """
    Check if the file or directory at `path` can
    be accessed by the program using `mode` open flags.
    """
    try:
        f = open(path, mode)
        f.close()
    except IOError:
        return False
    return True

class Rexe:
    def __init__(self, conf_path, command_file_path=""):
        self.host_generic = ['alls', 'allp']
        self.conf_path = conf_path
        self.command_file_path = command_file_path
        self.parse_conf_file()
        if command_file_path != "":
            self.parse_exec_file()
        logger.debug(f"Conf file data : {self.conf_data}")

    def parse_conf_file(self):
        """
        Function to parse the config file to get
        the host details, host username and host password.
        """
        self.conf_file_handle = open(self.conf_path)
        self.conf_data = yaml.load(self.conf_file_handle, Loader=yaml.FullLoader)
        self.conf_file_handle.close()
        self.host_list = self.conf_data['host_list']
        self.host_user = self.conf_data['user']
        self.host_passwd = self.conf_data['passwd']

    def parse_exec_file(self):
        """
        Function to parse the exec file
        """
        logger.debug("Parsing exec file")
        self.exec_file_handle = open(self.command_file_path)
        self.exec_data = yaml.load(self.exec_file_handle, Loader=yaml.FullLoader)
        self.conf_file_handle.close()
        logger.debug(f"Exec file data : {self.exec_data}")

    def establish_connection(self):
        """
        Function to establish connection with the given
        set of hosts.
        """
        logger.debug("establish connection")
        self.node_dict = {}
        self.connect_flag = True
        
        for node in self.host_list:
            node_ssh_client = paramiko.SSHClient()
            node_ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                node_ssh_client.connect(hostname=node, username=self.host_user, password=self.host_passwd)
                logger.debug(f"SSH connection to {node} is successful.")
            except paramiko.ssh_exception.AuthenticationException:
                logger.error("Authentication failure. Please check conf.")
                self.connect_flag = False
            self.node_dict[node] = node_ssh_client

    def execute_command(self, node, cmd):
        """
        Function to execute command in the given node.
        """
        ret_dict = {}
        if not self.connect_flag:
            ret_dict['Flag'] = False
            return ret_dict
        stdin, stdout, stderr = self.node_dict[node].exec_command(cmd)
        if stderr.readlines() != []:
            logger.error(stderr.readlines())
        ret_dict['node'] = node
        ret_dict['cmd'] = cmd
        ret_dict['Flag'] = True
        ret_dict['msg'] = stdout.readlines()
        logger.debug(ret_dict)
        return ret_dict

    def execute_command_multinode(self, node_list, cmd):
        """
        Function to execute command in multiple nodes
        parallely.
        """
        ret_val = []
        with concurrent.futures.ThreadPoolExecutor(max_workers = len(node_list)) as executor:
            future_exec = {executor.submit(self.execute_command, node, cmd): node for node in node_list}
            for future_handle in concurrent.futures.as_completed(future_exec):
                try:
                    ret_val.append(future_handle.result())
                except Exception as exc:
                    print(f"Generated exception : {exc}")
        logger.info(ret_val)
        return ret_val

    def execute_command_file(self):
        """
        Function to execute the commands provided in the
        command file.
        """
        if self.command_file_path == "":
            return -1
        for command_node in self.exec_data:
            if command_node not in self.host_list and command_node not in self.host_generic:
                logger.info(f"The command node {command_node} is not in host list.")
                continue
            commands_list = self.exec_data[command_node]
            if command_node == 'allp':
                # This is for parallel execution of commands in all nodes.
                for command in commands_list:
                    self.execute_command_multinode(self.host_list, command)
            elif command_node == 'alls':
                # Sequential execution of commands in all nodes.
                for command in commands_list:
                    for node in self.host_list:
                        self.execute_command(node, command)
            else:
                for command in commands_list:
                    self.execute_command(node, command)

if __name__ == "__main__":
    exit_flag = False

    # Configuring Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf_path', dest='conf_path', help="Configuration file path",
                        default="/home/rexe_conf.ini", type=str)
    parser.add_argument('-e', '--exec_fpath', dest='exec_fpath', help="Execution instructions file path",
                        default="", type=str, required=False)
    parser.add_argument('-l', '--log_path', dest='log_path', help="Logfile path",
                        default="/tmp/rexe.log", type=str)
    parser.add_argument('-ll', '--log_level', dest='log_level', help="Log Level",
                        default="I", type=str)
    args = parser.parse_args()

    # Set logger options
    set_logging_options(args.log_path, args.log_level)
    logger.info("REXE Initiated")

    # Validate the conf and command_exec file path.
    if not is_file_accessible(args.conf_path, 'r'):
        print(f"Configuration file doesn't exist at {args.conf_path}")
        logger.debug(f"Configuration file not accessible at {args.conf_path}")
        exit_flag = True
    if args.exec_fpath != "" and not is_file_accessible(args.exec_fpath, 'r'):
        print(f"Command execution file doesn't exist at {args.exec_fpath}")
        logger.debug(f"Command execution file not accessible at {args.exec_fpath}")
        exit_flag = True
    if not exit_flag:
        # Create an object of rexe class.
        remote_executor = Rexe(args.conf_path, args.exec_fpath)

        # Establish connection.
        remote_executor.establish_connection()

        # Execute the commands.
        remote_executor.execute_command_file()
