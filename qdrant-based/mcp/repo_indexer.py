import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class CodeChunk:
    """Represents a logical code chunk"""
    file_path: str
    chunk_id: str
    content: str
    chunk_type: str  # "function", "class", "import", "comment", "other"
    start_line: int
    end_line: int
    language: str  # "python", "javascript", "typescript", etc.


class RepoIndexer:
    """
    Intelligent code chunking for semantic search.
    Parses repo and splits into logical chunks (functions, classes, imports).
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.supported_extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".go": "go",
            ".java": "java",
        }
    
    def index_repo(self, max_files: int = 100) -> List[CodeChunk]:
        """
        Index all code files in repo and return chunks.
        
        Args:
            max_files: Limit to first N files (for MVP)
        
        Returns:
            List of CodeChunk objects
        """
        chunks = []
        file_count = 0
        
        for file_path in self.repo_path.rglob("*"):
            if file_count >= max_files:
                break
            
            # Skip hidden files, node_modules, __pycache__, etc.
            if self._should_skip(file_path):
                continue
            
            if file_path.is_file():
                ext = file_path.suffix
                if ext in self.supported_extensions:
                    language = self.supported_extensions[ext]
                    file_chunks = self._chunk_file(file_path, language)
                    chunks.extend(file_chunks)
                    file_count += 1
        
        print(f"Indexed {file_count} files, created {len(chunks)} chunks")
        return chunks
    
    def _should_skip(self, path: Path) -> bool:
        """Check if file/directory should be skipped"""
        skip_dirs = {
            "__pycache__", ".git", ".venv", "venv", "node_modules",
            ".vscode", ".idea", "dist", "build", ".next", ".pytest_cache"
        }
        skip_files = {".DS_Store", ".gitignore", ".env"}
        
        # Check directory parts
        for part in path.parts:
            if part in skip_dirs:
                return True
        
        # Check file name
        if path.name in skip_files:
            return True
        
        # Check hidden files
        if path.name.startswith("."):
            return True
        
        return False
    
    def _chunk_file(self, file_path: Path, language: str) -> List[CodeChunk]:
        """
        Parse file and extract logical chunks.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
        
        rel_path = file_path.relative_to(self.repo_path)
        
        if language == "python":
            return self._chunk_python(str(rel_path), content)
        elif language in ["javascript", "typescript"]:
            return self._chunk_javascript(str(rel_path), content)
        else:
            # Fallback: treat whole file as one chunk
            return [CodeChunk(
                file_path=str(rel_path),
                chunk_id=f"{rel_path}#0",
                content=content[:2000],  # Limit size
                chunk_type="file",
                start_line=1,
                end_line=len(content.split("\n")),
                language=language
            )]
    
    def _chunk_python(self, file_path: str, content: str) -> List[CodeChunk]:
        """Extract Python functions, classes, and imports."""
        chunks = []
        lines = content.split("\n")
        chunk_counter = 0
        
        # Extract imports block
        import_lines = []
        i = 0
        while i < len(lines) and (lines[i].startswith("import ") or 
                                  lines[i].startswith("from ") or
                                  lines[i].strip() == ""):
            if lines[i].strip():
                import_lines.append(lines[i])
            i += 1
        
        if import_lines:
            chunks.append(CodeChunk(
                file_path=file_path,
                chunk_id=f"{file_path}#imports",
                content="\n".join(import_lines),
                chunk_type="import",
                start_line=1,
                end_line=i,
                language="python"
            ))
        
        # Extract functions and classes
        i = i or 0
        while i < len(lines):
            line = lines[i]
            
            # Function definition
            if re.match(r"^def\s+\w+", line):
                chunk = self._extract_python_function(lines, i, file_path, chunk_counter)
                if chunk:
                    chunks.append(chunk)
                    chunk_counter += 1
                    i = chunk.end_line
                else:
                    i += 1
            
            # Class definition
            elif re.match(r"^class\s+\w+", line):
                chunk = self._extract_python_class(lines, i, file_path, chunk_counter)
                if chunk:
                    chunks.append(chunk)
                    chunk_counter += 1
                    i = chunk.end_line
                else:
                    i += 1
            else:
                i += 1
        
        return chunks
    
    def _extract_python_function(self, lines: List[str], start: int, 
                                 file_path: str, chunk_id: int) -> Optional[CodeChunk]:
        """Extract a Python function."""
        func_lines = [lines[start]]
        i = start + 1
        
        # Collect function body (indented lines)
        while i < len(lines):
            line = lines[i]
            if line.strip() == "":
                func_lines.append(line)
            elif line[0] not in (" ", "\t"):
                break
            else:
                func_lines.append(line)
            i += 1
        
        content = "\n".join(func_lines).strip()
        if len(content) > 10000:  # Limit chunk size
            content = content[:10000] + "..."
        
        return CodeChunk(
            file_path=file_path,
            chunk_id=f"{file_path}#func_{chunk_id}",
            content=content,
            chunk_type="function",
            start_line=start + 1,
            end_line=i,
            language="python"
        )
    
    def _extract_python_class(self, lines: List[str], start: int, 
                              file_path: str, chunk_id: int) -> Optional[CodeChunk]:
        """Extract a Python class."""
        class_lines = [lines[start]]
        i = start + 1
        
        # Collect class body
        while i < len(lines):
            line = lines[i]
            if line.strip() == "":
                class_lines.append(line)
            elif line[0] not in (" ", "\t"):
                break
            else:
                class_lines.append(line)
            i += 1
        
        content = "\n".join(class_lines).strip()
        if len(content) > 10000:
            content = content[:10000] + "..."
        
        return CodeChunk(
            file_path=file_path,
            chunk_id=f"{file_path}#class_{chunk_id}",
            content=content,
            chunk_type="class",
            start_line=start + 1,
            end_line=i,
            language="python"
        )
    
    def _chunk_javascript(self, file_path: str, content: str) -> List[CodeChunk]:
        """Extract JavaScript functions and classes."""
        chunks = []
        lines = content.split("\n")
        chunk_counter = 0
        
        # Extract imports block
        import_lines = []
        i = 0
        while i < len(lines) and (lines[i].startswith("import ") or 
                                  lines[i].startswith("export ") or
                                  lines[i].startswith("const ") or
                                  lines[i].strip() == ""):
            if lines[i].strip():
                import_lines.append(lines[i])
            i += 1
        
        if import_lines:
            chunks.append(CodeChunk(
                file_path=file_path,
                chunk_id=f"{file_path}#imports",
                content="\n".join(import_lines),
                chunk_type="import",
                start_line=1,
                end_line=i,
                language="javascript"
            ))
        
        # Extract functions
        pattern = r"^(async\s+)?(function\s+\w+|const\s+\w+\s*=|export\s+(?:function|const|class))"
        
        for j, line in enumerate(lines[i:], start=i):
            if re.match(pattern, line):
                chunk = self._extract_js_function(lines, j, file_path, chunk_counter)
                if chunk:
                    chunks.append(chunk)
                    chunk_counter += 1
        
        return chunks
    
    def _extract_js_function(self, lines: List[str], start: int, 
                             file_path: str, chunk_id: int) -> Optional[CodeChunk]:
        """Extract a JavaScript function."""
        func_lines = [lines[start]]
        i = start + 1
        brace_count = 0
        found_brace = False
        
        # Count braces to find function end
        for k, char in enumerate(lines[start]):
            if char == "{":
                brace_count += 1
                found_brace = True
            elif char == "}":
                brace_count -= 1
        
        if not found_brace:
            # Look for opening brace on next lines
            while i < len(lines) and "{" not in lines[i]:
                func_lines.append(lines[i])
                i += 1
            
            if i < len(lines):
                func_lines.append(lines[i])
                brace_count = 1
                i += 1
        
        # Collect until braces are balanced
        while i < len(lines) and brace_count > 0:
            line = lines[i]
            func_lines.append(line)
            brace_count += line.count("{") - line.count("}")
            i += 1
        
        content = "\n".join(func_lines).strip()
        if len(content) > 10000:
            content = content[:10000] + "..."
        
        return CodeChunk(
            file_path=file_path,
            chunk_id=f"{file_path}#func_{chunk_id}",
            content=content,
            chunk_type="function",
            start_line=start + 1,
            end_line=i,
            language="javascript"
        )
