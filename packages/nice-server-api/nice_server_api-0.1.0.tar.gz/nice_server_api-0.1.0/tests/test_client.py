import unittest
from nice_server_api.client import NiceClient

class TestNiceClient(unittest.TestCase):
    def setUp(self):
        self.client = NiceClient("http://httpbin.org")

    def test_get(self):
        response = self.client.get("get", params={"name": "Alex"})
        self.assertIn("args", response)
        self.assertEqual(response["args"], {"name": "Alex"})

    def test_post(self):
        response = self.client.post("post", data={"key": "value"})
        self.assertIn("json", response)
        self.assertEqual(response["json"], {"key": "value"})

if __name__ == "__main__":
    unittest.main()