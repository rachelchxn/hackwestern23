from gptSummary import getSummary
from firebase import create_document, read_document

print(getSummary(''' "hey what's your name? my name is xander. Cool I am 25. I'm 32!'''))

# print(
# getSummary(f''' "hey what's your name?
#                 i'm rachel.
#                 nice to meet you rachel, I'm Xander.
#                 Nice to meet you too. What are you here for today.
#                 I'm trying to win this hackathon.
#                 Oh really? me too!
#                 Whoa! Let's team up and win together!
#                 Bet." ''')

# )

