from PyQt5.QtWidgets import (
    QTableWidget,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from utils import ServiceManagerProtocol
from utils import resource_path


class SerManUi(QWidget):
    def __init__(self, service_manager: ServiceManagerProtocol):
        super().__init__()
        self.service_manager = service_manager

        self.setWindowTitle("SerMan")
        self.setWindowIcon(
            QIcon(resource_path("assets/window_icon.png"))
        )  # Set icon for main window

        self.resize(500, 400)  # Set initial window size

        self.layout = QVBoxLayout()

        services = service_manager.get_s_number_services()

        self.table = QTableWidget(len(services), 3)  # rows equal to number of services, 2 columns
        self.table.setHorizontalHeaderLabels(["Service", "Status", "PID"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # Select entire row
        self.table.verticalScrollBar().hide()  # Hide vertical scroll bar
        self.table.horizontalHeader().setStretchLastSection(
            True
        )  # Make the last column stretch to fill the table

        for i, (service_name, service_pid, service_status) in enumerate(services):
            name = QTableWidgetItem(service_name)
            name.setFlags(name.flags() & ~Qt.ItemIsEditable)  # Make item read-only
            self.table.setItem(i, 0, name)

            status = QTableWidgetItem(service_status)  # Initial status
            status.setFlags(status.flags() & ~Qt.ItemIsEditable)  # Make item read-only
            self.table.setItem(i, 1, status)  # Update the status in the table

            pid = QTableWidgetItem(service_pid)  # Initial status
            pid.setFlags(pid.flags() & ~Qt.ItemIsEditable)  # Make item read-only
            self.table.setItem(i, 2, pid)  # Add the PID to the table

        self.startButton = QPushButton("Start")
        self.startButton.setIcon(
            QIcon(resource_path("assets/start_icon.png"))
        )  # Set icon for Start button

        self.stopButton = QPushButton("Stop")
        self.stopButton.setIcon(
            QIcon(resource_path("assets/stop_icon.png"))
        )  # Set icon for Stop button

        self.restartButton = QPushButton("Restart")
        self.restartButton.setIcon(
            QIcon(resource_path("assets/restart_icon.png"))
        )  # Set icon for Restart button

        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.setIcon(
            QIcon(resource_path("assets/refresh_icon.png"))
        )  # Set icon for Restart button

        self.searchInput = QLineEdit()
        self.searchInput.textChanged.connect(self.filter_table)

        # Create a horizontal layout for the buttons
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.startButton)
        buttonLayout.addWidget(self.stopButton)
        buttonLayout.addWidget(self.restartButton)

        searchLayout = QHBoxLayout()
        searchLayout.addWidget(self.searchInput)
        searchLayout.addWidget(self.refreshButton)

        self.layout.addLayout(searchLayout)
        self.layout.addWidget(self.table)
        self.layout.addLayout(buttonLayout)

        self.setLayout(self.layout)

    def filter_table(self, text):
        # Iterate over all rows in the table
        for row in range(self.table.rowCount()):
            service_name = self.table.item(row, 0).text()
            # If the service name contains the search text, show the row, otherwise hide it
            self.table.setRowHidden(row, text not in service_name)
