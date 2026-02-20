import sqlite3
import discord

DB_NAME = "rss/no_webhook.db"

#only run once
def setup_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # create the table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS webhooks (
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            webhook_url TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def get_webhook_data(guild_id: int, channel_id: int, username: str):
    """Retrieves webhook data from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT webhook_url 
        FROM webhooks 
        WHERE guild_id = ? AND channel_id = ? AND username = ?
    ''', (guild_id, channel_id, username))
    data = cursor.fetchone()
    conn.close()
    return data # returns (url, name) or None

def save_webhook_data(guild_id: int, channel_id: int, webhook_url: str, username: str):
    """Saves webhook data in the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Use INSERT OR REPLACE to either save a new entry or update an existing one
    cursor.execute('''
        INSERT OR REPLACE INTO webhooks 
        (guild_id, channel_id, webhook_url, username) 
        VALUES (?, ?, ?, ?)
    ''', (guild_id, channel_id, webhook_url, username))
    conn.commit()
    conn.close()

async def delete_all_discord_webhooks(ctx):
    """
    Deletes all webhooks stored in the database from Discord.
    
    Returns:
        int: The number of webhooks successfully deleted.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT webhook_url FROM webhooks')
    # Fetch all results, and use a list comprehension to flatten the list of tuples
    webhook_urls = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    deleted_count = 0
    
    print(f"Attempting to delete {len(webhook_urls)} webhooks from Discord...")
    
    for url in webhook_urls:
        try:
            # Recreate the Webhook object from the URL
            webhook = discord.Webhook.from_url(url, client=ctx.bot)
            
            # The delete operation requires the webhook's token (part of the URL)
            await webhook.delete()
            print(f"Successfully deleted webhook: {url}")
            deleted_count += 1
            
        except discord.NotFound:
            # The webhook might have been deleted manually or by Discord already
            print(f"Webhook not found (already deleted?): {url}")
        except discord.HTTPException as e:
            # Catch other potential Discord errors (e.g., rate limit, forbidden)
            print(f"Error deleting webhook {url}: {e}")
        except Exception as e:
            # Catch other potential errors, e.g., if the URL is malformed
            print(f"An unexpected error occurred for URL {url}: {e}")

    print(f"Finished Discord cleanup. Successfully deleted {deleted_count} webhooks.")
    return deleted_count

# returns webhook
async def create_and_store_webhook(ctx, webhook_name: str, pfp_bytes: bytes, username: str):
    webhook = await ctx.channel.create_webhook(
        name=webhook_name,
        avatar=pfp_bytes,
    )
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id
    webhook_url = webhook.url
    save_webhook_data(guild_id,channel_id,webhook_url, username)
    return webhook

def delete_webhook_entry(webhook_url: str) -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # SQL statement to delete the row where the webhook_url matches
    cursor.execute('''
        DELETE FROM webhooks 
        WHERE webhook_url = ?
    ''', (webhook_url,)) # Tuple format for parameter passing is critical
    
    rows_deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_deleted

async def delete_all_webhook_entries(ctx):
    """
    Deletes all entries from the 'webhooks' table.
    
    Returns:
        int: The number of rows deleted.
    """
    await delete_all_discord_webhooks(ctx)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # SQL statement to delete ALL rows from the table
    cursor.execute('DELETE FROM webhooks')
    
    rows_deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return

async def cleanup_all_webhooks(ctx):
    """delete all webhooks, I fucked up"""

    # 2. Fetch all webhooks in the channel
    try:
        webhooks = await ctx.channel.webhooks()
    except discord.Forbidden:
        await ctx.send("I don't have permission to manage webhooks in this channel.")
        return

    deleted_count = 0
    
    # 3. Iterate and delete those whose URLs don't match the one we want to keep
    for webhook in webhooks:
        # Check if the webhook URL is DIFFERENT from the one we want to keep
        # and if the webhook name matches the expected name.
        await webhook.delete()
        deleted_count += 1
        print(f"Deleted stale webhook: {webhook.name} ({webhook.url})")

    print(f"deleted {deleted_count} stale webhooks.")

async def send_message_via_webhook(ctx, webhook_name: str, pfp_bytes: bytes, username: str, message_content: str = None, file = None):
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id
    db_data = get_webhook_data(guild_id, channel_id, username)

    webhook_url = None
    if db_data:
        webhook_url = db_data[0]
        # check if the found webhook is valid
        try:
            webhook = discord.Webhook.from_url(webhook_url, client=ctx.bot)
            if file:
                await webhook.send(content=message_content,file=file,username=username)
            else:
                await webhook.send(content=message_content,username=username)
            return
        except discord.NotFound:
            # deleted webhook
            delete_webhook_entry(webhook_url)
            print(f"webhook is deleted: {webhook_url}")
        except ValueError as e:
            delete_webhook_entry(webhook_url)
            print(f"Error creating webhook: {e}")
        except discord.HTTPException as e:
            # rate limit catcher
            print(f"error sending message via webhook: {e}")
            return

    # 3. Create and store new webhook if it didn't exist or was invalid
    try:
        # create_and_store_webhook handles the creation and DB saving
        new_webhook = await create_and_store_webhook(ctx, webhook_name, pfp_bytes, username)
        
        # 4. Send the message via the newly created webhook
        if file:
            await new_webhook.send(content=message_content,file=file,username=username)
        else:
            await new_webhook.send(content=message_content,username=username)

    except discord.HTTPException as e:
        print(f"error creating or sending message via new webhook: {e}")
        
async def delete_message(ctx, message_id: int):
    """Deletes a message by its ID using stored webhooks."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Fetch all webhook URLs from the database
    cursor.execute('SELECT webhook_url FROM webhooks')
    webhook_urls = cursor.fetchall()
    conn.close()
    
    for (webhook_url,) in webhook_urls:
        try:
            webhook = discord.Webhook.from_url(webhook_url, client=ctx.bot)
            await webhook.delete_message(message_id)
            print(f"Deleted message {message_id} using webhook {webhook_url}")
            return  # Exit after successful deletion
        except discord.NotFound:
            print(f"Webhook not found: {webhook_url}")
        except discord.HTTPException as e:
            print(f"Error deleting message with webhook {webhook_url}: {e}")

async def send_embed_webhook(ctx, title, content, color, webhook_name: str, pfp_bytes: bytes, username: str):
    guild_id = ctx.guild.id
    channel_id = ctx.channel.id
    db_data = get_webhook_data(guild_id, channel_id, username)

    embed = discord.Embed(title=title, description=content, color=color)
    
    webhook_url = None
    if db_data:
        webhook_url = db_data[0]
        # check if the found webhook is valid
        try:
            webhook = discord.Webhook.from_url(webhook_url, client=ctx.bot)
            await webhook.send(
                embeds=[embed],
                username=username
            )
            return
        except discord.NotFound:
            # deleted webhook
            delete_webhook_entry(webhook_url)
            print(f"webhook is deleted: {webhook_url}")
        except ValueError as e:
            delete_webhook_entry(webhook_url)
            print(f"Error creating webhook: {e}")
        except discord.HTTPException as e:
            # rate limit catcher
            print(f"error sending message via webhook: {e}")
            return

    # 3. Create and store new webhook if it didn't exist or was invalid
    try:
        # create_and_store_webhook handles the creation and DB saving
        new_webhook = await create_and_store_webhook(ctx, webhook_name, pfp_bytes, username)
        
        # 4. Send the message via the newly created webhook
        await new_webhook.send(
            embeds=[embed],
            username=username                            #do I need this line
        )
    except discord.HTTPException as e:
        print(f"error creating or sending message via new webhook: {e}")

