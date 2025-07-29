import re
from American_Directions.process_complex_text import process_complex_tasks
from American_Directions.phone import phone_classification


# def clean_return_text(text):
#     # Replace ') ' at the start of any argument with just a space
#     # Handle first argument
#     text = text.replace("returnText(') ", "returnText(' ")
#     # Handle second argument
#     text = text.replace("',' )", "',' ")
#     return text


# def process_text(model, text,question_type):
#     if not text:
#         return text
    

#     # print("we are doing ami dir ami dir")
   
        
#     # # First handle bold and italic formatting
#     # text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
#     # text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)

    
#     phone=phone_classification(model, text)
#     output=phone.get("phone",True)

#     print("the output for the Phone text is ", phone , "and the input text was : ", text)
#     if output:

#         try:
#             text_lower = text.lower()
#             phone_count = len(re.findall(r'(?i)phone\s*:?', text_lower))
#             online_count = len(re.findall(r'(?i)online\s*:?', text_lower))
            
#             sms_count = len(re.findall(r'(?i)sms\s*:?', text_lower))

#             if phone_count > 1 or online_count > 1 or sms_count>1:
#                 return process_complex_tasks(model,text)
            
#             # Check if we have content within brackets
#             bracket_match = re.search(r'\[(.*?)\]', text)
#             if bracket_match:
#                 # Split text into pre-bracket, bracket content, and post-bracket
#                 start_bracket = text.find('[')
#                 end_bracket = text.find(']', start_bracket)
                
#                 before_bracket = text[:start_bracket]
#                 bracket_content = text[start_bracket + 1:end_bracket]
#                 after_bracket = text[end_bracket + 1:]
                
#                 # Process only the content within brackets
#                 bracket_lower = bracket_content.lower()
                
#                 if "phone" in bracket_lower and "online" in bracket_lower:
#                     phone_index = bracket_lower.find("phone")
#                     online_index = bracket_lower.find("online")
                    
#                     # Get the text segments within brackets
#                     before_phone = bracket_content[:phone_index]
#                     between_phone_online = bracket_content[phone_index:online_index].strip()
#                     after_online = bracket_content[online_index:].strip()
                    
#                     # Clean up phone text
#                     phone_text = between_phone_online
#                     phone_text = re.sub(r'(?i)phone\s*:?', '', phone_text, 1)
#                     phone_text = re.sub(r'(?i)only\s*:?', '', phone_text).strip()
                    
#                     # Clean up online text
#                     online_text = after_online
#                     online_text = re.sub(r'(?i)online\s*:?', '', online_text, 1)
#                     online_text = re.sub(r'(?i)only\s*:?', '', online_text).strip()
                    
#                     # Close formatting tags before returnText if needed
#                     open_strongs = before_phone.count('<strong>') - before_phone.count('</strong>')
#                     open_ems = before_phone.count('<em>') - before_phone.count('</em>')
#                     prefix = ''
#                     suffix = ''
#                     if open_strongs > 0:
#                         prefix = '</strong>' * open_strongs
#                         suffix = '<strong>' * open_strongs
#                     if open_ems > 0:
#                         prefix = '</em>' * open_ems + prefix
#                         suffix = suffix + '<em>' * open_ems
                    
#                     # Escape single quotes
#                     phone_text = phone_text.replace("'", "\\'")
#                     online_text = online_text.replace("'", "\\'")
                    
#                     # Reconstruct text with brackets
#                     text = f"{before_bracket}[{prefix}^returnText('{phone_text}','{online_text}')^{suffix}]{after_bracket}"

#                 elif "phone" in bracket_lower and "sms" in bracket_lower:
#                     phone_index = bracket_lower.find("phone")
#                     online_index = bracket_lower.find("sms")
                    
#                     # Get the text segments within brackets
#                     before_phone = bracket_content[:phone_index]
#                     between_phone_online = bracket_content[phone_index:online_index].strip()
#                     after_online = bracket_content[online_index:].strip()
                    
#                     # Clean up phone text
#                     phone_text = between_phone_online
#                     phone_text = re.sub(r'(?i)phone\s*:?', '', phone_text, 1)
#                     phone_text = re.sub(r'(?i)only\s*:?', '', phone_text).strip()
                    
