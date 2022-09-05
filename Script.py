import praw
import pandas as pd
import csv

from PIL import Image, ImageDraw, ImageFont

import textwrap

import re
import math

import os

from instagrapi import Client

import config, syntax

directory= os. getcwd()


#First we're going to access reddit

reddit_read_only = praw.Reddit(client_id=config.client_id,         # your client id
                               client_secret=config.client_secret,      # your client secret
                               user_agent=config.user_agent)        # your user agent

subreddit= reddit_read_only.subreddit("AmItheAsshole")

# Display the name of the Subreddit
print("Display Name:", subreddit.display_name)
 
# Display the title of the Subreddit
#print("Title:", subreddit.title)
 
# Display the description of the Subreddit
#print("Description:", subreddit.description)


# Scraping the top posts of the current month:

posts = subreddit.top("month")

 
posts_dict = {"Title": [], "Post Text": [],
              "ID": [], "Score": [],
              "Total Comments": [], "Post URL": []
              }
 
for post in posts:
    # Title of each post
    posts_dict["Title"].append(post.title)
     
    # Text inside a post
    posts_dict["Post Text"].append(post.selftext)
     
    # Unique ID of each post
    posts_dict["ID"].append(post.id)
     
    # The score of a post
    posts_dict["Score"].append(post.score)
     
    # Total number of comments inside the post
    posts_dict["Total Comments"].append(post.num_comments)
     
    # URL of each post
    posts_dict["Post URL"].append(post.url)

#Saving the data in a pandas dataframe
top_posts = pd.DataFrame(posts_dict)

#I'm messing about with separate files, it's probably useful having a syntax one?
span=syntax.span
width = syntax.width
height = syntax.height
font = syntax.font


def message_prepare(postnumber):
    
    #The biggest pain is keeping the user inputted linebreaks whilst also wrapping the text to fit

    #This standardises all our spaces with a rogue character - if someone uses one of these in the
    #post we're finished - call your loved ones it's all over

    message=top_posts.loc[:,"Post Text"][postnumber]

    message_005=message.replace("&#x200B;","§") 

    message_1=message_005.replace("\n","§") 

    #Right now we're splitting up our text into different chunks separated by these breaks

    message_array=re.split(r'§', message_1)

    
    #And now we're poaching each of these bits into a nice array
    message_af=[x for x in message_array if x]

    #Now we're going to tidy up each of these chunks of message and wrap them individually
    #This might seem tedious but trust me it's a mess otherwise
    #If the user is writing a sentence, then puts a linebreak in to start a new one
    #textwrap will keep counting the characters as if nothing has happened
    #so it'll just break the line halfway through so the first lines of paragraphs are always messy
    loop_message=[]

    for i in range(len(message_af)):
        message_i= textwrap.fill(text=message_af[i], width=55,break_long_words=True,replace_whitespace=False)
        loop_message.append(message_i)
    
    #This now turns what we've tidied up above into a nice string where the lines are the length
    #we want 'em and they're separated by some nice linebreaks
    message_first=''
    for i in range(len(loop_message)-1):
    
        message_first= message_first+ loop_message[i]+ "\n" + "\n"

    #We're now hitting the issue where we want to split up these messages depending on how many lines
    #we have which can happen halfway through a paragraph, so we need to keep split up our messages AGAIN

    words = message_first.split("\n")
    split_result=["\n".join(words[i:i+span]) for i in range(0, len(words), span)]

    return split_result


def title_page(postnumber):

    title_uw=top_posts.loc[:,"Title"][postnumber]

    title=textwrap.fill(text=title_uw, width=30,break_long_words=True,replace_whitespace=False)

    title_font= ImageFont.truetype('arial.ttf', 60)

    image_name= title_uw[:50]

    title_directory=directory+'\images\{}title.jpeg'.format(image_name)

    img = Image.new('RGB', (width, height), color='black')

    imgDraw = ImageDraw.Draw(img)

    imgDraw.text((10, 10), title, font=title_font, fill=(200, 217, 227))

    img.save(title_directory, 'JPEG') 

def message_page(postnumber):
#Generates our images with the post text
    split_result=message_prepare(postnumber)

    for i in range(len(split_result)):

        message= split_result[i]

        message_font= ImageFont.truetype('arial.ttf', 40)

        

        
        image_name= top_posts.loc[:,"Title"][postnumber][:50]

        img = Image.new('RGB', (width, height), color='black')

        imgDraw = ImageDraw.Draw(img)

        imgDraw.text((10, 10), message, font=message_font, fill=(200, 217, 227))

    
        
        message_directory=directory+'\images\{}message{}.jpeg'.format(image_name,i)



        img.save(message_directory, 'JPEG')

postnumber=0
message_page(postnumber)
title_page(postnumber)

def bot_post(postnumber):
    bot = Client()
    bot.login(config.username, config.password)

    title_uw=top_posts.loc[:,"Title"][postnumber]

    image_name= top_posts.loc[:,"Title"][postnumber][:50]

    album_path=[directory+'\images\{}title.jpeg'.format(image_name)]


    for i in range(len(message_prepare(postnumber))):
        album_path.append(directory+'\images\{}message{}.jpeg'.format(image_name,i))



    bot.album_upload(
        album_path,
        caption = title_uw
    )
bot_post(postnumber)