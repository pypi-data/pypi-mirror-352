import requests
import copy

DEFAULT_JSON = {
    "username": "Webhook",
    "avatar_url": "",
    "content": "",
    "embeds": []
}

DEFAULT_FOOTER = {
    "text": "",
    "icon_url": ""
}

DEFAULT_THUMBNAIL = {
    "url": ""
}

DEFAULT_FIELD = {
    "name": "",
    "value": "",
    "inline": True
}

DEFAULT_EMBED = {
      "title": "",
      "description": "",
      "color": 0
    }

colors = {
    "red": 0xFF0000,
    "green": 0x00FF00,
    "blue": 0x0000FF,
    "yellow": 0xFFFF00,
    "orange": 0xFFA500,
    "purple": 0x800080,
    "cyan": 0x00FFFF,
    "pink": 0xFFC0CB,
    "gray": 0xD3D3D3,
    "black": 0x000000,
    "white": 0xFFFFFF
}

class Embed():
    def __init__(self, title: str, description: str, color: int | str = None):
        self.title = title
        self.description = description
        self.color = color
        self.fields: list[dict[str, str]] = []
        self.footer = None
        self.thumbnail = None

        if color != None:
            if color in colors.keys():
                self.color = colors[color]
            else:
                try:
                    self.color = int(color)
                except ValueError:
                    raise ValueError("Invalid parameter : color must be a str (red, blue, yellow...) or an decimal (16776960, 65280, 16711680...)")
            
    def set_thumbnail(self, icon_url: str) -> None:
        self.thumbnail        = copy.deepcopy(DEFAULT_THUMBNAIL)
        self.thumbnail["url"] = icon_url

    def set_footer(self, text: str, icon_url: str = None) -> None:  
        self.footer             = copy.deepcopy(DEFAULT_FOOTER)      
        self.footer["text"]     = text
        self.footer["icon_url"] = icon_url if icon_url != None else ""

    def add_field(self, name: str, content: str = None, inline: bool = True) -> None:
        field            = copy.deepcopy(DEFAULT_FIELD)

        field["name"]    = name
        field["content"] = content if content != None else ""
        field["inline"]  = inline

        self.fields.append(field)

class Webhook():
    def __init__(self, url):
        self.url = url

    def send(self, message: str = None, embed: Embed = None, username: str = None, avatar_url: str = None) -> None:
        url = self.url

        json = copy.deepcopy(DEFAULT_JSON)
        embed_dict = copy.deepcopy(DEFAULT_EMBED)

        if embed != None:
            embed_dict["title"]       = embed.title
            embed_dict["description"] = embed.description
            embed_dict["color"]       = embed.color if embed.color != None else 0
 
            if embed.footer   != None:
                embed_dict["footer"]      = embed.footer
            if embed.fields   !=   []:
                embed_dict["fields"]      = embed.fields
            if embed.thumbnail != None:
                embed_dict["thumbnail"]    = embed.thumbnail

        json["username"]   = username        if username   != None else "Python Webhook"
        json["content"]    = message         if message    != None else ""
        json["embeds"]     = [embed_dict]    if embed      != None else []
        json["avatar_url"] = avatar_url      if avatar_url != None else ""        

        if embed == None and message == None:
            raise "No such embed or message"
            return

        try:
            rsp = requests.post(url, json=json)

            if rsp.status_code == 419:
                raise requests.RequestException(f"Your are being rate limited ! {f'Please retry after {rsp.json().get("retry_after", None) if rsp.json().get("retry_after", None) != None else "--"} seconds.'}")
            elif rsp.status_code == 404:
                raise requests.RequestException("Invalid webhook url")
            elif rsp.status_code == 400:
                print(json, "\n\n\n\n\n")
                print(rsp.json(), "\n\n\n\n\n")
                raise requests.RequestException("Invalid datas")
        except Exception as e:
            raise Exception(f"An error occured while sending the message : {e}")

    def delete(self) -> None:
        try:
            rsp = requests.delete(self.url)

            if rsp.status_code == 404:
                raise Exception("Invalid webhook")
            elif rsp.status_code == 419:
                raise requests.RequestException(f"Your are being rate limited ! {f'Please retry after {rsp.json().get("retry_after", None) if rsp.json().get("retry_after", None) != None else "--"} seconds.'}")
        except Exception as e:
            raise requests.RequestException(f"Couldn't delete the webhook : {e}")
        
    def is_valid(self) -> bool:
        try:
            rsp = requests.get(self.url)
            return False if rsp.status_code != 200 else True
        
        except Exception as e:
            raise Exception(f"An error occured while checking the webhook : {e}")
        
__all__ = ["Webhook", "Embed"]