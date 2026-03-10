"""
Batch ingestion script for Stripe documentation.
Run locally (not in the sandbox) after the server is running:

    cd /Users/iegorkovalov/Cursor/clarifai/backend
    source venv/bin/activate
    python ingest_stripe.py
"""

import asyncio
import httpx

API_KEY = "sk_FYjHWD7YKiuH4iTRu790gvMDp8Ysd24vnWpYCrCZPic"
BASE_URL = "http://localhost:8000"

URLS = [
    # --- Already ingested (original list) ---
    "https://docs.stripe.com/billing/subscriptions/cancel",
    "https://docs.stripe.com/billing/subscriptions/trials",
    "https://docs.stripe.com/billing/subscriptions/upgrade-downgrade",
    "https://docs.stripe.com/billing/subscriptions/pause-payment",
    "https://docs.stripe.com/refunds",
    "https://docs.stripe.com/disputes",
    "https://docs.stripe.com/payments/payment-intents",
    "https://docs.stripe.com/invoicing/overview",
    "https://docs.stripe.com/billing/taxes/tax-rates",
    "https://docs.stripe.com/payments/3d-secure",
    "https://docs.stripe.com/error-codes",
    "https://docs.stripe.com/keys",
    "https://docs.stripe.com/webhooks",
    "https://docs.stripe.com/testing",
    "https://docs.stripe.com/customer-management",

    # --- Pricing & Billing ---
    "https://stripe.com/pricing",
    "https://support.stripe.com/questions/stripe-pricing-fees",
    "https://support.stripe.com/questions/understanding-ic-fees",
    "https://support.stripe.com/questions/see-the-stripe-fee-applied-to-a-specific-charge",

    # --- Account Management ---
    "https://support.stripe.com/questions/reset-a-forgotten-stripe-password",
    "https://support.stripe.com/questions/trouble-signing-in",
    "https://support.stripe.com/questions/sign-in-to-your-stripe-account-without-a-two-step-authentication-device-or-backup-code",
    "https://support.stripe.com/questions/i-forgot-my-username-or-email-address",
    "https://support.stripe.com/questions/completing-account-ownership-verification",

    # --- Core Product Features ---
    "https://docs.stripe.com/payments",
    "https://docs.stripe.com/billing/subscriptions/overview",
    "https://docs.stripe.com/products-prices/pricing-models",

    # --- Troubleshooting ---
    "https://support.stripe.com/questions/why-is-my-customers-payment-failing",
    "https://support.stripe.com/questions/rejected-payouts",
    "https://support.stripe.com/questions/understanding-refund-statuses",

    # --- Refund & Payment Policies ---
    "https://support.stripe.com/questions/where-is-my-customers-refund",
    "https://support.stripe.com/questions/refunds-and-disputes-after-closing-a-stripe-account",
]


async def ingest_url(client: httpx.AsyncClient, url: str, index: int):
    try:
        response = await client.post(
            f"{BASE_URL}/api/ingest/url",
            json={"url": url},
            headers={"X-API-Key": API_KEY},
            timeout=120,
        )
        data = response.json()
        if response.status_code == 200:
            print(f"[{index + 1}/{len(URLS)}] ✅  {url}\n           → {data.get('message')}\n")
        else:
            print(f"[{index + 1}/{len(URLS)}] ❌  {url}\n           → {data}\n")
    except Exception as e:
        print(f"[{index + 1}/{len(URLS)}] ❌  {url}\n           → {e}\n")


async def main():
    print(f"Starting ingestion of {len(URLS)} Stripe docs pages...\n")
    async with httpx.AsyncClient() as client:
        for i, url in enumerate(URLS):
            await ingest_url(client, url, i)
            if i < len(URLS) - 1:
                await asyncio.sleep(1)  # avoid hammering OpenAI embeddings API

    print("Done. Run a test chat to verify RAG quality:")
    print(f"""
  curl -s -X POST {BASE_URL}/api/chat \\
    -H "Content-Type: application/json" \\
    -H "X-API-Key: {API_KEY}" \\
    -d '{{"message": "How do I cancel a subscription?"}}' | python3 -m json.tool
""")


asyncio.run(main())
