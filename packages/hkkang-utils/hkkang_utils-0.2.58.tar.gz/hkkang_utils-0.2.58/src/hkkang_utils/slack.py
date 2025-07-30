import contextlib
import logging
import os
from typing import *

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse
import hkkang_utils.misc as misc_utils
import hkkang_utils.socket as socket_utils

# Load environment variables
misc_utils.load_dotenv(stack_depth=2)

DEFAULT_ACCESS_TOKEN = os.environ.get("SLACK_ACCESS_TOKEN")

logger = logging.getLogger("SlackMessenger")


class SlackMessenger:
    """A wrapper class for sending Slack messages with enhanced functionality.

    This class provides a convenient interface for sending messages to Slack channels,
    managing message threads, and handling notifications with success/error states.

    Attributes:
        channel (str): The Slack channel to send messages to
        token (str): Slack API authentication token
        append_server_info (bool): Whether to include server information in messages
        last_thread_ts (str): Timestamp of the last message thread
    """

    def __init__(
        self,
        channel: str,
        token: str = DEFAULT_ACCESS_TOKEN,
        web_client: Optional[WebClient] = None,
        append_server_info: bool = True,
    ):
        """Initialize the SlackMessenger.

        Args:
            channel: The Slack channel to send messages to
            token: Slack API authentication token (defaults to env variable)
            web_client: Optional pre-configured WebClient instance
            append_server_info: Whether to include server information in messages
        """
        self.channel = channel
        self.token = token
        self._web_client = web_client
        self.append_server_info = append_server_info
        self.last_thread_ts = None
        self.__post_init__()

    def __post_init__(self):
        if not self.token:
            raise ValueError(
                """Please set token or SLACK_ACCESS_TOKEN environment variable.
                   Follow the tutorial to set up bot OAuthToken and permissions: 
                   https://github.com/slackapi/python-slack-sdk/tree/main/tutorial"""
            )

    @property
    def client(self) -> WebClient:
        """Get or create a WebClient instance.

        Returns:
            WebClient: The Slack Web API client
        """
        if self._web_client is None:
            self._web_client = WebClient(token=self.token)
        return self._web_client

    @contextlib.contextmanager
    def notification(
        self,
        success_msg: str,
        error_msg: str,
        start_msg: Optional[str] = None,
        user_id_to_mention: Optional[str] = None,
        replies: Optional[List[str]] = None,
        disable: bool = False,
        disable_callback: Optional[Callable[[], bool]] = None,
    ) -> Generator[Optional["SlackMessenger"], None, None]:
        """
        Send a message when the task within the code block is finished, with an optional short preview.
        If start_msg is None:
            1. The success/error message will be sent.
            2. The replies will be sent as replies to the success/error message.
        If start_msg is not None:
            1. The start message will be sent.
            2. The replies will be sent as replies to the start message.
            3. The success/error message will be sent as a reply to the start message.
        """
        # Skip notification if the debugger is active or if the disable flag is True
        if misc_utils.is_debugger_active() or disable:
            yield None
            return

        # Append the user_id_to_mention to the messages if it is provided
        if user_id_to_mention is not None:
            success_msg = f"<@{user_id_to_mention}> {success_msg}"
            error_msg = f"<@{user_id_to_mention}> {error_msg}"
            if start_msg is not None:
                start_msg = f"<@{user_id_to_mention}> {start_msg}"

        thread_ts = None  # Initialize thread_ts here
        try:
            # Skip notification if the disable_callback returns True
            if disable_callback is not None and disable_callback():
                yield None
                return

            # Send the start message if it is not None
            if start_msg is not None:
                response = self.send(
                    start_msg, replies=replies
                )  # Use self.send instead of send_message directly
                thread_ts = response["ts"]
                self.last_thread_ts = thread_ts

            yield self

            # Send the success message
            if start_msg is None:
                self.send(success_msg, replies=replies)
            else:
                # Send the start message as reply to the start message
                self.send_reply(success_msg, thread_ts=thread_ts)
        except Exception as e:
            if disable_callback is not None and disable_callback():
                return
            # Send the error message
            message_to_send = f"{error_msg} ({e.__class__.__name__}: {e})"
            if start_msg is None:
                self.send(message_to_send, replies=replies)
            else:
                # Send the error message as reply to the start message
                self.send_reply(message_to_send, thread_ts=thread_ts)
            raise

    def send(self, text: str, replies: Optional[List[str]] = None) -> SlackResponse:
        """Send a Slack message with optional replies."""
        response = send_message(
            channel=self.channel,
            text=text,
            web_client=self.client,
            token=self.token,
            append_server_info=self.append_server_info,
        )
        self.last_thread_ts = response["ts"]

        # Send replies if provided
        if replies:
            for reply in replies:
                self.send_reply(reply, thread_ts=self.last_thread_ts)

        return response

    def send_reply(self, text: str, thread_ts: Optional[str] = None) -> SlackResponse:
        """Send a Slack reply with an optional reply."""
        if thread_ts is None:
            assert (
                self.last_thread_ts is not None
            ), "No thread to reply to. Send a message first."
            thread_ts = self.last_thread_ts

        response = send_reply(
            channel=self.channel,
            text=text,
            web_client=self.client,
            token=self.token,
            thread_ts=thread_ts,
        )
        self.last_thread_ts = response["ts"]
        return response


