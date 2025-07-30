import os

os.environ['API_KEY'] = "NjRkZjI4NTYwMjMzNmMwYjIyOWY4OWRlLDEwMDAsMTcxNzA4MTkzNjM3Mg=="
os.environ['GEMINI_SERVER_HOST'] = 'https://dev-ai-api.betteryeah.com'
os.environ['RUN_ENV'] = 'BETTERYEAH_SDK'


def get_betteryeah():
    from betteryeah import BetterYeah
    better_yeah = BetterYeah(api_key=os.environ['API_KEY'])
    return better_yeah


if __name__ == "__main__":
    get_betteryeah()
