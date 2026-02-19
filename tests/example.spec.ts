import { test, expect, Page } from '@playwright/test';
import sqlite3 from 'sqlite3';


test.beforeEach(async () => {
  await create_user('Emma', 'elephant')
//   const response = await fetch('http://127.0.0.1:8000/tasks/api/register', {
//   method: 'POST',
//   headers: {
//     'Content-Type': 'application/json',
//   },
//   body: JSON.stringify({
//     username: 'Emma',
//     password: 'elephant',
//   }),
// });
});

test.afterEach(async () => {
  // 🔹 připojení k SQLite DB
  const db = new sqlite3.Database('db.sqlite3'); // cesta k tvé Django DB

  // 🔹 spuštění SQL dotazů
  db.run('delete FROM tasks_management_user where username = "test_melman"');
  db.run('delete FROM tasks_management_user where username = "Emma"');
  db.run('delete from pay_account');
  db.run('delete from pay_conversiontable');

  // 🔹 zavření DB
  db.close();
});

export async function login(
  page: Page,
  username: string = 'Emma',
  password: string = 'elephant'
): Promise<void> { 
  await page.goto('http://127.0.0.1:8000/pay/ui');

  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.locator('xpath=/html/body/div/div/div/form/button').click();
  await expect(page.locator('xpath=/html/body/div/div/h1')).toBeVisible();
  

  // // Playwright automaticky čeká
  // await page.waitForURL('**/dashboard');
}


export async function account_create(
  account_type: string, 
  currency: string, 
  account_number: string, 
  balance: number, 
  updated_at: string, 
  username: string,
  created_at: string

){
  const db = new sqlite3.Database('db.sqlite3');
  db.run(`INSERT INTO pay_account (owner_id, account_type, currency, balance, account_number, updated_at, created_at)VALUES ((select id from tasks_management_user where username='${username}'), '${account_type}', '${currency}', ${balance}, '${account_number}', '${updated_at}', '${created_at}')`);
  db.close();
}

