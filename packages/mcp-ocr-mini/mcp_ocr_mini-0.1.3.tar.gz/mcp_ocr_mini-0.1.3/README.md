# MCP Server for OCR

A OCR server built using MCP (Model Context Protocol) that provides OCR capabilities through a simple interface.

---

## Features

- Extract text from images using Tesseract OCR
- Support for multiple input types:
  - Local image files
  - Image URLs

## Installation

```bash
# Using pip
pip install mcp-ocr-mini
```

Tesseract will be installed automatically on supported platforms:
- macOS (via Homebrew)
- Linux (via apt, dnf, or pacman)

For Windows: 
- Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- After installation, ensure the Tesseract installation directory is in your system PATH by checking \"tesseract --version\" in command prompt.
            

## Usage

### As an MCP Server

1. Start the server:
    ```bash
    python -m mcp_ocr_mini
    ```

2. Configure Claude for Desktop:
    Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
    ```json
    {
        "mcpServers": {
            "ocr": {
                "command": "python",
                "args": ["-m", "mcp_ocr_mini"]
            }
        }
    }
    ```

### Available Tools

#### perform_ocr
Extract text from images:
```python
# From file
perform_ocr("/path/to/image.jpg")

# From URL
perform_ocr("https://example.com/image.jpg")

```

#### get_supported_languages
List available OCR languages:

```python
get_supported_languages()

```

## License

This project is licensed under the MIT License.  
It includes and modifies code from [rjn32s/mcp-ocr](https://github.com/rjn32s/mcp-ocr), which is also MIT licensed.  
See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Original MCP OCR Server by rjn32s](https://github.com/rjn32s/mcp-ocr). This package is a modified version of [rjn32s/mcp-ocr](https://github.com/rjn32s/mcp-ocr). All credit to the original authors.