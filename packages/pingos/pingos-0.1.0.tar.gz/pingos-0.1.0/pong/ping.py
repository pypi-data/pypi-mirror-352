import socket
import time
from typing import Tuple, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table

@dataclass
class PingResult:
    """Result of a single ping attempt"""
    success: bool
    rtt: float
    error: Optional[str] = None

class PortPing:
    def __init__(self, host: str, port: int, timeout: float = 1.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.console = Console()
        self.stats = {
            'transmitted': 0,
            'received': 0,
            'min_rtt': float('inf'),
            'max_rtt': 0,
            'total_rtt': 0
        }

    def tcp_ping(self) -> PingResult:
        """Perform a TCP ping to the specified host and port"""
        start_time = time.time()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
                rtt = (time.time() - start_time) * 1000  # Convert to milliseconds
                return PingResult(success=True, rtt=rtt)
        except socket.timeout:
            return PingResult(success=False, rtt=0, error="Connection timed out")
        except ConnectionRefusedError:
            return PingResult(success=False, rtt=0, error="Connection refused")
        except Exception as e:
            return PingResult(success=False, rtt=0, error=str(e))

    def udp_ping(self) -> PingResult:
        """Perform a UDP ping to the specified host and port"""
        start_time = time.time()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(self.timeout)
                sock.sendto(b"", (self.host, self.port))
                try:
                    data, _ = sock.recvfrom(1024)
                    rtt = (time.time() - start_time) * 1000  # Convert to milliseconds
                    return PingResult(success=True, rtt=rtt)
                except socket.timeout:
                    # For UDP, timeout might not mean failure
                    return PingResult(success=True, rtt=self.timeout * 1000)
        except Exception as e:
            return PingResult(success=False, rtt=0, error=str(e))

    def update_stats(self, result: PingResult) -> None:
        """Update ping statistics"""
        self.stats['transmitted'] += 1
        if result.success:
            self.stats['received'] += 1
            self.stats['min_rtt'] = min(self.stats['min_rtt'], result.rtt)
            self.stats['max_rtt'] = max(self.stats['max_rtt'], result.rtt)
            self.stats['total_rtt'] += result.rtt

    def print_stats(self) -> None:
        """Print final statistics"""
        if self.stats['transmitted'] == 0:
            return

        loss_rate = ((self.stats['transmitted'] - self.stats['received']) / 
                    self.stats['transmitted'] * 100)
        
        if self.stats['received'] > 0:
            avg_rtt = self.stats['total_rtt'] / self.stats['received']
            self.console.print(f"\n--- {self.host}:{self.port} ping statistics ---")
            self.console.print(
                f"{self.stats['transmitted']} packets transmitted, "
                f"{self.stats['received']} received, "
                f"{loss_rate:.1f}% packet loss"
            )
            self.console.print(
                f"rtt min/avg/max = {self.stats['min_rtt']:.3f}/"
                f"{avg_rtt:.3f}/{self.stats['max_rtt']:.3f} ms"
            )

    def ping(self, protocol: str, count: Optional[int] = None) -> None:
        """Perform pings and display results"""
        self.console.print(f"PING {self.host}:{self.port} ({self.host})")
        
        try:
            packet_num = 1
            while count is None or packet_num <= count:
                if protocol.lower() == "tcp":
                    result = self.tcp_ping()
                else:
                    result = self.udp_ping()
                
                self.update_stats(result)
                
                if result.success:
                    self.console.print(
                        f"{len(str(self.stats['transmitted']))} bytes from "
                        f"{self.host}:{self.port}: time={result.rtt:.3f}ms"
                    )
                else:
                    self.console.print(
                        f"Request timeout for icmp_seq {packet_num}"
                    )
                
                packet_num += 1
                time.sleep(1)  # Wait 1 second between pings
                
        except KeyboardInterrupt:
            self.console.print("\n")
            self.print_stats()
            return
        
        self.print_stats() 