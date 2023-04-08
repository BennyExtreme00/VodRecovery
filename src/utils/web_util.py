import os.path
import random

from file_util import open_file


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
