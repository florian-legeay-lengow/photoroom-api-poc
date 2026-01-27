# Photoroom API - Background Removal POC

A simple Python script to test Photoroom's Background Removal API for processing images in bulk.

## Features

- 📁 Process multiple images from a folder
- 🎨 Remove backgrounds with transparent or custom colors
- 📐 Multiple output sizes (preset or custom dimensions)
- 🖼️ Multiple output formats (png, jpg, webp)
- ✂️ Optional cropping to cutout border
- 🎬 Green screen despill support (v1)
- 📏 Custom dimensions support with v2 API (Plus Plan)
- 🔧 Max width/height constraints with aspect ratio preservation
- 🧪 Sandbox mode for testing

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your API key:**
   - Visit [Photoroom API Dashboard](https://app.photoroom.com/api-dashboard)
   - Copy your API key

3. **Create input/output folders:**
   ```bash
   mkdir input_images output_images
   ```

4. **Configure the script:**
   - Open `photoroom_processor.py`
   - Set your `API_KEY`
   - Configure other options as needed

## Usage

### Basic Usage

1. Place your images in the `input_images` folder
2. Run the script:
   ```bash
   python photoroom_processor.py
   ```
3. Find processed images in the `output_images` folder

### Configuration Options

Edit these variables in `photoroom_processor.py`:

```python
# Your Photoroom API key
API_KEY = "your_api_key_here"

# Enable sandbox mode (adds 'sandbox_' prefix to token)
SANDBOX_MODE = True

# API Version - v2 supports custom dimensions (Plus Plan required)
USE_V2 = False  # Set to True for v2/edit endpoint with custom dimensions

# Input and output folders
INPUT_FOLDER = "input_images"
OUTPUT_FOLDER = "output_images"

# Processing options
BG_COLOR = None  # None for transparent, or "#FFFFFF" for white, "red", etc.
SIZE = "full"    # (v1 only) Options: preview, medium, hd, full
FORMAT = "png"   # Options: png, jpg, webp
CROP = False     # Crop to cutout border
DESPILL = False  # Remove green screen reflections (v1 only)

# Custom dimensions (v2 only - requires Plus Plan)
OUTPUT_SIZE = None  # Examples: "1024x768", "800x600", "originalImage", "croppedSubject"
MAX_WIDTH = None    # Maximum width in pixels (maintains aspect ratio)
MAX_HEIGHT = None   # Maximum height in pixels (maintains aspect ratio)
```

### Sandbox Mode

When `SANDBOX_MODE = True`, the script automatically adds the `sandbox_` prefix to your API token. This is useful for testing without consuming your API credits.

### API Version Selection

The script supports two API endpoints:

- **v1/segment (Basic Plan)** - `USE_V2 = False` (default)
  - Preset sizes only (preview, medium, hd, full)
  - Green screen despill support
  - Lower cost

- **v2/edit (Plus Plan)** - `USE_V2 = True`
  - Custom dimensions support
  - Max width/height constraints
  - More advanced features
  - Requires Plus Plan subscription

## API Parameters

### Background Color (`BG_COLOR`)
- `None` - Transparent background (default)
- `"#FFFFFF"` - Hex color (white)
- `"red"`, `"blue"`, etc. - HTML color names

### Size (`SIZE`) - v1 Only
- `preview` - 0.25 Megapixels
- `medium` - 1.5 Megapixels
- `hd` - 4 Megapixels
- `full` - 36 Megapixels (default)

### Custom Dimensions (`OUTPUT_SIZE`) - v2 Only (Plus Plan)
- `"1024x768"` - Fixed dimensions (width x height)
- `"800x600"` - Any custom size in pixels
- `"originalImage"` - Keep original image dimensions
- `"croppedSubject"` - Crop to subject size
- `"auto"` - Automatic (default)

### Max Dimensions (`MAX_WIDTH`, `MAX_HEIGHT`) - v2 Only (Plus Plan)
- Set `MAX_WIDTH` to constrain width (e.g., `1920`)
- Set `MAX_HEIGHT` to constrain height (e.g., `1080`)
- Both can be used together to fit within a bounding box
- Automatically maintains aspect ratio
- Useful for responsive designs

### Format (`FORMAT`)
- `png` - PNG format (default, supports transparency)
- `jpg` - JPEG format
- `webp` - WebP format

### Crop (`CROP`)
- `False` - Keep original dimensions (default)
- `True` - Crop to cutout border, remove transparent pixels

### Despill (`DESPILL`) - v1 Only
- `False` - No despill (default)
- `True` - Remove colored reflections from green backgrounds

## Usage Examples

### Example 1: Basic background removal (v1)
```python
USE_V2 = False
BG_COLOR = None  # Transparent
SIZE = "full"
```

### Example 2: Fixed dimensions with white background (v2)
```python
USE_V2 = True
BG_COLOR = "#FFFFFF"
OUTPUT_SIZE = "1024x768"
```

### Example 3: Constrain to max width, keep aspect ratio (v2)
```python
USE_V2 = True
OUTPUT_SIZE = "originalImage"
MAX_WIDTH = 1920
```

### Example 4: Fit within bounding box (v2)
```python
USE_V2 = True
OUTPUT_SIZE = "originalImage"
MAX_WIDTH = 1920
MAX_HEIGHT = 1080
```

## API Documentation

- [Remove Background API (v1 Basic Plan)](https://docs.photoroom.com/remove-background-api-basic-plan)
- [Image Editing API (v2 Plus Plan)](https://docs.photoroom.com/image-editing-api-plus-plan)
- [API Reference](https://docs.photoroom.com/api-reference-openapi)

## Pricing

Check the [Photoroom pricing page](https://www.photoroom.com/api) for current API pricing and plans.

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)

Maximum image size: 30MB

## Example Output

```
==================================================
PHOTOROOM API - BACKGROUND REMOVAL POC
==================================================
API Version: v1/segment (Basic Plan)
Sandbox Mode: ON
Input Folder: input_images
Output Folder: output_images
Background Color: Transparent
Output Size: full
Output Format: png
Crop: False
Despill: False
==================================================

Found 3 images to process
==================================================
Processing: photo1.jpg...
✓ Saved to: photo1_processed.png
Processing: photo2.png...
✓ Saved to: photo2_processed.png
Processing: photo3.jpg...
✓ Saved to: photo3_processed.png
==================================================

Processing complete: 3/3 successful
```

## Troubleshooting

### Error 402 (Payment Required)
- Check your API plan and remaining credits
- Visit your [API Dashboard](https://app.photoroom.com/api-dashboard)

### Error 403 (Forbidden)
- Verify your API key is correct
- Check if sandbox mode is properly configured

### Error 400 (Bad Request)
- Check image format and size (max 30MB)
- Verify parameter values are valid

## License

This is a proof of concept script. Check Photoroom's terms of service for API usage rights.
