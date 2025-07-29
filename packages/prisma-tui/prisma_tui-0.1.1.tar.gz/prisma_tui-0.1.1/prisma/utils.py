import json
from collections import OrderedDict

############################# MOSAIC LAYOUT PARSER #############################
# ------------------------------------------------------------------------------
def apply_mask(idxs: list[list[int]], mat: list[list[str]], char: str) -> tuple[tuple[int]]:
    """Apply a mask to the matrix to filter out elements that match the given character."""
    mat_out = tuple(map(
        lambda idx, arr: tuple(filter(
            lambda tup: tup[1] == char,
            zip(idx, arr)
        )),
        idxs, mat
    ))
    return tuple(tuple(n[0] for n in arr) for arr in mat_out if arr)

# ------------------------------------------------------------------------------
def all_elements_equal(iterable: iter) -> bool:
    """Check if all elements in the iterable are equal."""
    iterator = iter(iterable)
    try: first = next(iterator)
    except StopIteration: return True
    return all(first == rest for rest in iterator)

# ------------------------------------------------------------------------------
def is_sequential(iterable: iter) -> bool:
    """Check if the elements in the iterable are sequential, starting from the first element."""
    iterator = iter(iterable)
    try: first = next(iterator)
    except StopIteration: return True
    return all(i == element for i,element in enumerate(iterator, start = first + 1))

# ------------------------------------------------------------------------------
def mosaic(layout: str, divider = '\n') -> dict:
    """Parse a mosaic layout string and return a dictionary with the dimensions
    and positions of each character in the layout."""
    if not layout: return {}

    rows = layout.split(divider)
    cols = tuple(zip(*rows))

    row_lenghts = map(len, rows)
    if len(set(row_lenghts)) != 1:
        raise ValueError("Not all mosaic rows have the same lenght.")

    row_idxs = tuple(range(len(row)) for row in rows)
    col_idxs = tuple(range(len(col)) for col in cols)

    chars = set(layout)
    if divider in chars: chars.remove(divider)

    h_mosaic = len(rows)
    w_mosaic = len(cols)

    data = OrderedDict()
    for char in sorted(chars):
        masked_row_idxs = apply_mask(row_idxs, rows, char)
        masked_col_idxs = apply_mask(col_idxs, cols, char)

        if not all_elements_equal(masked_row_idxs):
            raise ValueError(f"Not all rows for char '{char}' have the same length.")

        if not all_elements_equal(masked_col_idxs):
            raise ValueError(f"Not all columns for char '{char}' have the same length.")

        if not is_sequential(masked_row_idxs[0]):
            raise ValueError(f"Rows of char '{char}' are interrupted.")

        if not is_sequential(masked_col_idxs[0]):
            raise ValueError(f"Columns of char '{char}' are interrupted.")

        y_char = masked_col_idxs[0][0] / h_mosaic
        x_char = masked_row_idxs[0][0] / w_mosaic
        h_char = len(masked_col_idxs[0]) / h_mosaic
        w_char = len(masked_row_idxs[0]) / w_mosaic
        data[char] = (h_char, w_char, y_char, x_char)

    return data


########################### GENERAL UTILITY FUNCTIONS ##########################
# ------------------------------------------------------------------------------
def load_json(path_json: str) -> list | dict:
    """Load a JSON file and return its content."""
    with open(path_json, 'r') as file:
        return json.load(file)

# ------------------------------------------------------------------------------
def write_json(path_json: str, data: list | dict) -> None:
    """Write data to a JSON file."""
    with open(path_json, 'w') as file:
        json.dump(data, file)


################################# DEBUG LOGGER #################################
# //////////////////////////////////////////////////////////////////////////////
class Debug:
    """Debug logger class to log messages to a file.
    It creates a log file at the specified path and appends messages to it.
    Example:
        from prisma.utils import Debug;
        d = Debug("logs/name.log")
        d.log("Some value:", value)
    """
    def __init__(self, path: str):
        import datetime
        self.path = path
        with open(self.path, 'w') as file:
            file.write(f"{datetime.datetime.now()}\n\n")

    # --------------------------------------------------------------------------
    def log(self, *values, sep = ' ', end = '\n'):
        """Log values to the debug file.
        Args:
            *values: Values to log.
            sep (str): Separator between values. Default is a space.
            end (str): String appended after the last value. Default is a newline.
        """
        text = sep.join(map(str, values))
        with open(self.path, 'a') as file:
            file.write(text + end)


# //////////////////////////////////////////////////////////////////////////////