#                     # Clean up online text
#                     online_text = after_online
#                     online_text = re.sub(r'(?i)sms\s*:?', '', online_text, 1)
#                     online_text = re.sub(r'(?i)only\s*:?', '', online_text).strip()
                    
#                     # Close formatting tags before returnText if needed
#                     open_strongs = before_phone.count('<strong>') - before_phone.count('</strong>')
#                     open_ems = before_phone.count('<em>') - before_phone.count('</em>')
#                     prefix = ''
#                     suffix = ''
#                     if open_strongs > 0:
#                         prefix = '</strong>' * open_strongs
#                         suffix = '<strong>' * open_strongs
#                     if open_ems > 0:
#                         prefix = '</em>' * open_ems + prefix
#                         suffix = suffix + '<em>' * open_ems
                    
#                     # Escape single quotes
#                     phone_text = phone_text.replace("'", "\\'")
#                     online_text = online_text.replace("'", "\\'")
                    
#                     # Reconstruct text with brackets
#                     text = f"{before_bracket}[{prefix}^returnText('{phone_text}','{online_text}')^{suffix}]{after_bracket}"
                    
#                 elif "phone" in bracket_lower:
#                     phone_index = bracket_lower.find("phone")
#                     before_text = bracket_content[:phone_index]
#                     after_text = bracket_content[phone_index:].strip()
                    
#                     # Clean up text
#                     after_text = re.sub(r'(?i)phone\s*:?', '', after_text, 1)
#                     after_text = re.sub(r'(?i)only\s*:?', '', after_text).strip()
                    
#                     # Close formatting tags before returnText if needed
#                     open_strongs = before_text.count('<strong>') - before_text.count('</strong>')
#                     open_ems = before_text.count('<em>') - before_text.count('</em>')
#                     prefix = ''
#                     suffix = ''
#                     if open_strongs > 0:
#                         prefix = '</strong>' * open_strongs
#                         suffix = '<strong>' * open_strongs
#                     if open_ems > 0:
#                         prefix = '</em>' * open_ems + prefix
#                         suffix = suffix + '<em>' * open_ems
                    
#                     after_text = after_text.replace("'", "\\'")
#                     text = f"{before_bracket}[{prefix}^returnText('{after_text}','')^{suffix}]{after_bracket}"
                    
#                 elif "online" in bracket_lower:
#                     online_index = bracket_lower.find("online")
#                     before_text = bracket_content[:online_index]
#                     after_text = bracket_content[online_index:].strip()
                    
#                     # Clean up text
#                     after_text = re.sub(r'(?i)online\s*:?', '', after_text, 1)
#                     after_text = re.sub(r'(?i)only\s*:?', '', after_text).strip()
                    
#                     # Close formatting tags before returnText if needed
#                     open_strongs = before_text.count('<strong>') - before_text.count('</strong>')
#                     open_ems = before_text.count('<em>') - before_text.count('</em>')
#                     prefix = ''
#                     suffix = ''
#                     if open_strongs > 0:
#                         prefix = '</strong>' * open_strongs
#                         suffix = '<strong>' * open_strongs
#                     if open_ems > 0:
#                         prefix = '</em>' * open_ems + prefix
#                         suffix = suffix + '<em>' * open_ems
                    
#                     after_text = after_text.replace("'", "\\'")
#                     text = f"{before_bracket}[{prefix}^returnText('','{after_text}')^{suffix}]{after_bracket}"

#                 elif "sms" in bracket_lower:
#                     online_index = bracket_lower.find("sms")
#                     before_text = bracket_content[:online_index]
#                     after_text = bracket_content[online_index:].strip()
                    
#                     # Clean up text
#                     after_text = re.sub(r'(?i)sms\s*:?', '', after_text, 1)
#                     after_text = re.sub(r'(?i)only\s*:?', '', after_text).strip()
                    
#                     # Close formatting tags before returnText if needed
#                     open_strongs = before_text.count('<strong>') - before_text.count('</strong>')
#                     open_ems = before_text.count('<em>') - before_text.count('</em>')
#                     prefix = ''
#                     suffix = ''
#                     if open_strongs > 0:
#                         prefix = '</strong>' * open_strongs
#                         suffix = '<strong>' * open_strongs
#                     if open_ems > 0:
#                         prefix = '</em>' * open_ems + prefix
#                         suffix = suffix + '<em>' * open_ems
                    
