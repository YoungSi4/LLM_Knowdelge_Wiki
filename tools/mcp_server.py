import os
import glob
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("WikiMCP")

WIKI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "wiki"))
if not os.path.exists(WIKI_DIR):
    os.makedirs(WIKI_DIR)

@mcp.tool()
def search_wiki(keyword: str) -> str:
    """Search for a keyword in the wiki markdown files."""
    results = []
    for filepath in glob.glob(os.path.join(WIKI_DIR, "*.md")):
        if ".tmp." in filepath: continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            if keyword.lower() in content.lower():
                name = os.path.basename(filepath).replace(".md", "")
                results.append(f"- [[{name}]]")
    if not results:
        return "No matching documents found."
    return "Found in:\n" + "\n".join(results)

@mcp.tool()
def read_page(page_name: str) -> str:
    """Read the full content of a specific wiki page."""
    filepath = os.path.join(WIKI_DIR, f"{page_name}.md")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return f"[ERROR] Page '{page_name}' does not exist."

@mcp.tool()
def update_page(page_name: str, content: str) -> str:
    """Create or update a wiki page safely using an atomic write."""
    tmp_path = os.path.join(WIKI_DIR, f"{page_name}.tmp.md")
    final_path = os.path.join(WIKI_DIR, f"{page_name}.md")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, final_path)
        return f"[SUCCESS] Page '{page_name}' has been updated."
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return f"[ERROR_SIGNAL] Failed to update page: {str(e)}"

if __name__ == "__main__":
    mcp.run()
