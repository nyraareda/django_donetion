import requests

def get_fontawesome_icons():
    url = 'https://api.fontawesome.com/icons'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        icons = data.get('icons', [])
        icon_choices = [(icon['properties']['icon'], icon['label']) for icon in icons]
        return icon_choices
    return []
