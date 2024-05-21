import time

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtCore import Qt

from ui import SerManUi
from utils import service_manager


class UpdateThread(QThread):
    def __init__(self, service_manager: service_manager.ServiceManagerProtocol, parent=None):
        QThread.__init__(self, parent)
        self.service_manager = service_manager
        self.parent = parent

    def run(self):
        # Iterate over all rows in the table
        for row in range(self.parent.table.rowCount()):
            service_name = self.parent.table.item(row, 0).text()
            service_status = self.service_manager.get_service_status(service_name)
            service_pid = self.service_manager.get_service_pid(service_name)
            self.parent.update_row(service_name, service_status, service_pid)


class ServiceThread(QThread):
    update_signal = pyqtSignal(str, str, str)  # Add arguments to the signal

    def __init__(
        self,
        service_manager: service_manager.ServiceManagerProtocol,
        service_name,
        operation,
        parent=None,
    ):
        QThread.__init__(self, parent)
        self.service_manager = service_manager
        self.service_name = service_name
        self.operation = operation
        self.parent = parent

    def run(self):
        # Disable row selection in the table
        self.parent.disable_row(self.service_name)
        if self.operation == "start":
            self.service_manager.start_service(self.service_name)
        elif self.operation == "stop":
            self.service_manager.stop_service(self.service_name)
        elif self.operation == "restart":
            self.service_manager.restart_service(self.service_name)

        # Get the current status and PID of the service
        service_status = self.service_manager.get_service_status(self.service_name)
        service_pid = self.service_manager.get_service_pid(self.service_name)
        self.update_signal.emit(
            self.service_name, service_status, service_pid
        )  # Emit the signal with the status and PID


class ServiceManager(SerManUi):
    def __init__(self, service_manager: service_manager.ServiceManagerProtocol):
        super().__init__(service_manager)
        self.threads = []  # Add this line to create a list to store the threads

        self.startButton.clicked.connect(self.start_service)
        self.stopButton.clicked.connect(self.stop_service)
        self.restartButton.clicked.connect(self.restart_service)
        self.refreshButton.clicked.connect(self.update_table_thread)

    def start_service(self):
        print("Start service ...")
        self.manage_service("start")

    def stop_service(self):
        print("Stop service ...")
        self.manage_service("stop")

    def restart_service(self):
        print("Restart service ...")
        self.manage_service("restart")

    def disable_row(self, service_name):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == service_name:
                for column in range(self.table.columnCount()):
                    self.table.item(row, column).setFlags(Qt.NoItemFlags)

    def enable_row(self, service_name):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == service_name:
                for column in range(self.table.columnCount()):
                    self.table.item(row, column).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def manage_service(self, operation):
        selected_rows = self.table.selectionModel().selectedRows()
        for row in selected_rows:
            service_name = self.table.item(row.row(), 0).text()
            thread = ServiceThread(self.service_manager, service_name, operation, parent=self)
            thread.finished.connect(thread.deleteLater)
            thread.update_signal.connect(self.update_row)
            thread.start()
            self.threads.append(thread)

    def update_table_thread(self):
        thread = UpdateThread(self.service_manager, parent=self)
        thread.start()
        self.threads.append(thread)

    @pyqtSlot(str, str, str)  # Add this line to create a new slot
    def update_row(self, service_name, service_status, service_pid):
        # Find the row with the given service name
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == service_name:
                # Update the status and PID in the table
                self.table.item(row, 1).setText(service_status)
                self.table.item(row, 2).setText(service_pid)
                break
        # Re-enable the items in the row
        self.enable_row(service_name)
