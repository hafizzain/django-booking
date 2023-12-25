
# Short the UUID field Method
def short_uuid(self, uuid):
    uuid = str(uuid).replace('-','')[:6]
    return uuid