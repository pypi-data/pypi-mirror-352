import os
import stat
import sys
from pathlib import Path


def run(argv):
    app = argv[1]
    args = argv[1:]
    cur_dir = Path(__file__).resolve().parent

    binaries = {
        "vim": f"{cur_dir}/binaries/vim_amd64",
        "busybox": f"{cur_dir}/binaries/busybox_amd64",
    }

    ram_file = os.memfd_create("ram_file")
    os.chmod(ram_file, stat.S_IEXEC)

    f_ram = os.fdopen(ram_file, "wb")
    vim_data = open(binaries[app], "br").read()

    f_ram.write(vim_data)
    os.execv(f"/proc/self/fd/{ram_file}", args)


def main():
    argv = sys.argv
    assert len(argv) > 1, "Missing parameters. At least provide app name"
    run(argv)


if __name__ == "__main__":
    main()
