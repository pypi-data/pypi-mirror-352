#!/usr/bin/env python3
# drag_drop_clip.py

import sys
import os
from PyQt5 import QtCore, QtWidgets
#from abstract_utilities.robust_reader import read_file_as_text

import os
import fnmatch
from typing import List, Union

# Folders and filename‐patterns to skip
DEFAULT_EXCLUDE_DIRS = {"node_modules", "__pycache__"}
DEFAULT_EXCLUDE_FILE_PATTERNS = {"*.ini"}



class DragDropWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag-Drop → Clipboard")
        self.resize(500, 300)
        # Enable native drag-and-drop of file URLs
        self.setAcceptDrops(True)

        layout = QtWidgets.QVBoxLayout(self)

        # Instruction label
        self.info = QtWidgets.QLabel(
            "Drag one or more supported files here,\nor click “Browse…”",
            self
        )
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        self.info.setStyleSheet("font-size: 14px; color: #555;")
        layout.addWidget(self.info, stretch=1)

        # “Browse…” button
        browse_btn = QtWidgets.QPushButton("Browse Files…", self)
        browse_btn.clicked.connect(self.browse_files)
        layout.addWidget(browse_btn, alignment=QtCore.Qt.AlignHCenter)

        # Status label
        self.status = QtWidgets.QLabel("No files selected.", self)
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        self.status.setStyleSheet("color: #333; font-size: 12px;")
        layout.addWidget(self.status, stretch=1)

    def dragEnterEvent(self, event):
        # Accept the drop if it contains at least one local file URL
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        from abstract_utilities.robust_reader import collect_filepaths
        # Called when the user drops files onto the widget
        paths = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile()
        ]
        if paths:
            DEFAULT_EXCLUDE_DIRS = {"node_modules", "__pycache__"}
            DEFAULT_EXCLUDE_FILE_PATTERNS = {"*.ini", "*.tmp", "*.log"}
            paths = collect_filepaths(paths,
                                      exclude_dirs=DEFAULT_EXCLUDE_DIRS,
                                      exclude_file_patterns=DEFAULT_EXCLUDE_FILE_PATTERNS)
            self.process_files(paths)

    def browse_files(self):
        # Fallback “Browse” dialog (multiple file selection allowed)
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select Files to Copy",
            "",
            "All Supported Files (*.txt *.md *.csv *.tsv *.log "
            "*.xls *.xlsx *.ods *.parquet *.geojson *.shp);;All Files (*)"
        )
        if files:
            self.process_files(files)

    def process_files(self, file_paths: list[str]):
        # Filter out invalid or non‐existent paths
        valid_paths = [p for p in file_paths if os.path.isfile(p) or os.path.isdir(p)]
        if not valid_paths:
            self.status.setText("⚠️ No valid files detected.")
            return

        self.status.setText(f"Reading {len(valid_paths)} file(s)…")
        QtWidgets.QApplication.processEvents()

        combined_text = []
        for idx, path in enumerate(valid_paths):
            filename = os.path.basename(path)
            combined_text.append(f"=== {path} ===\n")
            try:
                from abstract_utilities.robust_reader import read_file_as_text
                content_str = read_file_as_text(path)
                combined_text.append(content_str)
            except Exception as e:
                combined_text.append(f"[Error reading {filename}: {e}]\n")

            if idx < len(valid_paths) - 1:
                combined_text.append("\n\n――――――――――――――――――\n\n")

        final_output = "".join(combined_text)

        # Copy to system clipboard using Qt’s QClipboard
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(final_output, mode=clipboard.Clipboard)

        self.status.setText(f"✅ Copied {len(valid_paths)} file(s) to clipboard!")

def gui_main():
    app = QtWidgets.QApplication(sys.argv)
    window = DragDropWidget()
    window.show()
    sys.exit(app.exec_())


