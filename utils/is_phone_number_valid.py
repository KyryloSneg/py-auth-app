import phonenumbers


def is_phone_number_valid(number, region = None):
    try:
      parsed_phone_number = phonenumbers.parse(number, region)
      return phonenumbers.is_valid_number(parsed_phone_number)
    except:
      return False
