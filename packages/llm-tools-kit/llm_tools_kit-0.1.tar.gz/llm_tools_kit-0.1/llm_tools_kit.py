from pathlib import Path
import llm
from kit import Repository


class Kit(llm.Toolbox):
    """A toolbox for exploring codebases using kit functionality."""
    
    _repositories = {}  # Class-level shared state
    
    def __init__(self, repo_path: str = "."):
        """Initialize with a repository path (defaults to current directory)."""
        self.repo_path = Path(repo_path).resolve()  # Normalize path
    
    def _get_repo(self):
        """Get or create repository instance with shared state."""
        if str(self.repo_path) not in self._repositories:
            self._repositories[str(self.repo_path)] = Repository(str(self.repo_path))
        return self._repositories[str(self.repo_path)]
    
    def set_repository(self, repo_path: str):
        """Set the current repository path for subsequent operations."""
        self.repo_path = Path(repo_path).resolve()
        return f"Repository set to: {self.repo_path}"
    
    def get_current_repository(self):
        """Get the current repository path."""
        return f"Current repository: {self.repo_path}"
    
    def get_file_tree(self) -> str:
        """Get the file and directory structure of the repository."""
        try:
            return self._get_repo().get_file_tree()
        except Exception as e:
            return f"Error getting file tree: {str(e)}"
    
    def get_file_content(self, file_path: str) -> str:
        """Read and return the content of a specific file in the repository."""
        try:
            return self._get_repo().get_file_content(file_path)
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
        
    def search_text(self, query: str, file_pattern: str = "*.py") -> str:
        """Search for literal text or regex patterns within files."""
        try:
            repo = self._get_repo()
            results = repo.search_text(query, file_pattern=file_pattern)
            
            if not results:
                return f"No matches found for '{query}' in files matching '{file_pattern}'"
            
            return results
        except Exception as e:
            return f"Error searching for '{query}': {str(e)}"
    
    def extract_symbols(self, file_path: str = None) -> str:
        """Extract code symbols (functions, classes, variables, etc.) from files."""
        try:
            repo = self._get_repo()
            symbols = repo.extract_symbols(file_path)
            
            if not symbols:
                if file_path:
                    return f"No symbols found in file: {file_path}"
                else:
                    return "No symbols found in repository"
            return symbols
        except Exception as e:
            return f"Error extracting symbols: {str(e)}"
        
    def find_symbol_usages(self, symbol_name: str, symbol_type: str = None) -> str:
        """Find definitions and references of a specific symbol across the repository."""
        try:
            return self._get_repo().find_symbol_usages(symbol_name, symbol_type)
        except Exception as e:
            return f"Error finding symbol usages for '{symbol_name}': {str(e)}"

    def chunk_file_by_lines(self, file_path: str, max_lines: int = 50) -> str:
        """Chunk a file's content based on line count."""
        try:
            return self._get_repo().chunk_file_by_lines(file_path, max_lines)
        except Exception as e:
            return f"Error chunking file '{file_path}' by lines: {str(e)}"

    def chunk_file_by_symbols(self, file_path: str) -> str:
        """Chunk a file's content based on its top-level symbols (functions, classes)."""
        try:
            return self._get_repo().chunk_file_by_symbols(file_path)
        except Exception as e:
            return f"Error chunking file '{file_path}' by symbols: {str(e)}"

    def extract_context_around_line(self, file_path: str, line: int):
        """Extract the surrounding code context for a specific line number."""
        try:
            return self._get_repo().extract_context_around_line(file_path, line)
        except Exception as e:
            return f"Error extracting context around line {line} in '{file_path}': {str(e)}"



@llm.hookimpl
def register_tools(register):
    # Register with default current directory
    register(Kit, "Kit")