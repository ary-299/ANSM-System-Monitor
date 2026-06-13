import psutil
import os
import colorama
import time
from colorama import Fore, Back, Style, init
import display
import safety

os.system('cls' if os.name == 'nt' else 'clear')

while True:
    cpu=psutil.cpu_percent(interval=1)                      #getting cpu precentage with an interval of 1 second and setting it as the "cpu" variable
    ram=psutil.virtual_memory().percent                     #same as in line 12, just replace "cpu" with "ram"
    os.system('cls' if os.name == 'nt' else 'clear')
    display.show_header() 
    display.print_cpu(cpu)                                   # taking the cpu temprature and sending it to display.py
    display.print_ram(ram)                                   #same as above but with the ram intake
    display.show_footer() 
    safety.check_treshhold

    continue
