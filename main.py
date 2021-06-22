from app import DiscordClient

if __name__ == "__main__":
    client = DiscordClient.DiscordClient()
    client.run(client.TOKEN)