import asyncio
import nest_asyncio
from dotenv import load_dotenv
from typing import List, Tuple, Optional

import streamlit as st
from ragbot.settings import build_settings
from llama_index.core.settings import Settings
from llama_index.core.schema import NodeWithScore
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from ragbot.workflows.rag_workflow import RAGWorkflow

# Constants
PAGE_TITLE = "RAGBot"
PAGE_ICON = ":robot_face:"
LAYOUT = "centered"
INPUT_PLACEHOLDER = "Enter your question here..."
THINKING_MESSAGE = "Thinking..."
MAX_PROMPT_LENGTH = 1000

# Initialize async
nest_asyncio.apply()
load_dotenv()

def initialize_session_state() -> None:
    """Initialize all session state variables."""
    # Build settings first if not already initialized
    if not st.session_state.get("settings_initialized", False):
        build_settings()
        st.session_state["settings_initialized"] = True

    initial_states = {
        "container": st.container(),
        "rag_workflow": RAGWorkflow(),
        "messages": [],
        "sources_history": [],
        "is_loading": False
    }

    from llama_index.core.workflow.drawing import draw_all_possible_flows
    draw_all_possible_flows(RAGWorkflow, filename="workflow_diagram.html")
    
    for key, value in initial_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

def setup_page_config() -> None:
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state="auto",
        menu_items=None
    )
    st.title(PAGE_TITLE)

def validate_prompt(prompt: str) -> bool:
    """Validate user input prompt."""
    if not prompt.strip():
        st.warning("Please enter a valid question.")
        return False
    if len(prompt) > MAX_PROMPT_LENGTH:
        st.warning(f"Question is too long. Please keep it under {MAX_PROMPT_LENGTH} characters.")
        return False
    return True

def set_loading_state(loading: bool) -> None:
    """Set the loading state of the application."""
    st.session_state["is_loading"] = loading

def display_source(source: NodeWithScore, index: int) -> None:
    """Display a single source with its details."""
    with st.expander(f"Source {index}"):
        st.markdown(f"**Text:** {source.text}")
        st.markdown(f"**Answer:** {source.metadata.get('answer', 'No answer available')}")
        if score := getattr(source, 'score', None):
            st.markdown(f"**Relevance Score:** {score:.2f}")

def display_source(source: NodeWithScore, index: int) -> None:
    """Display a single source with its details."""
    with st.expander(f"Source {index}"):
        st.markdown(f"**Text:** {source.text}")
        st.markdown(f"**Answer:** {source.metadata.get('answer', 'No answer available')}")
        if score := getattr(source, 'score', None):
            st.markdown(f"**Relevance Score:** {score:.2f}")

def display_messages() -> None:
    """Display all messages in the chat history with their sources."""
    try:
        
        for idx, message in enumerate(st.session_state.messages):
            with st.chat_message(message.role):
                st.markdown(message.content)
                
            if message.role == MessageRole.ASSISTANT:
                source_idx = idx // 2
                if (source_idx < len(st.session_state.sources_history) and 
                        st.session_state.sources_history[source_idx]):  # Check if sources exist and not empty
                    sources = st.session_state.sources_history[source_idx]
                    
                    # Store source visibility state in session_state
                    source_key = f"show_sources_{idx}"
                    if source_key not in st.session_state:
                        st.session_state[source_key] = False
                        
                    if st.button("📚 Show Sources", key=f"button_{idx}"):
                        st.session_state[source_key] = not st.session_state[source_key]
                    
                    if st.session_state[source_key]:
                        st.markdown("**Retrieved Sources:**")
                        for s_idx, src in enumerate(sources, 1):
                            display_source(src, s_idx)
    except Exception as e:
        st.error(f"Error displaying messages: {str(e)}")

async def add_message(message: ChatMessage) -> None:
    """Add a new message to the chat history."""
    try:
        st.session_state.messages.append(message)
    except Exception as e:
        st.error(f"Error adding message: {str(e)}")

async def add_sources(sources: List[NodeWithScore]) -> None:
    """Add new sources to the sources history."""
    try:
        st.session_state.sources_history.append(sources)
    except Exception as e:
        st.error(f"Error adding sources: {str(e)}")

async def process_user_input(prompt: str) -> None:
    """Process user input and generate response."""
    try:
        await add_message(ChatMessage(role=MessageRole.USER, content=prompt))
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(THINKING_MESSAGE):
                stream, sources = await st.session_state["rag_workflow"].run(
                    question=prompt,
                )
                response = st.write_stream((token.delta async for token in stream))

        await add_message(ChatMessage(role=MessageRole.ASSISTANT, content=str(response)))
        await add_sources(sources)
        st.rerun()  # Refresh the page to display new messages and sources
        
    except Exception as e:
        st.error(f"Error processing input: {str(e)}")

async def main() -> None:
    """Main application loop."""
    try:
        # Initialize settings if not already done
        if st.session_state.get("settings_initialized", False) is False:
            st.session_state["settings_initialized"] = True
            build_settings()

        # Display existing messages
        if st.session_state.messages:
            display_messages()

        # Handle new user input
        if prompt := st.chat_input(INPUT_PLACEHOLDER):
            if validate_prompt(prompt):
                try:
                    set_loading_state(True)
                    await process_user_input(prompt)
                finally:
                    set_loading_state(False)

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    initialize_session_state()
    setup_page_config()
    asyncio.run(main())








