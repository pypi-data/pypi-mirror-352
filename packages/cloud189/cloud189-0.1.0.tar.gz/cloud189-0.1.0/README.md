# Cloud189

A Python package for interacting with Cloud189 (天翼云盘).

## Installation

```bash
pip install cloud189
```

## Usage

```python
from cloud189 import Cloud189

# Init & Login the client 
client189 = Cloud189Client({
    'username': 'your_username',
    'password': 'your_password'
})

# List files
client189.get_all_files(folder_id)

# Upload file
client189.upload(file_path, folder_id, rename)

# Delete file
client189.delete(file_id, file_name, is_folder=False)

# Get media play url
client189.get_play_url(file_id)

# Get cloud disk space info 
client189.get_user_size_info()

```

## Features

- Login to Cloud189
- List files and folders
- Upload files
- Delete files/folders

## License

This project is licensed under the MIT License - see the LICENSE file for details. 