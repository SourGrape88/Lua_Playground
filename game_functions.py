# ------------ GAME_FUNCTIONS.PY -----------

# -------------DRAW COMMAND FUNCTIONS ------------------
# Circle() Function

def draw_circle(canvas, x=10, y=100, r=50, color=(100, 200, 255), thickness=2):
    canvas.add_draw_command(("circle", x, y, r, color, thickness))
    
def draw_circlefill(canvas, x=100, y=100, r=50, color=(250, 200, 55)):
    canvas.add_draw_command(("circlefill", x, y, r, color))

def draw_rect(canvas, x=200, y=100, w=70, h=50, color=(200, 50, 255), thickness=2):
    canvas.add_draw_command(("rect", x, y, w, h, color, thickness))

def draw_rectfill(canvas, x=300, y=100, w=70, h=50, color=(0,150, 255)):
    canvas.add_draw_command(("rectfill", x, y, w, h, color))

def draw_line(canvas, x1=400, y1=100, x2=200, y2=270, color=(0, 200, 250), thickness=2):
    canvas.add_draw_command(("line", x1, y1, x2, y2, color, thickness))
    
def print_to_canvas(canvas, text, x=10, y=20, color=(255, 255, 255), size=12):
    canvas.add_draw_command(("text", str(text), x, y, color, size))

def load_sprite_to_canvas(canvas, name, path):
    canvas.load_sprite(name, path)

def sprite(canvas, name, x=500, y=100, w=None, h=None):
    if w is None or h is None:
        canvas.add_draw_command(("sprite", name, x, y, w, h))
    else:
        canvas.add_draw_command(("sprite", name, x, y, w, h))

def cls(canvas):
    canvas.cls()
