import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Optional, List

from fastmcp import FastMCP
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from playwright_stealth import stealth_async, StealthConfig


def ensure_playwright_installed():
    """Ensure Playwright Chromium is installed"""
    try:
        # Quick check by trying to get browser executable path
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            try:
                # Try to get the browser executable path
                browser_path = p.chromium.executable_path
                if browser_path and os.path.exists(browser_path):
                    return  # Chromium is already installed
            except Exception:
                pass

        print("Playwright Chromium not found. Installing...")
        # Install chromium browser
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"],
            check=False,
        )
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"], check=False
        )

        if result.returncode != 0:
            print("Warning: Failed to install Playwright Chromium automatically.")
            print("Please run: playwright install chromium")
        else:
            print("Playwright Chromium installed successfully!")

    except Exception as e:
        print(f"Warning: Could not verify/install Playwright Chromium: {e}")
        print("Please run: playwright install chromium")


# Initialize MCP server
mcp = FastMCP("Playwright Stealth Browser")


class BrowserManager:
    """Manages browser state and operations"""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.pages: List[Page] = []
        self.current_page_index = 0
        self.network_requests = []
        self.console_messages = []
        self.vision_mode = False
        self.headless = False

    async def start_browser(self, headless: bool = False, vision_mode: bool = False):
        """Start the browser with the specified configuration"""
        self.headless = headless
        self.vision_mode = vision_mode

        if self.browser:
            await self.close_browser()

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self.page = await self.context.new_page()

        # Apply stealth
        await stealth_async(
            self.page,
            StealthConfig(
                languages=["en"],
            ),
        )

        # Set up network and console monitoring
        self.page.on(
            "request",
            lambda req: self.network_requests.append(
                {
                    "url": req.url,
                    "method": req.method,
                    "headers": dict(req.headers),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
        )

        self.page.on(
            "console",
            lambda msg: self.console_messages.append(
                {
                    "type": msg.type,
                    "text": msg.text,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
        )

        self.pages = [self.page]
        self.current_page_index = 0

    async def ensure_browser(self):
        """Ensure browser is running and return current page"""
        if not self.browser or not self.page:
            await self.start_browser(
                headless=self.headless, vision_mode=self.vision_mode
            )
        return self.page

    async def get_current_page(self) -> Page:
        """Get the currently active page"""
        if self.pages and 0 <= self.current_page_index < len(self.pages):
            return self.pages[self.current_page_index]
        return await self.ensure_browser()

    async def close_browser(self):
        """Close the browser and clean up resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.pages = []
        self.current_page_index = 0

    async def take_accessibility_snapshot(self):
        """Take accessibility snapshot of current page"""
        page = await self.get_current_page()
        try:
            # Get accessibility tree
            snapshot = await page.accessibility.snapshot()
            return (
                json.dumps(snapshot, indent=2)
                if snapshot
                else "No accessibility information available"
            )
        except Exception as e:
            return f"Failed to take accessibility snapshot: {str(e)}"


# Global browser manager instance
browser_manager = BrowserManager()


# Helper functions for backward compatibility
async def ensure_browser():
    """Ensure browser is running and return current page"""
    return await browser_manager.ensure_browser()


async def get_current_page() -> Page:
    """Get the currently active page"""
    return await browser_manager.get_current_page()


async def take_accessibility_snapshot():
    """Take accessibility snapshot of current page"""
    return await browser_manager.take_accessibility_snapshot()


# Navigation Tools
@mcp.tool()
async def browser_navigate(url: str) -> str:
    """Navigate to a URL"""
    try:
        page = await ensure_browser()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return f"Successfully navigated to {url}"
    except Exception as e:
        return f"Failed to navigate to {url}: {str(e)}"


@mcp.tool()
async def browser_navigate_back() -> str:
    """Go back to the previous page"""
    try:
        page = await get_current_page()
        await page.go_back(wait_until="domcontentloaded")
        return "Successfully navigated back"
    except Exception as e:
        return f"Failed to navigate back: {str(e)}"


@mcp.tool()
async def browser_navigate_forward() -> str:
    """Go forward to the next page"""
    try:
        page = await get_current_page()
        await page.go_forward(wait_until="domcontentloaded")
        return "Successfully navigated forward"
    except Exception as e:
        return f"Failed to navigate forward: {str(e)}"


# Interaction Tools
@mcp.tool()
async def browser_snapshot() -> str:
    """Capture accessibility snapshot of the current page, this is better than screenshot"""
    try:
        return await browser_manager.take_accessibility_snapshot()
    except Exception as e:
        return f"Failed to take snapshot: {str(e)}"


@mcp.tool()
async def browser_click(element: str, ref: str) -> str:
    """Click on an element"""
    try:
        page = await get_current_page()
        selectors = [ref, f'[data-testid="{ref}"]', f"#{ref}", f".{ref}"]

        for selector in selectors:
            try:
                if await page.locator(selector).count() > 0:
                    await page.click(selector)
                    return f"Successfully clicked on {element}"
            except Exception:
                continue

        return f"Could not find element {element} with reference {ref}"
    except Exception as e:
        return f"Failed to click on {element}: {str(e)}"


@mcp.tool()
async def browser_type(
    element: str, ref: str, text: str, submit: bool = False, slowly: bool = False
) -> str:
    """Type text into editable element"""
    try:
        page = await get_current_page()
        selectors = [ref, f'[data-testid="{ref}"]', f"#{ref}", f".{ref}"]

        for selector in selectors:
            try:
                if await page.locator(selector).count() > 0:
                    if slowly:
                        await page.type(selector, text, delay=100)
                    else:
                        await page.fill(selector, text)

                    if submit:
                        await page.press(selector, "Enter")

                    return f"Successfully typed '{text}' into {element}"
            except Exception:
                continue

        return f"Could not find element {element} with reference {ref}"
    except Exception as e:
        return f"Failed to type into {element}: {str(e)}"


@mcp.tool()
async def browser_hover(element: str, ref: str) -> str:
    """Hover over element on page"""
    try:
        page = await get_current_page()
        selectors = [ref, f'[data-testid="{ref}"]', f"#{ref}", f".{ref}"]

        for selector in selectors:
            try:
                if await page.locator(selector).count() > 0:
                    await page.hover(selector)
                    return f"Successfully hovered over {element}"
            except Exception:
                continue

        return f"Could not find element {element} with reference {ref}"
    except Exception as e:
        return f"Failed to hover over {element}: {str(e)}"


@mcp.tool()
async def browser_drag(
    startElement: str, startRef: str, endElement: str, endRef: str
) -> str:
    """Drag from one element to another"""
    try:
        page = await get_current_page()

        start_selectors = [
            startRef,
            f'[data-testid="{startRef}"]',
            f"#{startRef}",
            f".{startRef}",
        ]
        end_selectors = [
            endRef,
            f'[data-testid="{endRef}"]',
            f"#{endRef}",
            f".{endRef}",
        ]

        start_element = None
        end_element = None

        for selector in start_selectors:
            if await page.locator(selector).count() > 0:
                start_element = selector
                break

        for selector in end_selectors:
            if await page.locator(selector).count() > 0:
                end_element = selector
                break

        if start_element and end_element:
            await page.drag_and_drop(start_element, end_element)
            return f"Successfully dragged from {startElement} to {endElement}"
        else:
            return "Could not find start or end element"

    except Exception as e:
        return f"Failed to drag: {str(e)}"


@mcp.tool()
async def browser_select_option(element: str, ref: str, values: List[str]) -> str:
    """Select an option in a dropdown"""
    try:
        page = await get_current_page()
        selectors = [ref, f'[data-testid="{ref}"]', f"#{ref}", f".{ref}"]

        for selector in selectors:
            try:
                if await page.locator(selector).count() > 0:
                    await page.select_option(selector, values)
                    return f"Successfully selected {values} in {element}"
            except Exception:
                continue

        return f"Could not find element {element} with reference {ref}"
    except Exception as e:
        return f"Failed to select option: {str(e)}"


@mcp.tool()
async def browser_press_key(key: str) -> str:
    """Press a key on the keyboard"""
    try:
        page = await get_current_page()
        await page.keyboard.press(key)
        return f"Successfully pressed key: {key}"
    except Exception as e:
        return f"Failed to press key {key}: {str(e)}"


@mcp.tool()
async def browser_wait_for(
    time: Optional[float] = None,
    text: Optional[str] = None,
    textGone: Optional[str] = None,
) -> str:
    """Wait for a condition"""
    try:
        page = await get_current_page()

        if time:
            await page.wait_for_timeout(int(time * 1000))
            return f"Waited for {time} seconds"
        elif text:
            await page.wait_for_selector(f'text="{text}"', timeout=30000)
            return f"Text '{text}' appeared"
        elif textGone:
            await page.wait_for_selector(
                f'text="{textGone}"', state="detached", timeout=30000
            )
            return f"Text '{textGone}' disappeared"
        else:
            return "No wait condition specified"
    except Exception as e:
        return f"Failed to wait: {str(e)}"


@mcp.tool()
async def browser_file_upload(paths: List[str]) -> str:
    """Upload one or multiple files"""
    try:
        page = await get_current_page()
        # Look for file input elements
        file_inputs = page.locator('input[type="file"]')
        if await file_inputs.count() > 0:
            await file_inputs.first.set_input_files(paths)
            return f"Successfully uploaded files: {', '.join(paths)}"
        else:
            return "No file input found on the page"
    except Exception as e:
        return f"Failed to upload files: {str(e)}"


@mcp.tool()
async def browser_handle_dialog(accept: bool, promptText: Optional[str] = None) -> str:
    """Handle a dialog"""
    try:
        page = await get_current_page()

        # Set up dialog handler
        def handle_dialog(dialog):
            if accept:
                if promptText and dialog.type == "prompt":
                    dialog.accept(promptText)
                else:
                    dialog.accept()
            else:
                dialog.dismiss()

        page.on("dialog", handle_dialog)
        return (
            f"Dialog handler set up - will {'accept' if accept else 'dismiss'} dialogs"
        )

    except Exception as e:
        return f"Failed to handle dialog: {str(e)}"


# Resource Tools
@mcp.tool()
async def browser_take_screenshot(
    raw: bool = False,
    filename: Optional[str] = None,
    element: Optional[str] = None,
    ref: Optional[str] = None,
) -> str:
    """Take a screenshot of the current page"""
    try:
        page = await get_current_page()

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = "png" if raw else "jpeg"
            filename = f"page-{timestamp}.{extension}"

        screenshot_options = {
            "path": filename,
            "type": "png" if raw else "jpeg",
            "quality": 90 if not raw else None,
        }

        if element and ref:
            selectors = [ref, f'[data-testid="{ref}"]', f"#{ref}", f".{ref}"]
            for selector in selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.locator(selector).screenshot(**screenshot_options)
                        return f"Screenshot of {element} saved to {filename}"
                except Exception:
                    continue
            return f"Could not find element {element} with reference {ref}"
        else:
            await page.screenshot(**screenshot_options)
            return f"Screenshot saved to {filename}"
    except Exception as e:
        return f"Failed to take screenshot: {str(e)}"


@mcp.tool()
async def browser_pdf_save(filename: Optional[str] = None) -> str:
    """Save page as PDF"""
    try:
        page = await get_current_page()

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"page-{timestamp}.pdf"

        await page.pdf(path=filename, format="A4")
        return f"PDF saved to {filename}"
    except Exception as e:
        return f"Failed to save PDF: {str(e)}"


@mcp.tool()
async def browser_network_requests() -> str:
    """Returns all network requests since loading the page"""
    try:
        return json.dumps(browser_manager.network_requests, indent=2)
    except Exception as e:
        return f"Failed to get network requests: {str(e)}"


@mcp.tool()
async def browser_console_messages() -> str:
    """Returns all console messages"""
    try:
        return json.dumps(browser_manager.console_messages, indent=2)
    except Exception as e:
        return f"Failed to get console messages: {str(e)}"


# Utility Tools
@mcp.tool()
async def browser_install() -> str:
    """Install the browser specified in the config"""
    try:
        os.system("playwright install chromium")
        return "Browser installation completed"
    except Exception as e:
        return f"Failed to install browser: {str(e)}"


@mcp.tool()
async def browser_close() -> str:
    """Close the page"""
    global _browser, _context, _page, _playwright, _pages
    try:
        await browser_manager.close_browser()
        return "Browser closed successfully"
    except Exception as e:
        return f"Failed to close browser: {str(e)}"


@mcp.tool()
async def browser_resize(width: int, height: int) -> str:
    """Resize the browser window"""
    try:
        page = await get_current_page()
        await page.set_viewport_size({"width": width, "height": height})
        return f"Browser resized to {width}x{height}"
    except Exception as e:
        return f"Failed to resize browser: {str(e)}"


# Tab Management Tools
@mcp.tool()
async def browser_tab_list() -> str:
    """List browser tabs"""
    try:
        tabs_info = []
        for i, page in enumerate(browser_manager.pages):
            tabs_info.append(
                {
                    "index": i,
                    "url": page.url,
                    "title": page.title(),
                    "active": i == browser_manager.current_page_index,
                }
            )
        return json.dumps(tabs_info, indent=2)
    except Exception as e:
        return f"Failed to list tabs: {str(e)}"


@mcp.tool()
async def browser_tab_new(url: Optional[str] = None) -> str:
    """Open a new tab"""
    global _pages, _current_page_index
    try:
        context = browser_manager.context or await ensure_browser().context
        new_page = await context.new_page()

        # Apply stealth to new page
        await stealth_async(
            new_page,
            StealthConfig(
                languages=["en-US", "en"],
                webgl_vendor="Intel Inc.",
                webgl_renderer="Intel Iris OpenGL Engine",
            ),
        )

        browser_manager.pages.append(new_page)
        browser_manager.current_page_index = len(browser_manager.pages) - 1

        if url:
            await new_page.goto(url)
            return f"New tab opened and navigated to {url}"
        else:
            return "New blank tab opened"
    except Exception as e:
        return f"Failed to open new tab: {str(e)}"


@mcp.tool()
async def browser_tab_select(index: int) -> str:
    """Select a tab by index"""
    global _current_page_index
    try:
        if 0 <= index < len(browser_manager.pages):
            browser_manager.current_page_index = index
            return f"Selected tab {index}"
        else:
            return f"Invalid tab index {index}. Available tabs: 0-{len(browser_manager.pages) - 1}"
    except Exception as e:
        return f"Failed to select tab: {str(e)}"


@mcp.tool()
async def browser_tab_close(index: Optional[int] = None) -> str:
    """Close a tab"""
    global _pages, _current_page_index
    try:
        close_index = index if index is not None else browser_manager.current_page_index

        if 0 <= close_index < len(browser_manager.pages):
            await browser_manager.pages[close_index].close()
            browser_manager.pages.pop(close_index)

            if (
                browser_manager.current_page_index >= close_index
                and browser_manager.current_page_index > 0
            ):
                browser_manager.current_page_index -= 1

            return f"Closed tab {close_index}"
        else:
            return f"Invalid tab index {close_index}"
    except Exception as e:
        return f"Failed to close tab: {str(e)}"


# Testing Tools
@mcp.tool()
async def browser_generate_playwright_test(
    name: str, description: str, steps: List[str]
) -> str:
    """Generate a Playwright test for given scenario"""
    try:
        test_code = f'''
from playwright.sync_api import Page, expect
from playwright_stealth import stealth_sync, StealthConfig

def test_{name.lower().replace(" ", "_")}(page: Page):
    """
    {description}
    """
    # Apply stealth
    stealth_sync(page, StealthConfig(languages=["en-US", "en"]))
    
'''

        for i, step in enumerate(steps, 1):
            test_code += f"    # Step {i}: {step}\n"
            test_code += f"    # TODO: Implement step {i}\n\n"

        return test_code
    except Exception as e:
        return f"Failed to generate test: {str(e)}"


# Vision Mode Tools (for screenshot-based interaction)
@mcp.tool()
async def browser_screen_capture() -> str:
    """Take a screenshot of the current page"""
    return await browser_take_screenshot()


@mcp.tool()
async def browser_screen_move_mouse(element: str, x: int, y: int) -> str:
    """Move mouse to a given position"""
    try:
        page = await get_current_page()
        await page.mouse.move(x, y)
        return f"Mouse moved to ({x}, {y}) for {element}"
    except Exception as e:
        return f"Failed to move mouse: {str(e)}"


@mcp.tool()
async def browser_screen_click(element: str, x: int, y: int) -> str:
    """Click left mouse button"""
    try:
        page = await get_current_page()
        await page.mouse.click(x, y)
        return f"Clicked at ({x}, {y}) for {element}"
    except Exception as e:
        return f"Failed to click: {str(e)}"


@mcp.tool()
async def browser_screen_drag(
    element: str, startX: int, startY: int, endX: int, endY: int
) -> str:
    """Drag left mouse button"""
    try:
        page = await get_current_page()
        await page.mouse.move(startX, startY)
        await page.mouse.down()
        await page.mouse.move(endX, endY)
        await page.mouse.up()
        return f"Dragged from ({startX}, {startY}) to ({endX}, {endY}) for {element}"
    except Exception as e:
        return f"Failed to drag: {str(e)}"


@mcp.tool()
async def browser_screen_type(text: str, submit: bool = False) -> str:
    """Type text"""
    try:
        page = await get_current_page()
        await page.keyboard.type(text)
        if submit:
            await page.keyboard.press("Enter")
        return f"Typed: {text}"
    except Exception as e:
        return f"Failed to type: {str(e)}"


async def main():
    """Main entry point for the MCP server"""
    import sys

    # Parse command line arguments
    vision_mode = "--vision" in sys.argv
    headless_mode = "--headless" in sys.argv

    # Transport options - default to HTTP if running in Docker
    transport = "stdio"  # default
    host = "localhost"
    port = 3000

    # Detect if running in Docker and default to HTTP transport
    is_docker = os.path.exists("/.dockerenv") or os.environ.get("CONTAINER") == "docker"
    if is_docker and not any(
        arg in sys.argv for arg in ["--stdio", "--http", "--streamable-http", "--sse"]
    ):
        transport = "streamable-http"
        host = "0.0.0.0"  # Listen on all interfaces in Docker

    if "--stdio" in sys.argv:
        transport = "stdio"
    elif "--http" in sys.argv or "--streamable-http" in sys.argv:
        transport = "streamable-http"
    elif "--sse" in sys.argv:
        transport = "sse"

    # Parse host and port if provided
    for i, arg in enumerate(sys.argv):
        if arg == "--host" and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
        elif arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])

    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
Playwright Stealth Browser MCP Server

Usage:
  stealth-browser-mcp [OPTIONS]

Options:
  --vision              Enable vision mode (screenshot-based interactions)
  --headless            Run browser in headless mode
  --stdio               Force stdio transport (default outside Docker)
  --http, --streamable-http  Run with HTTP transport (default in Docker)
  --sse                 Run with Server-Sent Events transport
  --host HOST           Host to bind to (default: localhost, 0.0.0.0 in Docker)
  --port PORT           Port to bind to (default: 3000)
  --help, -h           Show this help message

Transport Examples:
  # Run with stdio transport (default outside Docker)
  stealth-browser-mcp
  
  # Run with HTTP transport
  stealth-browser-mcp --http --host 0.0.0.0 --port 8080
  
  # Run with SSE transport
  stealth-browser-mcp --sse --port 8080
  
  # Run in vision mode with HTTP transport
  stealth-browser-mcp --vision --http

Docker Usage:
  # Docker automatically defaults to HTTP transport on 0.0.0.0:3000
  docker run -p 3000:3000 playwright-mcp-server

MCP Client Configuration Examples:

For stdio transport:
{
  "mcpServers": {
    "stealth-browser": {
      "command": "uvx",
      "args": ["stealth-browser-mcp"]
    }
  }
}

For HTTP transport:
{
  "mcpServers": {
    "stealth-browser": {
      "transport": {
        "type": "http",
        "url": "http://localhost:3000"
      }
    }
  }
}

For SSE transport:
{
  "mcpServers": {
    "stealth-browser": {
      "transport": {
        "type": "sse",
        "url": "http://localhost:3000/sse"
      }
    }
  }
}
        """)
        return

    # Initialize browser on startup
    print(f"Starting browser - Vision mode: {vision_mode}, Headless: {headless_mode}")

    await browser_manager.start_browser(headless=headless_mode, vision_mode=vision_mode)

    print("Browser started successfully")
    if transport == "stdio":
        print("Running with stdio transport")
    elif transport == "streamable-http":
        print(f"Running with HTTP transport on {host}:{port}")
    elif transport == "sse":
        print(f"Running with SSE transport on {host}:{port}")

    try:
        if transport == "stdio":
            await mcp.run_async(transport="stdio")
        elif transport == "streamable-http":
            await mcp.run_async(transport="streamable-http", host=host, port=port)
        elif transport == "sse":
            await mcp.run_async(transport="sse", host=host, port=port)
    finally:
        # Clean up browser on shutdown
        await browser_manager.close_browser()


def main_sync():
    """Synchronous entry point for the script"""
    # Ensure Playwright Chromium is installed before starting
    ensure_playwright_installed()
    asyncio.run(main())


if __name__ == "__main__":
    ensure_playwright_installed()
    main_sync()
