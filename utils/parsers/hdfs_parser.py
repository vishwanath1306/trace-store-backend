import re
from datetime import datetime
from typing import Dict, Any, Tuple

def parse_hdfs_log_line(log_line: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse a single line from an HDFS log file.
    
    Example log format:
    081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving block blk_-1608999687919862906 src: /10.250.19.102:54106 dest: /10.250.19.102:50010
    
    Format: Date, Time, Pid, Level, Component, Content
    """
    pattern = r"""
        ^(?P<date>\d{6})\s+
        (?P<time>\d{6})\s+
        (?P<pid>\d+)\s+
        (?P<log_level>\w+)\s+
        (?P<component>[\w.$]+):\s+
        (?P<content>.*)$
    """

    match = re.match(pattern, log_line, re.VERBOSE)
    if not match:
        print("DEBUG - Regex match failed for line:", log_line)
        raise ValueError("Failed to parse log line")

    data = match.groupdict()
    
    # Parse the timestamp (YYMMDD HHMMSS)
    date_str = data['date']
    time_str = data['time']
    
    # Convert to standard format (assuming 20YY for the year)
    year = int("20" + date_str[0:2])
    month = int(date_str[2:4])
    day = int(date_str[4:6])
    
    hour = int(time_str[0:2])
    minute = int(time_str[2:4])
    second = int(time_str[4:6])
    
    timestamp = datetime(year, month, day, hour, minute, second)
    
    # Determine component details
    component_parts = data['component'].split('.')
    application = component_parts[0] if component_parts else ""
    
    parsed_data = {
        "labels": {
            "application": "hdfs",
            "log_level": data['log_level'],
            "component": data['component'],
            "pid": data['pid']
        },
        "structured_metadata": {
            # Add any structured metadata from the content if needed
        },
        "timestamp": timestamp.isoformat(),
        "content": data['content'].strip()
    }

    # Create formatted string
    formatted_string = ""
    for label_key, label_value in parsed_data["labels"].items():
        formatted_string += f"{label_key}:{label_value} "
    formatted_string += data['content'].strip()

    return parsed_data, formatted_string
