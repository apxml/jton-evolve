#!/usr/bin/env python3
"""
Manual Evolution Script for JSON Compressor

This script helps you manually evolve compression algorithms by:
1. Running evaluation on current version
2. Saving results and metrics
3. Managing different versions

Usage:
    python evolve.py evaluate <version>    # Evaluate a version
    python evolve.py compare               # Compare all versions
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from evaluator import evaluate

VERSIONS_DIR = Path("versions")
RESULTS_DIR = Path("results")


def ensure_dirs():
    """Ensure required directories exist."""
    VERSIONS_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)


def get_versions():
    """Get list of all versions."""
    if not VERSIONS_DIR.exists():
        return []
    return sorted([f.stem for f in VERSIONS_DIR.glob("v*.py")])


def evaluate_version(version_name):
    """
    Evaluate a specific version and save results.
    
    Args:
        version_name: Version name (e.g., 'v1', 'v2')
    """
    ensure_dirs()
    
    version_path = VERSIONS_DIR / f"{version_name}.py"
    if not version_path.exists():
        print(f"❌ Version {version_name} not found at {version_path}")
        return
    
    print(f"\n{'='*70}")
    print(f"Evaluating {version_name}")
    print(f"{'='*70}\n")
    
    # Run evaluation
    results = evaluate(str(version_path))
    
    # Add metadata
    results['version'] = version_name
    results['evaluated_at'] = datetime.now().isoformat()
    results['path'] = str(version_path)
    
    # Save results
    results_file = RESULTS_DIR / f"{version_name}_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"Results for {version_name}")
    print(f"{'='*70}\n")
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        if "traceback" in results:
            print(f"\nTraceback:\n{results['traceback']}")
    else:
        print(f"✅ Combined Score: {results['combined_score']:.2f}")
        print(f"\nCorrectness: {results['correctness']*100:.1f}% ({results['correct_datasets']}/{results['total_datasets']} datasets)")
        print(f"\nCompression Metrics:")
        print(f"  Character Ratio: {results['avg_compression_ratio']:.2%}")
        print(f"  Character Savings: {results['char_savings_pct']:.1f}%")
        print(f"  Token Ratio: {results['avg_token_ratio']:.2%}")
        print(f"  Token Savings: {results['token_savings_pct']:.1f}%")
        print(f"\nPerformance:")
        print(f"  Avg Time: {results['avg_time_ms']:.2f} ms per dataset")
        print(f"  Avg Compress Time: {results.get('avg_compress_time_ms', 0):.2f} ms per dataset")
        print(f"  Avg Decompress Time: {results.get('avg_decompress_time_ms', 0):.2f} ms per dataset")
        print(f"  Performance Penalty: {results['performance_penalty']:.3f}")
        print(f"\nTotal Stats:")
        print(f"  Original: {results['total_original_chars']:,} chars, {results['total_original_tokens']:,} tokens")
        print(f"  Compressed: {results['total_compressed_chars']:,} chars, {results['total_compressed_tokens']:,} tokens")
    
    print(f"\n{'='*70}")
    print(f"Results saved to {results_file}")
    print(f"{'='*70}\n")
    
    return results


def compare_versions():
    """Compare all versions and show the best one."""
    ensure_dirs()
    
    versions = get_versions()
    if not versions:
        print("❌ No versions found in versions/ directory")
        return
    
    print(f"\n{'='*70}")
    print("Comparing All Versions")
    print(f"{'='*70}\n")
    
    all_results = []
    
    for version in versions:
        results_file = RESULTS_DIR / f"{version}_results.json"
        
        if results_file.exists():
            with open(results_file) as f:
                results = json.load(f)
        else:
            print(f"⚠️  No cached results for {version}, evaluating now...")
            results = evaluate_version(version)
        
        all_results.append({
            'version': version,
            'score': results.get('combined_score', 0),
            'correctness': results.get('correctness', 0),
            'token_savings': results.get('token_savings_pct', 0),
            'char_savings': results.get('char_savings_pct', 0),
            'compress_time': results.get('avg_compress_time_ms', 0),
            'decompress_time': results.get('avg_decompress_time_ms', 0),
            'has_error': 'error' in results
        })
    
    # Sort by score
    all_results.sort(key=lambda x: x['score'], reverse=True)
    
    # Display comparison table
    print(f"\n{'Version':<10} {'Score':<12} {'Correctness':<15} {'Token Savings':<15} {'Compress':<12} {'Decompress':<12} {'Status':<10}")
    print("-" * 100)
    
    for r in all_results:
        status = "❌ ERROR" if r['has_error'] else "✅ OK"
        compress_time = f"{r.get('compress_time', 0):.3f}ms" if not r['has_error'] else "N/A"
        decompress_time = f"{r.get('decompress_time', 0):.3f}ms" if not r['has_error'] else "N/A"
        print(f"{r['version']:<10} {r['score']:<12.2f} {r['correctness']*100:<14.1f}% "
              f"{r['token_savings']:<14.1f}% {compress_time:<12} {decompress_time:<12} {status:<10}")
    
    # Show best version
    if all_results:
        best = all_results[0]
        if not best['has_error']:
            print(f"\n{'='*70}")
            print(f"🏆 Best Version: {best['version']} (Score: {best['score']:.2f})")
            print(f"{'='*70}\n")


def create_new_version():
    """Create a new version by copying the latest."""
    ensure_dirs()
    
    versions = get_versions()
    if not versions:
        print("❌ No versions found. Please create v1.py first.")
        return
    
    # Get latest version number
    latest = versions[-1]
    latest_num = int(latest[1:])
    new_num = latest_num + 1
    new_version = f"v{new_num}"
    
    # Copy latest to new version
    src = VERSIONS_DIR / f"{latest}.py"
    dst = VERSIONS_DIR / f"{new_version}.py"
    
    shutil.copy(src, dst)
    
    print(f"✅ Created {new_version}.py from {latest}.py")
    print(f"   Path: {dst}")
    print(f"\n   Edit this file to implement your improvements!")


def list_versions():
    """List all available versions."""
    ensure_dirs()
    
    versions = get_versions()
    if not versions:
        print("❌ No versions found in versions/ directory")
        return
    
    print(f"\n{'='*70}")
    print("Available Versions")
    print(f"{'='*70}\n")
    
    for version in versions:
        version_path = VERSIONS_DIR / f"{version}.py"
        results_file = RESULTS_DIR / f"{version}_results.json"
        
        status = "✅ Evaluated" if results_file.exists() else "⚠️  Not evaluated"
        print(f"{version:<10} {status:<20} {version_path}")
    
    print()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("JSON Compressor Evolution Tool")
        print("\nUsage:")
        print("  python evolve.py evaluate <version>   # Evaluate a specific version (e.g., v1)")
        print("  python evolve.py compare              # Compare all versions")
        print("  python evolve.py new                  # Create new version from latest")
        print("  python evolve.py list                 # List all versions")
        print("\nExamples:")
        print("  python evolve.py evaluate v1")
        print("  python evolve.py compare")
        print("  python evolve.py new")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "evaluate":
        if len(sys.argv) < 3:
            print("❌ Please specify a version to evaluate (e.g., v1)")
            sys.exit(1)
        version = sys.argv[2]
        evaluate_version(version)
    
    elif command == "compare":
        compare_versions()
    
    elif command == "new":
        create_new_version()
    
    elif command == "list":
        list_versions()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Valid commands: evaluate, compare, new, list")
        sys.exit(1)


if __name__ == "__main__":
    main()
