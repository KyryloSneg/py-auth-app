from services.send_email import send_email


def send_account_activation_message(email, activation_code):
    # 999999 => 999 999
    splitted_activation_code = f"{activation_code[0:3]} {activation_code[3:6]}"    
    result = send_email(email, "Account activation", f"Your activation code: {splitted_activation_code}")
    
    return result