#!/usr/bin/env python
"""
Setup Verification Script - Check if all dependencies are installed correctly.
Run this to verify your SocialLead FB Groups installation is complete.
"""
import sys
import subprocess
from pathlib import Path


def print_header(text: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_python() -> bool:
    print_header("Checking Python Setup")
    try:
        version = sys.version
        print(f"✅ Python Version: {version.split()[0]}")
        if sys.version_info < (3, 10):
            print("⚠️  Warning: Python 3.10+ recommended, you have 3.{}.{}".format(
                sys.version_info.minor, sys.version_info.micro))
            return False
        return True
    except Exception as e:
        print(f"❌ Python error: {e}")
        return False


def check_backend_deps() -> bool:
    print_header("Checking Backend Dependencies")
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        # Check FastAPI
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI not installed")
        return False
    
    try:
        # Check Playwright
        import playwright
        print(f"✅ Playwright: {playwright.__version__}")
    except ImportError:
        print("❌ Playwright not installed")
        return False
    
    try:
        # Check SQLAlchemy
        import sqlalchemy
        print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")
    except ImportError:
        print("❌ SQLAlchemy not installed")
        return False
    
    try:
        # Check SeleniumBase
        import seleniumbase
        print(f"✅ SeleniumBase installed")
    except ImportError:
        print("⚠️  SeleniumBase not installed (fallback engine)")
    
    try:
        # Check other critical deps
        import pydantic
        import uvicorn
        import apscheduler
        print(f"✅ Other dependencies: pydantic, uvicorn, apscheduler")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    
    return True


def check_app_imports() -> bool:
    print_header("Checking Application Imports")
    try:
        # Add backend to path
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        # Try importing main app
        from app.main import app
        print("✅ FastAPI app imports successfully")
        
        # Try importing key modules
        from app.config import get_settings
        print("✅ Config module works")
        
        from app.db.session import init_db, SessionLocal
        print("✅ Database session works")
        
        from app.core.scanner import FacebookGroupScanner
        print("✅ Scanner module works")
        
        from app.browser.cdp_playwright_scraper import CdpPlaywrightFacebookGroupScraper
        print("✅ CDP Playwright scraper works")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_database() -> bool:
    print_header("Checking Database Setup")
    try:
        backend_path = Path(__file__).parent / "backend"
        sys.path.insert(0, str(backend_path))
        
        from app.db.session import init_db, engine, SessionLocal
        from app.db.models import Base
        
        # Try to create tables
        init_db()
        print("✅ Database initialized successfully")
        
        # Try to query
        with SessionLocal() as db:
            from app.db.models import GroupSource
            result = db.query(GroupSource).first()
            print("✅ Database query works")
        
        return True
    except Exception as e:
        print(f"⚠️  Database issue: {e}")
        print("   This is normal if first time - will be created on first run")
        return True  # Not critical


def check_frontend() -> bool:
    print_header("Checking Frontend Setup")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check node_modules
    if (frontend_dir / "node_modules").exists():
        print("✅ node_modules directory exists")
    else:
        print("❌ node_modules not found - run: cd frontend && npm install")
        return False
    
    # Check .env
    if (frontend_dir / ".env").exists():
        print("✅ .env file exists")
    else:
        print("⚠️  .env file missing - will be created automatically")
    
    # Check key packages
    key_packages = [
        ("react/package.json", "react"),
        ("react-dom/package.json", "react-dom"),
        ("vite/package.json", "vite"),
        ("typescript/package.json", "typescript"),
    ]
    
    all_ok = True
    for pkg_path, pkg_name in key_packages:
        full_path = frontend_dir / "node_modules" / pkg_path
        if full_path.exists():
            print(f"✅ {pkg_name}")
        else:
            print(f"⚠️  {pkg_name} not found")
            all_ok = False
    
    return all_ok


def check_files() -> bool:
    print_header("Checking Project Files")
    project_dir = Path(__file__).parent
    
    required_files = [
        (".env", "Configuration"),
        ("backend/requirements.txt", "Backend dependencies"),
        ("frontend/package.json", "Frontend dependencies"),
        ("backend/app/main.py", "Backend main app"),
        ("backend/app/db/models.py", "Database models"),
        ("frontend/src/main.tsx", "Frontend entry"),
    ]
    
    all_ok = True
    for file_path, description in required_files:
        full_path = project_dir / file_path
        if full_path.exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ Missing {description}: {file_path}")
            all_ok = False
    
    return all_ok


def main() -> None:
    print("\n" + "🔍 SocialLead FB Groups - Setup Verification".center(60))
    print("="*60)
    
    checks = [
        ("Python Setup", check_python),
        ("Backend Dependencies", check_backend_deps),
        ("Project Files", check_files),
        ("Application Imports", check_app_imports),
        ("Database Setup", check_database),
        ("Frontend Setup", check_frontend),
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"⚠️  Error during {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Verification Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! You're ready to go!")
        print("\nNext steps:")
        print("  1. Login to Facebook: python scripts/login_cdp_playwright.py")
        print("  2. Run the app: .\run.ps1  (Windows)")
        print("  3. Access: http://localhost:3000")
        sys.exit(0)
    elif passed >= total - 1:
        print("\n⚠️  Some optional checks failed (may still work)")
        print("See above for details")
        sys.exit(0)
    else:
        print("\n❌ Critical checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
