from linkedin_api import Linkedin
import json

email = "igormalyga@gmail.com"
password = "funforweb2016"

api = Linkedin(email, password)

result = api.search_people(
     start=0,
     limit=15,
     keywords="python"
)

#result = api.get_profile('kirillstyopkin')

print(json.dumps(result, indent=4))
