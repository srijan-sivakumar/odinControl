# odinControl
A remote command executor

## Why do we need a remote command executor
Well it's an age old requirement. You have X servers and you want to configure them
all without actually going over to each of those servers and doing the operation 
again and again.

One could leverage BASH for doing the same ?
Well technically you can. Create a bash script, then leverage the use of ssh to
remotely execute that BASH script across the servers. ( Actually sounds like a 
challenge, maybe one should take a look into it..). But then comes the 
question of user friendliness.

Is odinControl user friendly?
You tell me. If it isn't, maybe the best way is to either open a BUG or request 
some new feature.

## Usage
One can create an object of Rexe,

`
rc_handle = Rexe(<path_of_conf_file>, <exec_file_path>) # <exec_file_path> is optional
`

Once the object has been created, connection has to be established to the remote servers
before any operation is undertaken.

`
rc_handle.establish_connection()
`

To execute any command, one can either use the function `execute_command` or `execute_command_multinode`
The difference being `execute_command` only executes a given command in one node while the latter does
it in a given list of nodes.

To obtain the list of nodes which were parsed from the config file, one could use the instance variable
`conf_data['host_list']`

For example if somebody had to execute a command `ls /home` on the first node in the given list of hosts,

`ret = rc_handle.execute_command(rc_handle.conf_data['host_list'][1], 'ls /home')`

Now the return value will be of the following format,

{
  'Flag' : True/False,
  'node' : "the node for which the command was run",
  'cmd' : "the command which was requested",
  'error_code' : BASH error code in integer
  'msg' : "The return value in form of dictionary for glusterfs commands or string for other commands"
}

In case of multinode command execution, the result will be a list of result dictionaries of all the nodes
so if we have `ret`', `ret2`, `ret3` then the return value of `execute_command_multinode` will be
[ret1, ret2, ret3]
