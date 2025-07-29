#!/usr/bin/env python3
"""
Test that demonstrates the VVP bug in VerilogEngine integration.

This test creates a VerilogEngine instance and shows the bug in action.
"""

import asyncio
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional

# Import the actual VerilogEngine from Environments
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from src.examples.verilog.engine import VerilogEngine
from tasks.core import TaskInstance


@dataclass
class MockTaskInstance(TaskInstance):
    """Mock task instance for testing."""
    snapshot_dir: str
    pristine_dir: Optional[str] = None
    
    async def serialize(self) -> Dict[str, Any]:
        return {
            "snapshot_dir": self.snapshot_dir,
            "pristine_dir": self.pristine_dir
        }
    
    @classmethod
    async def deserialize(cls, data: Dict[str, Any]) -> "MockTaskInstance":
        return cls(
            snapshot_dir=data["snapshot_dir"],
            pristine_dir=data.get("pristine_dir")
        )


async def test_vvp_bug_in_engine():
    """Test that shows the VVP subprocess bug in VerilogEngine."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create task instance
        task = MockTaskInstance(snapshot_dir=temp_dir)
        
        # Create engine
        engine = VerilogEngine(task)
        
        # Initialize engine
        priv, pub = await engine._reset_engine()
        
        # Create test files
        test_verilog = """module TopModule(output zero);
    assign zero = 1'b0;
endmodule
"""
        
        test_tb = """`timescale 1ns/1ps
module tb();
    wire zero;
    TopModule dut(.zero(zero));
    
    initial begin
        #10;
        $display("Hint: Output 'zero' has no mismatches.");
        $display("Mismatches: 0 in 1 samples");
        $display("ALL_TESTS_PASSED");
        $finish;
    end
endmodule
"""
        
        # Write files
        await engine.write_file("TopModule.v", test_verilog)
        await engine.write_file("test_tb.v", test_tb)
        
        # Compile
        compile_result = await engine.compile(sources=["TopModule.v", "test_tb.v"])
        print(f"Compile result: {compile_result}")
        
        assert compile_result["ok"], f"Compilation failed: {compile_result}"
        
        # Simulate - THIS IS WHERE THE BUG HAPPENS
        simulate_result = await engine.simulate()
        print(f"\n=== SIMULATE RESULT ===")
        print(f"OK: {simulate_result['ok']}")
        print(f"Stdout: '{simulate_result['stdout']}'")
        print(f"Stderr: '{simulate_result['stderr']}'")
        print(f"Passed: {simulate_result['passed']}")
        print("======================\n")
        
        # The bug: stdout should contain the test output, but it's empty!
        if simulate_result['stdout'].strip() == "":
            print("🐛 BUG CONFIRMED: VVP stdout is empty!")
            print("   Expected: Output with 'ALL_TESTS_PASSED' and success messages")
            print("   Actual: Empty string")
        else:
            print("✅ VVP stdout captured correctly")
            
        # Check if pattern detection worked
        if not simulate_result['passed']:
            print("🐛 CONSEQUENCE: Simulation marked as failed due to empty stdout")
        else:
            print("✅ Simulation correctly marked as passed")


async def test_direct_subprocess_comparison():
    """Compare direct subprocess call vs engine subprocess call."""
    
    import subprocess
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Write test files
        (temp_path / "simple.v").write_text("""module simple();
    initial begin
        $display("Hello from VVP!");
        $display("Mismatches: 0 in 1 samples");
        $finish;
    end
endmodule
""")
        
        # Compile
        compile_proc = subprocess.run(
            ["iverilog", "-o", "test.out", "simple.v"],
            cwd=temp_dir,
            capture_output=True,
            text=True
        )
        assert compile_proc.returncode == 0
        
        print("=== DIRECT SUBPROCESS TEST ===")
        
        # Method 1: Direct subprocess (should work)
        direct_proc = subprocess.run(
            ["vvp", "test.out"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"Direct stdout: '{direct_proc.stdout}'")
        print(f"Direct stderr: '{direct_proc.stderr}'")
        
        # Method 2: Engine-style subprocess (might have bug)
        bin_path = str(temp_path / "test.out")
        engine_proc = subprocess.run(
            ["vvp", bin_path],  # Using full path like engine does
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"\nEngine-style stdout: '{engine_proc.stdout}'")
        print(f"Engine-style stderr: '{engine_proc.stderr}'")
        
        # Compare
        if direct_proc.stdout != engine_proc.stdout:
            print("\n🐛 DIFFERENCE DETECTED!")
            print(f"   Direct method output length: {len(direct_proc.stdout)}")
            print(f"   Engine method output length: {len(engine_proc.stdout)}")
        else:
            print("\n✅ Both methods produce same output")


def main():
    """Run all tests."""
    print("Testing VVP bug in VerilogEngine...\n")
    
    # Test 1: Engine integration
    print("TEST 1: VerilogEngine Integration")
    print("-" * 40)
    asyncio.run(test_vvp_bug_in_engine())
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: Direct comparison
    print("TEST 2: Direct Subprocess Comparison")
    print("-" * 40)
    asyncio.run(test_direct_subprocess_comparison())


if __name__ == "__main__":
    main()