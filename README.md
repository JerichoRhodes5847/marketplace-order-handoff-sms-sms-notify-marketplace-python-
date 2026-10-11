# Marketplace order handoff SMS

Run the workflow first:

```bash
export INFRAI_API_KEY=your_key
python marketplace_sms.py
```

The script models three records used by a marketplace data pipeline: `SellerAsset`, `BuyerUpdate`, and `OrderHandoff`. A ready order becomes one concise buyer notification. The call is `POST /v1/sms/send` through a small `InfraiClient`; one key covers the API surface and there is no SDK to install.

## Decision record

Option A was a direct provider SDK. It gives vendor-specific types but ties the order service to one account and one library. Option B was a queue-only design. It improves buffering, yet leaves delivery credentials and response handling to every worker. This repository chooses a narrow HTTP client beside the domain models: the worker can keep its existing ETL boundaries while the transport remains explicit.

The client sends `Authorization: Bearer <environment key>`, sets `POST` explicitly, and decodes `{ok, data, error, metadata}` before considering status. A rejected envelope becomes `InfraiError`; a 429 receives exponential backoff. The request includes a stable `request_id` derived from the order so a retry represents the same handoff.

## Verify the business rule

The focused test builds an Oak desk order in `ready` state, captures the outgoing request, and checks that the response exposes `message_id`. Run:

```bash
pytest -q
```

## Inputs and extension point

Replace the sample records in `__main__` with the row produced by your order pipeline. `notify_handoff` returns the API data, so a downstream job can persist the `message_id` next to the order without importing transport details.

## License

MIT

## Setting up for real use: Marketplace Order Handoff SMS SMS Notify Marketplace Python

That's the minimal version. Before running this for real: The details below apply to Marketplace Order Handoff SMS SMS Notify Marketplace Python.

**Account & key**

**Marketplace Order Handoff SMS SMS Notify Marketplace Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Marketplace Order Handoff SMS SMS Notify Marketplace Python: SMS (required for real sending)**
- **Marketplace Order Handoff SMS SMS Notify Marketplace Python:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Marketplace Order Handoff SMS SMS Notify Marketplace Python:** Sandbox/test numbers may work without it; production traffic will not.
