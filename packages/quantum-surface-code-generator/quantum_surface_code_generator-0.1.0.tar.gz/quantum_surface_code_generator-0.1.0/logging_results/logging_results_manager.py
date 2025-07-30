import os
import yaml
import json
import csv
import sys
import threading
import datetime
from typing import List, Dict, Any, Optional, Callable
from configuration_management.config_manager import ConfigManager

class ConfigLoader:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or 'configs/logging.yaml'
        self.config = self.load_config(self.config_path)

    def load_config(self, path: str) -> dict:
        if path.endswith('.yaml') or path.endswith('.yml'):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        elif path.endswith('.json'):
            with open(path, 'r') as f:
                return json.load(f)
        else:
            raise ValueError("Unsupported config file format.")

    def get_setting(self, key: str, default=None):
        return self.config.get(key, default)

    def reload(self):
        self.config = self.load_config(self.config_path)

class LoggingResultsManager:
    def __init__(self, config_path: str = None):
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.config
        self.log_level = self.config.get('logging', {}).get('level', 'INFO')
        self.log_to_file = self.config.get('logging', {}).get('log_to_file', True)
        self.log_file_path = self.config.get('logging', {}).get('log_file_path', 'logs/app.log')
        self.log_to_stdout = self.config.get('logging', {}).get('log_to_stdout', True)
        self.results_dir = self.config.get('results', {}).get('storage_dir', 'results/')
        self.export_formats = self.config.get('results', {}).get('export_formats', ['json', 'csv', 'yaml'])
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)
        self.metrics: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}  # run_id -> metric_name -> list of {step, value}
        self.runs: Dict[str, Dict[str, Any]] = {}  # run_id -> run info
        self.results: Dict[str, dict] = {}  # run_id -> result dict
        self.lock = threading.Lock()
        self.log_backends: List[Callable[[str], None]] = []
        self.result_backends: List[Callable[[str, dict], None]] = []

    # --- Logging APIs ---
    def log_event(self, event: str, details: dict = None, level: str = 'INFO') -> None:
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'event': event,
            'details': details or {}
        }
        log_line = json.dumps(log_entry)
        if self.log_to_file:
            with open(self.log_file_path, 'a') as f:
                f.write(log_line + '\n')
        if self.log_to_stdout:
            print(log_line, file=sys.stdout)
        for backend in self.log_backends:
            backend(log_line)
        # Track run start/end
        if event == 'run_started':
            run_id = details.get('run_id')
            with self.lock:
                self.runs[run_id] = {'start_time': timestamp, 'status': 'running', 'events': [log_entry]}
        elif event == 'run_ended':
            run_id = details.get('run_id')
            with self.lock:
                if run_id in self.runs:
                    self.runs[run_id]['end_time'] = timestamp
                    self.runs[run_id]['status'] = 'completed'
                    self.runs[run_id]['events'].append(log_entry)
        elif 'run_id' in (details or {}):
            run_id = details['run_id']
            with self.lock:
                if run_id in self.runs:
                    self.runs[run_id]['events'].append(log_entry)

    def log_metric(self, metric_name: str, value: float, step: int = None, run_id: str = None) -> None:
        with self.lock:
            if run_id not in self.metrics:
                self.metrics[run_id] = {}
            if metric_name not in self.metrics[run_id]:
                self.metrics[run_id][metric_name] = []
            self.metrics[run_id][metric_name].append({'step': step, 'value': value, 'timestamp': datetime.datetime.now().isoformat()})

    def get_metrics(self, run_id: str, metric_name: str = None) -> dict:
        with self.lock:
            if run_id not in self.metrics:
                return {}
            if metric_name:
                return {metric_name: self.metrics[run_id].get(metric_name, [])}
            return self.metrics[run_id]

    def list_runs(self) -> List[str]:
        with self.lock:
            return list(self.runs.keys())

    def get_run_summary(self, run_id: str) -> dict:
        with self.lock:
            run = self.runs.get(run_id, {})
            summary = {
                'run_id': run_id,
                'start_time': run.get('start_time'),
                'end_time': run.get('end_time'),
                'status': run.get('status', 'unknown'),
                'key_metrics': {k: v[-1]['value'] if v else None for k, v in self.metrics.get(run_id, {}).items()},
            }
            return summary

    # --- Results APIs ---
    def store_result(self, run_id: str, result: dict) -> None:
        with self.lock:
            self.results[run_id] = result
        for backend in self.result_backends:
            backend(run_id, result)
        # Optionally persist to disk
        result_path = os.path.join(self.results_dir, f'{run_id}.json')
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)

    def get_result(self, run_id: str) -> dict:
        with self.lock:
            if run_id in self.results:
                return self.results[run_id]
        # Try loading from disk
        result_path = os.path.join(self.results_dir, f'{run_id}.json')
        if os.path.exists(result_path):
            with open(result_path, 'r') as f:
                return json.load(f)
        return {}

    def export_log(self, run_id: str, format: str, path: str) -> None:
        # Export metrics, events, and result for the run
        with self.lock:
            run = self.runs.get(run_id, {})
            metrics = self.metrics.get(run_id, {})
            result = self.get_result(run_id)
            events = run.get('events', [])
        if format == 'json':
            with open(path, 'w') as f:
                json.dump({'events': events, 'metrics': metrics, 'result': result}, f, indent=2)
        elif format in ('yaml', 'yml'):
            with open(path, 'w') as f:
                yaml.safe_dump({'events': events, 'metrics': metrics, 'result': result}, f)
        elif format == 'csv':
            # Export metrics as CSV
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['metric', 'step', 'value', 'timestamp'])
                for metric, vals in metrics.items():
                    for v in vals:
                        writer.writerow([metric, v.get('step'), v.get('value'), v.get('timestamp')])
        else:
            raise ValueError(f"Unsupported export format: {format}")

    # --- Extensibility ---
    def register_log_backend(self, backend: Callable[[str], None]):
        self.log_backends.append(backend)

    def register_result_backend(self, backend: Callable[[str, dict], None]):
        self.result_backends.append(backend)

    def reload_config(self):
        self.config_loader.reload()
        self.config = self.config_loader.config
        self.log_level = self.config.get('logging', {}).get('level', 'INFO')
        self.log_to_file = self.config.get('logging', {}).get('log_to_file', True)
        self.log_file_path = self.config.get('logging', {}).get('log_file_path', 'logs/app.log')
        self.log_to_stdout = self.config.get('logging', {}).get('log_to_stdout', True)
        self.results_dir = self.config.get('results', {}).get('storage_dir', 'results/')
        self.export_formats = self.config.get('results', {}).get('export_formats', ['json', 'csv', 'yaml'])
        os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True) 