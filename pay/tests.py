from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase 
from selenium.webdriver.firefox.webdriver import WebDriver
from .models import User, Account, ConversionTable, Transaction
import time, unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from datetime import datetime
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
import responses
from decimal import Decimal
from django.test import Client
from django.urls import reverse
import json



class SeleniumTest(StaticLiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp (self):
        user = User.objects.create_superuser(username='Gloria', password='myhouse', email='gloria@test.com', is_active=True)
        user.save()

    def login(self, username="Gloria", password ="myhouse"):
        self.selenium.get(f"{self.live_server_url}/pay/ui")
        username_input = self.selenium.find_element(By.XPATH, '//*[@id="username"]')
        username_input.send_keys(username)
        password_input = self.selenium.find_element(By.XPATH, '//*[@id="password"]')
        password_input.send_keys(password)
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        wait = WebDriverWait(self.selenium, 1)  
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/h1')))

    def test_login(self):
        self.login()
        wait = WebDriverWait(self.selenium, 1)  
        title = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/h1')))
        self.assertEqual(title.text, "Welcome Gloria!")

    def test_register(self):
        self.selenium.get(f"{self.live_server_url}/pay/ui")
        register_button = self.selenium.find_element(By.XPATH, '/html/body/div/div/button[2]')
        register_button.click()
        wait = WebDriverWait(self.selenium, 1)  
        title = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        self.assertEqual(title.text, "Register")
        username_input = self.selenium.find_element(By.XPATH, '//*[@id="username"]')
        username_input.send_keys("Melman")
        password_input = self.selenium.find_element(By.XPATH, '//*[@id="password"]')
        password_input.send_keys("mymelman")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Registration successful! You can now log in.")
        alert.accept() 
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        self.login(username = "Melman", password = "mymelman")
        wait = WebDriverWait(self.selenium, 1)  
        title = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/h1')))
        self.assertEqual(title.text, "Welcome Melman!")

    def test_no_account(self):
        self.login()
        wait = WebDriverWait(self.selenium, 1)
        no_account = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/p')))
        self.assertEqual(no_account.text, "No accounts found")
    
    def test_creation_account_saving_CZK(self):
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[2]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        currency_dropdown = Select(self.selenium.find_element(By.ID, 'currency'))
        currency_dropdown.select_by_visible_text("CZK")
        account_type = Select(self.selenium.find_element(By.XPATH, '//*[@id="type"]'))
        account_type.select_by_visible_text("savings")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Account opened successfully!")
        alert.accept() 
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        element = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li')
        text = element.text.strip()
        self.assertTrue(text.startswith("savings ("))
        self.assertTrue(text.endswith(": 0.00 CZK"))

    def test_creation_account_regular_EUR(self):
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[2]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        currency_dropdown = Select(self.selenium.find_element(By.ID, 'currency'))
        currency_dropdown.select_by_visible_text("EUR")
        account_type = Select(self.selenium.find_element(By.XPATH, '//*[@id="type"]'))
        account_type.select_by_visible_text("regular")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Account opened successfully!")
        alert.accept() 
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        element = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li')
        text = element.text.strip()
        self.assertTrue(text.startswith("regular ("))
        self.assertTrue(text.endswith(": 0.00 EUR"))
    
    def test_creation_account_regular_EUR(self):
        user = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user, account_type="regular", currency="USD", balance = 50, account_number = "123ab45")
        Account.objects.create(owner=user, account_type="savings", currency="CZK", balance = 30000, account_number= "54ba321")
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[2]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        currency_dropdown = Select(self.selenium.find_element(By.ID, 'currency'))
        currency_dropdown.select_by_visible_text("EUR")
        account_type = Select(self.selenium.find_element(By.XPATH, '//*[@id="type"]'))
        account_type.select_by_visible_text("regular")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Account opened successfully!")
        alert.accept() 
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        element = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li')
        creat_acounts = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]')
        creat_acounts = element.text.strip()
        self.assertTrue(creat_acounts.startswith("regular ("))
        self.assertTrue(creat_acounts.endswith(": 0.00 EUR"))

    def test_add_money_CZK(self):
        user = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user, account_type="regular", currency="USD", balance = 0, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=user, account_type="savings", currency="CZK", balance = 30000, account_number= "54ba321", created_at=datetime(2024, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[3]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        select_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="account"]'))
        select_account.select_by_visible_text("regular (123ab45) - 0.00 USD")
        amount = self.selenium.find_element(By.XPATH, '//*[@id="amount"]')
        amount.send_keys("20")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Money added successfully!")
        alert.accept()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        creat_acounts = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[2]')
        creat_acounts = creat_acounts.text.strip()
        self.assertTrue(creat_acounts.startswith("regular ("))
        self.assertTrue(creat_acounts.endswith(": 20.00 USD"))

    def test_send_money_beetween_my_acounts(self):
        user = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user, account_type="regular", currency="CZK", balance = 50000, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=user, account_type="savings", currency="CZK", balance = 30000, account_number= "54ba321", created_at=datetime(2024, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[4]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        self.selenium.find_element(By.XPATH,'/html/body/div/div/div/div/button[1]').click()
        select_your_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="account"]'))
        select_your_account.select_by_visible_text("regular (123ab45) - 50000.00 CZK")
        target_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="targetAccount"]'))
        target_account.select_by_visible_text("savings (54ba321) - 30000.00 CZK")
        amount = self.selenium.find_element(By.XPATH, '//*[@id="amount"]')
        amount.send_keys("10000")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Money sent successfully!")
        alert.accept()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        creat_acounts = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[2]')
        creat_acounts = creat_acounts.text.strip()
        self.assertEqual(creat_acounts, 'regular (123ab45): 40000.00 CZK')
        creat_acounts_2 = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]')
        creat_acounts_2 = creat_acounts_2.text.strip()
        self.assertEqual(creat_acounts_2, 'savings (54ba321): 40000.00 CZK')

    def test_send_money_beetween_my_acounts_EUR_vs_CZK(self):
        user = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user, account_type="regular", currency="EUR", balance = 55.29, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=user, account_type="savings", currency="CZK", balance = 155.85, account_number= "54ba321", created_at=datetime(2024, 1, 1, 10, 0, 0))
        ConversionTable.objects.create(base_currency = 'EUR', target_currency = 'CZK', conversion_rate = 25.2789 ) 
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[4]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        self.selenium.find_element(By.XPATH,'/html/body/div/div/div/div/button[1]').click()
        select_your_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="account"]'))
        select_your_account.select_by_visible_text("regular (123ab45) - 55.29 EUR")
        target_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="targetAccount"]'))
        target_account.select_by_visible_text("savings (54ba321) - 155.85 CZK")
        amount = self.selenium.find_element(By.XPATH, '//*[@id="amount"]')
        amount.send_keys("10.38")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Money sent successfully!")
        alert.accept()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        creat_acounts = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[2]')
        creat_acounts = creat_acounts.text.strip()
        self.assertEqual(creat_acounts, 'regular (123ab45): 44.91 EUR')
        creat_acounts_2 = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]')
        creat_acounts_2 = creat_acounts_2.text.strip()
        self.assertEqual(creat_acounts_2, 'savings (54ba321): 418.24 CZK')

    def test_send_money_beetween_other_acounts(self):
        user_alex = User.objects.create_superuser(username='Alex', password='lev?alex', email='alex@test.com', is_active=True)
        user_alex.save()
        Account.objects.create(owner=user_alex, account_type="regular", currency="CZK", balance = 500.50, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        user_glorie = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user_glorie, account_type="regular", currency="CZK", balance = 950.40, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[4]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        self.selenium.find_element(By.XPATH,'/html/body/div/div/div/div/button[2]').click()
        select_your_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="account"]'))
        select_your_account.select_by_visible_text("regular (123ab45) - 950.40 CZK")
        target_account = self.selenium.find_element(By.XPATH, '//*[@id="targetAccount"]')
        target_account.send_keys("678cd9")
        account = self.selenium.find_element(By.XPATH, '//*[@id="amount"]')
        account.send_keys("250.30")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Money sent successfully!")
        alert.accept()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        acounts_gloria = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]')
        acounts_gloria = acounts_gloria.text.strip()
        self.assertEqual(acounts_gloria, 'regular (123ab45): 700.10 CZK')

    
    def test_send_money_beetween_other_acounts_EUR_vs_CZK(self):
        user_alex = User.objects.create_superuser(username='Alex', password='lev?alex', email='alex@test.com', is_active=True)
        user_alex.save()
        Account.objects.create(owner=user_alex, account_type="regular", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        ConversionTable.objects.create(base_currency = 'CZK', target_currency = 'EUR', conversion_rate = 0.040 ) 
        user_glorie = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user_glorie, account_type="regular", currency="CZK", balance = 950.00, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[4]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        self.selenium.find_element(By.XPATH,'/html/body/div/div/div/div/button[2]').click()
        select_your_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="account"]'))
        select_your_account.select_by_visible_text("regular (123ab45) - 950.00 CZK")
        target_account = self.selenium.find_element(By.XPATH, '//*[@id="targetAccount"]')
        target_account.send_keys("678cd9")
        account = self.selenium.find_element(By.XPATH, '//*[@id="amount"]')
        account.send_keys("100.00")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Money sent successfully!")
        alert.accept()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        acounts_gloria = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]')
        acounts_gloria = acounts_gloria.text.strip()
        self.assertEqual(acounts_gloria, 'regular (123ab45): 850.00 CZK')
        acounts_melman = Account.objects.get(account_number = "678cd9")
        self.assertEqual(acounts_melman.balance, 14.00)

    def test_Authorized_transactions_one_accout(self):  
        user_glorie = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user_glorie, account_type="regular", currency="USD", balance = 20, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[3]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        select_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="account"]'))
        select_account.select_by_visible_text("regular (123ab45) - 20.00 USD")
        amount = self.selenium.find_element(By.XPATH, '//*[@id="amount"]')
        amount.send_keys("20")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Money added successfully!")
        alert.accept()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[5]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        completed  = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li/div[1]')
        self.assertTrue(completed.text.startswith("Completed "))
        deposit = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li/div[2]')
        self.assertEqual(deposit.text, "Deposit") 
        to = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li/div[3]')
        self.assertEqual(to.text,"To: 123ab45")
        money = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li/div[4]/div')
        self.assertEqual(money.text, "20.00 USD")

    def test_send_Authorized_transactions_my_acounts_CZK(self):
        user = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user, account_type="regular", currency="CZK", balance = 55.29, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=user, account_type="savings", currency="CZK", balance = 155.85, account_number= "54ba321", created_at=datetime(2024, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[4]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        self.selenium.find_element(By.XPATH,'/html/body/div/div/div/div/button[1]').click()
        select_your_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="account"]'))
        select_your_account.select_by_visible_text("regular (123ab45) - 55.29 CZK")
        target_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="targetAccount"]'))
        target_account.select_by_visible_text("savings (54ba321) - 155.85 CZK")
        amount = self.selenium.find_element(By.XPATH, '//*[@id="amount"]')
        amount.send_keys("10.20")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Money sent successfully!")
        alert.accept()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[5]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        completed  = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li/div[1]')
        self.assertTrue(completed.text.startswith("Completed "))
        from_my = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li/div[2]')
        self.assertEqual(from_my.text, "From: 123ab45") 
        to = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li/div[3]')
        self.assertEqual(to.text,"To: 54ba321")
        money = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li/div[4]/div')
        self.assertEqual(money.text, "10.20 CZK")

    def test_send_money_beetween_my_acounts_no_money_transakction(self):
        user = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user, account_type="regular", currency="CZK", balance = 100, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=user, account_type="savings", currency="CZK", balance = 100, account_number= "54ba321", created_at=datetime(2024, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[4]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        self.selenium.find_element(By.XPATH,'/html/body/div/div/div/div/button[1]').click()
        select_your_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="account"]'))
        select_your_account.select_by_visible_text("regular (123ab45) - 100.00 CZK")
        target_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="targetAccount"]'))
        target_account.select_by_visible_text("savings (54ba321) - 100.00 CZK")
        amount = self.selenium.find_element(By.XPATH, '//*[@id="amount"]')
        amount.send_keys("150")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Failed to send money. Please try again.")
        alert.accept()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[5]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        completed  = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li/div[1]')
        self.assertTrue(completed.text.startswith("Failed (insufficient funds) "))
        from_my = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li/div[2]')
        self.assertEqual(from_my.text, "From: 123ab45") 
        to = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li/div[3]')
        self.assertEqual(to.text,"To: 54ba321")
        money = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li/div[4]/div')
        self.assertEqual(money.text, "150.00 CZK")

    def test_send_Authorized_transactions_next_previous(self):
        user = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user, account_type="regular", currency="CZK", balance = 100, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        account_number = Account.objects.get(account_number="123ab45")
        Transaction.objects.create(to_account = account_number, original_amount = 50, converted_amount = 50, conversion_rate = 1, authorized_by = user, type = "Deposit", status = "Completed", created_at=datetime(2022, 1, 1, 10, 0, 0))
        for i in range(11):
            Transaction.objects.create(
                to_account=account_number,
                original_amount=10 + i,
                converted_amount=10 + i,
                conversion_rate=1,
                authorized_by=user,
                type="Deposit" if i % 2 == 0 else "Withdrawal",
                status="Completed", 
                created_at=datetime(2023, 1, 1, 10, 0, 0)
                )
        Transaction.objects.create(to_account = account_number, original_amount = 100, converted_amount = 100, conversion_rate = 1, authorized_by = user, type = "Deposit", status = "Completed", created_at=datetime(2024, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[5]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/div[1]/button[2]').click()
        completed_last  = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li[3]/div[1]')
        self.assertTrue(completed_last.text.startswith("Completed "))
        deposit_last = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li[3]/div[2]')
        self.assertEqual(deposit_last.text, "Deposit") 
        to_last = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[3]/div[3]')
        self.assertEqual(to_last.text,"To: 123ab45")
        money_last = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[3]/div[4]')
        self.assertEqual(money_last.text, "50.00 CZK")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/div[1]/button[1]').click()

        completed_first = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li[1]/div[1]')
        self.assertTrue(completed_first.text.startswith("Completed "))
        deposit_first = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li[1]/div[2]')
        self.assertEqual(deposit_first.text, "Deposit") 
        to_first = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]/div[3]')
        self.assertEqual(to_first.text,"To: 123ab45")
        money_first = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]/div[4]')
        self.assertEqual(money_first.text, "100.00 CZK")
    
    def test_send_Authorized_transactions_page_size(self):
        user = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user, account_type="regular", currency="CZK", balance = 100, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        account_number = Account.objects.get(account_number="123ab45")
        Transaction.objects.create(to_account = account_number, original_amount = 50, converted_amount = 50, conversion_rate = 1, authorized_by = user, type = "Deposit", status = "Completed", created_at=datetime(2022, 1, 1, 10, 0, 0))
        for i in range(6):
            Transaction.objects.create(
                to_account=account_number,
                original_amount=5 + i,
                converted_amount=5 + i,
                conversion_rate=1,
                authorized_by=user,
                type="Deposit" if i % 2 == 0 else "Withdrawal",
                status="Completed", 
                created_at=datetime(2023, 1, 1, 10, 0, 0)
                )
        Transaction.objects.create(to_account = account_number, original_amount = 100, converted_amount = 100, conversion_rate = 1, authorized_by = user, type = "Deposit", status = "Completed", created_at=datetime(2024, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[5]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        page_size = Select(self.selenium.find_element(By.XPATH, '//*[@id="pageSize"]'))
        page_size.select_by_visible_text("5")

        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/div[1]/button[2]').click()
        completed_last  = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li[3]/div[1]')
        self.assertTrue(completed_last.text.startswith("Completed "))
        deposit_last = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li[3]/div[2]')
        self.assertEqual(deposit_last.text, "Deposit") 
        to_last = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[3]/div[3]')
        self.assertEqual(to_last.text,"To: 123ab45")
        money_last = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[3]/div[4]')
        self.assertEqual(money_last.text, "50.00 CZK")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/div[1]/button[1]').click()

        completed_first = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li[1]/div[1]')
        self.assertTrue(completed_first.text.startswith("Completed "))
        deposit_first = self.selenium.find_element(By.XPATH,'/html/body/div/div/div/ul/li[1]/div[2]')
        self.assertEqual(deposit_first.text, "Deposit") 
        to_first = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]/div[3]')
        self.assertEqual(to_first.text,"To: 123ab45")
        money_first = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]/div[4]')
        self.assertEqual(money_first.text, "100.00 CZK")



    @responses.activate
    def test_send_money_between_other_accounts_EUR_vs_CZK_json(self):
        rsp1 = responses.Response(
        method="GET",
        url="https://open.er-api.com/v6/latest/CZK", 
        json={
            "result": "success",
            "rates": {
                "CZK": 1,
                "EUR": 0.045
            }
        },
        status=200)
        responses.add(rsp1)
        user_alex = User.objects.create_superuser(username='Alex', password='lev?alex', email='alex@test.com', is_active=True)
        user_alex.save()
        Account.objects.create(owner=user_alex, account_type="regular", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        user_glorie = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user_glorie, account_type="regular", currency="CZK", balance = 950.00, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[4]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        self.selenium.find_element(By.XPATH,'/html/body/div/div/div/div/button[2]').click()
        select_your_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="account"]'))
        select_your_account.select_by_visible_text("regular (123ab45) - 950.00 CZK")
        target_account = self.selenium.find_element(By.XPATH, '//*[@id="targetAccount"]')
        target_account.send_keys("678cd9")
        account = self.selenium.find_element(By.XPATH, '//*[@id="amount"]')
        account.send_keys("100.00")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Money sent successfully!")
        alert.accept()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        acounts_gloria = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]')
        acounts_gloria = acounts_gloria.text.strip()
        self.assertEqual(acounts_gloria, 'regular (123ab45): 850.00 CZK')
        acounts_melman = Account.objects.get(account_number = "678cd9")
        self.assertEqual(acounts_melman.balance, 14.50)

    @responses.activate
    def test_send_money_between_other_accounts_EUR_vs_CZK_json(self):
        rsp1 = responses.Response(
        method="GET",
        url="https://open.er-api.com/v6/latest/EUR", 
        json={
            "result": "success",
            "rates": {
                "EUR": 1, 
                "USD":0.95,
            }
        },
        status=200)
        responses.add(rsp1)
        user_alex = User.objects.create_superuser(username='Alex', password='lev?alex', email='alex@test.com', is_active=True)
        user_alex.save()
        Account.objects.create(owner=user_alex, account_type="regular", currency="USD", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        ConversionTable.objects.create(base_currency = 'EUR', target_currency = 'USD', conversion_rate = 0.040,  updated_at=datetime(2001, 1, 1, 10, 0, 0)) 
        user_glorie = User.objects.get(username="Gloria")  
        Account.objects.create(owner=user_glorie, account_type="regular", currency="EUR", balance = 95.00, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        self.login()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[4]').click()
        wait = WebDriverWait(self.selenium, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/h2')))
        self.selenium.find_element(By.XPATH,'/html/body/div/div/div/div/button[2]').click()
        select_your_account = Select(self.selenium.find_element(By.XPATH, '//*[@id="account"]'))
        select_your_account.select_by_visible_text("regular (123ab45) - 95.00 EUR")
        target_account = self.selenium.find_element(By.XPATH, '//*[@id="targetAccount"]')
        target_account.send_keys("678cd9")
        account = self.selenium.find_element(By.XPATH, '//*[@id="amount"]')
        account.send_keys("15.55")
        self.selenium.find_element(By.XPATH, '/html/body/div/div/div/form/button').click()
        alert = WebDriverWait(self.selenium, 5).until(EC.alert_is_present())
        alert_text = alert.text
        self.assertEqual(alert_text, "Money sent successfully!")
        alert.accept()
        self.selenium.find_element(By.XPATH, '/html/body/div/div/button[1]').click()
        acounts_gloria = self.selenium.find_element(By.XPATH, '/html/body/div/div/div/ul/li[1]')
        acounts_gloria = acounts_gloria.text.strip()
        self.assertEqual(acounts_gloria, 'regular (123ab45): 79.45 EUR')
        acounts_melman = Account.objects.get(account_number = "678cd9")
        self.assertEqual(acounts_melman.balance, Decimal('24.77'))

class RestApiTest(unittest.TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="slon", password="slon3")

    def tearDown(self):
        # Vymažeme všechny záznamy z tabulek v databázi
        User.objects.all().delete()
        ConversionTable.objects.all().delete()
        Account.objects.all().delete()


    def get_auth_token(self, username="slon", password="slon3"):
        response = self.client.post(reverse('tasks_management:login'), data={
            "username": username,
            "password": password
        }, content_type="application/json")
        return response.json().get("token")

    def test_user_registration_success(self):
        data = {
            "username": "hroch",
            "password": "hroch123",
        }
        response = self.client.post(reverse('tasks_management:register'), data=data, content_type="application/json") 
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="hroch").exists())

    def test_login_success(self):
        data = {"username": "slon", "password": "slon3"}
        response = self.client.post(reverse('tasks_management:login'), data=data, content_type="application/json") 
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())
        
    def test_login_wrong_credentials(self):
        data = {"username": "slon", "password": "hroch"}
        response = self.client.post(reverse('tasks_management:login'), data=data, content_type="application/json") 
        response_json = response.json()
        self.assertEqual(response_json["error"], "Invalid credentials")
        self.assertEqual(response.status_code, 400)
    
    def test_user_exist(self):
        data = {
            "username": "slon",
            "password": "hroch123",
        }
        response = self.client.post(reverse('tasks_management:register'), data=data, content_type="application/json") 
        response_json = response.json()
        self.assertEqual(response_json["error"], "User already exists")
        self.assertEqual(response.status_code, 400)

    def test_get_accounts(self):
        Account.objects.create(owner=self.user, account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=self.user, account_type="regular", currency="CZK", balance = 950.00, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        response = self.client.get(reverse('pay:get_accounts'), HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        accounts = response_json.get('accounts')
        self.assertEqual(len(accounts),2)
        account_1 = accounts[0]
        self.assertEqual (account_1["account_number"], '678cd9')
        self.assertEqual (account_1["balance"], "10.00")
        self.assertEqual (account_1["currency"], "EUR")
        self.assertEqual (account_1["account_type"], "saving")
        account_2 = accounts[1]
        self.assertEqual (account_2["account_number"], '123ab45')
        self.assertEqual (account_2["balance"], "950.00")
        self.assertEqual (account_2["currency"], "CZK")
        self.assertEqual (account_2["account_type"], "regular")

    def test_get_no_accounts(self):
        token = self.get_auth_token()
        response = self.client.get(reverse('pay:get_accounts'), HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        accounts = response_json.get('accounts')
        self.assertEqual(len(accounts),0)

    def test_get_account_types(self):
        token = self.get_auth_token()
        response = self.client.get(reverse('pay:get_account_types'), HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        account_types = response_json.get('account_types')
        self.assertEqual(len(account_types),2)
        self.assertIn("regular", account_types)
        self.assertIn("savings", account_types)
    
    def test_post_account_types(self):
        token = self.get_auth_token()
        response = self.client.post(reverse('pay:get_account_types'), HTTP_AUTHORIZATION=f'Bearer {token}')
        response_json = response.json()
        self.assertEqual(response_json["message"], "Invalid request method")
        self.assertEqual(response.status_code, 400)

    def test_get_currencies(self):
        token = self.get_auth_token()
        response = self.client.get(reverse('pay:get_currencies'), HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        currencies = response_json.get('currencies')
        self.assertEqual(len(currencies),3)
        self.assertIn("USD", currencies)
        self.assertIn("EUR", currencies)
        self.assertIn("CZK", currencies)
    
    def test_post_currencies(self):
        token = self.get_auth_token()
        response = self.client.post(reverse('pay:get_currencies'), HTTP_AUTHORIZATION=f'Bearer {token}')
        response_json = response.json()
        self.assertEqual(response_json["message"], "Invalid request method")
        self.assertEqual(response.status_code, 400)

    def test_post_open_account(self):
        data = {
            "currency":"USD",
            "type":"regular"
        }
        token = self.get_auth_token()
        response = self.client.post(reverse('pay:open_account'), data=data, content_type="application/json", HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertEqual (response_json["message"], 'Account opened successfully')
        self.assertIn("account_number", response_json)
        # vytahnutí z debilni databeze !!! dulezité podle M - picovina nejvetěí !!!!
        account_nr = response_json["account_number"]
        account = Account.objects.get(account_number = account_nr)
        self.assertEqual(account.balance, 0)

    def test_get_open_account(self):
        data = {
            "currency":"USD",
            "type":"regular"
        }
        token = self.get_auth_token()
        response = self.client.get(reverse('pay:open_account'), data=data, content_type="application/json", HTTP_AUTHORIZATION=f'Bearer {token}')
        response_json = response.json()
        self.assertEqual(response_json["message"], "Invalid request method")
        self.assertEqual(response.status_code, 400)

    def test_post_open_account_not_in_SUPPORTED_ACCOUNT_TYPES(self):
        data = {
            "currency":"USD",
            "type":"financial"
        }
        token = self.get_auth_token()
        response = self.client.post(reverse('pay:open_account'), data=data, content_type="application/json", HTTP_AUTHORIZATION=f'Bearer {token}')
        response_json = response.json()
        self.assertEqual(response_json["message"], "Unsupported account type")
        self.assertEqual(response.status_code, 400)
    
    def test_post_open_account_not_in_SUPPORTED_CURRENCIES(self):
        data = {
            "currency":"DKK",
            "type":"savings"
        }
        token = self.get_auth_token()
        response = self.client.post(reverse('pay:open_account'), data=data, content_type="application/json", HTTP_AUTHORIZATION=f'Bearer {token}')
        response_json = response.json()
        self.assertEqual(response_json["message"], "Unsupported currency")
        self.assertEqual(response.status_code, 400)

    def test_post_open_account_not_account_type(self):
        data = {
            "currency":"EUR",
            "type":" "
        }
        token = self.get_auth_token()
        response = self.client.post(reverse('pay:open_account'), data=data, content_type="application/json", HTTP_AUTHORIZATION=f'Bearer {token}')
        response_json = response.json()
        self.assertEqual(response_json["message"], "Invalid data")
        self.assertEqual(response.status_code, 400)
    
    def test_post_open_account_not_account_type(self):
        data = {
            "currency":" ",
            "type":"savings"
        }
        token = self.get_auth_token()
        response = self.client.post(reverse('pay:open_account'), data=data, content_type="application/json", HTTP_AUTHORIZATION=f'Bearer {token}')
        response_json = response.json()
        self.assertEqual(response_json["message"], "Invalid data")
        self.assertEqual(response.status_code, 400)
    
    def test_post_deposit(self):
        Account.objects.create(owner=self.user, account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        # URL pro deposit, musí odpovídat tvému urls.py
        url = reverse('pay:deposit', kwargs={'account_number': '678cd9'})
        # Data, která chceme poslat (částka vkladu)
        data = {'amount': '50.00'}
        # POST request s JSON tělem a autorizací
        response = self.client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        # Ověříme, že status je 200 OK
        self.assertEqual(response.status_code, 200)
        # Parsujeme JSON odpověď
        response_json = response.json()
        # Ověříme, že odpověď obsahuje očekávanou zprávu
        self.assertEqual(response_json.get('message'), 'Deposit successful')
        # Ověříme, že nový zůstatek je správný (10 + 50 = 60)
        self.assertEqual(response_json.get('new_balance'), '60.00')
        account = Account.objects.get(account_number = '678cd9')
        self.assertEqual(account.balance, 60)

        

    def test_post_deposit_invalid_amount(self):
        Account.objects.create(owner=self.user, account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        url = reverse('pay:deposit', kwargs={'account_number': '678cd9'})
        data = {'amount': '-20.00'}
        response = self.client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json.get('message'), "Invalid amount. Must be greater than 0.")
    
    def test_post_deposit_invalid_amount_format(self):
        Account.objects.create(owner=self.user, account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        url = reverse('pay:deposit', kwargs={'account_number': '678cd9'})
        data = {'amount': 'ab5.00'}
        response = self.client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json.get('message'), "Invalid amount format. Must be a valid decimal number.")

    def test_post_deposit_invalid_request_method(self):
        Account.objects.create(owner=self.user,   account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        url = reverse('pay:deposit', kwargs={'account_number': '678cd9'})
        data = {'amount': 'ab5.00'}
        response = self.client.delete(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json.get('message'), "Invalid request method")
    
    def test_post_deposit_account_not_found(self):
        Account.objects.create(owner=self.user,   account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        url = reverse('pay:deposit', kwargs={'account_number': '12856'})
        data = {'amount': '5.00'}
        response = self.client.delete(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json.get('message'), "Invalid request method")

    def test_post_transfer_invalid_amount_Must_be_greater_than_0(self):
        Account.objects.create(owner=self.user, account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=self.user, account_type="regular", currency="CZK", balance = 950.00, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        # URL pro deposit, musí odpovídat tvému urls.py
        url = reverse('pay:transfer', kwargs={'account_number': '678cd9'})
        data = {'amount': '-5', 
                'target_account': '123ab45'}
        response = self.client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json.get('message'), "Invalid amount. Must be greater than 0.")

    def test_post_transfer_invalid_amount_format(self):   
        Account.objects.create(owner=self.user, account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=self.user, account_type="regular", currency="CZK", balance = 950.00, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        # URL pro deposit, musí odpovídat tvému urls.py
        url = reverse('pay:transfer', kwargs={'account_number': '678cd9'})
        data = {'amount': 'ab5.00', 
                'target_account': '123ab45'}
        response = self.client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json.get('message'), "Invalid amount format. Must be a valid decimal number.")

    def test_post_transfer_cannot_transfer_to_the_same_account(self):
        Account.objects.create(owner=self.user, account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        # URL pro deposit, musí odpovídat tvému urls.py
        url = reverse('pay:transfer', kwargs={'account_number': '678cd9'})
        data = {'amount': '5', 
                'target_account': '678cd9'}
        response = self.client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json.get('message'), "Cannot transfer to the same account")
    
    def test_post_transfer_insufficient_funds(self):   
        Account.objects.create(owner=self.user, account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=self.user, account_type="regular", currency="CZK", balance = 950.00, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        # URL pro deposit, musí odpovídat tvému urls.py
        url = reverse('pay:transfer', kwargs={'account_number': '678cd9'})
        data = {'amount': '15', 
                'target_account': '123ab45'}
        response = self.client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json.get('message'), "Insufficient funds")
    
    def test_post_transfer_successful(self): 
        Account.objects.create(owner=self.user, account_type="saving", currency="CZK", balance = 1000.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=self.user, account_type="regular", currency="CZK", balance = 950.00, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        url = reverse('pay:transfer', kwargs={'account_number': '678cd9'})
        data = {'amount': '500.00', 
                'target_account': '123ab45'}
        response = self.client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        # Ověříme, že odpověď obsahuje očekávanou zprávu
        self.assertEqual(response_json.get('message'), 'Transfer successful')
        # vytahnutí z databáze
        account = Account.objects.get(account_number = '123ab45')
        self.assertEqual(account.balance, 1450.00)
        account = Account.objects.get(account_number = '678cd9')
        self.assertEqual(account.balance, 500.00)
    
    def test_post_transfer_successful_different_currency(self): 
        Account.objects.create(owner=self.user, account_type="saving", currency="EUR", balance = 10.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=self.user, account_type="regular", currency="CZK", balance = 8.50, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        ConversionTable.objects.create(
             base_currency = 'EUR', target_currency = 'CZK', conversion_rate = 25.25)
        token = self.get_auth_token()
        url = reverse('pay:transfer', kwargs={'account_number': '678cd9'})
        data = {'amount': '2.50', 
                'target_account': '123ab45'}
        response = self.client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        # Ověříme, že odpověď obsahuje očekávanou zprávu
        self.assertEqual(response_json.get('message'), 'Transfer successful')
        # vytahnutí z databáze
        account = Account.objects.get(account_number = '123ab45')
        self.assertEqual(account.balance, Decimal('71.63'))
        account = Account.objects.get(account_number = '678cd9')
        self.assertEqual(account.balance, 7.50)

    def test_post_account_not_found(self): 
        Account.objects.create(owner=self.user, account_type="saving", currency="CZK", balance = 1000.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=self.user, account_type="regular", currency="CZK", balance = 950.00, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        url = reverse('pay:transfer', kwargs={'account_number': '678cd9'})
        data = {'amount': '500.00', 
                'target_account': '123ab45ww'}
        response = self.client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 404)
        response_json = response.json()
        # Ověříme, že odpověď obsahuje očekávanou zprávu
        self.assertEqual(response_json.get('message'), 'Account not found')

    def test_post_invalid_request_method_transfer(self): 
        Account.objects.create(owner=self.user, account_type="saving", currency="CZK", balance = 1000.00, account_number = "678cd9", created_at=datetime(2023, 1, 1, 10, 0, 0))
        Account.objects.create(owner=self.user, account_type="regular", currency="CZK", balance = 950.00, account_number = "123ab45", created_at=datetime(2023, 1, 1, 10, 0, 0))
        token = self.get_auth_token()
        url = reverse('pay:transfer', kwargs={'account_number': '678cd9'})
        data = {'amount': '500.00', 
                'target_account': '123ab45'}
        response = self.client.delete(
        url,
        data=json.dumps(data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        # Ověříme, že odpověď obsahuje očekávanou zprávu
        self.assertEqual(response_json.get('message'), 'Invalid request method')
        
        


            


        
        

            




        


        






        
        
            