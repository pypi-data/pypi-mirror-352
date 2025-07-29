import asyncio
import logging
import sys
import time
from typing import List, Optional
from pydantic import BaseModel, Field
from notte_browser.session import NotteSession
from notte_agent import Agent
from dotenv import load_dotenv

# Configure logging to disable all output
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger('notte_browser').setLevel(logging.CRITICAL)
logging.getLogger('notte_agent').setLevel(logging.CRITICAL)
logging.getLogger('notte_browser.playwright').setLevel(logging.CRITICAL)
logging.getLogger('notte_browser.playwright:get_browser_resource').setLevel(logging.CRITICAL)

# Disable stdout and stderr
class DummyFile:
    def write(self, x): pass
    def flush(self): pass

# Store original stdout and stderr
original_stdout = sys.stdout
original_stderr = sys.stderr

class ProductResponse(BaseModel):
    Item_Name: str = Field(default="", description="Full product name with selected variants")
    selected_variants: List[str] = Field(default_factory=list, description="List of chosen options (color, size, etc.)")
    SKU: Optional[str] = Field(default=None, description="Product identifier if visible")
    quantity: int = Field(default=1, description="Number of items in cart")
    base_price: str = Field(default="", description="Original list price before any discounts")
    discounted_price: str = Field(default="", description="Price after any discounts (same as base_price if no discount)")
    shipping_cost: Optional[str] = Field(default=None, description="All shipping and handling fees")
    estimated_tax: Optional[str] = Field(default=None, description="Tax amount based on the zip code")
    total_price: str = Field(default="", description="Final amount to be paid including all components")

_ = load_dotenv()

url = "https://joybird.com/sleeper-sofas/miller-sleeper-sofa/?fabric=royale_evergreen&mattress=standard_foam"
task = f"""
You are tasked with automating browser interactions to extract complete pricing and shipping details from an e-commerce website. Your primary goal is to gather ALL pricing information, which typically requires proceeding to the checkout page.

1. **Initial Navigation and Setup:**
   - Navigate to: {url}
   - Wait for the page to fully load (1-2 seconds)
   - Handle any initial popups or overlays:
     * Close newsletter signups
     * Dismiss promotional modals
     * Accept cookie notices
     * Close chat widgets
     * Handle any exit intent popups
   - If any overlay cannot be closed, try clicking outside or using the ESC key

2. **Product Page Interaction - CRITICAL SCROLLING RULES:**
   - CRITICAL: The "Add to Cart" button is OFTEN below the viewport and requires scrolling
   - BEFORE clicking any cart/bag icons in the header:
     * Scroll down the page in small increments (300-400 pixels)
     * After each scroll, look for the add to cart button
     * The button is typically found in these locations (in order):
       1. Below the product images
       2. Below the product description
       3. In a sticky bar at the bottom of the page
       4. In the product options section
     * Common button text variations:
       - "Add to Cart"
       - "Add to Bag"
       - "Buy Now"
       - "Add to Shopping Cart"
   - IMPORTANT: Do NOT click the cart/bag icon in the header until you've:
     * Scrolled through the ENTIRE product page
     * Confirmed the add to cart button is not visible
     * This prevents the empty cart loop problem
   - If you find any size/color selection requirements:
     * Select the first available option
     * Wait for the selection to be applied (0.5 seconds)
     * Then look for the add to cart button
   - Only if you cannot find the add to cart button after scrolling the entire page:
     * Then look for the cart icon in the header
     * But this should be your last resort
   - After clicking "Add to Cart" or "Add to Bag":
     * Wait 1 second for any popup or overlay to appear
     * CRITICAL: Look for and click the "Proceed to Checkout" button in the popup
     * Common variations of the proceed button:
       - "Proceed to Checkout"
       - "Checkout"
       - "Go to Checkout"
       - "View Cart & Checkout"
     * Do NOT close the popup without proceeding to checkout
     * Do NOT click "Continue Shopping" or similar buttons
     * The popup might appear as:
       - A modal overlay
       - A slide-in panel
       - A floating notification
   - Proceed to cart/checkout to get complete pricing information

3. **Checkout Page - STRICT RULES:**
   - CRITICAL: Once you reach the checkout page:
     * IMMEDIATELY look for and extract all pricing information
     * Do NOT attempt to fill any forms
     * Do NOT click any "Continue" or "Next" buttons
     * Do NOT enter any information
   - IMPORTANT: The checkout page usually shows all pricing information without needing to enter anything
   - ONLY if you see a zip code field AND:
     * Shipping cost is not visible
     * AND there's no other way to see shipping costs
     * AND the page explicitly requires zip code to show shipping
     * THEN enter "02139" (Cambridge, MA)
   - If you see any of these, STOP and return current data:
     * Email field
     * Name fields
     * Address fields
     * Phone number field
     * Payment information fields
     * "Create Account" or "Sign In" prompts
     * "Continue to Payment" or similar buttons
   - Remember: Your ONLY goal is to extract pricing information, not to complete the checkout

4. **Critical Data Extraction:**
   You MUST collect these specific pricing components:
   - `base_price`: Original list price before any discounts
   - `discounted_price`: Price after any discounts (same as base_price if no discount)
   - `shipping_cost`: All shipping and handling fees
   - `estimated_tax`: Tax amount based on the zip code
   - `total_price`: Final amount to be paid including all components

   Additional product details to collect if available:
   - `Item_Name`: Full product name with selected variants
   - `selected_variants`: List of chosen options (color, size, etc.)
   - `SKU`: Product identifier if visible
   - `quantity`: Number of items in cart

5. **Important Rules:**
   - You MUST proceed to checkout to get complete pricing information
   - STOP at the first sign of personal information requirements
   - Do NOT attempt to complete any forms
   - Do NOT try to bypass any requirements
   - If asked for email, address, or payment details, stop and return current data
   - If the site requires account creation, stop and return current data
   - If any step fails, return whatever data has been collected so far
   - If shipping estimates require more than zip code, stop and return current data

6. **Return the data in this exact JSON format:**
   You MUST return a JSON object that matches this exact schema:
   {ProductResponse.model_json_schema()}

   Example response:
   {{
       "Item_Name": "Miller Sleeper Sofa",
       "selected_variants": ["Royale Evergreen Fabric", "Standard Foam Mattress"],
       "SKU": "MILLER-SLEEPER-SOFA",
       "quantity": 1,
       "base_price": "$1,199.00",
       "discounted_price": "$999.00",
       "shipping_cost": "$179.00",
       "estimated_tax": "$42.84",
       "total_price": "$1,220.84"
   }}

   IMPORTANT: 
   - Return ONLY the JSON object with the actual data, NOT the schema or any other format
   - Return EXACTLY what you find on the page, don't try to validate or fix the data
   - If a field is null or missing, return it as null
   - Don't try to format or clean up the data, just return it as is
   - The validation will be handled by the system, not by you

7. **Error Handling:**
   - If any step fails, document the last successful step
   - Return partial data if available
   - Include any error messages or unexpected behaviors
   - If the site structure changes, adapt to find similar information
   - If you can't get complete pricing information, note which components are missing
"""

