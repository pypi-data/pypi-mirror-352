# rsync-ssh-client

A flexible Python client for `rsync` over SSH.

## 🚀 Installation

```bash
pip install rsync-ssh-client  # when published
# or from source
pip install -e .
```

## 📦 Features

* Secure file transfers using `rsync` over SSH
* Supports both password and SSH private key authentication
* SSH auth via `sshpass` or key file
* Configurable via Python, YAML, or CLI
* Preserves file ownership and permissions
* Fully typed and testable
* `--dry-run` support for safe previews

---

## 🧑‍💻 Usage

### 1. As a Library (Python)

#### Via direct configuration:

```python
from rsync_ssh_client import RsyncSSHClient, RsyncConfig, RsyncOptions

options = RsyncOptions(
    exclude_file=".rsyncignore",
    owner=1000,
    group=1000,
    delete=True,
    chmod_flags="Du=rwx,Dgo=rx,Fu=rw,Fog=r",
    use_super=True,
    rsync_flags=["-avzP"]
)

config = RsyncConfig(
    user="deploy",
    host="example.com",
    ssh_port=22,
    ssh_private_key="~/.ssh/id_rsa",
    password=None,
    use_sshpass=False,
    options=options
)

client = RsyncSSHClient(config)
client.put("build/", "/remote/path")
client.get("/remote/logs", "logs/")
```

#### Via config file:

```yaml
# config.yaml
user: deploy
host: example.com
ssh_port: 22
ssh_private_key: ~/.ssh/id_rsa
use_sshpass: false

options:
  exclude_file: .rsyncignore
  owner: 1000
  group: 1000
  chmod_flags: Du=rwx,Dgo=rx,Fu=rw,Fog=r
  delete: true
  use_super: true
  rsync_flags:
    - -avzP
```

```python
import yaml
from rsync_ssh_client import RsyncSSHClient, RsyncConfig, RsyncOptions

with open("config.yaml") as f:
    data = yaml.safe_load(f)

config = RsyncConfig(
    **{
        **{k: v for k, v in data.items() if k != "options"},
        "options": RsyncOptions(**data.get("options", {}))
    }
)

client = RsyncSSHClient(config)
client.put("src", "/dst")
```

---

## 📿 CLI Usage

```bash
# using config file
rsync-client put --config config.yaml ./build /remote
rsync-client get --config config.yaml /remote/logs ./logs

# or passing options manually
rsync-client put --user deploy --host example.com ./src /dst \
  --exclude-file .rsyncignore --dry-run --use-sshpass --password secret

rsync-client get --user deploy --host example.com /srv/data ./data \
  --use-sshpass --password secret --dry-run
```

---

## 🐳 Docker Testing

A Dockerfile is included for local testing with an SSH+rsync server:

```bash
docker build -t rsync-test .
docker run -d --name rsync-test -p 2222:22 rsync-test
```

Default credentials:

* **user**: `rsyncuser`
* **password**: `rsyncpass`
* **port**: `2222`

Optionally mount volumes:

```bash
docker run -d --name rsync-test -p 2222:22 -v $(pwd)/remote:/home/rsyncuser/remote rsync-test
```

### 🔁 Automated test script

Run the following script to:

* create a 1024-byte file with random data
* transfer it via `put`
* fetch it back via `get`
* verify the contents match
* perform dry-run tests

```bash
#!/bin/bash
set -euo pipefail

mkdir -p test_data test_result

touch .rsyncignore

# Create input file
echo "🔧 Preparing test input..."
head -c 1024 </dev/urandom > test_data/random.bin

# Upload
rsync-client put \
  --user rsyncuser \
  --host localhost \
  --port 2222 \
  --password rsyncpass \
  --use-sshpass \
  --chmod=u+rw \
  --exclude-file=.rsyncignore \
  --delete \
  --use-super \
  test_data/random.bin \
  /home/rsyncuser/random.bin

# Download
rsync-client get \
  --user rsyncuser \
  --host localhost \
  --port 2222 \
  --password rsyncpass \
  --use-sshpass \
  --chmod=u+rw \
  --exclude-file=.rsyncignore \
  --delete \
  --use-super \
  /home/rsyncuser/random.bin \
  test_result/random.bin

cmp test_data/random.bin test_result/random.bin && echo "✅ Files match!"

# Dry-run PUT
rsync-client put \
  --user rsyncuser \
  --host localhost \
  --port 2222 \
  --password rsyncpass \
  --use-sshpass \
  --dry-run \
  test_data/random.bin \
  /home/rsyncuser/random_dryrun.bin

# Dry-run GET
rsync-client get \
  --user rsyncuser \
  --host localhost \
  --port 2222 \
  --password rsyncpass \
  --use-sshpass \
  --dry-run \
  /home/rsyncuser/random.bin \
  test_result/random_dryrun.bin

echo "✅ Dry-run tests executed (no files should have been transferred)"
```

---

## 🤮 Development

Install dev dependencies:

```bash
pip install -r requirements-dev.txt
```

Run checks:

```bash
ruff check . --fi
black .
mypy rsync_ssh_client/
pytest
```

---

## ✅ License

Licensed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)

---

## ✨ Author

Created by ilia iakhin
