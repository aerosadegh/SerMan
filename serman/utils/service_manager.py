import platform
import re
from typing import Protocol, List, Tuple, Type
import subprocess


class ServiceManagerProtocol(Protocol):
    def get_services(self) -> str: ...

    def get_service_pid(self, service: str) -> str: ...

    def get_service_status(self, service: str) -> str: ...

    def get_s_number_services(self) -> List[Tuple[str, str, str]]: ...

    def start_service(self, service: str) -> str: ...

    def stop_service(self, service: str) -> str: ...

    def restart_service(self, service: str) -> str: ...

    @staticmethod
    def parse_services(output: str) -> set: ...


class LinuxServiceManager:
    def get_services(self) -> str:
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--all"],
            capture_output=True,
            text=True,
        )
        return result.stdout

    def get_service_pid(self, service: str) -> str:
        result = subprocess.run(
            ["systemctl", "show", "-p", "MainPID", "--value", service],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def get_service_status(self, service: str) -> str:
        result = subprocess.run(
            ["systemctl", "is-active", service], capture_output=True, text=True
        )
        return result.stdout.strip()

    @staticmethod
    def parse_services(output: str) -> set:
        # This regular expression matches services in the format 'S{number}'
        pattern = re.compile(r"S\d+")
        services = pattern.findall(output)
        return set(services)

    def get_s_number_services(self) -> List[Tuple[str, str, str]]:
        services = self.get_services()
        s_number_services = self.parse_services(services)
        service_details = []
        for service in s_number_services:
            pid = self.get_service_pid(service)
            status = self.get_service_status(service)
            service_details.append((service, pid, status))
        return service_details

    def start_service(self, service: str) -> str:
        result = subprocess.run(["systemctl", "start", service], capture_output=True, text=True)
        return result.stdout.strip()

    def stop_service(self, service: str) -> str:
        result = subprocess.run(["systemctl", "stop", service], capture_output=True, text=True)
        return result.stdout.strip()

    def restart_service(self, service: str) -> str:
        result = subprocess.run(["systemctl", "restart", service], capture_output=True, text=True)
        return result.stdout.strip()


class WindowsServiceManager:
    def get_services(self) -> str:
        result = subprocess.run(
            ["sc", "queryex", "type=service", "state=all"],
            capture_output=True,
            text=True,
        )
        return result.stdout

    def get_service_pid(self, service: str) -> str:
        result = subprocess.run(["tasklist", "/svc", "/fo", "csv"], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        for line in lines:
            if service in line:
                return line.split(",")[1].replace('"', "").strip()  # PID is the second column
        return ""

    def get_service_status(self, service: str) -> str:
        result = subprocess.run(["sc", "query", service], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        for line in lines:
            if "STATE" in line:
                return line.split(":")[1].strip()  # Status is after the colon
        return ""

    @staticmethod
    def parse_services(output: str) -> set:
    def parse_services(output):
        # This regular expression matches services in the format 'S{number}'
        pattern = re.compile(r"S\d+")
        services = pattern.findall(output)
        return set(services)

    def get_s_number_services(self) -> List[Tuple[str, str, str]]:
        services = self.get_services()
        s_number_services = self.parse_services(services)
        service_details = []
        for service in s_number_services:
            pid = self.get_service_pid(service)
            status = self.get_service_status(service)
            service_details.append((service, pid, status))
        return service_details

    def start_service(self, service: str) -> str:
        cmd = ["net", "start", service]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()

    def stop_service(self, service: str) -> str:
        cmd = ["net", "stop", service]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()

    def restart_service(self, service: str) -> str:
        self.stop_service(service)
        return self.start_service(service)


def get_services_manager() -> Type[ServiceManagerProtocol]:
    if platform.system() == "Linux":
        return LinuxServiceManager
    elif platform.system() == "Windows":
        return WindowsServiceManager
    else:
        raise Exception("Unsupported platform: " + platform.system())