# url = "https://society6.com/a/products/surfboards3603212_framed-print?sku=s6-17482185p21a12v1053a13v57"
# task = f"""
# You are tasked with automating browser interactions to extract complete pricing and shipping details from an e-commerce website. Your primary goal is to gather ALL pricing information, which typically requires proceeding to the checkout page.

# 1. **Initial Navigation and Setup:**
#    - Navigate to: {url}
#    - Wait for the page to fully load (1-2 seconds)
#    - Handle any initial popups or overlays:
#      * Close newsletter signups
#      * Dismiss promotional modals
#      * Accept cookie notices
#      * Close chat widgets
#      * Handle any exit intent popups
#    - If any overlay cannot be closed, try clicking outside or using the ESC key

# 2. **Product Page Interaction - CRITICAL SCROLLING RULES:**
#    - CRITICAL: The "Add to Cart" button is OFTEN below the viewport and requires scrolling
#    - BEFORE clicking any cart/bag icons in the header:
#      * Scroll down the page in small increments (300-400 pixels)
#      * After each scroll, look for the add to cart button
#      * The button is typically found in these locations (in order):
#        1. Below the product images
#        2. Below the product description
#        3. In a sticky bar at the bottom of the page
#        4. In the product options section
#      * Common button text variations:
#        - "Add to Cart"
#        - "Add to Bag"
#        - "Buy Now"
#        - "Add to Shopping Cart"
#    - IMPORTANT: Do NOT click the cart/bag icon in the header until you've:
#      * Scrolled through the ENTIRE product page
#      * Confirmed the add to cart button is not visible
#      * This prevents the empty cart loop problem
#    - If you find any size/color selection requirements:
#      * Select the first available option
#      * Wait for the selection to be applied (0.5 seconds)
#      * Then look for the add to cart button
#    - Only if you cannot find the add to cart button after scrolling the entire page:
#      * Then look for the cart icon in the header
#      * But this should be your last resort
#    - After clicking "Add to Cart" or "Add to Bag":
#      * Wait 1 second for any popup or overlay to appear
#      * CRITICAL: Look for and click the "Proceed to Checkout" button in the popup
#      * Common variations of the proceed button:
#        - "Proceed to Checkout"
#        - "Checkout"
#        - "Go to Checkout"
#        - "View Cart & Checkout"
#      * Do NOT close the popup without proceeding to checkout
#      * Do NOT click "Continue Shopping" or similar buttons
#      * The popup might appear as:
#        - A modal overlay
#        - A slide-in panel
#        - A floating notification
#    - Proceed to cart/checkout to get complete pricing information

# 3. **STRICT FIELD MAPPING FOR SOCIETY6 DELIVERY FORM**

# **CRITICAL TIMING REQUIREMENT:**
# - After entering the ZIP code (02139), you MUST wait EXACTLY 3 seconds before attempting to extract any pricing information
# - This wait is MANDATORY because the shipping costs are calculated asynchronously after the zip code is entered
# - If you try to extract pricing information before the 3-second wait, the shipping cost will be missing or incorrect
# - Do NOT proceed with data extraction until the full 3 seconds have elapsed

