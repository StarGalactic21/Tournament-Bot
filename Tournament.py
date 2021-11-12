import discord
import os
from dotenv import load_dotenv
from pymongo import MongoClient
#setup
mongo_client=MongoClient()
mongo_client = MongoClient()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
client = discord.Client(intents=intents)

#create database
database=mongo_client['Tournament']

import math
  
def checkifUserExists(utag):
    guild = client.get_guild()
    #go through our member list and check if the members exist
    
    for member in guild.members:

            if str(member)==utag:
                return 1

    return 0


# Function to calculate the Probability
def Probability(rating1, rating2):
  
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))
  
  
# Function to calculate Elo rating
# K is a constant.
# d determines whether
# Player A wins or Player B. 

#returns a list of updated ELO ranks
def EloRating(Ra, Rb, K, d):
   
  
    # To calculate the Winning
    # Probability of Player B
    Pb = Probability(Ra, Rb)
  
    # To calculate the Winning
    # Probability of Player A
    Pa = Probability(Rb, Ra)
  
    # Case -1 When Player A wins
    # Updating the Elo Ratings
    if (d == 1) :
        Ra = Ra + K * (1 - Pa)
        Rb = Rb + K * (0 - Pb)
      
  
    # Case -2 When Player B wins
    # Updating the Elo Ratings
    else :
        Ra = Ra + K * (0 - Pa)
        Rb = Rb + K * (1 - Pb)
      

    return [Ra,Rb]
  
def checkIfUserIsCaptain(utag,clanname):
    clanscollection=database["clans"]
    cursor=clanscollection.find({'ClanName':clanname})
    result=list(cursor)
    utag=str(utag)
    for x in result:
      print(x["ClanMembers"][0],x["ClanMembers"][1],utag)
      if x["ClanMembers"][0]==utag or x["ClanMembers"][1]==utag:
        return 1
      else:
        return 0
        
    return 0


def searchClanInDatabase(clan):
    clanscollection=database["clans"]
    cursor=clanscollection.find_one({'ClanName':clan})
    return cursor

#function which search the database in the form X declared Y
def searchWars(first_clan,second_clan):
    clanscollection=database["wars"]
    cursor=clanscollection.find({'DeclaringClan':first_clan,'DeclaredClan':second_clan,'Status':'Pending'})
    result=list(cursor)
    #check if we can find the war
    if len(result)==0:
        return 0

    else:
      return result

      
def checkIfClanExists(clan):
    clanscollection=database["clans"]
    instance=clanscollection.count_documents({'ClanName':clan})
    return instance



#registers a new clan into the tournament
def register_clan(message):
    #ignore the register_clan command, and split by comma
    args=message.content.split(",")
    #get members and clan name
    members=args[2:None]
    clan_name=str(args[1])
    response=""
    #if we have less than 3 members, return
    
    if len(members)<3:
      response='You cannot register a subclan with less than 3 members. Atleast 2 captains and 1 member needed'
      return response


    #get the clans collection and check if the clan already exists
    clanscollection=database["clans"]
    cursor=clanscollection.find({'ClanName':clan_name,'ClanMembers':members})
    existingclan=list(cursor)

    #check if the clan exists in our dictionary
    if len(existingclan)!=0:
      response='clan already registered'
  
    #add a new subclan with a starting ELO of 1000
    else:
      captains=members[0:2]
      if checkifUserExists(captains[0])==1 and checkifUserExists(captains[1])==1:
        record={'ClanName':clan_name,'ClanMembers':members,'elo_standing':1000}
        x=clanscollection.insert_one(record)
        response='Clan has been registered'
      else:
        response="Could not register. Captains are not valid tags/not in the server"
    
    return response


#function which displays clans
def show_clans(message):
  #get the index of our clans collection
    clanscollection=database["clans"]
    str_message=""
    #go through each entry in our hash table
    cursor=clanscollection.find()
    clans=list(cursor)
    for x in clans:
      clan_name=x["ClanName"]
      list_members=x["ClanMembers"]
      members = ','.join(list_members)
      str_message=str_message+clan_name+"\t\t"+members+"\n"
    return str_message


