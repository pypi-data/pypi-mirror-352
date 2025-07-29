# Lexoffice Client

> [!WARNING]
> This project is currently in alpha. Only a very limited number of endpoints are supported, and the API may change without notice.

A Python client for the Lexoffice API.

## Installation

To install the package, use pip:

```bash
pip install lexoffice-client
```

## Usage

Here is a basic example of how to use the `lexoffice-client`:

```python
from lexoffice_client.client import LexofficeClient

# Initialize the client
client = LexofficeClient(api_key="your_api_key")

# Example: Retrieve Contact
contacts = client.retrieve_contact("123e4567-e89b-12d3-a456-426614174000")

```

## Development

To contribute to this project, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/yourusername/lexoffice-client.git
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run tests:

```bash
python -m unittest discover tests
```

4. Make your changes and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or issues, please open an issue on the GitHub repository or contact the maintainer.
