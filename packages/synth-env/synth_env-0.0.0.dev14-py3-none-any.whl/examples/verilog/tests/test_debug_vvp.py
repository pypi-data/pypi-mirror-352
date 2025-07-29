#!/usr/bin/env python3
"""
Test to investigate VVP output capture and expose it to agents.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Add imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.verilog.environment import VerilogEnvironment
from examples.verilog.engine import VerilogEngine


async def test_raw_vvp_output():
    """Test to see what VVP actually outputs and how it's captured."""
    print("🔍 Testing Raw VVP Output Capture")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a failing test to see error output
        module_content = """module TopModule(
    input a,
    input b,
    output out
);
    assign out = a | b;  // Wrong - should be AND (&) not OR (|)
endmodule
"""
        
        testbench_content = """module testbench();
    reg a, b;
    wire out;
    
    TopModule uut(
        .a(a),
        .b(b), 
        .out(out)
    );
    
    initial begin
        $dumpfile("test.vcd");
        $dumpvars(0, testbench);
        
        // Test AND gate - this will fail since we implemented OR
        a = 0; b = 0; #10;
        if (out !== 0) $display("MISMATCH: Test 1 - Expected 0, got %b", out);
        
        a = 0; b = 1; #10; 
        if (out !== 0) $display("MISMATCH: Test 2 - Expected 0, got %b", out);
        
        a = 1; b = 0; #10;
        if (out !== 0) $display("MISMATCH: Test 3 - Expected 0, got %b", out);
        
        a = 1; b = 1; #10;
        if (out !== 1) $display("MISMATCH: Test 4 - Expected 1, got %b", out);
        
        // Count and report mismatches
        $display("Mismatches: 2 in 4 samples");
        $finish;
    end
endmodule
"""
        
        # Create mock task
        mock_task = MagicMock()
        mock_task.id = "test_task"
        mock_task.impetus.instructions = "Test"
        mock_task.metadata.problem_name = "test"
        mock_task.initial_engine_snapshot = {}
        mock_task.snapshot_dir = temp_path
        mock_task.pristine_dir = temp_path
        
        # Write files
        (temp_path / "TopModule.v").write_text(module_content)
        (temp_path / "testbench.v").write_text(testbench_content)
        
        print("🔧 Testing VerilogEngine directly")
        print("-" * 30)
        
        # Test engine directly to see raw output
        engine = VerilogEngine(mock_task)
        priv, pub = await engine._reset_engine()
        
        # Compile
        compile_result = await engine.compile(["TopModule.v"], "testbench.v")
        print(f"Compile result: {compile_result['ok']}")
        
        # Simulate
        simulate_result = await engine.simulate()
        print(f"Simulate result keys: {list(simulate_result.keys())}")
        print(f"Simulate OK: {simulate_result.get('ok')}")
        print(f"Simulate passed: {simulate_result.get('passed')}")
        
        if "stdout" in simulate_result:
            vvp_stdout = simulate_result["stdout"]
            print(f"\n🎯 RAW VVP STDOUT:")
            print(f"   Length: {len(vvp_stdout)} characters")
            print(f"   Content: '{vvp_stdout}'")
            print(f"   Has 'Mismatches:'? {'Mismatches:' in vvp_stdout}")
            print(f"   Has '2 in 4'? {'2 in 4' in vvp_stdout}")
        else:
            print("❌ No stdout in simulate result!")
            
        if "stderr" in simulate_result:
            vvp_stderr = simulate_result["stderr"]
            print(f"\n📢 RAW VVP STDERR:")
            print(f"   Length: {len(vvp_stderr)} characters")
            print(f"   Content: '{vvp_stderr}'")
        
        print(f"\n🏢 Testing VerilogEnvironment wrapper")
        print("-" * 30)
        
        # Test environment wrapper
        env = VerilogEnvironment(mock_task)
        await env.initialize()
        
        # Write files via environment
        await env.step({
            "tool": "write_file",
            "args": {"path": "TopModule.v", "content": module_content}
        })
        
        # Compile via environment
        compile_obs = await env.step({
            "tool": "compile", 
            "args": {"sources": ["TopModule.v"], "testbench": "testbench.v"}
        })
        print(f"Environment compile status: '{compile_obs.get('compile_status', '')}'")
        
        # Simulate via environment
        simulate_obs = await env.step({
            "tool": "simulate",
            "args": {}
        })
        
        print(f"\n📊 Environment Observation:")
        print(f"   Simulate status: '{simulate_obs.get('simulate_status', '')}'")
        print(f"   Task completed: {simulate_obs.get('task_completed', False)}")
        print(f"   Available keys: {list(simulate_obs.keys())}")
        
        # Check if VVP output is anywhere in the observation
        vvp_found = False
        for key, value in simulate_obs.items():
            if isinstance(value, str) and ("MISMATCH" in value or "Mismatches:" in value):
                print(f"   🎯 Found VVP-like output in '{key}': {value[:100]}...")
                vvp_found = True
        
        if not vvp_found:
            print(f"   ❌ No VVP output found in environment observation")
            print(f"   → Agents cannot see detailed test results!")
            
        print(f"\n🔍 CONCLUSION:")
        print(f"   Engine captures VVP output: {'✅' if 'stdout' in simulate_result else '❌'}")
        print(f"   Environment exposes it: {'✅' if vvp_found else '❌'}")


if __name__ == "__main__":
    asyncio.run(test_raw_vvp_output()) 