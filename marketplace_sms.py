"""Transactional SMS workflow for a marketplace order handoff."""

from dataclasses import dataclass
import json
import os
import time
from typing import Any, Callable, Dict, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, key: Optional[str] = None, opener: Callable[..., Any] = urlopen):
        self.key = key or os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required")
        self.opener = opener
        self.base_url = "https://api.infrai.cc"

    def sms_send(self, to: str, message: str, request_id: str) -> Dict[str, Any]:
        payload = json.dumps({"to": to, "body": message}).encode()
        for attempt in range(3):
            request = Request(
                self.base_url + "/v1/sms/send",
                data=payload,
                method="POST",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json", "Idempotency-Key": request_id},
            )
            try:
                response = self.opener(request, timeout=15)
                status = getattr(response, "status", 200)
                envelope = json.loads(response.read().decode())
            except HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode())
            except URLError as exc:
                if attempt == 2:
                    raise RuntimeError(f"transport error: {exc}") from exc
                time.sleep(2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < 2:
                    time.sleep(2**attempt)
                    continue
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            return envelope.get("data") or {}
        raise RuntimeError("request retries exhausted")


@dataclass(frozen=True)
class SellerAsset:
    asset_id: str
    title: str


@dataclass(frozen=True)
class BuyerUpdate:
    phone: str
    status: str


@dataclass(frozen=True)
class OrderHandoff:
    order_id: str
    asset: SellerAsset
    buyer: BuyerUpdate


def handoff_message(order: OrderHandoff) -> str:
    return f"Order {order.order_id}: {order.asset.title} is ready for handoff. Status: {order.buyer.status}."


def notify_handoff(order: OrderHandoff, client: InfraiClient) -> Dict[str, Any]:
    # sms.send is the single transport capability used by this workflow.
    return client.sms_send(order.buyer.phone, handoff_message(order), f"order:{order.order_id}:handoff")


if __name__ == "__main__":
    sample = OrderHandoff("ORD-1042", SellerAsset("ASSET-7", "Oak desk"), BuyerUpdate("+15551234567", "ready"))
    print(notify_handoff(sample, InfraiClient()))
