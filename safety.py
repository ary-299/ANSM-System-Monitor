import threading
from jira import JIRA
import os
import yaml
from dotenv import load_dotenv

# Load environmental variables from your hidden local .env file
load_dotenv()

# Set up the path to your config file
config_path = "cfg.YAML"  

# Open up the YAML file so we can read it
with open(config_path, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

# Dig safely into the nested thresholds and settings sections
threshold_dict = cfg.get("thresholds") or {}
settings_dict = cfg.get("settings") or {}

# List with active alert strings vvv
active_alerts = []
total_tickets_created = 0  #Session tracker
# Safely extract values and convert to integers
cpu_warn_tresh = int(threshold_dict.get("cpu_warn_tresh") or 80)
ram_warn_tresh = int(threshold_dict.get("ram_warn_tresh") or 80) 
cpu_crit_tresh = int(threshold_dict.get("cpu_crit_tresh") or 95)
ram_crit_tresh = int(threshold_dict.get("ram_crit_tresh") or 95) 
check_interval_seconds = int(settings_dict.get("check_interval_seconds") or 5)

# Counter variables initialization
cpu_strikes = 0             
cpu_critical = 0            
cpu_reset = 0               
ram_strikes = 0             
ram_critical = 0
ram_reset = 0

# --- PERSISTENT SEED STATE AND MESSAGE VARIABLES ---
total_tickets_created = 0   # Total tickets created since monitor session started

# Booleans tracking active alert states
cpu_ticket_active = False
cpu_alert_active = False
ram_ticket_active = False
ram_alert_active = False

# Message buffers to hold content for the recurring reprint loops
active_cpu_ticket_msg = ""
active_cpu_alert_msg = ""
active_ram_ticket_msg = ""
active_ram_alert_msg = ""


# ==================== ASYNCHRONOUS REPRINT LOOPS ====================
def loop_cpu_ticket_print():
    global cpu_ticket_active, active_cpu_ticket_msg, check_interval_seconds
    if cpu_ticket_active:
        if active_cpu_ticket_msg:
            print(active_cpu_ticket_msg)
        threading.Timer(check_interval_seconds, loop_cpu_ticket_print).start()

def loop_cpu_alert_print():
    global cpu_alert_active, active_cpu_alert_msg, check_interval_seconds
    if cpu_alert_active:
        if active_cpu_alert_msg:
            print(active_cpu_alert_msg)
        threading.Timer(check_interval_seconds, loop_cpu_alert_print).start()

def loop_ram_ticket_print():
    global ram_ticket_active, active_ram_ticket_msg, check_interval_seconds
    if ram_ticket_active:
        if active_ram_ticket_msg:
            print(active_ram_ticket_msg)
        threading.Timer(check_interval_seconds, loop_ram_ticket_print).start()

def loop_ram_alert_print():
    global ram_alert_active, active_ram_alert_msg, check_interval_seconds
    if ram_alert_active:
        if active_ram_alert_msg:
            print(active_ram_alert_msg)
        threading.Timer(check_interval_seconds, loop_ram_alert_print).start()


# The fixed function: gets its thresholds dropped right into it from main.py
def check_treshhold(cpu, ram, cpu_warn, cpu_crit, ram_warn, ram_crit):
    # lets the function access and change the tracking counters we made up top
    global cpu_strikes, cpu_critical, cpu_reset
    global ram_strikes, ram_critical, ram_reset
    
    # ==================== CPU MONITORING ====================
    if cpu < cpu_warn:
        cpu_reset += 1                                      
        
    if cpu >= cpu_warn and cpu < cpu_crit:
        cpu_strikes += 1                                    
        cpu_reset = 0                                       
        
    if cpu >= cpu_crit:
        cpu_critical += 1                                   
        cpu_reset = 0                                       
        
    if cpu_strikes == 5:
        ticket_sender = threading.Thread(target=create_jira_ticket, args=("CPU", cpu))
        ticket_sender.start()                               
        cpu_strikes = 0                                     
        
    if cpu_critical == 5:
        calling_twl = threading.Thread(target=send_critical_alert, args=("CPU", cpu))
        calling_twl.start()                                 
        cpu_critical = 0                                    
        
    if cpu_reset == 5:
        cpu_critical = 0
        cpu_strikes = 0
        cpu_reset = 0

    # ==================== RAM MONITORING ====================
    if ram < ram_warn:
        ram_reset += 1  
        
    if ram >= ram_warn and ram < ram_crit:
        ram_strikes += 1
        ram_reset = 0
        
    if ram >= ram_crit:
        ram_critical += 1
        ram_reset = 0
        
    if ram_strikes == 5:
        ticket_sender = threading.Thread(target=create_jira_ticket, args=("RAM", ram))
        ticket_sender.start()
        ram_strikes = 0                                     
        
    if ram_critical == 5:
        calling_twl = threading.Thread(target=send_critical_alert, args=("RAM", ram))
        calling_twl.start()
        ram_critical = 0
        
    if ram_reset == 5:
        ram_strikes = 0
        ram_critical = 0
        ram_reset = 0


# ========================== JIRA TICKET CREATION =======================================
def create_jira_ticket(part, part_value):
    global total_tickets_created, cpu_ticket_active, ram_ticket_active, active_cpu_ticket_msg, active_ram_ticket_msg
    try: 
        jira_url = os.getenv("JIRA_URL")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_token = os.getenv("JIRA_TOKEN") 

        if not jira_url or not jira_email or not jira_token:
            raise ValueError("Missing required JIRA environment variables (JIRA_URL, JIRA_EMAIL, JIRA_TOKEN)") 
        
        jira_connection = JIRA(
            options={'server': jira_url}, 
            basic_auth=(jira_email, jira_token) 
        )
        
        ticket_data = {
            'project': {'key': 'KAN'},                                                                    
            'issuetype': {'name': 'Task'},                                                                
            'summary': f'WARNING:{part} usage too high!',                                                 
            'description': f'The server {part} utilization is dangerously high. Current value: {part_value}%.', 
            'priority': {'name': 'High'}                                                                  
        }
        
        new_issue = jira_connection.create_issue(fields=ticket_data)                                    
        success_msg = f"{part} usage dangerously high. Check {new_issue.key} on Jira for more information!"
        
        total_tickets_created += 1
        
        # Set persistent state message and spin up asynchronous loop thread
        if part == "CPU":
            active_cpu_ticket_msg = success_msg
            if not cpu_ticket_active:
                cpu_ticket_active = True
                threading.Thread(target=loop_cpu_ticket_print, daemon=True).start()
        else:
            active_ram_ticket_msg = success_msg
            if not ram_ticket_active:
                ram_ticket_active = True
                threading.Thread(target=loop_ram_ticket_print, daemon=True).start()

    except Exception as e:
        print(f"\n[JIRA ERROR] Failed to create ticket: {e}")


# ================== Twilio Call (critical alert) ================================
def send_critical_alert(part, part_value):
    global cpu_alert_active, ram_alert_active, active_cpu_alert_msg, active_ram_alert_msg
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")            
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_num = os.getenv("TWILIO_PHONENUM")
    to_num = os.getenv("TO_PHONE_NUM")

    alert_message = f"ALERT! {part} IS REACHING CRITICAL LIMITS! CURRENT USAGE: {part_value}"     

    if not account_sid or not auth_token or not from_num or not to_num:
        print("\n[TWILIO ERROR] Missing credential variables in local environment file.")
        return

    if "mock_" in account_sid or "YOUR_TWILIO" in account_sid:                                   
        sim_msg = f"\n📱 [TWILIO SIMULATION MODE]\nTO: {to_num}\nFROM: {from_num}\nBODY: {alert_message}\n📞 STATUS: Active alert handled safely!"
        
        if part == "CPU":
            active_cpu_alert_msg = sim_msg
            if not cpu_alert_active:
                cpu_alert_active = True
                threading.Thread(target=loop_cpu_alert_print, daemon=True).start()
        else:
            active_ram_alert_msg = sim_msg
            if not ram_alert_active:
                ram_alert_active = True
                threading.Thread(target=loop_ram_alert_print, daemon=True).start()
    else:
        try:
            from twilio.rest import Client                                                                      
            client = Client(account_sid, auth_token)                                                            

            message = client.messages.create(                                                                  
                body=alert_message,
                from_=from_num,
                to=to_num
            )
            live_msg = f"Message sent successfully! ID: {message.sid} ~Twilio"
            
            if part == "CPU":
                active_cpu_alert_msg = live_msg
                if not cpu_alert_active:
                    cpu_alert_active = True
                    threading.Thread(target=loop_cpu_alert_print, daemon=True).start()
            else:
                active_ram_alert_msg = live_msg
                if not ram_alert_active:
                    ram_alert_active = True
                    threading.Thread(target=loop_ram_alert_print, daemon=True).start()

        except Exception as e:
            print(f"SENDING MESSAGE FAILED: {e}")