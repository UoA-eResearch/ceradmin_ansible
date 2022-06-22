import re


def get_server_ipv4s(openstack_instance: dict, ip_regex: str = None):
    ips = []
    networks = openstack_instance['addresses'].values()
    for network in networks:
        if ip_regex is None:
            ips.extend((address['addr'] for address in network if address['version'] == 4))
        else:
            ips.extend((address['addr'] for address in network
                       if address['version'] == 4 and re.match(ip_regex, address['addr'])))
    return ips


def get_first_server_ipv4(openstack_instance: dict, ip_regex: str):
    ip = None
    ips = get_server_ipv4s(openstack_instance, ip_regex)
    if len(ips) > 0:
        ip = ips[0]
    return ip


class FilterModule(object):

    def filters(self):
        return {
            'get_server_ipv4s': get_server_ipv4s,
            'get_first_server_ipv4': get_first_server_ipv4
        }