export async function create_user(username: string, password: string) {
  const response = await fetch('http://127.0.0.1:8000/tasks/api/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  // if (!response.ok) {
  //   throw new Error(`User creation failed: ${response.status}`);
  // }
}

export async function conversion_rate_create (
  base_currency: string, 
  target_currency: string, 
  conversion_rate: number, 
  updated_at: string

){
  const db = new sqlite3.Database('db.sqlite3');
  db.run(`INSERT INTO pay_conversiontable (base_currency, target_currency, conversion_rate, updated_at) Values ('${base_currency}', '${target_currency}', '${conversion_rate}', '${updated_at}')`);
  db.close();
}


test('User registration and login flow', async ({ page }) => {
  // 🟢 1️⃣ Otevření stránky
  await page.goto('http://127.0.0.1:8000/pay/ui');

  // 🟢 2️⃣ Kliknutí na tlačítko "Register"
  await page.locator('xpath=/html/body/div/div/button[2]').click();

  // 🟢 3️⃣ Ověření, že se objeví registrační formulář
  const title = await page.locator('xpath=/html/body/div/div/div/h2');
  await expect(title).toHaveText('Register');

  // 🟢 4️⃣ Vyplnění formuláře
  const username = 'test_melman'; // unikátní jméno
  await page.locator('#username').fill(username);
  await page.locator('#password').fill('mymelman');

  // 🟢 5️⃣ Zachycení alertu a otestování hlášky
  const dialogPromise = page.waitForEvent('dialog');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();
  const dialog = await dialogPromise;
  expect(dialog.message()).toBe('Registration successful! You can now log in.');
  await dialog.accept();

  // 🟢 6️⃣ Přechod na login tlačítkem
  await page.locator('xpath=/html/body/div/div/button[1]').click();

  // 🟢 7️⃣ Přihlášení
  await page.locator('#username').fill(username);
  await page.locator('#password').fill('mymelman');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  // 🟢 8️⃣ Ověření přihlášení
  const welcomeTitle = await page.locator('xpath=/html/body/div/div/h1');
  await expect(welcomeTitle).toHaveText(`Welcome ${username}!`);
});

test('User login flow', async ({ page }) => {
  await page.goto('http://127.0.0.1:8000/pay/ui');
  // .locator = .find_element
  // .fill = .send_keys
  // .goto = .get
  //  expect = self.assertEqual
  await page.locator('#username').fill('Melman');
  await page.locator('#password').fill('mymelman');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();
  const welcomeTitle = await page.locator('xpath=/html/body/div/div/h1');
  await expect(welcomeTitle).toHaveText(`Welcome Melman!`);
});


test('Creation account saving CZK flow', async ({ page }) => {
  await login(page);
  await page.locator('xpath=/html/body/div/div/button[2]').click();
  const openAcountTitle = await page.locator('xpath=/html/body/div/div/div/h2');
  await expect(openAcountTitle).toHaveText(`Open Account`);
  await page.selectOption('#currency', { label: 'CZK' });
  await page.selectOption('xpath=//*[@id="type"]', {label: 'savings'});
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const dialog = await page.waitForEvent('dialog');
  expect(dialog.message()).toBe('Account opened successfully!');
  await dialog.accept();

  await page.locator('xpath=/html/body/div/div/button[1]').click();
  const account = await page.locator('xpath=/html/body/div/div/div/ul/li');
  await expect(account).toContainText(/^savings \(/);
  await expect(account).toContainText(/: 0\.00 CZK$/);  
});


test('Creation account regular EUR flow', async ({ page }) => {
  await login(page);
  await page.locator('xpath=/html/body/div/div/button[2]').click();
  const openAcountTitle = await page.locator('xpath=/html/body/div/div/div/h2');
  await expect(openAcountTitle).toHaveText(`Open Account`);
  await page.selectOption('#currency', { label: 'EUR' });
  await page.selectOption('xpath=//*[@id="type"]', {label: 'regular'});
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const dialog = await page.waitForEvent('dialog');
  expect(dialog.message()).toBe('Account opened successfully!');
  await dialog.accept();

  await page.locator('xpath=/html/body/div/div/button[1]').click();
  const account = await page.locator('xpath=/html/body/div/div/div/ul/li');
  await expect(account).toContainText(/^regular \(/);
  await expect(account).toContainText(/: 0\.00 EUR$/);
  });

test('Add money CZK flow', async ({ page }) => {
  await account_create ('savings', 'CZK', '123ab45', 0, '2025-02-01', 'Emma', '2026-02-01');
  await login(page);
  await page.locator('xpath=/html/body/div/div/button[3]').click();
  await page.selectOption('xpath=//*[@id="account"]', {label: 'savings (123ab45) - 0.00 CZK'});
  await page.fill('xpath=//*[@id="amount"]', '100');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const dialog = await page.waitForEvent('dialog');
  expect(dialog.message()).toBe('Money added successfully!');
  await dialog.accept();

  await page.locator('xpath=/html/body/div/div/button[1]').click();
  const newAccount = await page.locator('xpath=/html/body/div/div/div/ul/li');
  await expect(newAccount).toHaveText(`savings (123ab45): 100.00 CZK`);
 });


  test('Add negative amount validation', async ({ page }) => {
  await account_create ('savings', 'CZK', '123ab45', 0, '2025-02-01', 'Emma', '2026-02-01')
  await login(page);
  await page.locator('xpath=/html/body/div/div/button[3]').click();
  await page.selectOption('xpath=//*[@id="account"]', {label: 'savings (123ab45) - 0.00 CZK'})
  await page.fill('#amount', '-15');
  await page.click('form button');

  const isValid = await page.locator('#amount').evaluate(
    (el: HTMLInputElement) => el.checkValidity()
  );

  expect(isValid).toBe(false);

  await expect(page.locator('h2')).toHaveText('Add Money');

  await page.fill('xpath=//*[@id="amount"]', '100');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const dialog = await page.waitForEvent('dialog');
  expect(dialog.message()).toBe('Money added successfully!');
  await dialog.accept();

  await page.locator('xpath=/html/body/div/div/button[1]').click();
  const newAccount = await page.locator('xpath=/html/body/div/div/div/ul/li');
  await expect(newAccount).toHaveText(`savings (123ab45): 100.00 CZK`);
 });


test('Send money beetween my acounts flow', async ({ page }) => {
  await account_create('savings', 'CZK', '123ab45', 2599.25, '2025-02-01', 'Emma', '2026-02-01');
  await account_create ('regular', 'CZK', 'bbbaa01', 4500.56, '2024-02-01', 'Emma', '2024-02-01');
  await login(page);
  await page.locator('xpath=/html/body/div/div/button[4]').click();
  await page.locator('xpath=/html/body/div/div/div/div/button[1]').click();
  await page.selectOption('xpath=//*[@id="account"]', {label: 'regular (bbbaa01) - 4500.56 CZK'});
  await page.selectOption('xpath=//*[@id="targetAccount"]', {label: 'savings (123ab45) - 2599.25 CZK'});
  await page.fill('xpath=//*[@id="amount"]', '2999.50');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const dialog = await page.waitForEvent('dialog');
  expect(dialog.message()).toBe('Money sent successfully!');
  await dialog.accept();

  await page.locator('xpath=/html/body/div/div/button[1]').click();
  const newAccount_savings = await page.locator('xpath=/html/body/div/div/div/ul/li[1]');
  await expect(newAccount_savings).toHaveText(`savings (123ab45): 5598.75 CZK`);

  const newAccount_regular = await page.locator('xpath=/html/body/div/div/div/ul/li[2]');
  await expect(newAccount_regular).toHaveText(`regular (bbbaa01): 1501.06 CZK`);
 });
 
  //TEST - POSLAT PENÍZE ZE SVEHO UCTU NA SVUJ STEJNÝ UCET OTESTOVAT HLASKU 

  test('Send money beetween my same acounts flow', async ({ page }) => {
  await account_create('savings', 'CZK', '123ab45', 2599.25, '2025-02-01', 'Emma', '2026-02-01');
  await account_create ('regular', 'CZK', 'bbbaa01', 4500.56, '2024-02-01', 'Emma', '2024-02-01');
  await login(page);
  await page.locator('xpath=/html/body/div/div/button[4]').click();
  await page.locator('xpath=/html/body/div/div/div/div/button[1]').click();
  await page.selectOption('xpath=//*[@id="account"]', {label: 'regular (bbbaa01) - 4500.56 CZK'});
  await page.selectOption('xpath=//*[@id="targetAccount"]', {label: 'regular (bbbaa01) - 4500.56 CZK'});
  await page.fill('xpath=//*[@id="amount"]', '2999.50');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const dialog = await page.waitForEvent('dialog');
  expect(dialog.message()).toBe('Failed to send money. Please try again.');
  await dialog.accept();
 });


  test('Send money beetween my acounts EUR vs CZK flow', async ({ page }) => {
  await account_create('savings', 'EUR', '123ab45', 259.25, '2025-02-01', 'Emma', '2026-02-01');
  await account_create ('regular', 'CZK', 'bbbaa01', 4500.00, '2024-02-01', 'Emma', '2024-02-01');
  const today = new Date().toISOString().slice(0, 10);
  await conversion_rate_create('EUR', 'CZK', 25.54, today);
  await login(page);

  await page.locator('xpath=/html/body/div/div/button[4]').click();
  await page.locator('xpath=/html/body/div/div/div/div/button[1]').click();
  await page.selectOption('xpath=//*[@id="account"]', {label: 'savings (123ab45) - 259.25 EUR'});
  await page.selectOption('xpath=//*[@id="targetAccount"]', {label: 'regular (bbbaa01) - 4500.00 CZK'});
  await page.fill('xpath=//*[@id="amount"]', '50.50');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const dialog = await page.waitForEvent('dialog');
  expect(dialog.message()).toBe('Money sent successfully!');
  await dialog.accept();

  await page.locator('xpath=/html/body/div/div/button[1]').click();
  const newAccount_savings = await page.locator('xpath=/html/body/div/div/div/ul/li[1]');
  await expect(newAccount_savings).toHaveText(`savings (123ab45): 208.75 EUR`);

  const newAccount_regular = await page.locator('xpath=/html/body/div/div/div/ul/li[2]');
  await expect(newAccount_regular).toHaveText(`regular (bbbaa01): 5789.77 CZK`);  
 });

test('send money beetween other acounts CZK vs CZK flow', async ({ page }) => {
  await create_user ('Laura', 'PinkPig22')
  await account_create('savings', 'CZK', '123ab45', 2599.25, '2025-02-01', 'Laura', '2026-02-01');

  await account_create ('regular', 'CZK', 'bbbaa01', 4500.56, '2024-02-01', 'Emma', '2024-02-01');
  await login(page);
  await page.locator('xpath=/html/body/div/div/button[4]').click();
  await page.locator('xpath=/html/body/div/div/div/div/button[2]').click();

  await page.selectOption('xpath=//*[@id="account"]', {label: 'regular (bbbaa01) - 4500.56 CZK'});
  await page.fill('xpath=//*[@id="targetAccount"]', '123ab45');
  await page.fill('xpath=//*[@id="amount"]', '3500.45');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const dialog = await page.waitForEvent('dialog');
  expect(dialog.message()).toBe('Money sent successfully!');
  await dialog.accept();

  await page.locator('xpath=/html/body/div/div/button[1]').click();
  const newAccount_regular = await page.locator('xpath=/html/body/div/div/div/ul/li[1]');
  await expect(newAccount_regular).toHaveText(`regular (bbbaa01): 1000.11 CZK`);
  await page.locator('xpath=/html/body/div/div/button[6]').click();

  await login (page, 'Laura', 'PinkPig22');
  const Laura_Account = await page.locator('xpath=/html/body/div/div/div/ul/li');
  await expect(Laura_Account).toHaveText(`savings (123ab45): 6099.70 CZK`)
 });


 test('send money beetween other acounts EUR vs USD flow', async ({ page }) => {
  await create_user ('Peter', 'HippoBlue7')
  await account_create('savings', 'EUR', 'xxvv55', 4856.78, '2025-02-01', 'Peter', '2026-02-01');

  await account_create ('regular', 'USD', 'ww99op', 6595.45, '2024-02-01', 'Emma', '2024-02-01');
  const today = new Date().toISOString().slice(0, 10);
  await conversion_rate_create('USD', 'EUR', 0.84, today);
  await login(page);
  await page.locator('xpath=/html/body/div/div/button[4]').click();
  await page.locator('xpath=/html/body/div/div/div/div/button[2]').click();

  await page.selectOption('xpath=//*[@id="account"]', {label: 'regular (ww99op) - 6595.45 USD'});
  await page.fill('xpath=//*[@id="targetAccount"]', 'xxvv55');
  await page.fill('xpath=//*[@id="amount"]', '146.68');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const dialog = await page.waitForEvent('dialog');
  expect(dialog.message()).toBe('Money sent successfully!');
  await dialog.accept();

  await page.locator('xpath=/html/body/div/div/button[1]').click();
  const newAccount_regular = await page.locator('xpath=/html/body/div/div/div/ul/li[1]');
  await expect(newAccount_regular).toHaveText(`regular (ww99op): 6448.77 USD`);
  await page.locator('xpath=/html/body/div/div/button[6]').click();

  await login (page, 'Peter', 'HippoBlue7');
  const Laura_Account = await page.locator('xpath=/html/body/div/div/div/ul/li');
  await expect(Laura_Account).toHaveText(`savings (xxvv55): 4979.99 EUR`)

});

  test('send money beetween other acounts EUR vs USD more money flow', async ({ page }) => {
  await create_user ('Peter', 'HippoBlue7')
  await account_create('savings', 'EUR', 'xxvv55', 86.78, '2025-02-01', 'Peter', '2026-02-01');

  await account_create ('regular', 'USD', 'ww99op', 65.45, '2024-02-01', 'Emma', '2024-02-01');
  const today = new Date().toISOString().slice(0, 10);
  await conversion_rate_create('USD', 'EUR', 0.84, today);
  await login(page);
  await page.locator('xpath=/html/body/div/div/button[4]').click();
  await page.locator('xpath=/html/body/div/div/div/div/button[2]').click();

  await page.selectOption('xpath=//*[@id="account"]', {label: 'regular (ww99op) - 65.45 USD'});
  await page.fill('xpath=//*[@id="targetAccount"]', 'xxvv55');
  await page.fill('xpath=//*[@id="amount"]', '100.00');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const failed_dialog = await page.waitForEvent('dialog');
  expect(failed_dialog.message()).toBe('Failed to send money. Please try again.');
  await failed_dialog.accept();

  await page.fill('xpath=//*[@id="amount"]', '60.00');
  await page.locator('xpath=/html/body/div/div/div/form/button').click();

  const ok_dialog = await page.waitForEvent('dialog');
  expect(ok_dialog.message()).toBe('Money sent successfully!');
  await ok_dialog.accept();

  await page.locator('xpath=/html/body/div/div/button[1]').click();
  const newAccount_regular = await page.locator('xpath=/html/body/div/div/div/ul/li[1]');
  await expect(newAccount_regular).toHaveText(`regular (ww99op): 5.45 USD`);
  await page.locator('xpath=/html/body/div/div/button[6]').click();

  await login (page, 'Peter', 'HippoBlue7');
  const Laura_Account = await page.locator('xpath=/html/body/div/div/div/ul/li');
  await expect(Laura_Account).toHaveText(`savings (xxvv55): 137.18 EUR`)
});

