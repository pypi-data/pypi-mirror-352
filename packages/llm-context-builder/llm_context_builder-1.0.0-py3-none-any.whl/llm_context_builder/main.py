#!/usr/bin/env python3
"""
LLM Context Builder - Main CLI interface
Export any project to a single text file optimized for LLM context
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
import fnmatch
import click
from colorama import init, Fore, Style

from .project_detector import ProjectDetector
from .exporters.base_exporter import BaseExporter

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Project presets configuration
PRESETS = {
    "web": {
        "name": "Web Project",
        "description": "React, Vue, Angular, HTML/CSS/JS projects",
        "include_extensions": [".js", ".jsx", ".ts", ".tsx", ".vue", ".html", ".css", ".scss", ".sass", ".less", ".json", ".md", ".txt", ".yaml", ".yml"],
        "exclude_folders": ["node_modules", "dist", "build", ".next", ".nuxt", "coverage", ".nyc_output"],
        "exclude_files": ["package-lock.json", "yarn.lock", "*.min.js", "*.min.css"],
        "max_file_size": 100000,  # 100KB
    },
    "python": {
        "name": "Python Project", 
        "description": "Python packages, Django, Flask, FastAPI projects",
        "include_extensions": [".py", ".pyi", ".pyx", ".pxd", ".md", ".rst", ".txt", ".toml", ".cfg", ".ini", ".yaml", ".yml", ".json"],
        "exclude_folders": ["__pycache__", ".pytest_cache", "venv", "env", ".venv", ".env", "dist", "build", "*.egg-info"],
        "exclude_files": ["*.pyc", "*.pyo", "*.pyd", ".coverage", "*.log"],
        "max_file_size": 200000,  # 200KB
    },
    "node": {
        "name": "Node.js Project",
        "description": "Node.js, npm packages, backend projects",
        "include_extensions": [".js", ".ts", ".json", ".md", ".txt", ".yaml", ".yml"],
        "exclude_folders": ["node_modules", "dist", "build", "coverage", ".nyc_output"],
        "exclude_files": ["package-lock.json", "yarn.lock", "*.log"],
        "max_file_size": 100000,
    },
    "mobile": {
        "name": "Mobile Project",
        "description": "React Native, Flutter, mobile app projects",
        "include_extensions": [".js", ".jsx", ".ts", ".tsx", ".dart", ".java", ".kt", ".swift", ".m", ".h", ".json", ".md", ".yaml", ".yml"],
        "exclude_folders": ["node_modules", "build", "ios/build", "android/build", ".dart_tool"],
        "exclude_files": ["*.log", "Podfile.lock"],
        "max_file_size": 150000,
    },
    "docs": {
        "name": "Documentation Project",
        "description": "Documentation, blog, content projects",
        "include_extensions": [".md", ".rst", ".txt", ".adoc", ".org", ".tex", ".html", ".css", ".js", ".json", ".yaml", ".yml"],
        "exclude_folders": ["_site", "public", "dist", "build", "node_modules"],
        "exclude_files": ["*.log"],
        "max_file_size": 500000,  # 500KB for docs
    },
    "minimal": {
        "name": "Minimal Export",
        "description": "Only essential text files",
        "include_extensions": [".md", ".txt", ".json", ".yaml", ".yml"],
        "exclude_folders": [],
        "exclude_files": [],
        "max_file_size": 50000,
    },
    "full": {
        "name": "Full Export",
        "description": "Include everything (use with caution)",
        "include_extensions": None,  # Include all text files
        "exclude_folders": [".git", "__pycache__", "node_modules"],  # Minimal exclusions
        "exclude_files": ["*.log"],
        "max_file_size": 1000000,  # 1MB
    }
}

def estimate_tokens(text):
    """Rough token estimation for OpenAI models"""
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        return len(encoding.encode(text))
    except ImportError:
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(text) // 4

def print_success(message):
    """Print success message in green"""
    click.echo(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print info message in blue"""
    click.echo(f"{Fore.BLUE}📁 {message}{Style.RESET_ALL}")

def print_stats(message):
    """Print stats in yellow"""
    click.echo(f"{Fore.YELLOW}📊 {message}{Style.RESET_ALL}")

def print_tokens(message):
    """Print token info in magenta"""
    click.echo(f"{Fore.MAGENTA}🔤 {message}{Style.RESET_ALL}")

