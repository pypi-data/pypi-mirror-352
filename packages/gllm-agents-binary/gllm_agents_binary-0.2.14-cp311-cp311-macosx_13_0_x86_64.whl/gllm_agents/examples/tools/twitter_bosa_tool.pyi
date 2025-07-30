from _typeshed import Incomplete
from pydantic import BaseModel

logger: Incomplete

class TwitterUserInput(BaseModel):
    """Input for Twitter user tool."""
    username: str

def twitter_get_user_tool(username: str) -> str:
    """Retrieves details for specified Twitter user.

    Args:
        username: The username of target user to search for.

    Returns:
        A response of user details object from BOSA endpoint
    """
