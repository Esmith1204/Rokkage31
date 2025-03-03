import json
from typing import Final
import os
import discord
from dotenv import load_dotenv
from discord import Intents, Client, Message, app_commands
from discord.ext import commands
from AI_31 import generate_response

# Load environment variables
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Initialize bot with necessary intents
intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Splitting a message into multiple messages for Discord for code blocks
def split_for_discord(input: str, max_length: int = 2000) -> list:
    messages = []
    current_message = []
    current_length = 0
    inside_code_block = False
    code_block_lang = ""

    lines = input.split("\n")

    for line in lines:
        # Detect code block starts/ends
        if line.startswith("```"):
            if inside_code_block:
                inside_code_block = False  # Closing a code block
                code_block_lang = ""
            else:
                inside_code_block = True   # Opening a code block
                code_block_lang = line[3:].strip()  # Capture language (if any)

        # If adding this line exceeds Discord's limit
        if current_length + len(line) + 1 > max_length:
            if inside_code_block:
                # Close the block, store message, start new block
                current_message.append("```")
                messages.append("\n".join(current_message))
                current_message = [f"```{code_block_lang}"]
                current_length = len(code_block_lang) + 4
            else:
                messages.append("\n".join(current_message))
                current_message = []
                current_length = 0

        # If the line itself is too long, break it into chunks
        while len(line) > max_length:
            messages.append(line[:max_length])
            line = line[max_length:]

        current_message.append(line)
        current_length += len(line) + 1  # +1 for newline

    # Append remaining content
    if current_message:
        messages.append("\n".join(current_message))

    return messages

# Ask RokkageBot+ a question with a thread
@bot.tree.command(name="askrokkage_thread", description="Ask RokkageBot+ a question with a thread")
@app_commands.describe(question="Ask anything")

async def askrokkage_thread(interaction: discord.Interaction, question: str):
    await interaction.response.defer()

    bot_name = "RokkageBot"
    user_name = interaction.user.name

    # If the user's name is "rokkage" and they say a specific greeting, handle differently
    if user_name.lower() == "rokkage" and question.lower() in ["hello", "hi", "hey", "yo", "sup", "wsp", 
                                                               "wake up", "lets go", "lets get to work",
                                                               "wake up daddys home", "wake up daddy's home",]:
        response = f"Hello Rokkage, what do you need today?"
    else:
        response = generate_response(question)

    # Prepare a message to display the user's original question
    original_message = f"{interaction.user.mention}: {question}"

    try:
        # Create a thread (private or public)
        thread_type = discord.ChannelType.public_thread
        thread = await interaction.channel.create_thread(
            name=f"{bot_name} Response: {interaction.user.name}",
            type=thread_type,
            auto_archive_duration=60 
        )

        # Send the original question in the channel (for public threads)
        await interaction.followup.send(f"{original_message}\n\nResponse sent in {thread.mention}", ephemeral=True)

        # Send the response in the thread
        split_responses = split_for_discord(response)
        for msg in split_responses:
            await thread.send(msg)

    except Exception as e:
        await interaction.followup.send(f"Error generating response: {e}")


#AI RokkageBot+ command
@bot.tree.command(name="askrokkage", description="Ask RokkageBot+ a question")
@app_commands.describe(question="Ask anything")

async def askrokkage(interaction: discord.Interaction, question: str):
    try:
        await interaction.response.defer()

        bot_name = "RokkageBot"
        user_name = interaction.user.name

        # Special response for user "rokkage"
        if user_name.lower() == "rokkage" and question.lower() in ["hello", "hi", "hey", "yo", "sup", "wsp", 
                                                                   "wake up", "lets go", "lets get to work",
                                                                   "wake up daddys home", "wake up daddy's home"]:
            response = f"Hello Rokkage, what do you need today?"
        else:
            response = generate_response(question)  # Call AI response generator

        original_response = f"{interaction.user.mention}: {question}"
        await interaction.followup.send(original_response)

        # Split response and send it in multiple messages
        split_responses = split_for_discord(response)
        for msg in split_responses:
            await interaction.followup.send(msg)

    except Exception as e:
        await interaction.followup.send(f"Error generating response: {e}")


def main() -> None:
    bot.run(TOKEN)

if __name__ == "__main__":
    main()