# RetailDialogue
Retail-Dialogue is  a chatbot for an E-commerce platform 


How to run this app ? 
Step 1 : 
  Build the chatbot agent in DialogFlow Console
  Take the reference from the video ( https://youtu.be/2e5pQqBvGco?feature=shared ) 

Step 2 : 
  Make the flask App 
  run the main.py app by running command in terminal : uvicorn main:app --reload

Step 3 :
  Install ngrok app ( Ngrok convert normal http local port to https secure port that is accepted by DialogFlow ) 
  After installing ngrok open the ngrok and run command  ngrok http 8000 
  Run command will give new https secure local host link 

Step 4 :  
  Paste the ngrok link into fullfillment section in Webhook url 
  Save the link 

Step 5 : 
  Run the react app that is made in Nyxiee Folder 
