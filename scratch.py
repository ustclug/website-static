#!/usr/bin/python3

'''
Download resources needed, change origin url, sync the static repo(if needed).
Make sure you are in dir for storage.
'''

from os import path
import os
import sys
import codecs
from urllib import request
import re
import json

local_static_repo_dir = '/root/lugustc/website-static'

save_dir = ''
converted = []


def download(url):
    saved_file = path.join(save_dir, url.split('/')[-1])
    if path.exists(saved_file): # resist repetition
        with open(saved_file, 'rb') as f:
            hash_value = hash(f.read())
            if hash_value == hash(request.urlopen(url).read()):
                return path.relpath(saved_file, local_static_repo_dir)
        path.join(save_dir, hash_value + '.' + saved_file.split('.')[-1])
    try:
        with open(saved_file, 'wb') as f:
            f.write(request.urlopen(url).read())
    except:
        print(f'{saved_file} fail to save.')
        return None
    return path.relpath(saved_file, local_static_repo_dir)

def main(dir_file):
    if path.isdir(dir_file):
        files = [i if i[-3:] == '.md' else None for i in os.listdir(dir_file)]
    else:
        files = [dir_file]
        dir_file = ''
    for file in files:
        if file:
            file_content = ''
            with codecs.open(path.join(dir_file, file), 'r', encoding='utf-8') as f:
                for line in f:
                    if (match := re.findall(r'\!\[.*?\]\((.*?)\)', line)):
                        new_url = 'https://static.beta.ustclug.org/'+ download(match[0])
                        file_content += re.sub(r'\!\[(.*?)\]\(.*?\)', '![\1]('+new_url+')', line)
                    else:
                        file_content += line
            with codecs.open(path.join(dir_file, file), 'w', encoding='utf-8') as f:
                f.write(file_content)
    global converted
    converted += files

def help(exit_code):
    print('./scratch.py [source file|source dir] [static repo dir]')
    exit(exit_code)

if __name__ == "__main__":
    if '-h' in sys.argv or '--help' in sys.argv:
        help(0)
    for i in sys.argv[1:]:
        if not path.isdir(i) and not path.isfile(i):
            help(1)
    if len(sys.argv) == 3:
        save_dir = sys.argv[2]
    elif len(sys.argv) < 2 or len(sys.argv) > 3:
        help(1)
    
    try:
        with open(path.join(save_dir, '_converted.json'), 'r') as f:
            converted = json.load(f)
    except FileNotFoundError:
        pass

    main(sys.argv[1])

    with open(path.join(save_dir, '_converted.json'), 'w') as f:
        json.dump(converted, f)
    
        