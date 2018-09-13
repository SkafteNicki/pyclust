#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 11:58:56 2018

@author: nsde
"""

#%%
import paramiko

#%%
def my_usage(ssh):
    try:
        counter = 0
        for i in range(1, 13):
            print(47*"=" + "titan{0:02d}".format(i) + 47*"=")
    
            # Connect to host
            ssh.connect("titan{0:02d}".format(i))
        
            # Commands to run
            comm = ['top -c -n 1 |grep nsde']
            comm = ';'.join(comm)

            # Execute commands        
            stdin, stdout, stderr = ssh.exec_command(comm, get_pty=True)
            
            # Print output
            output = stdout.read().decode("utf-8")
            output = output.split('\n')
            for line in output:
                if 'top' not in line and len(line)>1:
                    print(line)
                    counter += 1
        print('You are using ' + str(counter) + ' GPUs')
    finally:
        ssh.close()
        
#%%
if __name__ == '__main__':
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    my_usage(ssh)
    

