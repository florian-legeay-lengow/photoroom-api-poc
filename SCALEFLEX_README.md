# Scaleflex Processor - Usage Guide

## Overview

This script processes product images from a CSV file using Scaleflex's DAM (Digital Asset Management) API. It uploads images with metadata and applies presets to the CDN URLs.

## Features

- ✅ Upload images from URLs to Scaleflex DAM
- ✅ Attach metadata (brand, title, description) to images
- ✅ Retrieve CDN URLs from Scaleflex
- ✅ Apply URL presets (e.g., `amz_hero` for Amazon)
- ✅ Save results to a new CSV file with CDN URLs
- ✅ Sandbox mode for testing without actual API calls

## Prerequisites

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Scaleflex Credentials

You need two credentials from Scaleflex:

1. **Filerobot Token**: Your project identifier
   - Found in VXP Asset Hub settings

2. **Filerobot API Key** (X-Filerobot-Key): API authentication key
   - Create from: [Settings > Project > Access > API keys](https://hub.filerobot.com/settings/project/access/api-keys)
   - Ensure permissions include: `FILE_UPLOAD`, `OBJECTS_LIST`

## Usage

### Basic Usage (Sandbox Mode)

Test the script without making actual API calls:

```bash
python scaleflex_processor.py \
  --input sample_products.csv \
  --output products_processed.csv \
  --image-url-column "image_url" \
  --sandbox
```

### Production Usage

Process images with full API integration:

```bash
python scaleflex_processor.py \
  --input sample_products.csv \
  --output products_processed.csv \
  --api-token "YOUR_API_TOKEN" \
  --filerobot-token "YOUR_FILEROBOT_TOKEN" \
  --image-url-column "image_url" \
  --brand-column "brand" \
  --title-column "title" \
  --description-column "description" \
  --preset "amz_hero"
```

## Parameters

### Required Parameters

| Parameter | Description |
|-----------|-------------|
| `--input` | Path to input CSV file |
| `--output` | Path to output CSV file |
| `--image-url-column` | Name of column containing image URLs |

### API Credentials (Required in production mode)

| Parameter | Description |
|-----------|-------------|
| `--api-token` | Filerobot API key (X-Filerobot-Key) |
| `--filerobot-token` | Filerobot project token |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--brand-column` | Column containing brand names | None |
| `--title-column` | Column containing product titles | None |
| `--description-column` | Column containing descriptions | None |
| `--preset` | Preset name to apply to CDN URLs | `amz_hero` |
| `--sandbox` | Run in sandbox mode (no API calls) | False |

## Input CSV Format

Your CSV file should contain at least one column with image URLs. Additional columns for metadata are optional.

Example:

```csv
brand,title,description,image_url
Nike,Air Max 90,Classic running shoe,http://sample.li/nike-air-max.jpg
Adidas,Ultraboost 21,Premium running shoe,http://sample.li/adidas-ultraboost.jpg
```

## Output CSV Format

The script adds three new columns to your CSV:

| Column | Description |
|--------|-------------|
| `scaleflex_cdn_url` | Original CDN URL from Scaleflex |
| `scaleflex_preset_url` | CDN URL with preset applied (e.g., `?p=amz_hero`) |
| `scaleflex_status` | Processing status (`success`, `failed`, `skipped_empty_url`) |

## URL Presets

Presets allow you to apply predefined transformations to images via URL parameters.

### Using Presets

The script automatically adds the preset parameter to CDN URLs:

```
Original: https://token.filerobot.com/folder/image.jpg?vh=abc123
With preset: https://token.filerobot.com/folder/image.jpg?vh=abc123&p=amz_hero
```

### Common Presets

- `amz_hero` - Amazon hero image format
- Custom presets can be created in Scaleflex Hub settings

### Configuring Presets

To create custom presets:

1. Log in to [Scaleflex Hub](https://hub.filerobot.com)
2. Go to Settings > DMO > Delivery > Presets
3. Create a new preset with desired transformations
4. Use the preset name with `--preset` parameter

## API Documentation

- [Scaleflex DAM API](https://developers.scaleflex.com/#e3b464d2-c176-418b-890c-acaaa369b521)
- [URL Presets Documentation](https://docs.scaleflex.com/dynamic-media-optimization-dmo/settings/delivery/url-format#presets)

## Error Handling

The script includes comprehensive error handling:

- Invalid CSV columns: Shows available columns
- Missing image URLs: Skips with status `skipped_empty_url`
- Upload failures: Marks with status `failed`
- API errors: Displays error messages with context

## Rate Limiting

The script includes a 0.5-second delay between requests to avoid rate limiting. This can be adjusted in the code if needed.

## Troubleshooting

### "Column not found" Error

Ensure the column name matches exactly (case-sensitive):

```bash
# Check your CSV columns first
python -c "import pandas as pd; print(pd.read_csv('your_file.csv').columns.tolist())"
```

### Authentication Errors

Verify your credentials:
- API Token has correct permissions
- Filerobot Token matches your project
- No extra spaces in credential strings

### Upload Failures

Common causes:
- Invalid image URL (returns 404)
- Image format not supported
- Network connectivity issues

## Examples

### Example 1: Minimal Setup (Sandbox)

```bash
python scaleflex_processor.py \
  --input products.csv \
  --output results.csv \
  --image-url-column "url" \
  --sandbox
```

### Example 2: Full Metadata Upload

```bash
python scaleflex_processor.py \
  --input products.csv \
  --output results.csv \
  --api-token "abc123..." \
  --filerobot-token "mytoken" \
  --image-url-column "product_image" \
  --brand-column "manufacturer" \
  --title-column "product_name" \
  --description-column "details"
```

### Example 3: Custom Preset

```bash
python scaleflex_processor.py \
  --input products.csv \
  --output results.csv \
  --api-token "abc123..." \
  --filerobot-token "mytoken" \
  --image-url-column "image_url" \
  --preset "my_custom_preset"
```

## Support

For issues with:
- **Script functionality**: Check the error messages and troubleshooting guide above
- **Scaleflex API**: Contact [Scaleflex Support](https://www.scaleflex.com/contact-us)
- **API credentials**: Visit [Scaleflex Hub](https://hub.filerobot.com)
