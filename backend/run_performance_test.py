"""
Simple wrapper to run the performance test and save output to file
"""
import subprocess
import sys

output_file = "mongodb_test_results.txt"

print(f"Running MongoDB performance tests...")
print(f"Output will be saved to: {output_file}")

try:
    # Run the test and capture output
    result = subprocess.run(
        [sys.executable, "test_mongodb_performance.py"],
        capture_output=True,
        text=True,
        timeout=180
    )
    
    # Combine stdout and stderr
    output = result.stdout + result.stderr
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    # Also print to console
    print(output)
    
    print(f"\n{'='*70}")
    print(f"✅ Test completed! Results saved to: {output_file}")
    print(f"{'='*70}")
    
except subprocess.TimeoutExpired:
    print("❌ Test timed out after 180 seconds")
except Exception as e:
    print(f"❌ Error running test: {e}")

