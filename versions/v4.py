# EVOLVE-BLOCK-START
"""
JSON Compressor v4 - Aggressive Key & Array Optimization

Key improvements:
1. Lower minimum key length to 5 characters
2. Remove wrapper overhead - use single char "m" and "d"
3. Optimize array threshold to 2 items minimum
4. Simplified structure to reduce metadata overhead
"""

import json
from typing import Any, Dict, List, Union


class JSONCompressor:
    """Compress JSON data to minimize token usage."""
    
    def __init__(self):
        self.key_map = {}
        self.reverse_key_map = {}
        self.key_counter = 0
        self.min_key_length = 5  # Compress keys longer than 5 chars
        
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
    
    def _compress_array(self, arr: List[Any]) -> Union[List, Dict]:
        """Optimize array representation based on homogeneity."""
        if not arr:
            return arr
        
        # Check if array contains objects with same structure
        if all(isinstance(item, dict) for item in arr):
            first_keys = set(arr[0].keys()) if arr else set()
            if all(set(item.keys()) == first_keys for item in arr):
                # Homogeneous object array - use columnar format with lower threshold
                if len(arr) >= 2:
                    keys = list(arr[0].keys())
                    short_keys = [self._get_short_key(k) for k in keys]
                    
                    columns = {sk: [] for sk in short_keys}
                    for item in arr:
                        for orig_key, short_key in zip(keys, short_keys):
                            value = self._compress_value(item[orig_key])
                            columns[short_key].append(value)
                    
                    # Use minimal keys: a=array, k=keys, d=data
                    return {"a": 1, "k": short_keys, "d": [columns[sk] for sk in short_keys]}
        
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
            return value
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
        
        compressed_data = self._compress_value(data)
        
        # Minimal structure
        result = {"d": compressed_data}
        
        if self.key_map:
            result["m"] = self.key_map
        
        return result
    
    def _decompress_value(self, value: Any, key_map: Dict[str, str]) -> Any:
        """Recursively decompress a value."""
        if isinstance(value, dict):
            # Check if it's a compressed array (has "a" marker)
            if "a" in value and value.get("a") == 1:
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
        
        # Reconstruct objects
        result = []
        num_rows = len(columns[0]) if columns else 0
        
        for i in range(num_rows):
            obj = {}
            for j, short_key in enumerate(short_keys):
                original_key = key_map.get(short_key, short_key)
                value = self._decompress_value(columns[j][i], key_map)
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