#displays each clan and their respective ELO
def show_rankings(message):
    clanscollection=database["clans"]
    counter=1
    str_message=""
    rankings={}
    #go through each entry in our hash table
    cursor=clanscollection.find()
    clans=list(cursor)
    for x in clans:
      clan_name=x["ClanName"]
      ELO=x["elo_standing"]
      rankings[clan_name]=ELO
    counter=1
    rankings=sorted(rankings.items(), key=lambda x: x[1], reverse=True)
    for x in rankings:
        clan_name=x[0]
        ELO=x[1]
        str_message=str_message+str(counter)+"."+str(clan_name)+"("+str(ELO)+")"+"\n"
        counter=counter+1

    return str_message



def show_pendingwars(message):
    warsscollection=database["wars"]
    counter=1
    str_message=""
    #go through each entry in our hash table
    cursor=warsscollection.find({'Status':'Pending'})
    clans=list(cursor)
    for x in clans:
      declaringclan=x["DeclaringClan"]
      declaredclan=x["DeclaredClan"]
      str_message=str_message+str(counter)+"."+declaringclan+" vs "+declaredclan+"\n"
      counter=counter+1
    return str_message

def show_scheduledwars(message):
    warsscollection=database["wars"]
    counter=1
    str_message=""
    #go through each entry in our hash table
    cursor=warsscollection.find({'Status':'Scheduled'})
    clans=list(cursor)
    for x in clans:
      declaringclan=x["DeclaringClan"]
      declaredclan=x["DeclaredClan"]
      str_message=str_message+str(counter)+"."+declaringclan+" vs "+declaredclan+"\n"
      counter=counter+1
    return str_message

  
#function which starts a clan war
def clan_war(message):
    args=message.content.split(",")
    print(len(args))
    if len(args)!=3:
      return "invalid command"

    declaring_clan=args[1]
    declared_clan=args[2]
    str_message=""


    #check if the declaring clan is registed
    if checkIfClanExists(declaring_clan) == 0:
       str_message=str(declaring_clan)+" is not a registered clan"
       return str_message
    
    #check if the clan which was declared is registered
    if checkIfClanExists(declared_clan) == 0:
       str_message=str(declared_clan)+" is not a registered clan"
       return str_message


    #add the clan war to our wars collection
    else:
      # wars[declaring_clan]=declared_clan
      # str_message="Clan war scheduled"

      #check if the user submitting the war request is a captain
      if checkIfUserIsCaptain(message.author,declaring_clan)==0:
        return ("You are not a registered captain of: "+str(declaring_clan))

      #insert war into our war database
      else:
        record={'DeclaringClan':declaring_clan,'DeclaredClan':declared_clan,'Status':'Pending'}
        warscollection=database["wars"]
        x=warscollection.insert_one(record)
        str_message='War has been declared by '+declaring_clan+". Captain from "+declared_clan+" must accept before the war can continue."
    
    return str_message


#function which displays help
def _help():
  help_message="List of supported commands"
  registerclan="\n$register_clan:registers a new clan, ie $register_clan eXer Aero(C) Astronaut(C)"
  showclans="\n$show_clans: shows the clans currently registered"
  clan_war="\n$clan_war: war declare, ie $clan_war eXer TA"
  str_message=help_message+registerclan+showclans+clan_war
  return str_message
#function which updates elo in database
def update_Elo(winningclan,losingclan):
      clansCollection=database["clans"]
      Firstclan=searchClanInDatabase(winningclan)
      Secondclan=searchClanInDatabase(losingclan)
      FirstclanMMR=Firstclan["elo_standing"]
      SecondclanMMR=Secondclan["elo_standing"]

      ELOChange=EloRating(FirstclanMMR,SecondclanMMR, 30, 1)
        #update ELO standings in the dictionary
      print(ELOChange[0],ELOChange[1])
      clansCollection.update_one({'ClanName':winningclan},{"$set":{'elo_standing':ELOChange[0]}})
      clansCollection.update_one({'ClanName':losingclan},{"$set":{'elo_standing':ELOChange[1]}})

def accept_declaration(message):
    args=message.content.split(",")
    warscollection=database["wars"]
    #if we have less than 2 arguments, return
    if len(args)!=4:
      return "invalid command"
    declaredClan=str(args[1])
    str_message=str(args[2])
    declaringClan=str(args[3])

    if checkIfUserIsCaptain(message.author,declaredClan)==0:
      return ("You are not a registered captain of: "+str(declaredClan))

    if str_message=="accept":
     war=searchWars(declaringClan,declaredClan)     
     if war==0:
       return "war does not exist"
     else:
        warscollection.update_one({'DeclaringClan':declaringClan,'DeclaredClan':declaredClan,'Status':'Pending'},{"$set":{'Status':'Scheduled'}})
        return "war between "+declaredClan+ " and " + declaringClan + " has been confirmed"


