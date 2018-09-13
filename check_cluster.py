#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 14:42:44 2018

@author: nsde
"""

#%%
import paramiko

#%%
def check_cluster(ssh, verbose=True):
    try:
        found = False
        count_all = count_filt = 0
        cluster, gpu = None, None
        for i in range(1, 13):
            if verbose:
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
            
            for j, line in enumerate(output):
                count_all += 1
                in_use = int(line.split(':')[-1].split('of')[0])
                if in_use < 20:
                    if verbose:
                        print(line)
                    count_filt += 1
                    found = True
                    if not verbose and found:
                        cluster = i
                        gpu = j
                        break
                    
            if not verbose and found:
                break
                    
        if count_all != count_filt:
            if verbose:
                print(101*"=")
                print(str(count_filt) + ' availble GPUs out of ' + str(count_all))            
    finally:
        ssh.close()        

    return cluster, gpu

#%%
def main():
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    _, _ = check_cluster(ssh, verbose=True)

#%%
if __name__ == '__main__':
    main()