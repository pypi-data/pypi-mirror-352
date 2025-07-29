import llm


def trigger_error(message: str) -> str:
    """
    Trigger an error with the provided message.
    """
    raise Exception(message)


@llm.hookimpl
def register_tools(register):
    register(trigger_error)