#                     after_text = after_text.replace("'", "\\'")
#                     text = f"{before_bracket}[{prefix}^returnText('','{after_text}')^{suffix}]{after_bracket}"
                    
#             else:
#                 # Original processing for non-bracketed content
#                 if "phone" in text_lower and "online" in text_lower:
#                     phone_index = text_lower.find("phone")
#                     online_index = text_lower.find("online")
                    
#                     before_phone = text[:phone_index]
#                     between_phone_online = text[phone_index:online_index].strip()
#                     after_online = text[online_index:].strip()
                    
#                     phone_text = between_phone_online
#                     phone_text = re.sub(r'(?i)phone\s*:?', '', phone_text, 1)
#                     phone_text = re.sub(r'(?i)only\s*:?', '', phone_text).strip()
                    
#                     online_text = after_online
#                     online_text = re.sub(r'(?i)online\s*:?', '', online_text, 1)
#                     online_text = re.sub(r'(?i)only\s*:?', '', online_text).strip()
                    
#                     open_strongs = before_phone.count('<strong>') - before_phone.count('</strong>')
#                     open_ems = before_phone.count('<em>') - before_phone.count('</em>')
#                     prefix = ''
#                     suffix = ''
#                     if open_strongs > 0:
#                         prefix = '</strong>' * open_strongs
#                         suffix = '<strong>' * open_strongs
#                     if open_ems > 0:
#                         prefix = '</em>' * open_ems + prefix
#                         suffix = suffix + '<em>' * open_ems
                    
#                     phone_text = phone_text.replace("'", "\\'")
#                     online_text = online_text.replace("'", "\\'")
                    
#                     text = f"{before_phone}{prefix}^returnText('{phone_text}','{online_text}')^{suffix}"

#                 elif "phone" in text_lower and "sms" in text_lower:
#                     phone_index = text_lower.find("phone")
#                     online_index = text_lower.find("sms")
                    
#                     before_phone = text[:phone_index]
#                     between_phone_online = text[phone_index:online_index].strip()
#                     after_online = text[online_index:].strip()
                    
#                     phone_text = between_phone_online
#                     phone_text = re.sub(r'(?i)phone\s*:?', '', phone_text, 1)
#                     phone_text = re.sub(r'(?i)only\s*:?', '', phone_text).strip()
                    
#                     online_text = after_online
#                     online_text = re.sub(r'(?i)sms\s*:?', '', online_text, 1)
#                     online_text = re.sub(r'(?i)only\s*:?', '', online_text).strip()
                    
#                     open_strongs = before_phone.count('<strong>') - before_phone.count('</strong>')
#                     open_ems = before_phone.count('<em>') - before_phone.count('</em>')
#                     prefix = ''
#                     suffix = ''
#                     if open_strongs > 0:
#                         prefix = '</strong>' * open_strongs
#                         suffix = '<strong>' * open_strongs
#                     if open_ems > 0:
#                         prefix = '</em>' * open_ems + prefix
#                         suffix = suffix + '<em>' * open_ems
                    
#                     phone_text = phone_text.replace("'", "\\'")
#                     online_text = online_text.replace("'", "\\'")
                    
#                     text = f"{before_phone}{prefix}^returnText('{phone_text}','{online_text}')^{suffix}"
                    
#                 elif "phone" in text_lower:
#                     phone_index = text_lower.find("phone")
#                     before_text = text[:phone_index]
#                     after_text = text[phone_index:].strip()
                    
#                     # Clean up text
#                     after_text = re.sub(r'(?i)phone\s*:?', '', after_text, 1)
#                     after_text = re.sub(r'(?i)only\s*:?', '', after_text).strip()
                    
#                     # Close formatting tags before returnText if needed
#                     open_strongs = before_text.count('<strong>') - before_text.count('</strong>')
#                     open_ems = before_text.count('<em>') - before_text.count('</em>')
#                     prefix = ''
#                     suffix = ''
#                     if open_strongs > 0:
#                         prefix = '</strong>' * open_strongs
#                         suffix = '<strong>' * open_strongs
#                     if open_ems > 0:
#                         prefix = '</em>' * open_ems + prefix
#                         suffix = suffix + '<em>' * open_ems
                    
