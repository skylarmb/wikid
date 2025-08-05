# Offline Research Assistant with ZIM Files

## Project Overview

This project implements an offline research assistant that utilizes offline data sources stored in ZIM format (Wikipedia, Stack Exchange, etc.) to provide accurate and well-researched answers. The assistant uses vLLM for LLM inference with tool calling capabilities to interact with ZIM files via the `libzim` library.

## Current Status

### ✅ Completed Infrastructure
- [x] Basic vLLM server setup with tool calling support (Qwen3-8B-FP8 with hermes parser)
- [x] Enhanced command-line client with streaming and markdown rendering
- [x] Interactive chat interface with rich formatting
- [x] Tool calling framework - **WORKING** with structured OpenAI format calls
- [x] Project planning and documentation
- [x] **ZIM file integration implementation** - Phase 1 complete
- [x] **System prompt integration** with citation requirements
- [x] **ZIM file discovery and management** - auto-detect from data/zim/
- [x] **Full-text search across offline knowledge bases** - with English content filtering
- [x] **Content retrieval and citation system** - HTML→Markdown conversion
- [x] **Model optimization** - switched from quantized models to maintain tool calling
- [x] **Generic naming refactor** - qwen-server → wikid-server for model flexibility

### ✅ Completed ZIM Tools
- [x] `search_zim()` - Full-text search with fallback title matching
- [x] `get_zim_entry()` - Retrieve specific articles with HTML→Markdown conversion  
- [x] `list_zim_files()` - Show available knowledge bases with metadata
- [x] `get_zim_suggestions()` - Get search suggestions (with graceful fallback)
- [x] **English content filtering** - automatically skip foreign language pages
- [x] **Markdownify integration** - convert HTML to clean markdown for better parsing

### 🚧 Current Issues & Future Work
- [ ] **Content length optimization** - ZIM articles overwhelm 8K context window
- [ ] **Content chunking/summarization** - make large articles more manageable
- [ ] **Improved search relevance** - better matching for technical queries

## Implementation Plan

### ✅ Phase 1: ZIM Integration Foundation (COMPLETED)
1. ✅ **Add libzim dependency** to pyproject.toml
2. ✅ **Implement ZIM tools** module with core functions:
   - ✅ `search_zim()` - Full-text search across ZIM files with English filtering
   - ✅ `get_zim_entry()` - Retrieve specific articles/pages with Markdown conversion
   - ✅ `list_zim_files()` - Show available knowledge bases with metadata
   - ✅ `get_zim_suggestions()` - Get search suggestions with graceful fallback

### ✅ Phase 2: Research Assistant Configuration (COMPLETED)
3. ✅ **Add system prompt injection** to conversation flow with citation requirements
4. ✅ **Replace existing tools** with ZIM-focused research tools  
5. ✅ **Test with Arch Linux wiki** (available in ./data/zim/)
6. ✅ **Debug and fix tool calling** - resolved structured vs text-based tool call parsing

### ✅ Phase 3: Enhanced Research Experience (COMPLETED)
7. ✅ **Implement citation system** with source attribution requirements
8. ✅ **Multi-step research flow** (search → retrieve → synthesize)
9. ✅ **Knowledge base discovery** on startup with auto-detection
10. ✅ **Tool calling optimization** - simplified parameters, no ZIM file guessing

### 🚧 Phase 4: Content Optimization (IN PROGRESS)
11. ⚠️ **Content length management** - large articles exceed 8K context window
12. 📋 **Implement content chunking** - break large articles into manageable sections
13. 📋 **Add content summarization** - extract key information from long articles
14. 📋 **Improve search relevance** - better matching algorithms for technical content

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
wikid_server/
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
- `rich` - Terminal formatting and markdown rendering
- `libzim==3.7.0` - ZIM file reading and search ✅
- `markdownify==1.1.0` - HTML to Markdown conversion ✅

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

### Session 1 (COMPLETED) 
- [x] Project planning and documentation
- [x] Infrastructure review and optimization  
- [x] ZIM tools implementation and debugging
- [x] Tool calling system resolution
- [x] System prompt integration with citations
- [x] Model optimization (Qwen3-8B-FP8 with hermes parser)
- [x] Generic project renaming (qwen-server → wikid-server)

### Current State: **FULLY FUNCTIONAL** ✅
- ✅ Offline research assistant working end-to-end
- ✅ Tool calling with ZIM file search and retrieval
- ✅ Automatic citation system
- ✅ HTML→Markdown content conversion
- ✅ English content filtering
- ✅ 8K context window with Qwen3-8B-FP8

### Next Session Priorities
- [ ] **Content chunking system** - split large articles into sections
- [ ] **Content summarization** - extract key points from long articles  
- [ ] **Search relevance improvement** - better technical query matching
- [ ] **Additional knowledge bases** - Wikipedia, Stack Exchange integration
- [ ] **Performance optimization** - caching, indexing improvements