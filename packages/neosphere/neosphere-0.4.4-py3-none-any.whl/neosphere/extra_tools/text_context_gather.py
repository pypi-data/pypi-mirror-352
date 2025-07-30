import json
import logging
import tiktoken

def GatherTextContext(context: str, text_list: list[str] = None, textfile_paths_list: list[str] = None) -> str:
    """
    Gather context from various sources and combine them.
    
    Args:
        context: Initial context string
        text_list: List of text strings to add to context
        textfile_paths_list: List of file paths to read and add to context
    
    Returns:
        Combined context string
    """
    if text_list:
        try:
            if isinstance(text_list, str):
                text_list = json.loads(text_list)
            if isinstance(text_list, list):
                context += " ".join(text_list)
        except json.JSONDecodeError:
            # logger.warning("Failed to parse text_list as JSON, using as-is")
            context += text_list

    if textfile_paths_list:
        for file_path in textfile_paths_list:
            # logger.info(f"Reading file: {file_path}")
            try:
                with open(file_path, 'r') as f:
                    context += f.read() + '\n'
            except Exception as e:
                # logger.error(f"Error reading file {file_path}: {e}")
                pass
    token_count = count_tokens(context)
    # logger.info(f"Final gathered context token count: {token_count}: {context[:50]}...{context[-50:]}")
    return context, token_count

def count_tokens(text: str, model: str = "cl100k_base") -> int:
    try:
        encoding = tiktoken.get_encoding(model)
        return len(encoding.encode(text))
    except Exception as e:
        # Fallback to rough word count - this is not accurate but better than nothing
        # Each word is roughly 1.3 tokens on average
        return int(len(text.split()) * 1.3) 