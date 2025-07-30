import asyncio
import base64
from io import BytesIO
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from fastmcp import FastMCP
from PIL import Image

# Create an MCP server instance
# This serves as a dedicated server for retrieving OGP information
mcp = FastMCP("OGP Information Server")


async def fetch_html(url: str) -> str:
    """
    Asynchronously fetch HTML content from a specified URL.
    
    This function sends an HTTP request to a web page and returns the HTML content
    as a string. It includes timeout handling and error management for robust operation.
    
    Args:
        url: The target URL to fetch content from
        
    Returns:
        HTML content as a string
        
    Raises:
        httpx.HTTPError: When HTTP-related errors occur
        Exception: For any other unexpected errors
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        return response.text


def extract_ogp_info(html: str, base_url: str) -> Dict[str, Any]:
    """
    Extract Open Graph Protocol (OGP) information from HTML content.
    
    This function parses HTML content to find OGP meta tags and returns
    the information in a structured dictionary format. If OGP tags are not found,
    it attempts to extract alternative information from basic HTML tags (like title).
    
    Args:
        html: The HTML content to parse
        base_url: Base URL for converting relative URLs to absolute URLs
        
    Returns:
        Dictionary containing OGP information with possible keys:
        - title: Page title
        - description: Page description
        - image: OGP image URL
        - url: Page URL
        - type: Content type
        - site_name: Site name
    """
    soup = BeautifulSoup(html, 'html.parser')
    ogp_data = {}
    
    # Search for OGP meta tags and extract information
    # We look for meta tags with property attributes starting with "og:"
    ogp_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
    
    for tag in ogp_tags:
        property_name = tag.get('property')
        content = tag.get('content')
        
        if property_name and content:
            # Remove "og:" prefix to create clean key names
            key = property_name.replace('og:', '')
            ogp_data[key] = content
    
    # Fallback processing when OGP tags are not found
    # Attempt to extract basic information from standard HTML tags
    if 'title' not in ogp_data:
        title_tag = soup.find('title')
        if title_tag:
            ogp_data['title'] = title_tag.get_text().strip()
    
    if 'description' not in ogp_data:
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            ogp_data['description'] = desc_tag.get('content', '').strip()
    
    # Convert relative image URLs to absolute URLs
    if 'image' in ogp_data:
        ogp_data['image'] = urljoin(base_url, ogp_data['image'])
    
    return ogp_data


async def fetch_image_data(image_url: str) -> Optional[str]:
    """
    Fetch image data from a URL and return it as a Base64-encoded string.
    
    This function downloads an image file from the specified URL, processes it
    using the PIL library, and then performs Base64 encoding. This allows
    image data to be handled in text format for transmission.
    
    Args:
        image_url: The URL of the image to fetch
        
    Returns:
        Base64-encoded image data in data URL scheme format
        Returns None if fetching fails
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(image_url, follow_redirects=True)
            response.raise_for_status()
            
            # Process image data with PIL
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            
            # Optimize image (resize if necessary)
            # Large images can cause processing time and memory usage issues, so we limit them
            max_size = (1200, 1200)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert image to byte data
            output = BytesIO()
            # Preserve original format, convert to PNG if unsupported
            format_to_save = image.format if image.format in ['JPEG', 'PNG', 'GIF', 'WebP'] else 'PNG'
            image.save(output, format=format_to_save)
            output.seek(0)
            
            # Base64 encoding
            encoded_image = base64.b64encode(output.getvalue()).decode('utf-8')
            
            # Determine MIME type
            mime_type = {
                'JPEG': 'image/jpeg',
                'PNG': 'image/png',
                'GIF': 'image/gif',
                'WebP': 'image/webp'
            }.get(format_to_save, 'image/png')
            
            # Return in data URL scheme format
            return f"data:{mime_type};base64,{encoded_image}"
            
    except Exception as e:
        print(f"Image fetch error: {str(e)}")
        return None


@mcp.tool()
async def ogp_info(url: str) -> Dict[str, Any]:
    """
    Extract Open Graph Protocol (OGP) information from a specified URL.
    
    This function retrieves OGP metadata from web pages, which is commonly used
    for social media sharing previews. It extracts information like title,
    description, image URL, site name, and other OGP properties.
    
    Args:
        url: The URL of the web page to extract OGP information from
        
    Returns:
        Dictionary containing OGP metadata:
        - title: Page title
        - description: Page description
        - image: OGP image URL
        - url: Page URL
        - type: Content type
        - site_name: Site name
        - Other OGP properties as available
    """
    try:
        # Fetch HTML content from the target URL
        html_content = await fetch_html(url)
        
        # Extract OGP information from the HTML
        ogp_data = extract_ogp_info(html_content, url)
        
        # Return only the extracted OGP data
        return ogp_data
        
    except Exception as e:
        # Return empty dict on error to maintain consistent return type
        return {}


@mcp.tool()
async def ogp_image(url: str) -> Optional[str]:
    """
    Retrieve the OGP image from a specified URL and return it as Base64-encoded data.
    
    This function first extracts OGP information to locate the image URL,
    then downloads the image and converts it to Base64 format. This allows
    the image to be transmitted as text data in a data URL format.
    
    Args:
        url: The URL of the web page to extract the OGP image from
        
    Returns:
        Base64-encoded image data in data URL format (e.g., "data:image/jpeg;base64,...")
        Returns None if no image is found or if an error occurs
    """
    try:
        # First, extract OGP information to find the image URL
        html_content = await fetch_html(url)
        ogp_data = extract_ogp_info(html_content, url)
        
        # Check if OGP image URL exists
        image_url = ogp_data.get('image')
        if not image_url:
            return None
        
        # Fetch and process the image data
        image_data = await fetch_image_data(image_url)
        
        # Return the Base64-encoded image data directly
        return image_data
            
    except Exception as e:
        # Return None on any error to maintain consistent return type
        return None
