import requests

def lookup_mac_vendor(mac_address):
    try:
        url = f"https://api.macvendors.com/{mac_address}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"Unknown (Status {response.status_code})"
    except requests.RequestException:
        return "Lookup failed (network error)"