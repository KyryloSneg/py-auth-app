from services.pymongo_get_database import get_database


database = get_database()


def activate_account(userId):
    users = database["users"]
    users.update_one({ "_id": userId }, { "$set": { "isActivated": True } })
  