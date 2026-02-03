import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os

def Request_PO_Amendment(data):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.set_default_timeout(60000)        
        email = os.getenv("ERP_EMAIL", "bharathielectricalanna@gmail.com")
        password = os.getenv("ERP_PASSWORD", "Nexus.Jan@2026")
        try:
            print("Navigating to login page...")
            page.goto("https://induserp.industowers.com/OA_HTML/AppsLocalLogin.jsp")
            page.wait_for_timeout(5000)            
            print("Filling login credentials...")
            page.fill('input[name="usernameField"]', email)
            page.fill('input[name="passwordField"]', password)
            page.press('input[name="passwordField"]', 'Enter')            
            print("Waiting for login to complete...")
            page.wait_for_timeout(8000)            
            try:
                page.wait_for_selector("img[title='Expand']", timeout=15000)
                print("Login successful, clicking Expand...")
                page.click("img[title='Expand']")
            except PlaywrightTimeoutError:
                print("Warning: Expand button not found, continuing anyway...")            
            print("Navigating to Home Page...")
            try:
                page.wait_for_selector("li >> text=Home Page", timeout=15000)
                page.click("li >> text=Home Page")
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                print("Warning: Home Page menu not found, trying alternative navigation...")            
            print("Navigating to Orders...")
            try:
                page.wait_for_selector("a:has-text('Orders')", timeout=15000)
                page.click("a:has-text('Orders')")
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                print("Error: Orders menu not found")
                raise            
            print("Clicking Purchase Orders...")
            try:
                page.wait_for_selector("a[title='Purchase Orders']", timeout=15000)
                page.click("a[title='Purchase Orders']")
                page.wait_for_timeout(5000)
            except PlaywrightTimeoutError:
                print("Error: Purchase Orders link not found")
                raise            
            print("Clicking Advanced Search...")
            try:
                page.wait_for_selector("button:has-text('Advanced Search')", timeout=15000)
                page.click("button:has-text('Advanced Search')")
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                print("Error: Advanced Search button not found")
                raise            
            print(f"Searching for PO Number: {data['PO_Number']}")
            try:
                page.wait_for_selector("input#Value_0", timeout=15000)
                page.fill("input#Value_0", data["PO_Number"])
                page.wait_for_timeout(1000)
            except PlaywrightTimeoutError:
                print("Error: Search input field not found")
                raise            
            print("Clicking Submit button...")
            try:
                page.wait_for_selector("button#customizeSubmitButton", timeout=15000)
                page.click("button#customizeSubmitButton")
                page.wait_for_timeout(8000)
            except PlaywrightTimeoutError:
                print("Error: Submit button not found")
                raise            
            print("Looking for PO number link...")
            po_selectors = [f"a:has-text('{data['PO_Number']}')","a[id^='N93:PosPoNumber:']",f"a:contains('{data['PO_Number']}')","table a",]
            po_link_found = False
            for selector in po_selectors:
                try:
                    page.wait_for_selector(selector, timeout=10000)
                    page.click(selector)
                    print(f"Clicked PO link using selector: {selector}")
                    po_link_found = True
                    break
                except PlaywrightTimeoutError:
                    continue            
            if not po_link_found:
                page.screenshot(path="debug_search_results.png")
                print("Screenshot saved as debug_search_results.png")
                raise Exception(f"PO Number link for {data['PO_Number']} not found")            
            print("Clicking Request PO Amendment...")
            page.wait_for_timeout(3000)            
            amendment_selectors = ["button:text('Request PO Amendment')","button:has-text('Request PO Amendment')","input[value='Request PO Amendment']",]            
            amendment_found = False
            for selector in amendment_selectors:
                try:
                    page.wait_for_selector(selector, timeout=10000)
                    page.click(selector)
                    print(f"Clicked Request PO Amendment using selector: {selector}")
                    amendment_found = True
                    break
                except PlaywrightTimeoutError:
                    continue            
            if not amendment_found:
                raise Exception("Request PO Amendment button not found")            
            print("Waiting for PO Amendment form to load...")
            page.wait_for_timeout(10000)                        
            try:
                page.wait_for_selector("table[id='POLinesAddRN:Content']", timeout=15000)
                print("PO Amendment form loaded successfully")
            except PlaywrightTimeoutError:
                print("Warning: Table not found with specific ID, trying alternative...")
                tables = page.locator("table").all()
                print(f"Found {len(tables)} tables on the page")
                if len(tables) > 0:
                    page.screenshot(path="debug_amendment_form.png")
                    print("Screenshot saved as debug_amendment_form.png")            
            change_items = data.get("Change_Item", [])
            for change_item in change_items:
                item_code = change_item["Item_Code"]
                new_quantity = change_item["New_Quantity"]                
                print(f"Looking for Item Code: {item_code}")                
                try:
                    table_rows = page.locator("table[id='POLinesAddRN:Content'] tr").all()
                    print(f"Found {len(table_rows)} table rows")
                except:
                    print("Could not find table rows, trying alternative selector...")
                    table_rows = page.locator("tr.xn0").all()                
                for row_idx, row in enumerate(table_rows):
                    if row_idx == 0:
                        continue 
                    try:
                        item_cell = row.locator("td[headers='ItemCol']")
                        if item_cell.count() > 0:
                            item_text = item_cell.inner_text()
                            print(f"Row {row_idx}: Found item text: {item_text}")                            
                            if item_code in item_text:
                                print(f"Match found for {item_code} at row {row_idx}")                                
                                action_select = row.locator("select")
                                if action_select.count() > 0:
                                    try:
                                        action_select.select_option(label="Quantity Change")
                                        print("Action changed to Quantity Change")
                                        page.wait_for_timeout(1000)
                                    except:
                                        try:
                                            action_select.select_option(value="Quantity Change")
                                            print("Action changed to Quantity Change (by value)")
                                            page.wait_for_timeout(1000)
                                        except:
                                            print("Could not change Action dropdown")                                
                                new_qty_cell = row.locator("td[headers='NEWQty']")
                                if new_qty_cell.count() > 0:
                                    new_qty_cell.click()
                                    page.wait_for_timeout(500)
                                    new_qty_input = new_qty_cell.locator("input")
                                    if new_qty_input.count() > 0:
                                        new_qty_input.fill(new_quantity)
                                        new_qty_input.press("Tab")
                                        print(f"Updated New Quantity to {new_quantity}")
                                        page.wait_for_timeout(500)
                                    else:
                                        new_qty_cell.type(new_quantity)
                                        print(f"Typed New Quantity: {new_quantity}")
                                        page.wait_for_timeout(500)
                                reason_cell = row.locator("td[headers='ReasonCol']")
                                if reason_cell.count() > 0:
                                    reason_cell.click()
                                    page.wait_for_timeout(500)
                                    reason_input = reason_cell.locator("input")
                                    if reason_input.count() > 0:
                                        reason_input.fill("As per BOQ")
                                        reason_input.press("Tab")
                                        print("Updated Reason to 'As per BOQ'")
                                        page.wait_for_timeout(500)
                                    else:
                                        reason_cell.type("As per BOQ")
                                        print("Typed Reason: As per BOQ")
                                        page.wait_for_timeout(500)                                
                                break
                    except Exception as e:
                        print(f"Error processing row {row_idx}: {e}")
                        continue
            page.wait_for_timeout(3000)            
            browser.close()
            print("Browser closed successfully")            
        except Exception as e:
            print(f"Error during process: {e}")
            try:
                page.screenshot(path="error_screenshot.png")
                print("Error screenshot saved as error_screenshot.png")
            except:
                pass
            time.sleep(20)
            browser.close()
            raise Exception(f"Failed to process PO Amendment request: {str(e)}")

if __name__ == "__main__":
    data = {
        "PO_Number": "23030562008",
        "File_Url": "https://3f9a4e5dd7b6b0998a280c44401343a5.cdn.bubble.io/f1742198933168x784106798636753400/Signed_File.pdf",
        "Change_Item": [
            {
                "PO_Line_No": "1",
                "Item_Code": "22-208830-0-03-ZZ-ZZ-000",
                "New_Quantity": "10"
            },
            {
                "PO_Line_No": "2",
                "Item_Code": "29-300000-C-00-ZZ-ZZ-L46",
                "New_Quantity": "10"
            },
        ],
        "Added_Items": []
    }    
    try:
        result = Request_PO_Amendment(data)
        print("PO Amendment request completed successfully")
    except Exception as e:
        print(f"Script failed: {e}")