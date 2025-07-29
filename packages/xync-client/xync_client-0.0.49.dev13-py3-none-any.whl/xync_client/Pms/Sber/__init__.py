import asyncio
import os
from playwright.async_api import async_playwright
from playwright._impl._errors import TimeoutError
import re
from x_model import init_db
from xync_schema import models
from xync_client.loader import PG_DSN


async def input_(page, selectot: str, code: str)->None:
    await page.wait_for_selector(selectot, timeout=10000)
    page.locator('[class="BjsSl7Uv2es5tUtwB03r"]')
    for i in range(5):
        await page.keyboard.press(code[i])
    await page.wait_for_timeout(1000)

async def fiveDigitCode(page, agent):
    sms_code = input("Введите код из SMS: ")
    for i in range(5):
        await page.locator(f'input[name="confirmPassword-{i}"]').fill(sms_code[i])

    passcode = input("Введите 5-значный код: ")
    await input_(page, '.FWAhBZHPePsATLTVFeTT', passcode)
    await input_(page, '.Re_Wg4Drqw9QjVM43vJ_', passcode)
    agent.auth["pass"] = passcode
    await agent.save()

async def login_cart(page, number_cart:str, agent)->None:
        await page.locator('button[aria-controls="tabpanel-card"]').click()
        await page.wait_for_selector('input[placeholder="Введите номер карты"]', timeout=10000)
        await page.locator('input[placeholder="Введите номер карты"]').fill(number_cart)
        await page.locator('button[type="submit"]').click()
        await fiveDigitCode(page, agent)

async def login_and_password(page, login:str, password:str, agent)->None:
    await page.locator('input[autocomplete="login"]').fill(login)
    await page.locator('input[autocomplete="password"]').fill(password)
    await page.locator('button[data-testid="button-continue"]').click()
    await fiveDigitCode(page, agent)

async def logged(page, passcode: str)->None:
    await page.wait_for_selector('.UFWVuux_h6LdkrisQYCk', timeout=10000)
    page.locator('.WpYaKiJknodWYw32MZd9')
    for i in range(5):
        await page.keyboard.press(passcode[i])
    await page.wait_for_timeout(10000)

async def sendCredCard(
        page,
        amount: int,
        payment: str,
        cred: str
    )->None:

    await page.locator('a#nav-link-payments').click()
    await page.locator('.sxZoARZF').click()
    await page.locator('input#text-field-1').fill(cred)
    await page.locator('.tMUGN6jK').click()
    if len(cred) < 15:
        await page.click('button[title="В другой банк по СБП"]')
        await page.fill('input[name="sbptransfer\\:init\\:targetBank"]', payment)
        # await page.wait_for_selector('#sbptransfer\\:init\\:targetBank-option-100000000004', state="visible")
        await page.locator('#sbptransfer\\:init\\:targetBank-option-100000000004').click()
        # await page.wait_for_selector('.Fv3KdbZw', state="visible")
        # await page.locator('.Fv3KdbZw').click()
        await page.wait_for_selector("#sbptransfer\\:init\\:summ", state="visible")
        await page.fill("#sbptransfer\\:init\\:summ", str(amount))
        await page.click('.transfers-fps-17yzyu7 e5hllya1')
        sms_code = input("Введите код из SMS: ")
        await page.fill('input[autocomplete="one-time-code"]', sms_code)
        await page.click('.transfers-fps-17yzyu7 e5hllya1')

    else:
        await page.wait_for_selector('#p2ptransfer\\:xbcard\\:amount', state="visible")
        await page.fill('#p2ptransfer\\:xbcard\\:amount', str(amount))
        await page.wait_for_selector('button.bjm6hnlx', state="visible")
        await page.wait_for_timeout(1000)
        await page.click('button:has-text("Продолжить")')
        await page.click('button.bjm6hnlx')
        await page.click('button.bjm6hnlx')
        sms_code = input("Введите код из SMS: ")
        await page.fill('input.MH9z5OYE', sms_code)
        await page.click('button.bjm6hnlx')


async def last_transaction(page, amounts: int, transactions: str)->bool:
    transaction = await page.locator('.JsCdEfJ6').all_text_contents()
    amount = await page.locator('.ibtVVZxM.APTNeSaT').all_text_contents()
    cleaned_amount = int(re.sub(r"[^\d]", "", amount[0]))
    amount_ = cleaned_amount == amounts
    transaction_ = transaction[0].strip().upper() == transactions.strip().upper()
    return amount_ and transaction_

async def check_last_transaction(result: bool):
    if result:
        print("Платеж получен")
    else:
        print("Не получен")


async def main():

    _ = await init_db(PG_DSN, models, True)
    agent = await models.PmAgent.filter(pm__norm="sber", auth__isnull=False).first()

    storage_state = "state.json" if os.path.exists("state.json") else None
    url = "https://online.sberbank.ru/CSAFront/index.do"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=storage_state, record_video_dir="videos")
        page = await context.new_page()
        await page.goto(url)
        try:
            await page.wait_for_url(f"{url}#/", timeout=3000)
        except TimeoutError:
            if card := agent.auth.get("card"):
                if await page.locator('button[aria-controls="tabpanel-card"]').is_visible():
                    await login_cart(page, card, agent)
                else:
                    await logged(page, agent.auth.get("pass"))
                    result = await last_transaction(page, 20, "твой нейм")
                    await check_last_transaction(result)
                    await sendCredCard(page, 10, "Т-Банк", "2202 2062 7529 5967")
                    await page.wait_for_timeout(10000)

            elif login := agent.auth.get("login"):
                if await page.locator('button[aria-controls="tabpanel-login"]').is_visible():
                    await login_and_password(page, login, agent.auth.get("password"), agent)
                else:
                    await logged(page, agent.auth.get("pass"))
                    result = await last_transaction(page, 20, "твой нейм")
                    await check_last_transaction(result)
                    await sendCredCard(page, 10, "Т-Банк", "9308185958")
                    await page.wait_for_timeout(10000)


            await context.storage_state(path="state.json")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
