import os
import glob
import discord

from discord.ext import commands
from discord.utils import get
from dotenv import load_dotenv

#Load Config
load_dotenv('.env')
Token = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=',', description="This is a Study Group Bot", intents=intents, help_command=None)

@bot.command()
async def help(ctx):
    
    embed=discord.Embed(title="Study Group Commands ", description="A list of commands and their uses", color=0xffffff)
    embed.add_field(name=",create groupName", value="Creates a group named 'groupName'", inline=False)
    embed.add_field(name=",delete groupName", value="Deletes the group", inline=False)
    embed.add_field(name=",list", value="Sends you a list of groups", inline=False)
    embed.add_field(name=",join groupName", value="Adds you to groupName ", inline=False)
    embed.add_field(name=",leave groupName", value="Removes you from groupName ", inline=False)
    embed.add_field(name=",ping groupName", value="DMs all members of groupName", inline=False)
    embed.set_footer(text="DM JoshoTheMosho#0077 if you have any requests or issues")
    
    await ctx.message.author.send(embed=embed)

@bot.command()
async def create(ctx, groupName: str):
    #Blocks this command (And those below) from being used in DMs 
    if ctx.message.channel.type is discord.ChannelType.private: 
        return
        
    authorID = ctx.message.author.id
    
    #If the study group already exists, they can only join it
    try:
        f = open('./UVic Engr Study Groups/' + groupName + '.txt', "x") 
    except FileExistsError:
        await ctx.send('The group ' + groupName + ' already exists')
        return
       
    f.write(str(authorID) + '\n')
    f.close()
    await ctx.send('<@' + str(authorID) + '> has created a new group: ' + groupName)
    
@bot.command()
async def delete(ctx, groupName: str):
    if ctx.message.channel.type is discord.ChannelType.private: 
        return
        
    authorID = ctx.message.author.id

    if(os.path.exists('./UVic Engr Study Groups/' + groupName + '.txt')):
        f = open(groupName + '.txt')
        #This is the owner of the group
        leadUser = f.readline()
        f.close()
        
        #If the user is a mod, they override and delete the group
        #Mod role specifically for the uvic engr server
        modRole = ctx.guild.get_role(636645305223217172)
            
        #Moderators can override and delete the groups themselves
        if modRole in ctx.message.author.roles:
            os.remove('./UVic Engr Study Groups/' + groupName + '.txt')
            await ctx.send('Group ' + groupName + ' has been deleted by <@' + str(authorID) + '>')
                
        #If the owner tries to delete the group, then it gets deleted
        elif(str(leadUser.strip()) == str(authorID)):
            os.remove('./UVic Engr Study Groups/' + groupName + '.txt')
            await ctx.send('Group ' + groupName + ' has been deleted by <@' + str(authorID) + '>')
            
        #If there is no owner, or its specified to be the mods, they will be able to delete the group. It will let regular users know to contact mods about it, and ping mods
        elif((leadUser.strip() == 'mod') or (leadUser.strip() == '')):
            await ctx.send('The group owner has left ' + groupName + '. Please contact a <@&636645305223217172> to delete this group.')
        
        #If someone other than the owner tries to delete the group, this happens
        else:
            await ctx.send('You cannot delete the group ' + groupName + '! Only the group owner, <@' + leadUser.strip() +'>, can do that.')
    else:
        await ctx.send('The group ' + groupName + ' does not exist')
   
@bot.command()
async def list(ctx):
        
    #Gets a list of all text files in the global directory
    #TO ADD: Seperate directories for each guild -- Current plans are usage on a single server so this can wait for now

    # If the file doesn't exist, print to the terminal and create the folder
    try:
        os.chdir(r'./UVic Engr Study Groups/')
    except FileNotFoundError:
        print("Creating Study Groups Folder...")
        os.makedirs(r'./UVic Engr Study Groups/')
        os.chdir(r'./UVic Engr Study Groups/')

    #Continue as normal
    #Make sure there isn't something funky or an empty folder
    try:
        myFiles = glob.glob('*.txt')
        groups = [x[:-4] for x in myFiles]
        groups = sorted(groups, key=str.casefold)
        
        embed=discord.Embed(title="Study Groups", description="", color=0xffffff)

        allGroups = ''
    
        for x in groups:
            allGroups += str(x) + ', '
        
        embed.add_field(name='Here is a full list of all study groups', value=allGroups[:-2], inline=False)
        await ctx.message.author.send(embed=embed)
    except:
        print("No groups/files inside folder")

