


class RedrawHandler:

    def __init__(self, model):
        self.model = model

    def handle_grid_resize(self, args):

        for grid_id, width, height in args:
            
            buffer_height = max(height, 1000)

            chars = [[" "] * width for _ in range(buffer_height)]
            hl = [[(self.model.default_fg, self.model.default_bg)
                  for _ in range(width)] for _ in range(buffer_height)]

            self.model.grids[grid_id] = {
                "chars": chars,
                "hl": hl,
                "width": width,
                "height": height,
                "row": 0,
                "col": 0
            }

    def handle_grid_line(self, args):

        for line in args:
            grid_id, row, col, cells = line[:4]
            grid = self.model.grids.get(grid_id)
            if not grid:
                continue
        
            # Ensure buffer can hold this row
            while row >= len(grid["chars"]):
                grid["chars"].append([" "] * grid["width"])
                grid["hl"].append([(self.model.default_fg, self.model.default_bg)] * grid["width"])

            #chars = grid["chars"]
            #hl = grid["hl"]

            current_col = col
            last_hl_id = None

            for cell in cells:
                char = cell[0] if len(cell) > 0 else " "
                hl_id = cell[1] if len(cell) > 1 else last_hl_id
                repeat = cell[2] if len(cell) > 2 else 1

                last_hl_id = hl_id
                fg, bg = self.model.hl_attrs.get(
                    hl_id,
                    (self.model.default_fg, self.model.default_bg)
                )

                for i in range(repeat):
                    c_pos = current_col + i
                    if 0 <= c_pos < grid["width"]:
                        #display_char = char if char else " "
                        grid["chars"][row][c_pos] = char
                        grid["hl"][row][c_pos] = (fg, bg)

                current_col += repeat
                #print("HL ID:", hl_id)

    
    def handle_grid_scroll(self, args):
        for grid_id, top, bottom, left, right, rows, cols in args:
            grid = self.model.grids.get(grid_id)
            if not grid:
                continue

            chars = grid["chars"]
            hl = grid["hl"]

            # vertical scroll
            if rows != 0:
                region = chars[top:bottom]
                region_hl = hl[top:bottom]

                if rows > 0:
                    # scroll up
                    for r in range(top, bottom - rows):
                        chars[r][left:right] = region[r - top + rows][left:right]
                        hl[r][left:right] = region_hl[r - top + rows][left:right]

                    for r in range(bottom - rows, bottom):
                        chars[r][left:right] = [" "] * (right - left)
                        hl[r][left:right] = [(self.model.default_fg, self.model.default_bg)] * (right - left)

                else:
                    rows = -rows
                    # scroll down
                    for r in range(bottom - 1, top + rows - 1, -1):
                        chars[r][left:right] = region[r - top - rows][left:right]
                        hl[r][left:right] = region_hl[r - top - rows][left:right]

                    for r in range(top, top + rows):
                        chars[r][left:right] = [" "] * (right - left)
                        hl[r][left:right] = [(self.model.default_fg, self.model.default_bg)] * (right - left)

    def clamp_grid_row(self, grid):
        # Ensure grid_row stays within valid buffer bounds
        max_row = max(0, len(grid["chars"]) - grid["height"])
        grid["row"] = max(0, min(grid["row"], max_row))
    