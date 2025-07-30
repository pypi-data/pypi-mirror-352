"""Test utilities and shared functions"""
import os
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Test cache directory
TEST_CACHE_DIR = Path(__file__).parent.parent / "test_cache"

def ensure_test_cache_dir():
    """Ensure test cache directory exists"""
    TEST_CACHE_DIR.mkdir(exist_ok=True)
    return TEST_CACHE_DIR

def generate_test_filename(base_name: str, extension: str = "jsonl") -> str:
    """Generate test filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"

def save_test_data(data: List[Dict[str, Any]], filename: str) -> Path:
    """Save test data to cache directory"""
    cache_dir = ensure_test_cache_dir()
    filepath = cache_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
    
    return filepath

def load_test_data(filename: str) -> List[Dict[str, Any]]:
    """Load test data from cache directory"""
    filepath = TEST_CACHE_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Test file does not exist: {filepath}")
    
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    
    return data

def cleanup_test_files(pattern: str = None):
    """Clean up test files"""
    if not TEST_CACHE_DIR.exists():
        return
    
    if pattern:
        # Clean files matching pattern
        for file in TEST_CACHE_DIR.glob(pattern):
            file.unlink()
    else:
        # Clean all test files
        for file in TEST_CACHE_DIR.iterdir():
            if file.is_file():
                file.unlink()

def create_sample_news_data(num_articles: int = 20) -> List[Dict[str, Any]]:
    """Create sample news data for testing"""
    news_topics = [
        ("Technology News", ["AI Artificial Intelligence", "Machine Learning", "Deep Learning", "Neural Networks", "Automation"]),
        ("Political News", ["Election Campaign", "Policy Reform", "Legislature", "Government Decisions", "Public Opinion"]),
        ("Economic News", ["Stock Performance", "Economic Growth", "Investment Finance", "Corporate Revenue", "Inflation"]),
        ("Sports News", ["Baseball Game", "Basketball League", "Football World Cup", "Athlete Performance", "Sports Events"]),
        ("Entertainment News", ["Movie Release", "Entertainment Industry", "Music Album", "Entertainment Events", "Celebrity News"])
    ]
    
    data = []
    for i in range(num_articles):
        topic_idx = i % len(news_topics)
        topic_name, keywords = news_topics[topic_idx]
        keyword = keywords[i % len(keywords)]
        
        article = {
            "id": f"news_{i:03d}",
            "title": f"{topic_name}: Latest Developments in {keyword}",
            "content": f"Detailed report about {keyword}, including relevant background information and latest updates. This is important news in the {topic_name} category.",
            "category": topic_name,
            "timestamp": datetime.now().isoformat()
        }
        data.append(article)
    
    return data

def get_test_embedding_model():
    """Get test embedding model name"""
    return "paraphrase-MiniLM-L6-v2"  # Lightweight model, suitable for testing
