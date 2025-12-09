"""
Verification tool to measure JSON compression effectiveness.

This tool measures:
1. Character count reduction
2. Estimated token count reduction (using tiktoken if available)
3. Compression ratios for different types of JSON structures
4. Performance metrics

Run this to see how effective the compression is on various datasets.
"""

import json
import time
from typing import Dict, Any, List, Tuple
from json_compressor import compress_json, decompress_json

# Try to import tiktoken for accurate token counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("Note: tiktoken not installed. Using character-based estimation.")
    print("Install with: pip install tiktoken\n")


class CompressionVerifier:
    """Verify and measure compression effectiveness."""
    
    def __init__(self):
        """Initialize the verifier."""
        if TIKTOKEN_AVAILABLE:
            # Using cl100k_base encoding (used by GPT-4, GPT-3.5-turbo)
            self.encoding = tiktoken.get_encoding("cl100k_base")
        else:
            self.encoding = None
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken or estimation."""
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Rough estimation: average 4 characters per token
            return len(text) // 4
    
    def measure_compression(self, data: Any, name: str = "Data") -> Dict[str, Any]:
        """
        Measure compression effectiveness for given data.
        
        Returns metrics including size reduction and token savings.
        """
        # Original JSON (compact)
        original_json = json.dumps(data, separators=(',', ':'))
        original_chars = len(original_json)
        original_tokens = self.count_tokens(original_json)
        
        # Compress
        start_time = time.time()
        compressed_json = compress_json(data)
        compress_time = time.time() - start_time
        
        compressed_chars = len(compressed_json)
        compressed_tokens = self.count_tokens(compressed_json)
        
        # Decompress (verify correctness)
        start_time = time.time()
        decompressed = decompress_json(compressed_json)
        decompress_time = time.time() - start_time
        
        # Verify integrity
        is_valid = (data == decompressed)
        
        # Calculate metrics
        char_savings = original_chars - compressed_chars
        char_ratio = compressed_chars / original_chars if original_chars > 0 else 0
        
        token_savings = original_tokens - compressed_tokens
        token_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 0
        
        return {
            "name": name,
            "original_chars": original_chars,
            "compressed_chars": compressed_chars,
            "char_savings": char_savings,
            "char_ratio": char_ratio,
            "char_savings_pct": (1 - char_ratio) * 100,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "token_savings": token_savings,
            "token_ratio": token_ratio,
            "token_savings_pct": (1 - token_ratio) * 100,
            "compress_time_ms": compress_time * 1000,
            "decompress_time_ms": decompress_time * 1000,
            "is_valid": is_valid
        }
    
    def print_metrics(self, metrics: Dict[str, Any]):
        """Print compression metrics in a readable format."""
        print(f"\n{'='*70}")
        print(f"Dataset: {metrics['name']}")
        print(f"{'='*70}")
        print(f"Valid decompression: {'✓' if metrics['is_valid'] else '✗'}")
        print(f"\nCharacter Metrics:")
        print(f"  Original:   {metrics['original_chars']:,} chars")
        print(f"  Compressed: {metrics['compressed_chars']:,} chars")
        print(f"  Savings:    {metrics['char_savings']:,} chars ({metrics['char_savings_pct']:.1f}%)")
        print(f"  Ratio:      {metrics['char_ratio']:.2%}")
        
        print(f"\nToken Metrics:")
        print(f"  Original:   {metrics['original_tokens']:,} tokens")
        print(f"  Compressed: {metrics['compressed_tokens']:,} tokens")
        print(f"  Savings:    {metrics['token_savings']:,} tokens ({metrics['token_savings_pct']:.1f}%)")
        print(f"  Ratio:      {metrics['token_ratio']:.2%}")
        
        print(f"\nPerformance:")
        print(f"  Compression:   {metrics['compress_time_ms']:.2f} ms")
        print(f"  Decompression: {metrics['decompress_time_ms']:.2f} ms")
    
    def compare_datasets(self, datasets: List[Tuple[str, Any]]):
        """Compare compression across multiple datasets."""
        results = []
        
        for name, data in datasets:
            metrics = self.measure_compression(data, name)
            self.print_metrics(metrics)
            results.append(metrics)
        
        # Summary
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"{'Dataset':<30} {'Token Savings':<20} {'Char Savings':<20}")
        print(f"{'-'*70}")
        
        for r in results:
            print(f"{r['name']:<30} {r['token_savings_pct']:>6.1f}% ({r['token_ratio']:.2%})   "
                  f"{r['char_savings_pct']:>6.1f}% ({r['char_ratio']:.2%})")
        
        # Overall statistics
        avg_token_savings = sum(r['token_savings_pct'] for r in results) / len(results)
        avg_char_savings = sum(r['char_savings_pct'] for r in results) / len(results)
        
        print(f"\n{'Average Savings:':<30} {avg_token_savings:>6.1f}%              {avg_char_savings:>6.1f}%")


def create_test_datasets() -> List[Tuple[str, Any]]:
    """Create various test datasets for verification."""
    datasets = []
    
    # 1. Simple flat object
    datasets.append(("Simple Object", {
        "first_name": "John",
        "last_name": "Doe",
        "email_address": "john.doe@example.com",
        "phone_number": "+1-555-0123",
        "is_active": True,
        "account_balance": 1234.56
    }))
    
    # 2. Nested object
    datasets.append(("Nested Object", {
        "user_information": {
            "personal_details": {
                "full_name": "Alice Smith",
                "date_of_birth": "1990-05-15",
                "nationality": "USA"
            },
            "contact_information": {
                "primary_email": "alice@example.com",
                "secondary_email": "alice.smith@work.com",
                "phone_numbers": ["+1-555-1111", "+1-555-2222"]
            }
        },
        "account_settings": {
            "notification_preferences": {
                "email_notifications": True,
                "sms_notifications": False,
                "push_notifications": True
            }
        }
    }))
    
    # 3. Homogeneous array (best case)
    datasets.append(("Homogeneous Array (10 items)", {
        "products": [
            {
                "product_id": i,
                "product_name": f"Product {i}",
                "category_name": "Electronics",
                "price_amount": 99.99 + i,
                "stock_quantity": 100 - i,
                "is_available": True,
                "manufacturer_name": f"Manufacturer {i % 3}"
            }
            for i in range(10)
        ]
    }))
    
    # 4. Larger homogeneous array
    datasets.append(("Homogeneous Array (50 items)", {
        "records": [
            {
                "record_identifier": i,
                "timestamp_created": f"2025-12-{i%28+1:02d}T10:30:00Z",
                "user_identifier": f"user_{i}",
                "action_performed": "login" if i % 2 == 0 else "logout",
                "ip_address": f"192.168.1.{i % 255}",
                "session_duration_seconds": i * 60,
                "successful_operation": i % 3 != 0
            }
            for i in range(50)
        ]
    }))
    
    # 5. Deep nesting
    datasets.append(("Deeply Nested (6 levels)", {
        "organization_structure": {
            "company_name": "Tech Corp",
            "departments": {
                "engineering_department": {
                    "teams": {
                        "backend_team": {
                            "members": {
                                "senior_developers": [
                                    {"name": "Alice", "experience_years": 5},
                                    {"name": "Bob", "experience_years": 7}
                                ],
                                "junior_developers": [
                                    {"name": "Charlie", "experience_years": 1}
                                ]
                            }
                        }
                    }
                }
            }
        }
    }))
    
    # 6. API Response structure
    datasets.append(("API Response", {
        "status_code": 200,
        "status_message": "success",
        "timestamp": "2025-12-08T14:30:00Z",
        "response_data": {
            "user_list": [
                {
                    "user_id": 1001,
                    "username": "alice_cooper",
                    "email_address": "alice@example.com",
                    "full_name": "Alice Cooper",
                    "registration_date": "2024-01-15",
                    "last_login_date": "2025-12-07",
                    "is_verified": True,
                    "subscription_type": "premium"
                },
                {
                    "user_id": 1002,
                    "username": "bob_smith",
                    "email_address": "bob@example.com",
                    "full_name": "Bob Smith",
                    "registration_date": "2024-03-22",
                    "last_login_date": "2025-12-06",
                    "is_verified": True,
                    "subscription_type": "free"
                },
                {
                    "user_id": 1003,
                    "username": "charlie_brown",
                    "email_address": "charlie@example.com",
                    "full_name": "Charlie Brown",
                    "registration_date": "2024-06-10",
                    "last_login_date": "2025-12-05",
                    "is_verified": False,
                    "subscription_type": "free"
                }
            ],
            "pagination_info": {
                "current_page": 1,
                "total_pages": 10,
                "items_per_page": 3,
                "total_items": 30
            }
        }
    }))
    
    # 7. Mixed content
    datasets.append(("Mixed Content", {
        "configuration": {
            "server_settings": {
                "hostname": "api.example.com",
                "port_number": 8080,
                "use_ssl": True,
                "max_connections": 1000
            },
            "database_settings": {
                "connection_string": "postgresql://localhost:5432/mydb",
                "pool_size": 20,
                "timeout_seconds": 30
            },
            "feature_flags": {
                "enable_caching": True,
                "enable_logging": True,
                "debug_mode": False
            }
        },
        "log_entries": [
            {"timestamp": "2025-12-08T10:00:00Z", "level": "INFO", "message": "Server started"},
            {"timestamp": "2025-12-08T10:01:00Z", "level": "INFO", "message": "Database connected"},
            {"timestamp": "2025-12-08T10:05:00Z", "level": "WARNING", "message": "High memory usage"}
        ]
    }))
    
    # 8. Very long keys (extreme case)
    datasets.append(("Long Key Names", {
        "user_profile_information_container": {
            "personal_identification_number": 12345,
            "complete_legal_full_name": "John Doe",
            "primary_contact_email_address": "john@example.com",
            "residential_street_address_line_one": "123 Main St",
            "residential_city_municipality_name": "Springfield",
            "residential_state_province_region": "IL",
            "residential_postal_zip_code": "62701"
        }
    }))
    
    # 9. Already minified/single-line JSON (baseline case)
    datasets.append(("Already Minified JSON", {
        "users": [
            {"id": 1, "name": "A", "email": "a@x.co", "active": True, "score": 95},
            {"id": 2, "name": "B", "email": "b@x.co", "active": False, "score": 87},
            {"id": 3, "name": "C", "email": "c@x.co", "active": True, "score": 92},
            {"id": 4, "name": "D", "email": "d@x.co", "active": True, "score": 78},
            {"id": 5, "name": "E", "email": "e@x.co", "active": False, "score": 88}
        ],
        "meta": {"count": 5, "page": 1, "total": 100}
    }))
    
    return datasets


def main():
    """Run verification tests on various datasets."""
    print("JSON Compression Effectiveness Verification")
    print("=" * 70)
    
    if TIKTOKEN_AVAILABLE:
        print("Using tiktoken for accurate token counting (cl100k_base encoding)")
    else:
        print("Using character-based estimation (install tiktoken for accuracy)")
    
    verifier = CompressionVerifier()
    datasets = create_test_datasets()
    
    verifier.compare_datasets(datasets)
    
    print(f"\n{'='*70}")
    print("Verification complete!")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
