def apply_style(app):
    app.setStyleSheet("""
    QMainWindow {
        background-color: #D35353;
    }
    
    QsciScintilla {
        background-color: #0A24F5;
                          
    }                  
    
    QWidget {
        color: #0B24D5;
        font-family: Consolas;
        font-size: 12pt;
    }
    
    QPlainTextEdit {
        background-color: #234EB3;
        color: #F2BC71;
        border: 1px solid #444; 
        font-size: 14pt;                 
    }
                      
    QPushButton {
        background-color: #EAA300;
        color: white;
        border-radius: 6px;
        padding: 6px;
    }
                      
    QPushButton:hover {
        background-color: #EAA100;                  
    }
                      
    QPushButton:pressed {
        background-color: #888;                  
    }
                      
""")