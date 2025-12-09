# JTON - JSON Token Optimized Notation

**JTON** (JSON Token Optimized Notation) is an LLM-evolved compression format that minimizes token count for AI consumption. Through 32 generations of evolution using the AlphaEvolve methodology, JTON achieved **62.2% token savings** while maintaining perfect correctness.

Available in two formats:
- **Human-Readable**: 57.5% token reduction with readable structure
- **Machine-Optimized**: 62.2% token reduction with maximum compression

> **Note**: This is an experimental project exploring how LLMs can evolve algorithms through iteration. It's meant to be educational, fun, and a demonstration of AI-assisted algorithm optimization!

## What It Does

JTON uses LLMs to evolve JSON compression algorithms that minimize token count for AI/LLM consumption. The AlphaEvolve approach enabled discovering novel compression strategies through:

- **Iterative Evolution**: LLM generates improved versions based on previous performance
- **Token-Aware Optimization**: Directly optimizes for LLM token count (not just character count)
- **Comprehensive Evaluation**: Tests compression on diverse real-world datasets
- **Performance Tracking**: Compare all versions to identify breakthrough improvements
- **Multi-Strategy Discovery**: Found both human-readable (57.5%) and optimized (62.2%) solutions

## Two Formats

After 32 generations of LLM-driven evolution, JTON offers two optimized formats:

### JTON-Machine (v27-v31)
**62.2% token savings** - Machine-optimized binary format prioritizing maximum compression
```python
from compressed_optimized import compress_json, decompress_json

# Small data: Overhead > savings (no compression benefit)
small = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
compressed_small = compress_json(small)  # Returns original - not worth compressing

# Large repeated structures: Excellent compression (77%+ savings)
large = {
    "products": [
        {"product_id": i, "name": f"Product {i}", "price": 10.0 + i, "in_stock": True}
        for i in range(1, 21)
    ]
}
compressed = compress_json(large)  # 1336 → 302 chars (77.4% savings)
original = decompress_json(compressed)  # Perfect reconstruction
```

### JTON-Human (v8-v20)
**56.8% token savings** - Human-readable format with strong compression
```python
from compressed_readable import compress_json, decompress_json

# Small data: Overhead > savings (no compression benefit)
small = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
compressed_small = compress_json(small)  # Returns original - not worth compressing

# Large repeated structures: Strong compression (67%+ savings)
large = {
    "products": [
        {"product_id": i, "name": f"Product {i}", "price": 10.0 + i, "in_stock": True}
        for i in range(1, 21)
    ]
}
compressed = compress_json(large)  # 1336 → 441 chars (67.0% savings)
original = decompress_json(compressed)  # Perfect reconstruction
```

## Quick Start

### Installation

```bash
# Clone or download the project
cd jton

# Install dependencies
pip install -r requirements.txt
```

### Use the Best Performing Versions

Use the evolved algorithms directly:

```python
# JTON-Machine: Maximum compression (62.2% token reduction on average)
from compressed_optimized import compress_json, decompress_json
import json

# JTON-Human: Readable compression (56.8% token reduction on average)
# from compressed_readable import compress_json, decompress_json

# Example: Array of structured objects (where JTON excels)
data = {
    "products": [
        {"product_id": i, "name": f"Product {i}", "price": 10.0 + i, "in_stock": True}
        for i in range(1, 21)  # 20 products with consistent structure
    ]
}

original_size = len(json.dumps(data, separators=(',', ':')))

# Compress (returns compact JSON string)
compressed = compress_json(data)
print(f"Original: {original_size} chars")
print(f"Compressed: {len(compressed)} chars")
print(f"Savings: {((original_size - len(compressed)) / original_size * 100):.1f}%")
# Output: 77.4% savings (1336 → 302 chars)

# Decompress (returns original data)
decompressed = decompress_json(compressed)
assert data == decompressed  # Perfect reconstruction

# Note: Small objects may not compress well due to overhead
small_data = {"id": 1, "name": "Alice"}
small_compressed = compress_json(small_data)  # Returns original if not beneficial
```

