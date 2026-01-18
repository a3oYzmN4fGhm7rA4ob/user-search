# Script for finding if a username exists across various websites.
# Features will soon be implemented to conduct additional OSINT if the proper flags are set.

import sys, requests, argparse, re, urllib, string
from colorama import *
from bs4 import *

defaultHeaders_1={
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Upgrade-Insecure-Requests": "1",
    }

def parseArgs():
    parser = argparse.ArgumentParser(description='Script for finding if a username exists across various websites.',usage='(python3) userDetector.py -u USERNAME')
    parser.add_argument('-u', required=True, help='Username input to search for.')
    
    # Nothing uses this right now, just leaving it here for eventual functionality perhaps.
    #parser.add_argument('-h', required=False, help='For sites that also require a homeserver or something like that, you can input one. If you don\'t, those sites will not be scanned.')

    # Eventual argument I will add for more extensive data gathering support
    parser.add_argument('--getInfo', action='store_true', help='If this flag is set, where applicable the script will attempt to grab additional information about a user from that profile.')
    args = parser.parse_args()
    return args

# This function prints the results of other search functions to display to the user
def printResult(site, username, stat, code):
    if stat == 1:
        # If user exists
        print(Fore.BLUE + f"\n{site}:" + Fore.GREEN + f"\nUser {username} exists!" + Fore.WHITE)
    if stat == 0:
        # If user does not exist
        print(Fore.BLUE + f"\n{site}:" + Fore.RED + f"\nUser {username} does not exist." + Fore.WHITE)
    if stat == 2:
        # If an unexpected response is recieved
        print(Fore.BLUE + f"\n{site}:" + Fore.YELLOW + f"\nAn error has occured with the site. Info: {code}" + Fore.WHITE)

# Print an additional information string
def printInformation(username, string, infoType):
   print(Fore.CYAN + f"Information about user {username} ({infoType}): " + Fore.MAGENTA + f"{string}" + Fore.WHITE)

# Search for a user directly, some sites will just let you do this by looking for a user page directly.
def searchForUserWithDirectURL(site, username, headers, foundCode, failCode, outputSite):
    # Failcode is usually 404 (user does not exist). Success code is usually 200.

    url = f"https://{site}{username}"

    req = requests.get(url, headers=headers)

    if req.status_code == failCode: # If user is not found
        printResult(outputSite, username, 0, req.status_code)
        return False
    elif req.status_code == foundCode: # If user is found
        printResult(outputSite, username, 1, req.status_code)
        return True
    else: # If neither, an error has occured
        printResult(outputSite, username, 2, req.status_code)
        return False

# Search for a username wherein the site will always return 200, but you can still search the string for a specific message to detect a fail or not
def searchForUserWithFindIn(site, username, headers, failString, outputSite):

    url = f"https://{site}{username}"

    req = requests.get(url, headers=headers)

    if req.status_code == 200:
        if failString in req.text: # If user is not found
            printResult(outputSite, username, 0, req.status_code) 
            return False
        else: # If user is found
            printResult(outputSite, username, 1, req.status_code) 
            return True
    else: # If neither, an error has occured
        printResult(outputSite, username, 2, req.status_code) 
        return False

# Search for a username where the site will always return 200, but with regex on the response
def searchForUserWithRegex(site, username, headers, failDetectionPattern, outputSite):

    url = f"https://{site}{username}"

    req = requests.get(url, headers=headers)

    if req.status_code == 200: # If site returns it exists
        if re.search(failDetectionPattern, req.text): # Use regex to search for a string that would indicate failure
            printResult(outputSite, username, 0, req.status_code)
            return False
        else: # If user does exist
            printResult(outputSite, username, 1, req.status_code)
            return True
    else: # If neither or site returns unexpected response
        printResult(outputSite, username, 2, req.status_code)
        return False


