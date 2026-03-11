# ---------- TOKENIZER.PY -------------------

import re

def highlight_python(editor):
    text = editor.text()

    # Define token patterns
    keywords = r"\b(import|from|def|class|return|if|else|elif|for|while|in|try|except|with|as|pass|break|continue)\b"
    numbers = r"\b\d+(\.\d+)?\b"
    strings = r"(\".*?\"|'.*?')"
    comments = r"#.*"
    identifiers = r"\b[A-Za-z_][A-Za-z0-9_]*\b"
    operators = r"[=+\-*/%<>!&|.:()]"

    # Reset styling
    editor.SendScintilla(editor.SCI_STARTSTYLING, 0, 31)
    editor.SendScintilla(editor.SCI_SETSTYLING, len(text), editor.semantic_styles.get("default", 1))

    # Comments first (so they override other tokens)
    for match in re.finditer(comments, text):
        start, end = match.start(), match.end()
        editor.apply_semantic_token(start, end - start, "comment")

    # Strings
    for match in re.finditer(strings, text):
        start, end = match.start(), match.end()
        editor.apply_semantic_token(start, end - start, "string")

    # Numbers
    for match in re.finditer(numbers, text):
        start, end = match.start(), match.end()
        editor.apply_semantic_token(start, end - start, "number")

    # Keywords
    for match in re.finditer(keywords, text):
        start, end = match.start(), match.end()
        editor.apply_semantic_token(start, end - start, "keyword")

    # Operators (including dots)
    for match in re.finditer(operators, text):
        start, end = match.start(), match.end()
        editor.apply_semantic_token(start, end - start, "operator")

    # Identifiers (variables, self, methods, properties)
    for match in re.finditer(identifiers, text):
        start, end = match.start(), match.end()
        # Look behind for a dot
        if start > 0 and text[start-1] == ".":
            token_type = "property"
        elif match.group() in ("self", "cls"):
            token_type = "variable"
        else:
            token_type = "variable"
        editor.apply_semantic_token(start, end - start, token_type)

    # Apply each token type
    for pattern, token_type in [
        (keywords, "keyword"),
        (numbers, "number"),
        (strings, "string"),
        (comments, "comment")
    ]:
        for match in re.finditer(pattern, text):
            start, end = match.start(), match.end()
            editor.apply_semantic_token(start, end - start, token_type)

def highlight_lua(editor):
    text = editor.text()
    keywords = r"\b(local|function|end|if|then|else|elseif|for|while|do|return|break)\b"
    numbers = r"\b\d+(\.\d+)?\b"
    strings = r"(\".*?\"|'.*?')"
    comments = r"--.*"

    # Reset styling
    editor.SendScintilla(editor.SCI_STARTSTYLING, 0, 31)
    editor.SendScintilla(editor.SCI_SETSTYLING, len(text), editor.semantic_styles.get("default", 1))

    # Apply token colors
    for pattern, token_type in [
        (keywords, "keyword"),
        (numbers, "number"),
        (strings, "string"),
        (comments, "comment")
    ]:
        for match in re.finditer(pattern, text):
            start, end = match.start(), match.end()
            editor.apply_semantic_token(start, end - start, token_type)

