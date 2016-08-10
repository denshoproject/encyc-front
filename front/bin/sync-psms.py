#!/usr/bin/env python
#
# This file is part of encyc-front
#

description = """sync-psms - Copies PSMS files from dango to tulie."""

epilog = """
This script uses rsync and scp to copy PSMS files from the editors' machine
running encyc-psms to an S3-style bucket on the public fileserver.

In the process the `source/I/ID/FILENAME.EXT` hierarchy of the PSMS files is
flattened to `encyc-psms/FILENAME.EXT`.

Rsync cannot copy files between two remote systems, so instead we scp from the
source to /tmp on the local system and then scp from /tmp to the destination.

Before copying, rsync is used to list files on both the source and destination.
The file lists are compared and only new or modified files are copied.

Source and destination USER@HOST:PATH are specified in /etc/encyc/production.cfg.

The user that runs this script must be able to access both source and destination
systems without entering passwords.  Run "ssh-keygen" and "ssh-copy-id" as the
script user to generate keys and set up passwordless SSH.

    root # su - encyc
    
    # Generate keys but DO NOT enter passwords!
    encyc $ ssh-keygen -t rsa -b 4096 -C "encyc@front"
    
    # copy keys to remote systems.
    encyc $ ssh-copy-id encyc@SOURCE
    encyc $ ssh-copy-id encyc@DESTINATION
    
    # test
    encyc $ ssh encyc@SOURCE
    encyc $ ssh encyc@DESTINATION

Add this to `/etc/crontab`:

    # encyc-front: get primary-source images from dango
    SHELL=/bin/bash
    */60 *  * * *   encyc   /usr/local/src/env/front/bin/python /usr/local/src/encyc-front/front/bin/sync-psms.py

"""

import argparse
import ConfigParser
from datetime import datetime
import os
import subprocess

# User-configurable settings are located in the following files.
# Files appearing *later* in the list override earlier files.
CONFIG_FILES = [
    '/etc/encyc/production.cfg',
    '/etc/encyc/local.cfg'
]

TMP_DIR = '/tmp/encyc-psms-sync'

RSYNC_CMD = [
    'rsync',
    '-a',
    '--list-only'
]
SCP_CMD = [
    'scp',
    '-p', # Preserves modification times, access times, and modes from the original file.
    #'-v', # Verbose mode.
]

def logprint(msg):
    if msg.strip():
        print('%s %s' % (datetime.now(), msg.strip()))

def check_tmpdir():
    """Make tmpdir if it doesn't exist
    """
    if not os.path.exists(TMP_DIR):
        logprint('mkdir %s' % TMP_DIR)
        os.makedirs(TMP_DIR)

def get_files_list(remote):
    """Get list of files from remote
    
    @param remote: str USER@HOST:PATH
    @returns: list RSYNC_CMD output split into lines.
    """
    cmd = RSYNC_CMD + [remote]
    logprint(' '.join(cmd))
    raw = subprocess.check_output(cmd)
    return raw.splitlines()

def separate_files_dirs(raw):
    """Separate lines into lists of files and dirs
    
    @param raw: list RSYNC_CMD output split into lines.
    @returns: files, dirs
    """
    files = []
    dirs = []
    for line in raw:
        info = parse_rsync_line(line)
        if info and (isinstance(info, dict)):
            files.append(info)
        elif info and (isinstance(info, basestring)):
            dirs.append(info)
    return files,dirs

def parse_rsync_line(line):
    """Parse output of RSYNC_CMD, return file info dict.
    
    >>> line = 'drwxr-xr-x        4096 2012/10/19 16:08:57 sources/1/1677'
    >>> parse_rsync_line(line)
    'sources/1/1677'
    
    >>> line = '-rwxr-xr-x     1234567 2015/03/26 10:21:27 sources/1/123/en-my-file-1_1.jpg'
    >>> parse_rsync_line(line)
    {'perms': '-rwxr-xr-x', 'basename': 'en-my-file-1_1.jpg', 'size': 1234567, 
    'modified': datetime.datetime(2015, 3, 26, 10, 21, 27), 'dirname': 'sources/1/123',
    'path': 'sources/1/123/en-my-file-1_1.jpg'}

    >>> line = 'lrwxrwxrwx          64 2015/01/15 16:45:05 sources/1/123/ddr-test-123-456.jpg -> /var/www/html/psms/media/sources/1/124/my-file-a1b2c3d4e5.jpg'
    >>> parse_rsync_line(line)
    >>> 
    
    @param line: str
    @returns: dict (file), str (directory), or None
    """
    parts = line.split()
    if not (len(parts) == 5):
        # wrong num of parts
        return None
    perms,size,date,time,path = line.split()
    if perms[0] == 'd':
        # directory
        return path
    elif perms[0] == '-':
        # file
        size = int(size.replace(',', ''))
        y,m,d = date.split('/')
        H,M,S = time.split(':')
        modified = datetime(int(y),int(m),int(d),int(H),int(M),int(S))
        parts = {
            'perms': perms,
            'size': size,
            'modified': modified,
            'path': path,
            'dirname': os.path.dirname(path),
            'basename': os.path.basename(path),
        }
        return parts
    return None

