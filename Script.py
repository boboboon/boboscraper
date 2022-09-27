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

# This is just to find out what directory you're working in. I like it as it allows me to quickly get save
# stuff where I want it.

directory= os. getcwd()


# First we're going to access reddit

# We're using praw to login to Reddit. Please refer to the PRAW LOGIN part of the README.md to see details on
# to get fancy stuff such as client_secrets (we're not insider trading I promise)

# Here's the praw website on this part if you want to stretch your wings:
# https://praw.readthedocs.io/en/stable/code_overview/reddit_instance.html

reddit_read_only = praw.Reddit(client_id=config.client_id,         # your client id
                               client_secret=config.client_secret,      # your client secret
                               user_agent=config.user_agent)        # your user agent

# You can of course choose whatever subreddit you want to scrape. I stayed close to home and chose this.
subreddit= reddit_read_only.subreddit("AmItheAsshole")


# I personally didn't want to clog up my terminal with all of these details about the specific subreddit
# but this may be useful to those of you who may want to look through multiple subreddits.

# Display the name of the Subreddit
#print("Display Name:", subreddit.display_name)
 
# Display the title of the Subreddit
#print("Title:", subreddit.title)
 
# Display the description of the Subreddit
#print("Description:", subreddit.description)


# I think the max limit is 1000 and the default is 100. You can choose how many posts you want to check.
# You can also do it by daily or weekly or monthly, we'll do it monthly below.


# Scraping the top posts of the current month:
limit=50

# This grabs the top posts from this month
# Again here's the documentation if you want to look at maybe filtering the results
# https://praw.readthedocs.io/en/stable/code_overview/models/subreddit.html
posts = subreddit.top("month",limit=limit)


# This is a directory of all the stuff we're grabbing from these top posts from the subreddit
# 
posts_dict = {"Title": [], "Post Text": [],
              "ID": [], "Score": [],
              "Total Comments": [], "Post URL": []
              }
 

# Now we're running through all our posts and adding the appropiate data into each directory column
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

# Saving the data in a pandas dataframe
top_posts = pd.DataFrame(posts_dict)

# You can then turn this into an excel file if you want to show your findings but we're using it to
# grab the text and title from. Plus never hurts to work with a pandas dataframe.



#Format stuff we'll need later on, we're calling this from the syntax file we imported at the start.
span= syntax.span
width = syntax.width
height = syntax.height
font = syntax.font


# When saving files before uploading, we use a portion of the title name as the file name so we can easily call
# it. However, there are characters which mess us up when saving them so we remove them below.



# All the characters in chars_to_remove will mess up our method of using our titles for our file names
chars_to_remove = ['.', '!', '?','<','>','*','/',' ','+','|'

,'=','#','&','{','}']

def title_clean(postnumber):

    #Adapted code from stack, just removes the aforementioned characters from our title which
    #can then be used as the file name for the images later on
    
    subj = top_posts.loc[:,"Title"][postnumber]
    subj.translate(''.join(chars_to_remove))
    sc = set(chars_to_remove)
    ''.join([c for c in subj if c not in sc])

    #https://stackoverflow.com/questions/10017147/removing-a-list-of-characters-in-string


# Now we've been given a story from a user. We're not going  to post it all on one instagram photo 
# so we will do an album of photos and put a message on each page with the first page being the 
# title page of the story which we'll do later. They've also naturally inputted linebreaks to break 
# up the story nicely and it wouldn't be great to just throw all of these away when we're modifying our text.
# So the first steps will be tidying up the text so it fits into an instagram photo without ruining the 
# natural paragraphs the user gave us to break up their message.

# I'll be honest, below is the equivalent of using your nostril to hold a pen. It's not very clean but
# it can sometimes work.

