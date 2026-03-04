"""Tasks:
Extract all prices from the receipt
Find all product names
Calculate total amount
Extract date and time information
Find payment method
Create a structured output (JSON or formatted text)"""

import re
import json

def parse_receipt(text):
    #Extract all prices from the receipt
    prices = []
    lines = text.split('\n')
    
    for line in lines: 
        #Find prices after the x symbol 
        x_matches = re.findall(r'x\s+(\d+(?:\s+\d+)?(?:\.\d+)?)', line)
        for price in x_matches:
            clean_price = float(price.replace(' ', ''))
            if clean_price > 0:
                prices.append(clean_price)
        
        # Find prices in lines with "Стоимость" (Cost)
        cost_matches = re.findall(r'Стоимость\s+(\d+(?:\s+\d+)?(?:\.\d+)?)', line)
        for price in cost_matches:
            clean_price = float(price.replace(' ', ''))
            if clean_price > 0:
                prices.append(clean_price)
    
    #Extract product names
    products = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        #Check if line starts with a number and dot 
        if re.match(r'^\d+\.', line):
            #Next line usually contains the product name
            if i + 1 < len(lines):
                product_line = lines[i + 1].strip()
                #Check that it's not a line with price
                if not re.search(r'x\s+\d+', product_line) and product_line:
                    #Remove extra characters
                    product_name = re.sub(r'^\s*\d+\s*', '', product_line)
                    if product_name and len(product_name) > 2:  #Ignore too short names
                        products.append(product_name)
            i += 2  
        else:
            i += 1
    
    #Calculate total amount
    total_pattern = r'ИТОГО:\s*(\d+(?:\s+\d+)?(?:\.\d+)?)'  # "TOTAL:"
    total_match = re.search(total_pattern, text)
    total_amount = 0
    if total_match:
        total_amount = float(total_match.group(1).replace(' ', ''))
    else:
        #amount after "Банковская карта:" (Bank card)
        card_pattern = r'Банковская карта:\s*(\d+(?:\s+\d+)?(?:\.\d+)?)'
        card_match = re.search(card_pattern, text)
        if card_match:
            total_amount = float(card_match.group(1).replace(' ', ''))
    
    #Extract date and time
    datetime_pattern = r'Время:\s*(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})'  
    datetime_match = re.search(datetime_pattern, text)
    datetime_info = ""
    if datetime_match:
        datetime_info = datetime_match.group(1)
    
    #Determine payment method
    payment_method = "Not specified"
    if "Банковская карта:" in text: 
        payment_method = "Bank card"
    elif "Наличные:" in text:
        payment_method = "Cash"
    elif "Карта:" in text:  
        payment_method = "Card"
    
    #Extract store information
    store_match = re.search(r'Филиал\s+([^\n]+)', text) 
    store = store_match.group(1) if store_match else "Not specified"
    
    bin_match = re.search(r'БИН\s+(\d+)', text)  
    bin_num = bin_match.group(1) if bin_match else "Not specified"
    
    cashier_match = re.search(r'Кассир\s+([^\n]+)', text)
    cashier = cashier_match.group(1) if cashier_match else "Not specified"
    
    receipt_num_match = re.search(r'Чек\s+№?(\d+)', text) 
    receipt_num = receipt_num_match.group(1) if receipt_num_match else "Not specified"
    
    # Create structured output
    result = {
        "prices": prices,
        "products": products,
        "total_amount": total_amount,
        "datetime": datetime_info,
        "payment_method": payment_method,
        "receipt_details": {
            "store": store,
            "bin": bin_num,
            "cashier": cashier,
            "receipt_number": receipt_num
        }
    }
    
    return result

# Read the file
try:
    with open('raw.txt', 'r', encoding='utf-8') as file:
        receipt_text = file.read()
except FileNotFoundError:
    print("Error: File 'raw.txt' not found!")
    exit(1)

# Parse the receipt
parsed_data = parse_receipt(receipt_text)

# Display results
print("=" * 50)
print("EXTRACTED DATA FROM RECEIPT")
print("=" * 50)

print(f"\n Number of items: {len(parsed_data['products'])}")
print(f"Number of prices: {len(parsed_data['prices'])}")

print("\nPRODUCTS:")
for i, product in enumerate(parsed_data['products'], 1):
    print(f"  {i:2d}. {product[:50]}{'...' if len(product) > 50 else ''}")

print("\nPRICES:")
total_sum = 0
for i, price in enumerate(parsed_data['prices'], 1):
    print(f"  {i:2d}. {price:8.2f} tenge")
    total_sum += price

print(f"\nSum of individual prices: {total_sum:.2f} tenge")
print(f"Total amount from receipt: {parsed_data['total_amount']:.2f} tenge")
print(f"Date and time: {parsed_data['datetime']}")
print(f"Payment method: {parsed_data['payment_method']}")

print("\nRECEIPT DETAILS:")
for key, value in parsed_data['receipt_details'].items():
    print(f"  {key}: {value}")

# Save to JSON file
with open('receipt_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(parsed_data, json_file, ensure_ascii=False, indent=2)



