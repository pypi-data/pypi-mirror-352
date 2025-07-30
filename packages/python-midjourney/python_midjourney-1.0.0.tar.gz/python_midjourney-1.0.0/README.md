# 🎨 Python Midjourney

Midjourney automation Python package using Discord user tokens

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/badge/pypi-1.0.0-orange.svg)](https://pypi.org/project/python-midjourney/)

## ✨ Key Features

- 🎨 **Midjourney Automation**: Execute `/imagine` commands using Discord user tokens
- 🔪 **Auto Image Splitting**: Automatically split 4-grid images into individual images
- 📦 **Batch Processing**: Process multiple prompts simultaneously
- 💾 **Auto Save**: Automatically save original + split images
- 🚀 **Full Automation**: Command → Generate → Download → Split → Save
- 📚 **Simple API**: Intuitive and easy-to-use interface

## 🚀 Installation

### Install with pip

```bash
pip install python-midjourney
```

### Install from source

```bash
git clone https://github.com/yourusername/python_midjourney.git
cd python_midjourney
pip install -e .
```

## ⚙️ Environment Setup

### 1. Required Environment Variables

```bash
# Set Discord user token
export DISCORD_USER_TOKEN="your_discord_user_token_here"

# Set Midjourney channel ID
export MIDJOURNEY_CHANNEL_ID="your_midjourney_channel_id_here"
```

### 2. Using .env file (Recommended)

Create a `.env` file in your project root:

```env
# Discord settings
DISCORD_USER_TOKEN=your_discord_user_token_here
MIDJOURNEY_CHANNEL_ID=your_midjourney_channel_id_here
```

### 3. How to Obtain Environment Variables

#### Getting Discord User Token

1. **Access Discord in web browser** (discord.com)
2. **Open Developer Tools** (F12)
3. **Go to Network tab**
4. **Send any message**
5. **Find Authorization header in API requests**
6. **Copy the token** (usually starts with `MTAxxxxx...`)

⚠️ **Important**: Never share your user token!

#### Getting Midjourney Channel ID

1. **Enable Developer Mode in Discord**
   - Settings → Advanced → Developer Mode ON
2. **Right-click on Midjourney channel**
3. **Select "Copy ID"**

## 🎯 Usage

### Basic Usage

```python
from python_midjourney import MidjourneyClient

# Create client (automatically uses environment variables)
client = MidjourneyClient()

# Generate image
result = client.generate_image("a beautiful sunset over mountains")

if result['success']:
    print(f"Original file: {result['original_file']}")
    print(f"Split files: {len(result['split_files'])} files")
    for i, file in enumerate(result['split_files'], 1):
        print(f"  {i}. {file}")
```

### Direct Token Specification

```python
from python_midjourney import MidjourneyClient

# Specify token and channel ID directly
client = MidjourneyClient(
    user_token="your_discord_token",
    channel_id="your_channel_id",
    auto_split=True  # Enable auto-split
)

result = client.generate_image("cyberpunk city landscape")
```

### Batch Processing

```python
from python_midjourney import MidjourneyClient

client = MidjourneyClient()

prompts = [
    "cozy coffee shop with warm lighting",
    "modern minimalist workspace",
    "serene mountain lake at dawn"
]

# Batch generation (5 second intervals)
results = client.generate_batch(prompts, delay=5)

# Check results
for i, result in enumerate(results):
    if result and result['success']:
        print(f"✅ Image {i+1}: {result['total_files']} files generated")
    else:
        print(f"❌ Image {i+1}: Failed")
```

### Quick Usage (Convenience Function)

```python
from python_midjourney import quick_generate

# Generate image in one line
result = quick_generate(
    "fantasy castle in the clouds",
    user_token="your_token",  # Optional
    channel_id="your_channel", # Optional
    auto_split=True
)
```

### Disable Auto-Split

```python
from python_midjourney import MidjourneyClient

# Save original image only (no splitting)
client = MidjourneyClient(auto_split=False)
result = client.generate_image("abstract art")

print(f"Original only saved: {result['original_file']}")
# split_files will be an empty list
```

### Check Channel Information

```python
from python_midjourney import MidjourneyClient

client = MidjourneyClient()

# Get current channel information
info = client.get_channel_info()
print(f"Channel name: {info['name']}")
print(f"Server ID: {info['guild_id']}")

# Change to another channel
client.set_channel("another_channel_id")
```

## 📂 Result File Structure

```
your_project/
├── images/                    # Original images
│   ├── 20231201_143022_sunset_mountains_midjourney.png
│   └── 20231201_143122_cyberpunk_city_midjourney.png
└── images/split/              # Split images
    ├── 20231201_143022_sunset_mountains_midjourney_part1.png
    ├── 20231201_143022_sunset_mountains_midjourney_part2.png
    ├── 20231201_143022_sunset_mountains_midjourney_part3.png
    └── 20231201_143022_sunset_mountains_midjourney_part4.png
```

## 🛠️ API Reference

### MidjourneyClient

#### Constructor

```python
MidjourneyClient(
    user_token: str = None,     # Discord user token
    channel_id: str = None,     # Midjourney channel ID  
    auto_split: bool = True     # Whether to auto-split
)
```

#### Methods

##### generate_image()

```python
generate_image(
    prompt: str,                # Image generation prompt
    channel_id: str = None,     # Channel ID (default: set during initialization)
    timeout: int = 60           # Timeout in seconds
) -> Optional[Dict[str, Any]]
```

**Return value:**
```python
{
    'success': True,
    'prompt': 'your prompt',
    'original_file': 'images/xxx.png',
    'split_files': ['images/split/xxx_part1.png', ...],
    'message_id': 'discord_message_id',
    'timestamp': '2023-12-01T14:30:22.123456',
    'total_files': 5
}
```

##### generate_batch()

```python
generate_batch(
    prompts: List[str],         # List of prompts
    channel_id: str = None,     # Channel ID
    delay: int = 5              # Delay between requests in seconds
) -> List[Dict[str, Any]]
```

##### set_channel()

```python
set_channel(channel_id: str)    # Change default channel
```

##### get_channel_info()

```python
get_channel_info(
    channel_id: str = None      # Channel ID (default: currently set channel)
) -> Dict[str, Any]
```

### Convenience Functions

#### quick_generate()

```python
quick_generate(
    prompt: str,                # Image generation prompt
    user_token: str = None,     # Discord user token
    channel_id: str = None,     # Channel ID
    auto_split: bool = True     # Whether to auto-split
) -> Optional[Dict[str, Any]]
```

## ⚠️ Important Notes

### 1. Discord Terms Compliance

- Using user tokens may violate Discord's Terms of Service
- **Use only for personal projects**
- Commercial use prohibited

### 2. Token Security

- Never share your user token
- Don't upload tokens to public repositories like GitHub
- Use environment variables or `.env` files

### 3. Usage Limitations

- Requires paid Midjourney subscription
- Must comply with Discord API rate limits
- Avoid excessive requests

### 4. Technical Limitations

- Internet connection required
- Dependent on Discord server status
- Dependent on Midjourney bot status

## 🔧 Troubleshooting

### Common Errors

#### 1. "Discord User Token not set"

```bash
# Check environment variable
echo $DISCORD_USER_TOKEN

# Set environment variable
export DISCORD_USER_TOKEN="your_token_here"
```

#### 2. "Midjourney Channel ID not set"

```bash
# Set channel ID
export MIDJOURNEY_CHANNEL_ID="your_channel_id_here"
```

#### 3. "Failed to get channel info: 403"

- Token is incorrect or expired
- No access permission to the channel
- Need to check Discord account status

#### 4. "Timeout: No response from Midjourney"

- Midjourney bot is offline or response delayed
- Try increasing timeout value (default: 60 seconds)
- Check network connection

### Debugging Tips

```python
from python_midjourney import MidjourneyClient

# Debug with detailed output
client = MidjourneyClient()

# Check channel connection
try:
    info = client.get_channel_info()
    print("✅ Channel connection successful:", info['name'])
except Exception as e:
    print("❌ Channel connection failed:", e)

# Test image generation
result = client.generate_image("test image", timeout=120)
if result:
    print("✅ Image generation successful")
else:
    print("❌ Image generation failed")
```

## 📝 License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

- Bug Reports: [GitHub Issues](https://github.com/yourusername/python_midjourney/issues)
- Feature Requests: [GitHub Discussions](https://github.com/yourusername/python_midjourney/discussions)

## 🙏 Acknowledgments

- [Midjourney](https://midjourney.com/) - Amazing AI art generation service
- [Discord](https://discord.com/) - Powerful communication platform
- [Pillow](https://pillow.readthedocs.io/) - Python image processing library

---

⚠️ **Disclaimer**: This package is created for educational and personal use purposes. Please comply with Discord's and Midjourney's Terms of Service when using. 