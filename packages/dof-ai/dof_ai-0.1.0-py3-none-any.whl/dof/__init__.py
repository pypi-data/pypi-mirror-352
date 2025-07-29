"""Top-level package for dof."""

from .dof import robot_hello, chain_robot_actions

__author__ = """Pieter Becking"""
__email__ = "ph.becking@gmail.com"
__version__ = "0.1.0"

# ASCII art for dof
DOF_ART = """
██████╗  ██████╗ ███████╗
██╔══██╗██╔═══██╗██╔════╝
██║  ██║██║   ██║█████╗  
██║  ██║██║   ██║██╔══╝  
██████╔╝╚██████╔╝██║     
╚═════╝  ╚═════╝ ╚═╝     
LangChain for Robotics 🤖
"""

__all__ = ["robot_hello", "chain_robot_actions"]

print(DOF_ART)
