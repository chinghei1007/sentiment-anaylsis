"""
Helper utility functions
"""

import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read JSON file and return as dictionary"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return {}


def write_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """Write dictionary to JSON file"""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        return False


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Sanitize text input"""
    if not text:
        return ""
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    return text


def validate_sentiment_label(label: str) -> str:
    """Validate and normalize sentiment label"""
    label = label.lower().strip()
    
    valid_labels = {
        'positive': 'positive',
        'neg': 'negative',
        'negative': 'negative',
        'pos': 'positive',
        '1': 'positive',
        '0': 'negative'
    }
    
    return valid_labels.get(label, 'neutral')


def convert_label_to_numeric(label: str) -> Optional[float]:
    """Convert sentiment label to numeric value"""
    label = validate_sentiment_label(label)
    
    if label == 'positive':
        return 1.0
    elif label == 'negative':
        return 0.0
    else:
        return None


def get_file_extension(file_path: str) -> str:
    """Get file extension from path"""
    return Path(file_path).suffix.lower().replace('.', '')
