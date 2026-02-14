"""
FILE: debug_ui_hanging.py
STATUS: Active
RESPONSIBILITY: Monitor UI activity and debug hanging on "high in the chart" query
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu

This script monitors UI requests, logs API interactions, and helps diagnose why the UI
hangs on certain queries like "high in the chart" while the API responds correctly.

Usage:
    poetry run python scripts/debug_ui_hanging.py
    Then interact with the UI at http://localhost:8501 and the script will log all activity.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging with timestamps
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("debug_ui_hanging.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


class RequestLogger:
    """Log HTTP requests with detailed timing information."""

    def __init__(self):
        self.session = self._create_session()

    @staticmethod
    def _create_session() -> requests.Session:
        """Create session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def log_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Log a request with timing."""
        start = time.time()
        logger.info(f"→ {method} {url}")

        if "data" in kwargs:
            logger.debug(f"  Request body: {kwargs['data']}")

        try:
            response = self.session.request(method, url, **kwargs)
            elapsed = time.time() - start

            logger.info(
                f"← {method} {url} | Status: {response.status_code} | "
                f"Time: {elapsed:.3f}s"
            )

            if response.status_code >= 400:
                logger.error(f"  Error response: {response.text[:200]}")
            else:
                if response.text:
                    try:
                        data = response.json()
                        logger.debug(f"  Response: {json.dumps(data, indent=2)[:500]}")
                    except ValueError:
                        logger.debug(f"  Response: {response.text[:200]}")

            return response

        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start
            logger.error(
                f"✗ {method} {url} | Error: {type(e).__name__} | Time: {elapsed:.3f}s"
            )
            logger.error(f"  Details: {str(e)}")
            raise


class UIActivityMonitor:
    """Monitor UI activity and test problematic queries."""

    API_BASE = "http://localhost:8002"
    STREAMLIT_URL = "http://localhost:8501"

    def __init__(self):
        self.logger = RequestLogger()
        self.test_results = []

    def check_api_health(self) -> bool:
        """Check if API is running and healthy."""
        logger.info("\n" + "=" * 60)
        logger.info("CHECKING API HEALTH")
        logger.info("=" * 60)

        try:
            response = self.logger.log_request("GET", f"{self.API_BASE}/health")
            health_data = response.json()

            logger.info(f"✅ API Status: {health_data.get('status')}")
            logger.info(f"   Index loaded: {health_data.get('index_loaded')}")
            logger.info(f"   Vector chunks: {health_data.get('vector_chunks', 'N/A')}")

            return response.status_code == 200

        except Exception as e:
            logger.error(f"❌ API health check failed: {e}")
            return False

    def check_streamlit_ui(self) -> bool:
        """Check if Streamlit UI is running."""
        logger.info("\n" + "=" * 60)
        logger.info("CHECKING STREAMLIT UI")
        logger.info("=" * 60)

        try:
            response = self.logger.log_request("GET", self.STREAMLIT_URL)

            if response.status_code == 200:
                logger.info("✅ Streamlit UI is accessible")
                return True
            else:
                logger.error(
                    f"❌ Streamlit UI returned status {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Cannot reach Streamlit UI: {e}")
            return False

    def test_api_query(self, query: str, expected_type: str = "both") -> dict:
        """Test a query directly against the API."""
        logger.info("\n" + "-" * 60)
        logger.info(f"TESTING API QUERY: '{query}'")
        logger.info("-" * 60)

        payload = {
            "query": query,
            "k": 5,
            "include_sources": True,
            "conversation_id": None,
        }

        try:
            start = time.time()
            response = self.logger.log_request(
                "POST",
                f"{self.API_BASE}/api/v1/chat",
                json=payload,
                timeout=30,
            )
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Query succeeded in {elapsed:.3f}s")
                logger.info(f"   Response type: {data.get('chat_type')}")
                logger.info(f"   Message length: {len(data.get('message', ''))}")
                logger.info(f"   Has sources: {'sources' in data}")

                result = {
                    "query": query,
                    "status": "success",
                    "elapsed_time": elapsed,
                    "response_type": data.get("chat_type"),
                    "message_length": len(data.get("message", "")),
                }

            else:
                logger.error(f"❌ Query failed with status {response.status_code}")
                result = {
                    "query": query,
                    "status": "error",
                    "error": response.text[:200],
                }

            self.test_results.append(result)
            return result

        except requests.exceptions.Timeout:
            logger.error("❌ Query timed out after 30 seconds")
            self.test_results.append(
                {"query": query, "status": "timeout", "elapsed_time": 30.0}
            )
            return {"query": query, "status": "timeout"}

        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            self.test_results.append(
                {"query": query, "status": "error", "error": str(e)}
            )
            return {"query": query, "status": "error", "error": str(e)}

    def test_problematic_queries(self):
        """Test the problematic 'high in the chart' query and variations."""
        logger.info("\n" + "=" * 60)
        logger.info("TESTING PROBLEMATIC QUERIES")
        logger.info("=" * 60)

        test_queries = [
            "high in the chart",  # Original problematic query
            "who is high in the chart",  # More specific
            "who is at the top of the list",  # Semantic equivalent
            "top 5 scorers",  # Query that worked
            "what are the scoring leaders",  # Vector variant
        ]

        for query in test_queries:
            try:
                self.test_api_query(query)
                time.sleep(2)  # Rate limiting
            except Exception as e:
                logger.error(f"Error testing '{query}': {e}")

    def monitor_with_instructions(self):
        """Print interactive monitoring instructions."""
        logger.info("\n" + "=" * 60)
        logger.info("INTERACTIVE MONITORING SETUP")
        logger.info("=" * 60)

        instructions = """
