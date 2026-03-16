# ------------ GAME_FUNCTIONS.PY -----------

# -------------DRAW COMMAND FUNCTIONS ------------------
# Circle() Function

def draw_circle(canvas, x=10, y=100, r=50, color=(100, 200, 255)):
    canvas.add_draw_command(("circle", x, y, r, color))
    
def draw_rect(canvas, x=100, y=100, w=70, h=50, color=(200, 50, 255)):
    canvas.add_draw_command(("rect", x, y, w, h, color))
    
def draw_line(canvas, x1=200, y1=100, x2=200, y2=270, color=(200, 200, 50), thickness=2):
    canvas.add_draw_command(("line", x1, y1, x2, y2, color, thickness))
    
def print_to_canvas(canvas, text, x=10, y=20, color=(255, 255, 255), size=12):
    canvas.add_draw_command(("text", str(text), x, y, color, size))

def cls(canvas):
    canvas.cls()