#                     after_text = after_text.replace("'", "\\'")
#                     text = f"{before_text}{prefix}^returnText('{after_text}','')^{suffix}"
                    
#                 elif "online" in text_lower:
#                     online_index = text_lower.find("online")
#                     before_text = text[:online_index]
#                     after_text = text[online_index:].strip()
                    
#                     # Clean up text
#                     after_text = re.sub(r'(?i)online\s*:?', '', after_text, 1)
#                     after_text = re.sub(r'(?i)only\s*:?', '', after_text).strip()
                    
#                     # Close formatting tags before returnText if needed
#                     open_strongs = before_text.count('<strong>') - before_text.count('</strong>')
#                     open_ems = before_text.count('<em>') - before_text.count('</em>')
#                     prefix = ''
#                     suffix = ''
#                     if open_strongs > 0:
#                         prefix = '</strong>' * open_strongs
#                         suffix = '<strong>' * open_strongs
#                     if open_ems > 0:
#                         prefix = '</em>' * open_ems + prefix
#                         suffix = suffix + '<em>' * open_ems
                    
#                     after_text = after_text.replace("'", "\\'")
#                     text = f"{before_text}{prefix}^returnText('','{after_text}')^{suffix}"

#                 elif "sms" in bracket_lower:
#                     online_index = bracket_lower.find("sms")
#                     before_text = bracket_content[:online_index]
#                     after_text = bracket_content[online_index:].strip()
                    
#                     # Clean up text
#                     after_text = re.sub(r'(?i)sms\s*:?', '', after_text, 1)
#                     after_text = re.sub(r'(?i)only\s*:?', '', after_text).strip()
                    
#                     # Close formatting tags before returnText if needed
#                     open_strongs = before_text.count('<strong>') - before_text.count('</strong>')
#                     open_ems = before_text.count('<em>') - before_text.count('</em>')
#                     prefix = ''
#                     suffix = ''
#                     if open_strongs > 0:
#                         prefix = '</strong>' * open_strongs
#                         suffix = '<strong>' * open_strongs
#                     if open_ems > 0:
#                         prefix = '</em>' * open_ems + prefix
#                         suffix = suffix + '<em>' * open_ems
                    
#                     after_text = after_text.replace("'", "\\'")
#                     text = f"{before_bracket}[{prefix}^returnText('','{after_text}')^{suffix}]{after_bracket}"
                    
#         except Exception as e:
#             print(f"Error processing phone/online text: {str(e)}")

#     else:
#         text=clean_return_text(text)
#         return text
    
#     text=clean_return_text(text)
#     return text




def clean_text(text):
    """Remove unwanted characters like colons and extra spaces, but keep parentheses."""
    if not text:
        return text
    return text.replace(':', '').strip()

def balance_brackets(text):
    """Remove unmatched parentheses from the text."""
    if not text:
        return text
    open_count = 0
    result = []
    for char in text:
        if char == '(':
            open_count += 1
            result.append(char)
        elif char == ')':
            if open_count > 0:
                open_count -= 1
                result.append(char)
            # Skip if no matching opening bracket
        else:
            result.append(char)
    # Remove any remaining unmatched opening brackets from the end
    while open_count > 0 and result[-1] == '(':
        result.pop()
        open_count -= 1
    return ''.join(result)

def remove_leading_paren_before_return(text):
    """Remove any '(' immediately preceding '^returnText' in the final output."""
    # Use regex to find '(' followed by '^returnText' and replace with just '^returnText'
    cleaned_text = re.sub(r'\(\s*\^returnText', '^returnText', text)
    return cleaned_text

