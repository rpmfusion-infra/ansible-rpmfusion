#!/usr/bin/env python
 
import sys

fedorasecondary = [ 'rawhide', '26', '27']
fedorasecondaryarches = [ 'i386', 'ppc64', 'aarch64' ]

def modify_url(line):
    list = line.split(' ')
    # first element of the list is the URL
    old_url = list[0]
    new_url = '\n'
    # take the decision and modify the url if needed
    # do remember that the new_url should contain a '\n' at the end.
    if 'dl.fedoraproject.org' in old_url:
        #if 'rawhide' or '/26/' or '/27/' in old_url:
        if '/fedora/' in old_url:
            if '/i386/' in old_url:
                new_url = old_url.replace('/fedora/linux/', '/fedora-secondary/') + '\n'
                return new_url

            elif '/ppc64' in old_url:
                new_url = old_url.replace('/fedora/linux/', '/fedora-secondary/') + '\n'
                return new_url

            if '/27/' in old_url or '/26/' in old_url :
                if '/aarch64/' in old_url:
                    new_url = old_url.replace('/fedora/linux/', '/fedora-secondary/') + '\n'
                return new_url

        if '/epel/7/' in old_url:
            if '/i386/' in old_url:
                new_url = old_url.replace('/i386/', '/x86_64/') + '\n'
                return new_url

        return new_url

    #altarch support for centos
    if 'mirror.centos.org' in old_url:
        if '/centos/6/' not in old_url:
            if '/x86_64/' not in old_url:
                new_url = old_url.replace('/centos/', '/altarch/') + '\n'
                return new_url

    return new_url
 
while True:
    # the format of the line read from stdin is
    # URL ip-address/fqdn ident method
    # for example
    # http://saini.co.in 172.17.8.175/saini.co.in - GET -
    line = sys.stdin.readline().strip()
    # new_url is a simple URL only
    # for example
    # http://fedora.co.in
    new_url = modify_url(line)
    sys.stdout.write(new_url)
    sys.stdout.flush()
