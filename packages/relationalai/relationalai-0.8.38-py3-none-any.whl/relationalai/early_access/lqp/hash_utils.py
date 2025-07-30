import hashlib

"""
Hashes an LQP node to a 128-bit integer.
"""
def lqp_hash(node) -> int:
    return hash_to_uint128(_lqp_hash_fn(node))

# TODO: this is NOT a good hash its just to get things working for now to get a stable id.
def _lqp_hash_fn(node) -> int:
    return int.from_bytes(hashlib.sha256(str(node).encode()).digest(), byteorder='big', signed=False)

def hash_to_uint128(h: int) -> int:
    return h % (2**128)  # Ensure it's within the 128-bit range
