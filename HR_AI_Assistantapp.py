


# Accenture - HR AI Assistant Application 

# Install below Libraries
#pip install streamlit

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

# Legacy Azure OpenAI defaults are retained only as a fallback. The preferred
# configuration uses the FOUNDRY_* values already present in this project's .env.
DEFAULT_ENDPOINT = "https://prakashfoundry111.services.ai.azure.com/api/projects/prakash-proj-111"
DEFAULT_DEPLOYMENT = "gpt-5"

SYSTEM_PROMPT = """You are an enterprise HR AI assistant.

Responsibilities:
- Answer HR questions clearly, professionally, and concisely.
- Help employees understand policies, leave, benefits, onboarding, payroll, performance, and workplace conduct.
- Use the provided HR policy context when available.
- Ask clarifying questions when a request is ambiguous.
- Do not invent company-specific policy details when context is missing.
- Avoid exposing confidential, personal, or restricted information.
- Escalate legal, medical, payroll-dispute, harassment, termination, or sensitive employee-relations cases to HR.

Response style:
- Use practical bullet points when helpful.
- Provide step-by-step guidance for processes.
- Mention assumptions and limitations clearly.
"""

QUICK_PROMPTS = {
    "Leave Policy": "Please explain our leave policy in simple terms, including annual leave, sick leave, and approval workflow.",
    "Onboarding": "Create an onboarding checklist for a new employee joining next week.",
    "Benefits": "Summarize common employee benefits and explain what details I should verify with HR.",
    "HR Email": "Draft a professional email to HR asking for clarification about remote work eligibility.",
}


def get_config() -> tuple[str, str, str, bool]:
    """Load Foundry agent settings first, with Azure OpenAI compatibility fallback."""
    agent_responses_endpoint = os.getenv("FOUNDRY_AGENT_ENDPOINT", "").rstrip("/")
    if agent_responses_endpoint:
        # OpenAI SDK base_url is the path before `/responses`; the SDK appends
        # the Responses API route itself when `client.responses.create` is used.
        endpoint = agent_responses_endpoint.removesuffix("/responses")
        deployment = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5")
        api_key = os.getenv("FOUNDRY_API_KEY", "")
        return endpoint, deployment, api_key, True

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", DEFAULT_ENDPOINT).rstrip("/")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", DEFAULT_DEPLOYMENT)
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
    return endpoint, deployment, api_key, False


def get_foundry_project_details() -> tuple[str, str, str]:
    """Read non-secret project metadata supplied through the local .env file."""
    return (
        os.getenv("FOUNDRY_PROJECT_ENDPOINT", ""),
        os.getenv("MCP_SERVER_NAME", ""),
        os.getenv("AZURE_TENANT_ID", ""),
    )


@st.cache_resource(show_spinner=False)
def get_client(endpoint: str, api_key: str, use_foundry_agent: bool) -> OpenAI:
    # Foundry agent protocol endpoints are project-scoped REST endpoints and
    # require api-version on every request. `default_query` lets the OpenAI SDK
    # append it correctly when it creates the `/responses` request URL.
    default_query = {"api-version": os.getenv("FOUNDRY_API_VERSION", "v1")} if use_foundry_agent else None
    # Foundry agent endpoints accept resource keys through `api-key`. The
    # generic OpenAI SDK otherwise sends its key as an Authorization bearer.
    default_headers = {"api-key": api_key} if use_foundry_agent else None
    return OpenAI(
        base_url=endpoint,
        api_key=api_key,
        default_query=default_query,
        default_headers=default_headers,
    )


