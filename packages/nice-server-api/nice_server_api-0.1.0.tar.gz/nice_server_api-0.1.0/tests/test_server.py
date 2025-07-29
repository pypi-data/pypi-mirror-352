import unittest
from nice_server_api.server import NiceServer

class TestNiceServer(unittest.TestCase):
    def setUp(self):
        self.server = NiceServer(debug=True)
        self.app = self.server.app.test_client()

    def test_hello_route(self):
        response = self.app.get("/api/hello?name=Alex")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Hello, Alex!"})

    def test_post_data(self):
        response = self.app.post("/api/data", json={"key": "value"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"received": {"key": "value"}, "status": "success"})

if __name__ == "__main__":
    unittest.main()