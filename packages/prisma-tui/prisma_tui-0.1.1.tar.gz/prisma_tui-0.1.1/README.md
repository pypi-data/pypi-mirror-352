# PRISMA TUI

**Prisma TUI** (Python teRminal graphIcS with Multilayered trAnsparency) is a Python framework for building composable Terminal User Interfaces (TUIs). The `Terminal` class serves as a wrapper for terminal backends (e.g. curses) while providing a customizable application loop. Flexible layouts can be arranged by creating a hierarchy of `Section` class instances. Complex displays can be composed by

**Prisma** is built around the idea of *multilayered transparency*, which consists in overlaying different "layers" of text on top of each other and merging them together to compose more complex displays (think of stacking together images with transparency). This can be achieved by using the `Layer` class. **Prisma** also provides advanced color management, allowing to write and read multi-colored layers from its own custom **PAL** (*PALette*, JSON with color pair values) and **PRI** (*PRisma Image*, binary with the chars and the respective color pairs to form an image) formats.

<p align="center">
  <img src="logo.png" alt="Prisma TUI Logo" width="200"/><br>
  <small>Rendition of "Prisma" the cat.</small>
</p>

## Features

- **Layered Rendering:** Compose a TUI from multiple layers using [`prisma.Layer`](prisma/layer.py).
- **Section Hierarchy:** Organize the interface into nested sections with [`prisma.Section`](prisma/section.py) for flexible layouts.
- **Customizable Graphics:** Manage color palettes and PRI image files with [`prisma.Graphics`](prisma/graphics.py).
- **Backend Abstraction:** Pluggable terminal backends (default: curses) via [`prisma.Backend`](prisma/backend.py).
- **Declarative Drawing:** Draw text, borders, and layers at relative or absolute positions.
- **Palette & Attribute Control:** Fine-grained control over colors, attributes, and blending modes.
- **Event Loop:** Simple application lifecycle with [`prisma.Terminal`](prisma/terminal.py).

## Quick Example

```python
import prisma

class MyTUI(prisma.Terminal):
    def on_start(self):
        prisma.init_pair(1, prisma.COLOR_BLACK, prisma.COLOR_CYAN)

    def on_update(self):
        self.draw_text('c', 'c', "Hello, Prisma!", prisma.A_BOLD)
        self.draw_text("c+1", 'c', f"Key pressed: {self.key}", prisma.A_BOLD)
        self.draw_text('b', 'l', "Press F1 to exit", prisma.get_color_pair(1))

    def should_stop(self):
        return self.key == prisma.KEY_F1

if __name__ == "__main__":
    MyTUI().run()
```

## Core Concepts

- **Layer:** 2D grid of [`prisma.Pixel`](prisma/pixel.py) objects. Layers can be combined by overwritting, blending or merging their attributes.
- **Section:** Container for layers and child sections, enabling complex layouts.
- **Graphics:** Handles palette loading/saving and PRI image serialization.
- **Terminal:** Main application class; manages input, rendering, and lifecycle.


## File Structure

- [`prisma/`](prisma/)
  - [`__init__.py`](prisma/__init__.py): Package entry, constants, and helpers.
  - [`backend.py`](prisma/backend.py): Terminal backend abstraction.
  - [`constants.py`](prisma/constants.py): Curses-compatible constants.
  - [`graphics.py`](prisma/graphics.py): Palette and PRI file management.
  - [`layer.py`](prisma/layer.py): Layer and blending logic.
  - [`pixel.py`](prisma/pixel.py): Pixel representation.
  - [`section.py`](prisma/section.py): Section and layout management.
  - [`terminal.py`](prisma/terminal.py): Main TUI application loop.
  - [`utils.py`](prisma/utils.py): Utilities (Debug class).

## Demos

See the [`demos/`](demos/) folder for example applications:
- [`images.py`](demos/images.py): Image rendered from a pair of PRI and PAL files.
- [`layouts.py`](demos/layouts.py): Example of a complex layout built using different Section techniques.
- [`movement.py`](demos/movement.py): Example of an application in no-delay mode.
- [`keys.py`](demos/keys.py): Simple "hello world" example.

## Getting Started

1. Install using: `pip install prisma-tui`
2. Run a demo: `python demos/layouts.py`
3. Explore the API in [`prisma/`](prisma/).

## License

MIT License. See [LICENSE](LICENSE).

---

*For more details, see the docstrings in each module and the demo scripts.*

# TODO

- Make `utilities/image_formatter.py` into an actual utility.
