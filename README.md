# boboscraper
This library was set up to web scrape and format it for upload to social media such as instagram by utilising their respective APIs.



Hello everyone! 

Welcome to my scraper

I just want to first get you introduced to all the files broadly and we can jump in deeper if need be

1) History.txt file: This keeps track of all the posts that you've uploaded to instagram (or whatever service you end up choosing). At the moment, I've just been deleting posts on the instagram directly as I do some random quality checks but there's most likely a way to do that using the instagrapi (the API we use to interact with instagram) so it will also remove the post from the history file so you can try again in the future. This is my README so I'm allowing run on sentences sorry.

2) Script.py: This is the actual script that grabs the reddit stories, formats them, and then uploads them. The script itself will involve heavy commenting so you can hopefully follow along. Please feel free to reach out if there's any difficulties here/ inconsistencies/ room for improvement!

3) syntax.py: This has all the syntax and style choices you might need in this process. It's quite limited right now but I wanted to include it as it has a similar structure to the config.py file I've got. You won't be able to see this file as it contains sensitive information to login to the instagram but it has the same strucutre as the syntax file.


PRAW LOGIN:

I've included a couple of steps so you can access the Reddit API:

1) Go to this address ---> https://www.reddit.com/prefs/apps
2) Either create a new account for scraping (reccomended) or use your own and login
3) You should see in a grey box either in the top left or bottom left (it moves about) with the
    unsettling question: "are you a developer? create an app..."
4) Fill out the details as you so wish but make sure you select script before creating the app
5) You should then get a card of data. Consider it your bot's passport to go to Reddit on your
    behalf. Make note of all the information! Or consider your passport lost.
6) I would then suggest having a secure config.py which has all your information such as:
    client_id="random numbers and letters"
    client_secret="you guessed it more random numbers and letters"
    user_agent="whatever you had chosen to name it in the API stage"
7) You can then import this file at the start of your script to call this info securely.
