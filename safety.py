import threading
from jira import JIRA

cpu_strikes = 0             #cpu strikes is the trigger for a jira ticket, as soon as this hits 5, a jira ticket will be created.
cpu_critical = 0             #cpu critical is the trigger for a phone call or sms, as soon as this hits 5, a phone call will be done.
cpu_reset = 0               #cpu reset is the reset trigger for the values above. As soon as this value hits 5, both critical and strike will be set back to zero
ram_strikes = 0             #same functions as the cpu values, just replace "cpu" with "ram" while reading and voila, you have your explanations!
ram_critical = 0
ram_reset = 0

def check_treshhold(cpu, ram):
    global cpu_strikes, cpu_critical, cpu_reset             #lets the if function access the variables above
    if cpu < 80:
        cpu_reset += 1                                      #adds to the reset counter 
    if cpu >= 80 and cpu < 95:
        cpu_strikes += 1                                    #adds a "strike" to the counter
        cpu_critical = cpu_critical   
        cpu_reset = 0                                       #keeps the critical counter the same, not resetting it
    if cpu >= 95:
        cpu_critical += 1
        cpu_strikes = cpu_strikes                           #keeps the strike counter the same, not resetting it
        cpu_reset = 0                                       #set reset to 0 as soon as were in a danger zone so it doesnt keep counting
    if cpu_strikes == 5:
        ticket_sender = threading.Thread(
            target=create_jira_ticket,                      #tells python what def to get ready to run
            args=("CPU", cpu)                               #gives python values to set into variables -> Since "CPU" comes first "CPU" will be assigned to the first variable mentioned. Here this is {part}
        )
        ticket_sender.start()                               #acctually runs the def "create_jira_ticket"
        cpu_strikes = 0                                     #reset the counter so it doesnt spam
    if cpu_critical == 5:
        pass #TODO: add code for phone call
        cpu_critical = 0
    if cpu_reset == 5:
        cpu_critical = 0
        cpu_strikes = 0
        cpu_reset = 0

    global ram_strikes, ram_critical, ram_reset             #check comments above, same as there but just with the ram instead of the cpu
    if ram < 80:
        ram_reset += 1  
    if ram >= 80 and ram < 95:
        ram_strikes += 1
        ram_critical = ram_critical
        ram_reset = 0
    if ram >= 95:
        ram_critical += 1
        ram_strikes = ram_strikes
        ram_reset = 0
    if ram_strikes == 5:
        ticket_sender = threading.Thread(
            target=create_jira_ticket,
            args=("RAM", ram)
        )
        ticket_sender.start()
    if ram_critical == 5:
        pass #TODO: code for phone call / sms here 
    if ram_reset == 5:
        ram_strikes = 0
        ram_critical = 0
        ram_reset = 0

def create_jira_ticket(part, part_value):
    try: 
        jira_connection = JIRA(
            options={'server': 'https://xxx.atlassian.net'}, 
            basic_auth=('xxx', 'xxx')
        )
        ticket_data = {
            'project': {'key': 'KAN'},
            'issuetype': {'name': 'Task'},
            'summary': f'WARNING:{part} usage too high!',
            'description': f'The server {part} utilization is dangerously high. Current value: {part_value}%.',
            'priority': {'name': 'High'}
        }
        new_issue = jira_connection.create_issue(fields=ticket_data)                                        
        print(f"{part} usage dangerously high. Check {new_issue.key} on Jira for more information!")

    except Exception as e:
        print(f"\n[JIRA ERROR] Failed to create ticket: {e}")