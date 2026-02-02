"""
Photoroom API - Background Removal POC
Simple script to process images using Photoroom's API
"""

import os
import requests
from pathlib import Path
from typing import Optional
import time
import csv
from datetime import datetime


# ============================================
# CONFIGURATION CONSTANTS
# ============================================

# CSV Column Configuration
IMAGE_URL_COLUMN = "image_link"  # Column name in CSV for image URLs
CSV_DELIMITER = ","  # CSV delimiter character (e.g., "," or "|")

# API Configuration
API_KEY = "17ddbd6e5f1fd30f60b21f13f8176c47d6475432"
SANDBOX_MODE = True  # Set to False for production
USE_V2 = True  # Set to True for v2/edit endpoint with custom dimensions

# Input/Output Configuration
INPUT_FOLDER = "input_images"
OUTPUT_FOLDER = "output_images"

# CSV Processing Configuration
USE_CSV = True  # Set to True to process CSV file, False to process folder
CSV_FILE = "test_files/Catalog One Vertical.csv"  # Path to CSV file
PROCESS_LIMIT = 1  # Limit number of items to process (None for all)

# ============================================
# AMAZON MARKETPLACE IMAGE REQUIREMENTS
# ============================================
# Background: White solid (#FFFFFF)
# Dimensions: 2000x2000px (recommended), min 500x500px
# Aspect Ratio: 1:1 (square)
# Format: JPEG (preferred for smaller file size)
# Product must fill 85% of image
# ============================================

# Processing Configuration
BG_COLOR = 'FFFFFF'  # White background (Amazon requirement)
SIZE = "hd"  # (v1 only) Options: preview, medium, hd, full
FORMAT = "jpg"  # JPEG format (Amazon compatible, smaller file size)
CROP = False  # Keep at False to maintain 1:1 aspect ratio
DESPILL = False  # Remove green screen reflections (v1 only)

# Custom Dimensions (v2 only - requires Plus Plan)
OUTPUT_SIZE = "2000x2000"  # Amazon recommended: 2000x2000px (1:1 aspect ratio)
MAX_WIDTH = None  # Not needed when OUTPUT_SIZE is specified
PADDING = 0.075  # 7.5% padding = ~85% product fill (Amazon requirement)
MAX_HEIGHT = None  # Not needed when OUTPUT_SIZE is specified