def main():
    print(Fore.GREEN + "\n-- a3's username scanner tool thingy --\n" + Fore.WHITE)
    args = parseArgs()

    # ---------------------------------------------------------------
    # All searches that are easily made with normal functions and should be done here

    # Soundcloud
    try:
        result = searchForUserWithDirectURL("soundcloud.com/", args.u, {}, 200, 404, "Soundcloud")
    except(ConnectionError, requests.ConnectionError, requests.ConnectTimeout):
        printResult("Soundcloud", args.u, 2, "ConnectionError")
        
    # Reddit
    result = searchForUserWithFindIn("reddit.com/u/", args.u, defaultHeaders_1, "Sorry, nobody on Reddit goes by that name.", "Reddit")

    # Telegram (functionality currently BROKEN. awaiting better user enumeration method.)
    # searchForUserWithRegex("t.me/", args.u, {}, r'<div[^>]*class="tgme_page_extra"[^>]*>', "Telegram")

    # Patreon
    result = searchForUserWithDirectURL("www.patreon.com/", args.u, {}, 200, 404, "Patreon")

    # Steam
    result = searchForUserWithFindIn("www.steamcommunity.com/id/", args.u, {}, "Error</title>", "Steam")

    # GitHub
    if (args.u).isalnum() is True:
        result = searchForUserWithDirectURL("github.com/", args.u, {}, 200, 404, "GitHub")
        
        # Adding additional info gathering here via bs4
        if result == True and args.getInfo == True: # Collect more information about user and print it
            req = requests.get(f"https://github.com/{args.u}")
            soup = BeautifulSoup(req.content, 'html.parser')

            # Scrape account links from GitHub
            scrapedContent = soup.find_all('a', class_='Link--primary wb-break-all')
            if scrapedContent != None:
                for item in scrapedContent:
                        printInformation(args.u, re.sub(r"\s", "", item.get('href')), "Account Link In Bio")
            else:
                printInformation(args.u, None, "Link In Bio")

            scrapedContent = soup.find_all('span', class_='repo')
            if scrapedContent:
            
                for item in scrapedContent:
                    printInformation(args.u, re.sub(r"\s", "", item.get_text()), "Popular Repo")
            else:
                printInformation(args.u, None, "Popular Repo")
    else:
        print(Fore.BLUE + "GitHub:" + Fore.YELLOW + "\nCannot search GitHub, as username has an invalid/illegal character in it that would mess up how links to profiles are parsed." + Fore.WHITE)
        
    # Snapchat
    headers = {'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'sec-ch-ua': "\"Google Chrome\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
        'sec-ch-ua-mobile': "?1",
        'sec-ch-ua-platform': "\"Android\"",
        'upgrade-insecure-requests': "1",
        'sec-fetch-site': "none",
        'sec-fetch-mode': "navigate",
        'sec-fetch-user': "?1",
        'sec-fetch-dest': "document",
        'accept-language': "en-US,en;q=0.9",
        'priority': "u=0, i"}

    result = searchForUserWithDirectURL("www.snapchat.com/@", args.u, headers, 200, 404, "Snapchat")    

    # Instagram
    try:
        outputSite = "Instagram"
        headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            'X-IG-App-ID': "936619743392459",
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "en-US,en;q=0.9",
            'X-Requested-With': "XMLHttpRequest",
            'Referer': f"https://www.instagram.com/{args.u}/"}

        result = searchForUserWithDirectURL("www.instagram.com/api/v1/users/web_profile_info/?username=", args.u, headers, 200, 404, "Instagram")
    except(ConnectionError, requests.ConnectionError, requests.RequestException):
        printResult(outputSite, args.u, 2, "ConnectionError")

    # Youtube
    headers = {'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'device-memory': "4",
        'sec-ch-ua': "\"Google Chrome\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
        'sec-ch-ua-mobile': "?1",
        'sec-ch-ua-full-version': "\"141.0.7390.111\"",
        'sec-ch-ua-arch': "\"\"",
        'sec-ch-ua-platform': "\"Android\"",
        'sec-ch-ua-platform-version': "\"15.0.0\"",
        'sec-ch-ua-bitness': "\"\"",
        'sec-ch-ua-wow64': "?0",
        'sec-ch-ua-full-version-list': "\"Google Chrome\";v=\"141.0.7390.111\", \"Not?A_Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"141.0.7390.111\"",
        'sec-ch-ua-form-factors': "\"Mobile\"",
        'upgrade-insecure-requests': "1",
        'sec-fetch-site': "none",
        'sec-fetch-mode': "navigate",
        'sec-fetch-user': "?1",
        'sec-fetch-dest': "document",
        'accept-language': "en-US,en;q=0.9",
        'priority': "u=0, i"}

    result = searchForUserWithDirectURL("m.youtube.com/@", args.u, headers, 200, 404, "Youtube")

    # ---------------------------------------------------------------
    # Custom requests that don't work with the normal functions

    # itch.io
    if (args.u).isalnum() is True:
        url = f"https://{args.u}.itch.io/"
        req = requests.get(url)
        outputSite = "itch.io"
        if req.status_code == 200:
            printResult(outputSite, args.u, 1, req.status_code)
        elif req.status_code == 404:
            printResult(outputSite, args.u, 0, req.status_code)
        else:
            printResult(outputSite, args.u, 2, req.status_code)
    else:
        print(Fore.BLUE + "\nitch.io:" + Fore.YELLOW + "\nCannot search itch.io, as username has an invalid character in it that would mess up how itch.io profiles are parsed." + Fore.WHITE)
    
    # Twitter
    url = "https://api.twitter.com/i/users/username_available.json"
    outputSite = "Twitter"

    parameters = {"username": args.u,
        "full_name": "V1",
        "email": "mankindisdeadbloodisfuelhellisfull@ultrakill.com"}

    headers = {"Authority": "api.twitter.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    
    try:
        req = requests.get(url, params=parameters, headers=headers, timeout=5.0)
        if req.status_code in [401, 403, 429, 500]:
            printResult(outputSite, args.u, 2, req.status_code)
        elif req.status_code == 200:
            data = req.json()
            if data.get('reason') == 'improper_format' or data.get('reason') == 'invalid_username' or data.get('reason') == 'is_banned_word':
                    printResult(outputSite, args.u, 2, f"Unexpected JSON error! {data}")
            elif data.get('reason') == 'taken':
                printResult(outputSite, args.u, 1, req.status_code)
            elif data.get('valid') is True:
                printResult(outputSite, args.u, 0, req.status_code)
            else:
                printResult(outputSite, args.u, 2, f"Unexpected JSON error! {data}")
        else:
            printResult(outputSite, args.u, 2, req.status_code)
       
    except(ConnectionError, requests.ConnectionError):
        printResult(outputSite, args.u, 2, req.status_code)

    # Discord
    url = "https://discord.com/api/v9/unique-username/username-attempt-unauthed"

    headers = {"authority": "discord.com",
        "accept": "/",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "origin": "https://discord.com",
        "referer": "https://discord.com/register"}

    parameters = {"username": args.u}

    try:
        req = requests.post(url, headers=headers, json=parameters, timeout=5.0)
        if req.status_code == 200:
            data = req.json()
            if data.get("taken") is True:
                printResult("Discord", args.u, 1, req.status_code)
            elif data.get("taken") is False:
                printResult("Discord", args.u, 0, req.status_code)
            else:
                printResult("Discord", args.u, 2, f"Unexpected JSON error! {data}")
        elif req.status_code == 400:
            printResult("Discord", args.u, 2, "HTTP 400 error has occured, indicating a bad request. Perhaps the username contains invalid characters?")
        
        else:
            printResult("Discord", args.u, 2, req.status_code)

    except(requests.ConnectionError, ConnectionError):
        printResult("Discord", args.u, 2, "ConnectionError")

    # Bluesky (only searches .bsky.social)
    if (args.u).isalnum() is True:
        handle = f"{args.u}.bsky.social"

        url = "https://bsky.social/xrpc/com.atproto.temp.checkHandleAvailability"

        headers = {'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
            'Accept-Encoding': "gzip",
            'atproto-accept-labelers': "did:plc:ar7c4by46qjdydhdevvrndac;redact",
            'sec-ch-ua-platform': "\"Android\"",
            'sec-ch-ua': "\"Google Chrome\";v=\"141\", \"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"141\"",
            'sec-ch-ua-mobile': "?1",
            'origin': "https://bsky.app",
            'sec-fetch-site': "cross-site",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://bsky.app/",
            'accept-language': "en-US,en;q=0.9"}
        
        parameters = {'handle':handle}

        req = requests.get(url, params=parameters, headers=headers, timeout=5.0)

        data = req.json()

        if req.status_code == 200:
            if 'com.atproto.temp.checkHandleAvailability#resultUnavailable' in req.text:
                printResult("Bluesky (.bsky.social)", handle, 1, req.status_code)
            elif 'com.atproto.temp.checkHandleAvailability#resultAvailable' in req.text:
                printResult("Bluesky (.bsky.social)", handle, 0, req.status_code)
            else:
                printResult("Bluesky (.bluesky.social)", handle, 2, req.status_code)

        elif req.status_code == 400 and 'handle must be a valid handle' not in req.text:
            printResult("Bluesky (.bsky.social)", handle, 2, f"HTTP 400 error has occured, indicating a bad request. Perhaps the username contains invalid characters? {data}")
        else:
            printResult("Bluesky (.bsky.social)", handle, 2, f"An unexpected error occured. Status {req.status_code}.")
    else:
        print(Fore.BLUE + "\nBluesky (.bsky.social)" + Fore.YELLOW + "\nCannot search Bluesky (.bsky.social), as username has an invalid character." + Fore.WHITE)

main()