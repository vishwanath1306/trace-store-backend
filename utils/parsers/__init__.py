from .openstack_parser import parse_openstack_log_line
from .openssh_parser import parse_openssh_log_line
from .hdfs_parser import parse_hdfs_log_line

parser_mapping = {
    "openstack": parse_openstack_log_line,
    "openssh": parse_openssh_log_line,
    "hdfs": parse_hdfs_log_line,
}

def get_parser_for_application(application_name):
    """
    Return the appropriate parser function for the given application name.
    Falls back to openstack parser if application parser is not available.
    """
    application_name = application_name.lower()
    return parser_mapping.get(application_name, parse_openstack_log_line)