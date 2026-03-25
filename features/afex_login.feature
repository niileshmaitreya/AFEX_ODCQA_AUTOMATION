
Feature: AFEX login and dashboard navigation
  As a user, I want to attempt login and land on the dashboard
  so that I can verify basic accessibility.

  @smoke @afex
  Scenario: Launch login page and (optionally) submit password to reach dashboard
    Given I open the AFEX login page
    Then I should see the login page
    When I enter the email
    And I enter the password if allowed
    And I click the Sign in button if allowed
    Then I should see the dashboard URL
    And the database connectivity check should pass

  @dataDriven @login
  Scenario Outline: User logs in using credentials from feature file
    Given I open the AFEX login page
    Then I should see the login page
    When I enter email "<username>"
    And I enter password "<password>"
    And I click the Sign in button if allowed
    Then I should see the dashboard URL
    And the database connectivity check should pass

  Examples:
    | username           | password  |
    | IRFAN              | PAssword1 |
    | TestA              | Test12345 |