"""
Enhanced memory management for Deep Agents following LangChain best practices.
"""
from typing import Dict, List, Any, Optional, Union
from langchain_core.memory import BaseMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import json
import os
from datetime import datetime, timedelta


class PersistentProjectMemory(BaseMemory):
    """
    Persistent memory for project context and long-term state management.
    
    Implements Deep Agents memory patterns for context quarantine and persistence.
    """
    
    def __init__(self, project_id: str, memory_dir: str = ".memory"):
        super().__init__()
        self.project_id = project_id
        self.memory_dir = memory_dir
        self.memory_file = os.path.join(memory_dir, f"{project_id}_memory.json")
        
        # Ensure memory directory exists
        os.makedirs(memory_dir, exist_ok=True)
        
        # Initialize memory structure
        self._memory = self._load_memory()
        
    @property
    def memory_variables(self) -> List[str]:
        """Return memory variable names."""
        return ["project_context", "agent_history", "decisions", "lessons_learned"]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables for the current context."""
        return {
            "project_context": self._get_project_context(),
            "agent_history": self._get_recent_agent_history(),
            "decisions": self._get_key_decisions(),
            "lessons_learned": self._get_lessons_learned()
        }
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from the current interaction."""
        timestamp = datetime.now().isoformat()
        
        # Save agent interaction
        self._memory["interactions"].append({
            "timestamp": timestamp,
            "inputs": inputs,
            "outputs": outputs,
            "agent": inputs.get("agent_name", "unknown")
        })
        
        # Extract and save decisions
        if "decision" in outputs or "architecture" in outputs:
            self._save_decision(inputs, outputs, timestamp)
        
        # Extract lessons learned
        if "lesson" in outputs or "error" in outputs:
            self._save_lesson(inputs, outputs, timestamp)
        
        # Persist to disk
        self._save_memory()
    
    def clear(self) -> None:
        """Clear memory."""
        self._memory = {
            "project_id": self.project_id,
            "created_at": datetime.now().isoformat(),
            "interactions": [],
            "decisions": [],
            "lessons_learned": [],
            "context": {}
        }
        self._save_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from disk."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return empty memory structure
        return {
            "project_id": self.project_id,
            "created_at": datetime.now().isoformat(),
            "interactions": [],
            "decisions": [],
            "lessons_learned": [],
            "context": {}
        }
    
    def _save_memory(self) -> None:
        """Save memory to disk."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self._memory, f, indent=2, default=str)
        except IOError as e:
            print(f"Warning: Could not save memory: {e}")
    
    def _get_project_context(self) -> str:
        """Get current project context summary."""
        context = self._memory.get("context", {})
        recent_decisions = self._get_recent_decisions(limit=3)
        
        context_parts = []
        
        if "project_size" in context:
            context_parts.append(f"Project size: {context['project_size']}")
        
        if "current_phase" in context:
            context_parts.append(f"Current phase: {context['current_phase']}")
        
        if recent_decisions:
            context_parts.append("Recent decisions:")
            for decision in recent_decisions:
                context_parts.append(f"- {decision['summary']}")
        
        return "\n".join(context_parts) if context_parts else "No project context available."
    
    def _get_recent_agent_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent agent interactions."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []
        
        for interaction in reversed(self._memory["interactions"]):
            try:
                interaction_time = datetime.fromisoformat(interaction["timestamp"])
                if interaction_time > cutoff:
                    recent.append({
                        "agent": interaction["agent"],
                        "timestamp": interaction["timestamp"],
                        "summary": self._summarize_interaction(interaction)
                    })
            except (ValueError, KeyError):
                continue
        
        return recent[:10]  # Limit to 10 most recent
    
    def _get_key_decisions(self) -> List[Dict[str, Any]]:
        """Get key architectural and design decisions."""
        return self._memory.get("decisions", [])[-5:]  # Last 5 decisions
    
    def _get_recent_decisions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent decisions with limit."""
        return self._memory.get("decisions", [])[-limit:]
    
    def _get_lessons_learned(self) -> List[Dict[str, Any]]:
        """Get lessons learned from previous issues."""
        return self._memory.get("lessons_learned", [])[-3:]  # Last 3 lessons
    
    def _save_decision(self, inputs: Dict[str, Any], outputs: Dict[str, str], timestamp: str) -> None:
        """Save an important decision."""
        decision = {
            "timestamp": timestamp,
            "agent": inputs.get("agent_name", "unknown"),
            "summary": self._extract_decision_summary(outputs),
            "rationale": outputs.get("rationale", ""),
            "impacts": outputs.get("impacts", [])
        }
        
        self._memory["decisions"].append(decision)
        
        # Keep only last 20 decisions
        if len(self._memory["decisions"]) > 20:
            self._memory["decisions"] = self._memory["decisions"][-20:]
    
    def _save_lesson(self, inputs: Dict[str, Any], outputs: Dict[str, str], timestamp: str) -> None:
        """Save a lesson learned."""
        lesson = {
            "timestamp": timestamp,
            "agent": inputs.get("agent_name", "unknown"),
            "issue": outputs.get("error", outputs.get("issue", "")),
            "solution": outputs.get("solution", ""),
            "prevention": outputs.get("prevention", "")
        }
        
        self._memory["lessons_learned"].append(lesson)
        
        # Keep only last 10 lessons
        if len(self._memory["lessons_learned"]) > 10:
            self._memory["lessons_learned"] = self._memory["lessons_learned"][-10:]
    
    def _summarize_interaction(self, interaction: Dict[str, Any]) -> str:
        """Create a summary of an interaction."""
        agent = interaction.get("agent", "unknown")
        outputs = interaction.get("outputs", {})
        
        if isinstance(outputs, dict):
            # Try to find a meaningful summary field
            for key in ["summary", "result", "message", "content"]:
                if key in outputs:
                    return str(outputs[key])[:100] + "..."
        
        return f"{agent} performed an action"
    
    def _extract_decision_summary(self, outputs: Dict[str, str]) -> str:
        """Extract decision summary from outputs."""
        for key in ["decision", "architecture", "design", "summary"]:
            if key in outputs:
                return str(outputs[key])[:200] + "..."
        
        return "Decision made"
    
    def update_context(self, key: str, value: Any) -> None:
        """Update project context."""
        self._memory["context"][key] = value
        self._save_memory()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get project context value."""
        return self._memory["context"].get(key, default)


class AgentMemoryManager:
    """
    Manager for agent-specific memory with context quarantine.
    """
    
    def __init__(self, memory_dir: str = ".memory"):
        self.memory_dir = memory_dir
        self._agent_memories: Dict[str, PersistentProjectMemory] = {}
    
    def get_agent_memory(self, agent_name: str, project_id: str) -> PersistentProjectMemory:
        """Get memory for a specific agent."""
        key = f"{agent_name}_{project_id}"
        
        if key not in self._agent_memories:
            self._agent_memories[key] = PersistentProjectMemory(
                project_id=key,
                memory_dir=self.memory_dir
            )
        
        return self._agent_memories[key]
    
    def clear_agent_memory(self, agent_name: str, project_id: str) -> None:
        """Clear memory for a specific agent."""
        key = f"{agent_name}_{project_id}"
        if key in self._agent_memories:
            self._agent_memories[key].clear()
    
    def get_shared_context(self, project_id: str) -> Dict[str, Any]:
        """Get shared context across all agents for a project."""
        shared_memory = PersistentProjectMemory(
            project_id=f"shared_{project_id}",
            memory_dir=self.memory_dir
        )
        
        return shared_memory.load_memory_variables({})
    
    def update_shared_context(self, project_id: str, key: str, value: Any) -> None:
        """Update shared context."""
        shared_memory = PersistentProjectMemory(
            project_id=f"shared_{project_id}",
            memory_dir=self.memory_dir
        )
        
        shared_memory.update_context(key, value)


# Global memory manager instance
_memory_manager = AgentMemoryManager()


def get_memory_manager() -> AgentMemoryManager:
    """Get the global memory manager instance."""
    return _memory_manager