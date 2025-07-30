import types

import pytest

from cognyx_bom_sdk.cognyx import automation_runtime


def test_extract_scope_filters_globals_and_privates():
    ns = {
        "a": 123,
        "_private": 456,
        "__hidden": 789,
        "mod": types,
        "builtin": len,
        "func": lambda x: x + 1,
    }
    global_vars = {"g": {"type": "primitive", "value": 42}}
    ignore = ["should_ignore"]
    result = automation_runtime.extract_scope(ns, global_vars, ignore)
    # Should not contain _private, __hidden, 'mod', 'builtin'
    assert "a" in result
    assert "_private" not in result
    assert "__hidden" not in result
    assert "mod" not in result
    assert "builtin" not in result
    assert "g" in result
    # Should serialize functions
    assert result["func"]["type"] == "serialized"
    assert result["func"]["value"](2) == 3


@pytest.mark.asyncio
async def test_execute_code_runs_and_captures_scope():
    async def fake_eval_async(code, scope):
        # Simulate an async code executor
        scope = dict(scope)
        exec(code, {}, scope)
        return scope

    code = "x = 1\ny = x + 2"
    global_vars = {"z": {"type": "primitive", "value": 99}}
    global_ignore = ["ignore_me"]
    scope = {}
    result = await automation_runtime.execute_code(
        code,
        fake_eval_async,
        global_vars,
        global_ignore,
        scope,
    )

    assert result["result"]["x"] == 1
    assert result["result"]["y"] == 3
    assert result["result"]["z"] == 99
