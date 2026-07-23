"""
Thin helper around the Azure AI Foundry Agent Service "Responses" API.

Shared by both capstone notebooks so the Azure plumbing (auth, MCP tool
approval loop, response parsing) is written and tested once.

Auth pattern used here (verified against the deployed agent):
  - header  : api-key: <FOUNDRY_API_KEY>
  - query   : ?api-version=v1
  - endpoint: FOUNDRY_AGENT_ENDPOINT (points at one specific, already-deployed
              agent -- "Prakash-aiAgent11" -- and its bound model + tools)

The agent already has the MCP tool ("Microsoft Learn MCP server") attached
server-side with require_approval="always", so every MCP tool call the model
makes comes back as an `mcp_approval_request` output item that must be
approved before the run can continue. `ask_agent()` handles that loop
automatically (auto-approving, since the attached tool is a read-only public
docs server -- see the note on `AUTO_APPROVE_MCP` below).
"""
import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

FOUNDRY_PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
FOUNDRY_AGENT_ENDPOINT = os.environ["FOUNDRY_AGENT_ENDPOINT"]
FOUNDRY_API_KEY = os.environ["FOUNDRY_API_KEY"]
MODEL_DEPLOYMENT_NAME = os.environ["MODEL_DEPLOYMENT_NAME"]
MCP_SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "Microsoft Learn MCP server")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
API_VERSION = os.environ.get("FOUNDRY_API_VERSION", "v1")

_RESPONSES_URL = f"{FOUNDRY_AGENT_ENDPOINT}?api-version={API_VERSION}"
_HEADERS = {"Content-Type": "application/json", "api-key": FOUNDRY_API_KEY}

# In production, tool calls that can WRITE data should always stop for a human
# approval step. The only tool wired to this agent is a read-only Microsoft
# Learn documentation search, so auto-approving here is safe for this
# educational notebook. Flip to False to review every call manually instead.
AUTO_APPROVE_MCP = True


def _post(payload: dict) -> dict:
    resp = requests.post(_RESPONSES_URL, headers=_HEADERS, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def _extract_output_text(response_json: dict) -> str:
    chunks = []
    for item in response_json.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    chunks.append(c["text"])
    return "".join(chunks).strip()


def _pending_approvals(response_json: dict) -> list:
    return [item for item in response_json.get("output", []) if item.get("type") == "mcp_approval_request"]


def ask_agent(prompt: str, previous_response_id: Optional[str] = None, verbose: bool = False) -> dict:
    """Send one turn to the Foundry agent and resolve any MCP approval requests.

    Returns the raw final response JSON (use `output_text()` / `response_id()`
    below to pull out what you need). Pass the returned response's "id" back
    in as `previous_response_id` to continue the same conversation.
    """
    payload = {"model": MODEL_DEPLOYMENT_NAME, "input": prompt}
    if previous_response_id:
        payload["previous_response_id"] = previous_response_id

    response = _post(payload)

    approvals = _pending_approvals(response)
    while approvals:
        approval_inputs = []
        for item in approvals:
            approve = AUTO_APPROVE_MCP
            if verbose:
                print(f"[MCP] {item.get('name')} on '{item.get('server_label')}' "
                      f"args={item.get('arguments')} -> {'approved' if approve else 'denied'}")
            approval_inputs.append({
                "type": "mcp_approval_response",
                "approval_request_id": item["id"],
                "approve": approve,
            })
        response = _post({
            "previous_response_id": response["id"],
            "input": approval_inputs,
        })
        approvals = _pending_approvals(response)

    return response


def output_text(response_json: dict) -> str:
    return _extract_output_text(response_json)


def response_id(response_json: dict) -> str:
    return response_json["id"]


def ask_agent_text(prompt: str, previous_response_id: Optional[str] = None, verbose: bool = False) -> str:
    """Convenience wrapper: send a prompt, return just the assistant's text."""
    return output_text(ask_agent(prompt, previous_response_id=previous_response_id, verbose=verbose))
