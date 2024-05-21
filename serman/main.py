import sys
from PyQt5.QtWidgets import QApplication

from manager import ServiceManager
from utils import get_services_manager


def main():
    app = QApplication(sys.argv)

    services_manager_class = get_services_manager()

    services_manager = services_manager_class()

    ui = ServiceManager(services_manager)

    ui.show()

    app.exec_()


if __name__ == "__main__":
    main()
