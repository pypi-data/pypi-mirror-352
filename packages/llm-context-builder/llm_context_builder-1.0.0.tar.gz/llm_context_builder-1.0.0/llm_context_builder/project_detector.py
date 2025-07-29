#!/usr/bin/env python3
"""
Project Detector - Automatically detect project type and suggest optimal presets
"""

import json
from pathlib import Path
from typing import Optional, Dict, List


class ProjectDetector:
    """Detects project type based on files and directory structure"""
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.files = self._get_project_files()
        
    def _get_project_files(self) -> List[str]:
        """Get list of files in the project root and immediate subdirectories"""
        files = []
        try:
            # Get files in root
            for item in self.project_path.iterdir():
                if item.is_file():
                    files.append(item.name)
                elif item.is_dir() and not item.name.startswith('.'):
                    # Add directory name for structure detection
                    files.append(f"DIR:{item.name}")
                    # Check for important files in immediate subdirectories
                    try:
                        for subitem in item.iterdir():
                            if subitem.is_file() and subitem.name in [
                                'package.json', 'requirements.txt', 'Cargo.toml', 
                                'pubspec.yaml', 'pom.xml', 'build.gradle'
                            ]:
                                files.append(f"{item.name}/{subitem.name}")
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass
        return files
    
    def detect_project_type(self) -> Optional[str]:
        """Detect the most likely project type"""
        detectors = [
            self._detect_web_project,
            self._detect_python_project,
            self._detect_node_project,
            self._detect_mobile_project,
            self._detect_docs_project,
        ]
        
        for detector in detectors:
            result = detector()
            if result:
                return result
        
        return None
    
    def suggest_preset(self) -> str:
        """Suggest the best preset for this project"""
        project_type = self.detect_project_type()
        
        # Map detected types to presets
        type_to_preset = {
            'react': 'web',
            'vue': 'web', 
            'angular': 'web',
            'nextjs': 'web',
            'nuxt': 'web',
            'svelte': 'web',
            'web': 'web',
            'python': 'python',
            'django': 'python',
            'flask': 'python',
            'fastapi': 'python',
            'node': 'node',
            'express': 'node',
            'react-native': 'mobile',
            'flutter': 'mobile',
            'ionic': 'mobile',
            'docs': 'docs',
            'gatsby': 'docs',
            'hugo': 'docs',
            'jekyll': 'docs',
        }
        
        return type_to_preset.get(project_type, 'minimal')
    
    def _detect_web_project(self) -> Optional[str]:
        """Detect web framework projects"""
        
        # Check package.json for web frameworks
        package_json_path = self.project_path / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                dependencies = {}
                dependencies.update(package_data.get('dependencies', {}))
                dependencies.update(package_data.get('devDependencies', {}))
                
                # React projects
                if 'react' in dependencies:
                    if 'next' in dependencies or 'next' in package_data.get('name', ''):
                        return 'nextjs'
                    return 'react'
                
                # Vue projects
                if 'vue' in dependencies:
                    if 'nuxt' in dependencies:
                        return 'nuxt'
                    return 'vue'
                
                # Angular projects
                if '@angular/core' in dependencies:
                    return 'angular'
                
                # Svelte projects
                if 'svelte' in dependencies:
                    return 'svelte'
                
                # React Native
                if 'react-native' in dependencies:
                    return 'react-native'
                
                # Ionic
                if '@ionic/react' in dependencies or '@ionic/angular' in dependencies or '@ionic/vue' in dependencies:
                    return 'ionic'
                
                # Static site generators
                if 'gatsby' in dependencies:
                    return 'gatsby'
                
                # General web if has common web dependencies
                web_indicators = ['webpack', 'vite', 'rollup', 'parcel', 'typescript', 'sass', 'less']
                if any(dep in dependencies for dep in web_indicators):
                    return 'web'
                    
            except (json.JSONDecodeError, IOError):
                pass
        
        # Check for common web files
        web_files = [
            'index.html', 'index.htm', 'webpack.config.js', 'vite.config.js',
            'rollup.config.js', 'tsconfig.json', 'tailwind.config.js'
        ]
        
        if any(f in self.files for f in web_files):
            return 'web'
        
        # Check for web directories
        web_dirs = ['src', 'public', 'static', 'assets']
        if any(f"DIR:{d}" in self.files for d in web_dirs):
            # Additional check for common web file extensions
            extensions = ['.html', '.css', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte']
            for file_path in self.project_path.rglob('*'):
                if file_path.suffix in extensions:
                    return 'web'
        
        return None
    
    def _detect_python_project(self) -> Optional[str]:
        """Detect Python projects"""
        
        python_files = [
            'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile',
            'setup.cfg', 'tox.ini', 'pytest.ini', 'manage.py'
        ]
        
        if any(f in self.files for f in python_files):
            # Check for specific frameworks
            if 'manage.py' in self.files:
                return 'django'
            
            # Check requirements.txt content
            req_file = self.project_path / 'requirements.txt'
            if req_file.exists():
                try:
                    content = req_file.read_text(encoding='utf-8').lower()
                    if 'django' in content:
                        return 'django'
                    elif 'flask' in content:
                        return 'flask'
                    elif 'fastapi' in content:
                        return 'fastapi'
                except (IOError, UnicodeDecodeError):
                    pass
            
            return 'python'
        
        # Check for .py files in root
        if any(f.endswith('.py') for f in self.files):
            return 'python'
        
        return None
    
    def _detect_node_project(self) -> Optional[str]:
        """Detect Node.js backend projects"""
        
        if 'package.json' not in self.files:
            return None
        
        package_json_path = self.project_path / "package.json"
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            dependencies = {}
            dependencies.update(package_data.get('dependencies', {}))
            dependencies.update(package_data.get('devDependencies', {}))
            
            # Skip if it's a frontend project
            frontend_indicators = ['react', 'vue', '@angular/core', 'svelte']
            if any(dep in dependencies for dep in frontend_indicators):
                return None
            
            # Node.js backend indicators
            backend_indicators = [
                'express', 'koa', 'fastify', 'nest', '@nestjs/core',
                'apollo-server', 'graphql', 'mongoose', 'sequelize',
                'typeorm', 'prisma', 'nodemon'
            ]
            
            if any(dep in dependencies for dep in backend_indicators):
                if 'express' in dependencies:
                    return 'express'
                return 'node'
                
        except (json.JSONDecodeError, IOError):
            pass
        
        return None
    
    def _detect_mobile_project(self) -> Optional[str]:
        """Detect mobile app projects"""
        
        # Flutter
        if 'pubspec.yaml' in self.files:
            return 'flutter'
        
        # React Native
        if 'package.json' in self.files:
            package_json_path = self.project_path / "package.json"
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                dependencies = package_data.get('dependencies', {})
                if 'react-native' in dependencies:
                    return 'react-native'
                    
            except (json.JSONDecodeError, IOError):
                pass
        
        # iOS/Android native indicators
        mobile_files = ['Podfile', 'build.gradle', 'AndroidManifest.xml']
        mobile_dirs = ['ios', 'android', 'DIR:ios', 'DIR:android']
        
        if any(f in self.files for f in mobile_files + mobile_dirs):
            return 'mobile'
        
        return None
    
    def _detect_docs_project(self) -> Optional[str]:
        """Detect documentation projects"""
        
        # Static site generators
        docs_files = [
            '_config.yml',  # Jekyll
            'config.toml', 'config.yaml',  # Hugo
            'gatsby-config.js',  # Gatsby
            'mkdocs.yml',  # MkDocs
            'docusaurus.config.js',  # Docusaurus
            'vuepress.config.js',  # VuePress
            'gitbook.json',  # GitBook
            'book.toml',  # mdBook
        ]
        
        if any(f in self.files for f in docs_files):
            if '_config.yml' in self.files:
                return 'jekyll'
            elif 'gatsby-config.js' in self.files:
                return 'gatsby'
            elif any(f in self.files for f in ['config.toml', 'config.yaml']):
                return 'hugo'
            return 'docs'
        
        # Check for docs directories
        docs_dirs = ['docs', 'documentation', 'wiki', '_posts', 'content']
        if any(f"DIR:{d}" in self.files for d in docs_dirs):
            return 'docs'
        
        # High ratio of markdown files
        md_files = [f for f in self.files if f.endswith('.md')]
        if len(md_files) >= 3:  # At least 3 markdown files
            return 'docs'
        
        return None
    
    def get_project_info(self) -> Dict:
        """Get comprehensive project information"""
        return {
            'path': str(self.project_path),
            'name': self.project_path.name,
            'detected_type': self.detect_project_type(),
            'suggested_preset': self.suggest_preset(),
            'files_found': len(self.files),
            'has_git': 'DIR:.git' in self.files,
            'key_files': [f for f in self.files if not f.startswith('DIR:')][:10]  # First 10 files
        }