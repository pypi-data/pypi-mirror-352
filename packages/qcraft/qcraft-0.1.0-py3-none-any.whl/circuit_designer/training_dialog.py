from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QGroupBox, QFormLayout, QComboBox, QDoubleSpinBox, QSpinBox, QPushButton, QLabel, QProgressBar, QTextEdit, QMessageBox
from PySide6.QtCore import QTimer
from .workflow_bridge import QuantumWorkflowBridge

class TrainingDialog(QDialog):
    def __init__(self, parent=None, bridge=None):
        super().__init__(parent)
        self.bridge = bridge or QuantumWorkflowBridge()
        self.selected_module = 'surface_code'
        self.training_in_progress = False
        self.current_episode = 0
        self.total_episodes = 1000
        self.current_reward = None
        self.current_ler = None
        self.reward_history = []
        self.episode_history = []
        self._setup_ui()
        self._initialize_agent_config()
        self._update_ui_for_agent_type()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        self._setup_configuration_tab()
        self._setup_training_tab()
        self._setup_results_tab()
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Training")
        self.start_button.clicked.connect(self._on_start_training)
        button_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop Training")
        self.stop_button.clicked.connect(self._on_stop_training)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        main_layout.addLayout(button_layout)
        self._populate_device_list()

    def _setup_configuration_tab(self):
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        module_group = QGroupBox("Module to Train")
        module_layout = QVBoxLayout(module_group)
        self.module_combo = QComboBox()
        self.module_combo.addItems([
            "Surface Code Generator",
            "Circuit Optimizer"
        ])
        self.module_combo.currentIndexChanged.connect(self._on_module_changed)
        module_layout.addWidget(self.module_combo)
        config_layout.addWidget(module_group)
        self.dynamic_config_area = QVBoxLayout()
        config_layout.addLayout(self.dynamic_config_area)
        self._populate_dynamic_config_fields('surface_code')
        config_layout.addStretch()
        self.tab_widget.addTab(config_tab, "Configuration")

    def _on_module_changed(self, idx):
        modules = ['surface_code', 'optimizer']
        self.selected_module = modules[idx]
        for i in reversed(range(self.dynamic_config_area.count())):
            widget = self.dynamic_config_area.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self._populate_dynamic_config_fields(self.selected_module)
        self._update_ui_for_agent_type()

    def _populate_dynamic_config_fields(self, module):
        if module == 'surface_code':
            self._add_surface_code_fields()
        elif module == 'optimizer':
            self._add_optimizer_fields()

    def _add_surface_code_fields(self):
        # Provider selection
        self.provider_label = QLabel("Provider:")
        self.provider_combo = QComboBox()
        # Dynamically get providers from config registry
        providers = []
        for module in self.bridge.list_configs():
            if module.endswith('_devices'):
                providers.append(module.split('_')[0])
        if not providers:
            providers = ['ibm']
        self.provider_combo.addItems(sorted(set(providers)))
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        self.dynamic_config_area.addWidget(self.provider_label)
        self.dynamic_config_area.addWidget(self.provider_combo)
        # Device selection (populated by provider)
        self.device_label = QLabel("Device:")
        self.device_combo = QComboBox()
        self.dynamic_config_area.addWidget(self.device_label)
        self.dynamic_config_area.addWidget(self.device_combo)
        # Layout type
        self.layout_label = QLabel("Layout Type:")
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(['planar', 'rotated'])
        self.dynamic_config_area.addWidget(self.layout_label)
        self.dynamic_config_area.addWidget(self.layout_combo)
        # Code distance
        self.distance_label = QLabel("Code Distance:")
        self.distance_spin = QSpinBox()
        self.distance_spin.setRange(3, 15)
        self.distance_spin.setSingleStep(2)
        self.distance_spin.setValue(5)
        self.dynamic_config_area.addWidget(self.distance_label)
        self.dynamic_config_area.addWidget(self.distance_spin)
        # Learning rate
        self.lr_label = QLabel("Learning Rate:")
        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setRange(0.0001, 0.1)
        self.lr_spin.setSingleStep(0.001)
        self.lr_spin.setValue(0.001)
        self.lr_spin.setDecimals(4)
        self.dynamic_config_area.addWidget(self.lr_label)
        self.dynamic_config_area.addWidget(self.lr_spin)
        # Episodes
        self.episodes_label = QLabel("Episodes:")
        self.episodes_spin = QSpinBox()
        self.episodes_spin.setRange(100, 10000)
        self.episodes_spin.setSingleStep(100)
        self.episodes_spin.setValue(1000)
        self.dynamic_config_area.addWidget(self.episodes_label)
        self.dynamic_config_area.addWidget(self.episodes_spin)
        # Do NOT call self._populate_device_list() here

    def _add_optimizer_fields(self):
        self.optimizer_provider_label = QLabel("Provider:")
        self.optimizer_provider_combo = QComboBox()
        providers = []
        for module in self.bridge.list_configs():
            if module.endswith('_devices'):
                providers.append(module.split('_')[0])
        if not providers:
            providers = ['ibm']
        self.optimizer_provider_combo.addItems(sorted(set(providers)))
        self.optimizer_provider_combo.currentIndexChanged.connect(self._on_optimizer_provider_changed)
        self.dynamic_config_area.addWidget(self.optimizer_provider_label)
        self.dynamic_config_area.addWidget(self.optimizer_provider_combo)
        self.optimizer_device_label = QLabel("Device:")
        self.optimizer_device_combo = QComboBox()
        self.dynamic_config_area.addWidget(self.optimizer_device_label)
        self.dynamic_config_area.addWidget(self.optimizer_device_combo)
        self.optimizer_lr_label = QLabel("Learning Rate:")
        self.optimizer_lr_spin = QDoubleSpinBox()
        self.optimizer_lr_spin.setRange(0.0001, 0.1)
        self.optimizer_lr_spin.setSingleStep(0.001)
        self.optimizer_lr_spin.setValue(0.001)
        self.optimizer_lr_spin.setDecimals(4)
        self.dynamic_config_area.addWidget(self.optimizer_lr_label)
        self.dynamic_config_area.addWidget(self.optimizer_lr_spin)
        self.optimizer_episodes_label = QLabel("Episodes:")
        self.optimizer_episodes_spin = QSpinBox()
        self.optimizer_episodes_spin.setRange(100, 10000)
        self.optimizer_episodes_spin.setSingleStep(100)
        self.optimizer_episodes_spin.setValue(1000)
        self.dynamic_config_area.addWidget(self.optimizer_episodes_label)
        self.dynamic_config_area.addWidget(self.optimizer_episodes_spin)
        self._populate_optimizer_device_list()

    def _setup_training_tab(self):
        training_tab = QWidget()
        training_layout = QVBoxLayout(training_tab)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        training_layout.addWidget(self.progress_bar)
        self.status_label = QLabel("Ready")
        training_layout.addWidget(self.status_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        training_layout.addWidget(self.log_text)
        self.tab_widget.addTab(training_tab, "Training")

    def _setup_results_tab(self):
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        self.final_reward_label = QLabel("Final Reward: N/A")
        results_layout.addWidget(self.final_reward_label)
        self.final_avg_reward_label = QLabel("Average Reward: N/A")
        results_layout.addWidget(self.final_avg_reward_label)
        self.training_time_label = QLabel("Training Time: N/A")
        results_layout.addWidget(self.training_time_label)
        self.tab_widget.addTab(results_tab, "Results")

    def _initialize_agent_config(self):
        if self.selected_module == 'surface_code':
            self.module_combo.setCurrentIndex(0)
        elif self.selected_module == 'optimizer':
            self.module_combo.setCurrentIndex(1)

    def _update_ui_for_agent_type(self):
        if self.selected_module == 'surface_code':
            self.setWindowTitle("Surface Code Generator Training")
        elif self.selected_module == 'optimizer':
            self.setWindowTitle("Circuit Optimizer Training")
        self._add_log_message(f"Selected agent type: {self.selected_module}")

    def _on_start_training(self):
        self.training_in_progress = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.tab_widget.setCurrentIndex(1)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.reward_history = []
        self.episode_history = []
        self.current_reward = None
        self.current_ler = None
        self._add_log_message("Training started...")

        def gui_log_callback(message, progress):
            self._add_log_message(message)
            if progress is not None:
                self.progress_bar.setValue(int(progress * 100))
            # Parse reward and LER if present in message
            if "Reward:" in message:
                try:
                    parts = message.split(",")
                    for part in parts:
                        if "Reward:" in part:
                            self.current_reward = float(part.split("Reward:")[1].strip())
                        if "LER:" in part or "Logical Error Rate" in part:
                            self.current_ler = float(part.split(":")[-1].strip())
                    if self.current_reward is not None:
                        self.reward_history.append(self.current_reward)
                except Exception:
                    pass

        # Start backend training with callback
        if self.selected_module == 'surface_code':
            provider = self.provider_combo.currentText().lower()
            device = self.device_combo.currentText()
            layout_type = self.layout_combo.currentText()
            code_distance = self.distance_spin.value()
            learning_rate = self.lr_spin.value()
            episodes = self.episodes_spin.value()
            self.bridge.update_config('hardware', {'provider_name': provider, 'device_name': device})
            self.bridge.update_config('surface_code', {
                'surface_code': {
                    'code_distance': code_distance,
                    'layout_type': layout_type
                },
                'rl_agent': {
                    'learning_rate': learning_rate,
                    'num_episodes': episodes
                }
            })
            config_overrides = {'rl_agent': {'learning_rate': learning_rate, 'num_episodes': episodes}}
            result = self.bridge.train_surface_code_agent(
                provider, device, layout_type, code_distance, config_overrides, log_callback=gui_log_callback)
            agent_path = result['policy_path']
            run_id = result['run_id']
            self._add_log_message(f"Run ID: {run_id}")
            self.training_status = self.bridge.get_surface_code_training_status(agent_path)
        elif self.selected_module == 'optimizer':
            provider = self.optimizer_provider_combo.currentText().lower()
            device = self.optimizer_device_combo.currentText()
            learning_rate = self.optimizer_lr_spin.value()
            episodes = self.optimizer_episodes_spin.value()
            self.bridge.update_config('hardware', {'provider_name': provider, 'device_name': device})
            self.bridge.update_config('optimization', {
                'rl_config': {
                    'learning_rate': learning_rate,
                    'num_episodes': episodes
                }
            })
            config_overrides = {'rl_agent': {'learning_rate': learning_rate, 'num_episodes': episodes}}
            try:
                agent_path = self.bridge.train_optimizer_agent({}, {'name': device}, config_overrides)
                self.training_status = self.bridge.get_optimizer_training_status(agent_path)
            except NotImplementedError:
                QMessageBox.information(self, "Not Implemented", "Optimizer training is not implemented yet.")
                self.training_in_progress = False
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                return
        self.training_in_progress = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        # Show results only if real data is available
        if self.reward_history:
            self.final_reward_label.setText(f"Final Reward: {self.reward_history[-1]}")
            avg_reward = sum(self.reward_history) / len(self.reward_history)
            self.final_avg_reward_label.setText(f"Average Reward: {avg_reward:.2f}")
        else:
            self.final_reward_label.setText("Final Reward: N/A")
            self.final_avg_reward_label.setText("Average Reward: N/A")
        self.training_time_label.setText(f"Training Time: {len(self.reward_history)} episodes")
        self.tab_widget.setCurrentIndex(2)
        QMessageBox.information(self, "Training Complete", "Training has completed successfully.")

    def _on_stop_training(self):
        if not self.training_in_progress:
            return
        self.training_in_progress = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self._add_log_message("Training stopped by user.")

    def _add_log_message(self, message):
        self.log_text.append(message)

    def _on_provider_changed(self, idx=None):
        self._populate_device_list()

    def _populate_device_list(self):
        provider = self.provider_combo.currentText().lower() if hasattr(self, 'provider_combo') else 'ibm'
        devices = self.bridge.list_devices(provider)
        print(f"[DEBUG] Devices for provider '{provider}': {devices}")
        self.device_combo.clear()
        if devices:
            self.device_combo.addItems(devices)
            self.start_button.setEnabled(True)
            self.device_combo.setToolTip("")
        else:
            self.device_combo.addItem("No devices found")
            self.start_button.setEnabled(False)
            self.device_combo.setToolTip("No devices found for this provider. Check your config files.")

    def _on_optimizer_provider_changed(self, idx=None):
        self._populate_optimizer_device_list()

    def _populate_optimizer_device_list(self):
        provider = self.optimizer_provider_combo.currentText().lower() if hasattr(self, 'optimizer_provider_combo') else 'ibm'
        devices = self.bridge.list_devices(provider)
        print(f"[DEBUG] Optimizer devices for provider '{provider}': {devices}")
        self.optimizer_device_combo.clear()
        if devices:
            self.optimizer_device_combo.addItems(devices)
            self.start_button.setEnabled(True)
            self.optimizer_device_combo.setToolTip("")
        else:
            self.optimizer_device_combo.addItem("No devices found")
            self.start_button.setEnabled(False)
            self.optimizer_device_combo.setToolTip("No devices found for this provider. Check your config files.") 