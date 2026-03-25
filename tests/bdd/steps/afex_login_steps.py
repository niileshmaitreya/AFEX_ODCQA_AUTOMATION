
import re
import pytest
from pytest_bdd import given, when, then, parsers
from playwright.sync_api import expect
from pages.afex_login_page import AfexLoginPage

@given('I open the AFEX login page')
def open_login(page):
    AfexLoginPage(page).goto()
    
@then("I should see the login page")
def assert_login_page(page):
    ap = AfexLoginPage(page)
    ap.wait_for_login(timeout_ms=40000)
    expect(page).to_have_url(re.compile(ap.pom.url), timeout=30000)

@when('I enter the email')
def enter_email(page, creds):
    if not creds["email"]:
        pytest.skip("Set USERNAME env")
    AfexLoginPage(page).enter_email(creds["email"])

@when('I enter the password if allowed')
def enter_password_if_allowed(page, creds):
    if creds["password"] and creds["allow_submit"]:
        AfexLoginPage(page).enter_password(creds["password"])

@when('I click the Sign in button if allowed')
def click_sign_in_if_allowed(page, creds):
    if creds["password"] and creds["allow_submit"]:
        AfexLoginPage(page).sign_in_after_password()

@then('I should see the dashboard URL')
def assert_dashboard_url(page):
    ap = AfexLoginPage(page)
    ap.wait_for_dashboard(timeout_ms=10000)
    expect(page).to_have_url(re.compile(ap.pom.dashboard_regex), timeout=30000)
    

@then('the database connectivity check should pass')
def db_connectivity(mssql_client):
    if mssql_client is None:
        pytest.skip("DB not configured; skipping connectivity check")
        
    rows = mssql_client.query_all("select top 1 * from [AFEX-CORE-FINANCIALS].core.cor_acl_user order by 1 DESC;")

    assert len(rows) == 1,"MSSQL connectivity failed or returned unexpected result"


@when(parsers.parse('I enter email "{email}"'))
def enter_email_from_feature(page, email):
    AfexLoginPage(page).enter_email(email)


@when(parsers.parse('I enter password "{password}"'))
def enter_password_from_feature(page, password):
    AfexLoginPage(page).enter_password(password)
