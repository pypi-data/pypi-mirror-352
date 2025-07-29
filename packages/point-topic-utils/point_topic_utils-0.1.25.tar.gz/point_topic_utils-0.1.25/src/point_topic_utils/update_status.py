from datetime import datetime, timezone

from .db.mongodb import MongoDBClient
from .models.project import Project
from .get_secrets import get_secrets

import argparse

def update_status(
    project_name: str,
    status: str,
    logs: str = '',
    command: str = None
) -> Project:
    """
    Updates the status of a project in MongoDB.

    Args:
        project_name (str): Name of the project to update
        status (str): Current run status (must be one of: running, finished, failed)
        logs (str, optional): Log messages. Defaults to empty string.
        command (str, optional): Last run command. Defaults to None.

    Returns:
        Project: Updated project object with new status, logs and timestamps

    Raises:
        ValueError: If status is not one of: running, finished, failed
    """
    # Validate status
    if status not in ['running', 'finished', 'failed']:
        raise ValueError('Invalid status')

    # Color code the status
    status_colors = {
        'finished': '\033[1;92m',  # Bright green
        'running': '\033[1;96m',   # Bright cyan
        'failed': '\033[1;91m'     # Bright red
    }
    color = status_colors.get(status, '\033[1;97m')
    reset = '\033[0m'
    print("\n\033[1;97;45m*** Updating project status: {0} -> {1}{2}{3}\033[1;97;45m ***\033[0m\n".format(
        project_name, color, status, reset))

    client = MongoDBClient()
    return client.update_project_status(
        project_name=project_name,
        current_run_status=status,
        last_run_date=datetime.now(timezone.utc),
        logs=logs,
        last_run_command=command
    )

def main():
    """CLI entrypoint for updating project status"""
    parser = argparse.ArgumentParser(description='Update project run status')
    parser.add_argument('--project-name', required=True, help='Name of the project to update')
    parser.add_argument('--status', required=True, help='Current run status (running, finished, failed)')
    parser.add_argument('--logs', default='', help='Log messages')
    parser.add_argument('--command', help='Last run command')
    
    args = parser.parse_args()
    
    update_status(
        project_name=args.project_name,
        status=args.status,
        logs=args.logs,
        command=args.command
    )

if __name__ == '__main__':
    main() 