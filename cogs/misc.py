import discord
from discord.ext import commands
from discord.commands import Option
import os
from discord.ui import *
from discord.utils import get


class Misc(commands.Cog):
    def __init__(self, lmbot):
        self.lmbot = lmbot

    
    @commands.slash_command(name="start-session", description="It sets up the respective Teacher | Student  roles in the server")
    async def start_session(self, ctx):
        try:

            await ctx.defer()
            # Creatting Respective Settup Roles
            guild = ctx.guild

            teacher_role = discord.utils.get(guild.roles, name="Teacher | Prof.")
            if not teacher_role:
                await guild.create_role(name="Teacher | Prof.", color=0xFF7F50, mentionable=True, hoist=True)
            student_role = discord.utils.get(guild.roles, name="Student")
            if not student_role:
                await guild.create_role(name="Student", color=0x1E90FF, mentionable=True, hoist=True)
            
            # Create a channel & Category
            categories = discord.utils.get(guild.categories, name="Teacher's Doubt Requests")
            if not categories:
                await guild.create_category(name="Teacher's Doubt Requests")
            


            # Option Views
            class MyView(discord.ui.View):
                @discord.ui.select(placeholder='Pick An Option', min_values=1, max_values=1, options=[
                    discord.SelectOption(label='Student', emoji='👨‍🎓',value="std-slct"),
                    discord.SelectOption(label='Teacher | Professor', emoji='👩‍🏫',value="teacher-slct"),
                ])
                async def select_callback(self, select, interaction):

                    response = select.values[0]

                    user = interaction.user
                    student_role = get(user.guild.roles, name="Student")
                    teacher_role = get(user.guild.roles, name="Teacher | Prof.")

                    if response == "std-slct":
                        if teacher_role in user.roles:
                            await user.remove_roles(teacher_role)
                            await user.add_roles(student_role)
                        else:
                            await user.add_roles(student_role)
                        await interaction.response.send_message("You have successfully selected `Student` Role", ephemeral=True)
                    
                    elif response == "teacher-slct":
                        if student_role in user.roles:
                            await user.remove_roles(student_role)
                            await user.add_roles(teacher_role)
                            cat = discord.utils.get(guild.categories, name="Teacher's Doubt Requests")
                            channel = await guild.create_text_channel(name=f"{interaction.user.name} Requests", category=cat)
                            await channel.set_permissions(target=student_role,view_channel=False)
                            await channel.set_permissions(ctx.guild.student_role,view_channel=False)
                        else:
                            await user.add_roles(teacher_role)
                            cat = discord.utils.get(guild.categories, name="Teacher's Doubt Requests")
                            channel = await guild.create_text_channel(name=f"{interaction.user.name} Requests", category=cat)
                            await channel.set_permissions(target=student_role,view_channel=False)

                        await interaction.response.send_message("You have successfully selected `Teacher` Role", ephemeral=True)





            embed = discord.Embed(title="Setting things Up",color=0x068FFB)
            embed.add_field(name="🧮 Select Respective Roles",value="`Teacher Option` - Select this option if you are a teacher \n `Student Option` - Select this option if you are a student")

            await ctx.respond(embed=embed, view=MyView())

        except Exception as e:
            print(e)
    

    @commands.slash_command(name='doubt-session', description='command to setup the doubts sessions for the teachers')
    async def doubt_session(self, ctx, teacher:discord.Member, doubt:Option(str, 'Please specify the doubt that you want to ask the teacher', requried=True)):
        try:
            guild = ctx.guild
            teacher = teacher


            teacher_role = discord.utils.get(guild.roles, name="Teacher | Prof.")
            if not teacher_role in teacher.roles:
                await ctx.respond('You Have to ask the question a `Teacher`, mention a teacher in the teacher parameter !', ephemeral=True)
            else:
                channel = discord.utils.get(guild.channels, name=f"{teacher.name.lower()}-requests")
                embed = discord.Embed(color=0x068FFB, title="Incomming Doubt Requests", description=f"`{ctx.author.name}` has asked you for help & doubt session ! \n \n Doubt : `{doubt}`")
                
                # define buttons
                accept = Button(label="Accept", style=discord.ButtonStyle.green)
                deny = Button(label="Deny", style=discord.ButtonStyle.red)

                # callback functions
                async def accept_callback(interaction: discord.Interaction):
                    embed = discord.Embed(color=0x00FF7F, description=f'✅ Doubt accepted for {ctx.author.name}')
                    await interaction.response.edit_message(content='', embed=embed, view=None)
                    await guild.create_category(name=f"{ctx.author.name}'s Doubt session")
                    cat = discord.utils.get(guild.categories, name=f"{ctx.author.name}'s Doubt session")
                    await guild.create_text_channel(name=f"Doubt Text Channel", category=cat)
                    await guild.create_voice_channel(name=f"Doubt voice Channel", category=cat)
                

                async def deny_callback(interaction:discord.Interaction):
                    embed = discord.Embed(color=0xff5252, description=f"❌ `{ctx.author.name}` doubt session has been denied")
                    await interaction.response.edit_message(content='',embed=embed, view=None)
                    

                    
                
                # assigning Interaction callbacks
                accept.callback = accept_callback
                deny.callback = deny_callback

                # Listing / Sorting / Adding Buttons
                button_view = View()
                button_view.add_item(accept)
                button_view.add_item(deny)

                # Main embed
                await ctx.respond('Teacher is Checking your requests , Please wait')
                message_channel = self.lmbot.get_channel(channel.id)
                await message_channel.send(embed=embed, view=button_view)
                

                
        except Exception as e:
            print(e)
    

    @commands.slash_command(name="create-assignment", description="Creats assignments for students , supports assignment images ! also make sure image is large in size")
    async def create_assignment(self, ctx, assignment_image:Option(discord.Attachment), assignment_description:Option(str, description="Please provide a description for the assingment", required=True), submission_date:Option(str, description="Please provide a submission_date for the assingment", required=False)):
        try:
            await ctx.defer()
            guild = ctx.guild
            teacher_role = discord.utils.get(guild.roles, name="Teacher | Prof.")
            if not teacher_role in ctx.author.roles:
                await ctx.respond('❌ This command can be used By Teachers only !', ephemeral=True)
            else:
                embed = discord.Embed(color=0x068FFB, title="New Assignment")
                embed.add_field(name="Details", value=f"Description  -  {assignment_description} \n Submission Date -  {submission_date}")
                embed.set_image(url=assignment_image)
                await ctx.respond(embed=embed)
        except Exception as e:
                print(e)
    
    @commands.slash_command(name="assignment-feedback", description="Gives a feedback to the students about the assignment throught their dms !")
    async def assignment_feedback(self, ctx, student:Option(discord.Member, description="Mention the student you want to give the feedback", required=True), feedback:Option(str, description="Give the feedback of the assingment done by the student") ,assignment_image:Option(discord.Attachment, description="If you have the solved assingment of the student, you can attach it", required=False)):
        try:
            await ctx.defer()
            guild = ctx.guild
            teacher_role = discord.utils.get(guild.roles, name="Teacher | Prof.")
            if not teacher_role in ctx.author.roles:
                await ctx.respond('❌ This command can be used By Teachers only !', ephemeral=True)
            else:
                embed = discord.Embed(color=0x068FFB, title="Teachers Feedback", description=f"From {ctx.author} \n {feedback}")
                if assignment_image == None:
                    await ctx.respond(f'✅ Feedback Send Successfully to {student.name}', ephemeral=True)
                    await student.send(embed=embed)
                else:
                    await ctx.respond(f'✅ Feedback Send Successfully to {student.name}', ephemeral=True)
                    embed.set_image(url=assignment_image)
                    await student.send(embed=embed)

        except Exception as e:
            print(e)
    
    @commands.slash_command(name="study-group", description="Create a study group in a server and anyone can join !")
    async def study_group(self, ctx, group_name:Option(str, 'mention the study group name')):
        try:
            await ctx.defer()
            guild = ctx.guild
            await guild.create_category(name=f"{group_name}'s Study Group")
            cat = discord.utils.get(guild.categories, name=f"{group_name}'s Study Group")
            await guild.create_text_channel(name=f"Study Group Text", category=cat)
            await guild.create_voice_channel(name=f"Study Group Voice", category=cat)
            embed = discord.Embed(color=0x068FFB, description=f'✅ Created Public Study Group - {group_name}')
            await ctx.respond(embed=embed)
        except Exception as e:
            print(e)
    
    

    @commands.slash_command(name='help', description='The guide book of the bot')
    async def helpcommand(self, ctx):
        try:
            embed = discord.Embed(color=0x068FFB, description="", title="Learnezy Help Command")
            embed.add_field(name="Commands :", value="`/start-session` - It sets up the respective Teacher | Student  roles in the server \n `/doubt_session` - Doubt sessions between the students and the teachers \n `/create_assignment` - Create and Upload assignments for the students\n `/assignment_feedback` - Gives a feedback to the students about the assigment\n  `/study-group` - Create a study group in a server and anyone can join \n\n")
            embed.set_footer(text='LearnEzy', icon_url="https://cdn.discordapp.com/attachments/885938706568077323/975390182981382154/unknown.png")
            await ctx.respond(embed=embed)
        except Exception as e:
            print(e)
        


def setup(lmbot):
    lmbot.add_cog(Misc(lmbot))