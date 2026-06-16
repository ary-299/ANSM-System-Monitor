import psutil
import os
import colorama
import time
from colorama import Fore, Back, Style, init
import yaml
import display
import safety

# Load configuration from YAML file cleanly
with open('cfg.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Grabbing the inner 'thresholds' box from the YAML data structure
thresholds = config.get('thresholds', {})

# Pulling out the individual threshold numbers from that inner box
cpu_warn = thresholds.get('cpu_warn_tresh', 80)
cpu_crit = thresholds.get('cpu_crit_tresh', 95)
ram_warn = thresholds.get('ram_warn_tresh', 80)
ram_crit = thresholds.get('ram_crit_tresh', 95)

# Grabbing the inner 'settings' box so we can dynamic control loop sleep timers
settings = config.get('settings', {})
interval = settings.get('check_interval_seconds', 5)

os.system('cls' if os.name == 'nt' else 'clear')

while True:
    cpu = psutil.cpu_percent()                  
    ram = psutil.virtual_memory().percent # getting ram percentage and setting it as the "ram" variable
    
    os.system('cls' if os.name == 'nt' else 'clear')
    display.show_header() 
    display.print_cpu(cpu)      # taking the cpu tracking number and sending it over to display.py
    display.print_ram(ram)      # same as above but with the live ram intake data
    display.show_footer() 
    
    # passing the live system numbers AND the limits directly into safety.py so it can process them instantly
    safety.check_treshhold(cpu, ram, cpu_warn, cpu_crit, ram_warn, ram_crit)

    time.sleep(interval)        # dynamic sleep command that uses the actual check_interval_seconds value from your YAML file