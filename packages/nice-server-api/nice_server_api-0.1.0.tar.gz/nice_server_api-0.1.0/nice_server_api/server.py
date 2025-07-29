from flask import Flask, request, jsonify

class NiceServer:
    """Класс для упрощенного создания Flask-сервера."""
    def __init__(self, port=5000, host="0.0.0.0", debug=False):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.debug = debug
        self.routes = {}  # Словарь для хранения функций маршрутов

    def route(self, url):
        """Декоратор для добавления функций в маршруты сервера."""
        def decorator(func):
            def wrapped():
                try:
                    # Передаем параметры из запроса (GET или POST) в функцию
                    if request.method == "GET":
                        args = request.args.to_dict()
                    else:
                        args = request.get_json() or {}
                    result = func(url, **args)
                    return jsonify({"result": result, "status": "success"})
                except Exception as e:
                    return jsonify({"error": str(e), "status": "error"}), 400

            # Регистрируем маршрут для GET и POST
            self.routes[url] = func
            self.app.route(url, methods=["GET", "POST"])(wrapped)
            return func
        return decorator

    def run(self):
        """Запускает сервер."""
        self.app.run(host=self.host, port=self.port, debug=self.debug)