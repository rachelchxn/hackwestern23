from functions.gptSummary import getSummary
from functions.firebase import create_document, read_document


# print(getSummary(''' "hey what's your name? my name is xander. Cool I am 25. I'm 32!'''))

data = {"test": "test"}
# param 
# data
# optional name of collection
# return the document id
doc_id = create_document(data)
print(doc_id)
print(read_document(doc_id))


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

