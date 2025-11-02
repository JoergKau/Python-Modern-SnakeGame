"""
Utility functions for PySnakes game.
"""
import os
import sys


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    
    When running as a PyInstaller executable, resources are extracted to
    sys._MEIPASS. This function handles both development and bundled scenarios.
    
    Args:
        relative_path (str): Path relative to the project root
        
    Returns:
        str: Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Running in development mode
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def get_font_path(font_name):
    """
    Get the absolute path to a font file.
    
    Args:
        font_name (str): Name of the font file (e.g., "Heroking-Regular.ttf")
        
    Returns:
        str: Absolute path to the font file
    """
    return resource_path(os.path.join("assets", "fonts", font_name))


def get_sound_path(sound_name):
    """
    Get the absolute path to a sound file.
    
    Args:
        sound_name (str): Name of the sound file (e.g., "eat.wav")
        
    Returns:
        str: Absolute path to the sound file
    """
    return resource_path(os.path.join("assets", "sounds", sound_name))


def get_data_path(filename):
    """
    Get the absolute path to a data file (like highscores.json).
    
    Args:
        filename (str): Name of the data file (e.g., "highscores.json")
        
    Returns:
        str: Absolute path to the data file
    """
    return resource_path(filename)