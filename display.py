
from colorama import Fore, Back, Style, init

def show_header():
    print(Fore.RED+Style.BRIGHT+"ANSM "+Style.RESET_ALL+Style.BRIGHT+"Panel\n")

def print_cpu(cpu_val):         #setting "def" commands to run them on "main" later in the script
    if cpu_val<50:
        print(Style.BRIGHT+"CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f" {cpu_val}% " + Style.RESET_ALL)   #prints green for good values
    elif cpu_val<77:
        print(Style.BRIGHT+"CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f" {cpu_val}% " + Style.RESET_ALL)  #prints yellow for okay values
    elif cpu_val<85:
        print(Style.BRIGHT +"CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {cpu_val}% " + Style.RESET_ALL)   #prints red for bad values
    elif cpu_val>=95:
        print(Style.BRIGHT +"CPU usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {cpu_val}% ! ! !" + Style.RESET_ALL)  #prints red with three exl. marks for horrible values

def print_ram(ram_val):         #setting "def" commands to run them on "main" later in the script
    if ram_val<50:
        print(Style.BRIGHT +  "RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f" {ram_val}% " + Style.RESET_ALL) #check cpu values
    elif ram_val<80:
        print(Style.BRIGHT+"RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.YELLOW + f" {ram_val}% " + Style.RESET_ALL)
    elif ram_val<90:
        print(Style.BRIGHT +"RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {ram_val}% " + Style.RESET_ALL)
    elif ram_val>=95:
        print(Style.BRIGHT +"RAM usage: " + Style.RESET_ALL + Style.BRIGHT + Fore.RED + f" {ram_val}% ! ! !" + Style.RESET_ALL)

def show_footer():
    print("\nmade by ary")
