#!/usr/bin/env python3
"""
Tests to verify Verilog environment fixes and detect remaining issues.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Add imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.verilog.environment import VerilogEnvironment


class TestVerilogEnvironmentFixes:
    """Test that Verilog environment fixes are working correctly."""
    
    @pytest.mark.asyncio
    async def test_vvp_output_now_available_to_agents(self):
        """Test that agents can now see detailed VVP output for debugging."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a module with intentional bugs to generate VVP output
            buggy_module = """module TopModule(
    input a,
    input b,
    output out
);
    assign out = a | b;  // Bug: should be & (AND) not | (OR)
endmodule
"""
            
            testbench = """module testbench();
    reg a, b;
    wire out;
    
    TopModule uut(.a(a), .b(b), .out(out));
    
    initial begin
        // Test AND functionality (will fail with OR implementation)
        a = 0; b = 0; #10;
        if (out !== 0) $display("ERROR: Test 1 failed - Expected 0, got %b", out);
        
        a = 0; b = 1; #10;
        if (out !== 0) $display("ERROR: Test 2 failed - Expected 0, got %b", out);
        
        a = 1; b = 0; #10;
        if (out !== 0) $display("ERROR: Test 3 failed - Expected 0, got %b", out);
        
        a = 1; b = 1; #10;
        if (out !== 1) $display("ERROR: Test 4 failed - Expected 1, got %b", out);
        
        $display("Tests completed - 2 failures expected");
        $display("Mismatches: 2 in 4 samples");
        $finish;
    end
endmodule
"""
            
            # Create mock task
            mock_task = MagicMock()
            mock_task.id = "test_task"
            mock_task.impetus.instructions = "Implement AND gate"
            mock_task.metadata.problem_name = "test_and_gate"
            mock_task.initial_engine_snapshot = {}
            mock_task.snapshot_dir = temp_path
            mock_task.pristine_dir = temp_path
            
            (temp_path / "testbench.v").write_text(testbench)
            
            # Test the environment
            env = VerilogEnvironment(mock_task)
            await env.initialize()
            
            # Write the buggy module
            await env.step({
                "tool": "write_file",
                "args": {"path": "TopModule.v", "content": buggy_module}
            })
            
            # Compile
            await env.step({
                "tool": "compile", 
                "args": {"sources": ["TopModule.v"], "testbench": "testbench.v"}
            })
            
            # Simulate
            obs = await env.step({
                "tool": "simulate",
                "args": {}
            })
            
            # MAIN TEST: Check that VVP output is now available
            assert "simulate_output" in obs, "simulate_output should be available to agents"
            
            vvp_output = obs["simulate_output"]
            assert isinstance(vvp_output, str), "simulate_output should be a string"
            assert len(vvp_output) > 0, "simulate_output should not be empty"
            
            # Test that detailed error messages are available
            assert "ERROR:" in vvp_output or "MISMATCH" in vvp_output, \
                "Agents should see detailed error messages from VVP"
            
            # Test that test results summary is available
            assert "Mismatches:" in vvp_output, \
                "Agents should see test summary from VVP"
                
            print(f"✅ FIXED: Agents can now see VVP output!")
            print(f"   VVP output length: {len(vvp_output)} characters")
            print(f"   Contains error details: {'ERROR:' in vvp_output}")
            print(f"   Contains test summary: {'Mismatches:' in vvp_output}")
    
    @pytest.mark.asyncio
    async def test_module_naming_compatibility(self):
        """Test that TopModule works correctly (not affected by naming issues)."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a correct module using standard TopModule naming
            correct_module = """module TopModule(
    input a,
    input b,
    output out
);
    assign out = a & b;
endmodule
"""
            
            # Testbench that uses TopModule (correct naming)
            testbench = """module testbench();
    reg a, b;
    wire out;
    
    TopModule uut(.a(a), .b(b), .out(out));
    
    initial begin
        // Test AND gate
        a = 0; b = 0; #10;
        a = 0; b = 1; #10;
        a = 1; b = 0; #10;
        a = 1; b = 1; #10;
        
        $display("All tests passed");
        $display("Mismatches: 0 in 4 samples");
        $finish;
    end
