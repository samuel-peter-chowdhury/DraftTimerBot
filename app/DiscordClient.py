import asyncio
import os
from datetime import timedelta, time
import discord
from dotenv import load_dotenv


class Coach:
	def __init__(self, name, timer):
		self.name = name
		self.timer = timer

class DiscordClient(discord.Client):
	def __init__(self, **options):
		super().__init__(**options)
		load_dotenv()
		self.TOKEN = os.getenv('DISCORD_TOKEN')
		self.GUILD = os.getenv('DISCORD_GUILD')

		self.message_id = None
		self.category = 'Season 3'
		self.channel = 'draft'

	async def on_ready(self):
		guild = discord.utils.get(self.guilds, name=self.GUILD)
		print(f'{self.user} is connected to the following guild:\n{guild.name}(id: {guild.id})')

	async def on_message(self, message):
		if self.validateMessage(message):
			self.message_id = message.id
			next_coach = message.content.split('Next up is ')[1]
			await self.sendMessage(message, f'Timer has started for {next_coach}')
			await asyncio.sleep(5)
			await self.sendMessage(message, f'One hour remaining for {next_coach}')
			await asyncio.sleep(10)
			await self.sendMessage(message, f'Timer has ended for {next_coach}')

	async def sendMessage(self, message, content):
		if self.message_id == message.id:
			await message.channel.send(content)

	def validateMessage(self, message):
		return str(message.channel.category) == self.category and str(message.channel) == self.channel \
		       and message.author != self.user and 'Next up is ' in message.content

	@staticmethod
	def getDelay(start, interval):

		# Check if its past midnight and before 8:00am
		if start.time() > time(0, 0) and start.time() < time(8,0):
			# If past midnight and before 8, then the upper bound is 8am that same day
			# The lower bound is 11pm the previous day
			upper_bound = start.replace(hour=8, minute=0, second=0, microsecond=0)
			lower_bound = (start - timedelta(days=1)).replace(hour=23, minute=0, second=0, microsecond=0)
		else:
			# If not past midnight and before 8, then the upper bound is 8am the next day
			# The lower bound is 11pm the same day
			upper_bound = (start + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
			lower_bound = start.replace(hour=23, minute=0, second=0, microsecond=0)
		# If the pick was submitted during the 'dead zone' (11pm - 8am), then the interval will be
		# the allotted amount of time, plus the time it takes to reach 8am
		if start > lower_bound and start < upper_bound:
			return interval + (upper_bound - start).seconds

		else:
			# If end of the timer lands in the 'dead zone' (11pm - 8am), then the interval will be
			# the allotted amount of time plus 7 hours
			time = start + timedelta(hours=interval/3600)
			if time > lower_bound and time < upper_bound:
				return interval + (9 * 3600)
			# If the end of the timer does not land in the 'dead zone' (11pm - 8am), then the interval will be
			# the allotted amount of time
			else:
				return interval