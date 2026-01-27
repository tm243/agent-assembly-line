
# AI Agent Rules & Project Context

This file contains critical architectural rules and coding standards for all AI agents (Claude, Copilot, Cursor, etc.) working on this codebase. These instructions override general model defaults.

## Commenting Standards

- Prioritize self-documenting code: Use descriptive variable and function names so that the logic is clear without explanation.

- No trivial comments: Do not add comments that merely restate what the code is doing (e.g., avoid // increment counter above i++).

- Explain the "Why," not the "What": Only use comments to document non-obvious business logic, complex algorithms, or "hacks" that require context.

- Use standard documentation formats: Use JSDoc for TypeScript/JavaScript, Docstrings for Python, or XML comments for C# only for public APIs and complex methods.
No "commented-out" code: Never leave dead or commented-out code blocks in the output; delete them instead.

## Formatting Rules

- empty lines should not contain any spaces or other invisible characters, they should truly be empty

- lines should not end with a space, no space characters or tabs after the last actual character
