import time
import json
import sys


class ComputerComponent():
    def __init__(self, name: str):
        self._name = name
        self._sleep_func = time.sleep

    def name(self) -> str:
        return self._name

    def sleep(self, seconds: float):
        self._sleep_func(seconds)

    def set_sleep_func(self, func):
        self._sleep_func = func


class Software():
    def __init__(self, name: str, size_mb: int):
        self._name = name
        self._size = size_mb

    def name(self) -> str:
        return self._name

    def size(self) -> int:
        return self._size


class CPU(ComputerComponent):
    def __init__(self, name: str, speed_mhz: int):
        ComputerComponent.__init__(self, name)
        self._speed = speed_mhz

    def speed(self) -> int:
        return self._speed


class RAM(ComputerComponent):
    def __init__(self, name: str, speed_mhz: int, size_mb: int):
        ComputerComponent.__init__(self, name)
        self._speed = speed_mhz
        self._size = size_mb
        self._open_software = []

    def speed(self) -> int:
        return self._speed

    def size(self) -> int:
        return self._size

    def taken(self) -> int:
        return sum(soft.size() / 10 for soft in self._open_software)

    def open(self, soft: Software) -> bool:
        can_open = soft.size() / 10 < self.size() - self.taken()
        if can_open:
            self._open_software.append(soft)
            self.sleep(soft.size() / self.speed())
        return can_open

    def close(self, soft_name: str) -> bool:
        for soft in self._open_software:
            if soft.name() == soft_name:
                self.sleep(soft.size() / self.speed())
                self._open_software.remove(soft)
                return True
        self.sleep(1.0)
        return False


class Disk(ComputerComponent):
    def __init__(self, name: str, speed_mbps: int, size_mb: int):
        ComputerComponent.__init__(self, name)
        self._speed = speed_mbps
        self._size = size_mb
        self._soft = []

    def speed(self) -> int:
        return self._speed

    def size(self) -> int:
        return self._size

    def taken(self) -> int:
        return sum(soft.size() for soft in self._soft)

    def install(self, soft: Software) -> bool:
        can_install = soft.size() < self.size() - self.taken()
        if can_install:
            self.sleep(soft.size() / self.speed())
            self._soft.append(soft)
        return can_install

    def uninstall(self, soft_name) -> bool:
        for soft in self._soft:
            if soft.name() == soft_name:
                self.sleep(soft.size() / self.speed())
                self._soft.remove(soft)
                return True
        self.sleep(2.0)
        return False

    def retrieve(self, soft_name: str) -> Software:
        for soft in self._soft:
            if soft.name() == soft_name:
                self.sleep(soft.size() / self.speed())
                return soft
        self.sleep(3.0)
        return None


class StandardOutput():
    def print(self, msg):
        print(msg)


class OperatingSystem(Software):
    def __init__(self, name: str, size_mb: int):
        Software.__init__(self, name, size_mb)
        self._output = StandardOutput()
        self._computer = None

    def set_output(self, output: StandardOutput):
        self._output = output

    def output(self) -> StandardOutput:
        return self._output

    def manage(self, computer: "Computer"):
        self._computer = computer

    def install(self, soft: Software) -> bool:
        self.output().print(f'Loading setup for {soft.name()} into RAM')
        if self._computer.ram().open(soft):
            self.output().print(f'Installing {soft.name()} into disk')
            if self._computer.disk().install(soft):
                self._computer.ram().close(soft.name())
                self.output().print(f'Successfully installed {soft.name()}')
                return True
            else:
                self._computer.ram().close(soft.name())
                self.output().print(f'Not enough space in disk to install {soft.name()}')
        else:
            self.output().print(f'Not enough RAM to install {soft.name()}')
        return False

    def uninstall(self, soft_name: str) -> bool:
        self.output().print(f'Attempting to uninstall {soft_name}')
        if self._computer.disk().uninstall(soft_name):
            self.output().print(f'Successfully uninstalled {soft_name}')
            return True
        self.output().print(f'Failed to uninstall {soft_name}, installation not found')
        return False

    def launch(self, soft_name: str) -> bool:
        self.output().print(f'Looking for an installation of {soft_name}')
        soft = self._computer.disk().retrieve(soft_name)
        if soft is not None:
            self.output().print(f'Loading {soft.name()} into RAM')
            if self._computer.ram().open(soft):
                self.output().print(f'Application {soft.name()} launched!')
                return True
            else:
                self.output().print(f'Not enough RAM to launch {soft.name()}')
        else:
            self.output().print(f'Could not find an installation named {soft.name()}')
        return False

    def close(self, soft_name: str) -> bool:
        self.output().print(f'Attempting to close {soft_name}')
        if self._computer.ram().close(soft_name):
            self.output().print(f'{soft_name} has been closed')
            return True
        self.output().print(f'Failed to unload {soft_name}, was not open')
        return False