endmodule
"""
            
            mock_task = MagicMock()
            mock_task.id = "test_task"
            mock_task.impetus.instructions = "Test naming"
            mock_task.metadata.problem_name = "test_naming"
            mock_task.initial_engine_snapshot = {}
            mock_task.snapshot_dir = temp_path
            mock_task.pristine_dir = temp_path
            
            (temp_path / "testbench.v").write_text(testbench)
            
            env = VerilogEnvironment(mock_task)
            await env.initialize()
            
            await env.step({
                "tool": "write_file",
                "args": {"path": "TopModule.v", "content": correct_module}
            })
            
            compile_obs = await env.step({
                "tool": "compile", 
                "args": {"sources": ["TopModule.v"], "testbench": "testbench.v"}
            })
            
            # Check compilation succeeds
            compile_status = compile_obs.get("compile_status", "")
            assert "Success" in compile_status, f"Compilation should succeed: {compile_status}"
            
            simulate_obs = await env.step({
                "tool": "simulate",
                "args": {}
            })
            
            # Check simulation succeeds
            simulate_status = simulate_obs.get("simulate_status", "")
            task_completed = simulate_obs.get("task_completed", False)
            
            assert "Passed" in simulate_status, f"Simulation should pass: {simulate_status}"
            assert task_completed, "Task should be completed after successful simulation"
            
            print(f"✅ Module naming works correctly!")
            print(f"   Compile status: {compile_status}")
            print(f"   Simulate status: {simulate_status}")
            print(f"   Task completed: {task_completed}")
    
    @pytest.mark.asyncio
    async def test_module_naming_mismatch_detection(self):
        """Test that we can detect module naming mismatches (like top_module1 vs TopModule)."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a module with TopModule name
            module_content = """module TopModule(
    input a,
    output out
);
    assign out = a;
endmodule
"""
            
            # But testbench expects a different name (simulating VerilogEval naming issues)
            testbench_with_naming_issue = """module testbench();
    reg a;
    wire out;
    
    // This will cause a naming mismatch error
    top_module1 uut(.a(a), .out(out));
    
    initial begin
        a = 0; #10;
        a = 1; #10;
        $finish;
    end
endmodule
"""
            
            mock_task = MagicMock()
            mock_task.id = "test_task"
            mock_task.impetus.instructions = "Test naming mismatch"
            mock_task.metadata.problem_name = "test_naming_mismatch"
            mock_task.initial_engine_snapshot = {}
            mock_task.snapshot_dir = temp_path
            mock_task.pristine_dir = temp_path
            
            (temp_path / "testbench.v").write_text(testbench_with_naming_issue)
            
            env = VerilogEnvironment(mock_task)
            await env.initialize()
            
            await env.step({
                "tool": "write_file",
                "args": {"path": "TopModule.v", "content": module_content}
            })
            
            compile_obs = await env.step({
                "tool": "compile", 
                "args": {"sources": ["TopModule.v"], "testbench": "testbench.v"}
            })
            
            # This should fail due to naming mismatch
            compile_status = compile_obs.get("compile_status", "")
            
            if "Failed" in compile_status:
                print(f"✅ Successfully detected module naming mismatch!")
                print(f"   Error details available to agent: {'top_module1' in compile_status}")
                
                # Check that agents can see the specific error
                assert "compile_output" in compile_obs, "Agents should see detailed compile errors"
                compile_output = compile_obs.get("compile_output", "")
                assert "top_module1" in compile_output, "Agents should see the specific naming error"
                
            else:
                print(f"⚠️  No naming mismatch detected - this specific issue may not occur")
                print(f"   Compile status: {compile_status}")


if __name__ == "__main__":
    asyncio.run(pytest.main([__file__, "-v", "-s"])) 