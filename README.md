# CuckooHash

A Python implementation of a cuckoo hash table using two underlying tables and two hash functions. Lookups and deletes check at most two slots, so they run in worst-case constant time, and inserts run in amortized constant time.

## How it works

Every key has exactly two possible homes: one slot in table 1 (chosen by hash function 1) and one slot in table 2 (chosen by hash function 2).

1. **Insert:** the key goes to its slot in table 1. If that slot is occupied, the resident key is evicted and the new key takes its place.
2. The evicted key is moved to its slot in table 2. If that slot is also occupied, *that* resident is evicted and sent back to table 1, and so on.
3. If the eviction chain runs longer than `MAX_LOOPS` (20), the table assumes it is stuck in a cycle. It picks new hash functions with `ResetBitHash()`, doubles the size of both tables, reinserts every entry, and retries.
4. **Find / delete:** only the key's two candidate slots are checked.

Credit for the design goes to the sources this was based on: Shannon Larson's slides (March 2011), the [Wikipedia article on cuckoo hashing](https://en.wikipedia.org/wiki/Cuckoo_hashing), and [lkozma.net's cuckoo hashing visualization](https://lkozma.net/cuckoo_hashing_visualization).

## Requirements

- Python 3
- `BitHash.py` in the same directory. It must provide `BitHash(key, hashFuncNum=...)` (with function numbers 1 and 2) and `ResetBitHash()`.
- `pytest` (only for running the tests)

## Usage

```python
from CuckooHash import CuckooHash

table = CuckooHash(10)       # two underlying tables of 10 slots each

table.insert("apple", 3)     # True
table.insert("banana", 5)    # True
table.insert("apple", 99)    # False: key already present, value not overwritten

table.find("apple")          # 3
table.find("cherry")         # None

table.delete("banana")       # removes the key; does nothing if it's absent
len(table)                   # 1

table.display()              # prints all key/data pairs, useful for debugging
```

## API

| Method | Description | Returns | Complexity |
|--------|-------------|---------|------------|
| `CuckooHash(size)` | Creates a table with two underlying arrays of `size` slots each | | O(size) |
| `insert(k, d)` | Inserts the pair if `k` is not already present. Never overwrites an existing key. | `True` if inserted, `False` if the key already exists | Amortized O(1) |
| `find(k)` | Looks up a key | The data, or `None` if absent | O(1) |
| `delete(k)` | Removes a key if present | Nothing | O(1) |
| `len(table)` | Number of stored keys across both tables | `int` | O(1) |
| `display()` | Prints all key/data pairs | Nothing | O(size) |

## Implementation notes

- **Storage:** each slot holds either `None` or a `(key, data)` tuple.
- **Cycle detection:** a fixed cap of `MAX_LOOPS = 20` evictions per insert attempt.
- **Growth:** tables double in size only when a cycle is detected, not at a fixed load factor. Tables never shrink on delete.
- **Rehashing:** `ResetBitHash()` selects new hash functions before the tables are rebuilt, which makes repeated cycles unlikely.
- **Duplicates:** inserting an existing key returns `False` and leaves the original data untouched.

## Testing

The test suite in `test_CuckooHash.py` is a black-box pytest suite that uses only the public API. It includes:

- Constructor and empty-table behavior
- Duplicate-key handling
- Delete and reinsert behavior
- Length accounting
- Edge-case keys (empty string, Unicode, near-identical strings)
- Collision stress on tiny tables (forcing rehash and growth)
- Randomized differential testing against a Python `dict` oracle
- A deterministic large insert test

Run it with:

```bash
pytest -v test_CuckooHash.py
```

## Project structure

```
.
├── CuckooHash.py        # the hash table
├── test_CuckooHash.py   # pytest suite
├── BitHash.py           # hash functions (required)
└── README.md
```

## Authorship

`CuckooHash.py` was written entirely by me, with no AI assistance. `test_CuckooHash.py` was written by AI at my prompting. `BitHash.py` was provided by professor.
