"""
Evaluator for JSON Compression

This evaluator measures the effectiveness of JSON compression strategies:
1. Compression ratio (smaller is better)
2. Token savings (using tiktoken if available)
3. Correctness (must decompress to original)
4. Performance (compression/decompression speed)

The combined_score is calculated to reward better compression while
penalizing incorrect decompression or poor performance.
"""

import json
import time
import importlib.util
import traceback
from typing import Dict, Any, List, Tuple

# Try to import tiktoken for accurate token counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
    ENCODING = tiktoken.get_encoding("cl100k_base")
except ImportError:
    TIKTOKEN_AVAILABLE = False
    ENCODING = None


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken or estimation."""
    if ENCODING:
        return len(ENCODING.encode(text))
    else:
        # Rough estimation: average 4 characters per token
        return len(text) // 4


def create_test_datasets() -> List[Tuple[str, Any]]:
    """Create various test datasets for evaluation."""
    datasets = []
    
    # 1. Simple flat object
    datasets.append(("simple", {
        "first_name": "John",
        "last_name": "Doe",
        "email_address": "john.doe@example.com",
        "phone_number": "+1-555-0123",
        "is_active": True,
        "account_balance": 1234.56
    }))
    
    # 2. Nested object
    datasets.append(("nested", {
        "user_information": {
            "personal_details": {
                "full_name": "Alice Smith",
                "date_of_birth": "1990-05-15"
            },
            "contact_information": {
                "primary_email": "alice@example.com",
                "phone_numbers": ["+1-555-1111", "+1-555-2222"]
            }
        }
    }))
    
    # 3. Homogeneous array (best case for compression)
    datasets.append(("homogeneous_array", {
        "products": [
            {
                "product_id": i,
                "product_name": f"Product {i}",
                "category_name": "Electronics",
                "price_amount": 99.99 + i,
                "stock_quantity": 100 - i,
                "is_available": True
            }
            for i in range(20)
        ]
    }))
    
    # 4. API Response structure
    datasets.append(("api_response", {
        "status_code": 200,
        "status_message": "success",
        "response_data": {
            "user_list": [
                {
                    "user_id": 1001 + i,
                    "username": f"user_{i}",
                    "email_address": f"user{i}@example.com",
                    "registration_date": "2024-01-15",
                    "is_verified": i % 2 == 0,
                    "subscription_type": "premium" if i % 3 == 0 else "free"
                }
                for i in range(15)
            ]
        }
    }))
    
    # 5. Deep nesting
    datasets.append(("deep_nesting", {
        "level1": {
            "level2": {
                "level3": {
                    "level4": {
                        "level5": {
                            "data_value": "deep",
                            "count_number": 5
                        }
                    }
                }
            }
        }
    }))
    
    # 6. Mixed naming conventions and string patterns
    datasets.append(("naming_conventions", {
        "pascal_case_items": [
            {
                "item_id": i,
                "UserAccount": f"UserAccount{i}",
                "UserProfile": f"UserProfile{i}",
                "UserSettings": f"UserSettings{i}"
            }
            for i in range(10)
        ],
        "camel_case_items": [
            {
                "item_id": i,
                "userId": f"userId{i}",
                "userName": f"userName{i}",
                "userEmail": f"userEmail{i}"
            }
            for i in range(10)
        ],
        "email_addresses": [
            f"person{i}@example.com" for i in range(15)
        ],
        "api_urls": [
            f"https://api.example.com/v1/users/{i}" for i in range(12)
        ]
    }))
    
    return datasets


def evaluate(program_path: str) -> Dict[str, Any]:
    """
    Evaluate a JSON compression program.
    
    Args:
        program_path: Path to the Python file containing compression functions
        
    Returns:
        Dictionary with evaluation metrics including combined_score
    """
    try:
        # Load the program
        spec = importlib.util.spec_from_file_location("compressor_module", program_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Get the compression functions
        if not hasattr(module, 'compress_json') or not hasattr(module, 'decompress_json'):
            return {
                "combined_score": 0.0,
                "error": "Missing compress_json or decompress_json functions",
                "correctness": 0.0,
                "avg_compression_ratio": 0.0,
                "avg_token_savings_pct": 0.0
            }
        
        compress_json = module.compress_json
        decompress_json = module.decompress_json
        
        # Test on multiple datasets
        datasets = create_test_datasets()
        
        total_original_chars = 0
        total_compressed_chars = 0
        total_original_tokens = 0
        total_compressed_tokens = 0
        total_compress_time = 0
        total_decompress_time = 0
        correct_count = 0
        
        for name, data in datasets:
            try:
                # Original JSON
                original_json = json.dumps(data, separators=(',', ':'))
                original_chars = len(original_json)
                original_tokens = count_tokens(original_json)
                
                # Run compression 5 times and average
                compress_times = []
                compressed_json = None
                for _ in range(5):
                    start_time = time.time()
                    compressed_json = compress_json(data)
                    compress_times.append(time.time() - start_time)
                compress_time = sum(compress_times) / len(compress_times)
                
                compressed_chars = len(compressed_json)
                compressed_tokens = count_tokens(compressed_json)
                
                # Run decompression 5 times and average
                decompress_times = []
                decompressed = None
                for _ in range(5):
                    start_time = time.time()
                    decompressed = decompress_json(compressed_json)
                    decompress_times.append(time.time() - start_time)
                decompress_time = sum(decompress_times) / len(decompress_times)
                
                # Verify correctness
                is_correct = (data == decompressed)
                
                if is_correct:
                    correct_count += 1
                    total_original_chars += original_chars
                    total_compressed_chars += compressed_chars
                    total_original_tokens += original_tokens
                    total_compressed_tokens += compressed_tokens
                    total_compress_time += compress_time
                    total_decompress_time += decompress_time
                    
            except Exception as e:
                # Dataset failed - skip it
                continue
        
        # Calculate metrics
        if correct_count == 0:
            return {
                "combined_score": 0.0,
                "correctness": 0.0,
                "avg_compression_ratio": 1.0,
                "avg_token_savings_pct": 0.0,
                "error": "No datasets passed correctness check"
            }
        
        correctness_rate = correct_count / len(datasets)
        
        # Compression metrics (only for correct cases)
        avg_char_ratio = total_compressed_chars / total_original_chars if total_original_chars > 0 else 1.0
        avg_token_ratio = total_compressed_tokens / total_original_tokens if total_original_tokens > 0 else 1.0
        
        char_savings_pct = (1 - avg_char_ratio) * 100
        token_savings_pct = (1 - avg_token_ratio) * 100
        
        # Performance penalty for slow operations (over 10ms per dataset)
        avg_time_ms = ((total_compress_time + total_decompress_time) / correct_count) * 1000
        performance_penalty = max(0, min(1, (avg_time_ms - 10) / 100))  # Penalty 0-1
        
        # Combined score: higher is better
        # Rewards: token savings, correctness
        # Penalties: slow performance
        combined_score = (
            token_savings_pct * 2.0 +  # Primary: token savings
            char_savings_pct * 1.0 +   # Secondary: character savings
            correctness_rate * 50.0 -   # Must be correct
            performance_penalty * 10.0  # Performance penalty
        )
        
        # Ensure non-negative
        combined_score = max(0.0, combined_score)
        
        return {
            "combined_score": combined_score,
            "correctness": correctness_rate,
            "correct_datasets": correct_count,
            "total_datasets": len(datasets),
            "avg_compression_ratio": avg_char_ratio,
            "char_savings_pct": char_savings_pct,
            "avg_token_ratio": avg_token_ratio,
            "token_savings_pct": token_savings_pct,
            "avg_time_ms": avg_time_ms,
            "avg_compress_time_ms": (total_compress_time / correct_count) * 1000,
            "avg_decompress_time_ms": (total_decompress_time / correct_count) * 1000,
            "performance_penalty": performance_penalty,
            "total_original_chars": total_original_chars,
            "total_compressed_chars": total_compressed_chars,
            "total_original_tokens": total_original_tokens,
            "total_compressed_tokens": total_compressed_tokens
        }
        
    except Exception as e:
        return {
            "combined_score": 0.0,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "correctness": 0.0,
            "avg_compression_ratio": 1.0,
            "avg_token_savings_pct": 0.0
        }





if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python evaluator.py <program_path>")
        sys.exit(1)
    
    program_path = sys.argv[1]
    results = evaluate(program_path)
    
    print("\n" + "="*70)
    print("JSON Compression Evaluation Results")
    print("="*70)
    
    if "error" in results:
        print(f"\n❌ Error: {results['error']}")
        if "traceback" in results:
            print(f"\nTraceback:\n{results['traceback']}")
    else:
        print(f"\n✅ Combined Score: {results['combined_score']:.2f}")
        print(f"\nCorrectness: {results['correctness']*100:.1f}% ({results['correct_datasets']}/{results['total_datasets']} datasets)")
        print(f"\nCompression Metrics:")
        print(f"  Character Ratio: {results['avg_compression_ratio']:.2%}")
        print(f"  Character Savings: {results['char_savings_pct']:.1f}%")
        print(f"  Token Ratio: {results['avg_token_ratio']:.2%}")
        print(f"  Token Savings: {results['token_savings_pct']:.1f}%")
        print(f"\nPerformance:")
        print(f"  Avg Time: {results['avg_time_ms']:.2f} ms per dataset")
        print(f"  Avg Compress Time: {results['avg_compress_time_ms']:.2f} ms per dataset")
        print(f"  Avg Decompress Time: {results['avg_decompress_time_ms']:.2f} ms per dataset")
        print(f"  Performance Penalty: {results['performance_penalty']:.3f}")
        print(f"\nTotal Stats:")
        print(f"  Original: {results['total_original_chars']:,} chars, {results['total_original_tokens']:,} tokens")
        print(f"  Compressed: {results['total_compressed_chars']:,} chars, {results['total_compressed_tokens']:,} tokens")
    
    print("\n" + "="*70)
