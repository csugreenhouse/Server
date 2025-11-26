import importlib
from pathlib import Path
import os
import pytest
from processing import height

# Make sure Python can import "Server.processing.height" no matter the CWD
ROOT = Path(__file__).resolve().parents[2]  # repo root (contains "Server")
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))
    
BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images" / "test_estimate_height"

def test_estimate_height_01():
    src = IMG_DIR / "TEST01.jpg"
    dst = IMG_DIR / "TEST01_out.png"
    
    mod = importlib.import_module("Server.processing.height")
    assert hasattr(mod, "estimated_height"), "estimated_height() not found"
    
    estimated_height = mod.estimated_height(str(src))
    mod.plot_image(str(src), str(dst), estimated_height=estimated_height)
    
    print(f"Estimated height: {estimated_height} m")
    
    assert estimated_height == pytest.approx(.0256, rel=.01) 


    

    