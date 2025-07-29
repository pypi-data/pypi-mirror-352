import llm
import json
from llm_tools_trigger_error import trigger_error


def test_tool():
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps(
            {
                "tool_calls": [
                    {"name": "trigger_error", "arguments": {"message": "An error"}}
                ]
            }
        ),
        tools=[trigger_error],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    assert tool_results == [
        {"name": "trigger_error", "output": "Error: An error", "tool_call_id": None}
    ]
