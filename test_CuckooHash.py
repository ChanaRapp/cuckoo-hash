# test_cuckoohash.py
#
# Black-box pytest suite for CuckooHash
#
# Uses only the public API:
#   CuckooHash(size)
#   insert(key, data)
#   find(key)
#   delete(key)
#   len(table)

import pytest
import random
from CuckooHash import CuckooHash


# ============================================================
# ORACLE MODEL
# ============================================================

class OracleCuckooHash:
    def __init__(self, size):
        self._data = {}

    def __len__(self):
        return len(self._data)

    def insert(self, k, d):
        if k in self._data:
            return False
        self._data[k] = d
        return True

    def find(self, k):
        return self._data.get(k, None)

    def delete(self, k):
        if k in self._data:
            del self._data[k]


# ============================================================
# HELPER
# ============================================================

def compare_with_oracle(real, oracle, keys):
    """Verifies observable state matches oracle."""
    assert len(real) == len(oracle)

    for k in keys:
        assert real.find(k) == oracle.find(k)


# ============================================================
# CATEGORY 1: Constructor / Initial State
# ============================================================

def test_constructor_empty():
    """Fresh table should be empty."""
    h = CuckooHash(10)

    assert len(h) == 0
    assert h.find("x") is None


def test_delete_empty():
    """Deleting from empty table should not change state."""
    h = CuckooHash(10)

    h.delete("ghost")

    assert len(h) == 0
    assert h.find("ghost") is None


# ============================================================
# CATEGORY 2: Single Insert
# ============================================================

def test_single_insert():
    """Single insert should succeed and be retrievable."""
    h = CuckooHash(10)

    assert h.insert("apple", 42) is True
    assert h.find("apple") == 42
    assert len(h) == 1


def test_insert_none_value():
    """Should allow storing None as data."""
    h = CuckooHash(10)

    assert h.insert("k", None) is True
    assert h.find("k") is None
    assert len(h) == 1


# ============================================================
# CATEGORY 3: Duplicate Key Behavior
# ============================================================

def test_duplicate_insert_same_value():
    """Duplicate insert should fail and preserve original."""
    h = CuckooHash(10)

    assert h.insert("cat", 1) is True
    assert h.insert("cat", 1) is False

    assert h.find("cat") == 1
    assert len(h) == 1


def test_duplicate_insert_different_value():
    """Duplicate insert must not overwrite."""
    h = CuckooHash(10)

    h.insert("cat", 1)

    assert h.insert("cat", 999) is False
    assert h.find("cat") == 1
    assert len(h) == 1


# ============================================================
# CATEGORY 4: Multi-Key Independence
# ============================================================

def test_multiple_keys():
    """Distinct keys should coexist independently."""
    h = CuckooHash(10)
    
    entries = {
        "a": 1,
        "b": 2,
        "c": 3
    }

    for k, v in entries.items():
        assert h.insert(k, v)
        
    for k, v in entries.items():
        assert h.find(k) == v

    assert len(h) == 3


def test_delete_one_preserves_others():
    """Deleting one key should not affect others."""
    h = CuckooHash(10)

    h.insert("a", 1)
    h.insert("b", 2)
    h.insert("c", 3)

    h.delete("b")

    assert h.find("a") == 1
    assert h.find("b") is None
    assert h.find("c") == 3


# ============================================================
# CATEGORY 5: Delete Behavior
# ============================================================

def test_delete_existing():
    """Deleting existing key removes it."""
    h = CuckooHash(10)

    h.insert("dog", 5)
    h.delete("dog")

    assert h.find("dog") is None


def test_delete_nonexistent():
    """Deleting absent key should not affect existing entries."""
    h = CuckooHash(10)

    h.insert("dog", 5)
    h.delete("cat")

    assert h.find("dog") == 5
    assert len(h) == 1


def test_delete_twice():
    """Deleting same key twice should be safe."""
    h = CuckooHash(10)

    h.insert("x", 1)
    h.delete("x")
    h.delete("x")

    assert h.find("x") is None


# ============================================================
# CATEGORY 6: Length Accounting
# ============================================================

def test_length_complex_sequence():
    """Length should track unique live keys only."""
    h = CuckooHash(10)

    h.insert("a", 1)
    h.insert("b", 2)
    h.insert("c", 3)

    h.delete("b")
    h.insert("a", 999)

    assert len(h) == 2


# ============================================================
# CATEGORY 7: Key Edge Cases
# ============================================================

def test_empty_string_key():
    """Empty string should be valid key."""
    h = CuckooHash(10)

    h.insert("", 123)

    assert h.find("") == 123


def test_unicode_keys():
    """UTF-8 keys should work."""
    h = CuckooHash(10)

    keys = {
        "שלום": 1,
        "😀": 2,
        "café": 3
    }

    for k, v in keys.items():
        h.insert(k, v)

    for k, v in keys.items():
        assert h.find(k) == v


def test_similar_keys():
    """Similar strings should remain distinct."""
    h = CuckooHash(10)

    h.insert("cat", 1)
    h.insert("Cat", 2)
    h.insert("cat ", 3)

    assert h.find("cat") == 1
    assert h.find("Cat") == 2
    assert h.find("cat ") == 3


# ============================================================
# CATEGORY 8: Small Table Collision Stress
# ============================================================

def test_small_table_many_inserts():
    """Tiny tables should still preserve all keys."""
    h = CuckooHash(2)

    entries = {f"k{i}": i for i in range(20)}

    for k, v in entries.items():
        assert h.insert(k, v)
    for k, v in entries.items():
        assert h.find(k) == v

    assert len(h) == 20


# ============================================================
# CATEGORY 9: Reinsert After Delete
# ============================================================

def test_reinsert_after_delete():
    """Deleted key should be insertable again."""
    h = CuckooHash(10)

    assert h.insert("x", 1)
    h.delete("x")
    assert h.insert("x", 2)

    assert h.find("x") == 2


# ============================================================
# CATEGORY 10: Mixed Operation Sequence
# ============================================================

def test_mixed_sequence():
    """Complex deterministic sequence."""
    h = CuckooHash(10)

    h.insert("A", 1)
    h.insert("B", 2)
    h.delete("A")
    h.insert("C", 3)
    h.insert("B", 99)
    h.delete("C")
    h.insert("A", 4)

    assert h.find("A") == 4
    assert h.find("B") == 2
    assert h.find("C") is None
    assert len(h) == 2


# ============================================================
# CATEGORY 11: Randomized Differential Testing
# ============================================================

def test_randomized_against_oracle():
    """Random sequence compared against oracle model."""
    random.seed(12345)

    real = CuckooHash(5)
    oracle = OracleCuckooHash(5)

    keys = [f"k{i}" for i in range(50)]

    for _ in range(300):
        op = random.choice(["insert", "delete", "find"])
        k = random.choice(keys)

        if op == "insert":
            v = random.randint(0, 1000)
            assert real.insert(k, v) == oracle.insert(k, v)

        elif op == "delete":
            real.delete(k)
            oracle.delete(k)

        else:
            assert real.find(k) == oracle.find(k)

        compare_with_oracle(real, oracle, keys)


# ============================================================
# CATEGORY 12: Deterministic Large Stress
# ============================================================

def test_large_deterministic_stress():
    """Large reproducible insert set."""
    h = CuckooHash(5)

    entries = {f"key{i}": i for i in range(100)}

    for k, v in entries.items():
        assert h.insert(k, v)

    for k, v in entries.items():
        assert h.find(k) == v

    assert len(h) == 100
    
pytest.main(["-v", "-s", "test_CuckooHash.py"])   