class PhotoroomProcessor:
    """Process images using Photoroom API"""
    
    def __init__(self, api_key: str, sandbox_mode: bool = False, use_v2: bool = False):
        """
        Initialize the processor
        
        Args:
            api_key: Your Photoroom API key
            sandbox_mode: If True, adds 'sandbox_' prefix to the token
            use_v2: If True, uses v2/edit endpoint (Plus Plan) with custom dimensions support
        """
        self.api_key = f"sandbox_{api_key}" if sandbox_mode else api_key
        self.use_v2 = use_v2
        self.base_url = "https://image-api.photoroom.com/v2/edit" if use_v2 else "https://sdk.photoroom.com/v1/segment"
        self.headers = {
            "x-api-key": self.api_key
        }
    
    def process_image(
        self,
        image_path: Optional[str] = None,
        output_path: str = "",
        bg_color: Optional[str] = None,
        size: str = "full",
        format: str = "png",
        crop: bool = False,
        despill: bool = False,
        output_size: Optional[str] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        padding: Optional[float] = None,
        image_url: Optional[str] = None
    ) -> bool:
        """
        Process a single image through Photoroom API
        
        Args:
            image_path: Path to input image (ignored if image_url is provided)
            output_path: Path to save processed image
            bg_color: Background color (hex or HTML color name), None for transparent
            size: Output size for v1 (preview, medium, hd, full)
            format: Output format (png, jpg, webp)
            crop: Crop to cutout border
            despill: Remove colored reflections from green backgrounds
            output_size: (v2 only) Custom dimensions "WIDTHxHEIGHT" (e.g., "1024x768"), 
                        "auto", "originalImage", or "croppedSubject"
            max_width: (v2 only) Maximum width in pixels (maintains aspect ratio)
            max_height: (v2 only) Maximum height in pixels (maintains aspect ratio)
            padding: (v2 only) Padding around subject (0-0.49). Lower = more fill. 
                    For 85% fill, use ~0.075 (7.5% padding = 85% product)
            image_url: (v2 only) URL of the image to process (alternative to image_path)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print("-" * 50)
            print(f"Starting processing for: {Path(image_path).name if image_path else image_url[:60]}")
            # Check if using URL (v2 only)
            if image_url and self.use_v2:
                # Use GET request with imageUrl parameter
                params = {
                    'imageUrl': image_url,
                    'export.format': format,
                    'removeBackground': 'true'
                }
                
                # Add custom dimensions for v2
                if output_size:
                    params['outputSize'] = output_size
                if max_width:
                    params['maxWidth'] = str(max_width)
                if max_height:
                    params['maxHeight'] = str(max_height)
                if crop:
                    params['outputSize'] = 'croppedSubject'
                if padding is not None:
                    params['padding'] = str(padding)
                
                # Add background color if specified
                if bg_color:
                    params['background.color'] = bg_color
                
                # Make GET request for URL-based processing
                print(f"Processing URL: {image_url[:60]}...")
                print(f"  API Endpoint: {self.base_url}")
                print(f"  Parameters: {params}")
                print(f"  Headers: {self.headers}")
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
            # File-based processing
            elif image_path:
                # Prepare the image file
                with open(image_path, 'rb') as image_file:
                    if self.use_v2:
                        # v2/edit endpoint (Plus Plan) with file upload
                        files = {'imageFile': image_file}
                        data = {
                            'export.format': format,
                            'removeBackground': 'true'
                        }
                    
                        # Add custom dimensions for v2
                        if output_size:
                            data['outputSize'] = output_size
                        if max_width:
                            data['maxWidth'] = str(max_width)
                        if max_height:
                            data['maxHeight'] = str(max_height)
                        if crop:
                            data['outputSize'] = 'croppedSubject'
                        if padding is not None:
                            data['padding'] = str(padding)
                        
                        # Add background color if specified
                        if bg_color:
                            data['background.color'] = bg_color
                    else:
                        # v1/segment endpoint (Basic Plan)
                        files = {'image_file': image_file}
                        data = {
                            'format': format,
                            'size': size,
                            'crop': 'true' if crop else 'false',
                            'despill': 'true' if despill else 'false'
                        }
                        
                        # Add background color if specified
                        if bg_color:
                            data['bg_color'] = bg_color
                    
                    # Make API request
                    print(f"Processing: {Path(image_path).name}...")
                    response = requests.post(
                        self.base_url,
                        headers=self.headers,
                        files=files,
                        data=data,
                        timeout=30
                    )
            else:
                print("Error: Either image_path or image_url must be provided")
                return False
                
            # Check response
            if response.status_code == 200:
                # Save processed image
                with open(output_path, 'wb') as out_file:
                    out_file.write(response.content)
                print(f"✓ Success: {Path(output_path).name}")
                return True
            else:
                # Detailed error logging
                print(f"✗ Error: HTTP {response.status_code}")
                print(f"  Response: {response.text}")
                if image_url:
                    print(f"  Source URL: {image_url}")
                elif image_path:
                    print(f"  Source File: {image_path}")
                print(f"  API Endpoint: {self.base_url}")
                return False
                    
        except Exception as e:
            error_name = Path(image_path).name if image_path else image_url[:60] if image_url else "unknown"
            print(f"✗ Exception processing {error_name}")
            print(f"  Error Type: {type(e).__name__}")
            print(f"  Error Message: {str(e)}")
            if image_url:
                print(f"  Source URL: {image_url}")
            return False
    
    def process_folder(
        self,
        input_folder: str,
        output_folder: str,
        bg_color: Optional[str] = None,
        size: str = "full",
        format: str = "png",
        crop: bool = False,
        despill: bool = False,
        output_size: Optional[str] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        padding: Optional[float] = None,
        extensions: tuple = ('.jpg', '.jpeg', '.png', '.webp')
    ):
        """
        Process all images in a folder
        
        Args:
            input_folder: Folder containing input images
            output_folder: Folder to save processed images
            bg_color: Background color (hex or HTML color name)
            size: Output size for v1 (preview, medium, hd, full)
            format: Output format (png, jpg, webp)
            crop: Crop to cutout border
            despill: Remove colored reflections
            output_size: (v2 only) Custom dimensions "WIDTHxHEIGHT"
            max_width: (v2 only) Maximum width in pixels
            max_height: (v2 only) Maximum height in pixels
            padding: (v2 only) Padding around subject (0-0.49)
            extensions: Tuple of file extensions to process
        """
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Get list of images
        input_path = Path(input_folder)
        image_files = [
            f for f in input_path.iterdir() 
            if f.is_file() and f.suffix.lower() in extensions
        ]
        
        if not image_files:
            print(f"No images found in {input_folder}")
            return
        
        print(f"\nFound {len(image_files)} images to process")
        print("=" * 50)
        
        # Process each image
        success_count = 0
        for image_file in image_files:
            # Generate output filename
            output_filename = f"{image_file.stem}_processed.{format}"
            output_path = Path(output_folder) / output_filename
            
            # Process image
            if self.process_image(
                image_path=str(image_file),
                output_path=str(output_path),
                bg_color=bg_color,
                size=size,
                format=format,
                crop=crop,
                despill=despill,
                output_size=output_size,
                max_width=max_width,
                max_height=max_height,
                padding=padding
            ):
                success_count += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        print("=" * 50)
        print(f"\nProcessing complete: {success_count}/{len(image_files)} successful")
    
    def process_csv(
        self,
        csv_path: str,
        output_folder: str,
        bg_color: Optional[str] = None,
        size: str = "full",
        format: str = "png",
        crop: bool = False,
        despill: bool = False,
        output_size: Optional[str] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        padding: Optional[float] = None,
        limit: Optional[int] = None
    ):
        """
        Process images from a CSV file containing image URLs
        
        Args:
            csv_path: Path to CSV file
            output_folder: Folder to save processed images
            bg_color: Background color (hex or HTML color name)
            size: Output size for v1 (preview, medium, hd, full)
            format: Output format (png, jpg, webp)
            crop: Crop to cutout border
            despill: Remove colored reflections
            output_size: (v2 only) Custom dimensions "WIDTHxHEIGHT"
            max_width: (v2 only) Maximum width in pixels
            max_height: (v2 only) Maximum height in pixels
            padding: (v2 only) Padding around subject (0-0.49)
            limit: Maximum number of items to process (None for all)
        """
        if not self.use_v2:
            print("Error: CSV processing with URLs requires v2 API (use_v2=True)")
            return
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Read CSV file
        rows = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=CSV_DELIMITER)
                if IMAGE_URL_COLUMN not in reader.fieldnames:
                    print(f"Error: Column '{IMAGE_URL_COLUMN}' not found in CSV")
                    print(f"Available columns: {', '.join(reader.fieldnames)}")
                    return
                
                for row in reader:
                    rows.append(row)
        except Exception as e:
            print(f"Error reading CSV file: {str(e)}")
            return
        
        # Apply limit if specified
        if limit:
            rows = rows[:limit]
            print(f"\nProcessing first {len(rows)} items (limit: {limit})")
        else:
            print(f"\nProcessing all {len(rows)} items")
        
        print("=" * 50)
        
        # Process each row
        success_count = 0
        for idx, row in enumerate(rows, 1):
            image_url = row.get(IMAGE_URL_COLUMN, '').strip()
            
            if not image_url:
                print(f"Row {idx}: No URL found, skipping...")
                continue
            
            # Generate output filename
            output_filename = f"row_{idx}_processed.{format}"
            output_path = Path(output_folder) / output_filename
            
            # Process image
            print(f"\n[{idx}/{len(rows)}] ", end='')
            if self.process_image(
                image_path=None,  # Not used for URL processing
                output_path=str(output_path),
                bg_color=bg_color,
                size=size,
                format=format,
                crop=crop,
                despill=despill,
                output_size=output_size,
                max_width=max_width,
                max_height=max_height,
                padding=padding,
                image_url=image_url
            ):
                success_count += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        print("=" * 50)
        print(f"\nProcessing complete: {success_count}/{len(rows)} successful")


def main():
    """Main function to run the processor"""
    
    # Initialize processor
    processor = PhotoroomProcessor(API_KEY, sandbox_mode=SANDBOX_MODE, use_v2=USE_V2)
    
    # Display configuration
    print("\n" + "=" * 50)
    print("PHOTOROOM API - BACKGROUND REMOVAL POC")
    print("=" * 50)
    print(f"API Version: {'v2/edit (Plus Plan)' if USE_V2 else 'v1/segment (Basic Plan)'}")
    print(f"Sandbox Mode: {'ON' if SANDBOX_MODE else 'OFF'}")
    print(f"Input Folder: {INPUT_FOLDER}")
    print(f"Output Folder: {OUTPUT_FOLDER}")
    print(f"Background Color: {BG_COLOR or 'Transparent'}")
    
    if USE_V2:
        print(f"Output Size: {OUTPUT_SIZE or 'auto'}")
        if MAX_WIDTH:
            print(f"Max Width: {MAX_WIDTH}px")
        if MAX_HEIGHT:
            print(f"Max Height: {MAX_HEIGHT}px")
        if PADDING is not None:
            print(f"Padding: {PADDING} (~{int((1-2*PADDING)*100)}% product fill)")
    else:
        print(f"Output Size: {SIZE}")
        print(f"Despill: {DESPILL}")
    
    print(f"Output Format: {FORMAT}")
    print(f"Crop: {CROP}")
    print("=" * 50)
    
    # Process based on mode
    if USE_CSV:
        print(f"\nMode: CSV Processing")
        print(f"CSV File: {CSV_FILE}")
        if PROCESS_LIMIT:
            print(f"Limit: {PROCESS_LIMIT} items")
        print()
        
        processor.process_csv(
            CSV_FILE,
            OUTPUT_FOLDER,
            bg_color=BG_COLOR,
            size=SIZE,
            format=FORMAT,
            crop=CROP,
            despill=DESPILL,
            output_size=OUTPUT_SIZE,
            padding=PADDING,
            max_width=MAX_WIDTH,
            max_height=MAX_HEIGHT,
            limit=PROCESS_LIMIT
        )
    else:
        print(f"\nMode: Folder Processing\n")
        
        # Process all images in the folder
        processor.process_folder(
            INPUT_FOLDER,
            OUTPUT_FOLDER,
            bg_color=BG_COLOR,
            size=SIZE,
            format=FORMAT,
            crop=CROP,
            despill=DESPILL,
            output_size=OUTPUT_SIZE,
            padding=PADDING,
            max_width=MAX_WIDTH,
            max_height=MAX_HEIGHT
        )


if __name__ == "__main__":
    main()
