from .memory import store

def prompt(state):
    """Prepare the messages for the LLM."""
    # Get store from configured contextvar; 
    memories = store.search(
        # Search within the same namespace as the one
        # we've configured for the agent
        ("memories",),
        query=state["messages"][-1].content,
    )
    system_msg = f"""You are a helpful assistant.

    ## Memories
    <memories>
    {memories}
    </memories>
    """
    return [{"role": "system", "content": system_msg}, *state["messages"]]