import discord
from discord import file
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
import youtube_dl

load_dotenv()

#Lấy Token API DISCORD
DISCORD_TOKEN = os.getenv("discord_token")

#Mucdich

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

#GetYoutubeVideoMusic
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format' : 'bestaudio/best',
    'restrictfilenames' : True,
    'noplaylist' : True,
    'ignoreerrors' : False,
    'logtostderr' : False,
    'quiet' : True,
    'no_warnings' : True,
    'default_search' : 'auto',
    #Sử dụng địa chỉ IPV4 vì IPV6 có thể dẫn tới lỗi
    'source_address' : '0.0.0.0'
}
ffmpeg_options = {
    'options' : '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume= 0.5):
        super().__init__(source, volume)
        self.data = data
        self.titles = data.get('titles')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            #Lấy video nào trong danh sách - Ở đây sẽ lấy vị trí đầu tiên
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
#Chức năng join
@bot.command(name='join', help='Yêu cầu bot tham gia vào channel.')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} đang không kết nối vào channel".format(ctx.message.author.name))
        return
    else: 
        channel = ctx.messange.author.voice.channel
    await channel.connect()
#Chức năng thoát
@bot.command(name='leave', help='Để bot rời khỏi channel.')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Bot đang không connect vào channel.")

#Chức năng play
@bot.command(name='play_song', help='Chơi bài hát')
async def play(ctx,url):
    try :
        server = ctx.message.guild
        voice_chanel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_chanel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe",source=filename))
        await ctx.send('** Đang phát: ** {}'.format(filename))
    except : 
        await ctx.send("Bot đang không được kết nối tới channel.")

@bot.command(name='pause', help='Tạm dừng bài hát')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("Hiện tại Bot đang không phát nhạc.")

@bot.command(name='resume', help=' Tiếp tục phát')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("Trước đó bot không đang phát bài hát nào. Hãy dùng play_song để bắt đầu một bài hát mới.")

@bot.command(name='stop', help='Dừng phát nhạc')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("Hiện tại Bot đang không đang phát bài hát nào.")

if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)