INSTRUCTIONS FOR MANUAL TESTING:

1. The debug script is now running and logging all API requests
   - All requests/responses are logged to: debug_ui_hanging.log
   - Check the terminal for real-time logging

2. In another terminal/browser:
   - Open http://localhost:8501 (Streamlit UI)
   - Type "high in the chart" in the chat input
   - Watch what happens (hang or successful response)

3. The script is monitoring:
   ✓ API health and status
   ✓ Direct API query responses
   ✓ Response timing
   ✓ Error messages

4. What to look for if UI hangs:
   ✓ Check if API actually receives/processes the request
   ✓ Check if API returns a response
   ✓ Check the timing - does API respond quickly?
   ✓ Check the browser console (F12) for JavaScript errors
   ✓ Check Streamlit logs for Python errors

5. Known observations from earlier testing:
   ✓ "high in the chart" works via direct API call (~2.68s)
   ✓ "top 5 scorers" works via UI
   ✓ Issue appears to be in UI/Streamlit layer, not API

6. Press Ctrl+C to stop monitoring when done
        """
        logger.info(instructions)

    def diagnose_hanging(self):
        """Run comprehensive diagnostics."""
        logger.info("\n" + "=" * 60)
        logger.info("UI HANGING DIAGNOSIS SCRIPT")
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        # Step 1: Check health
        if not self.check_api_health():
            logger.error("❌ Cannot proceed without API - please start the API")
            return

        if not self.check_streamlit_ui():
            logger.error("❌ Cannot proceed without UI - please start Streamlit")
            return

        # Step 2: Test problematic queries
        self.test_problematic_queries()

        # Step 3: Show instructions for manual testing
        self.monitor_with_instructions()

        # Step 4: Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary."""
        logger.info("\n" + "=" * 60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 60)

        if not self.test_results:
            logger.info("No test results yet")
            return

        success_count = sum(1 for r in self.test_results if r.get("status") == "success")
        error_count = sum(1 for r in self.test_results if r.get("status") == "error")
        timeout_count = sum(1 for r in self.test_results if r.get("status") == "timeout")

        logger.info(f"Total tests: {len(self.test_results)}")
        logger.info(f"✅ Successful: {success_count}")
        logger.info(f"❌ Errors: {error_count}")
        logger.info(f"⏱️  Timeouts: {timeout_count}")

        logger.info("\nDetailed results:")
        for result in self.test_results:
            status_icon = (
                "✅"
                if result.get("status") == "success"
                else "❌" if result.get("status") == "error" else "⏱️"
            )
            elapsed = (
                f"{result.get('elapsed_time', 0):.3f}s"
                if result.get("elapsed_time")
                else "N/A"
            )
            logger.info(
                f"{status_icon} {result.get('query', 'N/A'):30} | "
                f"Time: {elapsed:10} | Status: {result.get('status')}"
            )

        logger.info("\n" + "=" * 60)
        logger.info("NEXT STEPS:")
        logger.info("=" * 60)
        logger.info("""
1. If all API tests pass but UI still hangs:
   → Issue is in Streamlit/UI layer or network communication
   → Check browser console (F12) for JavaScript errors
   → Check Streamlit terminal for Python exceptions

2. If API tests timeout or fail:
   → API has issues processing the query
   → Check API logs for detailed error messages
   → Query may need SQL/Vector search optimization

3. For "high in the chart" specifically:
   → Query classification: might be CONTEXTUAL/VECTOR
   → Check if it needs special handling
   → Compare with similar working queries
        """)


def main():
    """Main entry point."""
    monitor = UIActivityMonitor()

    try:
        monitor.diagnose_hanging()

        # Keep running to capture real-time logs
        logger.info("\n🔍 Monitoring active... (Press Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n\n📊 Monitoring stopped by user")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
