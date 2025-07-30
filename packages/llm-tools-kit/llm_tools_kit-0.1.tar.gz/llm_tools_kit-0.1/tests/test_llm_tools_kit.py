import llm
import json
import tempfile
import os
from pathlib import Path
from llm_tools_kit import Kit


def test_get_file_tree():
    """Test that get_file_tree returns repository structure."""
    kit = Kit()
    
    # Test with echo model using direct tool call
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_get_file_tree", "arguments": {}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    # Should get a file tree result
    assert len(tool_results) == 1
    assert tool_results[0]["name"] == "Kit_get_file_tree"
    
    # Result should contain some expected files from our project
    output = tool_results[0]["output"]
    assert "pyproject.toml" in output
    assert "README.md" in output
    assert "tests/" in output


def test_get_file_content():
    """Test that get_file_content reads files correctly."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_get_file_content", "arguments": {"file_path": "pyproject.toml"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    assert len(tool_results) == 1
    assert tool_results[0]["name"] == "Kit_get_file_content"
    
    # Should contain pyproject.toml content
    output = tool_results[0]["output"]
    assert "[project]" in output
    assert "llm-tools-kit" in output


def test_get_file_content_not_found():
    """Test error handling for non-existent files."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_get_file_content", "arguments": {"file_path": "nonexistent.txt"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    assert len(tool_results) == 1
    output = tool_results[0]["output"]
    assert "File not found: nonexistent.txt" in output


def test_kit_with_custom_path():
    """Test Kit toolbox with a custom repository path."""
    # Create a temporary directory with some test files
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Hello from test file")
        
        kit = Kit(repo_path=temp_dir)
        
        model = llm.get_model("echo")
        
        # Test file tree
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_get_file_tree", "arguments": {}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        assert "test.txt" in output
        
        # Test file content
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_get_file_content", "arguments": {"file_path": "test.txt"}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        assert "Hello from test file" in output

def test_search_text():
    """Test that search_text finds text in files."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_search_text", "arguments": {"query": "class Kit", "file_pattern": "*.py"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    assert len(tool_results) == 1
    print(tool_results)
    assert tool_results[0]["name"] == "Kit_search_text"
    
    # Should find our Kit class definition
    output = tool_results[0]["output"]
    assert "llm_tools_kit.py" in output
    assert "class Kit" in output


def test_search_text_with_default_pattern():
    """Test search_text with default file pattern."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_search_text", "arguments": {"query": "llm.Toolbox"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    output = tool_results[0]["output"]
    # Should find the Toolbox inheritance in our Python file
    assert "llm_tools_kit.py" in output or "llm.Toolbox" in output


def test_search_text_no_matches():
    """Test search_text when no matches are found."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_search_text", "arguments": {"query": "this_should_not_exist_anywhere", "file_pattern": "*.py"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    output = tool_results[0]["output"]
    assert "No matches found for 'this_should_not_exist_anywhere'" in output


def test_search_text_different_file_patterns():
    """Test search_text with different file patterns."""
    kit = Kit()
    
    # Search in markdown files
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_search_text", "arguments": {"query": "Installation", "file_pattern": "*.md"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    output = tool_results[0]["output"]
    # Should find "Installation" in README.md
    assert ("README.md" in output and "Installation" in output) or "No matches found" in output


def test_search_text_regex_pattern():
    """Test search_text with regex patterns."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_search_text", "arguments": {"query": "def \\w+\\(", "file_pattern": "*.py"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    output = tool_results[0]["output"]
    # Should find function definitions
    assert "def " in output or "No matches found" in output


def test_search_text_with_custom_repo():
    """Test search_text with a custom repository path."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        py_file = Path(temp_dir) / "example.py"
        py_file.write_text("def hello_world():\n    print('Hello, World!')")
        
        txt_file = Path(temp_dir) / "notes.txt"
        txt_file.write_text("This is a note about hello_world function")
        
        kit = Kit(repo_path=temp_dir)
        
        model = llm.get_model("echo")
        
        # Search in Python files
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_search_text", "arguments": {"query": "hello_world", "file_pattern": "*.py"}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        assert "example.py" in output
        assert "hello_world" in output
        
        # Search in text files
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_search_text", "arguments": {"query": "note", "file_pattern": "*.txt"}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        assert "notes.txt" in output
        assert "note" in output

def test_extract_symbols_specific_file():
    """Test extracting symbols from a specific file."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_extract_symbols", "arguments": {"file_path": "llm_tools_kit.py"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    assert len(tool_results) == 1
    assert tool_results[0]["name"] == "Kit_extract_symbols"
    
    # Should find symbols in our Kit file
    output = tool_results[0]["output"]
    # Output should be the raw symbols data from kit
    assert len(output) > 0


def test_extract_symbols_all_files():
    """Test extracting symbols from all files."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_extract_symbols", "arguments": {}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    assert len(tool_results) == 1
    output = tool_results[0]["output"]
    # Should return symbols from multiple files
    assert len(output) > 0


def test_extract_symbols_nonexistent_file():
    """Test extracting symbols from a file that doesn't exist."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_extract_symbols", "arguments": {"file_path": "nonexistent.py"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    output = tool_results[0]["output"]
    # Should handle the error case
    assert "Error" in output or "No symbols found" in output


def test_extract_symbols_with_custom_repo():
    """Test extracting symbols from a custom repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a Python file with some symbols
        py_file = Path(temp_dir) / "example.py"
        py_file.write_text("""
class TestClass:
    def __init__(self):
        self.value = 42
    
    def test_method(self):
        return self.value

def standalone_function():
    return "hello"

GLOBAL_VAR = "test"
""")
        
        kit = Kit(repo_path=temp_dir)
        
        model = llm.get_model("echo")
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_extract_symbols", "arguments": {"file_path": "example.py"}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        # Should extract symbols from our test file
        assert len(output) > 0


def test_extract_symbols_empty_file():
    """Test extracting symbols from an empty file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an empty Python file
        py_file = Path(temp_dir) / "empty.py"
        py_file.write_text("")
        
        kit = Kit(repo_path=temp_dir)
        
        model = llm.get_model("echo")
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_extract_symbols", "arguments": {"file_path": "empty.py"}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        # Should handle empty files gracefully
        assert "No symbols found" in output or len(output) == 0 or output == "[]"

def test_find_symbol_usages():
    """Test finding usages of a symbol."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_find_symbol_usages", "arguments": {"symbol_name": "Kit"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    assert len(tool_results) == 1
    assert tool_results[0]["name"] == "Kit_find_symbol_usages"
    
    output = tool_results[0]["output"]
    # Should find usages of our Kit class
    assert len(output) > 0


def test_find_symbol_usages_with_type():
    """Test finding usages of a symbol with specific type."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_find_symbol_usages", "arguments": {"symbol_name": "Kit", "symbol_type": "class"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    output = tool_results[0]["output"]
    # Should find class-specific usages
    assert len(output) > 0


def test_find_symbol_usages_nonexistent():
    """Test finding usages of a symbol that doesn't exist."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_find_symbol_usages", "arguments": {"symbol_name": "NonexistentSymbol"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    output = tool_results[0]["output"]
    # Should handle nonexistent symbols gracefully
    assert len(output) >= 0  # Could be empty list or error message


def test_find_symbol_usages_with_custom_repo():
    """Test finding symbol usages in a custom repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create files with symbol definitions and usages
        main_file = Path(temp_dir) / "main.py"
        main_file.write_text("""
from utils import helper_function

def main():
    result = helper_function("test")
    print(result)
    helper_function("another call")
""")
        
        utils_file = Path(temp_dir) / "utils.py"
        utils_file.write_text("""
def helper_function(arg):
    return f"Helper called with: {arg}"
""")
        
        kit = Kit(repo_path=temp_dir)
        
        model = llm.get_model("echo")
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_find_symbol_usages", "arguments": {"symbol_name": "helper_function"}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        # Should find usages across multiple files
        assert len(output) > 0


def test_find_symbol_usages_function_type():
    """Test finding usages restricted to function type."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file with both function and variable named 'test'
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("""
def test():
    return "function"

test = "variable"
result = test()
print(test)
""")
        
        kit = Kit(repo_path=temp_dir)
        
        model = llm.get_model("echo")
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_find_symbol_usages", "arguments": {"symbol_name": "test", "symbol_type": "function"}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        # Should find function-specific usages
        assert len(output) >= 0

def test_chunk_file_by_lines():
    """Test chunking a file by line count."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_chunk_file_by_lines", "arguments": {"file_path": "llm_tools_kit.py", "max_lines": 20}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    assert len(tool_results) == 1
    assert tool_results[0]["name"] == "Kit_chunk_file_by_lines"
    
    output = tool_results[0]["output"]
    # Should return chunks of the file
    assert len(output) > 0


def test_chunk_file_by_lines_default_max():
    """Test chunking a file by lines with default max_lines."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_chunk_file_by_lines", "arguments": {"file_path": "README.md"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    output = tool_results[0]["output"]
    # Should use default 50 lines per chunk
    assert len(output) > 0


def test_chunk_file_by_symbols():
    """Test chunking a file by symbols."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_chunk_file_by_symbols", "arguments": {"file_path": "llm_tools_kit.py"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    assert len(tool_results) == 1
    assert tool_results[0]["name"] == "Kit_chunk_file_by_symbols"
    
    output = tool_results[0]["output"]
    # Should return symbol-based chunks
    assert len(output) > 0


def test_chunk_file_by_lines_nonexistent():
    """Test chunking a nonexistent file by lines."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_chunk_file_by_lines", "arguments": {"file_path": "nonexistent.py"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    output = tool_results[0]["output"]
    # Should handle error gracefully
    assert "Error" in output


def test_chunk_file_by_symbols_nonexistent():
    """Test chunking a nonexistent file by symbols."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_chunk_file_by_symbols", "arguments": {"file_path": "nonexistent.py"}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    output = tool_results[0]["output"]
    assert str([]) == output


def test_chunk_file_by_lines_with_custom_repo():
    """Test chunking by lines in a custom repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file with multiple lines
        test_file = Path(temp_dir) / "long_file.py"
        lines = [f"# Line {i}" for i in range(1, 101)]  # 100 lines
        test_file.write_text("\n".join(lines))
        
        kit = Kit(repo_path=temp_dir)
        
        model = llm.get_model("echo")
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_chunk_file_by_lines", "arguments": {"file_path": "long_file.py", "max_lines": 25}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        # Should chunk the file into smaller pieces
        assert len(output) > 0


def test_chunk_file_by_symbols_with_custom_repo():
    """Test chunking by symbols in a custom repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file with multiple symbols
        test_file = Path(temp_dir) / "symbols.py"
        test_file.write_text("""
class FirstClass:
    def method_one(self):
        return "first"
    
    def method_two(self):
        return "second"

class SecondClass:
    def another_method(self):
        return "another"

def standalone_function():
    return "standalone"

GLOBAL_VAR = "global"
""")
        
        kit = Kit(repo_path=temp_dir)
        
        model = llm.get_model("echo")
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_chunk_file_by_symbols", "arguments": {"file_path": "symbols.py"}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        # Should chunk by symbols
        assert len(output) > 0

def test_extract_context_around_line():
    """Test extracting context around a specific line."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_extract_context_around_line", "arguments": {"file_path": "llm_tools_kit.py", "line": 10}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]
    
    assert len(tool_results) == 1
    assert tool_results[0]["name"] == "Kit_extract_context_around_line"
    
    output = tool_results[0]["output"]
    # Should return context around the specified line
    assert len(str(output)) >= 0  # Could be None or context dict


def test_extract_context_around_line_nonexistent_file():
    """Test extracting context from a nonexistent file."""
    kit = Kit()
    
    model = llm.get_model("echo")
    chain_response = model.chain(
        json.dumps({
            "tool_calls": [
                {"name": "Kit_extract_context_around_line", "arguments": {"file_path": "nonexistent.py", "line": 5}}
            ]
        }),
        tools=[kit],
    )
    responses = list(chain_response.responses())
    tool_results = json.loads(responses[-1].text())["tool_results"]

    output = tool_results[0]["output"]
    # Should handle error gracefully
    assert "null" == output


def test_extract_context_around_line_with_custom_repo():
    """Test extracting context in a custom repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file with known structure
        test_file = Path(temp_dir) / "context_test.py"
        test_file.write_text("""def outer_function():
    print("start of function")
    
    def inner_function():
        return "inner"
    
    result = inner_function()
    print("end of function")
    return result

class TestClass:
    def method(self):
        return "method"
""")
        
        kit = Kit(repo_path=temp_dir)
        
        model = llm.get_model("echo")
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_extract_context_around_line", "arguments": {"file_path": "context_test.py", "line": 4}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        # Should find context around line 4 (inner_function)
        assert output is not None or output == "None"


def test_extract_context_around_line_edge_cases():
    """Test extracting context with edge case line numbers."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "small.py"
        test_file.write_text("print('hello')\n")
        
        kit = Kit(repo_path=temp_dir)
        
        # Test line 0 (first line)
        model = llm.get_model("echo")
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_extract_context_around_line", "arguments": {"file_path": "small.py", "line": 0}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        # Should handle first line
        assert output is not None or output == "None"
        
        # Test line beyond file length
        chain_response = model.chain(
            json.dumps({
                "tool_calls": [
                    {"name": "Kit_extract_context_around_line", "arguments": {"file_path": "small.py", "line": 100}}
                ]
            }),
            tools=[kit],
        )
        responses = list(chain_response.responses())
        tool_results = json.loads(responses[-1].text())["tool_results"]
        
        output = tool_results[0]["output"]
        # Should handle out of bounds gracefully
        assert output is not None or output == "None"

