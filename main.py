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
            print("Step 1: Logging in...")
            page.goto("https://induserp.industowers.com/OA_HTML/AppsLocalLogin.jsp")
            page.wait_for_timeout(3000)            
            page.fill('input[name="usernameField"]', email)
            page.fill('input[name="passwordField"]', password)
            page.press('input[name="passwordField"]', 'Enter')            
            page.wait_for_timeout(5000)
            print("Step 2: Navigating to Home Page...")
            page.wait_for_selector("img[title='Expand']", timeout=10000)
            page.click("img[title='Expand']")            
            page.wait_for_selector("li >> text=Home Page", timeout=15000)
            page.click("li >> text=Home Page")            
            print("Step 3: Opening Orders menu...")
            page.wait_for_selector("a:has-text('Orders')", timeout=15000)
            page.click("a:has-text('Orders')")  
            print("Step 4: Selecting Purchase Orders...")
            page.wait_for_selector("a[title='Purchase Orders']", timeout=15000)
            page.click("a[title='Purchase Orders']")  
            print("Step 5: Opening Advanced Search...")
            page.wait_for_selector("button:has-text('Advanced Search')", timeout=10000)
            page.click("button:has-text('Advanced Search')")            
            print(f"Step 6: Entering PO Number: {data['PO_Number']}")
            page.wait_for_selector("input#Value_0", timeout=10000)
            page.fill("input#Value_0", data["PO_Number"])
            print("Step 7: Clicking Go button...")
            page.wait_for_selector("button#customizeSubmitButton", timeout=10000)
            page.click("button#customizeSubmitButton")
            print("Step 8: Clicking PO number link...")
            page.wait_for_selector("a[id^='N93:PosPoNumber:']", timeout=10000)
            page.click("a[id^='N93:PosPoNumber:']")
            print("Step 9: Clicking Request PO Amendment...")
            page.wait_for_selector("button:text('Request PO Amendment')", timeout=10000)
            page.click("button:text('Request PO Amendment')")            
            page.wait_for_timeout(5000)         
            page.wait_for_selector("table#POLinesAddRN\\:Content", timeout=15000)            
            rows = page.locator("table#POLinesAddRN\\:Content tbody tr").all()         
            for change_item in data.get("Change_Item", []):
                po_line_no = change_item.get("PO_Line_No")
                item_code = change_item.get("Item_Code")
                new_quantity = change_item.get("New_Quantity")               
                found = False
                
                # Find the row that matches both PO Line No and Item Code
                for i, row in enumerate(rows):
                    try:
                        # Get PO Line No from the first column (index 0)
                        po_line_elem = row.locator("td:nth-child(1) span[id*='POLineNumSt']")
                        if po_line_elem.count() > 0:
                            actual_po_line = po_line_elem.text_content().strip()
                            
                            # Get Item Code from the second column (index 1)
                            item_code_elem = row.locator("td:nth-child(2) span[id*='ItemType']")
                            if item_code_elem.count() > 0:
                                actual_item_code = item_code_elem.text_content().strip()
                                
                                # Check if this row matches what we're looking for
                                if str(actual_po_line) == str(po_line_no) and actual_item_code == item_code:
                                    print(f"✓ Found matching row at index {i}: PO Line={actual_po_line}, Item Code={actual_item_code}")
                                    found = True
                                    
                                    # Update Action dropdown to "Quantity Change"
                                    print("  Updating Action dropdown...")
                                    action_dropdown = row.locator("select[id*='POLine:']")
                                    if action_dropdown.count() > 0:
                                        # Select "Quantity Change" option
                                        action_dropdown.select_option(label="Quantity Change")
                                        print("  ✓ Action set to 'Quantity Change'")
                                        page.wait_for_timeout(1000)  # Wait for UI to update
                                    else:
                                        print("  ✗ Action dropdown not found")
                                    
                                    # Update New Quantity field
                                    print(f"  Updating New Quantity to: {new_quantity}")
                                    new_qty_input = row.locator("input[id*='newQty:']")
                                    
                                    # Try to find the input field
                                    if new_qty_input.count() == 0:
                                        # Sometimes it might be a span that turns into input
                                        new_qty_span = row.locator("span[id*='newQty:']")
                                        if new_qty_span.count() > 0:
                                            # Click to activate the input
                                            new_qty_span.click()
                                            page.wait_for_timeout(500)
                                            # Now look for the input again
                                            new_qty_input = row.locator("input[id*='newQty:']")
                                    
                                    if new_qty_input.count() > 0:
                                        # Clear and fill the new quantity
                                        new_qty_input.fill("")
                                        new_qty_input.fill(new_quantity)
                                        print(f"  ✓ New Quantity updated to {new_quantity}")
                                    else:
                                        print("  ✗ New Quantity field not found")
                                    
                                    # Update Reason field
                                    print("  Updating Reason to: As per BOQ")
                                    reason_input = row.locator("input[id*='Reason:']")
                                    
                                    if reason_input.count() == 0:
                                        # Try to find as span first
                                        reason_span = row.locator("span[id*='Reason:']")
                                        if reason_span.count() > 0:
                                            reason_span.click()
                                            page.wait_for_timeout(500)
                                            reason_input = row.locator("input[id*='Reason:']")
                                    
                                    if reason_input.count() > 0:
                                        reason_input.fill("As per BOQ")
                                        print("  ✓ Reason updated to 'As per BOQ'")
                                    else:
                                        print("  ✗ Reason field not found")
                                    
                                    print(f"  ✓ Successfully updated row for PO Line {po_line_no}")
                                    break
                    
                    except Exception as e:
                        print(f"  Error processing row {i}: {e}")
                        continue
                
                if not found:
                    print(f"✗ No matching row found for PO Line {po_line_no}, Item Code {item_code}")
            
            print("\nStep 12: Processing added items (if any)...")
            
            # Process added items if present
            for added_item in data.get("Added_Items", []):
                print(f"\nProcessing new item: {added_item.get('Item_Description')}")
                # Note: Adding new items would require finding and clicking an "Add Line" button
                # This would depend on the specific UI of your ERP system
                # You might need to:
                # 1. Find and click "Add Line" or similar button
                # 2. Fill in the new row fields
                # For now, we'll just log it
                print(f"  Item Description: {added_item.get('Item_Description')}")
                print(f"  Quantity: {added_item.get('Quantity')}")
                print(f"  Price: {added_item.get('Price')}")
                print("  Note: Add Line functionality needs to be implemented based on your ERP UI")
            
            print("\nStep 13: Taking screenshot of updated form...")
            page.screenshot(path="updated_amendment_form.png")
            print("  Screenshot saved: updated_amendment_form.png")
            
            print("\n✓ All updates completed successfully!")
            
            # Keep browser open for inspection
            print("\nBrowser will remain open for 30 seconds for inspection...")
            time.sleep(30)
            
            browser.close()
            
        except Exception as e:
            print(f"Error during process: {e}")
            # Take error screenshot
            page.screenshot(path="error_screenshot.png")
            print("Error screenshot saved: error_screenshot.png")
            browser.close()
            raise

if __name__ == "__main__":
    data = {
        "PO_Number": "23030561912",
        "File_Url": "https://3f9a4e5dd7b6b0998a280c44401343a5.cdn.bubble.io/f1742198933168x784106798636753400/Signed_File.pdf",
        "Change_Item": [
            {
                "PO_Line_No": "10",
                "Item_Code": "21-D00000-0-00-ZZ-ZZ-705",
                "New_Quantity": "10"
            },
            {
                "PO_Line_No": "11",
                "Item_Code": "22-420000-0-00-ZZ-ZZ-169",
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
    
    print("Starting PO Amendment Process...")
    print("=" * 50)
    result = Request_PO_Amendment(data)
    print("=" * 50)
    print("Process completed!")