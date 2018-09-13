#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 10:27:49 2018

@author: nsde
"""

#%%
import paramiko
import argparse 
import select
import sys
from check_cluster import check_cluster

#%%
def argparser( ):
    parser = argparse.ArgumentParser(description='''Something''') 
    parser.add_argument('-c', action="store", dest='c', type=int, 
                        default=None, help='''Cluster to use''')
    parser.add_argument('-g', action="store", dest='g', type=int,
                        default=None, help='''gpu to use''')
    parser.add_argument('-d', action="store", dest='d', type=str,
                        default=None, help='''Directory to use''')
    parser.add_argument('-f', action="store", dest='f', type=str,
                        default=None, help='''File to run''')
    args = parser.parse_args() 
    args = vars(args) 
    return args

#%%
if __name__ == '__main__':  
    # Start connection to cluster                 
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    
    # Get input arguments
    args=argparser()
    cluster, gpu, directory, file = args['c'], args['g'], args['d'], args['f']
    if (cluster is None) or (gpu is None): # find the first and best gpu to run on
        cluster, gpu = check_cluster(ssh, verbose=False)
        print(70 * "=")
        print('Running commands on cluster ' + str(cluster) + " and gpu " + str(gpu))
        print(70 * "=")

    # Setup for cluster
    python_loc = "~/.conda/envs/tensorflow/bin/python "
    cuda_str = "CUDA_VISIBLE_DEVICES="
    setup_commands = ['export cuda=/usr/local/cuda-9.0',
                      'export cudnn=/usr/local/cuDNNv7.0-9',
                      'export PATH="$cuda/bin:$cuda/include:$cudnn/include:$PATH"',
                      'export LD_LIBRARY_PATH="$cuda/lib64:$cudnn/lib64:$PATH"']
    python_path = "PYTHONPATH=~/" + directory

    try:
        # Connect to host
        ssh.connect("titan{0:02d}".format(cluster))
        
        # Commands to run
        comm = [*setup_commands,
                'cd '+directory+'/',
                'pwd',
                'git pull',
                cuda_str + str(gpu) +' '+ python_path + ' ' + python_loc + file]
        comm = ';'.join(comm)
        
        # Execute commands        
        stdin, stdout, stderr = ssh.exec_command(comm)

        # get the shared channel for stdout/stderr/stdin
        channel = stdout.channel
        
        # we do not need stdin.
        stdin.close()
        
        # indicate that we're not going to write to that channel anymore
        channel.shutdown_write()      
        
        # read stdout/stderr in order to prevent read block hangs
        # chunked read to prevent stalls
        while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready(): 
            # stop if channel was closed prematurely, and there is no data in the buffers.
            got_chunk = False
            readq, _, _ = select.select([stdout.channel], [], [], 0.0)
            for c in readq:
                if c.recv_ready(): 
                    stdout_chunk=stdout.channel.recv(len(c.in_buffer)).decode("utf-8")
                    got_chunk = True
                    
                    # Print to screen
                    sys.stdout.write(stdout_chunk)
                    sys.stdout.flush()
                    
                if c.recv_stderr_ready(): 
                    # make sure to read stderr to prevent stall    
                    stdout_chunk=stderr.channel.recv_stderr(len(c.in_stderr_buffer))  
                    got_chunk = True  
                    
                    # Print to screen
                    sys.stdout.write(stdout_chunk.decode("utf-8"))
                    sys.stdout.flush()
                    
            if not got_chunk \
                and stdout.channel.exit_status_ready() \
                and not stderr.channel.recv_stderr_ready() \
                and not stdout.channel.recv_ready(): 
                # indicate that we're not going to read from this channel anymore
                stdout.channel.shutdown_read()  
                # close the channel
                stdout.channel.close()
                break    # exit as remote side is finished and our bufferes are empty
        
        # close all the pseudofiles
        stdout.close()
        stderr.close()
        
    finally: # close connection in the end
        ssh.close()
