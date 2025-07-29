"""
Moonlight SDK - Advanced Multi-Agent AI Orchestration Framework

A powerful framework for building intelligent AI applications with multiple execution modes,
extensive tool integration, and comprehensive workflow automation.
"""
    
__version__ = "0.1.9"
__author__ = "ecstra"
__description__ = "Advanced Multi-Agent AI Orchestration Framework"

import os
os.environ['TOKENIZERS_PARALLELISM'] = "false"

# Core Agent Architecture
from .core.agent_architecture import MoonlightProvider, Agent, Hive

# Execution Modes
from .core.modes.workflow import Workflow, WorkflowGenerator
from .core.modes.orchestrator import Orchestra
from .core.modes.deepsearch import DeepResearcher

# MCP Integration (if available)
try:
    from .core.mcp import MCPConfig, MCPClient, MCPRegistry
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False
    MCPConfig = None
    MCPRegistry = None
    MCPClient = None

__all__ = [
    # Core Components
    "MoonlightProvider",
    "Agent", 
    "AgentResponse",
    "AgentHistory",
    "Hive",
    
    # Workflow Components
    "WorkflowGenerator",
    "Workflow",
    
    # Modes
    "Orchestra",
    "DeepResearcher",
    
    # MCP Components
    "MCPConfig",
    "MCPRegistry", 
    "MCPClient",
    
    # Metadata
    "__version__",
    "__author__",
    "__description__",
]