#!/usr/bin/env python3
"""
Simple debugging script to expose Verilog environment issues.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Add imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.verilog.environment import VerilogEnvironment


async def test_verilog_environment_issues():
    """Simple test to expose Verilog environment issues."""
    print("🔍 Testing Verilog Environment Issues")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a correct Verilog solution
        module_content = """module TopModule(
    input a,
    input b,
    output out
);
    assign out = a & b;
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
        
        // Test all combinations
        a = 0; b = 0; #10;
        if (out !== 0) $display("MISMATCH: Expected 0, got %b at test 1", out);
        
        a = 0; b = 1; #10;
        if (out !== 0) $display("MISMATCH: Expected 0, got %b at test 2", out);
        
        a = 1; b = 0; #10;
        if (out !== 0) $display("MISMATCH: Expected 0, got %b at test 3", out);
        
        a = 1; b = 1; #10;
        if (out !== 1) $display("MISMATCH: Expected 1, got %b at test 4", out);
        
        $display("Mismatches: 0 in 4 samples");
        $finish;
    end
endmodule
"""
        
        # Create mock task
        mock_task = MagicMock()
        mock_task.id = "test_task"
        mock_task.impetus.instructions = "Test AND gate"
        mock_task.metadata.problem_name = "test_and_gate"
        mock_task.initial_engine_snapshot = {}
        mock_task.snapshot_dir = temp_path
        mock_task.pristine_dir = temp_path
        
        # Write testbench
        (temp_path / "testbench.v").write_text(testbench_content)
        
        # Create environment
        env = VerilogEnvironment(mock_task)
        
        print("🚀 Step 1: Initialize environment")
        obs = await env.initialize()
        print(f"Initial files: {list(obs.get('files', {}).keys())}")
        
        print("\n✏️  Step 2: Agent writes module")
        obs = await env.step({
            "tool": "write_file",
            "args": {
                "path": "TopModule.v",
                "content": module_content
            }
        })
        print(f"Files after write: {list(obs.get('files', {}).keys())}")
        
        print("\n🔨 Step 3: Agent compiles")
        obs = await env.step({
            "tool": "compile", 
            "args": {"sources": ["TopModule.v"], "testbench": "testbench.v"}
        })
        compile_status = obs.get("compile_status", "")
        print(f"Compile status: '{compile_status}'")
        
        if "Failed" in compile_status:
            print(f"❌ COMPILATION FAILED: {compile_status}")
            return
            
        print("\n🏃 Step 4: Agent simulates")
        obs = await env.step({
            "tool": "simulate",
            "args": {}
        })
        
        simulate_status = obs.get("simulate_status", "")
        task_completed = obs.get("task_completed", False)
        
        print(f"\n📊 RESULTS:")
        print(f"   Simulate Status: '{simulate_status}'")
        print(f"   Task Completed: {task_completed}")
        print(f"   Total Reward: {obs.get('total_reward', 0)}")
        
        # Check for key issues
        print(f"\n🔍 ISSUE ANALYSIS:")
        
        # Issue 1: VVP output availability
        if "vvp_output" in obs:
            print(f"   ✅ VVP output available to agents")
            vvp_output = obs["vvp_output"]
            print(f"   VVP output snippet: {vvp_output[:100]}...")
        else:
            print(f"   ⚠️  VVP output NOT available to agents")
            print(f"   → Agents cannot see actual simulation results")
        
        # Issue 2: Status parsing accuracy
        if "Mismatches: 0" in str(obs):
            print(f"   ✅ Success pattern found in observation")
            if "Failed" in simulate_status:
                print(f"   ❌ BUG: VVP shows success but status is 'Failed'")
            elif "Passed" in simulate_status:
                print(f"   ✅ Status correctly shows 'Passed'")
        else:
            print(f"   ⚠️  Success pattern not found in observation")
        
        # Issue 3: Task completion logic
        if task_completed:
            print(f"   ✅ Task marked as completed")
        else:
            print(f"   ⚠️  Task NOT marked as completed despite success")
            
        print("\n📋 OBSERVATION SUMMARY:")
        print(f"   Available keys: {list(obs.keys())}")
        for key, value in obs.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"   {key}: {value[:50]}... ({len(value)} chars)")
            else:
                print(f"   {key}: {value}")


if __name__ == "__main__":
    asyncio.run(test_verilog_environment_issues()) 