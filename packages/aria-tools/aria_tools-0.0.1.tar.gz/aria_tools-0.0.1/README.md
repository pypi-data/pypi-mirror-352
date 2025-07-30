# Aria Tools

Schema tools for automating and managing scientific research workflows. Adapted from [Aria Agents](https://github.com/aicell-lab/aria-agents).

## Development

### Prerequisites

- Python 3.11
- Conda

### Installation

To install, run the setup script:
```bash
scripts/setup_dev.sh
```

### Running the Development Environment

#### Running on local server

To run the development server locally, use:
```bash
python -m aria_tools local
```

#### Running on remote server

To run the development server on a remote server, use:
```bash
python -m aria_tools remote --server-url <server_url>
```

### Testing

Run the tests using pytest:
```bash
pytest
```
