import sys
import traceback

try:
    # ... باقي الكود
except Exception as e:
    printادة)

### 2️⃣ إذا فيه مشكلة عدّل الملف:

1. في GitHub اضغط على `requirements.txt`
2. اضغط **Edit** (الأيقونة ب Discord Developer Portal مباشرة)
4. اضغط **Add**

---

### بعدين:

1. اضغط **Redeploy** 
2. انتظر 30 ثانية
3. شيك الـ **Logs** مرة ثانية

---

## سؤال:

**و أخطاء**

---

## إذا في خطأ في requirements.txt:

جرّب استبدل المحتوى بهذا:

```txt
discord.py==2.3.2
python-dotenv==1.0.0
aiohttp==3.8.5
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store temporary channels and their creators
temp_channels = {}

@bot.event
async def on_ready():
    print(f'✅ Bot logged in as {bot.user}')
    print(f'🤖 Bot ID: {bot.user.id}')
    try:
        synced = await bot.tree.sync()
        print(f'✨ Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.event
async def on_voice_state_update(member, before, after):
    # When user joins a voice channel
    if after.channel is not None and before.channel != after.channel:
        if hasattr(after.channel, 'name') and after.channel.name.startswith('➕'):
            await create_temp_channel(member, after.channel)
    
    # When user leaves - delete if empty
    if before.channel is not None:
        channel = before.channel
        if channel.id in temp_channels:
            if len(channel.members) == 0:
                await delete_temp_channel(channel)

async def create_temp_channel(member, creator_channel):
    """Create a temporary voice channel for the user"""
    try:
        guild = creator_channel.guild
        
        new_channel = await guild.create_voice_channel(
            name=f"🎤 {member.name}'s Channel",
            category=creator_channel.category,
            position=creator_channel.position + 1
        )
        
        temp_channels[new_channel.id] = {
            'creator': member.id,
            'guild': guild.id,
            'locked': False,
            'message_id': None
        }
        
        await member.move_to(new_channel)
        
        await new_channel.set_permissions(
            member,
            manage_channel=True,
            manage_permissions=True,
            move_members=True,
            deafen_members=True,
            mute_members=True
        )
        
        print(f'✨ Created temp channel: {new_channel.name}')
        
        # Send settings embed with buttons
        await send_channel_settings(new_channel, member)
        
    except Exception as e:
        print(f'❌ Error creating temp channel: {e}')

async def send_channel_settings(channel, creator):
    """Send settings embed with buttons to the voice channel's text channel"""
    try:
        # Find or create associated text channel
        guild = channel.guild
        
        # Create a text channel in the same category
        text_channel = await guild.create_text_channel(
            name=channel.name.lower().replace(' ', '-'),
            category=channel.category,
            topic=f"إعدادات القناة الصوتية - Settings for {channel.name}"
        )
        
        # Set permissions to match voice channel
        await text_channel.set_permissions(guild.default_role, read_messages=True, send_messages=False)
        await text_channel.set_permissions(creator, read_messages=True, send_messages=True, manage_messages=True)
        
        # Create embed
        embed = discord.Embed(
            title="⚙️ إعدادات قناتك الصوتية",
            description="استخدم الأزرار أدناه لتخصيص قناتك",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🎤 اسم القناة",
            value=channel.name,
            inline=False
        )
        embed.add_field(
            name="👥 عدد الأعضاء",
            value=f"{len(channel.members)}/{channel.user_limit if channel.user_limit > 0 else '∞'}",
            inline=False
        )
        embed.add_field(
            name="🔐 حالة القفل",
            value="🔓 مفتوحة",
            inline=False
        )
        embed.set_footer(text="اضغط على الأزرار لتعديل الإعدادات")
        
        # Create view with buttons
        view = ChannelSettingsView(channel, creator.id)
        
        message = await text_channel.send(embed=embed, view=view)
        
        temp_channels[channel.id]['message_id'] = message.id
        temp_channels[channel.id]['text_channel_id'] = text_channel.id
        
    except Exception as e:
        print(f'❌ Error sending settings: {e}')

async def delete_temp_channel(channel):
    """Delete a temporary voice channel"""
    try:
        if channel.id in temp_channels:
            # Delete associated text channel
            if 'text_channel_id' in temp_channels[channel.id]:
                text_channel = channel.guild.get_channel(temp_channels[channel.id]['text_channel_id'])
                if text_channel:
                    await text_channel.delete()
            
            del temp_channels[channel.id]
        await channel.delete()
        print(f'🗑️ Deleted temp channel: {channel.name}')
    except Exception as e:
        print(f'❌ Error deleting temp channel: {e}')

async def update_settings_embed(channel):
    """Update the settings embed"""
    try:
        if channel.id not in temp_channels:
            return
        
        text_channel_id = temp_channels[channel.id].get('text_channel_id')
        if not text_channel_id:
            return
        
        text_channel = channel.guild.get_channel(text_channel_id)
        if not text_channel:
            return
        
        is_locked = temp_channels[channel.id].get('locked', False)
        lock_status = "🔒 مقفولة" if is_locked else "🔓 مفتوحة"
        
        embed = discord.Embed(
            title="⚙️ إعدادات قناتك الصوتية",
            description="استخدم الأزرار أدناه لتخصيص قناتك",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🎤 اسم القناة",
            value=channel.name,
            inline=False
        )
        embed.add_field(
            name="👥 عدد الأعضاء",
            value=f"{len(channel.members)}/{channel.user_limit if channel.user_limit > 0 else '∞'}",
            inline=False
        )
        embed.add_field(
            name="🔐 حالة القفل",
            value=lock_status,
            inline=False
        )
        embed.set_footer(text="اضغط على الأزرار لتعديل الإعدادات")
        
        view = ChannelSettingsView(channel, temp_channels[channel.id]['creator'])
        
        # Try to edit the original message
        try:
            message_id = temp_channels[channel.id].get('message_id')
            if message_id:
                message = await text_channel.fetch_message(message_id)
                await message.edit(embed=embed, view=view)
        except:
            # If message not found, send a new one
            message = await text_channel.send(embed=embed, view=view)
            temp_channels[channel.id]['message_id'] = message.id
        
    except Exception as e:
        print(f'❌ Error updating embed: {e}')

class ChannelSettingsView(discord.ui.View):
    def __init__(self, channel, creator_id):
        super().__init__(timeout=None)
        self.channel = channel
        self.creator_id = creator_id
    
    async def check_creator(self, interaction: discord.Interaction) -> bool:
        """Check if user is the channel creator"""
        if interaction.user.id != self.creator_id:
            await interaction.response.send_message("❌ فقط مالك القناة يمكنه تعديل الإعدادات", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="✏️ إعادة تسمية", style=discord.ButtonStyle.primary, custom_id="rename_btn")
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_creator(interaction):
            return
        
        await interaction.response.send_modal(RenameModal(self.channel))
    
    @discord.ui.button(label="👥 تحديد الحد الأقصى", style=discord.ButtonStyle.primary, custom_id="limit_btn")
    async def limit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_creator(interaction):
            return
        
        await interaction.response.send_modal(LimitModal(self.channel))
    
    @discord.ui.button(label="🔐 قفل/فتح", style=discord.ButtonStyle.danger, custom_id="lock_btn")
    async def lock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_creator(interaction):
            return
        
        try:
            guild = self.channel.guild
            is_locked = temp_channels[self.channel.id].get('locked', False)
            temp_channels[self.channel.id]['locked'] = not is_locked
            
            if not is_locked:
                await self.channel.set_permissions(guild.default_role, connect=False)
                status = "🔒 تم قفل القناة"
            else:
                await self.channel.set_permissions(guild.default_role, connect=True)
                status = "🔓 تم فتح القناة"
            
            await interaction.response.send_message(f"✅ {status}", ephemeral=True)
            await update_settings_embed(self.channel)
        except Exception as e:
            await interaction.response.send_message(f"❌ خطأ: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="👤 الإذن للأعضاء", style=discord.ButtonStyle.secondary, custom_id="permit_btn")
    async def permit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_creator(interaction):
            return
        
        await interaction.response.send_modal(PermitModal(self.channel))
    
    @discord.ui.button(label="🚫 طرد عضو", style=discord.ButtonStyle.danger, custom_id="kick_btn")
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_creator(interaction):
            return
        
        if len(self.channel.members) <= 1:
            await interaction.response.send_message("❌ لا يوجد أعضاء لطردهم", ephemeral=True)
            return
        
        await interaction.response.send_modal(KickModal(self.channel))
    
    @discord.ui.button(label="📊 معلومات", style=discord.ButtonStyle.secondary, custom_id="info_btn")
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        creator = bot.get_user(self.creator_id)
        is_locked = "🔒 مقفولة" if temp_channels[self.channel.id].get('locked', False) else "🔓 مفتوحة"
        
        embed = discord.Embed(
            title=f"📊 {self.channel.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="👤 المالك", value=creator.mention if creator else "غير معروف", inline=False)
        embed.add_field(name="👥 الأعضاء", value=f"{len(self.channel.members)}/{self.channel.user_limit if self.channel.user_limit > 0 else '∞'}", inline=False)
        embed.add_field(name="🔐 الحالة", value=is_locked, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="❌ حذف القناة", style=discord.ButtonStyle.red, custom_id="delete_btn")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_creator(interaction):
            return
        
        await interaction.response.send_message("✅ جاري حذف القناة...", ephemeral=True)
        await delete_temp_channel(self.channel)

class RenameModal(discord.ui.Modal):
    def __init__(self, channel):
        super().__init__(title="✏️ إعادة تسمية القناة")
        self.channel = channel
        self.name_input = discord.ui.TextInput(
            label="الاسم الجديد",
            placeholder="أدخل الاسم الجديد للقناة",
            min_length=1,
            max_length=32
        )
        self.add_item(self.name_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            new_name = self.name_input.value
            await self.channel.edit(name=f"🎤 {new_name}")
            await interaction.response.send_message(f"✅ تم تغيير الاسم إلى: **{new_name}**", ephemeral=True)
            await update_settings_embed(self.channel)
        except Exception as e:
            await interaction.response.send_message(f"❌ خطأ: {str(e)}", ephemeral=True)

class LimitModal(discord.ui.Modal):
    def __init__(self, channel):
        super().__init__(title="👥 تحديد الحد الأقصى")
        self.channel = channel
        self.limit_input = discord.ui.TextInput(
            label="عدد الأعضاء الأقصى",
            placeholder="أدخل الرقم (0 = بدون حد)",
            min_length=1,
            max_length=2
        )
        self.add_item(self.limit_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.limit_input.value)
            if limit < 0 or limit > 99:
                await interaction.response.send_message("❌ أدخل رقم بين 0 و 99", ephemeral=True)
                return
            
            await self.channel.edit(user_limit=limit)
            limit_text = "بدون حد" if limit == 0 else str(limit)
            await interaction.response.send_message(f"✅ تم تعيين الحد الأقصى: **{limit_text}**", ephemeral=True)
            await update_settings_embed(self.channel)
        except ValueError:
            await interaction.response.send_message("❌ أدخل رقماً صحيحاً", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ خطأ: {str(e)}", ephemeral=True)

class PermitModal(discord.ui.Modal):
    def __init__(self, channel):
        super().__init__(title="👤 إعطاء صلاحيات")
        self.channel = channel
        self.user_input = discord.ui.TextInput(
            label="أدخل اسم أو ID العضو",
            placeholder="مثال: @username أو 123456789",
            min_length=1,
            max_length=100
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_input = self.user_input.value
            member = None
            
            # Try to find member by mention or ID
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = int(user_input[2:-1])
                member = await interaction.guild.fetch_member(user_id)
            else:
                try:
                    user_id = int(user_input)
                    member = await interaction.guild.fetch_member(user_id)
                except ValueError:
                    member = discord.utils.find(lambda m: m.name == user_input or m.display_name == user_input, interaction.guild.members)
            
            if not member:
                await interaction.response.send_message("❌ لم أجد هذا العضو", ephemeral=True)
                return
            
            await self.channel.set_permissions(
                member,
                manage_channel=False,
                manage_permissions=False,
                move_members=True,
                deafen_members=True,
                mute_members=True
            )
            
            await interaction.response.send_message(f"✅ تم إعطاء صلاحيات ل {member.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ خطأ: {str(e)}", ephemeral=True)

class KickModal(discord.ui.Modal):
    def __init__(self, channel):
        super().__init__(title="🚫 طرد عضو")
        self.channel = channel
        self.user_input = discord.ui.TextInput(
            label="أدخل اسم أو ID العضو",
            placeholder="مثال: @username أو 123456789",
            min_length=1,
            max_length=100
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_input = self.user_input.value
            member = None
            
            # Try to find member by mention or ID
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = int(user_input[2:-1])
                member = self.channel.guild.get_member(user_id)
            else:
                try:
                    user_id = int(user_input)
                    member = self.channel.guild.get_member(user_id)
                except ValueError:
                    member = discord.utils.find(lambda m: m.name == user_input or m.display_name == user_input, self.channel.members)
            
            if not member:
                await interaction.response.send_message("❌ لم أجد هذا العضو في القناة", ephemeral=True)
                return
            
            if member.id == interaction.user.id:
                await interaction.response.send_message("❌ لا يمكنك طرد نفسك", ephemeral=True)
                return
            
            await member.move_to(None)
            await interaction.response.send_message(f"✅ تم طرد {member.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ خطأ: {str(e)}", ephemeral=True)

@bot.tree.command(name='setup', description='إعداد قناة إنشاء الفويس تشات')
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_temp_voice(interaction: discord.Interaction):
    """Create a voice channel creator"""
    try:
        guild = interaction.guild
        
        # Create category if needed
        category = await guild.create_category("🎤 الفويس شات المؤقت")
        
        creator_channel = await guild.create_voice_channel(
            name='➕ إنشاء قناة جديدة',
            category=category
        )
        
        embed = discord.Embed(
            title='✅ تم الإعداد بنجاح!',
            description=f'تم إنشاء قناة الإنشاء: {creator_channel.mention}\n\nانضم إليها لإنشاء قناتك الخاصة!',
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title='❌ خطأ',
            description=f'Error: {str(e)}',
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Run the bot
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print('❌ Error: DISCORD_TOKEN not found in .env file')
else:
    bot.run(TOKEN)
