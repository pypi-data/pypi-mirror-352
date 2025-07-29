from abc import ABC, abstractmethod

# //////////////////////////////////////////////////////////////////////////////
class Backend(ABC):
    """Abstract base class for terminal backends.
    This class defines the interface for terminal operations, such as writing text,
    handling colors, and managing terminal size and key input.
    Subclasses must implement these methods to provide specific terminal functionality."""

    @abstractmethod
    def set_nodelay(self, boolean: bool) -> None:
        """Set the nodelay mode for the backend. When enabled, get_key() will not block the terminal."""
        pass

    @abstractmethod
    def sleep(self, ms: int) -> None:
        """Sleep for a given number of milliseconds."""
        pass

    @abstractmethod
    def write_text(self, y: int, x: int, chars: str, attr: int = 0) -> None:
        """Write text to the terminal at a specific position."""
        pass

    @abstractmethod
    def get_size(self, update = False) -> tuple[int,int]:
        """Get the size of the terminal, as (COLS, LINES).
        If update is True, a backend method will be called to update the current COLS and LINES values."""
        pass

    @abstractmethod
    def supports_color(self) -> bool:
        """Check if the backend supports color."""
        pass

    @abstractmethod
    def init_color(self, i: int, r: int, g: int, b: int) -> None:
        """Initialize a color with index 'i' and values 'r','g','b' to be used in color pairs by the terminal."""
        pass

    @abstractmethod
    def init_pair(self, i: int, fg: int, bg: int) -> None:
        """Initialize a color pair (fg,bg) which can be accessed with index 'i'."""
        pass

    @abstractmethod
    def get_color_pair(self, i: int) -> int:
        """Retrieve the color pair for a given index."""
        pass

    @abstractmethod
    def _start(self) -> None:
        """Initialize the backend, setting up the terminal."""
        pass

    @abstractmethod
    def _end(self) -> None:
        """Clean up the backend, restoring the terminal to its original state."""
        pass

    @abstractmethod
    def _refresh(self) -> None:
        """Refresh the terminal display."""
        pass

    @abstractmethod
    def _get_key(self) -> int:
        """Get a key press from the terminal."""
        pass

    @abstractmethod
    def _resize(self, h: int, w: int) -> None:
        """Resize the terminal to the given height and width."""
        pass


# //////////////////////////////////////////////////////////////////////////////
class CursesBackend(Backend):
    def __init__(self):
        self.curses = __import__("curses")

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_nodelay(self, boolean: bool) -> None:
        self.stdscr.nodelay(boolean)

    # --------------------------------------------------------------------------
    def sleep(self, ms: int) -> None:
        self.curses.napms(ms)

    # --------------------------------------------------------------------------
    def write_text(self, y: int, x: int, chars: str, attr: int = 0) -> None:
        try: self.stdscr.addstr(y, x, chars, attr)
        except self.curses.error: pass # ignore out of bounds error

    # --------------------------------------------------------------------------
    def get_size(self, update = False) -> tuple[int,int]:
        if update: self.curses.update_lines_cols()
        return self.curses.LINES, self.curses.COLS


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def supports_color(self) -> bool:
        try: return self.curses.can_change_color()
        except self.curses.error: return False

    # --------------------------------------------------------------------------
    def init_color(self, i: int, r: int, g: int, b: int) -> None:
        try: self.curses.init_color(i, r, g, b)
        except self.curses.error: pass

    # --------------------------------------------------------------------------
    def init_pair(self, i: int, fg: int, bg: int) -> None:
        try: self.curses.init_pair(i, fg, bg)
        except self.curses.error: pass

    # --------------------------------------------------------------------------
    def get_color_pair(self, i: int) -> int:
        try: return self.curses.color_pair(i)
        except self.curses.error: return 0


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _start(self) -> None:
        self.stdscr = self.curses.initscr()
        self.curses.noecho()
        self.curses.cbreak()
        self.stdscr.keypad(1)
        self.curses.curs_set(False)

        try: self.curses.start_color()
        except: pass

    # --------------------------------------------------------------------------
    def _end(self) -> None:
        if "stdscr" not in self.__dict__: return
        self.stdscr.keypad(0)
        self.curses.echo()
        self.curses.nocbreak()
        self.curses.endwin()


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _refresh(self) -> None:
        return # unnecessary, as stdscr.refresh() gets implicitly called by stdscr.getkey()

    # --------------------------------------------------------------------------
    def _get_key(self) -> int:
        return self.stdscr.getch()

    # --------------------------------------------------------------------------
    def _resize(self, h: int, w: int) -> None:
        try: self.stdscr.resize(h, w)
        except self.curses.error: pass


# //////////////////////////////////////////////////////////////////////////////
