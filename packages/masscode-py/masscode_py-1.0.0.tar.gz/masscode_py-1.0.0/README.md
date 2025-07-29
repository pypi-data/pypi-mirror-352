# masscode.py
A Python wrapper for [massCode](https://masscode.io/) - a free and open source code snippets manager for developers.

## Install
```bash
pip install masscode-py
```

## Features
- Full API client for massCode
- Direct file access to massCode database
- Rich query capabilities with Python expressions
- Command-line interface (CLI) for quick access
- Type-safe models with TypedDict
- Automatic file watching and reloading

## Usage

### API Client
```python
from masscode import MasscodeApi

# Initialize API client
api = MasscodeApi()
api.start_masscode()  # Start massCode if not running

# Create a new snippet
snippet = api.create_snippet(
    name="Hello World",
    content=[{"label": "Python", "language": "python", "value": "print('Hello World')"}]
)

# Query snippets
snippets = api.query_snippet(
    name="*hello*",
    isFavorites=True,
    query='(x["name"].startswith("py") and len(x["content"]) > 1)'
)
```

### File Access
```python
from masscode import MasscodeDBFile

# Initialize file client
db = MasscodeDBFile("path/to/db.json")

# Access database
folders = db.folders
snippets = db.snippets
tags = db.tags
```

### CLI Commands

The CLI provides easy access to massCode functionality from the command line:

```bash
# List all snippets
masscode snippets

# List all folders
masscode folders

# List all tags
masscode tags

# Query commands
masscode query tag --name "python" --query '(x["name"].startswith("py"))'
masscode query folder --name "*py*" --is-open
masscode query snippet --folder "python" --tags "web" "api"
```

#### Query Options

##### Tag Query
- `--name/-n`: Tag name (supports wildcards)
- `--query/-q`: Python expression to evaluate
- `--created-at/-c`: Creation timestamp
- `--updated-at/-u`: Update timestamp

##### Folder Query
- `--name/-n`: Folder name (supports wildcards)
- `--default-language/-l`: Default language
- `--parent/-p`: Parent folder name or ID
- `--is-open/-o`: Is folder open flag
- `--is-system/-s`: Is system folder flag
- `--created-at/-c`: Creation timestamp
- `--updated-at/-u`: Update timestamp
- `--query/-q`: Python expression to evaluate

##### Snippet Query
- `--name/-n`: Snippet name (supports wildcards)
- `--folder/-f`: Folder name or ID
- `--is-deleted/-d`: Is deleted flag
- `--is-favorites/-v`: Is favorites flag
- `--tags/-t`: Tag names or IDs (can be specified multiple times)
- `--created-at/-C`: Creation timestamp
- `--updated-at/-u`: Update timestamp
- `--query/-q`: Python expression to evaluate

#### Query Expressions

Query expressions are Python expressions that get evaluated on the object (x) with access to all its fields. This allows for complex filtering:

```bash
# Find folders with Python in name and are open
masscode query folder -q '(x["name"].startswith("py") and x["isOpen"])'

# Find snippets with multiple content fragments
masscode query snippet -q '(len(x["content"]) > 1 and any(c["language"] == "python" for c in x["content"]))'

# Find tags created in the last hour
masscode query tag -q '(time.time() - x["createdAt"]/1000 < 3600)'
```

## Development

### Project Structure
```
masscode/
├── core/
│   ├── api.py      # API client implementation
│   ├── i.py        # Interface definitions
│   └── discovery.py # massCode discovery utilities
├── model/
│   ├── db.py       # Database models
│   └── query.py    # Query models
├── utils/
│   ├── prop.py     # Property utilities
│   └── proc.py     # Process utilities
└── cli.py          # Command-line interface
```

### Memory Bank
The project maintains a memory bank for documentation and context:
- `projectbrief.md`: Core requirements and goals
- `productContext.md`: Project purpose and user experience
- `systemPatterns.md`: Architecture and design patterns
- `techContext.md`: Technical details and dependencies
- `activeContext.md`: Current work focus and decisions
- `progress.md`: Project status and evolution

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

