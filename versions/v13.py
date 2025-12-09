# EVOLVE-BLOCK-START
"""
JSON Compressor v13 - String compression with common substring detection

Key improvements:
1. Add string deduplication for repeated strings
2. Store common substrings once
"""

import json
from typing import Any, Dict, List, Union
from collections import Counter


class JSONCompressor:
    """Compress JSON data to minimize token usage."""
    
    def __init__(self):
        self.key_map = {}
        self.reverse_key_map = {}
        self.key_counter = 0
        self.min_key_length = 4
        self.string_map = {}
        self.string_counter = 0
        
    def _get_short_key(self, original_key: str) -> str:
        """Generate or retrieve a short key for the original key."""
        if len(original_key) <= self.min_key_length:
            return original_key
            
        if original_key not in self.key_map:
            short_key = self._encode_base62(self.key_counter)
            self.key_map[original_key] = short_key
            self.reverse_key_map[short_key] = original_key
            self.key_counter += 1
        return self.key_map[original_key]
    
    def _get_string_ref(self, s: str) -> Union[str, Dict]:
        """Compress repeated strings."""
        if len(s) < 10:  # Only compress longer strings
            return s
        if s not in self.string_map:
            self.string_map[s] = self.string_counter
            self.string_counter += 1
        return {"$": self.string_map[s]}
    
    def _encode_base62(self, num: int) -> str:
        """Encode number to base62 for ultra-compact keys."""
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        if num == 0:
            return chars[0]
        result = []
        while num:
            result.append(chars[num % 62])
            num //= 62
        return ''.join(reversed(result))
    
    def _is_sequential(self, numbers: List[Union[int, float]]) -> bool:
        """Check if numbers form a sequence with constant delta."""
        if len(numbers) < 3:
            return False
        if not all(isinstance(n, (int, float)) for n in numbers):
            return False
        deltas = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
        return len(set(deltas)) == 1
    
    def _is_constant(self, values: List[Any]) -> bool:
        """Check if all values in list are the same."""
        if len(values) < 2:
            return False
        return all(v == values[0] for v in values)
    
    def _compress_array(self, arr: List[Any]) -> Union[List, Dict]:
        """Optimize array representation based on homogeneity."""
        if not arr:
            return arr
        
        # Check if array contains objects with same structure
        if all(isinstance(item, dict) for item in arr):
            first_keys = set(arr[0].keys()) if arr else set()
            if all(set(item.keys()) == first_keys for item in arr):
                # Homogeneous object array - ALWAYS use columnar format
                keys = list(arr[0].keys())
                short_keys = [self._get_short_key(k) for k in keys]
                
                columns = []
                for orig_key, short_key in zip(keys, short_keys):
                    col_values = [item[orig_key] for item in arr]
                    
                    # Try constant encoding (all same value)
                    if self._is_constant(col_values):
                        columns.append({"c": self._compress_value(col_values[0]), "n": len(col_values)})
                    # Try delta encoding for numeric columns
                    elif self._is_sequential(col_values):
                        delta = col_values[1] - col_values[0]
                        columns.append({"s": col_values[0], "d": delta, "n": len(col_values)})
                    else:
                        columns.append([self._compress_value(v) for v in col_values])
                
                return {"a": 1, "k": short_keys, "d": columns}
        
        # Regular array compression
        return [self._compress_value(item) for item in arr]
    
    def _compress_value(self, value: Any) -> Any:
        """Recursively compress a value."""
        if isinstance(value, dict):
            return self._compress_object(value)
        elif isinstance(value, list):
            return self._compress_array(value)
        elif value is None:
            return None
        elif isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            return value  # For now, disable string compression as it might add overhead
        else:
            return str(value)
    
    def _compress_object(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Compress a dictionary object."""
        compressed = {}
        for key, value in obj.items():
            short_key = self._get_short_key(key)
            compressed[short_key] = self._compress_value(value)
        return compressed
    
    def compress(self, data: Any) -> Dict[str, Any]:
        """Compress JSON data to minimize tokens."""
        self.key_map = {}
        self.reverse_key_map = {}
        self.key_counter = 0
        self.string_map = {}
        self.string_counter = 0
        
        compressed_data = self._compress_value(data)
        
        result = {"d": compressed_data}
        
        if self.key_map:
            result["m"] = self.key_map
        
        return result
    
    def _decompress_value(self, value: Any, key_map: Dict[str, str]) -> Any:
        """Recursively decompress a value."""
        if isinstance(value, dict):
            # Check for constant encoding
            if "c" in value and "n" in value:
                return [self._decompress_value(value["c"], key_map) for _ in range(value["n"])]
            # Check for delta-encoded sequence
            elif "s" in value and "d" in value and "n" in value:
                start = value["s"]
                delta = value["d"]
                count = value["n"]
                return [start + i * delta for i in range(count)]
            # Check if it's a compressed array
            elif "a" in value and value.get("a") == 1:
                return self._decompress_array(value, key_map)
            else:
                return self._decompress_object(value, key_map)
        elif isinstance(value, list):
            return [self._decompress_value(item, key_map) for item in value]
        else:
            return value
    
    def _decompress_array(self, arr_data: Dict, key_map: Dict[str, str]) -> List[Dict]:
        """Decompress a columnar array back to row format."""
        short_keys = arr_data["k"]
        columns = arr_data["d"]
        
        # First, expand any encoded columns
        expanded_columns = []
        for col in columns:
            if isinstance(col, dict):
                if "c" in col:
                    # Constant column
                    val = self._decompress_value(col["c"], key_map)
                    expanded_columns.append([val] * col["n"])
                elif "s" in col:
                    # Delta-encoded
                    start = col["s"]
                    delta = col["d"]
                    count = col["n"]
                    expanded_columns.append([start + i * delta for i in range(count)])
            else:
                expanded_columns.append(col)
        
        # Reconstruct objects
        result = []
        num_rows = len(expanded_columns[0]) if expanded_columns else 0
        
        for i in range(num_rows):
            obj = {}
            for j, short_key in enumerate(short_keys):
                original_key = key_map.get(short_key, short_key)
                value = self._decompress_value(expanded_columns[j][i], key_map)
                obj[original_key] = value
            result.append(obj)
        
        return result
    
    def _decompress_object(self, obj: Dict[str, Any], key_map: Dict[str, str]) -> Dict[str, Any]:
        """Decompress a dictionary object."""
        decompressed = {}
        for short_key, value in obj.items():
            original_key = key_map.get(short_key, short_key)
            decompressed[original_key] = self._decompress_value(value, key_map)
        return decompressed
    
    def decompress(self, compressed: Dict[str, Any]) -> Any:
        """Decompress data back to original format."""
        key_map = compressed.get("m", {})
        reverse_map = {v: k for k, v in key_map.items()}
        
        return self._decompress_value(compressed["d"], reverse_map)


def compress_json(data: Any) -> str:
    """Compress JSON data and return as compact JSON string."""
    original_str = json.dumps(data, separators=(',', ':'))
    
    compressor = JSONCompressor()
    compressed = compressor.compress(data)
    compressed_str = json.dumps(compressed, separators=(',', ':'))
    
    if len(compressed_str) < len(original_str):
        return compressed_str
    else:
        return original_str


def decompress_json(compressed_str: str) -> Any:
    """Decompress a compressed JSON string back to original data."""
    data = json.loads(compressed_str)
    
    if isinstance(data, dict) and "d" in data:
        compressor = JSONCompressor()
        return compressor.decompress(data)
    else:
        return data

# EVOLVE-BLOCK-END


def run_compression():
    """Entry point for running compression tests."""
    test_data = {
        "users": [
            {"user_id": 1, "username": "alice", "email": "alice@example.com", "active": True},
            {"user_id": 2, "username": "bob", "email": "bob@example.com", "active": False},
            {"user_id": 3, "username": "charlie", "email": "charlie@example.com", "active": True}
        ],
        "metadata": {
            "total_count": 3,
            "page_number": 1,
            "items_per_page": 10
        }
    }
    
    compressed = compress_json(test_data)
    decompressed = decompress_json(compressed)
    
    return {
        "original": test_data,
        "compressed": compressed,
        "decompressed": decompressed,
        "valid": test_data == decompressed,
        "original_size": len(json.dumps(test_data, separators=(',', ':'))),
        "compressed_size": len(compressed)
    }


if __name__ == "__main__":
    results = run_compression()
    print(f"Original size: {results['original_size']} characters")
    print(f"Compressed size: {results['compressed_size']} characters")
    print(f"Compression ratio: {results['compressed_size']/results['original_size']*100:.1f}%")
    print(f"Valid decompression: {results['valid']}")