def _get_or_create_client(
    web_client: Optional[WebClient] = None, token: str = DEFAULT_ACCESS_TOKEN
) -> WebClient:
    """Create a new WebClient or return the provided one.

    Args:
        web_client: Existing WebClient instance, if any
        token: Slack API token to use when creating a new client

    Returns:
        WebClient: A configured Slack Web API client

    Raises:
        AssertionError: If no token is provided when creating a new client
    """
    if web_client is None:
        assert token is not None, "Please set SLACK_ACCESS_TOKEN environment variable."
        web_client = WebClient(token=token)
    return web_client


def send_message(
    channel: str,
    text: str,
    web_client: Optional[WebClient] = None,
    token: str = DEFAULT_ACCESS_TOKEN,
    append_server_info: bool = True,
) -> SlackResponse:
    """Send a single message to Slack.

    Args:
        channel: The channel to send the message to
        text: The message content
        web_client: Optional pre-configured WebClient
        token: Slack API token
        append_server_info: Whether to include server information

    Returns:
        SlackResponse: The response from the Slack API

    Raises:
        SlackApiError: If the message cannot be sent
    """
    web_client = _get_or_create_client(web_client, token)

    if append_server_info:
        ip = socket_utils.get_local_ip()
        host_name = socket_utils.get_host_name()
        text_with_prefix = f"Message from {host_name} ({ip}):\n{text}"
    else:
        text_with_prefix = text

    try:
        response = web_client.chat_postMessage(
            channel=channel,
            text=text_with_prefix,
        )
        return response
    except SlackApiError as e:
        error_msg = f"Error sending text message: {e.response['error']}"
        logger.error(error_msg)
        raise SlackApiError(message=error_msg, response=e.response)


def send_reply(
    channel: str,
    thread_ts: str,
    text: str,
    web_client: Optional[WebClient] = None,
    token: str = DEFAULT_ACCESS_TOKEN,
) -> SlackResponse:
    """Send a Slack reply with an optional reply."""
    web_client = _get_or_create_client(web_client, token)

    # Send the reply
    try:
        response = web_client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=text,
        )
        return response
    except SlackApiError as e:
        error_msg = f"Error sending reply: {e.response['error']}"
        logger.error(error_msg)
        raise SlackApiError(message=error_msg, response=e.response)


@contextlib.contextmanager
def notification(
    channel: str,
    success_msg: str,
    error_msg: str,
    start_msg: Optional[str] = None,
    user_id_to_mention: Optional[str] = None,
    token: str = DEFAULT_ACCESS_TOKEN,
    web_client: Optional[WebClient] = None,
    replies: Optional[List[str]] = None,
    disable: bool = False,
    disable_callback: Optional[Callable[[], bool]] = None,
    append_server_info: bool = True,
) -> Generator[Optional["SlackMessenger"], None, None]:
    """Send a message when the task within the code block is finished, with an optional short preview."""
    slack_messenger = SlackMessenger(
        channel=channel,
        token=token,
        web_client=web_client,
        append_server_info=append_server_info,
    )

    with slack_messenger.notification(
        success_msg=success_msg,
        error_msg=error_msg,
        start_msg=start_msg,
        user_id_to_mention=user_id_to_mention,
        replies=replies,
        disable=disable,
        disable_callback=disable_callback,
    ) as messenger:
        yield messenger


@contextlib.contextmanager
def slack_notification(*args, **kwargs):
    raise NotImplementedError("Please use notification instead of slack_notification")
