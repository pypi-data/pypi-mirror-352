# hercules/core.py
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, register_function
from typing import List, Dict, Any, Optional, Callable, Union, Annotated
import ast
import re
import json
import os
import requests
from pathlib import Path

class Hercules:
    def __init__(
        self,
        llm_config: Optional[Dict[str, Any]] = None,
        tools: bool = False,
        tools_config: Optional[Union[List[Any], Dict[str, Any]]] = None,
        roles_generator: Optional[Callable[[str], List[str]]] = None,
        custom_user_proxy: Optional[UserProxyAgent] = None,
        custom_agent_factory: Optional[Callable[[str, Dict[str, Any], str], Any]] = None,
        custom_prompts: Optional[Dict[str, str]] = None,
        max_rounds: int = 12,
        speaker_selection: str = "auto",
        enable_code_execution: bool = False,
    ):
        """
        Initialize Hercules multi-agent framework
        
        Args:
            llm_config: LLM configuration dictionary
            tools: Enable/disable tools for agents
            tools_config: List of tool functions or dict with tool configurations
            roles_generator: Custom function to generate agent roles
            custom_user_proxy: Custom UserProxyAgent instance
            custom_agent_factory: Custom agent creation function
            custom_prompts: Custom system prompts for specific roles
            max_rounds: Maximum conversation rounds
            speaker_selection: Method for selecting next speaker
            enable_code_execution: Enable code execution capabilities
        """
        self.llm_config = llm_config or {"model": "gpt-4", "temperature": 0.7}
        self.tools_enabled = tools
        self.tools_config = self._process_tools_config(tools_config)
        self.roles_generator = roles_generator or self._generate_roles
        self.custom_user_proxy = custom_user_proxy
        self.custom_agent_factory = custom_agent_factory
        self.custom_prompts = custom_prompts or {}
        self.max_rounds = max_rounds
        self.speaker_selection = speaker_selection
        self.enable_code_execution = enable_code_execution

        # Controller agent for generating roles and prompts
        self.controller = AssistantAgent(
            name="Architect", 
            llm_config=self.llm_config,
            system_message="You are an AI system architect that helps design agent roles and prompts."
        )

        # User proxy agent with code execution support
        code_execution_config = {
            "work_dir": "hercules_workspace",
            "use_docker": False,
        } if enable_code_execution else False

        self.user_proxy = custom_user_proxy or UserProxyAgent(
            name="User",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").strip().endswith("TERMINATE"),
            code_execution_config=code_execution_config,
        )

        self.agents = []
        self.groupchat = None
        self.manager = None
        self.registered_tools = {}

    def _process_tools_config(self, tools_config) -> List[Any]:
        """Process and validate tools configuration"""
        if not tools_config:
            return []
        
        if isinstance(tools_config, list):
            return tools_config
        elif isinstance(tools_config, dict):
            # Convert dict config to list of tools
            tools_list = []
            for tool_name, tool_func in tools_config.items():
                if callable(tool_func):
                    tools_list.append(tool_func)
                else:
                    print(f"Warning: Tool '{tool_name}' is not callable")
            return tools_list
        else:
            print("Warning: tools_config should be a list or dict")
            return []

    def _register_tools_with_agents(self, agent: AssistantAgent):
        """Register tools with a specific agent using AutoGen's register_function"""
        if not self.tools_enabled or not self.tools_config:
            return
        
        for tool_func in self.tools_config:
            try:
                # Register the function with the agent and user proxy
                register_function(
                    tool_func,
                    caller=agent,
                    executor=self.user_proxy,
                    name=getattr(tool_func, '__name__', str(tool_func)),
                    description=getattr(tool_func, '__doc__', f"Tool function: {tool_func}")
                )
                print(f"Registered tool '{getattr(tool_func, '__name__', str(tool_func))}' with agent '{agent.name}'")
            except Exception as e:
                print(f"Error registering tool {getattr(tool_func, '__name__', str(tool_func))}: {e}")

    def _generate_roles(self, task: str) -> List[str]:
        """Generate agent roles for the task using LLM"""
        sys_prompt = (
            "You're an AI system designer. Generate 3–5 role names for AI agents "
            f"to collaboratively solve this task:\n\n{task}\n\n"
            "Return only a Python list of role names, for example: ['Researcher', 'Analyst', 'Writer']\n"
            "Make sure the roles are relevant to the specific task."
        )
        
        try:
            # Use the controller agent to generate roles
            chat_result = self.user_proxy.initiate_chat(
                self.controller,
                message=sys_prompt,
                silent=True,
                max_turns=1
            )
            
            # Extract the response
            if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
                response = chat_result.chat_history[-1]['content']
            else:
                response = "['Researcher', 'Analyst', 'Writer']"
            
            # Try to extract list from response
            roles = self._extract_list_from_response(response)
            return roles if roles else ["Researcher", "Analyst", "Writer"]
            
        except Exception as e:
            print(f"Error generating roles: {e}")
            return ["Researcher", "Analyst", "Writer"]

    def _extract_list_from_response(self, response: str) -> Optional[List[str]]:
        """Extract a Python list from LLM response"""
        try:
            # Look for list pattern in response
            list_pattern = r'\[.*?\]'
            matches = re.findall(list_pattern, response, re.DOTALL)
            
            if matches:
                # Try to evaluate the first match
                list_str = matches[0]
                roles = ast.literal_eval(list_str)
                if isinstance(roles, list) and all(isinstance(role, str) for role in roles):
                    return roles
            
            # Alternative: look for quoted strings
            quoted_pattern = r'["\']([^"\']+)["\']'
            quotes = re.findall(quoted_pattern, response)
            if quotes and len(quotes) >= 3:
                return quotes[:5]  # Return max 5 roles
                
        except Exception as e:
            print(f"Error extracting list: {e}")
        
        return None

    def _generate_prompt(self, role: str, task: str) -> str:
        """Generate a system prompt for a specific role"""
        if role in self.custom_prompts:
            return self.custom_prompts[role]

        # Add tool information to prompt if tools are enabled
        tool_info = ""
        if self.tools_enabled and self.tools_config:
            tool_names = [getattr(tool, '__name__', str(tool)) for tool in self.tools_config]
            tool_info = f"\n\nYou have access to the following tools: {', '.join(tool_names)}. Use them when appropriate to complete your tasks. When you need to use a tool, call it directly by name."

        prompt_request = (
            f"Create a system prompt for an AI agent with the role '{role}' "
            f"working on this task: '{task}'.\n\n"
            "The prompt should:\n"
            "1. Define the agent's expertise and responsibilities\n"
            "2. Specify how they should contribute to the team\n"
            "3. Include any relevant guidelines or constraints\n"
            "4. Be concise but comprehensive\n"
            f"{tool_info}\n\n"
            "Return only the system prompt text without any additional formatting."
        )
        
        try:
            chat_result = self.user_proxy.initiate_chat(
                self.controller,
                message=prompt_request,
                silent=True,
                max_turns=1
            )
            
            if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
                prompt = chat_result.chat_history[-1]['content'].strip()
                return prompt + tool_info
            else:
                return self._default_prompt(role, task) + tool_info
                
        except Exception as e:
            print(f"Error generating prompt for {role}: {e}")
            return self._default_prompt(role, task) + tool_info

    def _default_prompt(self, role: str, task: str) -> str:
        """Generate a default system prompt for a role"""
        return (
            f"You are a {role} working on the following task: {task}\n\n"
            f"As a {role}, you should contribute your specialized knowledge and skills "
            "to help the team accomplish this task effectively. Provide clear, "
            "actionable insights and collaborate constructively with other team members."
        )

    def _default_agent_factory(self, role: str, config: Dict[str, Any], system_prompt: str):
        """Create an agent with the specified role and configuration"""
        agent_config = config.copy()
        
        # Create standard AssistantAgent
        agent = AssistantAgent(
            name=role,
            llm_config=agent_config,
            system_message=system_prompt
        )
        
        # Register tools with the agent if tools are enabled
        if self.tools_enabled:
            self._register_tools_with_agents(agent)
        
        return agent

    def _create_agents(self, roles: List[str], task: str):
        """Create agents for the specified roles"""
        factory = self.custom_agent_factory or self._default_agent_factory
        self.agents = []

        for role in roles:
            try:
                prompt = self._generate_prompt(role, task)
                agent = factory(role, self.llm_config, prompt)
                self.agents.append(agent)
                print(f"Created agent: {role}")
            except Exception as e:
                print(f"Error creating agent {role}: {e}")

    def add_tool(self, tool_func: Callable):
        """Add a tool to the tools configuration"""
        if not self.tools_enabled:
            print("Warning: Tools are not enabled. Enable tools=True to use this feature.")
            return
        
        if callable(tool_func):
            self.tools_config.append(tool_func)
            # Re-register tools with existing agents
            for agent in self.agents:
                self._register_tools_with_agents(agent)
            print(f"Added tool: {getattr(tool_func, '__name__', str(tool_func))}")
        else:
            print("Error: Tool must be a callable function")

    def remove_tool(self, tool_name: str):
        """Remove a tool by name"""
        original_count = len(self.tools_config)
        self.tools_config = [
            tool for tool in self.tools_config 
            if getattr(tool, '__name__', str(tool)) != tool_name
        ]
        if len(self.tools_config) < original_count:
            print(f"Removed tool: {tool_name}")
        else:
            print(f"Tool '{tool_name}' not found")

    def list_tools(self) -> List[str]:
        """List all available tools"""
        return [getattr(tool, '__name__', str(tool)) for tool in self.tools_config]

    def run(self, task: str) -> str:
        """Run the multi-agent collaboration on the given task"""
        try:
            # Generate roles and create agents
            roles = self.roles_generator(task)
            print(f"Generated roles: {roles}")
            
            self._create_agents(roles, task)
            
            if not self.agents:
                return "Error: No agents were created successfully."

            # Set up group chat
            all_agents = [self.user_proxy] + self.agents
            self.groupchat = GroupChat(
                agents=all_agents, 
                messages=[], 
                max_round=self.max_rounds,
                speaker_selection_method=self.speaker_selection
            )
            
            self.manager = GroupChatManager(
                groupchat=self.groupchat, 
                llm_config=self.llm_config
            )

            # Start the collaboration
            chat_result = self.user_proxy.initiate_chat(
                self.manager, 
                message=task,
                max_turns=self.max_rounds
            )

            # Generate summary
            summary = self._generate_summary(task, chat_result)
            return summary
            
        except Exception as e:
            return f"Error during execution: {str(e)}"

    def _generate_summary(self, task: str, chat_result) -> str:
        """Generate a summary of the collaboration"""
        summary = f"\n--- HERCULES Summary ---\nTask: {task}\n"
        summary += f"Agents Created: {[agent.name for agent in self.agents]}\n"
        summary += f"Tools Enabled: {self.tools_enabled}\n"
        
        if self.tools_enabled:
            summary += f"Available Tools: {self.list_tools()}\n"
        
        try:
            if hasattr(chat_result, 'chat_history') and chat_result.chat_history:
                summary += f"Total Messages: {len(chat_result.chat_history)}\n"
                summary += "\n--- Key Contributions ---\n"
                
                # Group messages by agent
                agent_contributions = {}
                for msg in chat_result.chat_history:
                    sender = msg.get('name', 'Unknown')
                    content = msg.get('content', '')
                    if sender not in agent_contributions:
                        agent_contributions[sender] = []
                    agent_contributions[sender].append(content)
                
                # Summarize contributions
                for agent_name, messages in agent_contributions.items():
                    if agent_name != 'User' and messages:
                        summary += f"\n[{agent_name}]:\n"
                        # Use the last message or a summary
                        last_msg = messages[-1][:200] + "..." if len(messages[-1]) > 200 else messages[-1]
                        summary += f"{last_msg}\n"
            else:
                summary += "No chat history available.\n"
                
        except Exception as e:
            summary += f"Error generating detailed summary: {e}\n"
        
        return summary

    # Getter methods
    def get_agents(self) -> List[AssistantAgent]:
        return self.agents
    
    def get_user_proxy(self) -> UserProxyAgent:
        return self.user_proxy
    
    def get_groupchat(self) -> Optional[GroupChat]:
        return self.groupchat
    
    def get_manager(self) -> Optional[GroupChatManager]:
        return self.manager


# ==================== EXAMPLE TOOLS ====================

# Default tools collection
# DEFAULT_TOOLS = [write_file, read_file, web_search, calculate]
