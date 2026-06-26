
from colorama import Fore, Back, Style, init
import yaml
import time
from rich.console import Console
console = Console()

config_path = "cfg.YAML"
with open(config_path, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

thresholds = cfg.get("thresholds", {})
settings = cfg.get("settings",{})

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

interval = int(settings.get("check_interval_seconds"))
iv_cw = interval / 15

def show_header():
    print(
        Fore.RED + Style.BRIGHT +
        r"""
 __   __ _  ____  _  _ 
/ _\ (  ( \/ ___)( \/ )
/    \/    /\___ \/ \/ \
\_/\_/\_)__)(____/\_)(_/
"""
        + Style.RESET_ALL + Style.BRIGHT +
        r"""
         ____   __   __ _  ____  __   
        (  _ \ / _\ (  ( \(  __)(  )  
         ) __//    \/    / ) _) / (_/\
        (__)  \_/\_/\_)__)(____)\____/
                    """
        + Style.RESET_ALL + "\n"
    )

def print_cpu(cpu_val):         #setting "def" commands to run them on "main" later in the script
    if cpu_val< cpu_warn_tresh:
        print(Style.BRIGHT+" CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f" {cpu_val}% \n" + Style.RESET_ALL)   #prints green for good values
    elif cpu_val>cpu_warn_tresh and cpu_val<cpu_crit_tresh:
        print(Style.BRIGHT+" CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f" {cpu_val}% \n" + Style.RESET_ALL)  #prints yellow for okay values
    elif cpu_val>cpu_crit_tresh and cpu_val>cpu_warn_tresh:
        print(Style.BRIGHT +" CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {cpu_val}% \n" + Style.RESET_ALL)   #prints red for bad values
    elif cpu_val>=95:
        print(Style.BRIGHT +" CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {cpu_val}% ! ! !\n" + Style.RESET_ALL)  #prints red with three exl. marks for horrible values

def print_ram(ram_val):         #setting "def" commands to run them on "main" later in the script
    if ram_val<ram_warn_tresh:
        print(Style.BRIGHT +  " RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f" {ram_val}% \n" + Style.RESET_ALL) #check cpu values
    elif ram_val>ram_crit_tresh and ram_val<ram_warn_tresh:
        print(Style.BRIGHT+" RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f" {ram_val}% \n" + Style.RESET_ALL)
    elif ram_val>ram_crit_tresh:
        print(Style.BRIGHT +" RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {ram_val}% \n" + Style.RESET_ALL)
    elif ram_val>=95:
        print(Style.BRIGHT +" RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {ram_val}% ! ! !\n" + Style.RESET_ALL)

def print_download(wifi_recv):
    if wifi_recv>download_warn_tresh:
        print(Style.BRIGHT +  " Download Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f" {wifi_recv}GB\n " + Style.RESET_ALL) #check download values
    elif wifi_recv>download_warn_tresh and wifi_recv>download_crit_tresh:
        print(Style.BRIGHT+" Download Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f" {wifi_recv}GB\n " + Style.RESET_ALL)
    elif wifi_recv>download_crit_tresh:
        print(Style.BRIGHT +" Download Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {wifi_recv}GB\n" + Style.RESET_ALL)
    elif wifi_recv<=1:
        print(Style.BRIGHT +" Download Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {wifi_recv}GB ! ! !\n" + Style.RESET_ALL)

def print_upload(wifi_sent):
    if wifi_sent>upload_warn_tresh:
        print(Style.BRIGHT +  " Upload Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f" {wifi_sent}GB \n\n" + Style.RESET_ALL) #check download values
    elif wifi_sent>upload_warn_tresh and wifi_sent>upload_crit_tresh:
        print(Style.BRIGHT+" Upload Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f" {wifi_sent}GB \n\n" + Style.RESET_ALL)
    elif wifi_sent>upload_crit_tresh:
        print(Style.BRIGHT +" Upload Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {wifi_sent}GB \n\n" + Style.RESET_ALL)
    elif wifi_sent<=1:
        print(Style.BRIGHT +" Upload Speed: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {wifi_sent}GB ! ! !\n\n" + Style.RESET_ALL)
    

def print_disk(disk_prec):
    if disk_prec < disk_warn_tresh:
        print(Style.BRIGHT + " Disk usage:"+Style.RESET_ALL + Style.BRIGHT+ Fore.GREEN +f"{disk_prec}%\n\n" + Style.RESET_ALL)
    if disk_prec > disk_warn_tresh and disk_prec < disk_crit_tresh:
        print(Style.BRIGHT + " Disk usage:"+Style.RESET_ALL + Style.BRIGHT+ Fore.YELLOW +f"{disk_prec}%\n\n" + Style.RESET_ALL)
    if disk_prec > disk_crit_tresh and disk_prec<97:
        print(Style.BRIGHT + " Disk usage:"+Style.RESET_ALL + Style.BRIGHT+ Fore.RED +f"{disk_prec}%\n\n" + Style.RESET_ALL)
    if disk_prec >= 97:
        print(Style.BRIGHT + " Disk usage:"+Style.RESET_ALL + Style.BRIGHT+ Fore.RED +f"{disk_prec}%! ! !\n\n" + Style.RESET_ALL)
def show_footer():
    console.print("[#FF0000]m[/]ade by ary", end="\r")
    time.sleep(iv_cw)
    console.print("[#F8C000]m[/][#FF0000]a[/]de by ary", end="\r")
    time.sleep(iv_cw)
    console.print("[#E9D502]m[/][#F8C000]a[/][#FF0000]d[/]e by ary", end="\r")
    time.sleep(iv_cw)
    console.print("[#85FF00]m[/][#E9D502]a[/][#F8C000]d[/][#FF0000]e[/] by ary", end="\r")
    time.sleep(iv_cw)
    console.print("[#0EE3D8]m[/][#85FF00]a[/][#E9D502]d[/][#F8C000]e[/] [#FF0000]b[/]y ary", end="\r")
    time.sleep(iv_cw)
    console.print("[#743089]m[/][#0EE3D8]a[/][#85FF00]d[/][#E9D502]e[/] [#F8C000]b[/][#FF0000]y[/] ary", end="\r")
    time.sleep(iv_cw)
    console.print("m[#743089]a[/][#0EE3D8]d[/][#85FF00]e[/] [#E9D502]b[/][#F8C000]y[/] [#FF0000]a[/]ry", end="\r")
    time.sleep(iv_cw)
    console.print("ma[#743089]d[/][#0EE3D8]e[/] [#85FF00]b[/][#E9D502]y[/] [#F8C000]a[/][#FF0000]r[/]y", end="\r")
    time.sleep(iv_cw)
    console.print("mad[#743089]e[/] [#0EE3D8]b[/][#85FF00]y[/] [#E9D502]a[/][#F8C000]r[/][#FF0000]y[/]", end="\r")
    time.sleep(iv_cw)
    console.print("made [#743089]b[/][#0EE3D8]y[/] [#85FF00]a[/][#E9D502]r[/][#F8C000]y[/]", end="\r")
    time.sleep(iv_cw)
    console.print("made b[#743089]y[/] [#0EE3D8]a[/][#85FF00]r[/][#E9D502]y[/]", end="\r")
    time.sleep(iv_cw)
    console.print("made by [#743089]a[/][#0EE3D8]r[/][#85FF00]y[/]", end="\r")
    time.sleep(iv_cw)
    console.print("made by a[#743089]r[/][#0EE3D8]y[/]", end="\r")
    time.sleep(iv_cw)
    console.print("made by ar[#743089]y[/]", end="\r")
    time.sleep(iv_cw)
    console.print("made by ary", end="\r")

