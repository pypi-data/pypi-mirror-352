# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@open.ac.uk>
#
# SPDX-License-Identifier: MIT
"""EMA commands."""

import os
import re
import shutil
import signal
import subprocess
import sys
from time import sleep
from urllib.parse import urlparse

import psutil
from rich import print  # noqa: A004
from typer import Typer

app = Typer()


@app.command()
def submit(student_pi: str) -> None:
    """Prepare a EMA submission."""
    if not os.path.isdir("ema"):
        print(
            "[red bold]Error:[/red bold] No [cyan]ema[/cyan] folder in the current folder. Check that you are in the folder that contains the ema folder"  # noqa: E501
        )
        return
    if os.path.isfile(f"ema-{student_pi}-q1.zip"):
        print(":litter_in_bin_sign: Removing old submission file")
        os.unlink(f"ema-{student_pi}-q1.zip")
    print(":hammer: Create the submission file")
    result = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "zip",
            "-r",
            f"ema-{student_pi}-q1.zip",
            "ema",
            "-x",
            "**/node_modules/",
            "**/node_modules/**",
            "**/dist/",
            "**/dist/**",
        ],
        check=True,
    )
    if result.returncode == 0:
        print(f":white_check_mark: Submission file ema-{student_pi}-q1.zip created")
    else:
        print("[red bold]Error:[/red bold]: Failed to correctly create the submission file")


