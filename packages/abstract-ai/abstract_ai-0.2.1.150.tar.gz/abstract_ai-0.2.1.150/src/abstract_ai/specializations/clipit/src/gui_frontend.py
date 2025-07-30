#!/usr/bin/env python3
# Revised gui_frontend.py

import sys
import os
from PyQt5 import QtCore, QtWidgets, QtGui
from typing import List

# (Adjust this import path to wherever your robust_reader actually lives.)
# Example:
# from abstract_utilities.robust_reader import read_file_as_text, collect_filepaths

DEFAULT_EXCLUDE_DIRS = {"node_modules", "__pycache__"}
DEFAULT_EXCLUDE_FILE_PATTERNS = {"*.ini", "*.tmp", "*.log"}


class FileDropArea(QtWidgets.QWidget):
    """
    Right‐hand pane: “Drag-Drop → Clipboard.”
    Wrap any exceptions in dropEvent so the app won’t shut down if you drop something unsupported.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Drag-Drop → Clipboard")
        self.resize(600, 400)
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

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent):
        """
        Wrap in try/except so that invalid drops don’t crash the entire app.
        """
        try:
            urls = event.mimeData().urls()
            paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
            if not paths:
                raise ValueError("No local files detected.")
            paths = self._filtered_file_list(paths)
            self.process_files(paths)
        except Exception as e:
            # Show the error in the status label instead of crashing
            self.status.setText(f"⚠️ Error: {str(e)}")

    def browse_files(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select Files to Copy",
            "",
            "All Supported Files (*.txt *.md *.csv *.tsv *.log "
            "*.xls *.xlsx *.ods *.parquet *.geojson *.shp);;All Files (*)"
        )
        if files:
            files = self._filtered_file_list(files)
            self.process_files(files)

    def _filtered_file_list(self, raw_paths: List[str]) -> List[str]:
        """
        Recursively collect files under directories (excluding node_modules/__pycache__, etc).
        """
        from abstract_utilities.robust_reader import collect_filepaths
        return collect_filepaths(
            raw_paths,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_file_patterns=DEFAULT_EXCLUDE_FILE_PATTERNS
        )

    def process_files(self, file_paths: List[str]):
        """
        Exactly the same as before: read each file or folder, concatenate,
        copy to clipboard, and update status.
        """
        valid_paths = [p for p in file_paths if os.path.isfile(p) or os.path.isdir(p)]
        if not valid_paths:
            self.status.setText("⚠️ No valid files detected.")
            return

        self.status.setText(f"Reading {len(valid_paths)} file(s)…")
        QtWidgets.QApplication.processEvents()

        combined_parts = []
        for idx, path in enumerate(valid_paths):
            combined_parts.append(f"=== {path} ===\n")
            try:
                from abstract_utilities.robust_reader import read_file_as_text
                content_str = read_file_as_text(path)
                combined_parts.append(content_str)
            except Exception as e:
                combined_parts.append(f"[Error reading {os.path.basename(path)}: {e}]\n")

            if idx < len(valid_paths) - 1:
                combined_parts.append("\n\n――――――――――――――――――\n\n")

        final_output = "".join(combined_parts)

        # Copy to system clipboard
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(final_output, mode=clipboard.Clipboard)

        self.status.setText(f"✅ Copied {len(valid_paths)} file(s) to clipboard!")


class FileSystemTree(QtWidgets.QWidget):
    """
    Left-hand pane: a file-browser plus a “Copy Selected” button.
    Allows multi-selection in the tree, and also supports dragging from the tree
    into the FileDropArea.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)

        # QFileSystemModel backed QTreeView
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(QtCore.QDir.rootPath())

        self.tree = QtWidgets.QTreeView()
        self.tree.setModel(self.model)

        # Hide all columns except “Name” (optional)
        for col in range(1, self.model.columnCount()):
            self.tree.hideColumn(col)

        # Start in the user's home directory
        home_index = self.model.index(QtCore.QDir.homePath())
        self.tree.setRootIndex(home_index)

        # Allow multi‐selection
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # Enable dragging from the tree (so you can drag into the drop zone)
        self.tree.setDragEnabled(True)
        # Optional: if you only want to allow dragging (not dropping) on the tree itself:
        self.tree.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)

        layout.addWidget(self.tree)

        # “Copy Selected” button underneath the tree
        copy_btn = QtWidgets.QPushButton("Copy Selected to Clipboard")
        copy_btn.clicked.connect(self.copy_selected)
        layout.addWidget(copy_btn)

        self.setLayout(layout)

    def copy_selected(self):
        """
        Collect all selected file‐indexes, convert to paths, and emit them
        (caller can connect to this or directly call process_files).
        """
        indexes = self.tree.selectionModel().selectedIndexes()
        # The model holds each row in multiple columns; only pick column 0 to avoid duplicates
        file_paths = set()
        for idx in indexes:
            if idx.column() == 0:  # only take the “Name” column for each selected row
                path = self.model.filePath(idx)
                file_paths.add(path)

        if not file_paths:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select at least one file or folder.")
            return

        # Notify parent by emitting a custom signal, or if parent stored a reference,
        # they can directly call drop_area.process_files(...)
        # For simplicity, we'll directly call the parent’s method if it exists:
        parent = self.parent()
        if parent and hasattr(parent, "on_tree_copy"):
            # Call parent's helper (defined below in DragDropWithBrowser)
            parent.on_tree_copy(list(file_paths))


class DragDropWithBrowser(QtWidgets.QWidget):
    """
    Main window: horizontal splitter with FileSystemTree on left,
    FileDropArea on right. Provides a helper `on_tree_copy()` so the
    tree can hand selected paths over to the drop area.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClipIt - File Browser + Drag/Drop")
        self.resize(900, 500)

        splitter = QtWidgets.QSplitter(self)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        # Left: file browser widget (with its own “Copy Selected” button)
        self.tree_wrapper = FileSystemTree(self)
        splitter.addWidget(self.tree_wrapper)

        # Right: drop area
        self.drop_area = FileDropArea()
        splitter.addWidget(self.drop_area)

        # Make left pane ~1/3, right pane ~2/3
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)

        # Also allow double‐click on a file in the tree to copy that file immediately
        self.tree_wrapper.tree.doubleClicked.connect(self.on_tree_double_click)

    def on_tree_double_click(self, index: QtCore.QModelIndex):
        """
        When a file is double-clicked, send it to drop_area.process_files([...]).
        If it's a folder, still pass it (collect_filepaths will recurse).
        """
        model = self.tree_wrapper.model
        path = model.filePath(index)
        if path:
            self.drop_area.process_files([path])

    def on_tree_copy(self, paths: List[str]):
        """
        Called when the “Copy Selected” button is pressed.
        Simply forward to drop_area.process_files([...]).
        """
        self.drop_area.process_files(paths)


def gui_main():
    app = QtWidgets.QApplication(sys.argv)
    window = DragDropWithBrowser()
    window.show()
    sys.exit(app.exec_())



