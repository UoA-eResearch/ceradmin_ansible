import re


def ipv4s(openstack_instance: dict, ip_regex: str = None):
    ips = []
    networks = openstack_instance['addresses'].values()
    for network in networks:
        if ip_regex is None:
            ips.extend((address['addr'] for address in network if address['version'] == 4))
        else:
            ips.extend((address['addr'] for address in network
                       if address['version'] == 4 and re.match(ip_regex, address['addr'])))
    return ips


def first_ipv4(openstack_instance: dict, ip_regex: str):
    ip = None
    ips = ipv4s(openstack_instance, ip_regex)
    if len(ips) > 0:
        ip = ips[0]
    return ip


class FilterModule(object):

    def filters(self):
        return {
            'ipv4s': ipv4s,
            'first_ipv4': first_ipv4
        }
