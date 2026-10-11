from marketplace_sms import BuyerUpdate, InfraiClient, OrderHandoff, SellerAsset, notify_handoff


class FakeResponse:
    status = 200

    def read(self):
        return b'{"ok": true, "data": {"message_id": "msg-1"}}'


def test_handoff_sends_domain_message_and_returns_message_id():
    seen = {}

    def opener(request, timeout):
        seen["method"] = request.method
        seen["url"] = request.full_url
        seen["body"] = request.data.decode()
        seen["idempotency"] = request.headers["Idempotency-key"]
        return FakeResponse()

    order = OrderHandoff("ORD-1042", SellerAsset("ASSET-7", "Oak desk"), BuyerUpdate("+15551234567", "ready"))
    result = notify_handoff(order, InfraiClient(key="test-key", opener=opener))
    assert result["message_id"] == "msg-1"
    assert seen["method"] == "POST"
    assert "Oak desk" in seen["body"]
    assert seen["idempotency"] == "order:ORD-1042:handoff"
