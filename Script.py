

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
limit=200

posts = subreddit.top("month",limit=limit)

 
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



#Format stuff we'll need later on
span=syntax.span
width = syntax.width
height = syntax.height
font = syntax.font

#Gets rid of all those pesky apostrophes which mess up the names of our save files

#All the characters below will mess up our method of using our titles for our file names
#as if the title has any of these we won't be able to save our images consistently.
chars_to_remove = ['.', '!', '?','<','>','*','/',' ','+','|'

,'=','#','&','{','}']

def title_clean(postnumber):

    #Adapted code from stack, just removes the aforementioned characters from our title which
    #can then be used as the file name for the images later on
    
    subj = title_uw=top_posts.loc[:,"Title"][postnumber]
    subj.translate(''.join(chars_to_remove))
    sc = set(chars_to_remove)
    ''.join([c for c in subj if c not in sc])

    #https://stackoverflow.com/questions/10017147/removing-a-list-of-characters-in-string




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
    #Span is how many lines you can fit on the page depending on your font so this will just
    #split it up into nice groups of 23 lines + the final one which should be less
    words = message_first.split("\n")
    split_result=["\n".join(words[i:i+span]) for i in range(0, len(words), span)]

    return split_result


def title_page(postnumber):

    #This function is just for creating our title page image which we post first 
    #and which has the title on it... obviously

    title_uw=top_posts.loc[:,"Title"][postnumber]

    title=textwrap.fill(text=title_uw, width=30,break_long_words=True,replace_whitespace=False)

    title_font= ImageFont.truetype('arial.ttf', 60)

    image_name= title_clean(postnumber)

    title_directory=directory+'\images\{}title.jpeg'.format(image_name)

    img = Image.new('RGB', (width, height), color='black')

    imgDraw = ImageDraw.Draw(img)

    imgDraw.text((10, 10), title, font=title_font, fill=(200, 217, 227))

    img.save(title_directory, 'JPEG') 

def message_page(postnumber):

#Generates our images with the post text! If we generate 9+ images here then we won't be able to post
#because of instagram limits. That being said we could look into doing part 1 part 2 posts but 
#that'd be a bit of code for a very rare event.

    split_result=message_prepare(postnumber)

    for i in range(len(split_result)):

        message= split_result[i]

        message_font= ImageFont.truetype('arial.ttf', 40)

        

        
        image_name= title_clean(postnumber)

        img = Image.new('RGB', (width, height), color='black')

        imgDraw = ImageDraw.Draw(img)

        imgDraw.text((10, 10), message, font=message_font, fill=(200, 217, 227))

    
        
        message_directory=directory+'\images\{}message{}.jpeg'.format(image_name,i)



        img.save(message_directory, 'JPEG')







def history_check(title):

#This checks if we've posted the post we're about to post before (if you'll pardon the posts)
#Not sure how this'll look after hundreds of post but for the scale of this I don't think it's a 
#huge issue.

    with open(r'history.txt', 'r') as fp:
        # read all lines in a list
        lines = fp.readlines()
        value=0
        for line in lines:
            # check if string present on a current line
            if line.find(title) != -1:
                value=1 #We have seen that title before
                
  
    return value


def bot_post(postnumber):
    #This takes all our hard work and actually posts it! Don't forget this bit that would just be
    #embarassing

    bot = Client()
    bot.login(config.username, config.password)

    title_uw=top_posts.loc[:,"Title"][postnumber]



    image_name= title_clean(postnumber)

    album_path=[directory+'\images\{}title.jpeg'.format(image_name)]


    for i in range(len(message_prepare(postnumber))):
        album_path.append(directory+'\images\{}message{}.jpeg'.format(image_name,i))



    bot.album_upload(
        album_path,
        caption = title_uw
        )
    
    file_object = open('history.txt', 'a')
    file_object.write(title_uw+',')





def full_monty():

#This is the uber function that uses all the ones from above, but sequences our checks on stuff that
#would mess up a post (is it too big/have we already done it) so we won't get an error message
#and our code will just keep running!
    v=0
    i=0
    val = int(input("How many posts would you like to do today? \n"))
    while i<=limit:#This makes sure we don't try and post a message we haven't loaded
        while v<=val:
            message=message_prepare(i)
            if len(message_prepare(0))<=9:
                print('Post',i,'is small enough to be uploaded')
                title_page(i)
                message_page(i)
                title_i=top_posts.loc[:,"Title"][i]
                check=history_check(title_i)


                if check==1:
                    print("We've already had post",i)
                    i+=1

                if check==0:
                    bot_post(i)
                    print('Successfully posted post',i)
                    i+=1
                    v+=1#v tracks our successful posts, the loop runs until we've done them
            
            
            
        
        else:
            print('Post',i,'had too many pages')
            i+=1

    print("Post complete") 


full_monty()