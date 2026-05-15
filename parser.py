from google import genai
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize client with your API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

from PIL import Image

def parse_receipt_with_gemini(image: Image.Image) -> dict:
    """
    Sends receipt image directly to Gemini Vision.
    Returns a dict with 'items' (list) and 'gst' (float).
    """

    prompt = f"""You are a receipt parsing assistant.

Below is an image of a receipt.
The image may have errors, inconsistent formatting, or noise.

Your job:
1. Extract all food/drink line items with their quantity and total price
2. If quantity is not explicitly mentioned, assume quantity is 1
3. The "price" field should be the TOTAL price for that line (quantity × unit price)
4. Also extract any GST, CGST, SGST, service tax, VAT, or service charge as a combined total tax amount
5. Ignore subtotals, grand totals, discounts, and headers
6. Return ONLY a valid JSON object — no explanation, no markdown, no extra text

Format:
{{
  "items": [
    {{"item": "item name", "quantity": 1, "price": 00.00}},
    ...
  ],
  "gst": 00.00
}}

If no tax/GST is found, set "gst" to 0."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[image, prompt]
    )

    raw_response = response.text.strip()

    # Strip markdown code fences if Gemini wraps the output
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_response, re.DOTALL)
    if match:
        raw_response = match.group(1)

    try:
        parsed = json.loads(raw_response.strip())
    except json.JSONDecodeError:
        raise ValueError(f"Gemini returned invalid JSON:\n{raw_response}")

    if not isinstance(parsed, dict) or "items" not in parsed:
        raise ValueError(f"Expected a dict with 'items' key, got: {type(parsed).__name__}")

    items = parsed["items"]
    gst = float(parsed.get("gst", 0))

    # Ensure every item has a quantity field and compute unit_price
    for item in items:
        item["quantity"] = item.get("quantity", 1)
        item["unit_price"] = round(item["price"] / item["quantity"], 2)

    return {"items": items, "gst": gst}