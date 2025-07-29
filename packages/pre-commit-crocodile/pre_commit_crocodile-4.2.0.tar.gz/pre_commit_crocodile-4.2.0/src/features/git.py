#!/usr/bin/env python3

# Standard libraries
from pathlib import Path
from typing import List

# Components
from ..system.commands import Commands

# Git class
class Git:

    # Constants
    BINARY: str = 'git'

    # Hooks directory
    @staticmethod
    def hooks_dir() -> str:

        # Result
        return Commands.output(Git.BINARY, [
            'rev-parse',
            '--git-path',
            'hooks',
        ])

    # Hooks files
    @staticmethod
    def hooks_files() -> List[str]:

        # Variables
        hooks_dir: Path = Path(Git.hooks_dir())

        # Result
        return [
            hook.name for hook in Path(hooks_dir).iterdir()
            if hook.is_file() and '.' not in hook.name
        ]

    # Remotes
    @staticmethod
    def remotes() -> List[str]:

        # List git remotes
        return [
            branch.lstrip('*').strip()
            for branch in Commands.output(Git.BINARY, [
                'remote',
            ]).splitlines()
        ]

    # Status
    @staticmethod
    def status(untracked: bool) -> bool:

        # Show git status
        return Commands.run(Git.BINARY, [
            'status',
        ] + ([
            '--untracked-files',
        ] if untracked else []))

    # Update remote head
    @staticmethod
    def update_remote_head(remote: str) -> bool:

        # Fetch remote branches
        Commands.run(Git.BINARY, [
            'fetch',
            f'{remote}',
        ])

        # Update remote head
        return Commands.run(Git.BINARY, [
            'remote',
            'set-head',
            f'{remote}',
            '-a',
        ])