def message_prepare(postnumber):
    
    # The biggest pain is keeping the user inputted linebreaks whilst also wrapping the text to fit

    # So we're going to 'tag' where our user has put in linebreaks with the § character. Which means
    # after we've wrapped all the text so it fits into nice images for instagram, we can turn the §'s back
    # into linebreaks so the story looks like how we started!

    # That being said if someone uses § in the post we're finished - call your loved ones it's all over.
    # I'm sure there's a better way to do this but call me dumbo because I'm all ears.


    # First we're going to grab a certain post out of our Pandas dataframe of top posts.
    # .loc basically locates a certain part of our data frame
    message=top_posts.loc[:,"Post Text"][postnumber]

    # &#x200B; is how a double linebreak is characterised, it cropped up a bit so we're giving it the same
    # treatment as the linebreaks which are distinguished by \n

    message_005=message.replace("&#x200B;","§") 

    message_1=message_005.replace("\n","§") 

    # Right now we're splitting up our text into different chunks separated by these breaks
    # This means we will essentially have a list of paragraphs that the original reddit poster intended.

    message_array=re.split(r'§', message_1)

    
    # And now we're poaching each of these bits into a nice array because who likes lists right?
    message_af=[x for x in message_array if x]

    # Now there's a possible issue:

    # If the user is writing a sentence, then puts a linebreak in to start a new one
    # textwrap will keep counting the characters as if nothing has happened
    # so it'll just break the line halfway through so the first lines of paragraphs are always messy

    
    # As a fix we're going to tidy up each of these chunks of message and wrap them individually
    # This might seem tedious but trust me it's a mess otherwise
 
    # This loop_message is where we're going to add each paragraph of the message after it's been tidied up.
    # Again by tidying up, I mean wrapping the text so it's only a certain number of characters.
    # The number of characters you want will depend on font and fontsize and desired margin size etc.
    loop_message=[]

    # Looping through our paragraphs above and tidying them.
    for i in range(len(message_af)):
        message_i= textwrap.fill(text=message_af[i], width=55,break_long_words=True,replace_whitespace=False)
        loop_message.append(message_i)
    
    # This now turns what we've tidied up above into a nice string where the lines are the length
    # we want them and they're separated by some nice linebreaks
    message_first=''
    for i in range(len(loop_message)-1):
    
        message_first= message_first+ loop_message[i]+ "\n" + "\n"


    # Now we've got another problem. We're not fitting all these messages on one page nor are we doing
    # one paragraph a page because often one page won't not hold a whole paragraph or we're just wasting space.

    # So we want to split up these messages depending on how many lines we have which can 
    # happen halfway through a paragraph, so we need to split up our messages AGAIN...

    # We'll split up the message as a whole after a certain number of linebreaks so we won't go past the image

    # Span is how many lines you can fit on the page depending on your font so this will just
    # split it up into nice groups of 23 lines + the final one which should be less

    words = message_first.split("\n")
    split_result=["\n".join(words[i:i+span]) for i in range(0, len(words), span)]

    

    # Voila! Tidied text where each element of split_result is text ready to put onto a single instagram photo.

    return split_result

    
    
   
# This function is just for creating our title page image which we post first 
# and which has the title on it... obviously

# Currently working on centering the text on the title_page but slowly slowly and all that.
def title_page(postnumber):

    
    # Grab the title from the post we're interested in
    title_uw=top_posts.loc[:,"Title"][postnumber]

    # Wrap the title of the post, we don't really need to worry about linebreaks here.
    title=textwrap.fill(text=title_uw, width=30,break_long_words=True,replace_whitespace=False)

    # Write our title with the same font as our text and variable size (will need tweaking)
    title_font= ImageFont.truetype(font, 60)

    # We're removing the weird characters from the title BUT this is just for the file name, not the post.
    image_name= title_clean(postnumber)


    # This is where we're going to save our title_page image. 
    # Please note the message pages and the title pages will have the same 'name' but distinguished by the
    # parts at the end of the file name, note the title.jpeg end to the string below.

    title_directory=directory+'\images\{}title.jpeg'.format(image_name)

    img = Image.new('RGB', (width, height), color='black')

    imgDraw = ImageDraw.Draw(img)

    imgDraw.text((10, 10), title, font=title_font, fill=(200, 217, 227))

    img.save(title_directory, 'JPEG') 




# This generates our images with the post text! If we generate 9+ images here then we won't be able to post
# because of instagram limits. That being said we could look into doing part 1 part 2 posts but 
# that'd be quite a bit of code for a very rare event and I'm a lazy dog.
def message_page(postnumber):


    # Now this is a very similar setup as for the title page but we're doing it for each message page

    # We will put the text from each part of split_result onto its own image and put these together in an
    # album. But we need to save each one and then upload them in the correct order so we index the filenames
    split_result=message_prepare(postnumber)

    for i in range(len(split_result)):

        message= split_result[i]

        message_font= ImageFont.truetype(font, 40)

        # We're re-using title_clean to tidy up the filenames for our individual messages
        image_name= title_clean(postnumber)

        img = Image.new('RGB', (width, height), color='black')

        imgDraw = ImageDraw.Draw(img)

        imgDraw.text((10, 10), message, font=message_font, fill=(200, 217, 227))

    
        # Note the second part of the format bracket that is indexing each message image.
        message_directory=directory+'\images\{}message{}.jpeg'.format(image_name,i)



        img.save(message_directory, 'JPEG')


