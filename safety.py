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
    # Turn the YAML text into a normal Python dictionary called cfg
    cfg = yaml.safe_load(f)

# Get the threshold limits from the YAML file using .get()
cpu_warn_tresh = cfg.get("cpu_warn_tresh")
ram_warn_tresh = cfg.get("ram_warn_tresh") 
cpu_crit_tresh = cfg.get("cpu_crit_tresh")
ram_crit_tresh = cfg.get("ram_crit_tresh") 

# Counter variables initialization
cpu_strikes = 0             # cpu strikes is the trigger for a jira ticket, as soon as this hits 5, a jira ticket will be created.
cpu_critical = 0            # cpu critical is the trigger for a phone call or sms, as soon as this hits 5, a phone call will be done.
cpu_reset = 0               # cpu reset is the reset trigger for the values above. As soon as this value hits 5, both critical and strike will be set back to zero
ram_strikes = 0             # same functions as the cpu values, just replace "cpu" with "ram" while reading and voila, you have your explanations!
ram_critical = 0
ram_reset = 0

# The fixed function: gets its thresholds dropped right into it from main.py
def check_treshhold(cpu, ram, cpu_warn, cpu_crit, ram_warn, ram_crit):
    # lets the function access and change the tracking counters we made up top
    global cpu_strikes, cpu_critical, cpu_reset
    global ram_strikes, ram_critical, ram_reset
    
    # ==================== CPU MONITORING ====================
    # If the CPU is chill and below the warning limit, tick up the reset counter
    if cpu < cpu_warn:
        cpu_reset += 1                                      
        
    # If it hits the warning zone but hasn't gone completely critical yet
    if cpu >= cpu_warn and cpu < cpu_crit:
        cpu_strikes += 1                                    # adds a "strike" to the counter
        cpu_reset = 0                                       # set reset to 0 so it doesn't try to clear the strikes while it's hot
        
    # If the CPU goes into absolute overdrive and hits the critical limit
    if cpu >= cpu_crit:
        cpu_critical += 1                                   # adds to the critical counter for the sms trigger
        cpu_reset = 0                                       # set reset to 0 as soon as we're in a danger zone so it doesn't keep counting
        
    # Once you hit 5 strikes, it's time to make a Jira ticket
    if cpu_strikes == 5:
        # tells python what def to get ready to run in the background
        ticket_sender = threading.Thread(target=create_jira_ticket, args=("CPU", cpu))
        ticket_sender.start()                               # actually runs the def "create_jira_ticket" asynchronously
        cpu_strikes = 0                                     # reset the counter so it doesn't spam tickets
        
    # If it stays critical for 5 checks, send out the emergency alert
    if cpu_critical == 5:
        # spins up a thread to run the twilio alert without freezing the main screen
        calling_twl = threading.Thread(target=send_critical_alert, args=("CPU", cpu))
        calling_twl.start()                                 # shoots the thread off to run
        cpu_critical = 0                                    # reset the counter so you don't get 50 texts a minute
        
    # If the server cools down and hits 5 clean checks in a row, wipe everything
    if cpu_reset == 5:
        cpu_critical = 0
        cpu_strikes = 0
        cpu_reset = 0


    # ==================== RAM MONITORING ====================
    # Check comments above, same exact logic here but just for RAM instead of CPU!
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
    try: 
        # gets the credentials from your local hidden .env file
        jira_url = os.getenv("JIRA_URL")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_token = os.getenv("JIRA_TOKEN") 

        # if one of the variables isn't set, Python will throw a ValueError
        if not jira_url or not jira_email or not jira_token:
            raise ValueError("Missing required JIRA environment variables (JIRA_URL, JIRA_EMAIL, JIRA_TOKEN)") 
        
        # entering the email of the jira account and the API token to log in
        jira_connection = JIRA(
            options={'server': jira_url}, 
            basic_auth=(jira_email, jira_token) 
        )
        
        # setting up all the fields that will be dropped into the Jira ticket
        ticket_data = {
            'project': {'key': 'KAN'},                                                    # ticket name / project key (bottom left of the ticket)
            'issuetype': {'name': 'Task'},                                                # task, like idk it's an editable task, yall know how to use jira ig, just accept it's here
            'summary': f'WARNING:{part} usage too high!',                                 # Big text in the centre of the ticket, "header of the ticket"
            'description': f'The server {part} utilization is dangerously high. Current value: {part_value}%.', # closer information regarding the ticket details
            'priority': {'name': 'High'}                                                  # sets priority level
        }
        
        # this line actually builds the ticket on your remote board
        new_issue = jira_connection.create_issue(fields=ticket_data)                                    
        print(f"{part} usage dangerously high. Check {new_issue.key} on Jira for more information!")

    except Exception as e:
        # if, for whatever reason, jira or python fails to create the ticket, it will tell you why here
        print(f"\n[JIRA ERROR] Failed to create ticket: {e}")


# ================== Twilio Call (critical alert) ================================
def send_critical_alert(part, part_value):
        # setting the variables from the .env file here for simplicity
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")            
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_num = os.getenv("TWILIO_PHONENUM")
        to_num = os.getenv("TO_PHONE_NUM")

        # setting up the text body as a variable for simplicity
        alert_message = f"ALERT! {part} IS REACHING CRITICAL LIMITS! CURRENT USAGE: {part_value}"     

        # Lets Python tell you exactly what part of the entered data in the .env file is missing
        if not account_sid:
            print("\nERROR Missing or incorrect Account SID in .env! (TWILIO_ACCOUNT_SID)")         
            return
        if not auth_token:
            print("\nERROR Missing or incorrect authentication Token in .env! (TWILIO_AUTH_TOKEN)")
            return
        if not from_num:
            print("\nERROR Missing or incorrect Twilio Phone Number in .env! (TWILIO_PHONENUM)")
            return
        if not to_num:
            print("\nERROR Missing or incorrect receiver Phone number in .env! (TO_PHONE_NUM)")
            return

        # AI generated mock for testing, irrelevant for real users, debug / dev only
        if "mock_" in account_sid or "YOUR_TWILIO" in account_sid:                                  
            print("\n" + "="*60)
            print("📱 [TWILIO SIMULATION MODE - LOGIC VERIFIED]")
            print(f"TO: {to_num}")
            print(f"FROM: {from_num}")
            print(f"BODY: {alert_message}")
            print("📞 STATUS: Simulated emergency alert handled safely!")
            print("="*60 + "\n")
        else:
            # if he doesn't find the mock keys, he knows this is real and runs the actual code
            try:
                from twilio.rest import Client                                                      
                client = Client(account_sid, auth_token)                                            

                # Creates the actual SMS payload, pieces it together, and fires it off
                message = client.messages.create(                                                   
                    body=alert_message,
                    from_=from_num,
                    to=to_num
                )
                print("Message sent successfully! ~Twilio")                                         # Message that appears in the main interface if an sms has been sent

            except Exception as e:
                # if, for whatever reason, twilio can't send a message, it will display this message
                print(f"SENDING MESSAGE FAILED: {e}, server might be dead, or burnt, or whatever, im probably cooked by the time you find this")