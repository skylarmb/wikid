#!/usr/bin/env python3
"""
ZIM file tools for offline knowledge base search.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from libzim import Archive, Searcher, Query, SuggestionSearcher, SuggestionItem
from markdownify import markdownify as md


ZIM_DATA_PATH = Path(__file__).parent.parent / "data" / "zim"


def _is_english_content(title: str, content: str) -> bool:
    """Check if content appears to be in English based on title and content."""
    # Skip pages with foreign language indicators in title
    foreign_indicators = [
        '(Español)', '(Français)', '(Deutsch)', '(Italiano)', '(Polski)', 
        '(Português)', '(Русский)', '(简体中文)', '(正體中文)', '(Magyar)',
        '(العربية)', '(日本語)', '(한국어)', '(Nederlands)', '(Svenska)',
        '(Türkçe)', '(Čeština)', '(Ελληνικά)', '(Български)'
    ]
    
    title_lower = title.lower()
    for indicator in foreign_indicators:
        if indicator.lower() in title_lower:
            return False
    
    # Check for common non-English phrases in content preview
    non_english_phrases = [
        'cet article', 'cette page', 'artikel', 'artículo', 'artigo',
        'данная статья', '本文', '이 문서', 'dit artikel', 'questa pagina'
    ]
    
    content_lower = content.lower()[:200]  # Check first 200 chars
    for phrase in non_english_phrases:
        if phrase in content_lower:
            return False
    
    return True


def list_zim_files() -> str:
    """
    List all available ZIM files in the data directory.
    
    Returns:
        JSON string with available ZIM files and their metadata
    """
    try:
        zim_files = []
        
        if not ZIM_DATA_PATH.exists():
            return json.dumps({"error": "ZIM data directory not found", "files": []})
        
        for zim_file in ZIM_DATA_PATH.glob("*.zim"):
            try:
                archive = Archive(str(zim_file))
                # Helper function to decode metadata bytes to string
                def get_metadata_str(key):
                    try:
                        value = archive.get_metadata(key)
                        return value.decode('utf-8') if isinstance(value, bytes) else str(value) if value else ""
                    except:
                        return ""
                
                file_info = {
                    "filename": zim_file.name,
                    "path": str(zim_file),
                    "title": get_metadata_str("Title") or zim_file.stem,
                    "description": get_metadata_str("Description"),
                    "creator": get_metadata_str("Creator"),
                    "publisher": get_metadata_str("Publisher"),
                    "date": get_metadata_str("Date"),
                    "entry_count": archive.entry_count,
                    "article_count": archive.article_count,
                    "media_count": archive.media_count
                }
                zim_files.append(file_info)
            except Exception as e:
                # If we can't read a ZIM file, still list it but mark as error
                zim_files.append({
                    "filename": zim_file.name,
                    "path": str(zim_file),
                    "error": f"Could not read ZIM file: {str(e)}"
                })
        
        return json.dumps({
            "found": len(zim_files),
            "files": zim_files
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error listing ZIM files: {str(e)}", "files": []})


def search_zim(query: str, zim_file: Optional[str] = None, max_results: int = 10) -> str:
    """
    Search for content across ZIM files.
    
    Args:
        query: Search query string
        zim_file: Optional specific ZIM file to search (filename or path)
        max_results: Maximum number of results to return
    
    Returns:
        JSON string with search results
    """
    try:
        results = []
        
        if zim_file:
            # Search specific file
            zim_path = _resolve_zim_file(zim_file)
            if not zim_path:
                return json.dumps({"error": f"ZIM file not found: {zim_file}", "results": []})
            
            archive_results = _search_archive(zim_path, query, max_results)
            results.extend(archive_results)
        else:
            # Search all available ZIM files
            if not ZIM_DATA_PATH.exists():
                return json.dumps({"error": "ZIM data directory not found", "results": []})
            
            for zim_path in ZIM_DATA_PATH.glob("*.zim"):
                try:
                    archive_results = _search_archive(zim_path, query, max_results // 2)
                    results.extend(archive_results)
                except Exception as e:
                    # Continue searching other files if one fails
                    continue
        
        # Sort by relevance (libzim should handle this, but we can re-sort if needed)
        return json.dumps({
            "query": query,
            "found": len(results),
            "results": results[:max_results]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Search error: {str(e)}", "results": []})


def get_zim_entry(title: str, zim_file: Optional[str] = None) -> str:
    """
    Retrieve a specific entry/article from ZIM files.
    
    Args:
        title: Title of the article to retrieve
        zim_file: Optional specific ZIM file to search
    
    Returns:
        JSON string with article content
    """
    try:
        if zim_file:
            # Search specific file
            zim_path = _resolve_zim_file(zim_file)
            if not zim_path:
                return json.dumps({"error": f"ZIM file not found: {zim_file}"})
            
            return _get_entry_from_archive(zim_path, title)
        else:
            # Search all available ZIM files
            if not ZIM_DATA_PATH.exists():
                return json.dumps({"error": "ZIM data directory not found"})
            
            for zim_path in ZIM_DATA_PATH.glob("*.zim"):
                try:
                    result = _get_entry_from_archive(zim_path, title)
                    result_data = json.loads(result)
                    if "content" in result_data:  # Found the entry
                        return result
                except Exception:
                    continue
            
            return json.dumps({"error": f"Entry '{title}' not found in any ZIM file"})
        
    except Exception as e:
        return json.dumps({"error": f"Error retrieving entry: {str(e)}"})


def get_zim_suggestions(query: str, zim_file: Optional[str] = None, max_suggestions: int = 10) -> str:
    """
    Get search suggestions for a query.
    
    Args:
        query: Query to get suggestions for
        zim_file: Optional specific ZIM file to search
        max_suggestions: Maximum number of suggestions to return
    
    Returns:
        JSON string with suggestions
    """
    try:
        suggestions = []
        
        if zim_file:
            # Get suggestions from specific file
            zim_path = _resolve_zim_file(zim_file)
            if not zim_path:
                return json.dumps({"error": f"ZIM file not found: {zim_file}", "suggestions": []})
            
            archive_suggestions = _get_suggestions_from_archive(zim_path, query, max_suggestions)
            suggestions.extend(archive_suggestions)
        else:
            # Get suggestions from all available ZIM files
            if not ZIM_DATA_PATH.exists():
                return json.dumps({"error": "ZIM data directory not found", "suggestions": []})
            
            for zim_path in ZIM_DATA_PATH.glob("*.zim"):
                try:
                    archive_suggestions = _get_suggestions_from_archive(zim_path, query, max_suggestions // 2)
                    suggestions.extend(archive_suggestions)
                except Exception:
                    continue
        
        return json.dumps({
            "query": query,
            "found": len(suggestions),
            "suggestions": suggestions[:max_suggestions]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error getting suggestions: {str(e)}", "suggestions": []})


def _resolve_zim_file(zim_file: str) -> Optional[Path]:
    """Resolve ZIM file path from filename or full path."""
    if os.path.isabs(zim_file):
        path = Path(zim_file)
        if path.exists():
            return path
    else:
        # Try as filename in ZIM data directory
        path = ZIM_DATA_PATH / zim_file
        if path.exists():
            return path
        # Try adding .zim extension
        path_with_ext = ZIM_DATA_PATH / f"{zim_file}.zim"
        if path_with_ext.exists():
            return path_with_ext
    
    return None


def _search_archive(zim_path: Path, query: str, max_results: int) -> List[Dict[str, Any]]:
    """Search within a specific ZIM archive."""
    archive = Archive(str(zim_path))
    
    # Try fulltext search first
    if archive.has_fulltext_index:
        try:
            searcher = Searcher(archive)
            search_query = Query(query)
            search = searcher.search(search_query)
            
            results = []
            estimated = search.getEstimatedMatches()
            
            if estimated > 0:
                for i in range(min(max_results, estimated)):
                    try:
                        result = search.getResults(i, 1)[0]
                        entry = archive.get_entry_by_path(result.path)
                        
                        content_preview = ""
                        # Get a preview of the content
                        if entry.is_redirect:
                            redirect_entry = entry.get_redirect_entry()
                            content_preview = f"Redirect to: {redirect_entry.title}"
                        else:
                            # Get actual content and convert HTML to markdown
                            html_content = entry.get_item().content.tobytes().decode('utf-8', errors='ignore')
                            markdown_content = md(html_content, strip=['script', 'style'])
                            content_preview = markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content
                        
                        # Only include English content
                        if _is_english_content(entry.title, content_preview):
                            results.append({
                                "title": entry.title,
                                "path": result.path,
                                "url": result.url,
                                "score": result.score,
                                "snippet": result.snippet,
                                "content_preview": content_preview,
                                "source_zim": zim_path.name
                            })
                        
                    except Exception as e:
                        # Skip entries that can't be processed
                        continue
                
                return results
        except Exception as e:
            # Fall through to title search if fulltext fails
            pass
    
    # Fallback: simple title-based search
    results = []
    count = 0
    
    # Get a random sample of entries to search through titles
    # This is a simple fallback - not ideal but functional
    for i in range(min(1000, archive.entry_count)):  # Sample first 1000 entries
        if count >= max_results:
            break
        try:
            entry = archive.get_random_entry()
            if query.lower() in entry.title.lower():
                content_preview = ""
                if entry.is_redirect:
                    redirect_entry = entry.get_redirect_entry()
                    content_preview = f"Redirect to: {redirect_entry.title}"
                else:
                    html_content = entry.get_item().content.tobytes().decode('utf-8', errors='ignore')
                    markdown_content = md(html_content, strip=['script', 'style'])
                    content_preview = markdown_content[:500] + "..." if len(markdown_content) > 500 else markdown_content
                
                # Only include English content
                if _is_english_content(entry.title, content_preview):
                    results.append({
                        "title": entry.title,
                        "path": entry.path,
                        "url": f"/{entry.path}",
                        "score": 1.0,  # Default score for title matches
                        "snippet": content_preview[:200] + "..." if len(content_preview) > 200 else content_preview,
                        "content_preview": content_preview,
                        "source_zim": zim_path.name
                    })
                count += 1
        except Exception:
            continue
    
    return results


def _get_entry_from_archive(zim_path: Path, title: str) -> str:
    """Get a specific entry from a ZIM archive."""
    archive = Archive(str(zim_path))
    
    try:
        # Try to get entry by title
        entry = archive.get_entry_by_title(title)
    except:
        # If not found by title, try by path
        try:
            entry = archive.get_entry_by_path(title)
        except:
            return json.dumps({"error": f"Entry '{title}' not found in {zim_path.name}"})
    
    try:
        if entry.is_redirect:
            redirect_entry = entry.get_redirect_entry()
            content = f"This page redirects to: {redirect_entry.title}"
            html_content = redirect_entry.get_item().content.tobytes().decode('utf-8', errors='ignore')
            markdown_content = md(html_content, strip=['script', 'style'])
            content += f"\n\nContent:\n{markdown_content}"
        else:
            html_content = entry.get_item().content.tobytes().decode('utf-8', errors='ignore')
            content = md(html_content, strip=['script', 'style'])
        
        return json.dumps({
            "title": entry.title,
            "path": entry.path,
            "content": content,
            "source_zim": zim_path.name
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error reading entry content: {str(e)}"})


def _get_suggestions_from_archive(zim_path: Path, query: str, max_suggestions: int) -> List[Dict[str, Any]]:
    """Get suggestions from a specific ZIM archive."""
    archive = Archive(str(zim_path))
    
    try:
        suggestion_searcher = SuggestionSearcher(archive)
        suggestion_search = suggestion_searcher.suggest(query)
        
        suggestions = []
        
        for i in range(min(max_suggestions, suggestion_search.getEstimatedMatches())):
            try:
                suggestion = suggestion_search.getResults(i, 1)[0]
                suggestions.append({
                    "title": suggestion.title,
                    "path": suggestion.path,
                    "url": suggestion.url,
                    "source_zim": zim_path.name
                })
            except Exception:
                break
        
        return suggestions
    except Exception:
        # Fallback: return empty suggestions if suggestion search fails
        return []


if __name__ == "__main__":
    # Test the ZIM tools
    print("Available ZIM files:")
    print(list_zim_files())
    
    print("\nTesting search:")
    print(search_zim("systemd", max_results=3))
    
    print("\nTesting suggestions:")
    print(get_zim_suggestions("system", max_suggestions=5))