# **For each field, ONLY enter the value if the field label matches EXACTLY as below. Leave all other fields blank.**

# | Field Label (as shown on page)      | Value to Enter         | Notes                                      |
# |-------------------------------------|------------------------|--------------------------------------------|
# | Email                              | johncambrige@gmail.com | This is the FIRST field at the top         |
# | First name                         | John                   |                                            |
# | Last name                          | Doe                    |                                            |
# | Company (optional)                 | (leave blank)          | DO NOT enter anything here                 |
# | Address                            | 270 norfolk st         |                                            |
# | Apartment, suite, etc. (optional)  | (leave blank)          | DO NOT enter anything here                 |
# | City                               | cambridge              | ONLY enter 'cambridge' here, not zip code  |
# | State                              | Massachusetts          |                                            |
# | ZIP code                           | 02139                  | ONLY enter '02139' here, not in city field |

# **DO NOT:**
# - Do NOT enter 'cambridge' in the apartment/suite field.
# - Do NOT enter '02139' in the city field.
# - Do NOT fill in company or apartment fields.
# - Do NOT enter anything in the phone field.

# **If you cannot find a field with the exact label, SKIP IT.**

# 4. **Critical Data Extraction:**
#    You MUST collect these specific pricing components:
#    - `base_price`: Original list price before any discounts
#    - `discounted_price`: Price after any discounts (same as base_price if no discount)
#    - `shipping_cost`: All shipping and handling fees
#    - `estimated_tax`: Tax amount based on the zip code
#    - `total_price`: Final amount to be paid including all components

#    Additional product details to collect if available:
#    - `Item_Name`: Full product name with selected variants
#    - `selected_variants`: List of chosen options (color, size, etc.)
#    - `SKU`: Product identifier if visible
#    - `quantity`: Number of items in cart

# 5. **Important Rules:**
#    - You MUST proceed to checkout to get complete pricing information
#    - STOP at the first sign of personal information requirements
#    - Do NOT attempt to complete any forms
#    - Do NOT try to bypass any requirements
#    - If asked for email, address, or payment details, stop and return current data
#    - If the site requires account creation, stop and return current data
#    - If any step fails, return whatever data has been collected so far
#    - If shipping estimates require more than zip code, stop and return current data

# 6. **Return the data in this exact JSON format:**
#    You MUST return a JSON object that matches this exact schema:
#    {ProductResponse.model_json_schema()}

#    Example response:
#    {{
#        "Item_Name": "Miller Sleeper Sofa",
#        "selected_variants": ["Royale Evergreen Fabric", "Standard Foam Mattress"],
#        "SKU": "MILLER-SLEEPER-SOFA",
#        "quantity": 1,
#        "base_price": "$1,199.00",
#        "discounted_price": "$999.00",
#        "shipping_cost": "$179.00",
#        "estimated_tax": "$42.84",
#        "total_price": "$1,220.84"
#    }}

#    IMPORTANT: 
#    - Return ONLY the JSON object with the actual data, NOT the schema or any other format
#    - Return EXACTLY what you find on the page, don't try to validate or fix the data
#    - If a field is null or missing, return it as null
#    - Don't try to format or clean up the data, just return it as is
#    - The validation will be handled by the system, not by you

# 7. **Error Handling:**
#    - If any step fails, document the last successful step
#    - Return partial data if available
#    - Include any error messages or unexpected behaviors
#    - If the site structure changes, adapt to find similar information
#    - If you can't get complete pricing information, note which components are missing

# **After entering all required fields:**
# - CRITICAL: Wait EXACTLY 3 seconds after entering the ZIP code
# - Do NOT attempt to extract any pricing information before the 3-second wait is complete
# - After the 3-second wait, verify that shipping costs are visible on the page
# - Only then proceed to extract all pricing information as required
# """

async def run_tasks(tasks: list[str], url: str | None = None) -> None:
    start_time = time.time()
    print("Kick in...")
    
    # Disable all output
    # sys.stdout = DummyFile()
    # sys.stderr = DummyFile()
    # logging.disable(logging.CRITICAL)
    
    try:
        async with NotteSession(headless=False) as session:
            agent = Agent(
                # reasoning_model="gemini/gemini-2.0-flash",
                # reasoning_model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
                max_steps=20,
                session=session,
                use_vision=True,
            )

            for task in tasks:
                result = await agent.arun(task=task)
                try:
                    # Temporarily restore stdout for printing
                    sys.stdout = original_stdout
                    sys.stderr = original_stderr
                    
                    # Extract JSON from the answer text
                    answer_text = result.answer
                    # Find the JSON part in the text (it might be wrapped in ```json or just be the JSON itself)
                    json_start = answer_text.find('{')
                    json_end = answer_text.rfind('}') + 1
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
                    print(f"\n❌ Error validating response: {e}")
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
    asyncio.run(run_tasks([task], url=url))
