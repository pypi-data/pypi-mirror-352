import typer
import yaml

from rsync_ssh_client import RsyncConfig, RsyncOptions, RsyncSSHClient

app = typer.Typer()


def build_config(
        user: str,
        host: str,
        port: int,
        ssh_key: str | None,
        password: str | None,
        exclude_file: str | None,
        owner: int | None,
        group: int | None,
        chmod: str | None,
        delete: bool,
        use_super: bool,
        dry_run: bool,
        use_sshpass: bool,
        flags: list[str],
) -> RsyncConfig:
    options = RsyncOptions(
        exclude_file=exclude_file,
        owner=owner,
        group=group,
        chmod_flags=chmod,
        delete=delete,
        use_super=use_super,
        dry_run=dry_run,
        use_sshpass=use_sshpass,
        rsync_flags=flags,
    )
    return RsyncConfig(
        user=user,
        host=host,
        ssh_port=port,
        ssh_private_key=ssh_key,
        password=password,
        options=options,
    )


def _load_config_from_yaml(path: str) -> RsyncConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    options = RsyncOptions(**data.get("options", {}))
    config = RsyncConfig(
        **{k: v for k, v in data.items() if k != "options"},
        options=options,
    )
    return config


@app.command()
def put(
        local_path: str,
        remote_path: str,
        config_path: str = typer.Option(None),
        user: str = typer.Option("root"),
        host: str = typer.Option("localhost"),
        port: int = typer.Option(22),
        ssh_key: str = typer.Option(None),
        password: str = typer.Option(None),
        exclude_file: str = typer.Option(None),
        owner: int = typer.Option(None),
        group: int = typer.Option(None),
        chmod: str = typer.Option(None),
        delete: bool = typer.Option(False),
        use_super: bool = typer.Option(False),
        dry_run: bool = typer.Option(False),
        use_sshpass: bool = typer.Option(False),
        flags: list[str] = typer.Option(["-avzP"]),
) -> None:
    config = (
        _load_config_from_yaml(config_path)
        if config_path
        else build_config(
            user,
            host,
            port,
            ssh_key,
            password,
            exclude_file,
            owner,
            group,
            chmod,
            delete,
            use_super,
            dry_run,
            use_sshpass,
            flags,
        )
    )
    client = RsyncSSHClient(config)
    result = (
        client.dry_run(remote_path, local_path, direction="put")
        if dry_run
        else client.put(local_path, remote_path)
    )
    print(result)


@app.command()
def get(
        remote_path: str,
        local_path: str,
        config_path: str = typer.Option(None),
        user: str = typer.Option("root"),
        host: str = typer.Option("localhost"),
        port: int = typer.Option(22),
        ssh_key: str = typer.Option(None),
        password: str = typer.Option(None),
        exclude_file: str = typer.Option(None),
        owner: int = typer.Option(None),
        group: int = typer.Option(None),
        chmod: str = typer.Option(None),
        delete: bool = typer.Option(False),
        use_super: bool = typer.Option(False),
        dry_run: bool = typer.Option(False),
        use_sshpass: bool = typer.Option(False),
        flags: list[str] = typer.Option(["-avzP"]),
) -> None:
    config = (
        _load_config_from_yaml(config_path)
        if config_path
        else build_config(
            user,
            host,
            port,
            ssh_key,
            password,
            exclude_file,
            owner,
            group,
            chmod,
            delete,
            use_super,
            dry_run,
            use_sshpass,
            flags,
        )
    )
    client = RsyncSSHClient(config)
    result = (
        client.dry_run(remote_path, local_path, direction="get")
        if dry_run
        else client.get(remote_path, local_path)
    )
    print(result)
