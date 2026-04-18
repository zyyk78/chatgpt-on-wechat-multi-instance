"""
Agent Event Handler - Handles agent events and thinking process output
"""

from common.log import logger


class AgentEventHandler:
    """
    Handles agent events and optionally sends intermediate messages to channel
    """
    
    def __init__(self, context=None, original_callback=None):
        """
        Initialize event handler
        
        Args:
            context: COW context (for accessing channel)
            original_callback: Original event callback to chain
        """
        self.context = context
        self.original_callback = original_callback
        
        # Get channel for sending intermediate messages
        self.channel = None
        if context:
            self.channel = context.kwargs.get("channel") if hasattr(context, "kwargs") else None
        
        # Track current thinking for channel output
        self.current_thinking = ""
        self.turn_number = 0
    
    def handle_event(self, event):
        """
        Main event handler

        Args:
            event: Event dict with type and data
        """
        event_type = event.get("type")
        data = event.get("data", {})

        # Dispatch to specific handlers
        if event_type == "turn_start":
            self._handle_turn_start(data)
        elif event_type == "message_update":
            self._handle_message_update(data)
        elif event_type == "message_end":
            self._handle_message_end(data)
        elif event_type == "tool_execution_start":
            self._handle_tool_execution_start(data)
        elif event_type == "tool_execution_end":
            self._handle_tool_execution_end(data)

        # Call original callback if provided
        if self.original_callback:
            self.original_callback(event)
    
    def _handle_turn_start(self, data):
        """Handle turn start event"""
        self.turn_number = data.get("turn", 0)
        self.has_tool_calls_in_turn = False
        self.current_thinking = ""
    
    def _handle_message_update(self, data):
        """Handle message update event (streaming text)"""
        delta = data.get("delta", "")

        # If show_thinking is False and delta starts with [thinking] tag,
        # this is thinking content that should not be sent to WeChat
        from config import conf
        if not conf().get("show_thinking", False):
            if delta.startswith("[thinking] ") or delta.startswith("<think>"):
                # Skip thinking content when show_thinking=False
                return

        self.current_thinking += delta
    
    def _handle_message_end(self, data):
        """Handle message end event"""
        from config import conf
        show_thinking = conf().get("show_thinking", False)

        tool_calls = data.get("tool_calls", [])

        # Log thinking content (for debugging/logging purposes) - always log regardless of show_thinking
        if self.current_thinking.strip():
            if tool_calls:
                logger.info(f"💭 {self.current_thinking.strip()[:200]}{'...' if len(self.current_thinking) > 200 else ''}")
            else:
                logger.debug(f"💬 {self.current_thinking.strip()[:200]}{'...' if len(self.current_thinking) > 200 else ''}")

        # For WeChat (show_thinking=false), thinking should NEVER be sent to channel
        # Only send thinking if show_thinking=True AND there are tool_calls
        if show_thinking and tool_calls and self.current_thinking.strip():
            self._send_to_channel(f"{self.current_thinking.strip()}")

        # Always clear thinking at the end of message
        self.current_thinking = ""
    
    def _handle_tool_execution_start(self, data):
        """Handle tool execution start event"""
        from config import conf
        # For WeChat (show_thinking=false), clear thinking immediately when tool execution starts
        # so it won't be sent to the channel
        if not conf().get("show_thinking", False):
            self.current_thinking = ""
    
    def _handle_tool_execution_end(self, data):
        """Handle tool execution end event - logged by agent_stream.py"""
        pass
    
    def _send_to_channel(self, message):
        """
        Try to send intermediate message to channel.
        Skipped in SSE mode because thinking text is already streamed via on_event.
        """
        if self.context and self.context.get("on_event"):
            return

        if self.channel:
            try:
                from bridge.reply import Reply, ReplyType
                reply = Reply(ReplyType.TEXT, message)
                self.channel._send(reply, self.context)
            except Exception as e:
                logger.debug(f"[AgentEventHandler] Failed to send to channel: {e}")
    
    def log_summary(self):
        """Log execution summary - simplified"""
        # Summary removed as per user request
        # Real-time logging during execution is sufficient
        pass
