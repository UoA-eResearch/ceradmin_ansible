import re


def get_server_ipv4s(server_dict: dict, ip_regex: str = None):
    ips = []
    # standard IPv4 addresses
    networks = server_dict['addresses'].values()
    for network in networks:
        if ip_regex is None:
            ips.extend((address['addr'] for address in network if address['version'] == 4))
        else:
            ips.extend((address['addr'] for address in network
                       if address['version'] == 4 and re.match(ip_regex, address['addr'])))

    # floating ips
    if 'floating_ips' in server_dict:
        if ip_regex is None:
            ips.extend((fip['floating_ip_address'] for fip in server_dict['floating_ips']))
        else:
            ips.extend((fip['floating_ip_address'] for fip in server_dict['floating_ips']
                        if re.match(ip_regex, fip['floating_ip_address'])))

    return list(set(ips))


def get_first_server_ipv4(server_dict: dict, ip_regex: str):
    ip = None
    ips = get_server_ipv4s(server_dict, ip_regex)
    if len(ips) > 0:
        ip = ips[0]
    return ip


class FilterModule(object):

    def filters(self):
        return {
            'get_server_ipv4s': get_server_ipv4s,
            'get_first_server_ipv4': get_first_server_ipv4
        }
