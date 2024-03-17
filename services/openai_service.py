from flask import current_app as app
from openai import OpenAI


def convert_to_prompt_base(log_lines):
    prompt = f'''

  
    The following log lines are given as input: 

    '''
    for line in log_lines:
        prompt += f"{line}\n"
    prompt += f'''
    Using the above log lines, extract only the <Log Line> parameter. Display it in this format: <Log Line>
    '''

    return prompt

def convert_to_prompt_ipaddr(log_lines, query):
    prompt = f'''

  
    The following log lines are given as input: 

    '''
    for line in log_lines:
        prompt += f"{line}\n"
    prompt += f'''
    Using the above log lines, answer the following query: {query}. Give output in the following format: 
    
    <IP1> <IP2> <IP3> <IP4> <IP5> <IP6> <IP7> <IP8> <IP9> ....

    Also give the count of IP at the end in a separate line. 
    '''

    return prompt

def convert_to_prompt_user(log_lines, query):
    prompt = f'''

  
    The following log lines are given as input: 

    '''
    for line in log_lines:
        prompt += f"{line}\n"
    prompt += f'''
    Using the above log lines, answer the following query: {query}. Give output in the following format: 
    
   <user1> <user2> <user3> <user4> <user5> <user6> <user7> <user8> <user9> ....

    Also give the count of users at the end in a separate line. 
    '''

    return prompt

def call_openai_api_log_file(prompt):
    # Call OpenAI API and get response
    system = '''You are a an assistant who is geared towards answering questions on SSH logs of format <Timestamp> LabSZ sshd[<PID>]: <Log line>. The log lines will contain IP of the format aaa.bbb.ccc.ddd. You can ignore LabSZ and sshd[<PID>], and only use Timestamp, Logline for answering questions. The <PID> is unique number, which is to used as an identifier, and not as a numeric value. 
    '''

    
    client = OpenAI(api_key=app.config['OPENAI_API_KEY'])
    MODEL = "gpt-3.5-turbo"
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ],
    temperature=0,
    )
    return response.choices[0].message.content


