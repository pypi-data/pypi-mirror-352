# BinCraft to JSON Converter

A Python module that converts BinCraft files to JSON format using a C++ extension for better performance.

## Installation

```bash
pip install bincraft2json
```

## Prerequisites

- Python 3.7 or higher
- zstd library (for decompression)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install libzstd-dev
  
  # CentOS/RHEL
  sudo yum install libzstd-devel
  ```

## Usage

```python
from bincraft2json import decode_bincraft

# Convert a BinCraft file to JSON
result = decode_bincraft("path/to/your/file.bincraft")

# If the file is compressed with zstd
result = decode_bincraft("path/to/your/file.bincraft", zstd_compressed=True)

# Display the result
print(result)
```

## Development

To install in development mode:

```bash
git clone https://github.com/aymene69/bincraft2json.git
cd bincraft2json
pip install -e .
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

- Aymene69 (@aymene69)

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request. 