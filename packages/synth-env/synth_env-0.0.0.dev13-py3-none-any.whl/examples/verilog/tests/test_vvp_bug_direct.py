#!/usr/bin/env python3
"""
Direct test to verify if VVP bug is truly fixed in the engine.
"""

import subprocess
import tempfile
from pathlib import Path

def test_vvp_methods():
    """Test different ways of calling VVP to see which ones fail."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a simple test file
        test_v = temp_path / "test.v"
        test_v.write_text("""module test();
    initial begin
        $display("SUCCESS: VVP output captured!");
        $display("Mismatches: 0 in 10 samples");
        $finish;
    end
endmodule
""")
        
        # Compile
        subprocess.run(
            ["iverilog", "-o", "test.out", "test.v"],
            cwd=temp_dir,
            check=True
        )
        
        print("=== Testing Different VVP Call Methods ===\n")
        
        # Method 1: Absolute path (BUGGY)
        print("1. ABSOLUTE PATH (Original buggy method):")
        abs_path = str(temp_path / "test.out")
        proc1 = subprocess.run(
            ["vvp", abs_path],
            capture_output=True,
            text=True
        )
        print(f"   Return code: {proc1.returncode}")
        print(f"   Stdout empty? {proc1.stdout == ''}")
        print(f"   Stdout length: {len(proc1.stdout)} chars")
        if proc1.stdout:
            print(f"   First line: {proc1.stdout.splitlines()[0]}")
        
        # Method 2: Relative path with cwd (FIXED)
        print("\n2. RELATIVE PATH + CWD (Fixed method):")
        proc2 = subprocess.run(
            ["vvp", "test.out"],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        print(f"   Return code: {proc2.returncode}")
        print(f"   Stdout empty? {proc2.stdout == ''}")
        print(f"   Stdout length: {len(proc2.stdout)} chars")
        if proc2.stdout:
            print(f"   First line: {proc2.stdout.splitlines()[0]}")
        
        # Method 3: Using Path.name with parent cwd (Engine fix)
        print("\n3. PATH.NAME + PARENT CWD (Engine fix method):")
        binary_path = temp_path / "test.out"
        proc3 = subprocess.run(
            ["vvp", binary_path.name],
            cwd=str(binary_path.parent),
            capture_output=True,
            text=True
        )
        print(f"   Return code: {proc3.returncode}")
        print(f"   Stdout empty? {proc3.stdout == ''}")
        print(f"   Stdout length: {len(proc3.stdout)} chars")
        if proc3.stdout:
            print(f"   First line: {proc3.stdout.splitlines()[0]}")
        
        # Compare results
        print("\n=== COMPARISON ===")
        if proc1.stdout == proc2.stdout == proc3.stdout:
            print("✅ All methods produce identical output")
            print("   The VVP bug does NOT manifest in this environment")
        else:
            print("❌ Methods produce different output!")
            print(f"   Method 1 stdout empty: {proc1.stdout == ''}")
            print(f"   Method 2 stdout empty: {proc2.stdout == ''}")
            print(f"   Method 3 stdout empty: {proc3.stdout == ''}")
            
            if proc1.stdout == '' and proc2.stdout != '' and proc3.stdout != '':
                print("\n🐛 VVP BUG CONFIRMED: Absolute path produces empty stdout!")
                print("✅ FIX VERIFIED: Both fixed methods capture stdout correctly")

if __name__ == "__main__":
    print("Testing VVP subprocess bug directly...\n")
    test_vvp_methods()