### Continue the Evolution

Evaluate any version from the evolutionary process:

```bash
python evolve.py evaluate v27
```

The evaluation:
1. Loads the version from `versions/v27.py`
2. Tests it on multiple diverse datasets
3. Calculates compression metrics and token savings
4. Saves results to `results/v27_results.json`

### Compare All Versions

```bash
python evolve.py compare
```

Shows a comparison table of all 32 evolved versions with their scores and metrics.

### Evolve New Versions

```bash
python evolve.py new
```

Creates a new version file by copying the latest version. Use an LLM to implement improvements based on the evaluation results!

## Evolution Performance Summary

Through 32 generations, the LLM discovered increasingly sophisticated strategies:

| Generation | Best Score | Token Savings | Primary Innovation |
|------------|-----------|---------------|----------------|
| **v1-v5** | 171.81 - 200.03 | 35.4% - 46.7% | Basic key mapping + columnar arrays |
| **v8-v20** | 227.93 | **56.8%** | **Best human-readable format** |
| **v21** | 228.87 | 56.8% | Transition to non-readable optimization |
| **v22-v25** | 230.75 | 57.5% | Binary encoding + bit-packing |
| **v27-v31** | 244.28 | **62.2%** | **Maximum optimization achieved** |

### Evolution Progress

![JTON Evolution Progress](https://raw.githubusercontent.com/apxml/jton-evolve/refs/heads/main/chart.jpg)

*Chart showing the improvement in compression performance across all 32 generations of evolution*

### Full Results (Top Performers)

```
Version    Score    Correctness  Token Savings  Compress   Decompress  Type
-------------------------------------------------------------------------------------
v27-v31    244.28   100.0%       62.2%         0.049ms    0.029ms     ✅ Maximum
v22-v25    230.75   100.0%       57.5%         0.047ms    0.029ms     ✅ Binary
v8-v20     227.93   100.0%       56.8%         0.042ms    0.022ms     ✅ Readable
v1         171.81   100.0%       35.4%         0.050ms    0.021ms     ✅ Baseline
```

### Evolved Strategies

The evolution process discovered:

- **Binary Packing**: Struct-based encoding for numeric arrays (v8+)
- **Boolean Bit-Packing**: 8 booleans per byte instead of individual values (v22+)
- **Prefix Detection**: Common string prefix extraction (v26-v27)
- **Scaled Float Encoding**: Pack floats as scaled integers (v27+)
- **Multiple Integer Formats**: Unsigned/signed 8/16/32-bit optimization (v27+)
- **Aggressive Key Compression**: Compress ALL keys regardless of length (v22+)
- **Smart Thresholds**: Dynamic compression based on data characteristics

## Technical Details: Final Optimization Strategies

After 32 generations of evolution, the algorithm discovered two distinct optimization peaks. Here's how they work:

### JTON-Machine (v27-v31): Maximum Compression

The machine-optimized format achieves **62.2% token reduction** through aggressive optimization:

#### 1. **Ultra-Compact Key Mapping**
All object keys are replaced with base62-encoded integers, regardless of length:
```python
# Before: {"product_id": 1, "name": "Product 1", "in_stock": true}
# After:  {"0": 1, "1": "Product 1", "2": true}
# Keys stored in header: {"m": {"product_id": "0", "name": "1", "in_stock": "2"}}
```

#### 2. **Multiple Numeric Packing Formats**
Numbers are analyzed and packed using the most efficient format:

| Format | Range | Bytes/Value | Prefix |
|--------|-------|-------------|--------|
| Unsigned 8-bit | 0-255 | 1 | `U` |
| Signed 8-bit | -128 to 127 | 1 | `B` |
| Unsigned 16-bit | 0-65535 | 2 | `V` |
| Signed 16-bit | -32768 to 32767 | 2 | `H` |
| Signed 32-bit | Other integers | 4 | `I` |
| Scaled Float | Floats (2 decimals) | 2 | `F` |
| Double | Other floats | 8 | `D` |

Example:
```python
# IDs 1-100 → "U" + base64(bytes([1,2,3,...,100]))
# Prices with 2 decimals → "F" + base64(scaled_shorts)
```

#### 3. **Boolean Bit-Packing**
8 booleans packed per byte with count suffix:
```python
# [True, False, True, True, False, False, False, True]
# → "T" + base64(byte with bits: 10110001) + "~8"
```

#### 4. **String Prefix Extraction**
Detects common prefixes (min 2 chars) in string arrays:
```python
# ["user_alice", "user_bob", "user_charlie"]
# → {"p": "user_", "x": ["alice", "bob", "charlie"]}
```

#### 5. **Columnar Array Format**
Homogeneous object arrays converted to column-oriented storage:
```python
# Original: [{"id": 1, "name": "A"}, {"id": 2, "name": "B"}]
# Compressed: {"a": 1, "k": ["0","1"], "d": [
#   "U" + base64([1,2]),           # id column packed
#   ["A", "B"]                      # name column
# ]}
```

#### 6. **Pattern Detection**
- **Sequential**: `[1,2,3,4,5]` → `{"s": 1, "d": 1, "n": 5}`
- **Constant**: `[true,true,true]` → `{"c": true, "n": 3}`

#### 7. **Smart Fallback**
Returns original JSON if compression overhead exceeds savings.

### JTON-Human (v8-v20, v22): Readable Compression

The human-readable format achieves **56.8% token reduction** while maintaining structure:

#### Differences from Machine Format:

1. **Readable Prefixes**: Single-character type indicators
   - `B` = signed byte array
   - `H` = signed short array  
   - `I` = signed int array
   - `D` = double array
   - `T` = boolean bit-packed
   - `S` = base64-encoded string

2. **Fewer Numeric Formats**: 4 formats instead of 7
   - Signed 8-bit, 16-bit, 32-bit, or double
   - No unsigned or scaled float optimization

3. **Higher Thresholds**: 
   - String encoding threshold: 20 chars (vs 15)
   - No prefix extraction for strings
   - Key compression for all keys

4. **Same Core Techniques**:
   - Columnar arrays for homogeneous objects
   - Boolean bit-packing (8 per byte)
   - Sequential/constant pattern detection
   - Smart fallback to original

### Example: Product Array Compression

Given this data with 20 products (sequential IDs, sequential prices, constant booleans):
```python
data = {
    "products": [
        {"product_id": i, "name": f"Product {i}", "price": 10.0 + i, "in_stock": True}
        for i in range(1, 21)
    ]
}
```

**Original JSON (1336 chars, 444 tokens):**
```json
{"products":[{"product_id":1,"name":"Product 1","price":11.0,"in_stock":true},{"product_id":2,"name":"Product 2","price":12.0,"in_stock":true},...]}
```

**JTON-Machine (302 chars, 130 tokens - 70.7% token reduction):**

Intelligently detects patterns and uses the most efficient encoding:
```json
{"d":{"0":{"a":1,"k":["1","2","3","4"],"d":[{"s":1,"d":1,"n":20},{"p":"Product ","x":["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20"]},{"s":11.0,"d":1.0,"n":20},{"c":true,"n":20}]}},"m":{"products":"0","product_id":"1","name":"2","price":"3","in_stock":"4"}}
```
- **Product IDs**: Sequential pattern `{"s":1,"d":1,"n":20}` (start=1, delta=1, count=20)
- **Names**: String prefix extraction `{"p":"Product ","x":["1","2",..."20"]}`
- **Prices**: Sequential floats `{"s":11.0,"d":1.0,"n":20}`
- **Booleans**: Constant value `{"c":true,"n":20}`

**JTON-Human (441 chars, 165 tokens - 62.8% token reduction):**
```json
{"d":{"0":{"a":1,"k":["1","2","3","4"],"d":[{"s":1,"d":1,"n":20},["Product 1","Product 2","Product 3","Product 4","Product 5","Product 6","Product 7","Product 8","Product 9","Product 10","Product 11","Product 12","Product 13","Product 14","Product 15","Product 16","Product 17","Product 18","Product 19","Product 20"],{"s":11.0,"d":1.0,"n":20},{"c":true,"n":20}]}},"m":{"products":"0","product_id":"1","name":"2","price":"3","in_stock":"4"}}
```
- Human-readable with full product names instead of prefix extraction

**When data has no patterns, JTON-Machine uses binary encoding:**
```json
{"d":{"0":{"a":1,"k":["1","2","3","4"],"d":["UAQUDCAIPBx...",{"p":"Product ","x":[...]},"DAAAA...==","TrbUG~20"]}},"m":{...}}
```
- Integers → Base64-encoded binary (prefix `U`, `B`, `V`, `H`, `I`, `F`, or `D`)
- Booleans → Bit-packed (8 bools per byte)

### When JTON Excels

✅ **Best Cases (70-80% reduction):**
- Arrays of 10+ similar objects
- Repeated keys/structures
- Numeric sequences or patterns
- Boolean flags in arrays
- API responses with consistent schemas

❌ **Poor Cases (0% reduction, returns original):**
- Small objects (<5 fields)
- Highly variable structures
- Unique string values
- Deep nesting without repetition

### Performance Characteristics

Both formats maintain:
- **100% correctness** (perfect reconstruction)
- **Sub-millisecond** compression/decompression
- **Memory efficient** (streaming-compatible design)
- **No dependencies** beyond Python stdlib

## The AlphaEvolve Methodology

This project demonstrates using LLMs to automatically evolve algorithms through iterative improvement:

1. **Initialize**: Start with a baseline implementation (v1)
2. **Evaluate**: Test on diverse datasets and measure performance
3. **Evolve**: LLM generates improved version based on results and code analysis
4. **Compare**: Rank all versions to identify best approaches
5. **Iterate**: Repeat until convergence or breakthrough discoveries occur

### Evaluation Metrics

The evaluator tests each algorithm on diverse datasets:

- **Simple objects**: Flat key-value structures
- **Nested objects**: Multi-level hierarchies
- **Homogeneous arrays**: Arrays of similar objects (best case)
- **API responses**: Real-world REST API structures
- **Deep nesting**: 5+ levels of nested objects

### Scoring Formula

```python
combined_score = (
    token_savings_pct * 2.0 +      # Primary metric (maximize)
    char_savings_pct * 1.0 +        # Secondary metric
    correctness_rate * 50.0 -       # Must be 100% correct
    performance_penalty * 10.0      # Must be fast enough
)
```

Perfect correctness is essential - any version with errors scores poorly.

## Project Structure

```
jton/
├── compressed_optimized.py   # JTON-Machine format (v27 - 62.2% savings)
├── compressed_readable.py    # JTON-Human format (v8-v20 - 56.8% savings)
│
├── versions/                 # All 32 evolved versions (v1-v32)
│   ├── v1.py                # Baseline (35.4% savings)
│   ├── v8.py                # Best readable (56.8% savings)
│   ├── v27.py               # Maximum optimization (62.2% savings)
│   └── ...                  # Other evolutionary steps
│
├── results/                 # Evaluation results for each version
│   ├── v1_results.json
│   ├── v27_results.json
│   └── ...
│
├── evaluator.py            # Evaluation metrics and test datasets
├── evolve.py               # Evolution management tool
├── requirements.txt        # Dependencies
├── README.md               # This file
│
├── json_compressor.py      # Reference implementation
├── test_compressor.py      # Comprehensive test suite
└── verify_compression.py   # Verification tool
```

## Evolution Tool Usage

The `evolve.py` script helps manage versions:

```bash
# List all versions
python evolve.py list

# Evaluate a specific version
python evolve.py evaluate v1

# Compare all versions
python evolve.py compare

# Create new version from latest
python evolve.py new
```

## Reproduction & Extension

To reproduce or extend this evolution experiment:

1. **Review the evolution**: `python evolve.py compare`
2. **Study best versions**: Examine [compressed_optimized.py](compressed_optimized.py) and [compressed_readable.py](compressed_readable.py)
3. **Create new version**: `python evolve.py new` (creates v33.py)
4. **Use LLM to evolve**: Provide the LLM with:
   - Current version code
   - Evaluation results from `python evolve.py compare`
   - Ideas for improvement
5. **Evaluate new version**: `python evolve.py evaluate v33`
6. **Compare results**: `python evolve.py compare`
7. **Iterate**: Repeat until you discover better strategies!

### How to Run an Evolution Iteration

You can use **AI coding agents** like GitHub Copilot, Cursor, Windsurf, or any AI-powered IDE to evolve the algorithm. Here's the workflow:

#### Using AI Coding Agents (GitHub Copilot, Cursor, Windsurf, etc.)

1. **Check current performance**:
   ```bash
   python evolve.py compare
   ```

2. **Ask the AI agent** to create and improve the next version:
   ```
   @workspace Create versions/v33.py by copying v32.py and improve the compression algorithm.
   
   Current best performance:
   - v27-v31: 62.2% token savings, 244.28 score
   - v22: 57.5% token savings (best readable)
   
   Potential new compression strategies that could beat 62.2%:
   - Better string prefix detection
   - Value dictionaries for repeated strings
   - More efficient encoding schemes
   - Pattern-specific optimizations
   
   Maintain 100% correctness and keep the compress_json/decompress_json API.
   ```

3. **Test the new version**:
   ```bash
   python evolve.py evaluate v33
   ```

4. **Compare results**:
   ```bash
   python evolve.py compare
   ```

5. **Iterate**: If v33 improves, ask the agent to create v34! If not, try different approaches.

#### Manual Iteration (Optional)

For manual control or terminal usage:

1. **Create new version**:
   ```bash
   python evolve.py new  # Creates v33.py from v32.py
   ```

2. **Edit the file** with a preferred editor and implement improvements

3. **Test and compare**:
   ```bash
   python evolve.py evaluate v33
   python evolve.py compare
   ```

#### Tips for Evolution

- **Try wild ideas**: Some breakthroughs (like v8's binary packing) came from bold changes
- **Watch the metrics**: Token savings is the main metric, but balance with performance
- **Embrace failure**: Many versions won't improve - that's part of evolution!
- **Test correctness**: Always verify `python test_compressor.py` passes
- **Focus on patterns**: Identify which datasets compress poorly and target them

### Main Insights from Evolution

- **Generations 1-7**: Gradual improvements through better thresholds and encoding
- **Generation 8**: Breakthrough with columnar arrays (35% → 56.8% savings)
- **Generations 9-20**: Refinement and stability at 56.8% (best readable format)
- **Generation 21**: Transition to binary/non-readable format (56.8%)
- **Generations 22-25**: Binary encoding improvements (57.5%)
- **Generations 26-27**: Breakthrough with advanced binary packing (62.2%)
- **Generations 28-31**: Convergence - maximum optimization achieved

## Advanced Usage

### Use in Production

```python
# For maximum compression in production (e.g., storing data, API payloads)
from compressed_optimized import compress_json, decompress_json

# Compress before sending to LLM or storing
data = {"large": "dataset", "with": ["many", "items"]}
compressed_str = compress_json(data)

# Send compressed_str to LLM or store it...

# Decompress when needed
original_data = decompress_json(compressed_str)
```

### Compare Specific Versions

```python
from evaluator import evaluate
import json

# Compare baseline vs optimized
with open('results/v1_results.json') as f:
    v1 = json.load(f)
with open('results/v27_results.json') as f:
    v27 = json.load(f)

print(f"V1 (Baseline) Score: {v1['combined_score']:.2f}")
print(f"V27 (Optimized) Score: {v27['combined_score']:.2f}")
print(f"Improvement: {v27['combined_score'] - v1['combined_score']:.2f}")
print(f"Token savings gain: {v27['avg_token_savings'] - v1['avg_token_savings']:.1f}%")
```

### Add Custom Test Datasets

Edit `evaluator.py` and add to the `create_test_datasets()` function:

```python
# Add your custom dataset
datasets.append(("my_dataset", {
    "your": "data",
    "goes": "here"
}))
```

### Run Tests

Comprehensive test suite:

```bash
python test_compressor.py
```

## Performance Characteristics

### JTON-Machine (v27) - For AI/LLM Consumption

- **Token Savings**: 62.2% average (up to 80%+ on homogeneous arrays)
- **Character Savings**: ~70%
- **Correctness**: 100% (perfect reconstruction)
- **Compression Time**: 0.049ms per dataset
- **Decompression Time**: 0.029ms per dataset
- **Output**: Machine-optimized, maximally compact
- **Use Case**: Production AI/LLM payloads, API responses, storage

### JTON-Human (v8-v20) - For Human Readability

- **Token Savings**: 56.8% average
- **Character Savings**: ~64%
- **Correctness**: 100% (perfect reconstruction)
- **Compression Time**: 0.042ms per dataset
- **Decompression Time**: 0.022ms per dataset
- **Output**: Human-readable JSON structure
- **Use Case**: Debugging, development, human review

### Token Savings by Data Type

Test results showing token reduction for different data structures:

#### JTON-Machine (v27) - Maximum Compression

| Data Type | Token Reduction | Original → Compressed | Description |
|-----------|----------------|----------------------|-------------|
| **Homogeneous arrays** | **76.3%** | 704 → 167 tokens | Product lists, similar objects |
| **API responses** | **58.6%** | 619 → 256 tokens | User lists, structured records |
| **String patterns** | **20.0%** | 685 → 548 tokens | Emails, URLs, mixed patterns |
| **Simple objects** | **0%** | No reduction | Overhead > savings for small data |
| **Deep nesting** | **0%** | No reduction | Overhead > savings for small data |

#### JTON-Human (v8-v20) - Readable Compression

| Data Type | Token Reduction | Original → Compressed | Description |
|-----------|----------------|----------------------|-------------|
| **Homogeneous arrays** | **70.5%** | 704 → 208 tokens | Product lists, similar objects |
| **API responses** | **52.8%** | 619 → 292 tokens | User lists, structured records |
| **String patterns** | **18.5%** | 685 → 558 tokens | Emails, URLs, mixed patterns |
| **Simple objects** | **0%** | No reduction | Overhead > savings for small data |
| **Deep nesting** | **0%** | No reduction | Overhead > savings for small data |

**Best use cases for JTON:**
- Arrays with 10+ similar objects
- Repeated key patterns across objects
- Structured API responses with consistent schemas

JTON excels with structured, repetitive data (arrays of objects). For small or highly variable objects, the compression overhead exceeds the savings.

## Research Notes

This project demonstrates the AlphaEvolve methodology for algorithm optimization:

- **32 generations** of evolution produced measurable improvements
- **LLM-driven iteration** discovered non-obvious optimizations (bit-packing, prefix detection)
- **Clear fitness function** (token count) enabled systematic progress
- **Convergence** observed after v27 (generations 28-31 showed no improvement)
- **Multiple local optima** found: readable (56.8% at v8-v20) vs binary optimized (62.2% at v27-v31)

### Potential Future Directions

- **Dictionary compression**: Extract common values across entire dataset
- **Adaptive algorithms**: Select strategy based on data structure analysis
- **Streaming compression**: Handle large datasets that don't fit in memory
- **Language-specific optimization**: Tune for specific LLM tokenizers
- **Multi-objective optimization**: Balance compression vs decompression speed

## License

This project is provided as-is for educational use.
