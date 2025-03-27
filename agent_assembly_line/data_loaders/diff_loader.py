import subprocess, os
from unidiff import PatchSet
from agent_assembly_line.models.document import Document
from langchain.document_loaders.base import BaseLoader

class GitDiffLoader(BaseLoader):
    raw_diff = None
    added = []
    removed = []
    context = []
    def __init__(self, repo_path: str, context_lines: int = 3):
        """
        :param repo_path: Path to the Git repository.
        :param context_lines: Number of lines of context around changes.
        """
        self.repo_path = repo_path
        self.context_lines = context_lines

    def get_diff(self):
        """Runs `git diff` to get uncommitted changes."""
        result = subprocess.run(
            ["git", "diff", "--unified=0"], cwd=self.repo_path, text=True, capture_output=True
        )
        return result.stdout

    def get_changed_files(self):
        """Gets the list of modified files."""
        patch = PatchSet(self.raw_diff)
        changed_files = [file.path for file in patch]
        return changed_files

    def get_file_content(self, filename):
        """
        Reads the full content of a file, if it exists.
        Moved or deleted files will not be attempted to be opened.
        """
        file_path = f"{self.repo_path}/{filename}"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def load_data(self, raw_diff: str = None):
        """Processes the diff and extracts structured changes."""
        self.raw_diff = raw_diff
        changed_files = self.get_changed_files()
        file_contents = {f: self.get_file_content(f) for f in changed_files}

        patch = PatchSet(self.raw_diff)
        docs = []

        for file in patch:
            filename = file.path
            full_source = file_contents.get(filename, "").splitlines()
            changes = {"file": filename, "added": [], "removed": [], "context": []}

            for hunk in file:
                for line in hunk:
                    if line.is_added:
                        changes["added"].append(file.target_file + " " + line.value.strip())
                    elif line.is_removed:
                        changes["removed"].append(file.target_file + " " + line.value.strip())

                    # Get surrounding context
                    if line.source_line_no is None:
                        continue
                    line_number = line.source_line_no - 1  # Convert to 0-based index
                    if line_number >= 0 and line_number < len(full_source):
                        start = max(0, line_number - self.context_lines)
                        end = min(len(full_source), line_number + self.context_lines + 1)
                        changes["context"].extend(full_source[start:end])

            changes["context"] = list(set(changes["context"]))  # Remove duplicates

            self.added += changes['added']
            self.removed += changes['removed']
            self.context += changes['context']

        return [
            Document(
                page_content=f"Added: {self.added}\nRemoved: {self.removed}\nContext: {self.context}",
                metadata={"files": " ".join(changed_files)}
            )
        ]
