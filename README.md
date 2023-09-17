# SCRABBLE GAME APP
#### Description:

Scrabble Game Application for players to use in conjunction with the Scrabble board game app. Contents include: a score keeper, a word checker, a game history page, and an about page. Users can login/make accounts to save their game info and stats.


Technologies used:
- Flask
- Python
- HTML
- CSS
- JavaScript
- sqlite3

Page details
- index.html: Score keeper, dynamically creates a table based on the selected number of players. On change of every score, the totals row will sum up all the scores auto update. 
    - At the end of the game, if a player was previously logged in, it will allow you to save the game into your user database based on logged in user id. 

- gamehistory.html: All your saved games can be viewed under game history. It shows the: date, duration, total moves, player names, scores, and winner. Pulls data from scores.db based on logged in user id.

- scores.db: sqlite database that stores 
    1. User's login id, username, and hashed password
    2. User's saved games: date, duration, total moves, player names, scores, and winner 

- checker.html: The word checker page has an input where you can submit words to check their validity. The submitted word is passed to python which reads a dictionary line by line to see if the word is in the dictionary. 
    - If valid, a success message and a check meaning button appears that will google search the word definition. 
    - If invalid, an invalid word message appears
    - If input was empty, it asks users to enter a word
- Below there is a simple infographic on 2 letter scrabble words

- Users can login or register an account from the navbar, both pop up a modal that submits the info to the user database.
- change.html: If logged in, users can change their password under the dropdown bar.
- The login, register, and change password interfaces all have validation checks to prevent errors
- Log out will clear user session and redirect back to the main page

- about.html: the about page contains 3 columns on a brief history of how Scrabble came to be, and its current popularity.

- collins.txt: A 2019 Collins Scrabble Dictionary which is used to check word validity on the checker.html page. Read line by line with Python to search for the word.

- layout.html: contains the template of the pages, including the navbar (logo, links, modals), footer, and other functions eg. flash message function. Included in every html page

- helpers.py: has apology function which returns an error message if there is an internal server error

- static folder: includes all the photos used in the webpage. Logo, favicon, 2 letter scrabble words. Also includes the css file linked to layout.html

- app.py: 
    - For all the GET and POST requests, returns and renders templates for the webpages. 
    - Checks for valid words by reading collins.txt file
    - Checks for valid user login/register
    - Also connects to the database to enter user inputted data and select user data for the game history page. 