import os.path
import random

from file_util import open_file
from config_util import load_config


def return_header():
    # Move up two directories in order to access the config directory
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
    # Find the user_agents.txt file and read from it.
    user_agents = open_file(os.path.join(config_path, 'user_agents.txt'), 'r')
    header = {
        'user-agent': f'{random.choice(user_agents)}'  # Choose a random user agent and return the header
    }
    return header


def return_domain_list():
    # Initialize the domain list
    domain_list = []
    # Move up two directories in order to access the config directory
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config'))
    # Find the domains.txt file and read from it.
    domains = open_file(os.path.join(config_path, 'domains.txt'), 'r')
    # Loop through the lines and append the domain to the domain list.
    for domain in domains:
        domain_list.append(domain.strip())
    return domain_list  # return the domain list


def check_response_status_code(response):
    # Load the status codes from the configuration file
    config_status_codes = load_config()["REQUESTS"]["STATUS CODES"]
    # Create a list containing each status code
    status_codes = config_status_codes["OK"], config_status_codes["BAD_REQUEST"], config_status_codes["FORBIDDEN"], config_status_codes["NOT_FOUND"], config_status_codes["INTERNAL_SERVER_ERROR"]
    # check if the response status code is in the status_codes list
    if response.status_code in status_codes:
        # If the response status code == OK return true
        if response.status_code == config_status_codes["OK"]:
            return True
        elif response.status_code == config_status_codes["BAD_REQUEST"]:
            return "The request was invalid or could not be understood by the server."
        elif response.status_code == config_status_codes["FORBIDDEN"]:
            return "The client does not have permission to access the requested resource."
        elif response.status_code == config_status_codes["NOT_FOUND"]:
            return "The server could not find the requested resource."
        elif response.status_code == config_status_codes["INTERNAL_SERVER_ERROR"]:
            return "The server encountered an unexpected condition that prevented it from fulfilling the request."
        else:
            return "Unexpected status code returned by the request. Please try again later."
