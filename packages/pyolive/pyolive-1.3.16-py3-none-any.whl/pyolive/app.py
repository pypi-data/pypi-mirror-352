import os
import sys
import signal
import socket
import json
import importlib
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .config import Config
from .adapter import Adapter
from .channel import Channel
from .heartbeat import Heartbeat
from .log import AgentLog, AppLog
from .context import JobContext


class ResourceReloadHandler(FileSystemEventHandler):
    def __init__(self, module_map, logger):
        super().__init__()
        self.module_map = module_map
        self.logger = logger

    def on_modified(self, event):
        if event.is_directory:
            return
        rel_path = os.path.relpath(event.src_path)
        module_name = self.module_map.get(rel_path)
        if module_name:
            try:
                mod = importlib.import_module(module_name)
                importlib.reload(mod)
                self.logger.info(f"main, reloaded module: {module_name}")
            except Exception as e:
                self.logger.error(f"main, reload failed for {module_name}: {e}")


def start_resource_watcher(tasks, logger):
    seen_modules = set()
    module_map = {}
    for task in tasks:
        resource = task.get("resource")
        if not resource:
            continue
        modname = resource.__module__
        if modname in seen_modules:
            continue
        seen_modules.add(modname)
        filepath = modname.replace(".", os.sep) + ".py"
        module_map[filepath] = modname

    if not module_map:
        logger.info("main, no resource modules to watch.")
        return None

    event_handler = ResourceReloadHandler(module_map, logger)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    thread = threading.Thread(target=observer.start, daemon=True)
    thread.start()
    logger.info("main, resource module watcher started.")
    return observer


def develop_mode(infile, param: dict):
    logger = AppLog("worker", devel=True).get_logger()
    channel = Channel(logger, "dps.msm", "worker", devel=True)
    context = JobContext(devel=True)

    logger.info("Developer mode started ...")
    context.set_fileset(infile, devel=True)
    context.set_param(param, devel=True)

    return logger, channel, context


class Athena:
    def __init__(self, **kwargs):
        self.home = Config.ATHENA_HOME
        if self.home is None:
            print("Not found environment variable, ATHENA_HOME")
            sys.exit(0)

        self.worker_name = 'ovd-worker'
        self.namespace = kwargs['namespace']
        self.alias = kwargs['alias']
        self.adapter = None
        self.channel = None
        self.tasks = []
        self._log = AgentLog(self.alias)
        self.agent_logger = self._log.get_logger()
        self.hot_reload = self._get_hot_reload()

    def _get_hot_reload(self):
        config = Config('athena-agent.yaml')
        return config.get_value('worker/reload-on-change')

    def _get_pid_path(self):
        return os.path.join(self.home, 'var/pid')

    def _get_pid_filename(self):
        file = self.worker_name + '+' + self.namespace + '@' + socket.gethostname() + '.pid'
        path = self._get_pid_path()
        return os.path.join(path, file)

    def _create_pid_file(self):
        name = self._get_pid_filename()
        pid = os.getpid()
        with open(name, "w") as f:
            f.write(str(pid))

    def _remove_pid_file(self):
        name = self._get_pid_filename()
        if os.path.exists(name):
            os.remove(name)

    def _callback_signal(self, signum, frame):
        self.channel.stop()
        self.adapter.stop_consume()

    def _callback_subscribe(self, ch, method, properties, body):
        json_str = body.decode()
        self.agent_logger.debug("received message, %s", json_str)
        message = json.loads(json_str)
        app_name = message['action-app']
        regkey = message['regkey']
        _s = regkey.split('@')[0] + '+' + app_name
        app_logger = AppLog(_s).get_logger()

        # worker를 thread로 실행함
        for task in self.tasks:
            if app_name == task['app']:
                ctx = JobContext(message)
                w = Worker(task['resource'], self.channel, self.agent_logger, app_logger, ctx)
                w.start()

    def run(self):
        self.agent_logger.info("------------------------------------------------")
        self.agent_logger.info("main, run %s", self.namespace)

        self.adapter = Adapter(self.agent_logger)
        if not self.adapter.open():
            return

        self._create_pid_file()
        # channel manager start
        self.channel = Channel(self.agent_logger, self.namespace, self.alias)
        self.channel.start()

        # heartbeat timer start
        heartbeat = Heartbeat(self.channel, self.namespace, self.worker_name)
        heartbeat.start()

        # module reloader
        if self.hot_reload:
            self.watcher = start_resource_watcher(self.tasks, self.agent_logger)

        # signal 처리
        signal.signal(signal.SIGTERM, self._callback_signal)
        signal.signal(signal.SIGINT, self._callback_signal)

        # consume manager looping
        self.adapter.start_consume(self.namespace, self._callback_subscribe)

        # end job
        self.agent_logger.info("main, exit")
        print("main, exit")
        self._log.close()
        self.adapter.close()
        heartbeat.stop()
        self._remove_pid_file()
        sys.exit(0)

    def add_resource(self, resource, app_name):
        task = {}
        task['app'] = app_name
        task['resource'] = resource
        self.tasks.append(task)
