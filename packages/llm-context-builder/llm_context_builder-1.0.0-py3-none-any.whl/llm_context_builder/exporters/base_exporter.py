#!/usr/bin/env python3
"""
Base Exporter - Core file combining logic optimized for LLM context
"""

import os
import fnmatch
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class BaseExporter:
    """Exports project files to a single text file optimized for LLM context"""
    
    def __init__(self, source_dir: Path, output_file: Path, config: Dict):
        self.source_dir = Path(source_dir)
        self.output_file = Path(output_file)
        self.config = config
        
        # Default exclusions (merged with config)
        self.default_excluded_extensions = [
            # Images
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp', '.tiff',
            # Videos
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v',
            # Audio
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
            # Archives
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.dmg', '.iso',
            # Executables
            '.exe', '.dll', '.so', '.dylib', '.app', '.deb', '.rpm',
            # Office documents (binary)
            '.doc', '.xls', '.ppt', '.docx', '.xlsx', '.pptx', '.pdf',
            # Other binary
            '.bin', '.dat', '.db', '.sqlite', '.sqlite3', '.pyc', '.pyo', '.class',
            # Font files
            '.ttf', '.otf', '.woff', '.woff2', '.eot',
            # Cache/temp
            '.cache', '.tmp', '.temp'
        ]
        
        self.default_excluded_folders = [
            # Version control
            '.git', '.svn', '.hg', '.bzr',
            # Build/cache directories  
            '__pycache__', 'node_modules', '.cache', 'build', 'dist', 'target',
            # Virtual environments
            'venv', 'env', '.venv', '.env', 'virtualenv',
            # Test/coverage
            'test_*', 'tests_*', '*_test', '*_tests', 'coverage', '.nyc_output', '.pytest_cache',
            # IDE/Editor directories
            '.vscode', '.idea', '.vs', '.sublime-project', '.sublime-workspace',
            # OS directories
            '.DS_Store', 'Thumbs.db', '$RECYCLE.BIN',
            # Project export directories
            'project_export', 'exports', 'combined_*',
            # Package/dependency directories
            'vendor', 'packages', 'bower_components',
            # Logs
            'logs', 'log'
        ]
        
        self.default_excluded_files = [
            # Log files
            '*.log', '*.logs',
            # Temporary files  
            '*.tmp', '*.temp', '*~', '.#*', '*.swp', '*.swo',
            # OS files
            '.DS_Store', 'Thumbs.db', 'desktop.ini',
            # Lock files
            '*.lock', 'package-lock.json', 'yarn.lock', 'Pipfile.lock', 'poetry.lock',
            # Environment files (may contain secrets)
            '.env', '.env.*', '*.env',
            # IDE files
            '*.sublime-project', '*.sublime-workspace',
            # Compiled files
            '*.min.js', '*.min.css', '*.bundle.js', '*.bundle.css',
            # This tool's files
            'export_project.py', 'llm_context_builder.py'
        ]
    
    def _should_exclude_folder(self, folder_name: str) -> bool:
        """Check if a folder should be excluded"""
        excluded_folders = self.config.get('exclude_folders', []) + self.default_excluded_folders
        
        for pattern in excluded_folders:
            if fnmatch.fnmatch(folder_name, pattern) or fnmatch.fnmatch(folder_name.lower(), pattern.lower()):
                return True
        return False
    
    def _should_exclude_file(self, file_path: Path) -> Tuple[bool, str]:
        """Check if a file should be excluded, return (should_exclude, reason)"""
        file_name = file_path.name
        file_ext = file_path.suffix.lower()
        
        # Check if we have explicit include extensions
        include_extensions = self.config.get('include_extensions')
        if include_extensions is not None:
            if file_ext not in [ext.lower() for ext in include_extensions]:
                return True, f"not in include list ({file_ext})"
        
        # Check extension exclusions
        excluded_extensions = self.config.get('exclude_extensions', []) + self.default_excluded_extensions
        if file_ext in [ext.lower() for ext in excluded_extensions]:
            return True, f"excluded extension ({file_ext})"
        
        # Check file pattern exclusions
        excluded_files = self.config.get('exclude_files', []) + self.default_excluded_files
        for pattern in excluded_files:
            if fnmatch.fnmatch(file_name, pattern) or fnmatch.fnmatch(file_name.lower(), pattern.lower()):
                return True, f"excluded pattern ({pattern})"
        
        return False, ""
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if a file is likely a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Try to read first 1KB
            return True
        except (UnicodeDecodeError, PermissionError):
            return False
    
    def _format_file_header(self, relative_path: Path, file_path: Path) -> str:
        """Create LLM-optimized file header"""
        file_size = file_path.stat().st_size
        return (
            f"\n{'='*80}\n"
            f"FILE: {relative_path}\n"
            f"PATH: {file_path}\n" 
            f"SIZE: {file_size:,} bytes\n"
            f"{'='*80}\n"
        )
    
    def _format_file_footer(self, relative_path: Path) -> str:
        """Create LLM-optimized file footer"""
        return f"\n{'='*80}\nEND: {relative_path}\n{'='*80}\n"
    
    def _read_file_content(self, file_path: Path, max_size: Optional[int] = None) -> str:
        """Read file content with size limiting"""
        try:
            file_size = file_path.stat().st_size
            
            # Check size limit
            if max_size and file_size > max_size:
                return f"[FILE TOO LARGE: {file_size:,} bytes > {max_size:,} bytes limit - showing first {max_size:,} bytes]\n\n"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if max_size:
                    content = f.read(max_size)
                    if file_size > max_size:
                        content += f"\n\n[... truncated {file_size - max_size:,} bytes ...]"
                else:
                    content = f.read()
                    
                return content
                
        except UnicodeDecodeError:
            return "[BINARY FILE - Cannot display content as text]"
        except PermissionError:
            return "[PERMISSION DENIED - Cannot read file]"
        except Exception as e:
            return f"[ERROR reading file: {str(e)}]"
    
    def export(self) -> Dict:
        """Export project files to combined text file"""
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory does not exist: {self.source_dir}")
        
        if not self.source_dir.is_dir():
            raise ValueError(f"Source path is not a directory: {self.source_dir}")
        
        files_processed = 0
        files_skipped = 0
        total_size = 0
        max_file_size = self.config.get('max_file_size', 1000000)  # 1MB default
        all_content = []
        
        # Create header
        header = self._create_header()
        all_content.append(header)
        
        try:
            # Walk through all files recursively
            for root, dirs, files in os.walk(self.source_dir):
                # Filter out excluded directories in-place
                dirs[:] = [d for d in dirs if not self._should_exclude_folder(d)]
                
                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.source_dir)
                    
                    # Skip output file if in same tree
                    try:
                        if file_path.samefile(self.output_file):
                            continue
                    except (OSError, FileNotFoundError):
                        pass
                    
                    # Check if file should be excluded
                    exclude_file, exclude_reason = self._should_exclude_file(file_path)
                    if exclude_file:
                        files_skipped += 1
                        continue
                    
                    try:
                        file_size = file_path.stat().st_size
                        
                        # Check file size limit
                        if file_size > max_file_size * 2:  # Skip very large files entirely
                            files_skipped += 1
                            continue
                        
                        # Check if file is readable as text
                        if not self._is_text_file(file_path):
                            files_skipped += 1
                            continue
                        
                        # Add file to output
                        all_content.append(self._format_file_header(relative_path, file_path))
                        content = self._read_file_content(file_path, max_file_size)
                        all_content.append(content)
                        
                        # Ensure content ends with newline
                        if not content.endswith('\n'):
                            all_content.append('\n')
                            
                        all_content.append(self._format_file_footer(relative_path))
                        
                        files_processed += 1
                        total_size += min(file_size, max_file_size)
                        
                    except Exception as e:
                        # Log error but continue
                        error_content = (
                            f"\n{'='*80}\n"
                            f"FILE: {relative_path}\n"
                            f"ERROR: {str(e)}\n"
                            f"{'='*80}\n"
                        )
                        all_content.append(error_content)
                        files_skipped += 1
            
            # Add summary
            summary = self._create_summary(files_processed, files_skipped, total_size)
            all_content.append(summary)
            
            # Write everything to output file
            combined_content = ''.join(all_content)
            with open(self.output_file, 'w', encoding='utf-8') as outf:
                outf.write(combined_content)
            
            return {
                'files_processed': files_processed,
                'files_skipped': files_skipped,
                'total_size': total_size,
                'output_file': str(self.output_file),
                'content': combined_content
            }
            
        except Exception as e:
            raise RuntimeError(f"Export failed: {e}")
    
    def _create_header(self) -> str:
        """Create LLM-optimized file header"""
        preset_name = self.config.get('name', 'Custom')
        return (
            f"{'='*100}\n"
            f"LLM CONTEXT EXPORT\n"
            f"{'='*100}\n"
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Source: {self.source_dir}\n"
            f"Preset: {preset_name}\n"
            f"Export Tool: llm-context-builder\n"
            f"{'='*100}\n\n"
            f"INSTRUCTIONS FOR LLM:\n"
            f"This file contains the complete source code and documentation for a project.\n"
            f"Each file is clearly marked with headers and footers.\n"
            f"Use this context to understand the project structure and help with development tasks.\n"
            f"{'='*100}\n"
        )
    
    def _create_summary(self, files_processed: int, files_skipped: int, total_size: int) -> str:
        """Create summary section"""
        return (
            f"\n\n{'='*100}\n"
            f"EXPORT SUMMARY\n"
            f"{'='*100}\n"
            f"Files processed: {files_processed:,}\n"
            f"Files skipped: {files_skipped:,}\n"
            f"Total content size: {total_size:,} bytes\n"
            f"Export completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Output file: {self.output_file}\n"
            f"{'='*100}\n"
        )