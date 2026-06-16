import threading
from jira import JIRA
import os
import yaml
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

# Read config from file at startup
config_path = "cfg.yaml"  # Changed from config_patch to config_path
with open(config_path, "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

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

def check_treshhold(cpu, ram):
    global cpu_strikes, cpu_critical, cpu_reset             # lets the if function access the variables above
    
    # ==================== CPU MONITORING ====================
    if cpu < cpu_warn_tresh:
        cpu_reset += 1                                      # adds to the reset counter 
    if cpu >= cpu_warn_tresh and cpu < cpu_crit_tresh:
        cpu_strikes += 1                                    # adds a "strike" to the counter
        cpu_reset = 0                                       # keeps the critical counter the same, not resetting it
    if cpu >= cpu_crit_tresh:
        cpu_critical += 1    
        cpu_reset = 0                                       # set reset to 0 as soon as were in a danger zone so it doesnt keep counting
    if cpu_strikes == 5:
        ticket_sender = threading.Thread(
            target=create_jira_ticket,                      # tells python what def to get ready to run
            args=("CPU", cpu)                               # gives python values to set into variables -> Since "CPU" comes first "CPU" will be assigned to the first variable mentioned. Here this is {part}
        )
        ticket_sender.start()                               # acctually runs the def "create_jira_ticket"
        cpu_strikes = 0                                     # reset the counter so it doesnt spam
    if cpu_critical == 5:
        calling_twl = threading.Thread(target=send_critical_alert, args=("CPU",cpu))
        calling_twl.start()
        cpu_critical = 0
    if cpu_reset == 5:
        cpu_critical = 0
        cpu_strikes = 0
        cpu_reset = 0




    # ==================== RAM MONITORING====================
    global ram_strikes, ram_critical, ram_reset             # check comments above, same as there but just with the ram instead of the cpu
    if ram < ram_warn_tresh:
        ram_reset += 1  
    if ram >= ram_warn_tresh and ram < ram_crit_tresh:
        ram_strikes += 1
        ram_reset = 0
    if ram >= ram_crit_tresh:
        ram_critical += 1
        ram_reset = 0
    if ram_strikes == 5:
        ticket_sender = threading.Thread(
            target=create_jira_ticket,
            args=("RAM", ram)
        )
        ticket_sender.start()
        ram_strikes = 0                                     # Added reset to prevent ticket spamming!
    if ram_critical == 5:
        calling_twl = threading.Thread(target=send_critical_alert, args=("RAM",ram))
        calling_twl.start()
        ram_critical = 0
    if ram_reset == 5:
        ram_strikes = 0
        ram_critical = 0
        ram_reset = 0











#==========================  JIRA TICKET CREATION =======================================
def create_jira_ticket(part, part_value):
    try: 
        jira_url = os.getenv("JIRA_URL")
        jira_email = os.getenv("JIRA_EMAIL")
        jira_token = os.getenv("JIRA_TOKEN")                                # gets the names from the .env file and sets them as the JIRA_URL, JIRA_EMAIL, JIRA_TOKEN variables

        if not jira_url or not jira_email or not jira_token:
            raise ValueError("Missing required JIRA environment variables (JIRA_URL, JIRA_EMAIL, JIRA_TOKEN)")              # if one of the Variables isnt set, Python will throw a Value Error
        
        jira_connection = JIRA(
            options={'server': jira_url}, 
            basic_auth=(jira_email, jira_token)         #entering the email of the jira account and the API token
        )
        ticket_data = {
            'project': {'key': 'KAN'},                                                #ticket name (bottm left of the ticket)
            'issuetype': {'name': 'Task'},                                                #task, like idk its a task thats editable, yall know how to use jira ig, just accept that this is here
            'summary': f'WARNING:{part} usage too high!',                                  #Big text in the centre of the ticket, "header of the ticket"
            'description': f'The server {part} utilization is dangerously high. Current value: {part_value}%.',     #closer information regarding the ticket
            'priority': {'name': 'High'}                                                       #sets priority
        }
        new_issue = jira_connection.create_issue(fields=ticket_data)                                #creates the ticket itself                                    
        print(f"{part} usage dangerously high. Check {new_issue.key} on Jira for more information!")

    except Exception as e:
        print(f"\n[JIRA ERROR] Failed to create ticket: {e}")                                            #if, for whatever reason, jira or python fails to create the ticket, it will tell you.
                                                                                                        #the fact that it even tried to create a ticket should be enough for the moment



#================== Twilio Call(critical alert)================================

def send_critical_alert(part, part_value):
        account_sid=os.getenv("TWILIO_ACCOUNT_SID")             #setting the variables from the .env file here for simplicity
        auth_token=os.getenv("TWILIO_AUTH_TOKEN")
        from_num=os.getenv("TWILIO_PHONENUM")
        to_num=os.getenv("TO_PHONE_NUM")

        alert_message=f"ALERT! {part} IS REACHING CRITICAL LIMITS! CURRENT USAGE: {part_value}"     #sms set as "alert_message" variable for simplicity

        if not account_sid:
            print("\nERROR Missing or incorrect Account SID in .env! (TWILIO_ACCOUNT_SID)")         #Lets Python tell you exactly what part of the entered data in the .env file is wrong
            return
        if not auth_token:
            print("\nERROR Missing or incorrect authentication Token in .env! (TWILIO_AUTH_TOKEN)")
            return
        if not from_num:
            print("\nERROR Missing or incorrect Twilion Phone Number in .env! (TWILIO_PHONENUM)")
            return
        if not to_num:
            print("\nERROR Missing or incorrect reciever Phone numer in .env! (TO_PHONE_NUM)")
            return

        if "mock_" in account_sid or "YOUR_TWILIO" in account_sid:                                  #AI generated mock for testing, irrelevant for real users, debug / dev only
            print("\n" + "="*60)
            print("📱 [TWILIO SIMULATION MODE - LOGIC VERIFIED]")
            print(f"TO: {to_num}")
            print(f"FROM: {from_num}")
            print(f"BODY: {alert_message}")
            print("📞 STATUS: Simulated emergency alert handled safely!")
            print("="*60 + "\n")
        else:
            try:
                from twilio.rest import Client                                                      #in the mock code, python checks for "mock_" in "account_sid" or "YOUR_TWILIO" in account_sid,
                client = Client(account_sid, auth_token)                                            # if he doesnt find it, he knows that this is not a mock and starts the acctual code

                message = client.messages.create(                                                   #Creates the acctual SMS to send, sets it together and sends it
                    body=alert_message,
                    from_=from_num,
                    to=to_num
                )
                print("Message sent successfully! ~Twilio")                                         #Message that appears in the main interface if a sms has been sent

            except Exception as e:
                print(f"SENDING MESSAGE FAILED: {e}, server might be dead, or burnt, or whatever, im probably cooked by the time you find this")    #if, for whatever reason, twilio cant send a message, it will only display this messaage