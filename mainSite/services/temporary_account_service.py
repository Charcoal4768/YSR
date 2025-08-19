from mainSite.models import User

def make_temp_account(data):
    user = User(
        email=data.get("email"),
        username=data.get("name"),
        # Set other user fields as needed
    )
    return user