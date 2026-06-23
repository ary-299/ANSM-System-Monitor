
from colorama import Fore, Back, Style, init
import yaml

config_path = "cfg.YAML"
with open(config_path, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

thresholds = cfg.get("thresholds", {})

cpu_warn_tresh = int(thresholds.get("cpu_warn_tresh", 80))
ram_warn_tresh = int(thresholds.get("ram_warn_tresh", 80)) 
cpu_crit_tresh = int(thresholds.get("cpu_crit_tresh", 95))
ram_crit_tresh = int(thresholds.get("ram_crit_tresh", 95))
disk_warn_tresh = int(thresholds.get("disk_warn_tresh", 85))
disk_crit_tresh = int(thresholds.get("disk_crit_tresh", 95))
download_warn_tresh = int(thresholds.get("download_warn_tresh", 50))
download_crit_tresh = int(thresholds.get("download_crit_tresh", 90))
upload_warn_tresh = int(thresholds.get("upload_warn_tresh", 50))
upload_crit_tresh = int(thresholds.get("upload_crit_tresh", 90))

def show_header():
    print(Fore.RED+Style.BRIGHT+"ANSM "+Style.RESET_ALL+Style.BRIGHT+"Panel\n")

def print_cpu(cpu_val):         #setting "def" commands to run them on "main" later in the script
    if cpu_val< cpu_warn_tresh:
        print(Style.BRIGHT+"CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f" {cpu_val}% " + Style.RESET_ALL)   #prints green for good values
    elif cpu_val<cpu_warn_tresh and cpu_val<cpu_crit_tresh:
        print(Style.BRIGHT+"CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f" {cpu_val}% " + Style.RESET_ALL)  #prints yellow for okay values
    elif cpu_val<cpu_crit_tresh and cpu_val<cpu_warn_tresh:
        print(Style.BRIGHT +"CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {cpu_val}% " + Style.RESET_ALL)   #prints red for bad values
    elif cpu_val>=95:
        print(Style.BRIGHT +"CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {cpu_val}% ! ! !" + Style.RESET_ALL)  #prints red with three exl. marks for horrible values

def print_ram(ram_val):         #setting "def" commands to run them on "main" later in the script
    if ram_val<ram_warn_tresh:
        print(Style.BRIGHT +  "RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f" {ram_val}% " + Style.RESET_ALL) #check cpu values
    elif ram_val<ram_crit_tresh and ram_val<ram_warn_tresh:
        print(Style.BRIGHT+"RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f" {ram_val}% " + Style.RESET_ALL)
    elif ram_val<ram_crit_tresh:
        print(Style.BRIGHT +"RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {ram_val}% " + Style.RESET_ALL)
    elif ram_val>=95:
        print(Style.BRIGHT +"RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {ram_val}% ! ! !" + Style.RESET_ALL)

def print_download(wifi_recv):
    if wifi_recv<download_warn_tresh:
        print(Style.BRIGHT +  "Download Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f" {wifi_recv}GB " + Style.RESET_ALL) #check download values
    elif wifi_recv<download_warn_tresh and wifi_recv<download_crit_tresh:
        print(Style.BRIGHT+"Download Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f" {wifi_recv}GB " + Style.RESET_ALL)
    elif wifi_recv<download_crit_tresh:
        print(Style.BRIGHT +"Download Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {wifi_recv}GB" + Style.RESET_ALL)
    elif wifi_recv>=1:
        print(Style.BRIGHT +"Download Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {wifi_recv}GB ! ! !" + Style.RESET_ALL)

def print_upload(wifi_sent):
    if wifi_sent<download_warn_tresh:
        print(Style.BRIGHT +  "Upload Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f" {wifi_sent}GB " + Style.RESET_ALL) #check download values
    elif wifi_sent<upload_warn_tresh and wifi_sent<upload_crit_tresh:
        print(Style.BRIGHT+"Upload Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f" {wifi_sent}GB " + Style.RESET_ALL)
    elif wifi_sent<upload_crit_tresh:
        print(Style.BRIGHT +"Upload Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {wifi_sent}GB " + Style.RESET_ALL)
    elif wifi_sent>=1:
        print(Style.BRIGHT +"Upload Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {wifi_sent}GB ! ! !" + Style.RESET_ALL)
    

def print_disk(disk_prec):
    if disk_prec < disk_warn_tresh:
        print(Style.BRIGHT + "Disk usage:"+Style.RESET_ALL + Style.BRIGHT+ Fore.GREEN +f"{disk_prec}%" + Style.RESET_ALL)
    if disk_prec > disk_warn_tresh and disk_prec < disk_crit_tresh:
        print(Style.BRIGHT + "Disk usage:"+Style.RESET_ALL + Style.BRIGHT+ Fore.YELLOW +f"{disk_prec}%" + Style.RESET_ALL)
    if disk_prec > disk_crit_tresh and disk_prec > 97:
        print(Style.BRIGHT + "Disk usage:"+Style.RESET_ALL + Style.BRIGHT+ Fore.RED +f"{disk_prec}%" + Style.RESET_ALL)
    if disk_prec > 97:
        print(Style.BRIGHT + "Disk usage:"+Style.RESET_ALL + Style.BRIGHT+ Fore.RED +f"{disk_prec}%! ! !" + Style.RESET_ALL)
def show_footer():
    print("\nmade by ary")
