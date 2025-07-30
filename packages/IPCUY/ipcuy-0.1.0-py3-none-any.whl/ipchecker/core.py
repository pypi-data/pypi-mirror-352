import ipaddress
import requests

def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_private_ip(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False

def is_in_subnet(ip: str, subnet: str) -> bool:
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(subnet, strict=False)
    except ValueError:
        return False

def get_public_ip() -> str:
    try:
        return requests.get("https://api.ipify.org").text
    except Exception:
        return "Unable to fetch public IP"
