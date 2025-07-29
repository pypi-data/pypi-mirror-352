import os
from pathlib import Path

DEFAULT_ENCODING = "utf-8"


class MdHeadNum(object):
    """A class to handle Markdown heading numbering."""

    def __init__(self, files, max_level=5):
        self.max_level = max_level
        self.files = files
        self._contents = self._read_file()

        self._counter = [0] * max_level

        self._numbering_flag = False

        self.numbered_contents = False  # Placeholder for numbered contents

    def _read_file(self):
        """Reads the content of the Markdown files."""
        contents = []
        for file in self.files:
            with open(file, "r", encoding="utf-8") as f:
                contents.append(f.readlines())
        return contents

    def numbering(self):
        """Adds numbering to the headings in the Markdown files."""
        self._counter = [0] * self.max_level
        numbered_contents = []
        for content in self._contents:
            numbered_content = []
            line: str
            for line in content:
                if line.startswith("#"):
                    level = self._get_heading_level(line)
                    numbering = self._number_title(
                        level,
                        self._counter,
                        self.max_level,
                    )
                    prefix = "#" * level
                    suffix = line[level + 1 :]
                    numbered_content.append(f"{prefix} {numbering} {suffix}")
                else:
                    numbered_content.append(line)
            numbered_contents.append(numbered_content)

        self._numbering_flag = True
        self.numbered_contents = numbered_contents
        return numbered_contents

    def save(self):
        if not self._numbering_flag:
            raise ValueError(
                "Numbering has not been applied yet. Call numbering() first."
            )
        else:
            for i, content in enumerate(self.numbered_contents):
                file_path = Path(self.files[i])
                if not file_path.exists():
                    raise FileNotFoundError(f"File {file_path} does not exist.")
                with open(file_path, "w", encoding=DEFAULT_ENCODING) as f:
                    f.writelines(content)
                print(f"File {file_path} saved successfully.")

    def save_as(self, adding="_numbered"):
        """Saves the numbered contents to new files."""
        if not self._numbering_flag:
            raise ValueError(
                "Numbering has not been applied yet. Call numbering() first."
            )
        else:
            for i, content in enumerate(self.numbered_contents):
                file_path = Path(self.files[i])
                new_file_path = file_path.with_name(
                    f"{file_path.stem}{adding}{file_path.suffix}"
                )
                with open(new_file_path, "w", encoding=DEFAULT_ENCODING) as f:
                    f.writelines(content)
                print(f"File {new_file_path} saved successfully.")

    @staticmethod
    def _get_heading_level(line: str) -> int:
        """Returns the heading level of a Markdown line."""
        count = 0
        for char in line:
            if char == "#":
                count += 1
            else:
                break
        return count if line[count : count + 1] == " " else 0

    @staticmethod
    def _number_title(level, counters=[], max_level=5):
        if len(counters) == 0:
            counters = [0] * level

        # 해당 레벨 카운터 증가
        counters[level - 1] += 1
        # 하위 레벨 카운터 초기화
        for i in range(level, len(counters)):
            counters[i] = 0
        # 번호 문자열 생성
        numbers = [str(counters[i]) for i in range(level) if counters[i] > 0]
        return ".".join(numbers)
