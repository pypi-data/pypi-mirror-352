# LLM Context Builder - Pip Package Structure

## Package Structure
```
llm-context-builder/
├── setup.py
├── pyproject.toml
├── README.md
├── llm_context_builder/
│   ├── __init__.py
│   ├── main.py
│   ├── project_detector.py
│   └── exporters/
│       ├── __init__.py
│       └── base_exporter.py
└── requirements.txt
```

## Installation & Usage

### Installation
```bash
pip install llm-context-builder
```

### Usage
```bash
# Export current directory
export_project

# Export specific directory
export_project /path/to/project

# Custom output location
export_project -o /custom/path/output.txt

# Quick web project export (auto-detects React/Vue/etc.)
export_project --preset web

# Quick Python project export
export_project --preset python

# Show token count estimate
export_project --count-tokens

# List available presets
export_project --list-presets
```

## Features

### 🎯 Smart Project Detection
- Automatically detects project type (Python, Node.js, React, Vue, etc.)
- Applies appropriate exclusions for each project type
- Suggests optimal presets

### 🧠 LLM-Optimized Output
- Clean, readable format perfect for LLM context
- Token counting to estimate context usage
- Optimized file headers for better parsing
- Smart content truncation for large files

### ⚡ Zero Configuration
- Works out of the box in any directory
- Sensible defaults for common project types
- Creates `project_export/` in current directory

### 🎛 Highly Configurable
- Custom exclusion patterns
- Project-specific presets
- Flexible output options
- Override any default behavior

## Example Outputs

### Command:
```bash
cd ~/my-react-app
export_project
```

### Result:
```
✅ Detected: React project
📁 Output: ./project_export/react_app_20250602_143052.txt
📊 Files processed: 45
🔤 Estimated tokens: ~12,500
⏱ Completed in 0.3s
```

### Command:
```bash
export_project --preset python --count-tokens
```

### Result:
```
🐍 Using Python preset
📁 Output: ./project_export/python_project_20250602_143105.txt
📊 Files: 23 processed, 156 skipped
🔤 Tokens: 8,342 (fits in GPT-4 context)
📋 Included: .py, .md, .txt, .yml, .toml
🚫 Excluded: __pycache__, .git, venv, *.pyc
```

## Project Presets

### Available Presets:
- `web` - React, Vue, Angular, general web projects
- `python` - Python packages, Django, Flask projects  
- `node` - Node.js, npm packages
- `mobile` - React Native, Flutter
- `docs` - Documentation projects
- `minimal` - Only essential text files
- `full` - Include everything (use with caution)

Each preset automatically configures:
- File type inclusions/exclusions
- Folder exclusions
- Size limits
- Output formatting