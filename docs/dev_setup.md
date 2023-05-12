#  Dev Setup

## Contributing

We welcome contributions from everyone.

## Required Tools

* [Git](http://git-scm.com/)
* [Python 3.11.3](https://www.python.org/downloads/)
* [docker](https://www.docker.com/)

## Recommended Tools

* [PyCharm](http://www.jetbrains.com/pycharm/) - Python IDE
* [Virtualenv](http://www.virtualenv.org/en/latest/) - Python virtual environment
* [asdf](https://asdf-vm.com/) - Version manager for multiple languages

## Setup

This tutorial assumes you have already installed all the required and recommended tools. You can adapt this tutorial to your own environment at your own risk.

1. Make sure you have the correct version of Python installed

    ```bash
    python --version
    ```

   If you don't have the correct version, you can install it using [asdf](https://asdf-vm.com/).

    ```bash
    asdf plugin add python
    asdf install python 3.11.3
    ```

2. Clone the repository

    ```bash
    git clone https://github.com/BRUTEUdesc/SiteColoquios
    cd SiteColoquios
    ```

3. Create and activate virtual environment

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ``` 

4. Install dependencies

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
   
5. Populate the .env file

    ```bash
    cp .env.example .env
    ```

    You can use the default values for development or Customize the .env file to your needs. Remember to update the .env.template when you add new environment variables.

6. Start the database

    ```bash
    docker-compose up -d
    flask db-create
    flask db-init
    ```
   
7. Run the application

    ```bash
    flask run
    ```
   
# Troubleshooting

Contact us on [Discord](https://discord.gg/8qZ2Y8Z) or [Telegram](https://t.me/bruteudesc) if you have any problems.
