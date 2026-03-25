
from __future__ import annotations
import json, re
from pathlib import Path
import time
from playwright.sync_api import Page, Locator

class POMLoader:
    def __init__(self, file_path: str | Path):
        self._data = json.loads(Path(file_path).read_text(encoding='utf-8'))

    @property
    def url(self) -> str:
        return self._data.get('url')

    @property
    def dashboard_regex(self) -> str:
        return self._data.get('dashboard_regex')

    def sel(self, key: str) -> str:
        return self._data['selectors'][key]

class AfexLoginPage:
    def __init__(self, page: Page, poml_path: str | Path = 'poml/afex_login.json'):
        self.page = page
        self.pom = POMLoader(poml_path)
        self.email_input: Locator = page.locator(self.pom.sel('email_input'))
        self.password_input: Locator = page.locator(self.pom.sel('password_input'))
        self.sign_in_button: Locator = page.locator(self.pom.sel('sign_in_button'))

    def goto(self):
        self.page.pause()
        self.page.set_default_navigation_timeout=60000
        self.page.goto(self.pom.url, wait_until="domcontentloaded", timeout=60000)

    def enter_email(self, email: str):
        self.email_input.fill(email)

    def enter_password(self, password: str):
        self.password_input.fill(password)

    def sign_in_after_password(self):
        self.sign_in_button.click()

    def wait_for_login(self, timeout_ms: int = 60000):
        self.page.wait_for_url(
                self.pom.url,
                wait_until="commit",
                timeout=40000
            )
    def wait_for_dashboard(self, timeout_ms: int = 60000):
        pat = re.compile(self.pom.dashboard_regex)
        # self.page.wait_for_url(pat, timeout=timeout_ms)
        self.page.wait_for_url(
                self.pom.dashboard_regex,
                wait_until="commit",
                timeout=40000
            )

