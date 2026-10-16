"""A from-scratch proof-of-work blockchain for tamper-proof certificates."""
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def merkle_root(hashes):
    """Pairwise-hash leaves up to a single root (duplicates last leaf on odd levels)."""
    if not hashes:
        return sha256("")
    level = list(hashes)
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [sha256(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]


def certificate_id(cert: dict) -> str:
    canonical = json.dumps({k: cert[k] for k in sorted(cert) if k != "cert_id"}, sort_keys=True)
    return sha256(canonical)


@dataclass
class Block:
    index: int
    timestamp: float
    certificates: list
    previous_hash: str
    difficulty: int = 3
    nonce: int = 0
    merkle: str = ""
    hash: str = ""
    mine_seconds: float = 0.0

    def header(self) -> str:
        return f"{self.index}|{self.timestamp}|{self.merkle}|{self.previous_hash}|{self.difficulty}|{self.nonce}"

    def compute_hash(self) -> str:
        return sha256(self.header())

    def mine(self):
        self.merkle = merkle_root([c["cert_id"] for c in self.certificates])
        target, start = "0" * self.difficulty, time.perf_counter()
        self.nonce = 0
        self.hash = self.compute_hash()
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()
        self.mine_seconds = time.perf_counter() - start
        return self


@dataclass
class Blockchain:
    difficulty: int = 3
    chain: list = field(default_factory=list)
    pending: list = field(default_factory=list)

    def __post_init__(self):
        if not self.chain:
            genesis = Block(0, time.time(), [{"cert_id": sha256("genesis"), "note": "Genesis block"}], "0" * 64, self.difficulty)
            self.chain.append(genesis.mine())

    # ---- issuing -------------------------------------------------------
    def add_certificate(self, **fields) -> str:
        cert = dict(fields)
        cert["cert_id"] = certificate_id(cert)
        self.pending.append(cert)
        return cert["cert_id"]

    def mine_pending(self):
        if not self.pending:
            return None
        blk = Block(len(self.chain), time.time(), self.pending, self.chain[-1].hash, self.difficulty).mine()
        self.chain.append(blk)
        self.pending = []
        return blk

    # ---- verification --------------------------------------------------
    def validate(self):
        """Return list of (index, ok, reason) for every block."""
        out = []
        for i, b in enumerate(self.chain):
            if b.merkle != merkle_root([c["cert_id"] for c in b.certificates]):
                out.append((i, False, "Merkle root mismatch — certificate data altered"))
            elif any(c.get("note") != "Genesis block" and c["cert_id"] != certificate_id(c) for c in b.certificates):
                out.append((i, False, "Certificate fields do not match their ID"))
            elif b.hash != b.compute_hash():
                out.append((i, False, "Block hash invalid"))
            elif not b.hash.startswith("0" * b.difficulty):
                out.append((i, False, "Proof-of-work not satisfied"))
            elif i > 0 and b.previous_hash != self.chain[i - 1].hash:
                out.append((i, False, "Broken link to previous block"))
            else:
                out.append((i, True, "Valid"))
        return out

    def is_valid(self):
        return all(ok for _, ok, _ in self.validate())

    def find(self, cert_id: str):
        for b in self.chain:
            for c in b.certificates:
                if c["cert_id"] == cert_id:
                    return b, c
        return None, None

    # ---- persistence ---------------------------------------------------
    def to_json(self) -> str:
        return json.dumps({"difficulty": self.difficulty, "chain": [asdict(b) for b in self.chain]}, indent=2)

    @classmethod
    def from_json(cls, text: str):
        d = json.loads(text)
        bc = cls.__new__(cls)
        bc.difficulty, bc.pending = d["difficulty"], []
        bc.chain = [Block(**b) for b in d["chain"]]
        return bc
