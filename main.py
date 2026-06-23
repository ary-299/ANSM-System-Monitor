import psutil
import os
import math
import colorama
import time
from colorama import Fore, Back, Style, init
import yaml
import display
import safety

with open('cfg.yaml', 'r') as f:                                            # Load configuration from YAML file cleanly
    config = yaml.safe_load(f)

thresholds = config.get('thresholds', {})  
interval = config["settings"]["check_interval_seconds"]                                 # Grabbing the inner "thresholds" box from the YAML data structure

cpu_warn = thresholds.get('cpu_warn_tresh', 80)                             # Pulling out the individual threshold numbers from that inner box
cpu_crit = thresholds.get('cpu_crit_tresh', 95)
ram_warn = thresholds.get('ram_warn_tresh', 80)
ram_crit = thresholds.get('ram_crit_tresh', 95)

settings = config.get('settings', {})                               # Grabbing the inner "settings" box so we can dynamic control loop sleep timers
interval = settings.get('check_interval_seconds', 5)

os.system('cls' if os.name == 'nt' else 'clear')
old_bytes_sent = psutil.net_io_counters().bytes_sent
old_bytes_recv = psutil.net_io_counters().bytes_recv
while True:
    cpu = psutil.cpu_percent()                  
    ram = psutil.virtual_memory().percent # getting ram percentage and setting it as the "ram" variable
    Cused = psutil.disk_usage("C://").used
    Ctotal = psutil.disk_usage("C://").total
    Cprec_unclean = psutil.disk_usage("C://").percent
    Cprec = round(Cprec_unclean, 1)
    Cfree = Ctotal - Cused

    Wifisent = psutil.net_io_counters().bytes_sent
    bytes_changed_sent = Wifisent - old_bytes_sent
    unclean_speed_sent = bytes_changed_sent / 1024/ interval
    speed_sent = round(unclean_speed_sent, 1)
    old_bytes_sent = Wifisent

    Wifirecv = psutil.net_io_counters().bytes_recv
    bytes_changed_recv = Wifirecv - old_bytes_recv
    unclean_speed_recv = bytes_changed_recv / 1024 / interval
    speed_recv = round(unclean_speed_recv, 1)
    old_bytes_recv = Wifirecv
    
    os.system('cls' if os.name == 'nt' else 'clear')
    display.show_header() 
    display.print_cpu(cpu)      # taking the cpu tracking number and sending it over to display.py
    display.print_ram(ram)      # same as above but with the live ram intake data
    display.print_download(speed_recv)
    display.print_upload(speed_sent)
    display.print_disk(Cprec)
    display.show_footer() 
    
    # passing the live system numbers AND the limits directly into safety.py so it can process them instantly
    safety.check_treshhold(cpu, ram, cpu_warn, cpu_crit, ram_warn, ram_crit)

    time.sleep(interval)        # dynamic sleep command that uses the actual check_interval_seconds value from your YAML file