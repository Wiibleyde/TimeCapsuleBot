# TimeCapsuleBot

![GitHub license](https://img.shields.io/github/license/Wiibleyde/TimeCapsuleBot) ![GitHub issues](https://img.shields.io/github/issues/Wiibleyde/TimeCapsuleBot) ![GitHub last commit](https://img.shields.io/github/last-commit/Wiibleyde/TimeCapsuleBot) ![GitHub repo size](https://img.shields.io/github/repo-size/Wiibleyde/TimeCapsuleBot) ![GitHub top language](https://img.shields.io/github/languages/top/Wiibleyde/TimeCapsuleBot) ![GitHub All Releases](https://img.shields.io/github/downloads/Wiibleyde/TimeCapsuleBot/total)

A Discord bot that allows you to make time capsules on a Discord server.

## Setup

1. Clone the repository
2. Create a file called `config.yml` in the root directory of the repository
3. Add the following to the file:
```yaml
Bot_token: bot token
Capsule_channel: capsule reveal channel id
```	
4. Run the docker container :
```bash
docker-compose up -d
```
5. Invite the bot to your server

## Usage

### Commands

#### `/setcapsulechannel`

Sets the channel where the bot will post the time capsules.

#### `/ajouter`

Adds a new time capsule to the server.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)

## Authors

- [**Wiibleyde**](https://github.com/Wiibleyde)