def process_text(model, text, question_type):
    if not text:
        return text
    
    phone=phone_classification(model, text)
    output=phone.get("phone",True)

    print("the output for the Phone text is ", phone , "and the input text was : ", text)

    if output :
        # Define keyword lists
        phone_keywords = ['(phone only)(landline sample)', '[PHONE ONLY][FOLLOW UP]',"[PHONE ONLY] (PROMPT)","[PHONE ONLY] [PROMPT] ",  '[PHONE ONLY]', 
                        '[PHONE]', 'phone only', 'landline sample', 'phone']
        online_keywords = ['(CELL SAMPLE AND SMS)', 'online only', 'sms only', 'web only', 
                        'online', 'sms', 'web']
        
        # Define delete list
        delete_list = ["(ONLY IF SKIPPED)"]
        
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Initialize result and current position
        result = []
        pos = 0
        
        while pos < len(text):
            # Find the next occurrence of any keyword from current position
            phone_idx = -1
            online_idx = -1
            phone_kw = ''
            online_kw = ''
            
            # Find phone keyword
            for kw in phone_keywords:
                idx = text_lower.find(kw.lower(), pos)
                if idx != -1 and (phone_idx == -1 or idx < phone_idx):
                    phone_idx = idx
                    phone_kw = kw
            
            # Find online keyword
            for kw in online_keywords:
                idx = text_lower.find(kw.lower(), pos)
                if idx != -1 and (online_idx == -1 or idx < online_idx):
                    online_idx = idx
                    online_kw = kw
            
            # If no more keywords are found, append remaining text and break
            if phone_idx == -1 and online_idx == -1:
                result.append(text[pos:])
                break
            
            # Determine the next keyword to process
            if phone_idx != -1 and (online_idx == -1 or phone_idx < online_idx):
                # Phone keyword comes first
                before_text = text[pos:phone_idx]  # Capture text before the phone keyword
                if before_text:
                    result.append(before_text)
                start = phone_idx + len(phone_kw)
                # Skip any extra whitespace after the keyword
                while start < len(text) and text[start].isspace():
                    start += 1
                if online_idx != -1 and online_idx > phone_idx:
                    # Online keyword follows, split the text
                    phone_text = balance_brackets(clean_text(text[start:online_idx]))
                    online_start = online_idx + len(online_kw)
                    # Skip any extra whitespace after the online keyword
                    while online_start < len(text) and text[online_start].isspace():
                        online_start += 1
                    # Look ahead for the next phone keyword to limit online_text
                    next_phone_idx = -1
                    for kw in phone_keywords:
                        idx = text_lower.find(kw.lower(), online_start)
                        if idx != -1 and (next_phone_idx == -1 or idx < next_phone_idx):
                            next_phone_idx = idx
                    if next_phone_idx != -1:
                        online_text = balance_brackets(clean_text(text[online_start:next_phone_idx]))
                        pos = next_phone_idx
                    else:
                        online_text = balance_brackets(clean_text(text[online_start:]))
                        pos = len(text)
                else:
                    # No online keyword, phone text goes until the next keyword or end
                    next_keyword_idx = -1
                    for kw in phone_keywords + online_keywords:
                        idx = text_lower.find(kw.lower(), start)
                        if idx != -1 and (next_keyword_idx == -1 or idx < next_keyword_idx):
                            next_keyword_idx = idx
                    if next_keyword_idx != -1:
                        phone_text = balance_brackets(clean_text(text[start:next_keyword_idx]))
                        pos = next_keyword_idx
                    else:
                        phone_text = balance_brackets(clean_text(text[start:]))
                        pos = len(text)
                    online_text = ''
            elif online_idx != -1:
                # Online keyword comes first
                before_text = text[pos:online_idx]  # Capture text before the online keyword
                if before_text:
                    result.append(before_text)
                online_start = online_idx + len(online_kw)
                # Skip any extra whitespace after the keyword
                while online_start < len(text) and text[online_start].isspace():
                    online_start += 1
                # Look ahead for the next keyword to limit online_text
                next_keyword_idx = -1
                for kw in phone_keywords + online_keywords:
                    idx = text_lower.find(kw.lower(), online_start)
                    if idx != -1 and (next_keyword_idx == -1 or idx < next_keyword_idx):
                        next_keyword_idx = idx
                if next_keyword_idx != -1:
                    online_text = balance_brackets(clean_text(text[online_start:next_keyword_idx]))
                    pos = next_keyword_idx
                else:
                    online_text = balance_brackets(clean_text(text[online_start:]))
                    pos = len(text)
                phone_text = ''
            
            # Remove items from delete_list
            for item in delete_list:
                phone_text = phone_text.replace(item, '')
                online_text = online_text.replace(item, '')
            phone_text = clean_text(phone_text)
            online_text = clean_text(online_text)
            
            # Append the returnText call
            result.append(f"^returnText('{phone_text}','{online_text}')^")
        
        final_result = ''.join(result)
        return remove_leading_paren_before_return(final_result)
    
    else:
        return text
    
    