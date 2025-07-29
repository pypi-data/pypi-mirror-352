#!/usr/bin/env python3

# Standard libraries
from pathlib import Path
from shutil import which
import subprocess
from typing import List

# Commands
class Commands:

    # Exists
    @staticmethod
    def exists(binary: str) -> bool:

        # Check system binary exists
        return which(binary) is not None

    # Grep
    @staticmethod
    def grep(file: Path, string: str) -> bool:

        # Ignore missing file
        if not file.exists():
            return False

        # Check file contains string
        with open(
                file,
                encoding='utf8',
                mode='r',
        ) as f:
            for line in f.readlines():

                # Find string in line
                if string in line:
                    return True

        # Fallback
        return False # pragma: no cover

    # Output
    @staticmethod
    def output(binary: str, arguments: List[str]) -> str:

        # Get system output
        try:
            return subprocess.check_output(
                args=[binary] + arguments,
                cwd=None,
                shell=False,
            ).strip().decode()
        except subprocess.CalledProcessError as err:
            return str(err.output.decode())
        except FileNotFoundError:
            return ''

    # Command
    @staticmethod
    def pip(arguments: List[str]) -> bool:

        # Run with pipx
        if Commands.exists('pipx'):
            return Commands.run(
                'pipx',
                arguments,
            )

        # Run with pip # pragma: no cover
        return Commands.run(
            'sudo',
            ['pip'] + arguments,
        )

    # Command
    @staticmethod
    def run(binary: str, arguments: List[str]) -> bool:

        # Run system command
        try:
            process = subprocess.run(
                args=[binary] + arguments,
                cwd=None,
                check=True,
                shell=False,
            )
            return process.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            return False
