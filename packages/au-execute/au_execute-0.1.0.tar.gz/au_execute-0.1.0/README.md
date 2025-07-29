# Data Pipeline Execution Framework

A framework for executing data processing and machine learning pipelines using the Command pattern. Provides flexible execution of complete pipelines or individual nodes with support for ML model versioning and Spark integration.

## Features

- **Command Pattern Implementation**: Encapsulate pipeline nodes as commands
- **Dual Pipeline Support**: Handle both standard data processing and ML pipelines
- **Flexible Execution**: Run complete pipelines or individual nodes
- **ML Features**:
  - Model versioning
  - Hyperparameter configuration
  - Spark integration for distributed computing
- **Logging**: Integrated logging with Loguru
- **I/O Management**: Built-in input loading and output saving capabilities

## Installation

1. **Prerequisites**:
   - Python 3.8+
   - Pip package manager

2. **Install dependencies**:
```bash
pip install au_iomanager auconfig