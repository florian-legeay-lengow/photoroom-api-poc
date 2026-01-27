"""
Photoroom API - Background Removal POC
Simple script to process images using Photoroom's API
"""

import os
import requests
from pathlib import Path
from typing import Optional
import time


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
        image_path: str,
        output_path: str,
        bg_color: Optional[str] = None,
        size: str = "full",
        format: str = "png",
        crop: bool = False,
        despill: bool = False,
        output_size: Optional[str] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        padding: Optional[float] = None
    ) -> bool:
        """
        Process a single image through Photoroom API
        
        Args:
            image_path: Path to input image
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
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare the image file
            with open(image_path, 'rb') as image_file:
                if self.use_v2:
                    # v2/edit endpoint (Plus Plan)
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
                
                # Check response
                if response.status_code == 200:
                    # Save processed image
                    with open(output_path, 'wb') as out_file:
                        out_file.write(response.content)
                    print(f"✓ Success: {Path(output_path).name}")
                    return True
                else:
                    print(f"✗ Error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"✗ Error processing {Path(image_path).name}: {str(e)}")
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
                str(image_file),
                str(output_path),
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


def main():
    """Main function to run the processor"""
    
    # ============================================
    # CONFIGURATION - Edit these values
    # ============================================
    
    # Your Photoroom API key
    API_KEY = "17ddbd6e5f1fd30f60b21f13f8176c47d6475432"
    
    # Sandbox mode (for testing without consuming credits)
    SANDBOX_MODE = True  # Set to False for production
    
    # API Version - v2 supports custom dimensions (Plus Plan required)
    USE_V2 = True  # Set to True for v2/edit endpoint with custom dimensions
    
    # Input and output folders
    INPUT_FOLDER = "input_images"
    OUTPUT_FOLDER = "output_images"
    
    # ============================================
    # AMAZON MARKETPLACE IMAGE REQUIREMENTS
    # ============================================
    # Background: White solid (#FFFFFF)
    # Dimensions: 2000x2000px (recommended), min 500x500px
    # Aspect Ratio: 1:1 (square)
    # Format: JPEG (preferred for smaller file size)
    # Product must fill 85% of image
    # ============================================
    
    # Processing options
    BG_COLOR = 'FFFFFF'  # White background (Amazon requirement)
    SIZE = "hd"  # (v1 only) Options: preview, medium, hd, full
    FORMAT = "jpg"  # JPEG format (Amazon compatible, smaller file size)
    CROP = False  # Keep at False to maintain 1:1 aspect ratio
    DESPILL = False  # Remove green screen reflections (v1 only)
    
    # Custom dimensions (v2 only - requires Plus Plan)
    OUTPUT_SIZE = "2000x2000"  # Amazon recommended: 2000x2000px (1:1 aspect ratio)
    MAX_WIDTH = None   # Not needed when OUTPUT_SIZE is specified
    PADDING = 0.075    # 7.5% padding = ~85% product fill (Amazon requirement)
    MAX_HEIGHT = None  # Not needed when OUTPUT_SIZE is specified
    
    # ============================================
    
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
    else:
        print(f"Output Size: {SIZE}")
        print(f"Despill: {DESPILL}")
    
    print(f"Output Format: {FORMAT}")
    print(f"Crop: {CROP}")
    print("=" * 50)
    
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
