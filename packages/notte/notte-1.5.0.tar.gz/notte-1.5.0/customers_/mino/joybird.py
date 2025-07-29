import logging
import sys
import time
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

_ = load_dotenv()

# ####################################################
# ############## Local VS Cloud Setup ################
# ####################################################

import notte  # Uncomment this line to use the local Notte SDK

# from notte_sdk import NotteClient     # Uncomment this line to use the cloud Notte SDK
# notte = NotteClient()                 # Uncomment this line to use the cloud Notte SDK

# ####################################################
# ####################################################
# ####################################################

# Configure logging to disable all output
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("notte_browser").setLevel(logging.CRITICAL)
logging.getLogger("notte_agent").setLevel(logging.CRITICAL)
logging.getLogger("notte_browser.playwright").setLevel(logging.CRITICAL)
logging.getLogger("notte_browser.playwright:get_browser_resource").setLevel(
    logging.CRITICAL
)
# Disable stdout and stderr


class DummyFile:
    def write(self, x):
        pass

    def flush(self):
        pass


# Store original stdout and stderr

original_stdout = sys.stdout
original_stderr = sys.stderr


class ProductResponse(BaseModel):
    Item_Name: str = Field(
        default="", description="Full product name with selected variants"
    )
    selected_variants: List[str] = Field(
        default_factory=list, description="List of chosen options (color, size, etc.)"
    )
    SKU: Optional[str] = Field(
        default=None, description="Product identifier if visible"
    )
    quantity: int = Field(default=1, description="Number of items in cart")
    base_price: str = Field(
        default="", description="Original list price before any discounts"
    )
    discounted_price: str = Field(
        default="",
        description="Price after any discounts (same as base_price if no discount)",
    )
    shipping_cost: Optional[str] = Field(
        default=None, description="All shipping and handling fees"
    )
    estimated_tax: Optional[str] = Field(
        default=None, description="Tax amount based on the zip code"
    )
    total_price: str = Field(
        default="", description="Final amount to be paid including all components"
    )


def load_prompt(url: str) -> str:
    """Load the prompt template from the prompts file and format it with the URL."""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "joybird")
    with open(prompt_path, "r") as f:
        prompt_template = f.read()
    prompt = prompt_template.format(url=url)
    schema = ProductResponse.model_json_schema()
    prompt = prompt.replace("{ProductResponse.model_json_schema()}", str(schema))
    return prompt


url = "https://joybird.com/sleeper-sofas/miller-sleeper-sofa/?fabric=royale_evergreen&mattress=standard_foam"
# url = "https://walkeredison.com/products/faux-leather-counter-stools?variant=39348896989250"
task = load_prompt(url)


def run_tasks(tasks: list[str], url: str | None = None) -> None:
    start_time = time.time()
    print("Kick in...")
    # Disable all output
    # sys.stdout = DummyFile()
    # sys.stderr = DummyFile()
    # logging.disable(logging.CRITICAL)
    try:
        with notte.Session(headless=False) as session:
            agent = notte.Agent(
                # reasoning_model="gemini/gemini-2.0-flash",
                # reasoning_model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
                max_steps=20,
                session=session,
                use_vision=True,
            )
            for task in tasks:
                result = agent.run(task=task)
                try:
                    # Temporarily restore stdout for printing
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    # Extract JSON from the answer text
                    answer_text = result.answer
                    # Find the JSON part in the text (it might be wrapped in ```json or just be the JSON itself)
                    json_start = answer_text.find("{")
                    json_end = answer_text.rfind("}") + 1
                    if json_start == -1 or json_end == 0:
                        raise ValueError("No JSON found in the response")
                    json_str = answer_text[json_start:json_end]
                    # Try to parse the result into our Pydantic model
                    response = ProductResponse.model_validate_json(json_str)
                    print("\n📦 Product Details:")
                    print("=" * 50)
                    print(f"Name: {response.Item_Name}")
                    print(f"SKU: {response.SKU}")
                    print(f"Quantity: {response.quantity}")
                    if response.selected_variants:
                        print(f"Variants: {', '.join(response.selected_variants)}")
                    print("\n💰 Pricing Information:")
                    print("-" * 50)
                    print(f"Base Price: {response.base_price}")
                    print(f"Discounted Price: {response.discounted_price}")
                    print(f"Shipping Cost: {response.shipping_cost or 'Not available'}")
                    print(f"Estimated Tax: {response.estimated_tax or 'Not available'}")
                    print(f"Total Price: {response.total_price}")
                    print("=" * 50)
                    # Disable output again
                    sys.stdout = DummyFile()
                    sys.stderr = DummyFile()
                except Exception as e:
                    # Temporarily restore stdout for error printing
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    print(f"\n:x: Error validating response: {e}")
                    print("Raw answer:", result.answer)
                    # Disable output again
                    sys.stdout = DummyFile()
                    sys.stderr = DummyFile()
    finally:
        # Restore stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        logging.disable(logging.NOTSET)
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n✨ Finish! Task completed in {duration:.2f} seconds")


if __name__ == "__main__":
    run_tasks([task], url=url)