def print_stats(raw, dirs, files):
    num_lines = len(raw)
    num_dirs = len(dirs)
    num_files = len(files)
    logprint('%s lines (%s dirs, %s files)' % (num_lines, num_dirs, num_files))

def make_files_dict(files_list):
    """Given list of file info dicts, make a dict keyed to file basename.
    
    @param files_list: list of file dicts
    @returns: dict
    """
    fd = {
        f['basename']: f
        for f in files_list
    }
    return fd

def choose_files(src_files, dest_files):
    """Choose new/updated files.
    
    @param src_files: list of file info dicts
    @param dest_files: list of file info dicts
    @returns: list of file info dicts
    """
    chosen = []
    dest_keys = dest_files.keys()
    for key in src_files.keys():
        if (key in dest_keys):
            if (src_files[key]['modified'] > dest_files[key]['modified']):
                # file in both places, source is newer
                chosen.append(src_files[key])
        else:
            # file not in dest
            chosen.append(src_files[key])
    return chosen

def make_scp_cmds(chosen, src_user_host, src_path, dest_user_host, dest_dir):
    """Generate set of scp commands for each file.
    
    Rsync can't copy directly from SOURCE to DESTINATION so 
    - scp file to local /tmp,
    - scp to dest,
    - delete from /tmp.
    
    Example src_path: '/var/www/html/psms/media/sources'
    Example dest_path: '/var/www/media/encyc-psms'
    
    @param chosen: list Chosen file info dicts
    @param src_user_host: str USER@HOST
    @param src_path: str Source path, including dir containing source files.
    @param dest_user_host: str USER@HOST
    @param dest_dir: str Destination directory.
    @returns: list of commands for subprocess
    """
    src_dir = os.path.dirname(src_path)
    src_paths = [
        os.path.join(src_dir, src_file['path'])
        for src_file in chosen
    ]
    commands = []
    for spath in src_paths:
        tmp_path = os.path.join(TMP_DIR, os.path.basename(spath))
        dest_path = os.path.join(dest_dir, os.path.basename(spath))
        commands.append([
            SCP_CMD + ['%s:%s' % (src_user_host, spath), tmp_path],
            SCP_CMD + [tmp_path, '%s:%s' % (dest_user_host, dest_path)],
            ['rm', '-f', tmp_path],
        ])
    return commands

def copy_files(cmds, dryrun=False):
    outs = []
    for cmd in cmds:
        logprint(' '.join(cmd))
        if not dryrun:
            out = subprocess.check_output(cmd)
            outs.append(out)
            logprint(out)
    return outs


def main():

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    args = parser.parse_args()
    
    config = ConfigParser.ConfigParser()
    configs_read = config.read(CONFIG_FILES)
    if not configs_read:
        raise Exception('No config file!')
    
    # source
    src_remote = config.get('sources', 'src_remote')
    src_user_host,src_path = src_remote.split(':')
    src_raw = get_files_list(src_remote)
    src_files_list,src_dirs = separate_files_dirs(src_raw)
    print_stats(src_raw, src_dirs, src_files_list)
    src_files = make_files_dict(src_files_list)
    
    # destination
    dest_remote = config.get('sources', 'dest_remote')
    dest_user_host,dest_path = dest_remote.split(':')
    dest_raw = get_files_list(dest_remote)
    dest_files_list,dest_dirs = separate_files_dirs(dest_raw)
    print_stats(dest_raw, dest_dirs, dest_files_list)
    dest_files = make_files_dict(dest_files_list)
    
    # find new/changed files
    chosen = choose_files(src_files, dest_files)
    num_chosen = len(chosen)
    logprint('copying %s files' % num_chosen)
    
    scp_cmds = make_scp_cmds(chosen, src_user_host, src_path, dest_user_host, dest_path)

    # OK go!
    check_tmpdir()
    n = 0
    for cmds in scp_cmds:
        n = n + 1
        logprint('%s/%s' % (n, num_chosen))
        outs = copy_files(cmds)
    logprint('DONE')
    

if __name__ == '__main__':
    main()
