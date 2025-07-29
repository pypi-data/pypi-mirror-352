from scapy.all import ARP ,Ether , srp
import socket
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import box
from datetime import datetime
from openrecon.core.macLookUp import lookup_mac_vendor


console = Console()

def resolve_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"
    

def live_discovery(target_range, interval=5):
    known_hosts = {}
    mac_tracking = {}

    def scan():
        pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_range)
        ans, _ = srp(pkt, timeout=2, verbose=0)
        results = {}
        for _, rcv in ans:
            ip = rcv.psrc
            mac = rcv.hwsrc
            hostname = resolve_hostname(ip)
            timestamp = datetime.now().strftime("%H:%M:%S")
            vendor = lookup_mac_vendor(mac)
            
            if ip in mac_tracking:
                if mac_tracking[ip] == mac:
                    device_type = "Static"
                else:
                    device_type = "Dynamic"
                    mac_tracking[ip] = mac
            else:
                mac_tracking[ip] = mac
                device_type = "Dynamic"
                
            results[ip] = {
                "ip": ip,
                "hostname": hostname,
                "mac": mac,
                "vendor": vendor,
                "device_type": device_type,
                "status": "UP",
                "rtt": round((rcv.time - _.sent_time) * 1000, 2),
                "timestamp": timestamp,
            }
        return results

    with Live(refresh_per_second=2) as live:
        while True:
            scan_results = scan()
            for ip in known_hosts:
                known_hosts[ip]["status"] = "DOWN"

            for ip, info in scan_results.items():
                known_hosts[ip] = info

            #table
            table = Table(title="Live ARP Discovery", box=box.SIMPLE_HEAD)
            table.add_column("IP / Hostname", style="bold yellow")
            table.add_column("Status", style="bold")
            table.add_column("RTT", justify="right")
            table.add_column("MAC Address")
            table.add_column("Vendor", style="dim")
            table.add_column("Type", justify="center", style="cyan")

            for ip, data in sorted(known_hosts.items()):
                status = data["status"]
                hostname = data["hostname"]
                color = {
                    "UP": "green",
                    "DOWN": "red",
                    "UNKNOWN": "grey"
                }.get(status, "grey")

                table.add_row(
                    f"{ip} / {hostname}",
                    f"[{color}]{status}[/{color}]",
                    f"{data.get('rtt', 'N/A')} ms",
                    data.get("mac", "N/A"),
                    data.get("vendor", "Unknown"),
                    data.get("device_type", "Unknown")
                )

            live.update(table)
            time.sleep(interval)