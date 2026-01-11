# user-search

A single-script OSINT tool for finding various social media accounts based on usernames.

![](./readme_assets/example1.png)

> This project is 100% sentient-made. No LLMs are used and will never be used in this project, for code or otherwise.

## Requirements

**Tested with Python 3.12.3 on Linux Mint 22.2 "Zara".**

### Python modules required:
```
requests
sys
argparse
re
urllib
string
colorama
bs4
```

## Usage
The usage is fairly simple as of now. It just has one required argument, `-u`, which is the input username to search for.
```
python3 user-search.py -u USERNAME
```

If you want to have the script scrape additional information (this feature is not implemented for many sites yet, but will be eventually), you can add the `--getInfo` flag.

```
python3 user-search.py -u USERNAME --getInfo
```

If the script prints something like `An error has occured with the site. Info: 403`, this is normal. It is just telling you that an unexpected response was received. I reccomend investigating what might have caused the error, and if you think that it is an issue with the script, a pull request for a fix would be great.

> Note that depending on your username search query, certian sites may be excluded from your search. An example would be itch.io usernames not being able to contain the period character, and therefore if I supplied the username argument `bob.joe`, the script would tell me that because of this it cannot search itch.io.

## Supported Sites

* Soundcloud
* Reddit
* Patreon
* Steam (By account ID)
* GitHub [Account Links, Popular Repositories]
* Snapchat
* Instagram
* YouTube
* itch.io
* Twitter
* Discord (By username, not Display name)
* Bluesky (only searches `USERNAME` .bsky.social)

> ALL supported sites can be assumed to have a basic "if account by input username exists" check. This is the only check that will happen if you run the script without the `--getInfo` flag. Additional information that can be gathered with `--getInfo` will be listed in brackets. Any clarifications to what the tool searches for will be in parenthases.



## Contributing
All contributions are welcome and greatly appreciated, pull request as you like. The most helpful contributions would be adding more social media sites to the tool, or primarily adding more scraping functionality to the `--getInfo` system (sorely needed, as I have less time these days to work on it).

If you are not capable of or do not want to fix an error you find, please make an issue in the repo.

> Note that any LLM generated code is not allowed and will be rejected.
