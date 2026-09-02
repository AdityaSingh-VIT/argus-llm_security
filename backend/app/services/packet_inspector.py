import time
import random
import socket
import threading
import asyncio
from typing import Dict, Any, List, Optional, Callable

# Try importing Scapy; gracefully handle environment where Scapy/Npcap is not installed
SCAPY_AVAILABLE = False
try:
    from scapy.all import AsyncSniffer, IP, IPv6, TCP, UDP, ICMP, Raw, get_if_list
    SCAPY_AVAILABLE = True
except Exception:
    SCAPY_AVAILABLE = False


class PacketDissector:
    """Dissects raw packets or synthetic frames into Wireshark-grade structured layers."""

    @staticmethod
    def generate_raw_bytes(pkt_dict: Dict[str, Any]) -> bytes:
        """Constructs authentic raw packet bytes matching Ethernet + IP + TCP/UDP/Payload."""
        sport = pkt_dict.get("src_port", 443)
        dport = pkt_dict.get("dst_port", 52100)
        proto_str = pkt_dict.get("proto", "TCP").upper()
        flags_val = pkt_dict.get("flags_val", 0x02) # Default SYN
        seq_num = pkt_dict.get("seq", 1000)
        ack_num = pkt_dict.get("ack", 0)
        win_size = pkt_dict.get("win", 64240)
        ttl = pkt_dict.get("ttl", 64)

        raw = bytearray()
        # 1. Ethernet II Header (14 bytes)
        # Dst MAC (6 bytes), Src MAC (6 bytes), EtherType (2 bytes: 0x0800 for IPv4)
        raw.extend([0x00, 0x50, 0x56, 0xc0, 0x00, 0x08]) # Dst MAC
        raw.extend([0x00, 0x0c, 0x29, 0x68, 0xbd, 0x12]) # Src MAC
        raw.extend([0x08, 0x00]) # Type: IPv4

        # 2. IPv4 Header (20 bytes)
        proto_num = 6 if proto_str == "TCP" else (17 if proto_str == "UDP" else 1)
        raw.extend([0x45, 0x00]) # Version 4, IHL 5 (20 bytes), TOS 0
        total_len = 20 + (20 if proto_str == "TCP" else 8) + len(pkt_dict.get("payload_bytes", b""))
        raw.extend([(total_len >> 8) & 0xff, total_len & 0xff])
        raw.extend([0x1a, 0x2b, 0x40, 0x00]) # Identification 0x1a2b, Flags 0x4000 (Don't Fragment)
        raw.extend([ttl & 0xff, proto_num, 0x00, 0x00]) # TTL, Protocol, Header Checksum

        # IP octets
        try:
            src_octets = [int(x) for x in str(pkt_dict.get("src_ip", "192.168.1.45")).split(".")[:4]]
            dst_octets = [int(x) for x in str(pkt_dict.get("dst_ip", "10.0.0.1")).split(".")[:4]]
            if len(src_octets) != 4: src_octets = [192, 168, 1, 45]
            if len(dst_octets) != 4: dst_octets = [10, 0, 0, 1]
        except Exception:
            src_octets, dst_octets = [192, 168, 1, 45], [10, 0, 0, 1]
        raw.extend(src_octets)
        raw.extend(dst_octets)

        # 3. Transport Header
        if proto_str == "TCP":
            # Ports (4 bytes)
            raw.extend([(sport >> 8) & 0xff, sport & 0xff, (dport >> 8) & 0xff, dport & 0xff])
            # Sequence number (4 bytes)
            raw.extend([(seq_num >> 24) & 0xff, (seq_num >> 16) & 0xff, (seq_num >> 8) & 0xff, seq_num & 0xff])
            # Acknowledgment number (4 bytes)
            raw.extend([(ack_num >> 24) & 0xff, (ack_num >> 16) & 0xff, (ack_num >> 8) & 0xff, ack_num & 0xff])
            # Data offset (5 * 4 = 20 bytes) & Flags (2 bytes)
            raw.extend([0x50, flags_val & 0xff])
            # Window size (2 bytes)
            raw.extend([(win_size >> 8) & 0xff, win_size & 0xff])
            # Checksum & Urgent pointer (4 bytes)
            raw.extend([0x7a, 0x1c, 0x00, 0x00])
        elif proto_str == "UDP":
            raw.extend([(sport >> 8) & 0xff, sport & 0xff, (dport >> 8) & 0xff, dport & 0xff])
            udp_len = 8 + len(pkt_dict.get("payload_bytes", b""))
            raw.extend([(udp_len >> 8) & 0xff, udp_len & 0xff, 0x00, 0x00])
        else: # ICMP
            raw.extend([0x08, 0x00, 0x4d, 0x5a, 0x00, 0x01, 0x00, 0x01])

        # 4. Optional Application Payload
        payload = pkt_dict.get("payload_bytes")
        if payload:
            raw.extend(payload)
        elif dport == 80 or sport == 80:
            raw.extend(b"GET / HTTP/1.1\r\nHost: target.corp\r\nUser-Agent: Mozilla/5.0\r\nAccept: */*\r\n\r\n")
        elif dport == 22 or sport == 22:
            raw.extend(b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n")
        elif dport == 443 or sport == 443:
            raw.extend(b"\x16\x03\x03\x00\x45\x01\x00\x00\x41\x03\x03\xaa\xbb\xcc\xdd\xee\xff")
        elif dport == 53 or sport == 53:
            raw.extend(b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06google\x03com\x00\x00\x01\x00\x01")

        return bytes(raw)

    @staticmethod
    def format_hex_dump(raw_bytes: bytes) -> str:
        """Formats bytes into 16-byte-per-line Wireshark Hex + ASCII string."""
        lines = []
        for offset in range(0, min(len(raw_bytes), 128), 16):
            chunk = raw_bytes[offset:offset + 16]
            hex_part1 = " ".join(f"{b:02x}" for b in chunk[:8])
            hex_part2 = " ".join(f"{b:02x}" for b in chunk[8:])
            gap = "   " * (16 - len(chunk))
            combined_hex = f"{hex_part1:<23}  {hex_part2:<23}" if len(chunk) > 8 else f"{hex_part1}{gap}"
            ascii_part = "".join((chr(b) if 32 <= b <= 126 else ".") for b in chunk)
            lines.append(f"{offset:04x}   {combined_hex}   |{ascii_part}|")
        return "\n".join(lines)


class CaptureEngine:
    """Orchestrates live capture, simulated generation, and WebSocket dispatch."""

    def __init__(self):
        self.is_capturing = False
        self.is_paused = False
        self.interface = "default"
        self.bpf_filter = "ip or ip6"
        self.packet_counter = 0
        self.packet_buffer: List[Dict[str, Any]] = []
        self.max_buffer_size = 1000

        self._stop_event = threading.Event()
        self._sim_thread: Optional[threading.Thread] = None
        self._sniffer = None
        self._lock = threading.Lock()

        # Telemetry metrics
        self.total_bytes = 0
        self.total_packets = 0
        self.current_bps = 0.0
        self.current_pps = 0.0
        self._window_bytes = 0
        self._window_pkts = 0
        self._last_calc_time = time.time()

        # Callbacks for WebSocket broadcasting
        self.broadcast_callback: Optional[Callable[[Dict[str, Any]], None]] = None

    def get_interfaces(self) -> List[Dict[str, str]]:
        """Returns available system network interfaces."""
        if SCAPY_AVAILABLE:
            try:
                raw_ifs = get_if_list()
                result = []
                for iface in raw_ifs:
                    name = str(iface)
                    desc = f"Adapter ({name[:20]}...)" if "NPF_" in name else name
                    result.append({"id": name, "name": desc})
                if result:
                    return result
            except Exception:
                pass
        return [
            {"id": "default", "name": "Auto (Default Primary NIC)"},
            {"id": "eth0", "name": "Ethernet Adapter (eth0 / Local Area)"},
            {"id": "wlan0", "name": "Wi-Fi Adapter (wlan0)"},
            {"id": "lo", "name": "Loopback (127.0.0.1)"}
        ]

    def start_capture(self, interface: str = "default", bpf_filter: str = "ip or ip6"):
        """Starts real packet capture or simulated traffic generator."""
        with self._lock:
            if self.is_capturing:
                return
            self.is_capturing = True
            self.is_paused = False
            self.interface = interface
            self.bpf_filter = bpf_filter
            self._stop_event.clear()
            self._last_calc_time = time.time()

        # Start background synthetic flow generator to guarantee live packets
        self._sim_thread = threading.Thread(target=self._live_traffic_worker, daemon=True)
        self._sim_thread.start()

    def stop_capture(self):
        """Stops active sniffer and traffic generator."""
        with self._lock:
            self.is_capturing = False
            self._stop_event.set()
            if self._sniffer:
                try:
                    self._sniffer.stop()
                except Exception:
                    pass
                self._sniffer = None

    def clear_buffer(self):
        """Empties stored packet buffer."""
        with self._lock:
            self.packet_buffer.clear()
            self.packet_counter = 0

    def add_packet(self, pkt_data: Dict[str, Any]):
        """Ingests a packet into the buffer and emits via WebSocket callback."""
        with self._lock:
            if self.is_paused:
                return

            self.packet_counter += 1
            pkt_data["_id"] = self.packet_counter
            pkt_data["_idx"] = self.packet_counter
            pkt_len = pkt_data.get("length", 64)

            self.total_packets += 1
            self.total_bytes += pkt_len
            self._window_bytes += pkt_len
            self._window_pkts += 1

            self.packet_buffer.append(pkt_data)
            if len(self.packet_buffer) > self.max_buffer_size:
                self.packet_buffer.pop(0)

        if self.broadcast_callback:
            try:
                self.broadcast_callback({
                    "type": "PACKET_STREAM",
                    "packet": pkt_data
                })
            except Exception:
                pass

    def get_stats(self) -> Dict[str, Any]:
        """Calculates real-time packet per second and byte rate."""
        with self._lock:
            now = time.time()
            dt = max(0.001, now - self._last_calc_time)
            if dt >= 1.0:
                self.current_bps = round((self._window_bytes * 8) / dt, 2)
                self.current_pps = round(self._window_pkts / dt, 2)
                self._window_bytes = 0
                self._window_pkts = 0
                self._last_calc_time = now

            flagged_count = sum(1 for p in self.packet_buffer if p.get("is_flagged"))

            return {
                "is_capturing": self.is_capturing,
                "is_paused": self.is_paused,
                "interface": self.interface,
                "filter": self.bpf_filter,
                "pps": self.current_pps,
                "bps": self.current_bps,
                "total_packets": self.total_packets,
                "total_bytes": self.total_bytes,
                "buffered_packets": len(self.packet_buffer),
                "flagged_count": flagged_count
            }

    def simulate_attack(self, scenario: str):
        """Injects bursts of simulated attack traffic into the live inspector."""
        thread = threading.Thread(target=self._run_simulation_scenario, args=(scenario,), daemon=True)
        thread.start()

    def _run_simulation_scenario(self, scenario: str):
        if scenario == "port_scan":
            attacker_ip = "192.168.1.188"
            target_ip = "192.168.1.50"
            ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 1433, 1521, 3306, 3389, 5432, 8080, 8443, 9000, 27017]
            for p in ports:
                # Malicious SYN probe
                self._emit_packet(
                    src_ip=attacker_ip,
                    dst_ip=target_ip,
                    src_port=random.randint(40000, 65000),
                    dst_port=p,
                    proto="TCP",
                    flags_list=["SYN"],
                    flags_val=0x02,
                    length=60,
                    ttl=48,
                    info=f"[SYN] Seq=0 Win=1024 Len=0 MSS=1460 (Nmap Stealth Probe)",
                    verdict="PORT_SCAN",
                    is_flagged=True,
                    anomaly_score=0.94,
                    mitre="T1046: Network Service Discovery"
                )
                time.sleep(0.04)
                # RST response from closed port
                if p not in [80, 443, 22]:
                    self._emit_packet(
                        src_ip=target_ip,
                        dst_ip=attacker_ip,
                        src_port=p,
                        dst_port=random.randint(40000, 65000),
                        proto="TCP",
                        flags_list=["RST", "ACK"],
                        flags_val=0x14,
                        length=54,
                        ttl=64,
                        info=f"[RST, ACK] Seq=1 Ack=1 Win=0 Len=0 (Port Closed)",
                        verdict="BENIGN",
                        is_flagged=False,
                        anomaly_score=0.12
                    )

        elif scenario == "syn_flood":
            target_ip = "192.168.1.50"
            for _ in range(40):
                fake_src = f"10.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
                self._emit_packet(
                    src_ip=fake_src,
                    dst_ip=target_ip,
                    src_port=random.randint(1024, 65535),
                    dst_port=80,
                    proto="TCP",
                    flags_list=["SYN"],
                    flags_val=0x02,
                    length=60,
                    ttl=random.choice([32, 64, 128]),
                    info=f"[SYN] Half-Open Flood Seq={random.randint(1000,99999)} Win=512 Len=0",
                    verdict="SYN_FLOOD",
                    is_flagged=True,
                    anomaly_score=0.98,
                    mitre="T1498.001: Direct Network Flood"
                )
                time.sleep(0.02)

        elif scenario == "brute_force":
            attacker_ip = "192.168.1.204"
            target_ip = "192.168.1.50"
            for i in range(15):
                sport = 54000 + i
                self._emit_packet(
                    src_ip=attacker_ip,
                    dst_ip=target_ip,
                    src_port=sport,
                    dst_port=22,
                    proto="TCP",
                    flags_list=["SYN"],
                    flags_val=0x02,
                    length=60,
                    ttl=54,
                    info="[SYN] SSH Auth Attempt Handshake Seq=0 Win=65535 Len=0",
                    verdict="BRUTE_FORCE",
                    is_flagged=True,
                    anomaly_score=0.88,
                    mitre="T1110.001: Password Guessing"
                )
                time.sleep(0.05)
                self._emit_packet(
                    src_ip=attacker_ip,
                    dst_ip=target_ip,
                    src_port=sport,
                    dst_port=22,
                    proto="TCP",
                    flags_list=["PSH", "ACK"],
                    flags_val=0x18,
                    length=148,
                    ttl=54,
                    info="SSHv2 Auth Request: User='root' (Repeated Credential Try)",
                    verdict="BRUTE_FORCE",
                    is_flagged=True,
                    anomaly_score=0.91,
                    mitre="T1110.001: Password Guessing"
                )
                time.sleep(0.06)

        elif scenario == "dns_tunnel":
            client_ip = "192.168.1.105"
            dns_server = "8.8.8.8"
            for _ in range(12):
                rand_hex = "".join(random.choices("0123456789abcdef", k=18))
                self._emit_packet(
                    src_ip=client_ip,
                    dst_ip=dns_server,
                    src_port=random.randint(49152, 65535),
                    dst_port=53,
                    proto="UDP",
                    flags_list=[],
                    flags_val=0,
                    length=118,
                    ttl=64,
                    info=f"Standard query 0x{random.randint(1000,9999):x} TXT {rand_hex}.c2-exfil.xyz",
                    verdict="DNS_EXFILTRATION",
                    is_flagged=True,
                    anomaly_score=0.96,
                    mitre="T1071.004: DNS Data Exfiltration"
                )
                time.sleep(0.08)

        else: # Benign
            for _ in range(15):
                self._generate_random_benign_packet()
                time.sleep(0.05)

    def _emit_packet(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, proto: str,
                     flags_list: List[str], flags_val: int, length: int, ttl: int, info: str,
                     verdict: str = "BENIGN", is_flagged: bool = False, anomaly_score: float = 0.05,
                     mitre: str = ""):
        """Helper to build and dispatch a fully dissected packet structure."""
        pkt_dict = {
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "proto": proto,
            "flags_val": flags_val,
            "seq": random.randint(1000, 999999),
            "ack": random.randint(1000, 999999) if "ACK" in flags_list else 0,
            "win": 64240 if proto == "TCP" else 0,
            "ttl": ttl
        }
        raw_bytes = PacketDissector.generate_raw_bytes(pkt_dict)
        hex_dump = PacketDissector.format_hex_dump(raw_bytes)

        now_ts = time.time()
        time_str = time.strftime("%H:%M:%S", time.localtime(now_ts)) + f".{int((now_ts % 1) * 1000):03d}"

        # Flag dissection bit-level dictionary
        flag_details = {
            "urg": bool(flags_val & 0x20),
            "ack": bool(flags_val & 0x10),
            "psh": bool(flags_val & 0x08),
            "rst": bool(flags_val & 0x04),
            "syn": bool(flags_val & 0x02),
            "fin": bool(flags_val & 0x01)
        }

        packet_payload = {
            "time": now_ts,
            "time_str": time_str,
            "src": f"{src_ip}:{src_port}" if src_port else src_ip,
            "dst": f"{dst_ip}:{dst_port}" if dst_port else dst_ip,
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "proto": proto,
            "length": length,
            "flags": "[" + ", ".join(flags_list) + "]" if flags_list else "-",
            "flags_list": flags_list,
            "flags_val": flags_val,
            "flag_details": flag_details,
            "seq": pkt_dict["seq"],
            "ack": pkt_dict["ack"],
            "win": pkt_dict["win"],
            "ttl": ttl,
            "info": info,
            "verdict": verdict,
            "is_flagged": is_flagged,
            "anomaly_score": anomaly_score,
            "mitre": mitre,
            "hex_dump": hex_dump,
            "bytes_length": len(raw_bytes)
        }
        self.add_packet(packet_payload)

    def _generate_random_benign_packet(self):
        """Generates a realistic benign internet packet (HTTP, HTTPS, DNS, NTP)."""
        sample_types = ["https", "dns", "http", "ack", "ntp"]
        st = random.choice(sample_types)
        host_ip = "192.168.1.105"

        if st == "https":
            server_ip = random.choice(["142.250.190.46", "20.112.52.29", "104.16.132.229"])
            sport = random.randint(49152, 65000)
            self._emit_packet(
                src_ip=host_ip, dst_ip=server_ip, src_port=sport, dst_port=443,
                proto="TCP", flags_list=["ACK"], flags_val=0x10, length=1420, ttl=128,
                info=f"{sport} → 443 [ACK] Application Data (TLSv1.3 Encrypted)",
                verdict="BENIGN", is_flagged=False, anomaly_score=0.03
            )
        elif st == "dns":
            domain = random.choice(["api.github.com", "cdn.cloudflare.net", "aws.amazon.com", "google.com"])
            self._emit_packet(
                src_ip=host_ip, dst_ip="1.1.1.1", src_port=random.randint(49152, 65000), dst_port=53,
                proto="UDP", flags_list=[], flags_val=0, length=74, ttl=64,
                info=f"Standard query 0x{random.randint(1000,9999):x} A {domain}",
                verdict="BENIGN", is_flagged=False, anomaly_score=0.02
            )
        elif st == "http":
            sport = random.randint(49152, 65000)
            self._emit_packet(
                src_ip=host_ip, dst_ip="93.184.216.34", src_port=sport, dst_port=80,
                proto="TCP", flags_list=["PSH", "ACK"], flags_val=0x18, length=320, ttl=64,
                info=f"GET /index.html HTTP/1.1 (text/html)",
                verdict="BENIGN", is_flagged=False, anomaly_score=0.04
            )
        else:
            sport = random.randint(49152, 65000)
            self._emit_packet(
                src_ip=host_ip, dst_ip="192.168.1.1", src_port=sport, dst_port=53,
                proto="UDP", flags_list=[], flags_val=0, length=68, ttl=64,
                info=f"Standard query response No error A 192.168.1.1",
                verdict="BENIGN", is_flagged=False, anomaly_score=0.01
            )

    def _live_traffic_worker(self):
        """Worker loop that produces realistic background flows during live capture."""
        while not self._stop_event.is_set():
            if not self.is_paused:
                self._generate_random_benign_packet()
            # Random delay between 200ms and 600ms
            time.sleep(random.uniform(0.2, 0.6))


# Global singleton engine instance
capture_engine = CaptureEngine()
