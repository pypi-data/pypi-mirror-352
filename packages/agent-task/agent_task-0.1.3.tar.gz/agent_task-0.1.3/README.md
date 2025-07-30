# Agent Task

A powerful task management platform for AI agents in Cursor AI (v0.1.0).

## Overview

Agent Task is a platform that helps manage, organize, and share task-specific configurations for AI agents in Cursor. It provides a structured way to define rules, guidelines, and model context protocols (MCP) for different AI tasks.

## Features

- **Task Management**: Create, load, archive, and import task configurations
- **Structured Organization**: Maintains a consistent directory structure for each task
- **Rule Management**: Store and manage task-specific guidelines and rules
- **MCP Support**: Handle Model Context Protocol servers for advanced AI configurations
- **Cross-platform**: Works across different operating systems using standard paths

## Installation

```bash
pip install agent-task
```

## Directory Structure

Each task follows this standard structure:

```
task_name/
├── README.md           # Task documentation
├── rules/             # Task-specific guidelines
│   └── rule.mdc       # Main rules file
└── mcp/               # Model Context Protocol servers
```

## Usage

### Initialize a New Task

```bash
agent-task init task_name
```

### List Available Tasks

```bash
agent-task list
```

### Archive a Task

```bash
agent-task archive task_name
```

### Import a Task

```bash
agent-task import task_name
```

### Clone a Task from Marketplace

```bash
agent-task clone [URL]
```

### Show Task Archive Directory

```bash
agent-task path
```

## Configuration

The platform uses standard application directories for storing tasks and configurations:

- **App Data**: User-specific application data
- **Config**: User-specific configuration files
- **Cache**: User-specific cache data
- **Logs**: User-specific log files

## Development

### Project Structure

- `agent_task/`
  - `__init__.py` - Package initialization and version
  - `paths.py` - Path management functionality
  - `task_manager.py` - Core task management logic
  - `cli.py` - Command-line interface implementation

### Requirements

- Python 3.6+
- `appdirs` for cross-platform path management
- `pyyaml` for configuration handling
- Additional dependencies as specified in requirements.txt

## License

[Add your license information here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.