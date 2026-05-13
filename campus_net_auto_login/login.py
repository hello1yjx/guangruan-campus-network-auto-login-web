from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, BrowserContext, Error, Page, Playwright, sync_playwright

from campus_net_auto_login.captcha_ocr import recognize_captcha


SELECTOR_PREFIX_MAP = {
    "id": "#",
    "class name": ".",
}


class CampusNetworkLogin:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.runtime_dir = Path("runtime")
        self.runtime_dir.mkdir(exist_ok=True)
        self.page_timeout_ms = int(self.config.get("page_timeout_seconds", 15)) * 1000

    def _build_browser(self, playwright: Playwright) -> tuple[Browser, BrowserContext, Page]:
        chrome_config = self.config.get("chrome", {})
        runtime_profile_dir = Path(os.environ.get("TEMP", "C:\\Temp")) / "campus-net-chrome-profile"
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-gpu",
            "--disable-dev-shm-usage",
        ]

        user_data_dir = str(chrome_config.get("user_data_dir", "")).strip()
        if not user_data_dir:
            runtime_profile_dir.mkdir(parents=True, exist_ok=True)
            user_data_dir = str(runtime_profile_dir.resolve())

        binary_path = str(chrome_config.get("binary_path", "")).strip() or None
        browser = playwright.chromium.launch(
            channel="chrome" if not binary_path else None,
            executable_path=binary_path,
            headless=bool(chrome_config.get("headless", False)),
            args=launch_args,
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True,
        )
        page = context.new_page()
        page.set_default_timeout(self.page_timeout_ms)
        return browser, context, page

    def _selector_to_playwright(self, by_name: str, value: str) -> str | None:
        by_name = by_name.lower()
        if by_name == "name":
            return f'[name="{value}"]'
        if by_name == "css selector":
            return value
        if by_name == "xpath":
            return f"xpath={value}"
        prefix = SELECTOR_PREFIX_MAP.get(by_name)
        if prefix is not None:
            return f"{prefix}{value}"
        if by_name == "tag name":
            return value
        return None

    def _find_with_candidates(self, page: Page, name: str):
        selectors = self.config["selectors"].get(name, [])
        last_error: Exception | None = None

        for selector in selectors:
            playwright_selector = self._selector_to_playwright(selector["by"], selector["value"])
            if playwright_selector is None:
                continue
            try:
                locator = page.locator(playwright_selector).first
                locator.wait_for(state="attached", timeout=self.page_timeout_ms)
                return locator
            except Error as error:
                last_error = error

        raise RuntimeError(f"Could not find element `{name}`. Check selectors in config.json.") from last_error

    def _fill(self, locator, value: str) -> None:
        locator.click()
        locator.fill("")
        locator.fill(value)

    def _capture_captcha(self, page: Page) -> Path:
        captcha_image = self._find_with_candidates(page, "captcha_image")
        captcha_path = self.runtime_dir / "captcha.png"
        captcha_image.screenshot(path=str(captcha_path))
        return captcha_path

    def _refresh_captcha(self, page: Page) -> None:
        try:
            refresh_target = self._find_with_candidates(page, "captcha_refresh")
            refresh_target.click()
            page.wait_for_timeout(1000)
        except RuntimeError:
            page.reload()
            page.wait_for_timeout(2000)

    def _page_text(self, page: Page) -> str:
        return page.content().lower()

    def _is_success_panel_visible(self, page: Page) -> bool:
        try:
            return page.locator("#success").is_visible()
        except Error:
            return False

    def _is_login_panel_hidden(self, page: Page) -> bool:
        try:
            login_panel = page.locator("#login")
            if login_panel.count() == 0:
                return False
            return not login_panel.is_visible()
        except Error:
            return False

    def _is_login_success(self, page: Page, previous_url: str) -> bool:
        current_url = page.url
        page_text = self._page_text(page)
        success_keywords = [keyword.lower() for keyword in self.config.get("success_keywords", [])]

        if self._is_success_panel_visible(page) or self._is_login_panel_hidden(page):
            return True

        if current_url != previous_url:
            return True

        return any(keyword in page_text for keyword in success_keywords)

    def _is_known_failure(self, page: Page) -> bool:
        page_text = self._page_text(page)
        failure_keywords = [keyword.lower() for keyword in self.config.get("failure_keywords", [])]
        return any(keyword in page_text for keyword in failure_keywords)

    def _submit_once(self, page: Page, attempt: int) -> bool:
        username_input = self._find_with_candidates(page, "username")
        password_input = self._find_with_candidates(page, "password")
        captcha_input = self._find_with_candidates(page, "captcha_input")
        submit_button = self._find_with_candidates(page, "submit_button")

        captcha_path = self._capture_captcha(page)
        captcha_code = recognize_captcha(captcha_path, self.config.get("ocr", {}))
        expected_length = int(self.config.get("ocr", {}).get("expected_length", 4))

        print(f"[Attempt {attempt}] OCR result: {captcha_code or '<empty>'}")

        if not captcha_code:
            print("Captcha OCR returned an empty result. Retrying.")
            return False

        if expected_length > 0 and len(captcha_code) != expected_length:
            print(f"Captcha length is not {expected_length}. Retrying.")
            return False

        self._fill(username_input, self.config["username"])
        self._fill(password_input, self.config["password"])
        self._fill(captcha_input, captcha_code)

        previous_url = page.url
        submit_button.click()
        page.wait_for_timeout(int(float(self.config.get("after_submit_wait_seconds", 3)) * 1000))

        if self._is_login_success(page, previous_url):
            return True

        if self._is_known_failure(page):
            print("The page returned a known failure message.")
        else:
            print("No clear success signal detected. Will retry if attempts remain.")
        return False

    def run(self) -> bool:
        max_attempts = int(self.config.get("max_attempts", 5))

        try:
            with sync_playwright() as playwright:
                browser, context, page = self._build_browser(playwright)
                try:
                    page.goto(self.config["login_url"], wait_until="domcontentloaded")

                    for attempt in range(1, max_attempts + 1):
                        try:
                            success = self._submit_once(page, attempt)
                            if success:
                                print("Login succeeded.")
                                return True
                        except RuntimeError as error:
                            print(f"Page structure does not match the current selectors: {error}")
                            return False

                        if attempt < max_attempts:
                            self._refresh_captcha(page)

                    print(f"Reached the maximum retry count ({max_attempts}). Login failed.")
                    return False
                finally:
                    context.close()
                    browser.close()
        except Error as error:
            print("Browser startup failed. Check Playwright and Chrome configuration.")
            print(f"Details: {error}")
            return False
