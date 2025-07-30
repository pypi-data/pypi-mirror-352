import os
import sys
import logging
from typing import List, Optional, Dict
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import urllib
import json

from leanclient import LeanLSPClient, DocumentContentChange

from mcp.server.fastmcp import Context, FastMCP

from lean_lsp_mcp.instructions import INSTRUCTIONS
from lean_lsp_mcp.utils import (
    OutputCapture,
    StdoutToStderr,
    extract_range,
    find_start_position,
    format_diagnostics,
    format_goal,
)


# Configure logging to stderr instead of stdout to avoid interfering with LSP JSON communication
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

logger = logging.getLogger("lean-lsp-mcp")


# Lean project path management
LEAN_PROJECT_PATH = os.environ.get("LEAN_PROJECT_PATH", "").strip()
cwd = os.getcwd().strip()  # Strip necessary?
if not LEAN_PROJECT_PATH:
    logger.error("Please set the LEAN_PROJECT_PATH environment variable")
    sys.exit(1)


# Server and context
@dataclass
class AppContext:
    client: LeanLSPClient
    file_content_hashes: Dict[str, str]


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    with StdoutToStderr():
        try:
            client = LeanLSPClient(
                LEAN_PROJECT_PATH, initial_build=True, print_warnings=False
            )
            logger.info(f"Connected to Lean project at {LEAN_PROJECT_PATH}")
        except Exception as e:
            client = LeanLSPClient(
                LEAN_PROJECT_PATH, initial_build=False, print_warnings=False
            )
            logger.error(f"Could not do initial build, error: {e}")
    try:
        context = AppContext(client=client, file_content_hashes={})
        yield context
    finally:
        logger.info("Closing Lean LSP client")
        context.client.close()


mcp = FastMCP(
    name="Lean LSP",
    instructions=INSTRUCTIONS,
    dependencies=["leanclient"],
    lifespan=app_lifespan,
    env_vars={
        "LEAN_PROJECT_PATH": {
            "description": "Path to the Lean project root",
            "required": True,
        }
    },
)


# File operations
def get_relative_file_path(file_path: str) -> Optional[str]:
    """Convert path relative to project path.

    Args:
        file_path (str): File path.

    Returns:
        str: Relative file path.
    """
    # Check if absolute path
    if os.path.exists(file_path):
        return os.path.relpath(file_path, LEAN_PROJECT_PATH)

    # Check if relative to project path
    path = os.path.join(LEAN_PROJECT_PATH, file_path)
    if os.path.exists(path):
        return os.path.relpath(path, LEAN_PROJECT_PATH)

    # Check if relative to CWD
    path = os.path.join(cwd, file_path)
    if os.path.exists(path):
        return os.path.relpath(path, LEAN_PROJECT_PATH)

    return None


def get_file_contents(rel_path: str) -> str:
    with open(os.path.join(LEAN_PROJECT_PATH, rel_path), "r") as f:
        data = f.read()
    return data


def update_file(ctx: Context, rel_path: str) -> str:
    """Update the file contents in the context.
    Args:
        ctx (Context): Context object.
        rel_path (str): Relative file path.

    Returns:
        str: Updated file contents.
    """
    # Get file contents and hash
    file_content = get_file_contents(rel_path)
    hashed_file = hash(file_content)

    # Check if file_contents have changed
    file_content_hashes: Dict[str, str] = (
        ctx.request_context.lifespan_context.file_content_hashes
    )
    if rel_path not in file_content_hashes:
        file_content_hashes[rel_path] = hashed_file
        return file_content

    elif hashed_file == file_content_hashes[rel_path]:
        return file_content

    # Update file_contents
    file_content_hashes[rel_path] = hashed_file

    # Reload file in LSP
    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    client.close_files([rel_path])
    return file_content


# Project level tools
@mcp.tool("lean_build")
def lsp_build(ctx: Context) -> str:
    """Build the Lean project and restart the LSP Server.

    Use only when necessary (e.g. imports).

    Returns:
        str: Build output or error message.
    """
    try:
        client: LeanLSPClient = ctx.request_context.lifespan_context.client
        client.close()

        with OutputCapture() as output:
            ctx.request_context.lifespan_context.client = LeanLSPClient(
                os.environ["LEAN_PROJECT_PATH"],
                initial_build=True,
                print_warnings=False,
            )
        build_output = output.get_output()
    except Exception as e:
        return f"Error during build:\n{str(e)}\n{build_output}"
    return build_output


