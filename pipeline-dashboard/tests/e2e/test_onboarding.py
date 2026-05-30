from playwright.sync_api import Page


def test_welcome_to_dashboard(page: Page, live_server_url: str):
    page.goto(live_server_url)
    page.evaluate("localStorage.clear()")
    page.reload()
    page.wait_for_selector("text=SDLC Pipeline Dashboard", state="visible", timeout=10000)
    page.wait_for_selector("button:has-text('Start Building')", state="visible")

    page.click("button:has-text('Start Building')")
    page.wait_for_selector("text=What is this?", state="visible")

    page.click("button:has-text('Next')")
    page.wait_for_selector("text=Pick Your AI Model", state="visible")

    page.click("button:has-text('Next')")
    page.wait_for_selector("text=Choose Build Type", state="visible")

    page.click("button:has-text('Next')")
    page.wait_for_selector("text=Describe Your Idea", state="visible")

    page.click("button:has-text('Next')")
    page.wait_for_selector("text=Watch It Build", state="visible")

    page.click("button:has-text('Get Started')")
    page.wait_for_selector("text=Select AI Model", state="visible")


def test_skip_tutorial(page: Page, live_server_url: str):
    page.goto(live_server_url)
    page.evaluate("localStorage.clear()")
    page.reload()
    page.wait_for_selector("button:has-text('Start Building')", state="visible", timeout=10000)
    page.click("button:has-text('Start Building')")
    page.click("button:has-text('Skip')")
    page.wait_for_selector("text=Select AI Model", state="visible")


def test_returning_user_skips_welcome(page: Page, live_server_url: str):
    page.goto(live_server_url)
    page.evaluate("localStorage.setItem('hasSeenTutorial', 'true')")
    page.reload()
    page.wait_for_selector("text=Select AI Model", state="visible", timeout=10000)
