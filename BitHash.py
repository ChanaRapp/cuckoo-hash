import random

_MAX_HASHES = 1000
_MASK64 = 0xffffffffffffffff
_BASE_SEED = "BitHash random numbers"

# Current hash-family number. Each reset advances to a new family.
_family_num = 0

# RNG and cached byte tables for the current family.
_rnd = None
_bits = None


def _init_family():
    global _rnd, _bits
    _rnd = random.Random(f"{_BASE_SEED}:{_family_num}")
    _bits = [None] * _MAX_HASHES


def _getBits(num):
    global _bits

    if num < 0:
        raise ValueError("hashFuncNum must be >= 1")
    if num >= _MAX_HASHES:
        raise ValueError(f"hashFuncNum must be <= {_MAX_HASHES}")

    # Create tables lazily, but in order, so behavior is deterministic.
    if _bits[num] is None:
        for n in range(num + 1):
            if _bits[n] is None:
                _bits[n] = [_rnd.getrandbits(64) for _ in range(256)]

    return _bits[num]

"""
Hash a Python string into a 64-bit unsigned integer.

Parameters
----------
s : str
    The string to hash.
hashFuncNum : int
    Selects which hash function from the current family to use.
    Must be >= 1 and <= _MAX_HASHES.

Returns
-------
int
    A 64-bit unsigned integer in the range 0 .. 2^64 - 1.

Notes
-----
- This is a deterministic, non-cryptographic hash family.
- It is intended for data-structure / algorithmic use such as
  hash tables, Bloom filters and cuckoo hashing.
- It supports all Python strings by hashing their UTF-8 bytes.
"""

def BitHash(s, hashFuncNum=1):

    if not isinstance(s, str):
        raise TypeError("BitHash expects a string")

    bits = _getBits(hashFuncNum - 1)
    
    # turn the string (which could be foreign language) into 
    # a utf-string of bytes
    data = s.encode("utf-8")

    # for each character in the user's string of characters
    #   circularly rotate the hash left by 5 bits
    #   XOR in the random number for the current character
    #   use AND to remove everything but the low 64 bits    
    h = 0
    for b in data:
        h = (((h << 5) | (h >> 59)) ^ bits[b]) & _MASK64

    return h


# Advance to a new family of hash functions.
# After calling this function, subsequent calls to BitHash() use a
# different family of hash functions than before. This is useful for
# rebuilding structures such as cuckoo hash tables when the current
# hash functions lead to insertion cycles.

def ResetBitHash():

    global _family_num
    _family_num += 1
    _init_family()

# Return the current hash-family number.
def GetBitHashFamilyNum():
    return _family_num


# Initialize family 0 on import.
_init_family()


def _main():
    # use BitHash to get two hash values for each of a bunch of strings
    # and print them out.
    v1 = BitHash("foo", 1);  v2 = BitHash("foo", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("bar", 1);  v2 = BitHash("bar", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("baz", 1);  v2 = BitHash("baz", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("blat", 1); v2 = BitHash("blat", 2); print(hex(v1), hex(v2))
    
    # now reset BitHash so that it is effectively 
    # a new family of hash functions, and print out the hash values
    # for the same words.
    print("\nresetting BitHash to a new family of hash functions\n")
    ResetBitHash()
    
    v1 = BitHash("foo", 1);  v2 = BitHash("foo", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("bar", 1);  v2 = BitHash("bar", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("baz", 1);  v2 = BitHash("baz", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("blat", 1); v2 = BitHash("blat", 2); print(hex(v1), hex(v2))

    # now reset BitHash again so that it is effectively 
    # yet another family of hash functions, and print out the hash values
    # for the same words.
    print("\nresetting BitHash to yet another family of hash functions\n")
    ResetBitHash()
    
    v1 = BitHash("foo", 1);  v2 = BitHash("foo", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("bar", 1);  v2 = BitHash("bar", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("baz", 1);  v2 = BitHash("baz", 2);  print(hex(v1), hex(v2))
    v1 = BitHash("blat", 1); v2 = BitHash("blat", 2); print(hex(v1), hex(v2))


 

if __name__ == "__main__":
    _main()