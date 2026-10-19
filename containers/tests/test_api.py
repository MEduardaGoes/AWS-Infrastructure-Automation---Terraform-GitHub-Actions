import importlib.util
import json
import os
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen


APP_PATH = Path(__file__).resolve().parents[1] / "app" / "main.py"
SPEC = importlib.util.spec_from_file_location("swarm_app", APP_PATH)
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_health_returns_ok(self):
        with urlopen(self.base_url + "/health", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(json.load(response), {"status": "ok"})

    def test_root_returns_service_metadata(self):
        with urlopen(self.base_url + "/", timeout=5) as response:
            payload = json.load(response)
            self.assertEqual(payload["service"], "devsecops-swarm-demo")
            self.assertTrue(payload["hostname"])
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertIn("application/json", response.headers["Content-Type"])

    def test_version_can_be_set_for_update_demonstrations(self):
        with patch.dict(os.environ, {"APP_VERSION": "2.0.0"}):
            with urlopen(self.base_url + "/", timeout=5) as response:
                self.assertEqual(json.load(response)["version"], "2.0.0")

    def test_unknown_path_returns_json_404(self):
        with self.assertRaises(HTTPError) as raised:
            urlopen(self.base_url + "/missing", timeout=5)
        with raised.exception as response:
            self.assertEqual(response.code, 404)
            self.assertEqual(json.load(response), {"error": "not_found"})

    def test_health_accepts_query_string(self):
        with urlopen(self.base_url + "/health?probe=ready", timeout=5) as response:
            self.assertEqual(json.load(response), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
