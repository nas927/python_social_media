import facebook
import requests

class Instagram(facebook.Facebook):
    def __init__(self):
        super().__init__()
        
    def getInstaId(self) -> tuple[str, str, str] | bool:
        page_id, access_token = self.get_page_id()
        
        if not page_id or not access_token:
            print("Quelque chose s'est mal passée veuillez retenter")
            return False
        
        uri: str = f"https://graph.facebook.com/v22.0/{page_id}"
        params: dict[str, str] = {
            "fields": "instagram_business_account",
            "access_token": access_token
        }
        
        r = requests.get(uri, params=params)
        
        if (r.status_code <= 300):
            r = r.json()
            print(r)
            if (r.get("instagram_business_account")):
                return r["instagram_business_account"]["id"], page_id, access_token
        else:
            print("Quelque chose s'est mal passée veuillez recommencer !")
            print(r.text)
            
        return False
             
    def get_attachments(self) -> tuple[str,str,str,str] | bool:
        insta_id, page_id, access_token = self.getInstaId()
        
        if not page_id or not access_token or not insta_id:
            print(self.error)
            return False
        
        uri: str = f"https://graph.facebook.com/v22.0/{page_id}/posts"
        
        params: dict[str, str] = {
            "fields": "attachments",
            "access_token": access_token
        }
    
        r = requests.get(uri, params=params)
        if r.status_code <= 300:
            r = r.json()
            if (r.get("data")):
                r = r['data'][0]["attachments"]["data"][0]["media"]["image"]["src"]
                print(r)
                return r, page_id, access_token, insta_id
        else:
            print(self.error)
            print(r.text)
        return False
    
    def upload_insta(self, message: str) -> tuple[str, str, str] | bool:
        source, page_id, access_token, insta_id = self.get_attachments()
        
        if not source or not page_id or not access_token or not insta_id:
            print(self.error)
            return False
        
        uri: str = f"https://graph.facebook.com/v22.0/{insta_id}/media"
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        data: dict[str, str] = {
            "image_url": source,
            "caption": message
        }
        
        r = requests.post(uri, headers=headers, json=data)
        
        if r.status_code <= 300:
            r = r.json()
            print(r)
            return r["id"], insta_id, access_token
        else:
            print(self.error)
            print(r.text)
        
        return False
    
    def post_insta(self, message: str):
        publication_id, insta_id, access_token = self.upload_insta(message)
        
        if not publication_id or not insta_id or not access_token:
            print(self.error)
            return False
        
        uri: str = f"https://graph.facebook.com/v22.0/{insta_id}/media_publish"
        params: dict[str, str] = {
            "creation_id": publication_id,
            "access_token": access_token
        }
        r = requests.post(uri, params=params)
        if r.status_code <= 300:
            r = r.json()
            print(r)
            if (r.get("id")):
                return r["id"]
        else:
            print(self.error)
            print(r.text)
        return False