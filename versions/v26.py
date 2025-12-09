# EVOLVE-BLOCK-START
"""
JSON Compressor v26 - Common prefix compression for strings

Key improvements:
1. Keep v25 as base
2. Add common prefix detection for string columns
3. Delta encode similar strings
4. More compact string encoding
"""

import json
import base64
import struct
from typing import Any, Dict, List, Union, Tuple


class JSONCompressor:
    """String prefix and binary compression."""
    
    def __init__(self):
        self.key_map = {}
        self.key_counter = 0
        
    def _get_short_key(self, k: str) -> str:
        """Compress all keys."""
        if k not in self.key_map:
            self.key_map[k] = self._b62(self.key_counter)
            self.key_counter += 1
        return self.key_map[k]
    
    def _b62(self, n: int) -> str:
        """Base62."""
        c = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        if n == 0:
            return c[0]
        r = []
        while n:
            r.append(c[n % 62])
            n //= 62
        return ''.join(reversed(r))
    
    def _common_prefix(self, strings: List[str]) -> Tuple[str, List[str]]:
        """Find common prefix in strings."""
        if not strings or len(strings) < 2:
            return "", strings
        
        prefix = strings[0]
        for s in strings[1:]:
            while not s.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return "", strings
        
        if len(prefix) >= 3:
            suffixes = [s[len(prefix):] for s in strings]
            return prefix, suffixes
        return "", strings
    
    def _pack_nums(self, nums: List[Union[int, float]]) -> str:
        """Pack numbers."""
        if all(isinstance(n, int) and 0 <= n <= 255 for n in nums):
            return "U" + base64.b64encode(bytes(nums)).decode()
        elif all(isinstance(n, int) and -128 <= n <= 127 for n in nums):
            return "B" + base64.b64encode(struct.pack(f'{len(nums)}b', *nums)).decode()
        elif all(isinstance(n, int) and 0 <= n <= 65535 for n in nums):
            return "V" + base64.b64encode(struct.pack(f'{len(nums)}H', *nums)).decode()
        elif all(isinstance(n, int) and -32768 <= n <= 32767 for n in nums):
            return "H" + base64.b64encode(struct.pack(f'{len(nums)}h', *nums)).decode()
        elif all(isinstance(n, int) for n in nums):
            return "I" + base64.b64encode(struct.pack(f'{len(nums)}i', *nums)).decode()
        else:
            return "D" + base64.b64encode(struct.pack(f'{len(nums)}d', *nums)).decode()
    
    def _unpack_nums(self, s: str) -> List[Union[int, float]]:
        """Unpack numbers."""
        t, d = s[0], base64.b64decode(s[1:])
        if t == 'U':
            return list(d)
        elif t == 'B':
            return list(struct.unpack(f'{len(d)}b', d))
        elif t == 'V':
            return list(struct.unpack(f'{len(d)//2}H', d))
        elif t == 'H':
            return list(struct.unpack(f'{len(d)//2}h', d))
        elif t == 'I':
            return list(struct.unpack(f'{len(d)//4}i', d))
        return list(struct.unpack(f'{len(d)//8}d', d))
    
    def _pack_bools(self, bools: List[bool]) -> str:
        """Pack booleans."""
        n = (len(bools) + 7) // 8
        ba = bytearray(n)
        for i, b in enumerate(bools):
            if b:
                ba[i // 8] |= (1 << (i % 8))
        return "T" + base64.b64encode(bytes(ba)).decode() + f"~{len(bools)}"
    
    def _unpack_bools(self, s: str) -> List[bool]:
        """Unpack booleans."""
        p = s[1:].split('~')
        d = base64.b64decode(p[0])
        c = int(p[1])
        return [bool(d[i // 8] & (1 << (i % 8))) for i in range(c)]
    
    def _is_seq(self, nums: List[Union[int, float]]) -> bool:
        """Sequential check."""
        if len(nums) < 3 or not all(isinstance(n, (int, float)) for n in nums):
            return False
        deltas = [nums[i+1] - nums[i] for i in range(len(nums)-1)]
        return len(set(round(d, 10) for d in deltas)) == 1
    
    def _is_const(self, vals: List[Any]) -> bool:
        """Constant check."""
        return len(vals) >= 2 and all(v == vals[0] for v in vals)
    
    def _compress_array(self, arr: List[Any]) -> Union[List, Dict, str]:
        """Compress array."""
        if not arr:
            return arr
        
        # Booleans
        if all(isinstance(x, bool) for x in arr):
            if self._is_const(arr):
                return {"c": arr[0], "n": len(arr)}
            if len(arr) >= 3:
                return self._pack_bools(arr)
        
        # Numbers
        if all(isinstance(x, (int, float)) for x in arr):
            if self._is_seq(arr):
                return {"s": arr[0], "d": arr[1] - arr[0], "n": len(arr)}
            if self._is_const(arr):
                return {"c": arr[0], "n": len(arr)}
            if len(arr) >= 3:
                return self._pack_nums(arr)
        
        # Strings with common prefix
        if all(isinstance(x, str) for x in arr):
            if self._is_const(arr):
                return {"c": arr[0], "n": len(arr)}
            prefix, suffixes = self._common_prefix(arr)
            if prefix and sum(len(s) for s in suffixes) + len(prefix) < sum(len(s) for s in arr):
                return {"p": prefix, "x": suffixes}
        
        # Objects
        if all(isinstance(x, dict) for x in arr):
            ks = set(arr[0].keys()) if arr else set()
            if all(set(x.keys()) == ks for x in arr):
                keys = list(arr[0].keys())
                sks = [self._get_short_key(k) for k in keys]
                
                cols = []
                for k in keys:
                    cv = [x[k] for x in arr]
                    
                    if self._is_const(cv):
                        cols.append({"c": self._c(cv[0]), "n": len(cv)})
                    elif self._is_seq(cv):
                        cols.append({"s": cv[0], "d": cv[1] - cv[0], "n": len(cv)})
                    elif all(isinstance(v, bool) for v in cv) and len(cv) >= 3:
                        cols.append(self._pack_bools(cv))
                    elif all(isinstance(v, (int, float)) for v in cv) and len(cv) >= 3:
                        cols.append(self._pack_nums(cv))
                    elif all(isinstance(v, str) for v in cv):
                        # Try prefix compression for string columns
                        if self._is_const(cv):
                            cols.append({"c": self._c(cv[0]), "n": len(cv)})
                        else:
                            prefix, suffixes = self._common_prefix(cv)
                            if prefix and sum(len(s) for s in suffixes) + len(prefix) < sum(len(s) for s in cv):
                                cols.append({"p": prefix, "x": suffixes})
                            else:
                                cols.append([self._c(v) for v in cv])
                    else:
                        cols.append([self._c(v) for v in cv])
                
                return {"a": 1, "k": sks, "d": cols}
        
        return [self._c(x) for x in arr]
    
    def _c(self, v: Any) -> Any:
        """Compress value."""
        if isinstance(v, dict):
            return {self._get_short_key(k): self._c(val) for k, val in v.items()}
        elif isinstance(v, list):
            return self._compress_array(v)
        elif v is None or isinstance(v, bool):
            return v
        elif isinstance(v, (int, float)):
            return v
        elif isinstance(v, str):
            if len(v) > 20:
                e = base64.b64encode(v.encode('utf-8')).decode('ascii')
                if len(e) < len(v):
                    return "S" + e
            return v
        return str(v)
    
    def compress(self, data: Any) -> Dict[str, Any]:
        """Compress."""
        self.key_map = {}
        self.key_counter = 0
        
        cd = self._c(data)
        r = {"d": cd}
        
        if self.key_map:
            r["m"] = self.key_map
        
        return r
    
    def _d(self, v: Any, km: Dict[str, str]) -> Any:
        """Decompress value."""
        if isinstance(v, dict):
            if "c" in v and "n" in v:
                return [self._d(v["c"], km) for _ in range(v["n"])]
            elif "s" in v and "d" in v and "n" in v:
                return [v["s"] + i * v["d"] for i in range(v["n"])]
            elif "p" in v and "x" in v:
                # Prefix-compressed strings
                return [v["p"] + suffix for suffix in v["x"]]
            elif "a" in v and v.get("a") == 1:
                return self._d_arr(v, km)
            else:
                return {km.get(k, k): self._d(val, km) for k, val in v.items()}
        elif isinstance(v, list):
            return [self._d(x, km) for x in v]
        elif isinstance(v, str):
            if v.startswith("S"):
                return base64.b64decode(v[1:]).decode('utf-8')
            elif v.startswith("T"):
                return self._unpack_bools(v)
            elif v and v[0] in "UBVHID":
                return self._unpack_nums(v)
        return v
    
    def _d_arr(self, ad: Dict, km: Dict[str, str]) -> List[Dict]:
        """Decompress array."""
        sks = ad["k"]
        cols = ad["d"]
        
        ecs = []
        for col in cols:
            if isinstance(col, dict):
                if "c" in col:
                    ecs.append([self._d(col["c"], km)] * col["n"])
                elif "s" in col:
                    ecs.append([col["s"] + i * col["d"] for i in range(col["n"])])
                elif "p" in col and "x" in col:
                    ecs.append([col["p"] + suffix for suffix in col["x"]])
            elif isinstance(col, str) and col and col[0] in "UBVHIDT":
                ecs.append(self._d(col, km))
            else:
                ecs.append(col)
        
        nr = len(ecs[0]) if ecs else 0
        r = []
        for i in range(nr):
            obj = {}
            for j, sk in enumerate(sks):
                obj[km.get(sk, sk)] = self._d(ecs[j][i], km)
            r.append(obj)
        
        return r
    
    def decompress(self, compressed: Dict[str, Any]) -> Any:
        """Decompress."""
        km = compressed.get("m", {})
        rkm = {v: k for k, v in km.items()}
        return self._d(compressed["d"], rkm)


def compress_json(data: Any) -> str:
    """Compress JSON."""
    orig = json.dumps(data, separators=(',', ':'))
    
    comp = JSONCompressor()
    c = comp.compress(data)
    cs = json.dumps(c, separators=(',', ':'))
    
    return cs if len(cs) < len(orig) else orig


def decompress_json(s: str) -> Any:
    """Decompress JSON."""
    d = json.loads(s)
    
    if isinstance(d, dict) and "d" in d:
        return JSONCompressor().decompress(d)
    return d

# EVOLVE-BLOCK-END
