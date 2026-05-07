"""
Basic tests without heavy dependencies
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


def test_imports():
    """Test that core modules can be imported"""
    try:
        from app.core import config
        print("✓ Config module imports successfully")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        from app.services import sequence_processor
        print("✓ Sequence processor module imports successfully")
    except Exception as e:
        print(f"✗ Sequence processor import failed: {e}")
        return False
    
    return True


def test_config():
    """Test configuration"""
    from app.core.config import settings
    
    assert settings.APP_NAME is not None
    assert settings.APP_VERSION is not None
    assert settings.MODEL_DEVICE in ['cpu', 'cuda']
    
    print(f"✓ Configuration loaded")
    print(f"  App: {settings.APP_NAME}")
    print(f"  Version: {settings.APP_VERSION}")
    print(f"  Device: {settings.MODEL_DEVICE}")
    
    return True


def test_file_structure():
    """Test that required files exist"""
    backend_dir = Path(__file__).parent.parent
    
    required_files = [
        'app/main.py',
        'app/core/config.py',
        'app/models/deep_learning.py',
        'app/services/sequence_processor.py',
        'app/api/analysis.py',
        'requirements.txt',
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    return all_exist


def test_directory_structure():
    """Test that required directories exist"""
    backend_dir = Path(__file__).parent.parent
    
    required_dirs = [
        'app',
        'app/api',
        'app/core',
        'app/models',
        'app/services',
        'training',
        'scripts',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = backend_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✓ {dir_path}/ exists")
        else:
            print(f"✗ {dir_path}/ missing")
            all_exist = False
    
    return all_exist


if __name__ == '__main__':
    print("Running Basic Tests...")
    print("=" * 60)
    
    results = []
    
    print("\n1. Testing File Structure...")
    print("-" * 60)
    results.append(test_file_structure())
    
    print("\n2. Testing Directory Structure...")
    print("-" * 60)
    results.append(test_directory_structure())
    
    print("\n3. Testing Imports...")
    print("-" * 60)
    results.append(test_imports())
    
    print("\n4. Testing Configuration...")
    print("-" * 60)
    results.append(test_config())
    
    print("\n" + "=" * 60)
    if all(results):
        print("All basic tests passed! ✓")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r backend/requirements.txt")
        print("2. Run full tests: python backend/tests/test_models.py")
        print("3. Start backend: python backend/app/main.py")
    else:
        print("Some tests failed! ✗")
        sys.exit(1)
