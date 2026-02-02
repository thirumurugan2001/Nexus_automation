import time
from playwright.sync_api import sync_playwright
import os

def Request_PO_Amendment(data):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()        
        email = os.getenv("ERP_EMAIL", "bharathielectricalanna@gmail.com")
        password = os.getenv("ERP_PASSWORD", "Nexus.Jan@2026")      
        try:
            page.goto("https://induserp.industowers.com/OA_HTML/AppsLocalLogin.jsp")
            page.wait_for_timeout(3000)            
            page.fill('input[name="usernameField"]', email)
            page.fill('input[name="passwordField"]', password)
            page.press('input[name="passwordField"]', 'Enter')            
            page.wait_for_timeout(5000)
            page.wait_for_selector("img[title='Expand']", timeout=10000)
            page.click("img[title='Expand']")            
            page.wait_for_selector("li >> text=Home Page", timeout=15000)
            page.click("li >> text=Home Page")            
            page.wait_for_selector("a:has-text('Orders')", timeout=15000)
            page.click("a:has-text('Orders')")  
            page.wait_for_selector("a[title='Purchase Orders']", timeout=15000)
            page.click("a[title='Purchase Orders']")  
            page.wait_for_selector("button:has-text('Advanced Search')", timeout=10000)
            page.click("button:has-text('Advanced Search')")            
            page.wait_for_selector("input#Value_0", timeout=10000)
            page.fill("input#Value_0", data["PO_Number"])
            page.wait_for_selector("button#customizeSubmitButton", timeout=10000)
            page.click("button#customizeSubmitButton")
            page.click("a[id^='N93:PosPoNumber:']")
            page.click("button:text('Request PO Amendment')")
            time.sleep(20)
            browser.close()
        except Exception as e:
            print(f"Error during login: {e}")
            browser.close()
            raise Exception("Failed to process PO Amendment request")

if __name__ == "__main__":
    data = {
        "PO_Number": "23030561912",
        "File_Url": "https://3f9a4e5dd7b6b0998a280c44401343a5.cdn.bubble.io/f1742198933168x784106798636753400/Signed_File.pdf",
        "Change_Item": [
            {
                "PO_Line_No": "1",
                "Item_Code":"29-400000-0-00-ZZ-ZZ-886",
                "New_Quantity": "10"
            },
            {
                "PO_Line_No": "2",
                "Item_Code":"22-212660-0-03-ZZ-ZZ-000",
                "New_Quantity": "10"
            },
        ],
        "Added_Items": [
            {
                "Item_Description": "Widget A",
                "Quantity": "5",
                "Price": "500"
            }
        ]
    }
    result = Request_PO_Amendment(data)
