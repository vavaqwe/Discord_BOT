import discord
from pytube import YouTube , Search
import asyncio
intents = discord.Intents().all()
client = discord.Client(intents=intents)
key = "Discord_key"


voice_clients = {}
track_queue = []

ffmpeg_path = r'bin\ffmpeg.exe'
FFMPeG_CONf = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")

@client.event
async def on_message(msg):
    if msg.content.startswith("+join"):
        try:
            voice_client = await msg.author.voice.channel.connect()
            voice_clients[msg.guild.id] = voice_client
        except Exception as err:
            print(f"Error connecting to voice channel: {err}")
    if msg.content.startswith("+play"):
        try:
            if 'https://' in msg.content:
                url = msg.content.split()[1]
            else:
                text_url = msg.content.split()[1:]
                url = ' '.join(text_url)
                search_results = Search(url)
                for v in search_results.results:
                    link = f"{v.title}\n{v.watch_url}\n"
                    url = link
                    break
            track_queue.append(url)
            await msg.channel.send("Додав. Почекай, зара прогружусь")
            if len(track_queue) == 1:
                await play_track(msg.guild.id)

        except Exception as err:
            print(f"Error adding track to the queue: {err}")
            await msg.channel.send("Проблеми якісь")

    if msg.content.startswith("+pause"):
        try:
            voice_clients[msg.guild.id].pause()
            await msg.channel.send("Пауза")
        except Exception as err:
            print(f"Error pausing audio: {err}")

    if msg.content.startswith("+resume"):
        try:
            voice_clients[msg.guild.id].resume()
            await msg.channel.send("Нарешті")
        except Exception as err:
            print(f"Error resuming audio: {err}")

    if msg.content.startswith("+skip"):
        try:
            if len(track_queue) > 0:
                voice_clients[msg.guild.id].stop()
                await msg.channel.send("Вірно, мені це теж не подобається")
                await play_next_track(msg.guild.id)
            else:
                await msg.channel.send("Помилка, але не розумію чому")

        except Exception as err:
            print(f"Error skipping track: {err}")
        await asyncio.sleep(5)

    if msg.content.startswith("+off"):
        try:
            voice_clients[msg.guild.id].stop()
            await voice_clients[msg.guild.id].disconnect()
            del voice_clients[msg.guild.id]
            track_queue.clear()
            await msg.channel.send("Бувай")
        except Exception as err:
            print(f"Error stopping audio and disconnecting: {err}")


async def play_track(guild_id):
    url = track_queue[0]
    print(url)
    try:
        video = YouTube(url)
        audio_stream = video.streams.filter(only_audio=True, mime_type="audio/mp4").first()
        if audio_stream:
            voice_clients[guild_id].play(discord.FFmpegPCMAudio(source=audio_stream.url,
                                                                executable=ffmpeg_path, **FFMPeG_CONf),
                                         after=lambda e: asyncio.run_coroutine_threadsafe(play_next_track(guild_id),
                                                                                          client.loop))
    except Exception as err:
        print(f"Error playing audio: {err}")
        await voice_clients[guild_id].disconnect()
        del voice_clients[guild_id]
        track_queue.pop(0)
        if len(track_queue) > 0:
            await play_track(guild_id)

async def play_next_track(guild_id):
    track_queue.pop(0)
    if len(track_queue) > 0:
        await play_track(guild_id)

client.run(key)


