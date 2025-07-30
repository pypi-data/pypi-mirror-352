import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QProgressBar, QLabel, QMessageBox, QDialog
from PySide6.QtCore import QThread, Signal, QObject
from .circuit_editor import CircuitEditor
from .gate_palette import GatePalette
from .circuit_canvas import CircuitCanvas
from .config_dialog import ConfigDialog
from .training_dialog import TrainingDialog
from .workflow_bridge import QuantumWorkflowBridge
import os
import json

def get_provider_and_device(config_dir):
    hardware_json_path = os.path.join(config_dir, 'hardware.json')
    with open(hardware_json_path, 'r') as f:
        hw = json.load(f)
    return hw['provider_name'], hw['device_name']

class WorkflowWorker(QObject):
    progress = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, circuit_editor, device_info, layout_type, code_distance, backend_name, run_config=None, config_overrides=None, provider=None):
        super().__init__()
        self.circuit_editor = circuit_editor
        self.device_info = device_info
        self.layout_type = layout_type
        self.code_distance = code_distance
        self.backend_name = backend_name
        self.run_config = run_config
        self.config_overrides = config_overrides or {}
        self._is_cancelled = False
        self.provider = provider

    def cancel(self):
        self._is_cancelled = True

    def _progress_callback(self, message, percent):
        self.progress.emit(message)

    def run(self):
        try:
            self.progress.emit("Optimizing circuit...")
            if self._is_cancelled: return
            optimized = self.circuit_editor.optimize_circuit_backend(self.device_info, self.config_overrides, progress_callback=self._progress_callback)
            self.circuit_editor.circuit = optimized
            self.circuit_editor._notify_change()

            self.progress.emit("Generating surface code layout...")
            if self._is_cancelled: return
            layout = self.circuit_editor.generate_surface_code_layout_backend(
                self.layout_type, self.code_distance, self.device_info['name'], self.config_overrides, progress_callback=self._progress_callback
            )

            # Query supported logical gates from surface code API
            supported_gates = self.circuit_editor.workflow_bridge.surface_code_api.list_supported_logical_gates(
                self.layout_type, self.code_distance
            )
            # Filter out SWAP to ensure code switcher is triggered for SWAP
            supported_gates = [g for g in supported_gates if g != 'SWAP']

            self.progress.emit("Analyzing for code switching...")
            if self._is_cancelled: return
            code_info = {"supported_gates": supported_gates}
            switching_points = self.circuit_editor.identify_switching_points_backend(code_info)
            protocols = []
            if switching_points:
                for sp in switching_points:
                    proto = self.circuit_editor.select_switching_protocol_backend(
                        sp['gate'], ["magic_state_injection", "lattice_surgery"]
                    )
                    protocols.append({"name": proto})
                self.progress.emit("Applying code switching...")
                if self._is_cancelled: return
                self.circuit_editor.circuit = self.circuit_editor.apply_code_switching_backend(
                    switching_points, protocols, self.device_info
                )
                self.circuit_editor._notify_change()

            self.progress.emit("Mapping circuit to surface code...")
            if self._is_cancelled: return
            mapping_result = self.circuit_editor.map_circuit_to_surface_code_backend(
                self.device_info['name'], self.layout_type, self.code_distance, self.device_info.get('provider'), self.config_overrides, progress_callback=self._progress_callback
            )
            mapping_info = mapping_result.get('mapping_info', {})

            self.progress.emit("Transforming to fault-tolerant circuit...")
            if self._is_cancelled: return
            code_spaces = []
            ft_circuit = self.circuit_editor.assemble_fault_tolerant_circuit_backend(
                mapping_info, code_spaces, self.device_info
            )
            self.circuit_editor.circuit = ft_circuit
            self.circuit_editor._notify_change()

            self.progress.emit("Executing on hardware...")
            if self._is_cancelled: return
            job_id = self.circuit_editor.run_circuit_backend(self.backend_name, self.run_config)
            self.finished.emit(job_id)
        except Exception as e:
            self.error.emit(str(e))

class CircuitDesignerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graphical Circuit Designer")
        self.resize(1200, 700)
        self.editor = CircuitEditor()
        self.workflow_bridge = QuantumWorkflowBridge()
        self.config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../configs'))
        self.provider, self.device = get_provider_and_device(self.config_dir)
        self._init_ui()
        self._workflow_thread = None
        self._workflow_worker = None

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        h_layout = QHBoxLayout()
        # Left: Gate palette
        self.palette = GatePalette()
        h_layout.addWidget(self.palette, 0)
        # Center: Circuit canvas
        self.canvas = CircuitCanvas(self.editor)
        h_layout.addWidget(self.canvas, 1)
        main_layout.addLayout(h_layout, 1)
        # Workflow controls
        controls = QHBoxLayout()
        self.run_workflow_btn = QPushButton("Run Full Workflow")
        self.cancel_workflow_btn = QPushButton("Cancel")
        self.cancel_workflow_btn.setEnabled(False)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.status_label = QLabel("Ready")
        # Add config and training buttons
        self.config_btn = QPushButton("Edit Configs")
        self.training_btn = QPushButton("Train Module")
        controls.addWidget(self.run_workflow_btn)
        controls.addWidget(self.cancel_workflow_btn)
        controls.addWidget(self.progress_bar)
        controls.addWidget(self.status_label)
        controls.addWidget(self.config_btn)
        controls.addWidget(self.training_btn)
        main_layout.addLayout(controls)
        # Connect
        self.run_workflow_btn.clicked.connect(self.start_full_workflow)
        self.cancel_workflow_btn.clicked.connect(self.cancel_full_workflow)
        self.config_btn.clicked.connect(self.open_config_dialog)
        self.training_btn.clicked.connect(self.open_training_dialog)

    def start_full_workflow(self):
        # Always use provider/device from hardware.json
        self.provider, self.device = get_provider_and_device(self.config_dir)
        device_info = {'name': self.device, 'provider': self.provider}  # Include provider
        layout_type = 'rotated'  # You may want to load this from config or UI
        code_distance = 5        # You may want to load this from config or UI
        backend_name = self.device
        run_config = {'shots': 1024}
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting workflow...")
        self.run_workflow_btn.setEnabled(False)
        self.cancel_workflow_btn.setEnabled(True)
        self._workflow_thread = QThread()
        self._workflow_worker = WorkflowWorker(
            self.editor, device_info, layout_type, code_distance, backend_name, run_config, provider=self.provider
        )
        self._workflow_worker.moveToThread(self._workflow_thread)
        self._workflow_thread.started.connect(self._workflow_worker.run)
        self._workflow_worker.progress.connect(self.on_workflow_progress)
        self._workflow_worker.finished.connect(self.on_workflow_finished)
        self._workflow_worker.error.connect(self.on_workflow_error)
        self._workflow_thread.start()

    def cancel_full_workflow(self):
        if self._workflow_worker:
            self._workflow_worker.cancel()
        self.status_label.setText("Workflow cancelled.")
        self.run_workflow_btn.setEnabled(True)
        self.cancel_workflow_btn.setEnabled(False)

    def on_workflow_progress(self, message):
        self.status_label.setText(message)
        step_map = {
            "Optimizing circuit...": 10,
            "Analyzing for code switching...": 30,
            "Applying code switching...": 40,
            "Generating surface code layout...": 60,
            "Transforming to fault-tolerant circuit...": 80,
            "Executing on hardware...": 90,
        }
        self.progress_bar.setValue(step_map.get(message, 0))

    def on_workflow_finished(self, job_id):
        self.status_label.setText(f"Workflow complete. Job ID: {job_id}")
        self.progress_bar.setValue(100)
        self.run_workflow_btn.setEnabled(True)
        self.cancel_workflow_btn.setEnabled(False)
        self._workflow_thread.quit()
        self._workflow_thread.wait()

    def on_workflow_error(self, error_msg):
        QMessageBox.critical(self, "Workflow Error", error_msg)
        self.status_label.setText("Error occurred.")
        self.run_workflow_btn.setEnabled(True)
        self.cancel_workflow_btn.setEnabled(False)
        self._workflow_thread.quit()
        self._workflow_thread.wait()

    def open_config_dialog(self):
        dlg = ConfigDialog(self, bridge=self.workflow_bridge)
        dlg.setWindowTitle("Configuration Editor")
        dlg.exec()

    def open_training_dialog(self):
        dlg = TrainingDialog(self, bridge=self.workflow_bridge)
        dlg.setWindowTitle("Train Module")
        dlg.exec()

def main():
    import sys
    app = QApplication(sys.argv)
    window = CircuitDesignerGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 