def extract_uploaded_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""

    suffix = Path(uploaded_file.name).suffix.lower()
    raw_bytes = uploaded_file.getvalue()

    if suffix in {".txt", ".md", ".csv"}:
        return raw_bytes.decode("utf-8", errors="ignore")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader

            reader = PdfReader(uploaded_file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            st.warning(f"Could not read PDF text: {exc}")
            return ""

    st.warning("Supported files: PDF, TXT, MD, CSV.")
    return ""


def build_messages(policy_context: str, history: list[dict[str, str]]) -> list[dict[str, str]]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if policy_context.strip():
        messages.append(
            {
                "role": "system",
                "content": (
                    "Use this uploaded HR policy context when answering. "
                    "If the answer is not present in the context, say so clearly.\n\n"
                    f"{policy_context[:18000]}"
                ),
            }
        )
    messages.extend(history)
    return messages


def build_foundry_agent_input(policy_context: str, history: list[dict[str, str]]) -> str:
    """Flatten chat history into Responses-compatible input for a hosted agent."""
    parts = [SYSTEM_PROMPT]
    if policy_context.strip():
        parts.append(
            "HR policy context (use only when relevant; state when the answer is absent):\n"
            f"{policy_context[:18000]}"
        )
    parts.append("Conversation:")
    for message in history:
        speaker = "Employee" if message["role"] == "user" else "Assistant"
        parts.append(f"{speaker}: {message['content']}")
    parts.append("Assistant:")
    return "\n\n".join(parts)


def call_hr_assistant(
    client: OpenAI,
    deployment: str,
    policy_context: str,
    history: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    use_foundry_agent: bool,
) -> str:
    if use_foundry_agent:
        # The configured Foundry agent exposes the OpenAI Responses protocol.
        # Its model settings, instructions, and tools are applied server-side.
        # In particular, configured agents reject per-request temperature.
        response = client.responses.create(
            model=deployment,
            input=build_foundry_agent_input(policy_context, history),
            max_output_tokens=max_tokens,
        )
        return response.output_text or ""

    completion = client.chat.completions.create(
        model=deployment,
        messages=build_messages(policy_context, history),
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return completion.choices[0].message.content or ""


def initialize_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi, I am your HR AI assistant. How can I help with HR policies or employee support today?",
            }
        ]
    if "policy_context" not in st.session_state:
        st.session_state.policy_context = ""


def main() -> None:
    st.set_page_config(page_title="HR AI Portal", page_icon="HR", layout="wide")
    initialize_state()

    endpoint, deployment, api_key, use_foundry_agent = get_config()
    project_endpoint, mcp_server_name, tenant_id = get_foundry_project_details()

    with st.sidebar:
        st.title("HR AI Portal")
        st.caption("Azure AI Foundry powered employee support" if use_foundry_agent else "Azure OpenAI powered employee support")

        st.subheader("Connection")
        st.text_input("Foundry agent endpoint" if use_foundry_agent else "Azure OpenAI endpoint", value=endpoint, disabled=True)
        st.text_input("Deployment", value=deployment, disabled=True)
        if use_foundry_agent:
            # Only non-secret Foundry metadata is shown in the UI. The API key
            # stays in .env and is never rendered or logged.
            st.caption(f"Project: {project_endpoint or 'Not configured'}")
            st.caption(f"MCP server: {mcp_server_name or 'Not configured'}")
            st.caption(f"Tenant configured: {'Yes' if tenant_id else 'No'}")

        st.subheader("Settings")
        temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.05)
        max_tokens = st.slider("Max response tokens", 300, 3000, 900, 100)
        if use_foundry_agent:
            st.caption("Temperature is managed by the configured Foundry agent.")

        st.subheader("Policy Context")
        uploaded_file = st.file_uploader("Upload HR policy file", type=["pdf", "txt", "md", "csv"])
        if uploaded_file:
            st.session_state.policy_context = extract_uploaded_text(uploaded_file)
            if st.session_state.policy_context:
                st.success(f"Loaded {len(st.session_state.policy_context):,} characters from {uploaded_file.name}")

        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.title("Employee HR Assistant")
    st.write("Ask about leave, onboarding, benefits, HR processes, workplace policies, or draft HR communications.")

    if not api_key:
        required_key = "FOUNDRY_API_KEY" if use_foundry_agent else "AZURE_OPENAI_API_KEY"
        st.error(f"Set {required_key} in your environment or .env file before chatting.")
        st.stop()

    cols = st.columns(len(QUICK_PROMPTS))
    for col, (label, prompt_text) in zip(cols, QUICK_PROMPTS.items()):
        if col.button(label, use_container_width=True):
            st.session_state.pending_prompt = prompt_text

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask an HR question...")
    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pop("pending_prompt")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Checking HR guidance..."):
                try:
                    client = get_client(endpoint, api_key, use_foundry_agent)
                    answer = call_hr_assistant(
                        client=client,
                        deployment=deployment,
                        policy_context=st.session_state.policy_context,
                        history=st.session_state.messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        use_foundry_agent=use_foundry_agent,
                    )
                except Exception as exc:
                    provider = "Foundry agent" if use_foundry_agent else "Azure OpenAI"
                    answer = f"{provider} request failed: {exc}"

                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()

# Run the application with below command:
#streamlit run .\HR_AI_Assistantapp.py