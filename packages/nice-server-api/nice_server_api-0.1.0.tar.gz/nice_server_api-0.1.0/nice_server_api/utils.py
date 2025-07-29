def check_dependencies():
    """Проверяет наличие необходимых зависимостей."""
    try:
        import flask
        import requests
        return True
    except ImportError as e:
        raise ImportError(f"Missing dependency: {e.name}. Install it using 'pip install flask requests'")