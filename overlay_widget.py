# --------- OVERLAY_WIDGET.PY -----------------

from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtOpenGL import QOpenGLShader, QOpenGLShaderProgram
from PyQt6.QtCore import QTimer, Qt
from OpenGL import GL

class HolographicOverlay(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize OpenGL Functions
        
        # Allow Mouse Events to "Pass Through" the Overlay
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        # Always draw on top of other Widgets
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop)
        # Prevent Flickering by avoiding default background
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        # Placeholder for the Shader Program
        self.shader_program = None
        # Time Variable for Animation
        self.time = 0.0

        # Timer for updating the Shader Every Frame (~60FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(16) # 16ms = 60FPS

    def initializeGL(self):
        
        # Enable Transparency Blending
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        
        # Vertex Shader: Passes Normalized Coordinates to Fragment Shader
        vertex_src = """
        #version 330
        in vec2 position;
        void main() {
            gl_Position = vec4(position, 0.0, 1.0);
        }
        """

        # Fragment Shader: Creates the Holographic Color Animation
        fragment_src = """
        #version 330
        uniform float time;
        out vec4 fragColor;

        void main() {
            // Normalize Coordinates (0 to 1)
            vec2 uv = gl_FragCoord.xy / vec2(800.0, 600.0);

            // Holographic Glow: sin wave animation
            float glow = 0.5 + 0.5 * sin(time + uv.y * 10.0);

            // RGB Color with Transparency
            fragColor = vec4(uv.x * glow * 2.0, uv.y * glow * 2.0, glow * 2.0, 0.5);    
        }
        """

        # Compile and Link Shader Program
        self.shader_program = QOpenGLShaderProgram()
        self.shader_program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Vertex, vertex_src)
        self.shader_program.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment, fragment_src)
        self.shader_program.link()

    
    def resizeGL(self, w, h):
        # Make Sure OpenGL Viewport Matches Widget Size
        GL.glViewport(0, 0, w, h)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)

        parent = self.parent()
        if not parent:
            return
        
        status_height = 0

        self.setGeometry(
            0,
            0,
            parent.width(),
            parent.height() - status_height
        )

    def paintGL(self):
        # Clear the Buffer for Drawing
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Prevent Crashing
        if not self.shader_program:
            return

        # Bind Shader 
        self.shader_program.bind()
        self.shader_program.setUniformValue("time", self.time)

         # Draw full-screen quad using modern OpenGL functions
        # For simplicity, we can keep a vertex array approach
        GL.glBegin(GL.GL_TRIANGLES)

        GL.glVertex2f(-1.0, -1.0)
        GL.glVertex2f( 1.0, -1.0)
        GL.glVertex2f( 1.0,  1.0)

        GL.glVertex2f(-1.0, -1.0)
        GL.glVertex2f( 1.0,  1.0)
        GL.glVertex2f(-1.0,  1.0)

        GL.glEnd()
        
        # Release Shader Program
        self.shader_program.release()

    def update_frame(self):
        # Increment Time to Animate Shader
        self.time += 0.05
        # Redraw the Overlay
        self.update()