# File level tools
@mcp.tool("lean_file_contents")
def file_contents(ctx: Context, file_path: str, annotate_lines: bool = True) -> str:
    """Get the text contents of a Lean file.

    IMPORTANT! Look up the file_contents for the currently open file including line number annotations.
    Use this during the proof process to keep updated on the line numbers and the current state of the file.

    Args:
        file_path (str): Absolute path to the Lean file.
        annotate_lines (bool, optional): Annotate lines with line numbers. Defaults to False.

    Returns:
        str: Text contents of the Lean file or None if file does not exist.
    """
    rel_path = get_relative_file_path(file_path)
    if not rel_path:
        return "No valid lean file found."

    data = get_file_contents(rel_path)

    if annotate_lines:
        data = data.split("\n")
        max_digits = len(str(len(data)))
        annotated = ""
        for i, line in enumerate(data):
            annotated += f"{i + 1}{' ' * (max_digits - len(str(i + 1)))}: {line}\n"
        return annotated
    else:
        return data


@mcp.tool("lean_diagnostic_messages")
def diagnostic_messages(ctx: Context, file_path: str) -> List[str] | str:
    """Get all diagnostic messages for a Lean file.

    Attention:
        "no goals to be solved" indicates some code needs to be removed. Keep going!

    Args:
        file_path (str): Absolute path to the Lean file.

    Returns:
        List[str] | str: Diagnostic messages or error message.
    """
    rel_path = get_relative_file_path(file_path)
    if not rel_path:
        return "No valid lean file found."

    update_file(ctx, rel_path)

    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    diagnostics = client.get_diagnostics(rel_path)
    return format_diagnostics(diagnostics)


@mcp.tool("lean_goal")
def goal(ctx: Context, file_path: str, line: int, column: Optional[int] = None) -> str:
    """Get the proof goals at a specific location or line in a Lean file.

    VERY USEFUL AND CHEAP! This is your main tool to understand the proof state and its evolution!!
    Use this multiple times after every edit to the file!

    Solved proof state returns "no goals".

    Args:
        file_path (str): Absolute path to the Lean file.
        line (int): Line number (1-indexed)
        column (int, optional): Column number (1-indexed). Defaults to None => Both before and after the line.

    Returns:
        str: Goal at the specified location or error message.
    """
    rel_path = get_relative_file_path(file_path)
    if not rel_path:
        return "No valid lean file found."

    content = update_file(ctx, rel_path)
    client: LeanLSPClient = ctx.request_context.lifespan_context.client

    if column is None:
        lines = content.splitlines()
        if line < 1 or line > len(lines):
            return "Line number out of range. Try again?"
        column_end = len(lines[line - 1])
        column_start = next(
            (i for i, c in enumerate(lines[line - 1]) if not c.isspace()), 0
        )
        goal_start = client.get_goal(rel_path, line - 1, column_start)
        goal_end = client.get_goal(rel_path, line - 1, column_end)

        if goal_start is None and goal_end is None:
            return "No goals found on line. Try another position?"

        start_text = format_goal(goal_start, "No goal found at the start of the line.")
        end_text = format_goal(goal_end, "No goal found at the end of the line.")
        if start_text == end_text:
            return start_text
        return f"Before:\n{start_text}\nAfter:\n{end_text}"

    else:
        goal = client.get_goal(rel_path, line - 1, column - 1)
        return format_goal(goal, "Not a valid goal position. Try again?")


