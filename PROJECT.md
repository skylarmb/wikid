# Offline Research Assistant with ZIM Files

## Project Overview

This project implements an offline research assistant that utilizes offline data sources stored in ZIM format (Wikipedia, Stack Exchange, etc.) to provide accurate and well-researched answers. The assistant uses vLLM for LLM inference with tool calling capabilities to interact with ZIM files via the `libzim` library.

## Current Status

### ✅ Completed Infrastructure
- [x] Basic vLLM server setup with tool calling support
- [x] Enhanced command-line client with streaming and markdown rendering
- [x] Interactive chat interface with rich formatting
- [x] Tool calling framework with sample tools
- [x] Project planning and documentation

### 🚧 In Progress
- [ ] ZIM file integration implementation

### 📋 Planned Features
- [ ] System prompt integration for research assistant role
- [ ] ZIM file discovery and management
- [ ] Full-text search across offline knowledge bases
- [ ] Content retrieval and citation system

## Implementation Plan

### Phase 1: ZIM Integration Foundation
1. **Add libzim dependency** to pyproject.toml
2. **Implement ZIM tools** module with core functions:
   - `search_zim()` - Full-text search across ZIM files
   - `get_zim_entry()` - Retrieve specific articles/pages
   - `list_zim_files()` - Show available knowledge bases
   - `get_zim_suggestions()` - Get search suggestions

### Phase 2: Research Assistant Configuration
3. **Add system prompt injection** to conversation flow
4. **Replace existing tools** with ZIM-focused research tools
5. **Test with Arch Linux wiki** (available in ./data/zim/)

### Phase 3: Enhanced Research Experience
6. **Implement citation system** with source attribution
7. **Multi-step research flow** (search → retrieve → synthesize)
8. **Knowledge base discovery** on startup

## Technical Architecture

### System Prompt
```
You are an offline research assistant with access to local knowledge bases in ZIM format.

Your role:
- Provide accurate, well-researched answers using only offline sources
- Always cite sources when providing information
- Use search tools to find relevant content before responding
- Acknowledge limitations when information isn't available offline

Available tools:
- search_zim: Search across ZIM files for relevant content
- get_zim_entry: Retrieve specific articles/pages from ZIM files
- list_zim_files: See what knowledge bases are available
```

### File Structure
```
qwen_server/
├── server.py              # vLLM server with tool calling
├── tool_client.py          # Interactive client with markdown
├── tools.py               # Current sample tools (to be replaced)
├── zim_tools.py           # ZIM file interaction tools (new)
└── __init__.py

data/
└── zim/                   # ZIM files storage
    └── archlinux.zim      # Sample Arch Linux wiki (existing)
```

### Dependencies
- `vllm>=0.10.0` - LLM inference server
- `openai>=1.87.0,<=1.90.0` - API client
- `rich` - Terminal formatting
- `libzim` - ZIM file reading (to be added)

## Usage Flow

### Startup
```bash
uv run wikid-chat
# Expected output: "Found 1 knowledge base: Arch Linux Wiki"
```

### Research Example
```
User: "How do I configure systemd services?"
Assistant: [Searches Arch Wiki] → [Retrieves relevant articles] → 
"Based on the Arch Linux Wiki systemd documentation..."
```

## Development Guidelines

### ZIM File Management
- Store ZIM files in `./data/zim/` directory
- Auto-discover available ZIM files on startup
- Trust ZIM files from reputable sources (Kiwix downloads)
- No validation needed for trusted sources

### Error Handling
- Graceful handling of missing ZIM files
- Clear error messages for search failures
- Fallback behavior when content unavailable

### Citation Format
- Always include source ZIM file name
- Include article title when available
- Provide path/URL for reference

## Future Enhancements

### Additional Knowledge Bases
- Wikipedia dumps (multiple languages)
- Stack Exchange sites
- Technical documentation (Ubuntu, etc.)
- Academic papers and references

### Advanced Features
- Cross-reference search across multiple ZIM files
- Relevance ranking and result clustering
- Content summarization for long articles
- Bookmark/favorites system for frequently accessed content

## Development Notes

### Testing Strategy
- Start with Arch Linux wiki for initial testing
- Validate search functionality with known queries
- Test citation and source attribution
- Verify markdown rendering of retrieved content

### Performance Considerations
- ZIM file indexing and search performance
- Memory usage with large knowledge bases
- Streaming search results for large result sets
- Caching frequently accessed content

## Progress Tracking

### Session 1 (Current)
- [x] Project planning and documentation
- [x] Infrastructure review and optimization
- [ ] ZIM tools implementation (next)

### Future Sessions
- [ ] System prompt integration
- [ ] Research flow testing
- [ ] Additional knowledge base integration
- [ ] Performance optimization