import platform
import re
from typing import Protocol
import subprocess


class ServiceManagerProtocol(Protocol):
    def get_services(self):
        return NotImplemented

    def get_service_pid(self, service):
        return NotImplemented

    def get_service_status(self, service):
        return NotImplemented

    def get_s_number_services(self):
        return NotImplemented

    def start_service(self, service):
        return NotImplemented

    def stop_service(self, service):
        return NotImplemented

    def restart_service(self, service):
        return NotImplemented

    @staticmethod
    def parse_services():
        return NotImplemented


class LinuxServiceManager:
    def get_services(self):
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--all"],
            capture_output=True,
            text=True,
        )
        return result.stdout

    def get_service_pid(self, service):
        result = subprocess.run(
            ["systemctl", "show", "-p", "MainPID", "--value", service],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def get_service_status(self, service):
        result = subprocess.run(
            ["systemctl", "is-active", service], capture_output=True, text=True
        )
        return result.stdout.strip()

    @staticmethod
    def parse_services(output):
        # This regular expression matches services in the format 'S{number}'
        pattern = re.compile(r"S\d+")
        services = pattern.findall(output)
        return set(services)

    def get_s_number_services(self):
        services = self.get_services()
        s_number_services = self.parse_services(services)
        service_details = []
        for service in s_number_services:
            pid = self.get_service_pid(service)
            status = self.get_service_status(service)
            service_details.append((service, pid, status))
        return service_details

    def start_service(self, service):
        result = subprocess.run(["systemctl", "start", service], capture_output=True, text=True)
        return result.stdout.strip()

    def stop_service(self, service):
        result = subprocess.run(["systemctl", "stop", service], capture_output=True, text=True)
        return result.stdout.strip()

    def restart_service(self, service):
        result = subprocess.run(["systemctl", "restart", service], capture_output=True, text=True)
        return result.stdout.strip()


class WindowsServiceManager:
    def get_services(self):
        result = subprocess.run(
            ["sc", "queryex", "type=service", "state=all"],
            capture_output=True,
            text=True,
        )
        return result.stdout

    def get_service_pid(self, service):
        result = subprocess.run(["tasklist", "/svc", "/fo", "csv"], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        for line in lines:
            if service in line:
                return line.split(",")[1].replace('"', "").strip()  # PID is the second column
        return None

    def get_service_status(self, service):
        result = subprocess.run(["sc", "query", service], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        for line in lines:
            if "STATE" in line:
                return line.split(":")[1].strip()  # Status is after the colon
        return None

    @staticmethod
    def parse_services(output):
        # This regular expression matches services in the format 'S{number}'
        pattern = re.compile(r"S\d+")
        services = pattern.findall(output)
        return set(services)

    def get_s_number_services(self):
        services = self.get_services()
        s_number_services = self.parse_services(services)
        service_details = []
        for service in s_number_services:
            pid = self.get_service_pid(service)
            status = self.get_service_status(service)
            service_details.append((service, pid, status))
        return service_details

    def start_service(self, service):
        cmd = ["net", "start", service]
        print(f"CMD: {' '.join(cmd)!r}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()

    def stop_service(self, service):
        cmd = ["net", "stop", service]
        print(f"CMD: {' '.join(cmd)!r}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()

    def restart_service(self, service):
        cmd = ["net", "restart", service]
        print(f"CMD: {' '.join(cmd)!r}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()


def get_services_manager() -> ServiceManagerProtocol:
    if platform.system() == "Linux":
        return LinuxServiceManager
    elif platform.system() == "Windows":
        return WindowsServiceManager
    else:
        raise Exception("Unsupported platform: " + platform.system())
