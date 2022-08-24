# ooen-downloader

[![Build](https://github.com/franznemeth/ooen-downloader/actions/workflows/main.yaml/badge.svg?branch=main)](https://github.com/franznemeth/ooen-downloader/actions/workflows/main.yaml)
[![GitHub license](https://img.shields.io/github/license/franznemeth/ooen-downloader?style=flat-square)](https://github.com/franznemeth/ooen-downloader/blob/main/LICENSE)

Automatic downloader for Oberösterreichische Nachrichten Epaper Newspaper.

## Introduction
This application uses selenium to download the daily issue of [OÖNachrichten](https://www.nachrichten.at).
The ooen-downloader automatically logs in and downloads every edition and saves it locally.
It requires and [active subscription](https://shop.nachrichten.at/shop/) of OÖN.

## Requirements

- python 3.9
- pip
- Selenium python bindings
- firefox web browser
- geckodriver for selenium https://github.com/mozilla/geckodriver/releases

## Usage

You can run this script manually if you have all requirements present on your system or just run the container.

It supports the following environment variables as configuration:

| Variable          | Description                                                                                                                        | Type | Default   |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------|------|-----------|
| OOEN_DOWNLOAD_DIR | Directory to download the newspaper pdfs to                                                                                        | str  | /download |
| OOEN_USERNAME     | E-Mail or username of your subscription (NOTE: I did not test this with OIDC or Google Login                                       | str  | None      |
| OOEN_PASSWORD     | Password of your subscription                                                                                                      | str  | None      |
| DEBUG             | If this variable is set to True it will display additional output and disable headless mode for the browser for debugging purposes | bool | False     |

To run this locally install the prerequisites mentioned above and run `pip install -r requirements.txt`.
Then you just have to set the environment variables and run `python3 ./main.py`.

To run this in a container you can get started using the following command:
```bash
podman run -it --rm \
  -v `pwd`/ooen:/download \
  -e OOEN_USERNAME=<username or email> \
  -e OOEN_PASSWORD=<password> \ 
  --name ooen-downloader \
  ghcr.io/franznemeth/ooen-downloader:v0.0.2
```

If you want to run this as a scheduled job in kubernetes see the examples in `/deploy/kubernetes`.
