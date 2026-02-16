from test.util.abstract_integration_test import AbstractPostgresTest
from test.util.mock_user import mock_webui_user


class TestPricing(AbstractPostgresTest):
    BASE_PATH = "/api/v1/pricing"

    def test_get_pricing_empty(self):
        with mock_webui_user(id="2"):
            res = self.fast_api_client.get(self.create_url("/models"))
        assert res.status_code == 200
        assert res.json() == {"items": [], "updated_at": None}

    def test_refresh_pricing_empty(self):
        with mock_webui_user(id="2"):
            res = self.fast_api_client.post(
                self.create_url("/refresh"), json={"model_ids": ["gpt-4o"]}
            )
        assert res.status_code == 200
        assert "items" in res.json()
