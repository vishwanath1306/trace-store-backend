import re
import json
import os
from datetime import datetime
from typing import Dict, Any, List

def parse_openssh_log_line(log_line: str) -> Dict[str, Any]:
    pattern = r"""
        ^(?P<timestamp>
            (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+  # Month
            \d{1,2}\s+                                              # Day
            \d{2}:\d{2}:\d{2}                                       # Time
        )\s+
        (?P<hostname>\S+)\s+
        (?P<process>sshd)\[(?P<process_id>\d+)\]:\s+
        (?P<content>.*)$
    """

    match = re.match(pattern, log_line, re.VERBOSE)
    if not match:
        print("DEBUG - Regex match failed for line:", log_line)
        raise ValueError("Failed to parse OpenSSH log line")

    data = match.groupdict()

    # Determine log level based on content keywords
    log_level = "INFO"
    if any(keyword in data['content'].lower() for keyword in ["failed", "invalid", "error", "break-in"]):
        log_level = "ERROR"
    elif any(keyword in data['content'].lower() for keyword in ["warning", "possible"]):
        log_level = "WARNING"

    # Extract structured metadata - important fields from content
    structured_metadata = {}
    
    # Extract user information if present
    user_match = re.search(r"user (\S+)", data['content'])
    if user_match:
        structured_metadata["user"] = user_match.group(1)
    
    # Extract IP address if present
    ip_match = re.search(r"from (\d+\.\d+\.\d+\.\d+)", data['content'])
    if ip_match:
        structured_metadata["source_ip"] = ip_match.group(1)
    
    # Extract port if present
    port_match = re.search(r"port (\d+)", data['content'])
    if port_match:
        structured_metadata["port"] = port_match.group(1)

    # Convert timestamp - add current year as it's not in the logs
    current_year = datetime.now().year
    timestamp_str = f"{current_year} {data['timestamp']}"
    parsed_time = datetime.strptime(timestamp_str, '%Y %b %d %H:%M:%S')
    
    # If the parsed date is in the future, it's likely from the previous year
    if parsed_time > datetime.now():
        parsed_time = datetime.strptime(f"{current_year-1} {data['timestamp']}", '%Y %b %d %H:%M:%S')

    parsed_data = {
        "labels": {
            "application": "openssh",
            "log_level": log_level,
            "component": "sshd",
            "hostname": data['hostname'],
            "process_id": data['process_id']
        },
        "structured_metadata": structured_metadata,
        "timestamp": parsed_time.isoformat(),
        "content": data['content'].strip()
    }

    # Format a searchable string similar to the OpenStack parser
    formatted_string = ""
    for label_key, label_value in parsed_data["labels"].items():
        formatted_string += f"{label_key}:{label_value} "
    formatted_string += data['content'].strip()

    return parsed_data, formatted_string