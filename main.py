import discord
from message_editor import translateString
import Faction

class Cicero(discord.Client):

    #login
    async def on_ready(self):
        print(f'Ave, Caesar, morituri te salutant. Mögen euch die Götter gewogen sein.')

    #Nachrichten posten
    async def on_message(self, message, client=None):
        delivered_string = message.content.lower()
        used_string = translateString(delivered_string)

        PreSearchSet = {'hey', 'ave'}
        PostSearchSet = {'caesar', 'cicero', 'bot'}

        
        if message.author == client.user:
            return


        elif len(used_string.intersection({'!report_win'})):
            FactionList = [Faction.Faction(i) for i in range(70)]  # list with 70 fations in the columns name,wins,loses,win_rate,number_used


        elif len(used_string.intersection(PreSearchSet)) & len(used_string.intersection(PostSearchSet)):
            await message.channel.send(f'Ave Caesar')

        else:
            print(f'Nachricht von {str(message.author)} enthält  {str(message.content)}')


client = Cicero()
client.run("ODEwNDMwMDM4MDgzNjMzMTUz.YCjhyg.X0smQDY9zCaS5LBYV-dg_3S_l9c")