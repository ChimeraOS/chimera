#! /bin/bash

# All whitespace below is required for correct parsing in protondb
echo "
System Info:


Processor Information:
    CPU: $(cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d':' -f2)
 

Operating System Version:
    OS: $(lsb_release -d | cut -d':' -f2) $(lsb_release -r | cut -d':' -f2 | tr -d '\t')
    Kernel Name: Linux
    Kernel Version: $(uname -r)
 

Video Card:
    GPU: $(lspci | grep VGA | cut -d'[' -f2 | cut -d']' -f1)
    Driver Version: $(glxinfo | grep 'OpenGL version string' | cut -d':' -f2 | cut -d')' -f2)
 
 
 
 



Memory:
    RAM: $(expr `grep MemTotal /proc/meminfo | tr -s ' ' | cut -d' ' -f2` / 1024) Mb
"
