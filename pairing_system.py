def has_keys(obj, keys):
    return all(stream in obj for stream in keys)


class PairingSystem:
    def __init__(self, allowed_instances):
        self.seq_packets = {}
        self.last_paired_seq = None
        self.allowed_instances = allowed_instances

    def add_packet(self, packet):
        if packet is not None and packet.getInstanceNum() in self.allowed_instances:
            seq_key = packet.getSequenceNum()
            self.seq_packets[seq_key] = {
                **self.seq_packets.get(seq_key, {}),
                packet.getInstanceNum(): packet,
            }

    def get_pairs(self):
        results = []
        for key in list(self.seq_packets.keys()):
            if has_keys(self.seq_packets[key], self.allowed_instances):
                results.append(self.seq_packets[key])
                self.last_paired_seq = key
        if len(results) > 0:
            self.collect_garbage()
        return results

    def collect_garbage(self):
        for key in list(self.seq_packets.keys()):
            if key <= self.last_paired_seq:
                del self.seq_packets[key]
