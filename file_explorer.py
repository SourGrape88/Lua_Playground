# ---------------- FILE_EXPLORER.PY ---------------
from PyQt6.QtWidgets import QTreeView
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QDir

class FileExplorer(QTreeView):
    def __init__(self):
        super().__init__()

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath()) # Start at the Current Directory
        #self.file_model.setNameFilters(["*.lua"]) # Only Show Lua Files
        self.file_model.setNameFilterDisables(False) # Hide Non-Matching Files

        self.setModel(self.file_model) # Link model to Tree View
        self.setRootIndex(self.file_model.index(QDir.currentPath())) # Root = Project Folder
        #self.file_explorer.doubleClicked.connect(self.open_file_from_explorer) # When Double Clicked, Run "open_file_from_explorer"
        self.setHeaderHidden(False) # Hides Size/type Columns
        self.header().setStretchLastSection(True) # Column Stretches with the Tree
        self.header().setSectionResizeMode(0,
            self.header().ResizeMode.Interactive) # Allow Manual Resize
        self.setColumnWidth(0, 200) # Default Width
        self.setMinimumWidth(50) # Makes File Exp Small
        self.setAnimated(True)
        self.setIndentation(15)
        self.setSortingEnabled(True)
    
    def filepath_from_index(self, index):
        return self.file_model.filePath(index)
