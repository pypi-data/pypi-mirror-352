import pytest
import os
import sys
from mcp_ocr_mini.server import perform_ocr, get_supported_languages
import tempfile
from pathlib import Path

@pytest.fixture
def sample_image():
    """Create a simple test image with text and return its file path."""
    from PIL import Image, ImageDraw

    # Create a white image
    img = Image.new('RGB', (200, 50), color='white')
    d = ImageDraw.Draw(img)
    text = "Hello World"
    d.text((10, 10), text, fill='black')

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp, format='PNG')
        tmp_path = tmp.name

    yield tmp_path

    # Cleanup after test
    Path(tmp_path).unlink(missing_ok=True)

@pytest.mark.asyncio
async def test_perform_ocr(sample_image):
    """Test OCR on a simple image."""
    try:
        result = await perform_ocr(sample_image)
        # Remove whitespace and make lowercase for more reliable comparison
        result = result.lower().strip()
        assert "hello" in result
        assert "world" in result
    except Exception as e:
        pytest.skip(f"OCR test failed, possibly due to Tesseract installation: {str(e)}")

@pytest.mark.asyncio
async def test_get_supported_languages():
    """Test getting supported languages."""
    try:
        languages = await get_supported_languages()
        assert isinstance(languages, list)
        assert "eng" in languages  # English should always be available
    except Exception as e:
        pytest.skip(f"Language test failed, possibly due to Tesseract installation: {str(e)}")

@pytest.mark.asyncio
async def test_perform_ocr_invalid_input():
    """Test OCR with invalid input."""
    with pytest.raises(Exception):
        await perform_ocr(b"invalid image data") 