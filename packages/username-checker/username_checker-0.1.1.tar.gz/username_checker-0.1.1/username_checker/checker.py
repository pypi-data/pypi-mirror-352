import requests
from colorama import Fore, Style, init

init(autoreset=True)

def check_username(username):
    sites = {
        "GitHub": f"https://github.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "Facebook": f"https://www.facebook.com/{username}",
        "YouTube (Channel)": f"https://www.youtube.com/@{username}",
        "PythonAnywhere": f"https://www.pythonanywhere.com/user/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Telegram": f"https://t.me/{username}"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    for site, url in sites.items():
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"[{Fore.GREEN}+{Style.RESET_ALL}] {Fore.GREEN}{site}{Style.RESET_ALL} : {url}")
            elif response.status_code == 404:
                print(Fore.RED + f"[-] {site}" + Style.RESET_ALL)
            else:
                print(f"[{Fore.YELLOW}?{Style.RESET_ALL}] {Fore.GREEN}{site}{Style.RESET_ALL} da noma'lum holat: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[{Fore.MAGENTA}!{Style.RESET_ALL}] {Fore.GREEN}{site}{Style.RESET_ALL} uchun xatolik: {e}")

def main():
    username = input(Fore.GREEN + 'Ushbu kutubxona @muhamadyorg tomonidan yaratildi\nUsername kiriting: ' + Style.RESET_ALL)
    print(f'username {Fore.GREEN}{username}{Style.RESET_ALL} boyicha natijalar:\n')
    check_username(username)
