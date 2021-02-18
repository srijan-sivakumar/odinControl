from os import path
import argparse
import logging
import paramiko
import yaml


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
        self.conf_path = conf_path
        self.command_file_path = command_file_path
        self.parse_conf_file()
        print(self.conf_data)

    def logger_init(self):
        

    def parse_conf_file(self):
        """
        Function to parse the config file to get
        host details, host username and password.
        """
        self.conf_file_handle = open(self.conf_path)
        self.conf_data = yaml.load(self.conf_file_handle, Loader=yaml.FullLoader)
        self.conf_file_handle.close()
        self.host_list = self.conf_data['host_list']
        self.host_user = self.conf_data['user']
        self.host_passwd = self.conf_data['passwd']

    def establish_connection(self):
        """
        Function to establish connection with the given
        set of hosts.
        """
        self.node_dict = {}
        self.connect_flag = True
        for node in self.host_list:
            node_ssh_client = paramiko.SSHClient()
            node_ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                node_ssh_client.connect(hostname=node, username=self.host_user, password=self.host_passwd)
            except paramiko.ssh_exception.AuthenticationException:
                print("Authentication failure. Please check conf.")
                self.connect_flag = False
            self.node_dict[node] = node_ssh_client

    def execute_command(self, node, cmd):
        """
        Function to execute command in the given node.
        """
        print("Run the given command.")

    def execute_command_file(self):
        """
        Function to execute the commands provided in the
        command file.
        """
        print("Run the whole script.")


#ssh_client = paramiko.SSHClient()
#ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#ssh_client.connect(hostname='10.70.41.184', username='root', password='redhat')

def exec_remote(cmd):
    result_dict_val = {}
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    if stderr.readlines() != []:
        print(stderr.readlines())
    else:
        result_xml_string = ""
        for line in stdout.readlines():
            result_xml_string += line
        result_dict_val = xmltodict.parse(result_xml_string)['cliOutput']
    return result_dict_val

if __name__ == "__main__":
    exit_flag = False

    # Configuring Parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf_path', dest='conf_path', help="Configuration file path",
                        default="/home/rexe_conf.ini", type=str)
    parser.add_argument('-e', '--exec_fpath', dest='exec_fpath', help="Execution instructions file path",
                        default="/home/rexe_exec", type=str)
    parser.add_argument('-l', '--log_path', dest='log_path', help="Logfile path",
                        default="/tmp/rexe.log", type=str)
    parser.add_argument('-ll', '--log_level', dest='log_level', help="Log Level",
                        default="I", type=str)
    args = parser.parse_args()

    # Set logger options
    logger = logging.getLogger('root')
    format_val = '[%(asctime)s:%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s()]-5(message)s'

    # Validate the conf and command_exec file path.
    if not is_file_accessible(args.conf_path, 'r'):
        print(f"Configuration file doesn't exist at {args.conf_path}")
        exit_flag = True
    if not is_file_accessible(args.exec_fpath, 'r'):
        print(f"Command execution file doesn't exist at {args.exec_fpath}")
        exit_flag = True
    if not exit_flag:
        # Create an object of rexe class.
        remote_executor = Rexe(args.conf_path, args.exec_fpath)

        # Establish connection.
        remote_executor.establish_connection()

        # Execute the commands.
        remote_executor.execute_command_file()