@bot.command()
async def join(ctx, groupName: str):
    if ctx.message.channel.type is discord.ChannelType.private: 
        return
        
    authorID = ctx.message.author.id

    if(os.path.exists('./UVic Engr Study Groups/' + groupName + '.txt')):
        f = open('./UVic Engr Study Groups/' + groupName + '.txt', "r")
        #List of all users in group
        userList = f.read()
        
        if str(authorID) in userList:
            await ctx.send('You are already in the ' + groupName + ' group.')
        else:
            f.close()
            f = open('./UVic Engr Study Groups/' + groupName + '.txt', "a")
            f.write(str(authorID) + '\n')
            await ctx.send('You have successfully joined the ' + groupName + ' group.')
            
        f.close()
    else:
        await ctx.send('The group ' + groupName + ' does not exist yet.')        

@bot.command()
async def leave(ctx, groupName: str):
    if ctx.message.channel.type is discord.ChannelType.private: 
        return
        
    authorID = ctx.message.author.id

    try:
        f = open('./UVic Engr Study Groups/' + groupName + '.txt')
        
        #This is the owner of the group
        leadUser = f.readline()
        f.close()
        
        #If the owner leaves the group, the mod team takes over
        if(str(leadUser.strip()) == str(authorID)):            
            
            with open('./UVic Engr Study Groups/' + groupName + ".txt", "r") as f:
                lines = f.readlines()

                lines # ['This is the first line.\n', 'This is the second line.\n']

                lines[0] = "mod\n"

                lines # ["This is the line that's replaced.\n", 'This is the second line.\n']

            with open('./UVic Engr Study Groups/' + groupName + ".txt", "w") as f:
                f.writelines(lines)
                
            await ctx.send('Group owner <@' + str(authorID) + '> has left the ' + groupName + ' group. Only a moderator may delete the group now.')
            
        else:
            f = open('./UVic Engr Study Groups/' + groupName + '.txt', 'r')
            userList = f.readlines()
            f.close()
            
            for userID in userList:
        
                #Checks if the author is in the group 
                if(str(authorID) == str(userID.strip())):

                    #Once they're found, remove them then exit
                    f = open('./UVic Engr Study Groups/' + groupName + '.txt')
                    output = []
                    for line in f:
                        if not str(authorID) in line:
                            output.append(line)
                    f.close()
                    f = open('./UVic Engr Study Groups/' + groupName + '.txt', 'w')
                    f.writelines(output)
                    f.close()
                    await ctx.send('<@' + str(authorID) + '> has successfully been removed from the ' + groupName + ' group.')
                    return
                    
            #If they're not in the group, let them know
            await ctx.send('You are not in the ' + groupName + ' group.')
    except IOError:
        await ctx.send('The group ' + groupName + ' does not exist.')
    finally:
        f.close()

@bot.command()
async def ping(ctx, groupName: str):
    if ctx.message.channel.type is discord.ChannelType.private: 
        return
        
    authorUserID = ctx.message.author.id

    #Checks to see if the group exists
    if(os.path.exists('./UVic Engr Study Groups/' + groupName + '.txt')):
        
        f = open('./UVic Engr Study Groups/' + groupName + '.txt', "r")
        
        #List of all users in group
        userList = f.readlines()
        f.close()
           
        for userID in userList:
        
            #Checks if the author is in the group 
            if(str(authorUserID) == str(userID.strip())):
                
                #Once verified, goes through the list and DMs all users
                await ctx.send('<@' + str(authorUserID) + '> sent a ping to all students in the ' + groupName + ' group!')
                for userID in userList:  

                    #If the DM doesn't get sent for any reason, output in console that it failed to send
                    try:
                    
                        user = ctx.guild.get_member(int(userID))
                        await user.send(f'{ctx.message.author} has pinged the ' + groupName + ' group in the ' + str(ctx.message.channel) + ' channel!')
                   
                    except:
                        print('!Error! Failed to DM userID ' + str(userID).strip() + ' for study group ' + groupName)
                    
                #Once all users have been DMed, get out
                return
        
        #Failing to find author in the group stops them from pinging people
        await ctx.send('You can not ping a group if you are not in it.')

    else:
        await ctx.send('The group ' + groupName + ' does not exist.')

# Events
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="someones study group"))
    print('The bot has been deployed')
    print(f'We have logged in as {bot.user}')
    
bot.run(Token)