# Now we also need to make sure before we upload a story that we haven't uploaded it before. You could 
# of course remove dupes by hand on the instagram website, but I think keeping a history of posts by
# their title names is much better. Also useful incase a reddit user steals an old story and reposts it.
def history_check(title):

# This checks if we've posted the post we're about to post before (if you'll pardon the posts)
# Not sure how this'll look after hundreds of post but for the scale of this I don't think it's a 
# huge issue.

# This is a chunk of code that reads our history file and sees if our inputted title has been posted before.
    with open(r'history.txt', 'r') as fp:
        # read all lines in a list
        lines = fp.readlines()
        value=0 # 0 means we haven't seen that title before
        for line in lines:
            # check if string present on a current line
            if line.find(title) != -1:
                value=1 #1 means have seen that title before
                
  
    return value


# This takes all our hard work and actually posts it! 
# Don't forget this bit that would just be embarassing
def bot_post(postnumber):
    

    # This is just from instagrapi, the client is essentially an instagram user doing this on your behalf.

    bot = Client()

    # Again, private information to login to instagram.
    # If mobile/email verification is needed, instagrapi will request it in the terminal so don't worry
    # about that.
    bot.login(config.username, config.password)

    # Get our title
    title_uw=top_posts.loc[:,"Title"][postnumber]


    # Name our images that we're going to save
    image_name= title_clean(postnumber)

    # Now we have to be careful when using the instagram api to posts multiple photos, which is an album.
    # We need to tell it the directory of each thing we're going to post so first we're going to say
    # Hey here's where the first thing to post is, which is the title.
    # and then after we're appending this with the location of each message we're going to post.
    album_path=[directory+'\images\{}title.jpeg'.format(image_name)]


    # This adds the locations of where all our images are going to be when we generate them to our album_path
    for i in range(len(message_prepare(postnumber))):
        album_path.append(directory+'\images\{}message{}.jpeg'.format(image_name,i))


    # Now we upload each of these images that are in our album_path directory.
    # However note we have not created any images yet! We will create them and place them in the directories
    # above very nicely. This will happen in the full_monty function as we want to be careful making sure
    # our post is suitable before we feed it to the bot to upload.

    # Note that you can also choose the caption of the post, which I've chosen to be the title of the story
    # which I think is nice.
    # You can check out https://adw0rd.github.io/instagrapi/usage-guide/media.html to see what else you can do
    # You can put tags/ location for the posts if you're interested.

    bot.album_upload(
        album_path,
        caption = title_uw
        )
    
    file_object = open('history.txt', 'a')
    file_object.write(title_uw+',')



# This is the uber function that uses all the ones from above, but sequences our checks on stuff that
# would mess up a post (is it too big/have we already done it) so we won't get an error message
# and our code will just keep running!

# This is well and truly, the full monty.
def full_monty():

    # v is a counter for how many successful posts we have to make sure we hit the requested value below.
    v=0 
    # i is a counter for where we are in our list of posts. If something isn't suitable, we move onto the next.
    i=0
    # This asks you how many posts you'd like to do.
    val = int(input("How many posts would you like to do today? \n"))

    # This first while makes sure we don't try and post a message we haven't loaded in. 
    while i<=limit:
        # Otherwise we will keep running the code until we hit the required number of posts
        while v<val:
            
            # We first check if we've had the post before: 1 if yes, 0 if no.
            title_i=top_posts.loc[:,"Title"][i]
            check=history_check(title_i)

            
            if check==1:
                print("We've already had post",i)

                # i+=1 means we continue to the next post
                i+=1

            # This means we can continue with our post
            if check==0:

                # We first generate the messages for each image we have
                message=message_prepare(i)

                # We can only have 9 message images as instagram only allows 10 photos, one of which we're
                # using for the title page at the start.

                if len(message)<=9:
                    print('Post',i,'is small enough to be uploaded')
                    
                    # We now generate the title and message images
                    title_page(i)
                    message_page(i)

                    # We now post the title and message images
                    bot_post(i)
                    print('Successfully posted post',i)

                    # Move onto next post and note we've had a successful post with v
                    i+=1
                    v+=1
                
                
                
            
                else:
                    print('Post',i,'had too many pages')
                    i+=1

    print("Post complete") 





full_monty()