#submit a win or loss
def submit_result(message):
    clansCollection=database["clans"]
    warscollection=database["wars"]
    #tokenize message
    #messages should be in the form of x _beat y
    args=message.content.split(",")
    #if we have less than 2 arguments, return
    if len(args)!=4:
      return "invalid command"
    Firstclan=str(args[1])
    decision=str(args[2])
    Secondclan=str(args[3])
    #make sure the clans exist in the DB before checking captains
    if len(searchClanInDatabase(Firstclan)) == 0:
      str_message=str(Firstclan)+" is not a registered clan"
      return str_message
    
    #check if the clan which was declared is registered
    if len(searchClanInDatabase(Secondclan)) == 0:
      str_message=str(Secondclan)+" is not a registered clan"
      return str_message

    #if beat is called
    if decision=="_beat":

      #if the user is not a captain, ignore the war request
      if checkIfUserIsCaptain(message.author,Firstclan)==0 and checkIfUserIsCaptain(message.author,Secondclan)==0:
        return ("You are not a registered captain of: "+str(Firstclan)+" or "+str(Secondclan))

      #otherwise submit the war result
      else:

    #look for the war declaration
        resultNumber=warscollection.count_documents({'DeclaringClan':Firstclan,'DeclaredClan':Secondclan, 'Status':'Scheduled'})
        
      #try both combinations of declaring clan and declared clan
        if resultNumber==1:
             update_Elo(Firstclan,Secondclan)
             warscollection.update_one({'DeclaringClan':Firstclan,'DeclaredClan':Secondclan, 'Status':'Scheduled'},{"$set":{'Status':'Done'}})
             return "War concluded"
        else:
          resultNumber=warscollection.count_documents({'DeclaringClan':Secondclan,'DeclaredClan':Firstclan})
          if resultNumber==1:
                update_Elo(Firstclan,Secondclan)
                warscollection.update_one({'DeclaringClan':Secondclan,'DeclaredClan':Firstclan, 'Status':'Scheduled'},{"$set":{'Status':'Done'}})
                return "War concluded"
          else:
            return "Could not find war"

 


    



@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  response=""
  if message.author ==client.user:
    return

#method to register a new clan

  if message.content.startswith('$register_clan'):
    response=register_clan(message)
    await message.channel.send(response)
  
    
  #check if a user wants to show clans
  elif message.content.startswith('$show_clans'):
    await message.channel.send('Showing Clans. . .')
    await message.channel.send('Clan Name\tMembers\n')
    response=show_clans(message)
    #error check if there are no subclans
    if len(response)>0:
      await message.channel.send(response)
    else:
      return

  #check if user wants to see rankings
  elif message.content.startswith('$show_rankings'):
    await message.channel.send('Leaderboards')
    response=show_rankings(message)

    #check if the response is null(no subclans registered)
    if len(response)>0:
      await message.channel.send(response)
    else:
      return   

  #check if user wants to see wars
  elif message.content.startswith('$show_pendingwars'):
    await message.channel.send('Current Wars which have not been confirmed: ')
    response=show_pendingwars(message)

    #check if the response is null(no subclans registered)
    if len(response)>0:
      await message.channel.send(response)
    else:
      return
  elif message.content.startswith('$show_scheduledwars'):
    await message.channel.send('Current Wars which have been scheduled: ')
    response=show_scheduledwars(message)

    #check if the response is null(no subclans registered)
    if len(response)>0:
      await message.channel.send(response)
    else:
      return    


  elif message.content.startswith('$clan_war'):
    response=clan_war(message)
    await message.channel.send(response)
  
  elif message.content.startswith('$war_declaration'):
    response=accept_declaration(message)
    await message.channel.send(response)  
  
  elif message.content.startswith('$submit_result'):
    response=submit_result(message)
    await message.channel.send(response)

  elif message.content.startswith('$help'):
    response=_help()
    await message.channel.send(response)

    



client.run(TOKEN)

