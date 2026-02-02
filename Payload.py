# For PO Amendment Request API (Both Added Items and Changed Items) 
URL = "http://13.201.210.134/api/request_po_amendment/"
PAYLOAD = {
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
                "Item_Code": "29-400000-0-00-ZZ-ZZ-886",
                "Quantity": "5",
                "Project_Number": "R/RL-8230110"
            },
            {
                "Item_Code": "29-400000-0-00-ZZ-ZZ-886",
                "Quantity": "5",
                "Project_Number": "R/RL-8230110"
            }
        ]

    }
RESPONSE = {
    "Status": "Success",
    "Status_Code": 200,
    "Message": "PO Amendment request submitted successfully.",
    "PO_Amendment": "1234567890",
    "Date": "2025-04-05"
}

# For PO Amendment Request API (Changed Items)  
URL = "http://13.201.210.134/api/request_po_amendment/"
PAYLOAD = {
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
        "Added_Items": [{}]

    }
RESPONSE = {
    "Status": "Success",
    "Status_Code": 200,
    "Message": "PO Amendment request submitted successfully.",
    "PO_Amendment": "1234567890",
    "Date": "2025-04-05"
}


# For PO Amendment Request API (Added Items)  
URL = "http://13.201.210.134/api/request_po_amendment/"
PAYLOAD = {
        "PO_Number": "23030561912",
        "File_Url": "https://3f9a4e5dd7b6b0998a280c44401343a5.cdn.bubble.io/f1742198933168x784106798636753400/Signed_File.pdf",
        "Change_Item": [{}],
        "Added_Items": [
            {
                "Item_Code": "29-400000-0-00-ZZ-ZZ-886",
                "Quantity": "5",
                "Project_Number": "R/RL-8230110"
            },
            {
                "Item_Code": "29-400000-0-00-ZZ-ZZ-886",
                "Quantity": "5",
                "Project_Number": "R/RL-8230110"
            }
        ]

    }
RESPONSE = {
    "Status": "Success",
    "Status_Code": 200,
    "Message": "PO Amendment request submitted successfully.",
    "PO_Amendment": "1234567890",
    "Date": "2025-04-05"
}