@app.command()
def test(filename: str) -> None:
    """Test the submission for marking."""
    print(f":hammer: Extracting submission from {filename}")
    if os.path.isdir("test"):
        print(":litter_in_bin_sign: Removing old files")
        shutil.rmtree("test")
    os.mkdir("test")
    result = subprocess.run(  # noqa: S603
        ["unzip", os.path.join("..", filename)],  # noqa: S607
        cwd="test",
        check=False,
    )
    if result.returncode == 0:
        print(":white_check_mark: Submission file extracted")
    else:
        print("[red bold]Error:[/red bold] Failed to correctly extract the submission file")
        return
    if not os.path.isdir(os.path.join("test", "ema", "ema_service")):
        print(
            "[red bold]Error:[/red bold] No [cyan]test/ema/ema_service[/cyan] folder in the current folder. Required service not included in the submission"  # noqa: E501
        )
        return
    if not os.path.isdir(os.path.join("test", "ema", "ema_app")):
        print(
            "[red bold]Error:[/red bold] No [cyan]test/ema/ema_app[/cyan] folder in the current folder. Required application not included in the submission"  # noqa: E501
        )
        return
    if not os.path.isdir(os.path.join("test", "ema", "ema_app", "web")):
        print(
            "[red bold]Error:[/red bold] No [cyan]test/ema/ema_app/web[/cyan] folder in the current folder. Required web application not included in the submission"  # noqa: E501
        )
        return
    print(":hammer: Installing service dependencies")
    result = subprocess.run(  # noqa: S603
        ["npm", "ci", "--legacy-peer-deps"],  # noqa: S607
        cwd=os.path.join("test", "ema", "ema_service"),
        check=False,
    )
    if result.returncode != 0:
        print("\n\n[red bold]Error:[/red bold] Failed to install service dependencies\n")
        return
    print(":hammer: Installing application dependencies")
    result = subprocess.run(  # noqa: S603
        ["npm", "ci", "--legacy-peer-deps"],  # noqa: S607
        cwd=os.path.join("test", "ema", "ema_app"),
        check=False,
    )
    if result.returncode != 0:
        print("\n\n[red bold]Error:[/red bold] Failed to install application dependencies\n")
        return
    print(":hammer: Installing web application dependencies")
    result = subprocess.run(  # noqa: S603
        ["npm", "ci", "--legacy-peer-deps"],  # noqa: S607
        cwd=os.path.join("test", "ema", "ema_app", "web"),
        check=False,
    )
    if result.returncode != 0:
        print("\n\n[red bold]Error:[/red bold] Failed to install web application dependencies\n")
        return

    api_base = os.environ["JUPYTERHUB_SERVICE_PREFIX"] if "JUPYTERHUB_SERVICE_PREFIX" in os.environ else "/"
    app_base = os.environ["JUPYTERHUB_SERVICE_PREFIX"] if "JUPYTERHUB_SERVICE_PREFIX" in os.environ else "/"
    api_path = "http://localhost:3001"
    app_path = "http://localhost:5173"
    if "VSCODE_PROXY_URI" in os.environ:
        url = urlparse(os.environ["VSCODE_PROXY_URI"])
        api_path = f"{url.scheme}://{url.netloc}"
        app_path = f"{url.scheme}://{url.netloc}"
        api_base = api_base + "proxy/3001"
        app_base = app_base + "proxy/absolute/5173"
    api_path = api_path + api_base
    app_path = app_path + app_base
    if not api_path.endswith("/"):
        api_path = api_path + "/"

    print("\n:hammer: Fixing paths\n")
    apibase_fixed = False
    if os.path.exists(os.path.join("test", "ema", "ema_app", "libraries", "BookingService.ts")):
        with open(os.path.join("test", "ema", "ema_app", "libraries", "BookingService.ts")) as in_f:
            lines = in_f.readlines()
        with open(
            os.path.join("test", "ema", "ema_app", "libraries", "BookingService.ts"),
            "w",
        ) as out_f:
            for line in lines:
                if re.search(r"apibase\s*=\s*", line) and not re.search(r"^\s*//", line):
                    out_f.write(f'const apibase = "{api_path}";')
                    apibase_fixed = True
                else:
                    out_f.write(line)

    if not apibase_fixed:
        print(
            """\n
[red bold]============================[/red bold]
[red bold]No apibase found / corrected[/red bold]
[red bold]============================[/red bold]

No [cyan]apibase[/cyan] was found in the [cyan]test/ema/ema_app/libraries/PhotoService.ts[/cyan] file. The application may still work, but this cannot be guaranteed.

Press [green]Enter[/green] to continue
"""  # noqa: E501
        )
        input()

    print("\n:hammer: Compiling the ema service\n")
    result = subprocess.run(  # noqa: S603
        ["npm", "run", "build"],  # noqa: S607
        cwd=os.path.join("test", "ema", "ema_service"),
        check=False,
    )
    if result.returncode != 0:
        print("\n\n[red bold]Error:[/red bold] Failed to compile the EMA app\n")
        return
    print("\n:white_check_mark: ema service compiled\n")
    print("\n:hammer: Starting the ema service\n")
    ema_service = subprocess.Popen(  # noqa: S603
        ["npm", "run", "start"],  # noqa: S607
        cwd=os.path.join("test", "ema", "ema_service"),
        start_new_session=True,
    )
    while True:
        found = False
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr.port == 3001:  # noqa: PLR2004
                found = True
        if found:
            break
        sleep(1)
    print("\n:white_check_mark: ema service ready\n")
    print("\n:hammer: Starting the ema App\n")
    frontend_server = subprocess.Popen(  # noqa: S603
        ["npm", "run", "dev"],  # noqa: S607
        cwd=os.path.join("test", "ema", "ema_app", "web"),
        start_new_session=True,
        stdin=subprocess.DEVNULL,
    )
    while True:
        found = False
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr.port == 5173:  # noqa: PLR2004
                found = True
        if found:
            break
        sleep(1)
    print("\n:white_check_mark: Web application server ready\n")

    def shutdown_processes(sig, frame) -> None:  # noqa: ARG001, ANN001
        print(":hammer: Shutting down the ema service")
        os.killpg(os.getpgid(ema_service.pid), signal.SIGTERM)
        print(":hammer: Shutting down the EMA web application server")
        os.killpg(os.getpgid(frontend_server.pid), signal.SIGTERM)
        print(":white_check_mark: All servers shut down\n")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_processes)

    sleep(2)

    print(
        f"\n\n:white_check_mark: Ready for testing at [cyan bold]{app_path}[/cyan bold]. Press [green]Enter[/green] to shut down\n\n"  # noqa: E501
    )
    input()
    shutdown_processes(None, None)
