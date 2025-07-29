import logging
from dataclasses import dataclass, field
from subprocess import STDOUT, check_output
from typing import Optional


@dataclass
class RsyncOptions:
    exclude_file: Optional[str] = None
    owner: Optional[int] = None
    group: Optional[int] = None
    chmod_flags: Optional[str] = None
    delete: bool = False
    use_super: bool = False
    rsync_flags: list[str] = field(default_factory=lambda: ["-avzP"])
    dry_run: bool = False
    use_sshpass: bool = False  # newly added


@dataclass
class RsyncConfig:
    user: str
    host: str
    ssh_port: int = 22
    ssh_private_key: Optional[str] = None
    password: Optional[str] = None
    options: RsyncOptions = field(default_factory=RsyncOptions)


class RsyncSSHClient:
    def __init__(self, config: RsyncConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def _build_base_command(self, direction: str, local_path: str, remote_path: str) -> list[str]:
        ssh_cmd = [
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "HostKeyAlgorithms=+ssh-rsa",
            "-p",
            str(self.config.ssh_port),
        ]
        if self.config.ssh_private_key:
            ssh_cmd += ["-i", self.config.ssh_private_key]

        rsync_cmd = []
        if self.config.options.use_sshpass and self.config.password:
            rsync_cmd += ["sshpass", "-p", self.config.password]

        rsync_cmd += ["rsync"] + self.config.options.rsync_flags

        if self.config.options.delete:
            rsync_cmd.append("--delete")

        if self.config.options.dry_run:
            rsync_cmd.append("--dry-run")

        if self.config.options.exclude_file:
            rsync_cmd += ["--exclude-from", self.config.options.exclude_file]

        if self.config.options.chmod_flags:
            rsync_cmd += ["--chmod", self.config.options.chmod_flags]

        if self.config.options.use_super:
            rsync_cmd += ["--rsync-path", "sudo rsync"]

        rsync_cmd += ["-e", " ".join(ssh_cmd)]

        if direction == "put":
            rsync_cmd += [local_path, remote_path]
        elif direction == "get":
            rsync_cmd += [remote_path, local_path]
        else:
            raise ValueError("Invalid direction, use 'put' or 'get'")

        return rsync_cmd

    def _run_cmd(self, cmd: list[str]) -> str:
        self.logger.debug(f"Executing command: {' '.join(cmd)}")
        output = check_output(cmd, stderr=STDOUT)
        result = output.decode()
        if "sent" in result:
            self.logger.info("Rsync finished successfully")
        return result

    def put(self, local_path: str, remote_path: str) -> str:
        self.logger.info(f"Running rsync PUT: {local_path} -> {remote_path}")
        remote = f"{self.config.user}@{self.config.host}:{remote_path}"
        cmd = self._build_base_command("put", local_path, remote)
        return self._run_cmd(cmd)

    def get(self, remote_path: str, local_path: str) -> str:
        self.logger.info(f"Running rsync GET: {remote_path} -> {local_path}")
        remote = f"{self.config.user}@{self.config.host}:{remote_path}"
        cmd = self._build_base_command("get", local_path, remote)
        return self._run_cmd(cmd)

    def dry_run(self, remote_path: str, local_path: str, direction: str) -> str:
        self.logger.info("Executing dry run")
        self.config.options.dry_run = True
        if direction == "put":
            return self.put(local_path, remote_path)
        return self.get(remote_path, local_path)