def print_warning(message):
    """Print warning in yellow"""
    click.echo(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")

def print_error(message):
    """Print error in red"""
    click.echo(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

@click.command()
@click.argument('source_dir', default='.', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('-o', '--output', help='Output file path (default: project_export/PROJECT_NAME_TIMESTAMP.txt)')
@click.option('--preset', type=click.Choice(list(PRESETS.keys())), help='Use a predefined project preset')
@click.option('--list-presets', is_flag=True, help='List all available presets and exit')
@click.option('--count-tokens', is_flag=True, help='Estimate token count for LLM context')
@click.option('--max-size', type=int, help='Maximum file size in bytes to include')
@click.option('--exclude-ext', multiple=True, help='Additional file extensions to exclude')
@click.option('--exclude-folders', multiple=True, help='Additional folder patterns to exclude')
@click.option('--exclude-files', multiple=True, help='Additional file patterns to exclude')
@click.option('--include-ext', multiple=True, help='Only include these file extensions')
@click.option('--no-timestamp', is_flag=True, help='Disable timestamp in output filename')
@click.option('--quiet', is_flag=True, help='Minimal output')
@click.option('--auto-detect/--no-auto-detect', default=True, help='Auto-detect project type and suggest preset')
def cli(source_dir, output, preset, list_presets, count_tokens, max_size, exclude_ext, 
        exclude_folders, exclude_files, include_ext, no_timestamp, quiet, auto_detect):
    """
    Export any project to a single text file optimized for LLM context.
    
    Works in any directory - just run 'export_project' and it will export
    the current directory to project_export/PROJECT_NAME_TIMESTAMP.txt
    """
    
    if list_presets:
        if not quiet:
            click.echo(f"\n{Fore.CYAN}📋 Available Presets:{Style.RESET_ALL}\n")
        for preset_name, config in PRESETS.items():
            click.echo(f"{Fore.YELLOW}{preset_name:10}{Style.RESET_ALL} - {config['description']}")
        return
    
    start_time = time.time()
    source_path = Path(source_dir).resolve()
    
    if not quiet:
        click.echo(f"\n{Fore.CYAN}🚀 LLM Context Builder{Style.RESET_ALL}")
        click.echo(f"{Fore.BLUE}📂 Source: {source_path}{Style.RESET_ALL}")
    
    # Auto-detect project type
    detector = ProjectDetector(source_path)
    detected_type = detector.detect_project_type()
    
    if auto_detect and detected_type and not preset and not quiet:
        suggested_preset = detector.suggest_preset()
        if suggested_preset in PRESETS:
            print_success(f"Detected: {PRESETS[suggested_preset]['name']}")
            print_info(f"Suggestion: Use --preset {suggested_preset} for optimized settings")
    
    # Determine configuration
    config = {}
    if preset:
        config = PRESETS[preset].copy()
        if not quiet:
            print_success(f"Using preset: {config['name']}")
    else:
        # Use smart defaults based on detection
        suggested = detector.suggest_preset()
        if suggested in PRESETS:
            config = PRESETS[suggested].copy()
            if not quiet:
                print_info(f"Auto-applying {suggested} preset")
        else:
            config = PRESETS["minimal"].copy()  # Safe fallback
    
    # Override with command line options
    if max_size:
        config['max_file_size'] = max_size
    if include_ext:
        config['include_extensions'] = list(include_ext)
    if exclude_ext:
        config.setdefault('exclude_files', []).extend([f"*{ext}" for ext in exclude_ext])
    if exclude_folders:
        config.setdefault('exclude_folders', []).extend(exclude_folders)
    if exclude_files:
        config.setdefault('exclude_files', []).extend(exclude_files)
    
    # Generate output filename
    if output:
        output_file = Path(output)
    else:
        # Create project_export directory in current working directory
        export_dir = Path.cwd() / "project_export"
        export_dir.mkdir(exist_ok=True)
        
        # Generate filename based on project name
        project_name = source_path.name.lower().replace(' ', '_').replace('-', '_')
        if no_timestamp:
            filename = f"{project_name}_export.txt"
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{project_name}_{timestamp}.txt"
        
        output_file = export_dir / filename
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not quiet:
        print_info(f"Output: {output_file}")
    
    # Create exporter and run
    exporter = BaseExporter(
        source_dir=source_path,
        output_file=output_file,
        config=config
    )
    
    try:
        result = exporter.export()
        
        if not quiet:
            elapsed = time.time() - start_time
            print_stats(f"Files: {result['files_processed']} processed, {result['files_skipped']} skipped")
            
            if count_tokens and result['content']:
                tokens = estimate_tokens(result['content'])
                if tokens < 4000:
                    print_tokens(f"Tokens: ~{tokens:,} (fits in GPT-3.5 context)")
                elif tokens < 8000:
                    print_tokens(f"Tokens: ~{tokens:,} (fits in GPT-4 context)")
                elif tokens < 32000:
                    print_tokens(f"Tokens: ~{tokens:,} (fits in GPT-4-32k context)")
                elif tokens < 128000:
                    print_tokens(f"Tokens: ~{tokens:,} (fits in GPT-4-turbo context)")
                else:
                    print_warning(f"Tokens: ~{tokens:,} (exceeds most model limits)")
            
            print_success(f"Export completed in {elapsed:.1f}s")
            print_info(f"Ready for LLM context: {output_file}")
        else:
            # Quiet mode - just print the output file path
            click.echo(str(output_file))
            
    except Exception as e:
        print_error(f"Export failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()