@mcp.tool("lean_term_goal")
def term_goal(
    ctx: Context, file_path: str, line: int, column: Optional[int] = None
) -> str:
    """Get the term goal at a specific location in a Lean file.

    Use this to get a better understanding of the proof state.

    Args:
        file_path (str): Absolute path to the Lean file.
        line (int): Line number (1-indexed)
        column (int, optional): Column number (1-indexed). Defaults to None => end of line.

    Returns:
        str: Term goal at the specified location or error message.
    """
    rel_path = get_relative_file_path(file_path)
    if not rel_path:
        return "No valid lean file found."

    content = update_file(ctx, rel_path)
    if column is None:
        column = len(content.splitlines()[line - 1])

    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    term_goal = client.get_term_goal(rel_path, line - 1, column - 1)
    if term_goal is None:
        return "Not a valid term goal position. Try again?"
    rendered = term_goal.get("goal", None)
    if rendered is not None:
        rendered = rendered.replace("```lean\n", "").replace("\n```", "")
    return rendered


@mcp.tool("lean_hover_info")
def hover(ctx: Context, file_path: str, line: int, column: int) -> str:
    """Get the hover information at a specific location in a Lean file.

    Hover information provides documentation about any lean syntax, variables, functions, etc. in your code.

    Args:
        file_path (str): Absolute path to the Lean file.
        line (int): Line number (1-indexed)
        column (int): Column number (1-indexed). Make sure to use the start or within the term, not the end.

    Returns:
        str: Hover information at the specified location or error message.
    """
    rel_path = get_relative_file_path(file_path)
    if not rel_path:
        return "No valid lean file found."

    file_content = update_file(ctx, rel_path)
    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    hover_info = client.get_hover(rel_path, line - 1, column - 1)
    if hover_info is None:
        return "No hover information available. Try another position?"

    # Get the symbol and the hover information
    h_range = hover_info.get("range")
    symbol = extract_range(file_content, h_range)
    info = hover_info["contents"].get("value", "No hover information available.")
    info = info.replace("```lean\n", "").replace("\n```", "").strip()
    return f"Hover info `{symbol}`:\n{info}"


@mcp.tool("lean_proofs_complete")
def proofs_complete(ctx: Context, file_path: str) -> str:
    """Always check if all proofs in the file are complete in the end.

    Attention:
        "no goals to be solved" indicates code needs to be removed.
        Warnings (e.g. linter) indicate an unfinished proof.
        Keep going!

    Args:
        file_path (str): Absolute path to the Lean file.

    Returns:
        str: Message indicating if the proofs are complete or not.
    """
    rel_path = get_relative_file_path(file_path)
    if not rel_path:
        return "No valid lean file found."

    update_file(ctx, rel_path)

    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    diagnostics = client.get_diagnostics(rel_path)

    if diagnostics is None or len(diagnostics) > 0:
        return "Proof not complete!\n" + "\n".join(format_diagnostics(diagnostics))

    return "All proofs are complete!"


@mcp.tool("lean_completions")
def completions(
    ctx: Context, file_path: str, line: int, column: int, max_completions: int = 100
) -> List[str] | str:
    """Find possible code completions at a location in a Lean file.

    Check available identifiers and imports:
    - Dot Completion: Displays relevant identifiers after typing a dot (e.g., `Nat.`, `x.`, or `.`).
    - Identifier Completion: Suggests matching identifiers after typing part of a name.
    - Import Completion: Lists importable files after typing import at the beginning of a file.

    Use this on incomplete lines/statements to get suggestions for completing the code.

    Args:
        file_path (str): Absolute path to the Lean file.
        line (int): Line number (1-indexed)
        column (int): Column number (1-indexed).
        max_completions (int, optional): Maximum number of completions to return. Defaults to 100.

    Returns:
        List[str] | str: List of possible completions or error message.
    """
    rel_path = get_relative_file_path(file_path)
    if not rel_path:
        return "No valid lean file found."
    update_file(ctx, rel_path)

    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    completions = client.get_completions(rel_path, line - 1, column - 1)

    formatted = []
    for completion in completions:
        label = completion.get("label", None)
        if label is not None:
            formatted.append(label)

    if not formatted:
        return "No completions available. Try another position?"

    if len(formatted) > max_completions:
        formatted = formatted[:max_completions] + [
            f"{len(formatted) - max_completions} more, start typing and check again..."
        ]
    return formatted


