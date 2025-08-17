"""
LangChain callback handlers for monitoring and observability.
"""
from typing import Any, Dict, List, Optional, Union
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult
import logging
import time
import json


class SoftwareDevCallbackHandler(BaseCallbackHandler):
    """
    Custom callback handler for software development agent monitoring.
    
    Provides observability into agent operations, tool usage, and performance.
    """
    
    def __init__(self, log_level: str = "INFO"):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Metrics tracking
        self.tool_calls = []
        self.agent_calls = []
        self.errors = []
        self.start_times = {}
        
    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> Any:
        """Called when a tool starts running."""
        tool_name = serialized.get("name", "unknown")
        call_id = kwargs.get("run_id", "unknown")
        
        self.start_times[call_id] = time.time()
        
        self.logger.info(f"🔧 Tool started: {tool_name}")
        self.logger.debug(f"Tool input: {input_str}")
        
        # Track tool usage
        self.tool_calls.append({
            "tool": tool_name,
            "start_time": time.time(),
            "input": input_str,
            "run_id": call_id
        })
    
    def on_tool_end(
        self,
        output: str,
        **kwargs: Any,
    ) -> Any:
        """Called when a tool ends running."""
        call_id = kwargs.get("run_id", "unknown")
        start_time = self.start_times.pop(call_id, time.time())
        duration = time.time() - start_time
        
        self.logger.info(f"✅ Tool completed in {duration:.2f}s")
        self.logger.debug(f"Tool output: {output}")
        
        # Update tool call record
        for call in reversed(self.tool_calls):
            if call["run_id"] == call_id:
                call["end_time"] = time.time()
                call["duration"] = duration
                call["output"] = output
                break
    
    def on_tool_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        **kwargs: Any,
    ) -> Any:
        """Called when a tool encounters an error."""
        call_id = kwargs.get("run_id", "unknown")
        
        self.logger.error(f"❌ Tool error: {str(error)}")
        
        # Track error
        self.errors.append({
            "type": "tool_error",
            "error": str(error),
            "run_id": call_id,
            "timestamp": time.time()
        })
    
    def on_agent_action(
        self,
        action,
        **kwargs: Any,
    ) -> Any:
        """Called when an agent takes an action."""
        self.logger.info(f"🤖 Agent action: {action.tool}")
        self.logger.debug(f"Action input: {action.tool_input}")
    
    def on_agent_finish(
        self,
        finish,
        **kwargs: Any,
    ) -> Any:
        """Called when an agent finishes."""
        self.logger.info(f"🎯 Agent finished: {finish.return_values}")
    
    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> Any:
        """Called when LLM starts running."""
        model = serialized.get("model", "unknown")
        call_id = kwargs.get("run_id", "unknown")
        
        self.start_times[call_id] = time.time()
        self.logger.info(f"🧠 LLM started: {model}")
    
    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any,
    ) -> Any:
        """Called when LLM ends running."""
        call_id = kwargs.get("run_id", "unknown")
        start_time = self.start_times.pop(call_id, time.time())
        duration = time.time() - start_time
        
        # Track token usage if available
        usage = response.llm_output.get("token_usage", {}) if response.llm_output else {}
        
        self.logger.info(f"🧠 LLM completed in {duration:.2f}s")
        if usage:
            self.logger.info(f"Tokens used: {usage}")
    
    def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        **kwargs: Any,
    ) -> Any:
        """Called when LLM encounters an error."""
        call_id = kwargs.get("run_id", "unknown")
        
        self.logger.error(f"❌ LLM error: {str(error)}")
        
        # Track error
        self.errors.append({
            "type": "llm_error",
            "error": str(error),
            "run_id": call_id,
            "timestamp": time.time()
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return {
            "tool_calls": len(self.tool_calls),
            "errors": len(self.errors),
            "avg_tool_duration": self._avg_tool_duration(),
            "tool_usage_breakdown": self._tool_usage_breakdown(),
            "error_summary": self._error_summary()
        }
    
    def _avg_tool_duration(self) -> float:
        """Calculate average tool duration."""
        durations = [call.get("duration", 0) for call in self.tool_calls if "duration" in call]
        return sum(durations) / len(durations) if durations else 0.0
    
    def _tool_usage_breakdown(self) -> Dict[str, int]:
        """Get tool usage breakdown."""
        breakdown = {}
        for call in self.tool_calls:
            tool = call["tool"]
            breakdown[tool] = breakdown.get(tool, 0) + 1
        return breakdown
    
    def _error_summary(self) -> Dict[str, int]:
        """Get error summary."""
        summary = {}
        for error in self.errors:
            error_type = error["type"]
            summary[error_type] = summary.get(error_type, 0) + 1
        return summary
    
    def save_metrics(self, filepath: str):
        """Save metrics to file."""
        metrics = self.get_metrics()
        metrics["detailed_tool_calls"] = self.tool_calls
        metrics["detailed_errors"] = self.errors
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        self.logger.info(f"📊 Metrics saved to {filepath}")


class StreamingCallbackHandler(BaseCallbackHandler):
    """
    Streaming callback handler for real-time agent output.
    """
    
    def __init__(self, output_callback: Optional[callable] = None):
        super().__init__()
        self.output_callback = output_callback or print
        
    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Called when new token is generated."""
        if self.output_callback:
            self.output_callback(token, end="", flush=True)
    
    def on_agent_action(self, action, **kwargs: Any) -> Any:
        """Called when agent takes action."""
        self.output_callback(f"\n🤖 Using tool: {action.tool}\n")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        """Called when tool starts."""
        tool_name = serialized.get("name", "unknown")
        self.output_callback(f"🔧 Running {tool_name}...\n")
    
    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Called when tool ends."""
        self.output_callback(f"✅ Tool completed\n")


def get_default_callbacks() -> List[BaseCallbackHandler]:
    """Get default callback handlers for the system."""
    return [
        SoftwareDevCallbackHandler(log_level="INFO"),
        StreamingCallbackHandler()
    ]