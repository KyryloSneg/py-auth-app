from services.pymongo_get_database import get_database
from utils.form_line_edits_enum import FormLineEdit

import bcrypt


database = get_database()


def register(name, surname, phone, email, password):
    # i am lazy to make double validation check on the "server" side of the project
    users = database["users"]
    user_adresses = database["user_addresses"]
  
    email_candidate = user_adresses.find_one({ "email": email })    
    phone_candidate = user_adresses.find_one({ "phone_number": phone })
    
    error_obj = {}
    
    if email_candidate:
        error_obj[FormLineEdit.email.value] = "Such an email already exists"
      
    if phone_candidate:
        error_obj[FormLineEdit.phone.value] = "Such a phone already exists"
    
    if len(error_obj.keys()):
        return { "success": False, "data": error_obj } 

    salt = bcrypt.gensalt() 
    hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    
    inserted_user = users.insert_one({ "name": name, "surname": surname, "password": hash, "isActivated": False })
    inserted_user_address = user_adresses.insert_one({ "user_id": inserted_user.inserted_id, "email": email, "phone_number": phone })
    
    user = users.find_one(inserted_user.inserted_id)
    user_address = user_adresses.find_one(inserted_user_address.inserted_id)
    
    return { "success": True, "data": { "user": user, "user_address": user_address } }


def login(address, password, address_type = None):  
    users = database["users"]
    user_addresses = database["user_addresses"]
    
    email_candidate = user_addresses.find_one({ "email": address })    
    phone_candidate = user_addresses.find_one({ "phone_number": address })
  
    error_obj = {}
    
    if not email_candidate and not phone_candidate:
        if address_type == "phone":
            error_obj[FormLineEdit.phone.value] = "User with such a phone does not exist"
        elif address_type == "email":
            error_obj[FormLineEdit.email.value] = "User with such an email does not exist"
            
        return { "success": False, "data": error_obj }
      
    
    user_address = email_candidate
    if not email_candidate:
        user_address = phone_candidate
    
    user = users.find_one(user_address["user_id"])
    is_pass_equal = bcrypt.checkpw(password.encode("utf-8"), user["password"]) 
    
    if not is_pass_equal:
        error_obj[FormLineEdit.password.value] = "Incorrect password"
        return { "success": False, "data": error_obj }
    
    return { "success": True, "data": { "user": user, "user_address": user_address } }
