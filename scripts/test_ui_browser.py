
import time
from playwright.sync_api import sync_playwright

print("[BROWSER] Starting browser test...")
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("[BROWSER] Navigating to localhost:8501...")
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        
        print("[BROWSER] Waiting for chat input...")
        page.wait_for_selector("input", timeout=10000)
        
        # Find and fill chat input
        inputs = page.locator("input")
        if inputs.count() > 0:
            chat_input = inputs.last
            print("[BROWSER] Found chat input, typing query...")
            chat_input.fill("high in the chart")
            chat_input.press("Enter")
            
            print("[BROWSER] Submitted query, waiting for response...")
            start = time.time()
            
            # Wait for any response
            try:
                page.wait_for_function(
                    "() => document.body.innerText.length > 500",
                    timeout=50000
                )
                elapsed = time.time() - start
                print(f"[BROWSER] Response received in {elapsed:.2f}s")
            except:
                elapsed = time.time() - start
                print(f"[BROWSER] TIMEOUT after {elapsed:.2f}s")
        
        browser.close()
except Exception as e:
    print(f"[BROWSER] Error: {e}")
