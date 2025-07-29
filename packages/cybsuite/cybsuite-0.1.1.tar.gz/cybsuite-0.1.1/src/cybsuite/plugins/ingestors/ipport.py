from cybsuite.cyberdb import BaseIngestor, Metadata

from .utils import validate_ip_address


class IpportIngestor(BaseIngestor):
    name = "ipport"
    extension = "ip.txt"
    extensions = ["ip.txt", "ipport.txt", "ipportprotocol.txt"]

    metadata = Metadata(
        description="Ingest simple text files containing ip, ip:port (default protocol tcp) or ip:port:protocol"
    )

    def do_run(self, filepath):
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(":")

                ip = parts[0]
                validate_ip_address(ip)

                if len(parts) == 1:
                    self.cyberdb.feed("host", ip=ip)
                elif len(parts) <= 3:
                    port = parts[1]
                    protocol = parts[2] if len(parts) > 2 else "tcp"
                    self.cyberdb.feed("service", host=ip, port=port, protocol=protocol)
                else:
                    raise ValueError(f"Too many parts in line: {line}")