@mcp.tool("lean_declaration_file")
def declaration_file(ctx: Context, file_path: str, symbol: str) -> str:
    """Get the file contents where a symbol/lemma/class/structure/... is declared.

    Note:
        Symbol has to be in the file already. Add it first if necessary.
        Lean files can be large, use `lean_hover_info` before this tool.

    Args:
        file_path (str): Absolute path to the Lean file.
        symbol (str): Symbol to look up the declaration for. Case sensitive!

    Returns:
        str: Contents of the file where the symbol is declared or error message.
    """
    rel_path = get_relative_file_path(file_path)
    if not rel_path:
        return "No valid lean file found."
    orig_file_content = update_file(ctx, rel_path)

    # Find the first occurence of the symbol (line and column) in the file,
    position = find_start_position(orig_file_content, symbol)
    if not position:
        return f"Symbol `{symbol}` (case sensitive) not found in file `{rel_path}`. Add it first, then try again."

    client: LeanLSPClient = ctx.request_context.lifespan_context.client
    declaration = client.get_declarations(
        rel_path, position["line"], position["column"]
    )

    if len(declaration) == 0:
        return f"No declaration available for `{symbol}`."

    # Load the declaration file
    declaration = declaration[0]
    uri = declaration.get("targetUri")
    if not uri:
        uri = declaration.get("uri")

    abs_path = client._uri_to_abs(uri)
    if not os.path.exists(abs_path):
        return f"Could not open declaration file `{abs_path}` for `{symbol}`."

    with open(abs_path, "r") as f:
        file_content = f.read()

    return f"Declaration of `{symbol}`:\n{file_content}"


@mcp.tool("lean_multi_attempt")
def multi_attempt(
    ctx: Context, file_path: str, line: int, snippets: List[str]
) -> List[str] | str:
    """Attempt multiple lean code snippets and return goal state and diagnostics for each snippet.

    This tool is useful to screen different tactics/approaches to help pick the most promising one.
    Use this in your diagnostic process.
    A new line is inserted at the specified line number and each attempt is tried before resetting the line.

    Note:
        Each snippet has to include the full line including correct initial indentation!
        Only single line snippets are supported!

    Args:
        file_path (str): Absolute path to the Lean file.
        line (int): Line number (1-indexed) to attempt.
        snippets (list[str]): List of snippets to try on the line. 3+ snippets are recommended.

    Returns:
        List[str] | str: Diagnostics and goal state for each snippet or error message.
    """
    rel_path = get_relative_file_path(file_path)
    if not rel_path:
        return "No valid lean file found."
    update_file(ctx, rel_path)
    client: LeanLSPClient = ctx.request_context.lifespan_context.client

    client.open_file(rel_path)

    results = []
    snippets[0] += "\n"  # Extra newline for the first snippet
    for snippet in snippets:
        # Create a DocumentContentChange for the snippet
        change = DocumentContentChange(
            snippet + "\n",
            [line - 1, 0],
            [line, 0],
        )
        # Apply the change to the file, capture diagnostics and goal state
        diag = client.update_file(rel_path, [change])
        formatted_diag = "\n".join(format_diagnostics(diag, select_line=line - 1))
        goal = client.get_goal(rel_path, line - 1, len(snippet))
        formatted_goal = format_goal(goal, "Missing goal")
        results.append(f"{snippet}:\n {formatted_goal}\n\n{formatted_diag}")

    # Make sure it's clean after the attempts
    client.close_files([rel_path])
    return results


@mcp.tool("lean_leansearch")
def leansearch(ctx: Context, query: str, max_results: int = 5) -> List[Dict] | str:
    """Search for Lean theorems, definitions, and tactics using leansearch.net API.

    Args:
        query (str): Natural language search query
        max_results (int, optional): Max results. Defaults to 5.

    Returns:
        List[Dict] | str: List of search results or error message
    """
    try:
        headers = {"User-Agent": "lean-lsp-mcp/0.1", "Content-Type": "application/json"}
        payload = json.dumps(
            {"num_results": str(max_results), "query": [query]}
        ).encode("utf-8")

        req = urllib.request.Request(
            "https://leansearch.net/search",
            data=payload,
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            results = json.loads(response.read().decode("utf-8"))

        return (
            [r["result"] for r in results[0]]
            if results and results[0]
            else "No results found."
        )

    except Exception as e:
        return f"leansearch.net error:\n{str(e)}"


if __name__ == "__main__":
    mcp.run()
