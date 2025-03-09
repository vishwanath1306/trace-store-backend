import re
import json
import os
from datetime import datetime
from typing import Dict, Any, List

def parse_openstack_log_line(log_line: str) -> Dict[str, Any]:
    pattern = r"""
        ^(?P<log_file_name>
            nova-\w+         # e.g., nova-compute
            \.log            # .log
            (?:\.\d+)?       # optionally: .<digits> 
            \.\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}  # e.g., .2017-05-17_12:02:35
        )\s+
        (?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(\.\d+)?)\s+
        (?P<process_id>\d+)\s+
        (?P<log_level>\w+)\s+
        (?P<component>[\w.\-]+)\s*
        (?:\[(?P<request_metadata>[^\]]+)\]\s+)?  
        (?P<content>.*)$
    """

    match = re.match(pattern, log_line, re.VERBOSE)
    if not match:
        print("DEBUG - Regex match failed for line:", log_line)
        raise ValueError("Failed to parse log line")

    data = match.groupdict()

    # Determine log_file_type heuristically (this is unchanged)
    log_file_type = data['log_file_name'].split(".log.")[0]

    # If request_metadata is missing (None), handle gracefully
    request_metadata_raw = data.get('request_metadata') or ""
    metadata = request_metadata_raw.split()

    # We'll set defaults or parse them if they exist
    structured_metadata = {
        "request_id":  metadata[0] if len(metadata) > 0 and metadata[0] != "-" else "",
        "user_id":     metadata[1] if len(metadata) > 1 and metadata[1] != "-" else "",
        "tenant_id":   metadata[2] if len(metadata) > 2 and metadata[2] != "-" else ""
    }

    # Convert timestamp
    # You might need to handle no fractional second separately, but strptime can handle .%f if it’s present:
    # We'll do a small trick: if there is no dot in the time, add '.000000' or handle in a try/except
    timestamp_str = data['timestamp']
    dt_format = '%Y-%m-%d %H:%M:%S.%f'
    if '.' not in timestamp_str:
        dt_format = '%Y-%m-%d %H:%M:%S'
    parsed_time = datetime.strptime(timestamp_str, dt_format)

    parsed_data = {
        "labels": {
            "application": "openstack",
            "log_file_type": log_file_type,
            "log_level": data['log_level'],
            "component": data['component'],
            "log_file_name": data['log_file_name']
        },
        "structured_metadata": structured_metadata,
        "timestamp": parsed_time.isoformat(),
        "content": data['content'].strip()
    }

    formatted_string = ""
    for label_key, label_value in parsed_data["labels"].items():
        formatted_string += f"{label_key}:{label_value} "
    formatted_string += data['content'].strip()

    return parsed_data, formatted_string

