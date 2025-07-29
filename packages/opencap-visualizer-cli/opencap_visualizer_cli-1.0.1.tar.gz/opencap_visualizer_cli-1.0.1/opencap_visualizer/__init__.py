"""
OpenCap Visualizer CLI - Generate videos from biomechanics data files

A command-line tool for creating videos from OpenCap biomechanics data using 
the deployed OpenCap Visualizer web application.
"""

__version__ = "1.0.1"
__author__ = "OpenCap Team"
__email__ = "opencap@stanford.edu"

from .cli import main

__all__ = ["main"] 