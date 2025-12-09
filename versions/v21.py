# EVOLVE-BLOCK-START
"""
JSON Compressor v21 - Aggressive binary encoding

Key improvements:
1. Use base64 encoding for string values to reduce character count
2. Pack numeric arrays into binary format
3. Ultra-compact structure representation
4. Minimal overhead for metadata
"""

import json
import base64
import struct
from typing import Any, Dict, List, Union


class JSONCompressor:
    """Compress JSON data using aggressive binary encoding."""
    
    def __init__(self):
        self.key_map = {}
        self.key_counter = 0
        
    def _get_short_key(self, original_key: str) -> str:
        """Generate ultra-compact keys."""
        if len(original_key) <= 2:
            return original_key
            
        if original_key not in self.key_map:
            short_key = self._encode_base62(self.key_counter)
            self.key_map[original_key] = short_key
            self.key_counter += 1
        return self.key_map[original_key]
    
    def _encode_base62(self, num: int) -> str:
        """Encode number to base62."""
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        if num == 0:
            return chars[0]
        result = []
        while num:
            result.append(chars[num % 62])
            num //= 62
        return ''.join(reversed(result))
    
    def _pack_numbers(self, numbers: List[Union[int, float]]) -> str:
        """Pack numeric array into base64-encoded binary."""
        # Detect if all integers or floats
        if all(isinstance(n, int) and -128 <= n <= 127 for n in numbers):
            # Pack as signed bytes
            packed = struct.pack(f'{len(numbers)}b', *numbers)
            return "b:" + base64.b64encode(packed).decode('ascii')
        elif all(isinstance(n, int) and -32768 <= n <= 32767 for n in numbers):
            # Pack as signed shorts
            packed = struct.pack(f'{len(numbers)}h', *numbers)
            return "h:" + base64.b64encode(packed).decode('ascii')
        elif all(isinstance(n, int) for n in numbers):
            # Pack as signed ints
            packed = struct.pack(f'{len(numbers)}i', *numbers)
            return "i:" + base64.b64encode(packed).decode('ascii')
        else:
            # Pack as doubles
            packed = struct.pack(f'{len(numbers)}d', *numbers)
            return "d:" + base64.b64encode(packed).decode('ascii')
    
    def _unpack_numbers(self, packed_str: str) -> List[Union[int, float]]:
        """Unpack base64-encoded binary to numeric array."""
        type_char, b64_data = packed_str.split(':', 1)
        packed = base64.b64decode(b64_data)
        
        if type_char == 'b':
            size = len(packed)
            return list(struct.unpack(f'{size}b', packed))
        elif type_char == 'h':
            size = len(packed) // 2
            return list(struct.unpack(f'{size}h', packed))
        elif type_char == 'i':
            size = len(packed) // 4
            return list(struct.unpack(f'{size}i', packed))
        else:  # 'd'
            size = len(packed) // 8
            return list(struct.unpack(f'{size}d', packed))
    
    def _is_sequential(self, numbers: List[Union[int, float]]) -> bool:
        """Check if numbers form a sequence with constant delta."""
        if len(numbers) < 3:
            return False
        if not all(isinstance(n, (int, float)) for n in numbers):
            return False
        deltas = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
        unique_deltas = set(round(d, 10) for d in deltas)
        return len(unique_deltas) == 1
    
    def _is_constant(self, values: List[Any]) -> bool:
        """Check if all values are the same."""
        return len(values) > 0 and all(v == values[0] for v in values)
    
    def _compress_array(self, arr: List[Any]) -> Union[List, Dict, str]:
        """Aggressively compress arrays."""
        if not arr:
            return arr
        
        # Check for numeric array - pack to binary
        if all(isinstance(item, (int, float)) for item in arr):
            if self._is_sequential(arr):
                return {"s": arr[0], "d": arr[1] - arr[0], "n": len(arr)}
            elif self._is_constant(arr):
                return {"c": arr[0], "n": len(arr)}
            elif len(arr) >= 3:
                return {"p": self._pack_numbers(arr)}
        
        # Check for homogeneous objects
        if all(isinstance(item, dict) for item in arr):
            first_keys = set(arr[0].keys()) if arr else set()
            if all(set(item.keys()) == first_keys for item in arr):
                keys = list(arr[0].keys())
                short_keys = [self._get_short_key(k) for k in keys]
                
                columns = []
                for orig_key in keys:
                    col_values = [item[orig_key] for item in arr]
                    
                    # Try constant
                    if self._is_constant(col_values):
                        columns.append({"c": self._compress_value(col_values[0]), "n": len(col_values)})
                    # Try sequential
                    elif self._is_sequential(col_values):
                        columns.append({"s": col_values[0], "d": col_values[1] - col_values[0], "n": len(col_values)})
                    # Try binary packing for numeric columns
                    elif all(isinstance(v, (int, float)) for v in col_values) and len(col_values) >= 3:
                        columns.append({"p": self._pack_numbers(col_values)})
                    else:
                        columns.append([self._compress_value(v) for v in col_values])
                
                return {"a": 1, "k": short_keys, "d": columns}
        
        return [self._compress_value(item) for item in arr]
    
    def _compress_value(self, value: Any) -> Any:
        """Recursively compress a value."""
        if isinstance(value, dict):
            return self._compress_object(value)
        elif isinstance(value, list):
            return self._compress_array(value)
        elif value is None or isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            # Encode long strings with base64 if it saves space
            if len(value) > 20:
                encoded = base64.b64encode(value.encode('utf-8')).decode('ascii')
                if len(encoded) < len(value):
                    return "s:" + encoded
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
        """Compress JSON data."""
        self.key_map = {}
        self.key_counter = 0
        
        compressed_data = self._compress_value(data)
        result = {"d": compressed_data}
        
        if self.key_map:
            result["m"] = self.key_map
        
        return result
    
    def _decompress_value(self, value: Any, key_map: Dict[str, str]) -> Any:
        """Recursively decompress a value."""
        if isinstance(value, dict):
            if "c" in value and "n" in value:
                return [self._decompress_value(value["c"], key_map) for _ in range(value["n"])]
            elif "s" in value and "d" in value and "n" in value:
                return [value["s"] + i * value["d"] for i in range(value["n"])]
            elif "p" in value:
                return self._unpack_numbers(value["p"])
            elif "a" in value and value.get("a") == 1:
                return self._decompress_array(value, key_map)
            else:
                return self._decompress_object(value, key_map)
        elif isinstance(value, list):
            return [self._decompress_value(item, key_map) for item in value]
        elif isinstance(value, str) and value.startswith("s:"):
            return base64.b64decode(value[2:]).decode('utf-8')
        else:
            return value
    
    def _decompress_array(self, arr_data: Dict, key_map: Dict[str, str]) -> List[Dict]:
        """Decompress columnar array back to row format."""
        short_keys = arr_data["k"]
        columns = arr_data["d"]
        
        expanded_columns = []
        for col in columns:
            if isinstance(col, dict):
                if "c" in col:
                    val = self._decompress_value(col["c"], key_map)
                    expanded_columns.append([val] * col["n"])
                elif "s" in col:
                    start, delta, count = col["s"], col["d"], col["n"]
                    expanded_columns.append([start + i * delta for i in range(count)])
                elif "p" in col:
                    expanded_columns.append(self._unpack_numbers(col["p"]))
            else:
                expanded_columns.append(col)
        
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
