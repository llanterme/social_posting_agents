---
trigger: always_on
---

---
description: Code & Process Standards for Python Projects
globs:
  - "**/*.py"
alwaysApply: true
---

## Always start by reviewing the PLANNING.md file after each prompt to check for feature changes, project overview and features. When a feature is complete, please create or update the TASK.md file to represent the state.

## Never implement features that are outside the scope of your requirements. If you are unsure, please ask for confirmation.

# Code & Process Standards (Python)

## 1. General Principles

- **Clean Code:**  
  - Follow PEP 8 and The Zen of Python.  
  - Keep functions/classes small (≤ 50 lines). Single responsibility per function/class.  
  - Use descriptive names.  
  - Delete dead code; avoid commented-out code.  
  - Prioritize readability over cleverness.

- **Functional Style & Immutability:**  
  - Favor pure functions without side effects.  
  - Use immutable structures (tuples, `frozenset`) when data shouldn’t change.  
  - Minimize global mutable state.

## 2. Technology Stack

- **Language:** Python 3.9+  
- **Package Management:** Poetry (`pyproject.toml`, `poetry.lock`).  
  -  Always use the latest compatible dependencies
- **Runtime Environment:**  
  - Always use virtual environments (`poetry shell` or `python -m venv`). No global installs.

## 3. Documentation

- **Use context7 MCP server** for up-to-date language documentation.  
- **Use the Sequential Thinking MCP** to break down complex tasks.

## 4. Changes, New Features, and Enhancements

- Always compare the PLANNING.MD to the TASK.MD to see if any new functionality or features have been requested.