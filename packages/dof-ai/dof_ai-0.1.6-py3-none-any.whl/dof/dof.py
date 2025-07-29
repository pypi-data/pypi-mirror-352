"""Main module for dof - LangChain for robotics"""


def robot_hello():
    """A simple function to test our package works"""
    return "Hello from Sotrm, Jasper and Pieter!"


def chain_robot_actions(actions):
    """Example function for chaining robot actions"""
    return f"Executing robot action chain: {' -> '.join(actions)}"
