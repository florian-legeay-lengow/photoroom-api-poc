"""
Scaleflex Image Processor
This script processes images from a CSV file using Scaleflex's DAM API.
"""

import pandas as pd
import requests
import argparse
import sys
import time
from typing import Optional, Dict, Any


# Default configuration constants
DEFAULT_INPUT_CSV = "test_files/dior_feed.csv"
DEFAULT_OUTPUT_CSV = "test_files/dior_feed_processed.csv"
DEFAULT_IMAGE_URL_COLUMN = "image_link" # "image_link"
DEFAULT_BRAND_COLUMN = "brand" # "brand"
DEFAULT_TITLE_COLUMN = "title" # "title"
DEFAULT_DESCRIPTION_COLUMN = "description" #None
DEFAULT_EAN_COLUMN = None
DEFAULT_GTIN_COLUMN = "gtin" # "gtin"
DEFAULT_PRODUCT_ID_COLUMN = "id" # "id"
DEFAULT_PRESET = "amz_hero"
DEFAULT_FOLDER = "/Products/TEST_FLE"
DEFAULT_ROW_LIMIT = 150  # None means process all rows
DEFAULT_ROW_DELIMITER = '|'  # Change to '|' if your CSV uses pipe delimiter


class ScaleflexProcessor:
    """Process images using Scaleflex DAM API."""
    
    def __init__(self, api_token: str, filerobot_token: str, sandbox_mode: bool = True):
        """
        Initialize Scaleflex processor.
        
        Args:
            api_token: Filerobot API key (X-Filerobot-Key)
            filerobot_token: Filerobot project token
            sandbox_mode: Whether to run in sandbox mode (no actual API calls)
        """
        self.api_token = api_token
        self.filerobot_token = filerobot_token
        self.sandbox_mode = sandbox_mode
        self.base_url = f"https://api.filerobot.com/{filerobot_token}/v5/files"
        
    def get_file_details(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """
        Get file details by UUID from Scaleflex DAM.
        
        Args:
            file_uuid: UUID of the file to retrieve
            
        Returns:
            Response data with file details or None if failed
        """
        if self.sandbox_mode:
            print(f"[SANDBOX] Would retrieve file details for UUID: {file_uuid}")
            return {
                "status": "success",
                "file": {
                    "uuid": file_uuid,
                    "name": "mock-file.jpg",
                    "url": {
                        "cdn": f"https://{self.filerobot_token}.filerobot.com/mock/path/mock-file.jpg?vh=abc123"
                    }
                }
            }
        
        # Prepare headers
        headers = {
            "X-Filerobot-Key": self.api_token
        }
        
        # Build URL for get file details endpoint
        url = f"https://api.filerobot.com/{self.filerobot_token}/v5/files/{file_uuid}"
        
        try:
            print(f"Retrieving file details for UUID: {file_uuid}")
            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )
            
            # Try to parse JSON response
            try:
                data = response.json()
            except ValueError:
                print(f"✗ Invalid JSON response from get file details API")
                print(f"   Status code: {response.status_code}")
                print(f"   Response text: {response.text[:500]}")
                return None
            
            if data.get("status") == "success":
                print(f"✓ Successfully retrieved file details for UUID: {file_uuid}")
                return data
            else:
                print(f"✗ Failed to retrieve file details: {data.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error retrieving file details: {str(e)}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text[:500]}")
            return None
    
    def upload_image(
        self, 
        image_url: str, 
        brand: Optional[str] = None,
        title: Optional[str] = None, 
        description: Optional[str] = None,
        ean: Optional[str] = None,
        gtin: Optional[str] = None,
        product_id: Optional[str] = None,
        folder: str = DEFAULT_FOLDER
    ) -> Optional[Dict[str, Any]]:
        """
        Upload an image to Scaleflex DAM with metadata.
        
        Args:
            image_url: URL of the image to upload
            brand: Brand name
            title: Product title
            description: Product description
            ean: EAN code
            gtin: GTIN code
            product_id: Product ID
            folder: Destination folder in DAM
            
        Returns:
            Response data with CDN URL or None if failed
        """
        # Trim whitespace from image URL
        image_url = image_url.strip() if image_url else image_url
        
        if self.sandbox_mode:
            print(f"[SANDBOX] Would upload: {image_url}")
            # Return mock response in sandbox mode
            return {
                "status": "success",
                "file": {
                    "uuid": "mock-uuid-123",
                    "name": image_url.split('/')[-1],
                    "url": {
                        "cdn": f"https://{self.filerobot_token}.filerobot.com{folder}/{image_url.split('/')[-1]}?vh=abc123"
                    }
                }
            }
        
        # Prepare metadata
        meta = {}
        if brand and str(brand).strip():
            meta["brand"] = str(brand).strip()
        if title and str(title).strip():
            meta["title"] = str(title).strip()
        if description and str(description).strip():
            meta["description"] = str(description).strip()
        if ean and str(ean).strip():
            meta["ean"] = str(ean).strip()
        if gtin and str(gtin).strip():
            meta["gtin"] = str(gtin).strip()
        if product_id and str(product_id).strip():
            meta["product_id"] = str(product_id).strip()
        
        # Prepare request payload
        payload = {
            "files_urls": [
                {
                    "url": image_url,
                }
            ]
        }
        
        # Add metadata if provided
        if meta:
            payload["files_urls"][0]["meta"] = meta
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "X-Filerobot-Key": self.api_token
        }
        
        # Prepare query parameters
        params = {
            "folder": folder,
            "upload_beta": "true"  # Enable new response format
        }
        
        try:
            print(f"Uploading: {image_url}")
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                params=params,
                timeout=30
            )
            
            # Try to parse JSON response regardless of status code
            try:
                data = response.json()
            except ValueError:
                print(f"✗ Invalid JSON response from API")
                print(f"   Status code: {response.status_code}")
                print(f"   Response text: {response.text[:500]}")
                return None
            
            # Check for error status in the response
            if data.get("status") == "error":
                error_code = data.get("code", "UNKNOWN_ERROR")
                error_msg = data.get("msg", "Unknown error")
                error_hint = data.get("hint", "")
                existing_uuid = data.get("existing_file_uuid", "")
                
                # Special handling for SAME_ASSET_EXISTS_SKIP_UPLOAD
                if error_code == "SAME_ASSET_EXISTS_SKIP_UPLOAD" and existing_uuid:
                    print(f"⚠ File already exists: {image_url}")
                    print(f"   Existing file UUID: {existing_uuid}")
                    print(f"   Retrieving existing file details...")
                    
                    # Get file details for existing file
                    file_details = self.get_file_details(existing_uuid)
                    
                    if file_details and file_details.get("status") == "success":
                        # Extract CDN URL and return as successful upload
                        cdn_url = file_details["file"]["url"]["cdn"]
                        print(f"✓ Using existing file CDN URL: {cdn_url}")
                        
                        # Return success response with existing file data
                        return {
                            "status": "success",
                            "file": file_details["file"],
                            "reused_existing": True
                        }
                    else:
                        print(f"✗ Failed to retrieve existing file details")
                        # Fall through to return error
                
                # For other errors or if retrieval failed
                print(f"✗ Upload failed: {image_url}")
                print(f"   Error Code: {error_code}")
                print(f"   Message: {error_msg}")
                if error_hint:
                    print(f"   Hint: {error_hint}")
                if existing_uuid and error_code != "SAME_ASSET_EXISTS_SKIP_UPLOAD":
                    print(f"   Existing file UUID: {existing_uuid}")
                
                # Return error data for tracking
                return {
                    "status": "error",
                    "error_code": error_code,
                    "error_msg": error_msg,
                    "error_hint": error_hint,
                    "existing_file_uuid": existing_uuid,
                    "response": data
                }
            
            # Check HTTP status code
            if response.status_code >= 400:
                error_code = data.get("code", f"HTTP_{response.status_code}")
                error_msg = data.get("msg") or data.get("message", "Unknown error")
                
                print(f"✗ Upload failed: {image_url}")
                print(f"   HTTP Status: {response.status_code}")
                print(f"   Error Code: {error_code}")
                print(f"   Message: {error_msg}")
                
                return {
                    "status": "error",
                    "error_code": error_code,
                    "error_msg": error_msg,
                    "http_status": response.status_code,
                    "response": data
                }
            
            # Success case
            if data.get("status") == "success":
                print(f"✓ Successfully uploaded: {image_url}")
                return data
            else:
                # Unexpected response format
                print(f"✗ Unexpected response format for: {image_url}")
                print(f"   Status: {data.get('status', 'unknown')}")
                print(f"   Response: {str(data)[:200]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Network error uploading {image_url}: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text[:500]}")
            return None
    
    def add_preset_to_url(self, cdn_url: str, preset_name: str = "amz_hero") -> str:
        """
        Add a preset parameter to the CDN URL.
        
        Args:
            cdn_url: Original CDN URL
            preset_name: Name of the preset to apply
            
        Returns:
            Modified URL with preset parameter
        """
        # Check if URL already has query parameters
        separator = "&" if "?" in cdn_url else "?"
        
        # Add preset parameter
        preset_url = f"{cdn_url}{separator}p={preset_name}"
        
        return preset_url
    
    def process_csv(
        self,
        input_csv: str,
        output_csv: str,
        image_url_column: str,
        brand_column: Optional[str] = None,
        title_column: Optional[str] = None,
        description_column: Optional[str] = None,
        ean_column: Optional[str] = None,
        gtin_column: Optional[str] = None,
        product_id_column: Optional[str] = None,
        preset_name: str = "amz_hero",
        row_limit: Optional[int] = None
    ) -> bool:
        """
        Process a CSV file with product images.
        
        Args:
            input_csv: Path to input CSV file
            output_csv: Path to output CSV file
            image_url_column: Name of column containing image URLs
            brand_column: Name of column containing brand names
            title_column: Name of column containing product titles
            description_column: Name of column containing descriptions
            ean_column: Name of column containing EAN codes
            gtin_column: Name of column containing GTIN codes
            product_id_column: Name of column containing product IDs
            preset_name: Name of the preset to apply to CDN URLs
            row_limit: Maximum number of rows to process (None = process all)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read CSV file with robust parsing options
            print(f"\nReading CSV file: {input_csv}")
            df = pd.read_csv(
                input_csv,
                encoding='utf-8',
                sep=DEFAULT_ROW_DELIMITER,              # Use pipe delimiter
                on_bad_lines='warn',  # Skip bad lines instead of failing
                engine='python',      # Use Python engine for better error handling
                quoting=1,            # QUOTE_ALL - handle quoted fields properly
                escapechar='\\'       # Handle escape characters
            )
            print(f"Found {len(df)} rows")
            
            # Limit rows if specified
            if row_limit is not None and row_limit > 0:
                df = df.head(row_limit)
                print(f"Processing only first {len(df)} rows (limit: {row_limit})")
            
            # Validate required column exists
            if image_url_column not in df.columns:
                print(f"✗ Error: Column '{image_url_column}' not found in CSV")
                print(f"Available columns: {', '.join(df.columns)}")
                return False
            
            # Initialize new columns
            df['scaleflex_cdn_url'] = None
            df['scaleflex_preset_url'] = None
            df['scaleflex_status'] = None
            df['processing_time_seconds'] = None
            
            # Process each row
            success_count = 0
            fail_count = 0
            processing_times = []
            global_start_time = time.time()
            
            for idx, row in df.iterrows():
                product_start_time = time.time()
                
                image_url = row[image_url_column]
                
                # Trim whitespace from URL
                if image_url and isinstance(image_url, str):
                    image_url = image_url.strip()
                
                # Skip empty URLs
                if pd.isna(image_url) or not image_url:
                    df.at[idx, 'scaleflex_status'] = 'skipped_empty_url'
                    df.at[idx, 'processing_time_seconds'] = 0
                    continue
                
                # Extract metadata from columns if specified
                brand = row[brand_column] if brand_column and brand_column in df.columns else None
                title = row[title_column] if title_column and title_column in df.columns else None
                description = row[description_column] if description_column and description_column in df.columns and not pd.isna(row[description_column]) else None
                ean = row[ean_column] if ean_column and ean_column in df.columns and not pd.isna(row[ean_column]) else None
                gtin = row[gtin_column] if gtin_column and gtin_column in df.columns and not pd.isna(row[gtin_column]) else None
                product_id = row[product_id_column] if product_id_column and product_id_column in df.columns else None
                
                # Upload image
                result = self.upload_image(
                    image_url=image_url,
                    brand=brand,
                    title=title,
                    description=description,
                    ean=ean,
                    gtin=gtin,
                    product_id=product_id
                )
                
                if result and result.get("status") == "success":
                    # Extract CDN URL
                    cdn_url = result["file"]["url"]["cdn"]
                    
                    # Add preset to URL
                    preset_url = self.add_preset_to_url(cdn_url, preset_name)
                    
                    # Update dataframe
                    df.at[idx, 'scaleflex_cdn_url'] = cdn_url
                    df.at[idx, 'scaleflex_preset_url'] = preset_url
                    df.at[idx, 'scaleflex_status'] = 'success'
                    
                    success_count += 1
                elif result and result.get("status") == "error":
                    # Store error details
                    error_code = result.get("error_code", "UNKNOWN")
                    error_msg = result.get("error_msg", "Unknown error")
                    df.at[idx, 'scaleflex_status'] = f'error: {error_code}'
                    df.at[idx, 'scaleflex_cdn_url'] = error_msg
                    fail_count += 1
                else:
                    df.at[idx, 'scaleflex_status'] = 'failed'
                    fail_count += 1
                
                # Calculate and store processing time for this product
                product_end_time = time.time()
                product_time = product_end_time - product_start_time
                df.at[idx, 'processing_time_seconds'] = round(product_time, 2)
                processing_times.append(product_time)
                
                print(f"   Processing time: {product_time:.2f}s")
                
                # Add a small delay to avoid rate limiting
                if not self.sandbox_mode:
                    time.sleep(0.5)
            
            # Save output CSV
            print(f"\nSaving results to: {output_csv}")
            df.to_csv(output_csv, index=False)
            
            # Calculate timing statistics
            global_end_time = time.time()
            total_time = global_end_time - global_start_time
            avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Print summary
            print("\n" + "="*60)
            print("PROCESSING SUMMARY")
            print("="*60)
            print(f"Total rows: {len(df)}")
            print(f"Successfully processed: {success_count}")
            print(f"Failed: {fail_count}")
            print(f"Skipped: {len(df) - success_count - fail_count}")
            print(f"\n--- TIMING STATISTICS ---")
            print(f"Total processing time: {total_time:.2f}s ({total_time/60:.2f} minutes)")
            print(f"Average time per product: {avg_time:.2f}s")
            if processing_times:
                print(f"Fastest product: {min(processing_times):.2f}s")
                print(f"Slowest product: {max(processing_times):.2f}s")
            print(f"\nOutput saved to: {output_csv}")
            print("="*60)
            
            return True
            
        except FileNotFoundError:
            print(f"✗ Error: Input file '{input_csv}' not found")
            return False
        except Exception as e:
            print(f"✗ Error processing CSV: {str(e)}")
            return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Process product images using Scaleflex DAM API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process CSV in sandbox mode (no actual API calls)
  python scaleflex_processor.py --input products.csv --output products_processed.csv \\
    --image-url-column "image_url" --sandbox
  
  # Process CSV with full metadata
  python scaleflex_processor.py --input products.csv --output products_processed.csv \\
    --api-token "YOUR_API_TOKEN" --filerobot-token "YOUR_TOKEN" \\
    --image-url-column "image_url" --brand-column "brand" \\
    --title-column "title" --description-column "description" \\
    --preset "amz_hero"
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT_CSV,
        help=f"Path to input CSV file (default: {DEFAULT_INPUT_CSV})"
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_CSV,
        help=f"Path to output CSV file (default: {DEFAULT_OUTPUT_CSV})"
    )
    parser.add_argument(
        "--image-url-column",
        default=DEFAULT_IMAGE_URL_COLUMN,
        help=f"Name of column containing image URLs (default: {DEFAULT_IMAGE_URL_COLUMN})"
    )
    
    # API credentials
    parser.add_argument(
        "--api-token",
        help="Filerobot API token (X-Filerobot-Key)"
    )
    parser.add_argument(
        "--filerobot-token",
        help="Filerobot project token"
    )
    
    # Optional metadata columns
    parser.add_argument(
        "--brand-column",
        default=DEFAULT_BRAND_COLUMN,
        help=f"Name of column containing brand names (default: {DEFAULT_BRAND_COLUMN})"
    )
    parser.add_argument(
        "--title-column",
        default=DEFAULT_TITLE_COLUMN,
        help=f"Name of column containing product titles (default: {DEFAULT_TITLE_COLUMN})"
    )
    parser.add_argument(
        "--description-column",
        default=DEFAULT_DESCRIPTION_COLUMN,
        help=f"Name of column containing product descriptions (default: {DEFAULT_DESCRIPTION_COLUMN})"
    )
    parser.add_argument(
        "--ean-column",
        default=DEFAULT_EAN_COLUMN,
        help=f"Name of column containing EAN codes (default: {DEFAULT_EAN_COLUMN})"
    )
    parser.add_argument(
        "--gtin-column",
        default=DEFAULT_GTIN_COLUMN,
        help=f"Name of column containing GTIN codes (default: {DEFAULT_GTIN_COLUMN})"
    )
    parser.add_argument(
        "--product-id-column",
        default=DEFAULT_PRODUCT_ID_COLUMN,
        help=f"Name of column containing product IDs (default: {DEFAULT_PRODUCT_ID_COLUMN})"
    )
    
    # Preset configuration
    parser.add_argument(
        "--preset",
        default=DEFAULT_PRESET,
        help=f"Preset name to apply to CDN URLs (default: {DEFAULT_PRESET})"
    )
    
    # Row limit
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_ROW_LIMIT,
        help="Maximum number of rows to process (default: process all rows)"
    )
    
    # Sandbox mode
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="Run in sandbox mode (no actual API calls)"
    )
    
    args = parser.parse_args()
    
    # Validate credentials unless in sandbox mode
    if not args.sandbox:
        if not args.filerobot_token:
            print("✗ Error: --filerobot-token is required unless --sandbox is specified")
            sys.exit(1)
        if not args.api_token:
            print("✗ Error: --api-token is required unless --sandbox is specified")
            sys.exit(1)
    else:
        # Use dummy values in sandbox mode
        args.api_token = args.api_token or "sandbox-api-token"
        args.filerobot_token = args.filerobot_token or "sandbox-token"
    
    # Print configuration
    print("\n" + "="*60)
    print("SCALEFLEX PROCESSOR CONFIGURATION")
    print("="*60)
    print(f"Mode: {'SANDBOX' if args.sandbox else 'PRODUCTION'}")
    print(f"Input CSV: {args.input}")
    print(f"Output CSV: {args.output}")
    print(f"Image URL column: {args.image_url_column}")
    print(f"Brand column: {args.brand_column or 'Not specified'}")
    print(f"Title column: {args.title_column or 'Not specified'}")
    print(f"Description column: {args.description_column or 'Not specified'}")
    print(f"Preset: {args.preset}")
    print(f"Row limit: {args.limit if args.limit else 'None (process all)'}")
    print("="*60 + "\n")
    
    # Create processor
    processor = ScaleflexProcessor(
        api_token=args.api_token,
        filerobot_token=args.filerobot_token,
        sandbox_mode=args.sandbox
    )
    
    # Process CSV
    success = processor.process_csv(
        input_csv=args.input,
        output_csv=args.output,
        image_url_column=args.image_url_column,
        brand_column=args.brand_column,
        title_column=args.title_column,
        description_column=args.description_column,
        ean_column=args.ean_column,
        gtin_column=args.gtin_column,
        product_id_column=args.product_id_column,
        preset_name=args.preset,
        row_limit=args.limit
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
