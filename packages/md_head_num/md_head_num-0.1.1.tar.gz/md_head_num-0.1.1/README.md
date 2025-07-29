
## Usage
### 1. Import package
```python
from pathlib import Path
from md_head_num import MdHeadNum
```

### 2. Prepare the markdown file list

```python
md_files = list(Path("tests").glob("*.md"))
md_files  # [PosixPath('tests/test1.md'), PosixPath('tests/test2.md')]
```

### 3. Create an instance of `MdHeadNum`

```python
mn = MdHeadNum(md_files, max_level=5)
```

### 4. read markdown file and get the numbering 

```python
mn.numbering()
```

### 5. Numbered markdown file `save` and `save_as`

```python
# mn.save()  # Note: This will overwrite the original file
mn.save_as("_Numbered")  # This will save the numbered(Example: test1_Numbered.md) file with a suffix
```