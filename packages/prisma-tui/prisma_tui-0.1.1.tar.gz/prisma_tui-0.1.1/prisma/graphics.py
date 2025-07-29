import prisma

# //////////////////////////////////////////////////////////////////////////////
class Graphics:
    """Graphics class to manage palette and PRI files."""
    def __init__(self):
        self.palette: dict = {"colors": [], "pairs":  []}


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_colors(self, colors) -> None:
        """Update the color palette with a list of (r,g,b) colors.
        RBG values should be in the range 0-1000."""
        self.palette["colors"] = [[int(c) for c in color] for color in colors]

    # --------------------------------------------------------------------------
    def set_pairs(self, pairs) -> None:
        """Update the color pairs with a list of (fg, bg) pairs."""
        self.palette["pairs"] = [[int(p) for p in pair] for pair in pairs]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def save_palette(self, path_pal: str) -> None:
        """Save the current palette to a JSON file."""
        prisma.utils.write_json(path_pal, self.palette)

    # --------------------------------------------------------------------------
    def load_palette(self, path_pal: str) -> None:
        """Load a palette from a JSON file."""
        self.palette = prisma.utils.load_json(path_pal)
        colors = self.palette["colors"]
        pairs  = self.palette["pairs"]

        assert len(colors) <= prisma.MAX_PALETTE_COLORS, \
            f"Graphics has {len(colors)} colors, max is {prisma.MAX_PALETTE_COLORS}."

        assert len(pairs) <= prisma.MAX_PALETTE_PAIRS, \
            f"Graphics has {len(pairs)} pairs, max is {prisma.MAX_PALETTE_PAIRS}."

        if not prisma._BACKEND.supports_color(): return

        for i,color in enumerate(colors):
            prisma._BACKEND.init_color(i, *color)

        for i,(fg,bg) in enumerate(pairs):
            prisma._BACKEND.init_pair(i, fg, bg)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @classmethod
    def save_layer(cls, path_pri: str, layer: "prisma.Layer") -> None:
        """Save a layer to a PRI file"""
        chars: list[str] = layer.get_chars_row_as_strs()
        pairs: list[list[int]] = layer.get_attrs()

        h = len(chars)
        w = len(chars[0]) if h > 0 else 0

        assert all(len(row) == w for row in chars), "All rows in 'chars' must have the same width."
        assert all(len(row) == w for row in pairs), "All rows in 'pairs' must have the same width as 'chars'."
        assert len(pairs) == h , "'pairs' must have the same height as 'chars'."

        with open(path_pri, "wb") as file:
            file.write(h.to_bytes(2, byteorder="little"))
            file.write(w.to_bytes(2, byteorder="little"))
            file.write(b'\n')
            file.write('\n'.join(chars).encode("utf-8"))
            file.write(b'\n')
            for row in pairs: file.write(bytes(int(x) for x in row))

    # --------------------------------------------------------------------------
    @classmethod
    def load_layer(cls, path_pri: str) -> "prisma.Layer":
        """Load a layer from a PRI file."""
        with open(path_pri, "rb") as file:
            h = int.from_bytes(file.read(2), byteorder="little")
            w = int.from_bytes(file.read(2), byteorder="little")
            nchars = h * (w + 1) - 1 # +1 for breaklines (except the last one)

            file.read(1) # skip a breakline character
            chars = file.read(nchars).decode("utf-8")
            file.read(1) # skip a breakline character

            pairs = [[int(file.read(1)[0]) for _ in range(w)] for _ in range(h)]
            attrs = [[prisma._BACKEND.get_color_pair(i) for i in row] for row in pairs]
        return prisma.Layer(h, w, chars.split('\n'), attrs)


# //////////////////////////////////////////////////////////////////////////////
