import pytest
import pygame
from src.desktop import Desktop
from src.windows import Window

@pytest.fixture
def desktop():
    pygame.init()
    return Desktop(800, 600)

def test_window_creation(desktop):
    desktop.open_window("terminal")
    assert len(desktop.windows) == 1
    assert isinstance(desktop.windows[0], Window)

def test_window_closing(desktop):
    desktop.open_window("terminal")
    window = desktop.windows[0]
    desktop.close_window(window)
    assert not window.active 