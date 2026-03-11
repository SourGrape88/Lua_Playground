# ------------EDITOR_TABS.PY----------------
from PyQt6.QtWidgets import QTabWidget
from code_editor import CodeEditor

class EditorTabs(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Makes the "X" to Close Tabs
        self.setTabsClosable(True)
        # Remove Tab when "X" is Clicked
        self.tabCloseRequested.connect(self.close_tab)

        # Start with One Tab
        self.new_tab("Main.lua")

    def new_tab(self, filename="Untitled.lua", filepath=None, lsp_client=None, language="lua"):
        editor = CodeEditor()
        editor.setText("print('Hello World')")
        editor.apply_semantic_token(start_pos=6, length=5, token_type="keyword")
        # Test Semantic Color
        editor.apply_semantic_token(start_pos=0, length=5, token_type="class")

        # Store File Path on the editor
        editor.filepath = filepath
        editor.lsp_client = lsp_client 

        index = self.addTab(editor, filename)
        self.setCurrentIndex(index)

    def close_tab(self, index):
        self.removeTab(index)

    def current_editor(self):
        return self.currentWidget()
    
    def current_filepath(self):
        editor = self.current_editor()
        return getattr(editor, "filepath", None)