from aixblock_core.core.utils.params import get_env
from aixblock_core.core.settings.base import NOTION_API_TOKEN

NOTION_API_HEADERS = {
    'Authorization': f'Bearer {NOTION_API_TOKEN}',
    'Notion-Version': '2022-06-28',
}
NOTION_API_URL = "https://api.notion.com/v1"

# Need token from notion cookie to access private/unpublished page
# NOTION_CLIENT_HEADER ={
#     "Cookie": "token_v2=v02%3Auser_token_or_cookies%3AC_wdRx4RcVa2SmTakhplG7cCtQv6HjN84_Z5zlW1tXPf8CBOwoGDYah5IOjhrCXk72jxlD1teuH6tur6r4QUz0y5wA6-hXEbrLN2pFMgmsz50FrQqdJq46HidqngWiuXNc-m"
# }
NOTION_CLIENT_HEADER = {}
NOTION_CLIENT_API_URL = "https://www.notion.so/api/v3"

