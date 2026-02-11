import time
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os

def Request_PO_Amendment(data):
    with sync_playwright() as p:       
        try:            
            # INITIALIZE BROWSER
            try:
                browser = p.chromium.launch(headless=False, slow_mo=100)
                context = browser.new_context() 
                page = context.new_page()
                page.set_default_timeout(60000)                
                email = os.getenv("ERP_EMAIL", "bharathielectricalanna@gmail.com")
                password = os.getenv("ERP_PASSWORD", "Nexus.May@2026") 
            except Exception as e:
                print("INITIALIZE BROWSER")
                raise Exception(f"Failed to initialize browser: {str(e)}")

            # LOGIN TO ERP SYSTEM
            try: 
                page.goto("https://induserp.industowers.com/OA_HTML/AppsLocalLogin.jsp")
                page.wait_for_timeout(5000)            
                page.fill('input[name="usernameField"]', email)
                page.fill('input[name="passwordField"]', password)
                page.press('input[name="passwordField"]', 'Enter')            
                page.wait_for_timeout(8000)
            except Exception as e:
                print("LOGIN TO ERP SYSTEM")
                raise Exception(f"Failed to login - check credentials or page structure: {str(e)}")
            page.wait_for_timeout(2000)

            # EXPAND NAVIGATION MENU AND GO TO HOME PAGE
            try:
                page.wait_for_selector("img[title='Expand']", timeout=15000)
                page.click("img[title='Expand']")
            except PlaywrightTimeoutError:
                print("EXPAND NAVIGATION MENU AND GO TO HOME PAGE")
                raise Exception("Failed to expand navigation menu - structure may have changed")
            page.wait_for_timeout(2000) 

            # HOME PAGE LINK IN NAVIGATION MENU   
            try:
                page.wait_for_selector("li >> text=Home Page", timeout=15000)
                page.click("li >> text=Home Page")
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                print("HOME PAGE LINK IN NAVIGATION MENU")
                raise Exception("Failed to click Home Page link - structure may have changed")
            page.wait_for_timeout(2000)

            # CLICK ON ORDERS LINK IN NAVIGATION MENU
            try:
                page.wait_for_selector("a:has-text('Orders')", timeout=15000)
                page.click("a:has-text('Orders')")
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                print("ORDERS LINK IN NAVIGATION MENU")
                raise Exception("Failed to click Orders link - structure may have changed")
            page.wait_for_timeout(2000)          
            
            # PURCHASE ORDERS LINK IN ORDERS SUBMENU
            try:
                page.wait_for_selector("a[title='Purchase Orders']", timeout=15000)
                page.click("a[title='Purchase Orders']")
                page.wait_for_timeout(5000)
            except PlaywrightTimeoutError:
                print("PURCHASE ORDERS LINK IN ORDERS SUBMENU")
                raise Exception("Failed to click Purchase Orders link - structure may have changed") 
            page.wait_for_timeout(2000)

            # ADVANCED SEARCH BUTTON ON PURCHASE ORDERS PAGE
            try:
                page.wait_for_selector("button:has-text('Advanced Search')", timeout=15000)
                page.click("button:has-text('Advanced Search')")
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                print("ADVANCED SEARCH BUTTON ON PURCHASE ORDERS PAGE")
                raise Exception("Failed to click Advanced Search button - structure may have changed")
            page.wait_for_timeout(2000)

            # ENTER PO NUMBER IN SEARCH FIELD AND SUBMIT 
            try:
                page.wait_for_selector("input#Value_0", timeout=15000)
                page.fill("input#Value_0", data["PO_Number"])
                page.wait_for_timeout(1000)
            except PlaywrightTimeoutError:
                print("ENTER PO NUMBER IN SEARCH FIELD")
                raise Exception("Failed to enter PO number in search field - structure may have changed")
            page.wait_for_timeout(2000)

            # CLICK ON SEARCH SUBMIT BUTTON  
            try:
                page.wait_for_selector("button#customizeSubmitButton", timeout=15000)
                page.click("button#customizeSubmitButton")
                page.wait_for_timeout(8000)
            except PlaywrightTimeoutError:
                print("CLICK ON SEARCH SUBMIT BUTTON")
                raise Exception("Failed to click search submit button - structure may have changed") 
            page.wait_for_timeout(2000)    

            # CLICK ON PO NUMBER LINK
            try: 
                po_selectors = [f"a:has-text('{data['PO_Number']}')","a[id^='N93:PosPoNumber:']",f"a:contains('{data['PO_Number']}')","table a",]
                po_link_found = False
                for selector in po_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=10000)
                        page.click(selector)
                        po_link_found = True
                        break
                    except PlaywrightTimeoutError:
                        continue            
                if not po_link_found:
                    page.screenshot(path="debug_search_results.png")
                    raise Exception(f"PO Number link for {data['PO_Number']} not found")            
            except PlaywrightTimeoutError:
                print("CLICK ON PO NUMBER LINK")
                raise Exception("Failed to click on PO number link - structure may have changed or PO number not found in results")
            page.wait_for_timeout(2000) 
                       
            # INITIATE PO AMENDMENT REQUEST
            try:
                amendment_selectors = ["button:text('Request PO Amendment')","button:has-text('Request PO Amendment')","input[value='Request PO Amendment']",]            
                amendment_found = False
                for selector in amendment_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=10000)
                        page.click(selector)
                        amendment_found = True
                        break
                    except PlaywrightTimeoutError:
                        continue            
                if not amendment_found:
                    raise Exception("Request PO Amendment button not found")            
            except PlaywrightTimeoutError:
                print("INITIATE PO AMENDMENT REQUEST")
                raise Exception("Failed to initiate PO amendment request - structure may have changed or user may not have permissions")
            page.wait_for_timeout(10000)    

            # MODIFY EXISTING PO LINE ITEMS (QUANTITY CHANGES)
            try:
                page.wait_for_selector("table[id='POLinesAddRN:Content']", timeout=15000)
            except PlaywrightTimeoutError:
                print("MODIFY EXISTING PO LINE ITEMS")
                raise Exception("PO lines table not found - structure may have changed or page may not have loaded properly")
            
            # PROCESS CHANGE ITEMS
            try:
                change_items = data.get("Change_Item", [])
                for change_item in change_items:
                    item_code = change_item["Item_Code"]
                    new_quantity = change_item["New_Quantity"]                
                    try:
                        table_rows = page.locator("table[id='POLinesAddRN:Content'] tr").all()
                    except:
                        table_rows = page.locator("tr.xn0").all()                
                    for row_idx, row in enumerate(table_rows):
                        if row_idx == 0:
                            continue 
                        try:
                            item_cell = row.locator("td[headers='ItemCol']")
                            if item_cell.count() > 0:
                                item_text = item_cell.inner_text()
                                if item_code in item_text:
                                    # Change action to "Quantity Change"
                                    action_select = row.locator("select")
                                    if action_select.count() > 0:
                                        try:
                                            action_select.select_option(label="Quantity Change")
                                            page.wait_for_timeout(1000)
                                        except:
                                            try:
                                                action_select.select_option(value="Quantity Change")
                                                page.wait_for_timeout(1000)
                                            except:
                                                print("Could not change Action dropdown")
                                    
                                    # Update quantity
                                    new_qty_cell = row.locator("td[headers='NEWQty']")
                                    if new_qty_cell.count() > 0:
                                        new_qty_cell.click()
                                        page.wait_for_timeout(500)
                                        new_qty_input = new_qty_cell.locator("input")
                                        if new_qty_input.count() > 0:
                                            new_qty_input.fill(new_quantity)
                                            new_qty_input.press("Tab")
                                            page.wait_for_timeout(500)
                                        else:
                                            new_qty_cell.type(new_quantity)
                                            page.wait_for_timeout(500)
                                    
                                    # Add reason for change
                                    reason_cell = row.locator("td[headers='ReasonCol']")
                                    if reason_cell.count() > 0:
                                        reason_cell.click()
                                        page.wait_for_timeout(500)
                                        reason_input = reason_cell.locator("input")
                                        if reason_input.count() > 0:
                                            reason_input.fill("As per BOQ")
                                            reason_input.press("Tab")
                                            page.wait_for_timeout(500)
                                        else:
                                            reason_cell.type("As per BOQ")
                                            page.wait_for_timeout(500)                                
                                    break
                        except Exception as e:
                            continue
            except Exception as e:
                print("PROCESS CHANGE ITEMS")
                raise Exception(f"Failed to process change items - structure may have changed or items not found in table: {str(e)}")
            page.wait_for_timeout(2000)

            # ADD NEW LINE ITEMS TO PO
            try:
                added_items = data.get("Added_Items", [])            
                for added_item in added_items:
                    try:
                        add_line_selectors = ["img#addTableRow1","a[title='Add Line']","img[title='Add Line']","img[alt='Add Line']"]
                        add_line_clicked = False
                        for selector in add_line_selectors:
                            try:
                                page.wait_for_selector(selector, timeout=5000)
                                page.click(selector)
                                add_line_clicked = True
                                page.wait_for_timeout(3000)
                                break
                            except PlaywrightTimeoutError:
                                continue                    
                        if not add_line_clicked:
                            continue                    
                        page.wait_for_timeout(2000)                    
                        try:
                            all_rows = page.locator("table[id='POLinesAddRN:Content'] tr").all()
                            new_row_index = None                        
                            for idx, row in enumerate(all_rows):
                                if idx == 0:
                                    continue                             
                                po_line_span = row.locator("span[id^='POLinesAddRN:POLineNumSt:']")
                                if po_line_span.count() > 0:
                                    po_line_text = po_line_span.inner_text().strip()
                                    if po_line_text == "" or po_line_text == "<br>":
                                        new_row_index = idx
                                        new_row = row
                                        break                        
                            if new_row_index is None:
                                new_row = all_rows[1] if len(all_rows) > 1 else None
                        except Exception as e:
                            all_rows = page.locator("table[id='POLinesAddRN:Content'] tr").all()
                            new_row = all_rows[1] if len(all_rows) > 1 else None                  
                        
                        if not new_row:
                            continue                    
                        # Fill item code
                        item_code_input = new_row.locator("input[id^='POLinesAddRN:ItemType:']")
                        if item_code_input.count() > 0:
                            item_code_input.fill(added_item['Item_Code'])
                            item_code_input.press("Tab")
                            page.wait_for_timeout(2000)
                        else:
                            item_code_input2 = new_row.locator("td[headers='ItemCol'] input")
                            if item_code_input2.count() > 0:
                                item_code_input2.fill(added_item['Item_Code'])
                                item_code_input2.press("Tab")
                                page.wait_for_timeout(2000)                    
                        # Fill quantity
                        qty_input = new_row.locator("input[id^='POLinesAddRN:Qty:']")
                        if qty_input.count() > 0:
                            qty_input.fill(added_item['Quantity'])
                            qty_input.press("Tab")
                            page.wait_for_timeout(1000)
                        else:
                            print("Warning: Quantity input not found")
                            qty_input2 = new_row.locator("td[headers='QtyCol'] input")
                            if qty_input2.count() > 0:
                                qty_input2.fill(added_item['Quantity'])
                                qty_input2.press("Tab")
                                print(f"Filled Quantity (alt): {added_item['Quantity']}")
                                page.wait_for_timeout(1000)                    
                        # Fill project number
                        project_input = new_row.locator("input[id^='POLinesAddRN:ProjectNumberLov:']")
                        if project_input.count() > 0:
                            project_input.fill(added_item['Project_Number'])
                            project_input.press("Tab")
                            page.wait_for_timeout(1000)
                        else:
                            project_input2 = new_row.locator("td[headers='ProjectNumberCol'] input")
                            if project_input2.count() > 0:
                                project_input2.fill(added_item['Project_Number'])
                                project_input2.press("Tab")
                                page.wait_for_timeout(1000)                    
                        # Fill reason
                        reason_input = new_row.locator("input[id^='POLinesAddRN:Reason:']")
                        if reason_input.count() > 0:
                            reason_input.fill("As per BOQ")
                            reason_input.press("Tab")
                            page.wait_for_timeout(1000)
                        else:
                            reason_input2 = new_row.locator("td[headers='ReasonCol'] input")
                            if reason_input2.count() > 0:
                                reason_input2.fill("As per BOQ")
                                reason_input2.press("Tab")
                                print("Filled Reason (alt): As per BOQ")
                                page.wait_for_timeout(1000)                    
                        # Set action to "Add Line"
                        action_select = new_row.locator("select[id^='POLinesAddRN:ManualLine:']")
                        if action_select.count() > 0:
                            try:
                                current_value = action_select.input_value()
                                if "Add Line" not in current_value:
                                    try:
                                        action_select.select_option(label="Add Line")
                                    except:
                                        try:
                                            action_select.select_option(value="Add Line")
                                        except:
                                            print("Could not set Action dropdown")
                                else:
                                    print("Action already set to 'Add Line'")
                                page.wait_for_timeout(1000)
                            except Exception as e:
                                print(f"Error setting Action: {e}")
                        else:
                            print("Warning: Action dropdown not found in new row")                    
                        page.wait_for_timeout(2000)                     
                    except Exception as e:
                        print(f"Error adding item {added_item.get('Item_Code', 'Unknown')}: {e}")            
            except Exception as e:
                print("ADD NEW LINE ITEMS TO PO")
                raise Exception(f"Failed to add new line items - structure may have changed or inputs not found: {str(e)}")
            page.wait_for_timeout(2000)
            
            # ADD ATTACHMENT TO AMENDMENT REQUEST
            try:
                attachment_selectors = ["img[title='Add Attachment']","img[alt='Add Attachment']","img[src*='add_attach']","a:has(img[title='Add Attachment'])","a:has(img[alt='Add Attachment'])"]
                for selector in attachment_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        page.click(selector)
                        break
                    except PlaywrightTimeoutError:
                        continue
                page.wait_for_timeout(2000)
            except Exception as e:
                print("ADD ATTACHMENT TO AMENDMENT REQUEST")
                raise Exception(f"Failed to add attachment: {str(e)}")

            # SELECT ATTACHMENT CATEGORY 
            try:
                category_selectors = ["select#AkAttachmentCategory","select[title='Category Name']","select.x8","select[name='AkAttachmentCategory']"]
                category_found = False
                for selector in category_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        page.select_option(selector, label="Miscellaneous")
                        category_found = True
                        break
                    except Exception as e:
                        continue                
                if not category_found:
                    try:
                        page.select_option("select#AkAttachmentCategory", value="1WDSKCY-Z")
                        print("Selected 'Miscellaneous' using value attribute")
                    except:
                        print("Warning: Could not select category from dropdown")          
            except Exception as e:
                print(f"Error handling category dropdown: {e}")
            page.wait_for_timeout(2000)
            
            # CONFIGURE URL ATTACHMENT
            try:
                page.wait_for_selector("input#AkAttachR2", timeout=5000)
                page.click("input#AkAttachR2")
                page.wait_for_timeout(2000)                
                try:
                    page.wait_for_selector("input#URLInput", timeout=5000)
                    url_input = page.locator("input#URLInput")
                    url_input.click()
                    url_input.clear()                    
                    url_input.fill(data["File_Url"])                    
                    url_input.press("Tab")
                    page.wait_for_timeout(1000)                    
                except Exception as e:
                    try:
                        page.fill("input[name='URLInput']", data["File_Url"])
                        page.wait_for_timeout(1000)
                    except Exception as e2:
                        print(f"Could not fill URL input: {e2}")                        
            except Exception as e:
                try:
                    page.click("input[value='URL'][name='AkAttachRB']")
                    page.wait_for_timeout(2000)                    
                    page.fill("input#URLInput", data["File_Url"])                    
                except Exception as e2:
                    print("CONFIGURE URL ATTACHMENT")
            page.wait_for_timeout(2000)

            # SAVE ATTACHMENT
            try:
                page.wait_for_selector("button#Okay_uixr", timeout=5000)                
                apply_button = page.locator("button#Okay_uixr")                
                if apply_button.is_visible():
                    apply_button.click()
                    page.wait_for_timeout(8000)                    
                    try:
                        success_indicators = ["div:has-text('Attachment added')","div:has-text('successfully')","span:has-text('Attachment')","table:has-text('Signed_File.pdf')", "table:has-text('Miscellaneous')" ]
                        for indicator in success_indicators:
                            try:
                                page.wait_for_selector(indicator, timeout=3000)
                                break
                            except:
                                continue
                    except Exception as e:
                        print(f"Could not verify attachment save: {e}")
                else:
                    print("Apply button is not visible")                    
            except Exception as e:
                try:
                    page.click("button[title='Apply']")
                    page.wait_for_timeout(8000)
                except:
                    try:
                        page.click("button:has-text('Apply')")
                        page.wait_for_timeout(8000)
                    except:
                        try:
                            page.click("button.x80")
                            page.wait_for_timeout(8000)
                        except Exception as e2:
                            print("SAVE ATTACHMENT")            
            page.wait_for_timeout(2000)
            
            # SUBMIT PO AMENDMENT REQUEST
            try:
                page.wait_for_selector("button#Submit", timeout=10000)                
                submit_button = page.locator("button#Submit")                
                if submit_button.is_visible():
                    submit_button.click()
                    page.wait_for_timeout(8000)                    
                else:
                    submit_button.scroll_into_view_if_needed()
                    page.wait_for_timeout(2000)                    
                    if submit_button.is_visible():
                        submit_button.click()
                        page.wait_for_timeout(8000)
                    else:
                        raise Exception("Submit button not visible even after scrolling")                    
            except Exception as e:
                print(f"Error clicking Submit button by ID: {e}")                
                try:
                    page.click("button:has-text('Submit')")
                    page.wait_for_timeout(8000)
                except:
                    try:
                        page.click("button[title='Submit']")
                        page.wait_for_timeout(8000)
                    except:
                        try:
                            page.click("button.x80:has-text('Submit')")
                            page.wait_for_timeout(8000)
                        except:
                            try:
                                page.click("input[type='submit'][value='Submit']")
                                page.wait_for_timeout(8000)
                            except Exception as e2:
                                print("SUBMIT PO AMENDMENT REQUEST")
                                raise
            page.wait_for_timeout(5000)            

            # HANDLE CONFIRMATION POPUP AND EXTRACT REQUEST ID
            try:
                request_id = None
                success_message = None
                page.wait_for_selector("iframe#iframedefaultDialogPopup", timeout=15000)                
                iframe = page.frame_locator("iframe#iframedefaultDialogPopup")                
                iframe.locator("button[title='Yes']").wait_for(timeout=5000)                
                try:
                    success_message = iframe.locator("body").inner_text(timeout=3000)
                    request_id_pattern = r"Request ID:\s*([^\s]+)"
                    match = re.search(request_id_pattern, success_message)                    
                    if match:
                        request_id = match.group(1)
                        print(f"Extracted Request ID: {request_id}")
                    else:
                        patterns = [r"ID:\s*([^\s]+)",r"Request\s*ID\s*:\s*([^\s]+)",r"Request\s*#\s*:\s*([^\s]+)",r"([0-9]{8}-[0-9]{6,})", r"Changes has been submitted.*?([0-9-]+)"]
                        for pattern in patterns:
                            match = re.search(pattern, success_message)
                            if match:
                                request_id = match.group(1)
                                print(f"Extracted Request ID using pattern: {request_id}")
                                break
                except Exception as e:
                    print(f"Could not extract success message before clicking Yes: {e}")
                iframe.locator("button[title='Yes']").click()                
                page.wait_for_timeout(5000)                
                if not request_id:
                    try:
                        success_message = iframe.locator("body").inner_text(timeout=2000)
                        if success_message:
                            match = re.search(r"Request ID:\s*([^\s]+)", success_message)
                            if match:
                                request_id = match.group(1)
                                print(f"Extracted Request ID after click: {request_id}")
                    except:
                        pass                
                page.bring_to_front()                
            except Exception as e:
                print(f"Error handling confirmation popup: {e}")                
                try:
                    yes_button_selectors = ["button[title='Yes']","button:has-text('Yes')","button.x80:has-text('Yes')","button:has-text('Y')es"]
                    yes_clicked = False
                    for selector in yes_button_selectors:
                        try:
                            page.wait_for_selector(selector, timeout=3000)
                            page.click(selector)
                            print(f"Clicked Yes button using selector: {selector}")
                            yes_clicked = True
                            page.wait_for_timeout(5000)
                            break
                        except:
                            continue                    
                    if not yes_clicked:
                        print("Warning: Could not click Yes button in confirmation popup")                        
                except Exception as e2:
                    print(f"Alternative Yes button click also failed: {e2}")
            page.wait_for_timeout(10000)
            
            # If we still don't have the Request ID, try to find it on the main page
            if not request_id:
                try:
                    # Look for success message on main page
                    success_selectors = [
                        "div:has-text('Changes has been submitted')",
                        "div:has-text('Request ID')",
                        "div:has-text('successfully')",
                        "div.popupContent",
                        "div.OraParamPopupContent"
                    ]
                    
                    for selector in success_selectors:
                        try:
                            page.wait_for_selector(selector, timeout=3000)
                            success_message = page.locator(selector).inner_text()
                            if success_message:
                                print(f"Found success message on main page: {success_message}")
                                
                                # Extract Request ID
                                match = re.search(r"Request ID:\s*([^\s]+)", success_message)
                                if match:
                                    request_id = match.group(1)
                                    print(f"Extracted Request ID from main page: {request_id}")
                                    break
                        except:
                            continue
                            
                    # If still not found, try regex patterns on page content
                    if not request_id:
                        try:
                            page_content = page.content()
                            patterns = [
                                r"Request ID:\s*([^\s<>&]+)",
                                r"Changes has been submitted.*?([0-9]{8}-[0-9]{6,})",
                                r"([0-9]{8}-[0-9]{6,})"
                            ]
                            for pattern in patterns:
                                match = re.search(pattern, page_content)
                                if match:
                                    request_id = match.group(1)
                                    print(f"Extracted Request ID from page content: {request_id}")
                                    break
                        except Exception as e:
                            print(f"Could not extract Request ID from page content: {e}")
                except Exception as e:
                    print(f"Could not find Request ID on main page: {e}")
                     
            # CLEANUP AND CLOSE BROWSER
            browser.close()
            
            # Prepare response
            if request_id:
                return {
                    "Status": "Success",
                    "Status_Code": 200,
                    "Message": success_message if success_message else "PO Amendment request submitted successfully.",
                    "PO_Amendment": request_id,
                    "PO_Number": data["PO_Number"],
                    "Date": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            else:
                # If we couldn't extract the Request ID, still return success but with a note
                return {
                    "Status": "Success (Request ID not captured)",
                    "Status_Code": 200,
                    "Message": "PO Amendment request was submitted, but could not capture the Request ID. Please check manually.",
                    "PO_Amendment": "Not captured",
                    "PO_Number": data["PO_Number"],
                    "Date": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                
        except Exception as e:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            error_screenshot_path = f"po_amendment_error_{timestamp}.png"
            try:
                page.screenshot(path=error_screenshot_path, full_page=True)
                print(f"Error screenshot saved: {error_screenshot_path}")
            except:
                pass
            
            try:
                browser.close()
            except:
                pass                
            raise Exception(f"Failed to process PO Amendment request: {str(e)}")

if __name__ == "__main__":
    
    # TEST DATA CONFIGURATION 
    data = {
        "PO_Number": "23030558874",
        "File_Url": "https://3f9a4e5dd7b6b0998a280c44401343a5.cdn.bubble.io/f1742198933168x784106798636753400/Signed_File.pdf",
        "Change_Item": [
            {
                "PO_Line_No": "1",
                "Item_Code": "22-212660-0-03-ZZ-ZZ-000",
                "New_Quantity": "7"
            },
            {
                "PO_Line_No": "2",
                "Item_Code": "22-212760-0-03-ZZ-ZZ-000",
                "New_Quantity": "7"
            },
        ],
        "Added_Items": [{
                "Item_Code": "29-400000-0-00-ZZ-ZZ-886",
                "Quantity": "5",
                "Project_Number": "R/RL-8139267"
            }]
    }       
    try:
        result = Request_PO_Amendment(data)
        print("Result:", result)
    except Exception as e:
        print(f"Script failed: {e}")
