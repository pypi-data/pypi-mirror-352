"""Progress indicators and utilities."""

import sys
import time
import threading
from typing import Optional

class ProgressSpinner:
    """A simple progress spinner for console output."""
    
    def __init__(self, message: str = "Processing", delay: float = 0.1):
        """Initialize the spinner.
        
        Args:
            message: The message to display next to the spinner
            delay: Delay between spinner updates in seconds
        """
        self.message = message
        self.delay = delay
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.spinner_chars = '|/-\\'
        self.spinner_pos = 0
    
    def spin(self) -> None:
        """Run the spinner animation."""
        while not self._stop_event.is_set():
            sys.stdout.write(f"\r{self.message} {self.spinner_chars[self.spinner_pos]} ")
            sys.stdout.flush()
            self.spinner_pos = (self.spinner_pos + 1) % len(self.spinner_chars)
            self._stop_event.wait(self.delay)
    
    def start(self) -> None:
        """Start the spinner in a background thread."""
        if self.running:
            return
            
        self.running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.spin)
        self._thread.daemon = True
        self._thread.start()
    
    def stop(self, clear: bool = True) -> None:
        """Stop the spinner.
        
        Args:
            clear: Whether to clear the spinner line
        """
        if not self.running:
            return
            
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
        
        if clear:
            sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
            sys.stdout.flush()
        else:
            sys.stdout.write("\n")
            sys.stdout.flush()
            
        self.running = False
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


def progress_bar(iterable, length: int = 40, title: str = "Progress"):
    """A simple progress bar generator.
    
    Args:
        iterable: The iterable to track progress for
        length: Width of the progress bar in characters
        title: Title to display above the progress bar
        
    Yields:
        Items from the iterable
    """
    total = len(iterable)
    if total == 0:
        return
    
    print(f"{title}:")
    
    for i, item in enumerate(iterable):
        progress = (i + 1) / total
        bar_length = int(length * progress)
        bar = '█' * bar_length + '-' * (length - bar_length)
        sys.stdout.write(f"\r[{bar}] {int(progress * 100)}%")
        sys.stdout.flush()
        yield item
    
    # Clear the progress bar when done
    sys.stdout.write("\r" + " " * (length + 10) + "\r")
    sys.stdout.flush()