class Computer():
    def __init__(self):
        self._cpu = None
        self._ram = None
        self._disk = None
        self._os = None

    def set_cpu(self, cpu: CPU):
        self._cpu = cpu

    def set_ram(self, ram: RAM):
        self._ram = ram

    def set_disk(self, disk: Disk):
        self._disk = disk

    def cpu(self) -> CPU:
        return self._cpu

    def ram(self) -> RAM:
        return self._ram

    def disk(self) -> Disk:
        return self._disk

    def install_os(self, os: OperatingSystem) -> bool:
        os.output().print(f'Loading setup for {os.name()} into RAM')
        if self._ram.open(os):
            os.output().print(f'Installing {os.name()} into disk')
            if self._disk.install(os):
                os.output().print(f'Successfully installed {os.name()}')
                self._os = os
                self._os.manage(self)
                return True
            else:
                os.output().print(f'Not enough disk space, aborting')
        else:
            os.output().print(f'Not enough RAM to load the OS installer, aborting')
        return False

    def os(self) -> OperatingSystem:
        return self._os


def load_data_file(from_path: str) -> dict:
    data_file = None
    try:
        data_file = open(from_path, 'r')
        data = json.load(data_file)
        data_file.close()
        return data
    except IOError:
        return None


def read_property(property_name: str, from_dict: dict, fallback=None):
    if from_dict is not None and property_name in from_dict:
        return from_dict[property_name]
    return fallback


def setup_pc(with_data: dict) -> Computer:
    computer_data = read_property('computer', with_data, None)
    if computer_data is not None:
        computer = Computer()
        cpu_data = read_property('cpu', computer_data, None)
        if cpu_data is not None:
            computer.set_cpu(CPU(read_property('name', cpu_data, 'UNNAMED CPU'), read_property('speed_mhz', cpu_data, 1600)))
        ram_data = read_property('ram', computer_data, None)
        if ram_data is not None:
            computer.set_ram(RAM(read_property('name', ram_data, 'UNNAMED RAM'), read_property('speed_mhz', ram_data, 1), read_property('size_mb', ram_data, 2048)))
        disk_data = read_property('disk', computer_data, None)
        if disk_data is not None:
            computer.set_disk(Disk(read_property('name', disk_data, 'UNNAMED DISK'), read_property('speed_mbps', disk_data, 100), read_property('size_mb', disk_data, 60000)))
        os_data = read_property('os', computer_data, None)
        if os_data is not None:
            computer.install_os(OperatingSystem(read_property('name', os_data, 'UNNAMED OS'), read_property('size_mb', os_data, 10000)))
        return computer
    return None


def print_pc(pc: Computer):
    print(f'PC Configuration:')
    print(f'\tCPU: {pc.cpu().name()} @ {pc.cpu().speed()}Mhz')
    print(f'\tRAM: {pc.ram().name()} ({pc.ram().size()}MB) @ {pc.ram().speed()}Mhz')
    print(f'\tDisk: {pc.disk().name()} ({pc.disk().size()}MB) @ {pc.disk().speed()}MBPS')
    print(f'\tOS: {pc.os().name()}')


def setup_software_repository(from_data: dict) -> list:
    software = read_property('software', from_data, [])
    if software is not None:
        for i in range(len(software)):
            software[i] = Software(read_property('name', software[i], 'UNNAMED SOFTWARE'), read_property('size_mb', software[i], 100))
    return software


def read_commands(from_data: dict) -> list:
    return read_property('commands', from_data, [])


def run_command(on_pc: Computer, soft_repo: list, command: str):
    command = command.split()
    if command[0] == 'install':
        for soft in soft_repo:
            if soft.name() == command[1]:
                on_pc.os().install(soft)
    elif command[0] == 'uninstall':
        on_pc.os().uninstall(command[1])
    elif command[0] == 'launch':
        on_pc.os().launch(command[1])
    elif command[0] == 'close':
        on_pc.os().close(command[1])


if __name__ == '__main__':
    data = load_data_file(sys.argv[1])
    computer = setup_pc(data)
    if computer is not None:
        print_pc(computer)
        software_list = setup_software_repository(data)
        commands = read_commands(data)
        for command in commands:
            run_command(computer, software_list, command)
