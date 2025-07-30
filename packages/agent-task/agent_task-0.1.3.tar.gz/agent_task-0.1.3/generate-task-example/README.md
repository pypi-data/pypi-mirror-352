# Generate Task Example

A template task demonstrating how to create and structure new tasks in the Agent Task platform.

## Overview

This task serves as a reference implementation for creating new tasks in the Agent Task platform. It showcases the recommended directory structure, rule organization, and documentation practices.

## Directory Structure

```
generate-task-example/
├── README.md           # This documentation
└── rules/             # Task-specific guidelines and rules
    └── rule.mdc       # Main rules file
```

## Purpose

1. **Educational Resource**: Helps users understand how to create well-structured tasks
2. **Reference Implementation**: Provides a template for task creation
3. **Best Practices**: Demonstrates recommended patterns and documentation standards

## Features

- Complete directory structure following platform standards
- Example rules demonstrating proper rule formatting
- Comprehensive documentation template

## Usage

### Creating a New Task

1. Use this task as a template:
```bash
agent-task clone generate-task-example new-task-name
```

2. Customize the rules and documentation for your specific needs

### Modifying Rules

1. Navigate to the `rules` directory
2. Edit `rule.mdc` to define task-specific guidelines
3. Follow the established rule format for consistency

## Guidelines

When using this template:

1. **Documentation**: Keep README.md clear and comprehensive
2. **Rules**: Define specific, actionable guidelines
3. **Structure**: Maintain the standard directory organization
4. **Naming**: Use descriptive, kebab-case names for tasks

## Examples

### Basic Rule Structure

```markdown
# Rule Category
## Subcategory
1. **Rule Title**: Description
2. **Another Rule**: Details
```

## Contributing

Feel free to suggest improvements to this template by:

1. Creating an issue describing the enhancement
2. Submitting a pull request with proposed changes
3. Following the project's contribution guidelines

## Related Tasks

- `helloworld` - Basic task example
- `firstTask` - Another reference implementation
