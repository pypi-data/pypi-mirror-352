# Python Markdown (PMD) - Class Documentation

**PMD** stands for **Python Markdown**.

This class is a blueprint for parsing and converting Markdown syntax to HTML using Python. Each method represents a Markdown element and will be implemented in the future.

> 🛠️ **Note**: All methods are currently placeholders and will be developed with actual logic soon.

---

## Methods Overview

### 1. `Heading()`
Handles Markdown headings using `#`, `##`, `###`, etc., converting them into corresponding `<h1>` to `<h6>` HTML tags.

### 2. `Paragraphs()`
Detects and wraps blocks of text as paragraphs (`<p>` tags).

### 3. `LineBreak()`
Handles line breaks using two spaces or a backslash at the end of a line.

### 4. `Emphasis()`
Parses bold (`**bold**`, `__bold__`) and italic (`*italic*`, `_italic_`) text.

### 5. `Blockquote()`
Processes blockquotes using `>` and wraps them in `<blockquote>`.

### 6. `Lists()`
Supports ordered (`1.`) and unordered (`-`, `*`, `+`) lists, converting them into `<ol>` or `<ul>` with `<li>` items.

### 7. `Code()`
Handles inline code with backticks (`` `code` ``) and code blocks with triple backticks (```).

### 8. `HorizontalRule()`
Parses horizontal lines (`---`, `***`, `___`) into `<hr>`.

### 9. `Links()`
Handles links like `[text](url)` and converts them to HTML `<a href="">`.

### 10. `Images()`
Processes images with `![alt](url)` and converts to `<img src="" alt="">`.

### 11. `EscapingCharacters()`
Handles escaping special Markdown characters using the backslash (`\`).

### 12. `Tables()`
Supports simple Markdown tables and converts them into `<table>`, `<thead>`, `<tbody>`, etc.

### 13. `Footnotes()`
Handles footnote references (`[^1]`) and definitions (`[^1]: Footnote text`).

### 14. `HeadingIDs()`
Allows setting custom IDs for headings using `{#id}` after the heading.

### 15. `DefinitionLists()`
Processes definition lists using `Term` and `: Definition` format.

### 16. `Strikethrough()`
Handles `~~text~~` syntax to render `<del>` tags.

### 17. `TaskLists()`
Supports task list items (`- [x]`, `- [ ]`) often used in GitHub-flavored Markdown.

### 18. `Emoji()`
Converts emoji shortcodes like `:smile:` into real emoji characters 😄.

### 19. `Highlight()`
Handles highlighting using `==text==`, which may render with `<mark>` in HTML.

### 20. `Subscript()`
Parses subscript text like `H~2~O` into `H<sub>2</sub>O`.

### 21. `Superscript()`
Parses superscript text like `E=mc^2^` into `E=mc<sup>2</sup>`.

### 22. `AutomaticURL_Linking()`
Auto-detects plain URLs (e.g., `https://example.com`) and converts them into clickable links.

### 23. `DisablingAutomaticURL_Linking()`
Provides a way to disable auto-linking behavior for raw URLs.

---

## 🔜 Coming Soon...

All the above methods will be implemented with full logic to convert Markdown into proper HTML using Python.

Stay tuned for updates! 🚀

---

