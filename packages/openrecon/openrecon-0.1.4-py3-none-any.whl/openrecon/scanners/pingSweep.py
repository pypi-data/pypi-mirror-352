import subprocess
import platform
import datetime
import time
import ipaddress
import socket
import concurrent.futures
import re
from rich.console import Console
from rich.text import Text
from rich.progress import Progress, TaskID
from typing import List, Dict, Tuple, Optional, Union, Any

console = Console()

class PingSweeper:
    def __init__(self, timeout: float = 1.0, retry_count: int = 2,  packet_size: int = 56, dns_lookup: bool = False, rate_limit: float = 0.01, max_threads: int = 100, ipv6_support: bool = True, verbose: bool = False):
        self.timeout = timeout
        self.retry_count = retry_count
        self.packet_size = packet_size
        self.dns_lookup = dns_lookup
        self.rate_limit = rate_limit
        self.max_threads = max_threads
        self.ipv6_support = ipv6_support
        self.verbose = verbose
        self.system = platform.system().lower()
    
    def get_ping_command(self, ip: str) -> List[str]:
        is_ipv6 = ':' in ip
        
        if self.system == "windows": #windows
            cmd = ["ping"]
            if is_ipv6:
                cmd.append("-6")
            cmd.extend([
                "-n", "1",                              # Send only one packet
                "-w", str(int(self.timeout * 1000)),    # Timeout in ms
                "-l", str(self.packet_size),            # Packet size
                str(ip)
            ])
        elif self.system == "darwin":  # macos
            cmd = ["ping"]
            if is_ipv6:
                cmd.append("-6")
            cmd.extend([
                "-c", "1",
                "-W", str(self.timeout),
                "-s", str(self.packet_size),
                str(ip)
            ])
        else:  # Linux and others
            cmd = ["ping"]
            if is_ipv6:
                cmd = ["ping6"] if "ping6" in subprocess.run(["which", "ping6"], 
                                                            stdout=subprocess.PIPE, 
                                                            stderr=subprocess.PIPE).stdout.decode() else ["ping", "-6"]
            cmd.extend([
                "-c", "1",
                "-W", str(self.timeout),
                "-s", str(self.packet_size),
                str(ip)
            ])
        
        return cmd
    
    def parse_ping_output(self, output: str, system: str) -> Optional[float]:
        try:
            if system == "windows":
                # Windows format: "Reply from 192.168.1.1: bytes=32 time=4ms TTL=64"
                match = re.search(r'time=(\d+)ms', output)
                if match:
                    return float(match.group(1)) / 1000
            else:
                # Unix format: "64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.123 ms"
                match = re.search(r'time=([\d.]+) ms', output)
                if match:
                    return float(match.group(1)) / 1000
            
            return None
        except (ValueError, AttributeError):
            return None
    
    def get_hostname(self, ip: str) -> Optional[str]:
        """
        Perform reverse DNS lookup for an IP.
        
        Args:
            ip (str): IP address to look up
            
        Returns:
            Optional[str]: Hostname or None if lookup failed
        """
        if not self.dns_lookup:
            return None
        
        try:
            return socket.getfqdn(ip)
        except (socket.error, socket.herror, socket.gaierror):
            return None
    
    def ping_host(self, ip: str) -> Tuple[str, bool, Optional[float], str, Optional[str]]:
        """
        Ping a single host with retry logic.
        
        Args:
            ip (str): IP address to ping
            
        Returns:
            Tuple: (ip, is_up, rtt, timestamp, hostname)
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        hostname = self.get_hostname(ip) if self.dns_lookup else None
        
        # Initial try
        is_up, rtt = self._attempt_ping(ip)
        
        # Retry logic
        if not is_up and self.retry_count > 0:
            for _ in range(self.retry_count):
                time.sleep(0.5)
                retry_up, retry_rtt = self._attempt_ping(ip)
                if retry_up:
                    is_up, rtt = True, retry_rtt
                    break
        
        return str(ip), is_up, rtt, timestamp, hostname
    
    def _attempt_ping(self, ip: str) -> Tuple[bool, Optional[float]]:
        cmd = self.get_ping_command(ip)
        
        try:
            # Using timeout parameter for subprocess to prevent hanging
            start_time = time.time()
            result = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=self.timeout + 1  # Add a small buffer to subprocess timeout
            )
            elapsed = time.time() - start_time
            
            # Parse output if successful
            if result.returncode == 0:
                output = result.stdout.decode()
                rtt = self.parse_ping_output(output, self.system)
                
                # If we couldn't parse RTT from output, use our measured time as fallback
                if rtt is None:
                    rtt = elapsed
                
                return True, rtt
            
            return False, None
            
        except subprocess.TimeoutExpired:
            if self.verbose:
                console.print(f"[yellow][!] Timeout while pinging {ip}[/yellow]")
            return False, None
        except Exception as e:
            if self.verbose:
                console.print(f"[red][!] Error pinging {ip}: {str(e)}[/red]")
            return False, None
    
    def _format_result(self, ip: str, is_up: bool, rtt: Optional[float], 
                      timestamp: str, hostname: Optional[str]) -> Text:
        line = Text()

        # IP
        line.append(f"{ip:<15}", style="bold yellow")
        
        # Hostname (if available)
        if hostname and hostname != ip:
            line.append(f" ({hostname:<30})", style="blue")
        elif self.dns_lookup:
            line.append(" " + " " * 32, style="")
            
        line.append(" | ")

        # Status
        if is_up:
            line.append("UP  ", style="green bold")
        else:
            line.append("DOWN", style="red bold")

        line.append(" | ")

        # RTT
        if rtt is not None:
            line.append(f"{round(rtt * 1000, 2):<7} ms", style="cyan")
        else:
            line.append("N/A     ", style="grey50")

        line.append(" | ")

        # Timestamp
        line.append(timestamp, style="grey70")

        return line
    
    def validate_subnet(self, subnet: str) -> bool:
        try:
            if not self.ipv6_support and ':' in subnet:
                console.print(f"[yellow][+] IPv6 support is disabled, skipping {subnet}[/yellow]")
                return False
                
            ipaddress.ip_network(subnet, strict=False)
            return True
        except ValueError:
            console.print(f"[red][!] Invalid subnet format: {subnet}[/red]")
            return False
    
    def sweep(self, subnets: List[str]) -> Dict[str, List[Tuple]]:
        # Filter valid subnets
        valid_subnets = [s for s in subnets if self.validate_subnet(s)]
        if not valid_subnets:
            console.print("[red]No valid subnets to scan![/red]")
            return {}
            
        all_results = {}
        
        with Progress() as progress:
            for subnet in valid_subnets:
                network = ipaddress.ip_network(subnet, strict=False)
                hosts = list(network.hosts())
                
                # Handle empty networks (single IP address)
                if not hosts and network.num_addresses == 1:
                    hosts = [network.network_address]
                
                total_hosts = len(hosts)
                console.print(f"\n[bold][+] Scanning {subnet} ({total_hosts} hosts)[/bold]")
                
                #create progress bar
                task_id = progress.add_task(f"[green]Scanning {subnet}", total=total_hosts)
                
                #resualts for this subnet
                subnet_results = []
                completed = 0
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=min(self.max_threads, total_hosts)) as executor:
                    futures = {}
                    
                    #submit all tasks
                    for ip in hosts:
                        future = executor.submit(self.ping_host, str(ip))
                        futures[future] = str(ip)
                        time.sleep(self.rate_limit)  # Rate limiting
                    
                    #process results
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            result = future.result()
                            subnet_results.append(result)
                        except Exception as e:
                            ip = futures[future]
                            console.print(f"[red]Error processing {ip}: {str(e)}[/red]")
                            #add a failure entry
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                            subnet_results.append((ip, False, None, timestamp, None))
                        
                        #update progress
                        completed += 1
                        progress.update(task_id, completed=completed)
                
                #sort results by IP address
                subnet_results.sort(key=lambda x: [int(i) for i in x[0].split('.')] if '.' in x[0] else x[0])
                all_results[subnet] = subnet_results
        
        self._display_results(all_results)
        
        return all_results
    
    def _display_results(self, all_results: Dict[str, List[Tuple]]) -> None:
        """
        Display formatted results for all subnets.
        
        Args:
            all_results (Dict[str, List[Tuple]]): Results organized by subnet
        """
        for subnet, results in all_results.items():
            console.print(f"\n[bold]--- Ping Sweep Results for {subnet} ---[/bold]")
            
            total = len(results)
            up_count = sum(1 for r in results if r[1])
            
            # Calculate statistics
            rtts = [r[2] for r in results if r[1] and r[2] is not None]
            avg_rtt = sum(rtts) / len(rtts) if rtts else 0
            min_rtt = min(rtts) if rtts else 0
            max_rtt = max(rtts) if rtts else 0
            
            # Print stats header
            console.print(f"[bold green]Hosts up: {up_count}/{total} ({up_count/total*100:.1f}%)[/bold green]")
            if rtts:
                console.print(
                    f"[bold blue]RTT stats: min={min_rtt*1000:.2f}ms, "
                    f"avg={avg_rtt*1000:.2f}ms, max={max_rtt*1000:.2f}ms[/bold blue]"
                )
            
            # Print host details
            console.print("[bold]IP Address      Status  RTT          Timestamp[/bold]")
            console.print("=" * 100)
            
            for result in results:
                console.print(self._format_result(*result))


def ping_sweep(
    subnets: List[str], 
    timeout: float = 1, 
    max_threads: int = 100,
    retry_count: int = 1,
    packet_size: int = 56,
    dns_lookup: bool = False,
    rate_limit: float = 0.01,
    ipv6_support: bool = True,
    verbose: bool = False
) -> Dict[str, List[Tuple]]:
    sweeper = PingSweeper(
        timeout=timeout,
        retry_count=retry_count,
        packet_size=packet_size,
        dns_lookup=dns_lookup,
        rate_limit=rate_limit,
        max_threads=max_threads,
        ipv6_support=ipv6_support,
        verbose=verbose
    )
    
    return sweeper.sweep(subnets)