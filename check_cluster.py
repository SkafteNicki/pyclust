#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 14:42:44 2018

@author: nsde
"""

#%%
import paramiko

#%%
if __name__ == '__main__':
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    
    try:
        count_all = count_filt = 0
        for i in range(1, 13):
            print(47*"=" + "titan{0:02d}".format(i) + 47*"=")
            
            # Connect to host
            ssh.connect("titan{0:02d}".format(i))
            
            # Commands to run
            comm = [' cuda-smi']
            comm = ';'.join(comm)
            
            # Execute commands        
            stdin, stdout, stderr = ssh.exec_command(comm, get_pty=True)
            
            # Print output
            output = stdout.read().decode("utf-8")
            output = output.split('\n')[:-1]
            
            for line in output:
                count_all += 1
                in_use = int(line.split(':')[-1].split('of')[0])
                if in_use < 20:
                    print(line)
                    count_filt += 1
        if count_all != count_filt:
            print(101*"=")
            print(str(count_filt) + ' availble GPUs out of ' + str(count_all))
            
    finally:
        ssh.close()