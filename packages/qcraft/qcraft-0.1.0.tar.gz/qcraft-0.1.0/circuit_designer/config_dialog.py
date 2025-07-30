from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit, QPushButton, QLabel, QSplitter, QGroupBox, QFormLayout, QLineEdit, QMessageBox
from PySide6.QtCore import Qt
import yaml
from .workflow_bridge import QuantumWorkflowBridge

class ConfigDialog(QDialog):
    def __init__(self, parent=None, bridge=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Editor")
        self.resize(900, 700)
        self.bridge = bridge or QuantumWorkflowBridge()
        self._current_config_module = None
        self._setup_ui()
        self._populate_config_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        # Config list
        left_panel = QVBoxLayout()
        self.file_list = QListWidget()
        self.file_list.currentItemChanged.connect(self._on_file_selected)
        left_panel.addWidget(QLabel("Configuration Files"))
        left_panel.addWidget(self.file_list)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._populate_config_list)
        left_panel.addWidget(refresh_btn)
        left_widget = QGroupBox()
        left_widget.setLayout(left_panel)
        splitter.addWidget(left_widget)
        # Editor and schema
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Editor"))
        self.editor = QTextEdit()
        right_panel.addWidget(self.editor)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_current_file)
        self.save_button.setEnabled(False)
        right_panel.addWidget(self.save_button)
        right_panel.addWidget(QLabel("Schema"))
        self.schema_viewer = QTextEdit()
        self.schema_viewer.setReadOnly(True)
        right_panel.addWidget(self.schema_viewer)
        # API key management
        api_group = QGroupBox("Provider API Keys")
        api_layout = QFormLayout(api_group)
        self.api_key_fields = {}
        providers = set()
        for module in self.bridge.list_configs():
            if 'devices' in module or module in ['ibm_devices', 'ionq_devices', 'hardware']:
                providers.add(module.split('_')[0])
        for provider in sorted(providers):
            field = QLineEdit()
            field.setText(self.bridge.get_api_key(provider) or "")
            self.api_key_fields[provider] = field
            save_btn = QPushButton("Save")
            save_btn.clicked.connect(lambda _, p=provider, f=field: self._save_api_key(p, f))
            api_layout.addRow(f"{provider} API Key:", field)
            api_layout.addRow("", save_btn)
        right_panel.addWidget(api_group)
        right_widget = QGroupBox()
        right_widget.setLayout(right_panel)
        splitter.addWidget(right_widget)
        layout.addWidget(splitter)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _populate_config_list(self):
        self.file_list.clear()
        modules = self.bridge.list_configs()
        for module in modules:
            self.file_list.addItem(module)

    def _on_file_selected(self, current, previous):
        if not current:
            return
        module = current.text()
        try:
            config = self.bridge.get_config(module)
            config_text = yaml.safe_dump(config, sort_keys=False, allow_unicode=True)
        except Exception as e:
            config_text = f"Error loading config: {e}"
        try:
            schema = self.bridge.get_schema(module)
            schema_text = yaml.safe_dump(schema, sort_keys=False, allow_unicode=True)
        except Exception as e:
            schema_text = f"Schema not found: {e}"
        self.editor.setPlainText(config_text)
        self.schema_viewer.setPlainText(schema_text)
        self._current_config_module = module
        self.save_button.setEnabled(True)

    def _save_current_file(self):
        if not self._current_config_module:
            return
        try:
            content = self.editor.toPlainText()
            config = yaml.safe_load(content)
            self.bridge.save_config(self._current_config_module, config)
            QMessageBox.information(self, "Success", "Configuration saved successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving file: {str(e)}")

    def _save_api_key(self, provider, field):
        key = field.text().strip()
        self.bridge.set_api_key(provider, key)
        QMessageBox.information(self, "API Key Saved", f"API key for {provider} saved.") 