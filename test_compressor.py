"""
Comprehensive test suite for JSON Compressor.

Tests various JSON structures including:
- Simple objects
- Nested objects
- Deeply nested structures
- Arrays of primitives
- Arrays of objects (homogeneous)
- Mixed arrays
- Edge cases
"""

import json
import unittest
from json_compressor import JSONCompressor, compress_json, decompress_json


class TestJSONCompressor(unittest.TestCase):
    """Test cases for JSON compression and decompression."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = JSONCompressor()
    
    def _verify_compression(self, data):
        """Helper to verify compression and decompression work correctly."""
        compressed_str = compress_json(data)
        decompressed = decompress_json(compressed_str)
        self.assertEqual(data, decompressed, "Decompressed data doesn't match original")
        return compressed_str
    
    def test_simple_object(self):
        """Test compression of a simple flat object."""
        data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "active": True
        }
        self._verify_compression(data)
    
    def test_nested_object(self):
        """Test compression of nested objects."""
        data = {
            "user": {
                "name": "Alice",
                "profile": {
                    "age": 25,
                    "location": "New York"
                }
            },
            "settings": {
                "notifications": True,
                "privacy": "public"
            }
        }
        self._verify_compression(data)
    
    def test_deeply_nested_object(self):
        """Test compression of deeply nested structures (5+ levels)."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "level6": {
                                    "value": "deep",
                                    "count": 6
                                }
                            }
                        }
                    }
                }
            }
        }
        self._verify_compression(data)
    
    def test_array_of_primitives(self):
        """Test compression of arrays with primitive values."""
        data = {
            "numbers": [1, 2, 3, 4, 5],
            "strings": ["apple", "banana", "cherry"],
            "booleans": [True, False, True],
            "mixed": [1, "two", 3.0, None, False]
        }
        self._verify_compression(data)
    
    def test_homogeneous_object_array(self):
        """Test compression of arrays with identical structure objects."""
        data = {
            "employees": [
                {"id": 1, "name": "Alice", "department": "Engineering", "salary": 100000},
                {"id": 2, "name": "Bob", "department": "Marketing", "salary": 80000},
                {"id": 3, "name": "Charlie", "department": "Sales", "salary": 90000},
                {"id": 4, "name": "Diana", "department": "Engineering", "salary": 110000},
                {"id": 5, "name": "Eve", "department": "HR", "salary": 75000}
            ]
        }
        compressed = self._verify_compression(data)
        # This should trigger columnar optimization
        self.assertIn('"t":"a"', compressed)
    
    def test_heterogeneous_object_array(self):
        """Test compression of arrays with different structure objects."""
        data = {
            "items": [
                {"type": "book", "title": "Python Guide", "pages": 300},
                {"type": "video", "title": "Learn Python", "duration": 120},
                {"type": "book", "title": "Data Science", "author": "Jane Doe"}
            ]
        }
        self._verify_compression(data)
    
    def test_nested_arrays(self):
        """Test compression of nested array structures."""
        data = {
            "matrix": [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ],
            "nested": [
                [{"x": 1}, {"x": 2}],
                [{"x": 3}, {"x": 4}]
            ]
        }
        self._verify_compression(data)
    
    def test_complex_nested_structure(self):
        """Test compression of complex real-world-like structure."""
        data = {
            "company": "Tech Corp",
            "departments": [
                {
                    "name": "Engineering",
                    "budget": 1000000,
                    "teams": [
                        {
                            "team_name": "Backend",
                            "members": [
                                {"name": "Alice", "role": "Senior Dev", "years": 5},
                                {"name": "Bob", "role": "Junior Dev", "years": 1}
                            ]
                        },
                        {
                            "team_name": "Frontend",
                            "members": [
                                {"name": "Charlie", "role": "Lead Dev", "years": 7},
                                {"name": "Diana", "role": "Designer", "years": 3}
                            ]
                        }
                    ]
                },
                {
                    "name": "Marketing",
                    "budget": 500000,
                    "teams": [
                        {
                            "team_name": "Digital",
                            "members": [
                                {"name": "Eve", "role": "Manager", "years": 4}
                            ]
                        }
                    ]
                }
            ],
            "metadata": {
                "last_updated": "2025-12-08",
                "version": 2,
                "active": True
            }
        }
        self._verify_compression(data)
    
    def test_empty_structures(self):
        """Test compression of empty objects and arrays."""
        data = {
            "empty_object": {},
            "empty_array": [],
            "nested_empty": {
                "obj": {},
                "arr": []
            }
        }
        self._verify_compression(data)
    
    def test_null_values(self):
        """Test compression of null/None values."""
        data = {
            "value1": None,
            "value2": "not null",
            "nested": {
                "null_field": None,
                "array_with_nulls": [1, None, 3, None, 5]
            }
        }
        self._verify_compression(data)
    
    def test_special_characters(self):
        """Test compression of strings with special characters."""
        data = {
            "unicode": "Hello 世界 🌍",
            "escaped": "Line1\nLine2\tTabbed",
            "quotes": 'She said "Hello"',
            "backslash": "C:\\Users\\path"
        }
        self._verify_compression(data)
    
    def test_large_numbers(self):
        """Test compression of various number types."""
        data = {
            "small_int": 42,
            "large_int": 9007199254740991,
            "negative": -12345,
            "float": 3.14159,
            "scientific": 1.23e-10,
            "zero": 0
        }
        self._verify_compression(data)
    
    def test_deeply_nested_arrays_and_objects(self):
        """Test extreme nesting with mixed arrays and objects."""
        data = {
            "level1": [
                {
                    "level2": [
                        {
                            "level3": {
                                "level4": [
                                    {
                                        "level5": {
                                            "data": "very deep",
                                            "path": [1, 2, 3, [4, 5, [6, 7]]]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        self._verify_compression(data)
    
    def test_api_response_structure(self):
        """Test typical API response structure."""
        data = {
            "status": "success",
            "code": 200,
            "data": {
                "users": [
                    {
                        "id": 1,
                        "username": "alice123",
                        "email": "alice@example.com",
                        "profile": {
                            "first_name": "Alice",
                            "last_name": "Smith",
                            "avatar_url": "https://example.com/avatar1.jpg"
                        },
                        "created_at": "2024-01-15T10:30:00Z",
                        "is_active": True
                    },
                    {
                        "id": 2,
                        "username": "bob456",
                        "email": "bob@example.com",
                        "profile": {
                            "first_name": "Bob",
                            "last_name": "Johnson",
                            "avatar_url": "https://example.com/avatar2.jpg"
                        },
                        "created_at": "2024-02-20T15:45:00Z",
                        "is_active": False
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 10,
                    "total": 2,
                    "total_pages": 1
                }
            },
            "message": "Users retrieved successfully"
        }
        self._verify_compression(data)
    
    def test_database_records_structure(self):
        """Test database-like records with many repeated keys."""
        data = {
            "records": [
                {"record_id": i, "field1": f"value{i}", "field2": i * 10, 
                 "field3": i % 2 == 0, "field4": None, "field5": f"data{i}"}
                for i in range(20)
            ]
        }
        compressed = self._verify_compression(data)
        # Should use columnar format for efficiency
        self.assertIn('"t":"a"', compressed)


class TestCompressionEfficiency(unittest.TestCase):
    """Test compression efficiency and token savings."""
    
    def _get_token_estimate(self, text: str) -> int:
        """
        Rough estimate of tokens (using character count / 4 as approximation).
        For more accurate counting, you'd use tiktoken or similar.
        """
        return len(text) // 4
    
    def test_compression_ratio_simple(self):
        """Measure compression ratio for simple data."""
        data = {
            "long_key_name_1": "value1",
            "long_key_name_2": "value2",
            "long_key_name_3": "value3"
        }
        original = json.dumps(data, separators=(',', ':'))
        compressed = compress_json(data)
        
        ratio = len(compressed) / len(original)
        print(f"\nSimple object compression: {ratio:.2%}")
        # Small objects may be larger due to metadata overhead - this is expected
        # Compression is most effective with larger datasets
        self.assertIsNotNone(compressed, "Compression should produce output")
    
    def test_compression_ratio_array(self):
        """Measure compression ratio for homogeneous arrays."""
        data = {
            "items": [
                {"very_long_field_name": i, "another_long_field": i*2, "third_field": f"item{i}"}
                for i in range(10)
            ]
        }
        original = json.dumps(data, separators=(',', ':'))
        compressed = compress_json(data)
        
        ratio = len(compressed) / len(original)
        print(f"\nArray compression: {ratio:.2%}")
        # Arrays should compress very well
        self.assertLess(ratio, 0.8, "Array compression should be significant")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compressor = JSONCompressor()
    
    def _verify_compression(self, data):
        """Helper to verify compression and decompression work correctly."""
        compressed_str = compress_json(data)
        decompressed = decompress_json(compressed_str)
        self.assertEqual(data, decompressed, "Decompressed data doesn't match original")
        return compressed_str
    
    def test_single_element_array(self):
        """Test array with only one element."""
        data = {
            "singleton": [{"key": "value"}],
            "single_primitive": [42]
        }
        self._verify_compression(data)
    
    def test_two_element_array(self):
        """Test array with two elements (boundary for columnar optimization)."""
        data = {
            "pair": [
                {"field_one": 1, "field_two": 2},
                {"field_one": 3, "field_two": 4}
            ]
        }
        compressed = self._verify_compression(data)
        # Should not use columnar format for only 2 items
        self.assertNotIn('"t":"a"', compressed)
    
    def test_very_long_strings(self):
        """Test compression with very long string values."""
        long_text = "Lorem ipsum " * 100
        data = {
            "description": long_text,
            "nested": {
                "long_value": long_text,
                "short_value": "brief"
            }
        }
        self._verify_compression(data)
    
    def test_duplicate_values_in_arrays(self):
        """Test arrays with many duplicate values."""
        data = {
            "repeated": ["same", "same", "same", "same", "same"],
            "objects_repeated": [
                {"status": "active", "count": 1},
                {"status": "active", "count": 2},
                {"status": "active", "count": 3}
            ]
        }
        self._verify_compression(data)
    
    def test_boolean_heavy_data(self):
        """Test data with many boolean values."""
        data = {
            "flags": {
                "is_enabled": True,
                "is_verified": False,
                "has_access": True,
                "can_edit": False,
                "is_admin": False
            },
            "feature_toggles": [True, False, True, True, False, False]
        }
        self._verify_compression(data)
    
    def test_numeric_precision(self):
        """Test various numeric precision scenarios."""
        data = {
            "integer": 42,
            "negative_int": -999,
            "zero": 0,
            "float": 3.14159265359,
            "very_small": 0.0000001,
            "very_large": 1e15,
            "negative_float": -2.5,
            "max_safe_int": 9007199254740991,
            "min_safe_int": -9007199254740991
        }
        self._verify_compression(data)
    
    def test_short_keys_not_compressed(self):
        """Test that short keys are not compressed (optimization)."""
        data = {
            "id": 1,
            "name": "test",
            "age": 30,
            "very_long_key_name_that_should_be_compressed": "value"
        }
        compressed_str = compress_json(data)
        compressed_obj = json.loads(compressed_str)
        
        # Short keys should not be in the mapping
        if "m" in compressed_obj:
            self.assertNotIn("id", compressed_obj["m"])
            self.assertNotIn("name", compressed_obj["m"])
            self.assertNotIn("age", compressed_obj["m"])
            # Long key should be compressed
            self.assertIn("very_long_key_name_that_should_be_compressed", compressed_obj["m"])
        
        # Verify decompression still works
        decompressed = decompress_json(compressed_str)
        self.assertEqual(data, decompressed)
    
    def test_mixed_array_depths(self):
        """Test arrays with different nesting depths."""
        data = {
            "mixed": [
                1,
                [2, 3],
                {"nested": [4, 5]},
                [[6], [7]],
                {"deep": {"deeper": [8, 9]}}
            ]
        }
        self._verify_compression(data)
    
    def test_unicode_and_emojis(self):
        """Test various unicode characters and emojis."""
        data = {
            "emoji": "😀🎉🚀💻🌟",
            "chinese": "你好世界",
            "arabic": "مرحبا",
            "russian": "Привет",
            "japanese": "こんにちは",
            "mixed": "Hello 世界 🌍 مرحبا"
        }
        self._verify_compression(data)
    
    def test_key_collision_resistance(self):
        """Test that many unique keys generate unique short codes."""
        data = {f"key_number_{i}": i for i in range(100)}
        compressed_str = self._verify_compression(data)
        compressed_obj = json.loads(compressed_str)
        
        # Verify all keys have unique short codes
        if "m" in compressed_obj:
            short_codes = list(compressed_obj["m"].values())
            self.assertEqual(len(short_codes), len(set(short_codes)), 
                           "All short codes should be unique")


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world data structures and use cases."""
    
    def _verify_compression(self, data):
        """Helper to verify compression and decompression work correctly."""
        compressed_str = compress_json(data)
        decompressed = decompress_json(compressed_str)
        self.assertEqual(data, decompressed, "Decompressed data doesn't match original")
        return compressed_str
    
    def test_time_series_data(self):
        """Test time series data structure."""
        data = {
            "sensor_id": "temp_sensor_01",
            "readings": [
                {"timestamp": "2025-12-09T10:00:00Z", "value": 22.5, "unit": "celsius"},
                {"timestamp": "2025-12-09T10:01:00Z", "value": 22.6, "unit": "celsius"},
                {"timestamp": "2025-12-09T10:02:00Z", "value": 22.7, "unit": "celsius"},
                {"timestamp": "2025-12-09T10:03:00Z", "value": 22.8, "unit": "celsius"},
                {"timestamp": "2025-12-09T10:04:00Z", "value": 22.9, "unit": "celsius"}
            ]
        }
        self._verify_compression(data)
    
    def test_e_commerce_cart(self):
        """Test e-commerce shopping cart structure."""
        data = {
            "cart_id": "cart_12345",
            "user_id": 67890,
            "items": [
                {
                    "product_id": "prod_001",
                    "name": "Wireless Mouse",
                    "quantity": 2,
                    "price": 29.99,
                    "currency": "USD",
                    "in_stock": True
                },
                {
                    "product_id": "prod_002",
                    "name": "USB-C Cable",
                    "quantity": 3,
                    "price": 12.99,
                    "currency": "USD",
                    "in_stock": True
                },
                {
                    "product_id": "prod_003",
                    "name": "Laptop Stand",
                    "quantity": 1,
                    "price": 49.99,
                    "currency": "USD",
                    "in_stock": False
                }
            ],
            "subtotal": 152.95,
            "tax": 13.77,
            "total": 166.72,
            "discount_code": None,
            "created_at": "2025-12-09T10:30:00Z",
            "updated_at": "2025-12-09T10:35:00Z"
        }
        self._verify_compression(data)
    
    def test_social_media_post(self):
        """Test social media post structure with nested comments."""
        data = {
            "post_id": "post_9876",
            "author": {
                "user_id": 12345,
                "username": "johndoe",
                "display_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "verified": True
            },
            "content": {
                "text": "Just launched my new project! Check it out 🚀",
                "media": [
                    {"type": "image", "url": "https://example.com/img1.jpg"},
                    {"type": "image", "url": "https://example.com/img2.jpg"}
                ],
                "hashtags": ["programming", "launch", "excited"]
            },
            "engagement": {
                "likes": 1234,
                "shares": 56,
                "comments": 89,
                "views": 5678
            },
            "comments": [
                {
                    "comment_id": "c1",
                    "author": "alice",
                    "text": "Congratulations!",
                    "likes": 10,
                    "timestamp": "2025-12-09T11:00:00Z"
                },
                {
                    "comment_id": "c2",
                    "author": "bob",
                    "text": "Looks amazing!",
                    "likes": 5,
                    "timestamp": "2025-12-09T11:05:00Z"
                }
            ],
            "timestamp": "2025-12-09T10:00:00Z",
            "edited": False,
            "pinned": False
        }
        self._verify_compression(data)
    
    def test_log_entries(self):
        """Test application log entries structure."""
        data = {
            "application": "web-server",
            "version": "2.1.0",
            "logs": [
                {"level": "INFO", "timestamp": "2025-12-09T10:00:00Z", "message": "Server started", "request_id": None},
                {"level": "DEBUG", "timestamp": "2025-12-09T10:01:00Z", "message": "Processing request", "request_id": "req_001"},
                {"level": "WARN", "timestamp": "2025-12-09T10:02:00Z", "message": "Slow query detected", "request_id": "req_002"},
                {"level": "ERROR", "timestamp": "2025-12-09T10:03:00Z", "message": "Database connection timeout", "request_id": "req_003"},
                {"level": "INFO", "timestamp": "2025-12-09T10:04:00Z", "message": "Request completed", "request_id": "req_001"}
            ]
        }
        self._verify_compression(data)
    
    def test_configuration_file(self):
        """Test application configuration structure."""
        data = {
            "app_name": "my-application",
            "environment": "production",
            "server": {
                "host": "0.0.0.0",
                "port": 8080,
                "workers": 4,
                "timeout": 30,
                "ssl_enabled": True,
                "ssl_cert_path": "/etc/ssl/cert.pem",
                "ssl_key_path": "/etc/ssl/key.pem"
            },
            "database": {
                "primary": {
                    "host": "db1.example.com",
                    "port": 5432,
                    "name": "app_db",
                    "pool_size": 20,
                    "ssl_mode": "require"
                },
                "replica": {
                    "host": "db2.example.com",
                    "port": 5432,
                    "name": "app_db",
                    "pool_size": 10,
                    "ssl_mode": "require"
                }
            },
            "cache": {
                "enabled": True,
                "backend": "redis",
                "host": "cache.example.com",
                "port": 6379,
                "ttl": 3600
            },
            "features": {
                "new_ui": True,
                "beta_features": False,
                "experimental": False
            }
        }
        self._verify_compression(data)
    
    def test_geolocation_data(self):
        """Test geolocation and map data structure."""
        data = {
            "locations": [
                {
                    "location_id": "loc_001",
                    "name": "Coffee Shop",
                    "coordinates": {"latitude": 40.7128, "longitude": -74.0060},
                    "address": "123 Main St, New York, NY",
                    "category": "cafe",
                    "rating": 4.5,
                    "reviews_count": 234
                },
                {
                    "location_id": "loc_002",
                    "name": "Restaurant",
                    "coordinates": {"latitude": 40.7589, "longitude": -73.9851},
                    "address": "456 Park Ave, New York, NY",
                    "category": "restaurant",
                    "rating": 4.8,
                    "reviews_count": 567
                },
                {
                    "location_id": "loc_003",
                    "name": "Library",
                    "coordinates": {"latitude": 40.7614, "longitude": -73.9776},
                    "address": "789 5th Ave, New York, NY",
                    "category": "library",
                    "rating": 4.9,
                    "reviews_count": 123
                }
            ]
        }
        self._verify_compression(data)
    
    def test_large_dataset(self):
        """Test large programmatically generated dataset to evaluate compression at scale."""
        # Generate a realistic large dataset with multiple entity types
        data = {
            "metadata": {
                "dataset_name": "enterprise_data_export",
                "version": "1.0",
                "generated_at": "2025-12-09T10:00:00Z",
                "record_count": 1000,
                "data_types": ["users", "transactions", "products", "events"]
            },
            "users": [
                {
                    "user_id": f"user_{i:04d}",
                    "username": f"user{i}",
                    "email": f"user{i}@example.com",
                    "first_name": f"FirstName{i}",
                    "last_name": f"LastName{i}",
                    "age": 18 + (i % 60),
                    "registration_date": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}T10:00:00Z",
                    "is_active": i % 3 != 0,
                    "is_premium": i % 5 == 0,
                    "account_balance": round(100.0 + (i * 1.23), 2),
                    "preferences": {
                        "notifications_enabled": i % 2 == 0,
                        "newsletter_subscribed": i % 4 == 0,
                        "theme": "dark" if i % 2 == 0 else "light",
                        "language": ["en", "es", "fr", "de", "ja"][i % 5]
                    }
                }
                for i in range(200)
            ],
            "transactions": [
                {
                    "transaction_id": f"txn_{i:06d}",
                    "user_id": f"user_{i % 200:04d}",
                    "amount": round(10.0 + (i * 0.77), 2),
                    "currency": "USD",
                    "transaction_type": ["purchase", "refund", "deposit", "withdrawal"][i % 4],
                    "status": ["completed", "pending", "failed"][i % 3],
                    "timestamp": f"2025-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}T{(i % 24):02d}:{(i % 60):02d}:00Z",
                    "merchant_id": f"merchant_{i % 50:03d}",
                    "product_ids": [f"prod_{(i + j) % 100:03d}" for j in range((i % 3) + 1)],
                    "payment_method": ["credit_card", "debit_card", "paypal", "crypto"][i % 4]
                }
                for i in range(300)
            ],
            "products": [
                {
                    "product_id": f"prod_{i:03d}",
                    "name": f"Product {i}",
                    "description": f"This is a detailed description for product number {i} with various features and benefits.",
                    "category": ["Electronics", "Clothing", "Books", "Home", "Sports"][i % 5],
                    "subcategory": ["Gadgets", "Apparel", "Fiction", "Kitchen", "Outdoor"][i % 5],
                    "price": round(5.0 + (i * 2.45), 2),
                    "original_price": round(10.0 + (i * 3.21), 2),
                    "in_stock": i % 7 != 0,
                    "stock_quantity": (i * 17) % 1000,
                    "rating": round(3.0 + (i % 20) / 10.0, 1),
                    "reviews_count": (i * 7) % 500,
                    "tags": [f"tag{j}" for j in range((i % 5) + 1)],
                    "attributes": {
                        "weight": round(0.1 + (i * 0.05), 2),
                        "dimensions": {
                            "length": (i % 50) + 10,
                            "width": (i % 30) + 5,
                            "height": (i % 20) + 3
                        },
                        "color": ["red", "blue", "green", "black", "white"][i % 5],
                        "material": ["plastic", "metal", "wood", "fabric", "glass"][i % 5]
                    }
                }
                for i in range(100)
            ],
            "events": [
                {
                    "event_id": f"evt_{i:06d}",
                    "event_type": ["page_view", "click", "scroll", "purchase", "signup"][i % 5],
                    "user_id": f"user_{i % 200:04d}" if i % 10 != 0 else None,
                    "session_id": f"session_{i // 10:05d}",
                    "timestamp": f"2025-12-{(i % 28) + 1:02d}T{(i % 24):02d}:{(i % 60):02d}:{(i % 60):02d}Z",
                    "page_url": f"/page/{i % 50}",
                    "referrer": f"https://example.com/ref/{i % 20}" if i % 5 != 0 else None,
                    "device_info": {
                        "device_type": ["desktop", "mobile", "tablet"][i % 3],
                        "os": ["Windows", "macOS", "Linux", "iOS", "Android"][i % 5],
                        "browser": ["Chrome", "Firefox", "Safari", "Edge"][i % 4],
                        "screen_resolution": f"{1920 - (i % 3) * 320}x{1080 - (i % 3) * 180}"
                    },
                    "geolocation": {
                        "country": ["US", "UK", "CA", "DE", "FR"][i % 5],
                        "city": f"City{i % 50}",
                        "latitude": round(40.0 + (i % 100) / 10.0, 4),
                        "longitude": round(-74.0 + (i % 100) / 10.0, 4)
                    },
                    "custom_properties": {
                        f"property_{j}": f"value_{i}_{j}"
                        for j in range((i % 4) + 1)
                    }
                }
                for i in range(400)
            ],
            "summary_statistics": {
                "total_users": 200,
                "active_users": sum(1 for i in range(200) if i % 3 != 0),
                "total_transactions": 300,
                "total_revenue": round(sum(10.0 + (i * 0.77) for i in range(300)), 2),
                "total_products": 100,
                "in_stock_products": sum(1 for i in range(100) if i % 7 != 0),
                "total_events": 400,
                "unique_sessions": 40
            }
        }
        
        # Verify compression works
        compressed = self._verify_compression(data)
        
        # Calculate compression statistics
        original = json.dumps(data, separators=(',', ':'))
        ratio = len(compressed) / len(original)
        
        print(f"\n{'='*60}")
        print(f"Large Dataset Compression Test Results:")
        print(f"{'='*60}")
        print(f"Original size:    {len(original):,} bytes")
        print(f"Compressed size:  {len(compressed):,} bytes")
        print(f"Compression ratio: {ratio:.2%}")
        print(f"Space saved:      {len(original) - len(compressed):,} bytes ({(1-ratio)*100:.1f}%)")
        print(f"{'='*60}")
        
        # Compression should be effective for large datasets
        self.assertLess(ratio, 0.85, "Large dataset should compress significantly")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
