# Testing odinControl:
1. In conf.yaml file add the Host addresses of the remote machines you wish to connect.
2. In execfile.yaml, put the host addresses as keys and commands as values.
3. To run exec the following command:
`python3 rexe.py -l <location to log file>(ex:./test.log) -ll <log level>(ex:D) -c example/conf.yaml -e example/execfile.yaml`
