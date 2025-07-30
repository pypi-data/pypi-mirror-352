# Run VIM and Busybox as a Python module in Linux/x86_64 systems

Motivation: run programs not available in restricted environments where
any package can be installed by **pip**


### Installation
```bash
pip install binloader
```

## Usage:
### Vim
```bash
python -m binloader vim /etc/passwd
```

### Busybox
```bash
python -m binloader busybox uname -a
```

### ToDo
1. Support for other OS/architectures
2. Add other binaries

## Author

Ulises <ulises.odysseus22@gmail.com>
