import json
from operator import indexOf
import requests
import functools

response=requests.get("https://api.opendota.com/api/heroes")


IdResponse = json.loads(response.text)
IdtoName={}

for item in IdResponse:
    IdtoName[item['id']]=item['localized_name']
#Take input of Names
a=input("Enter first hero")
b=input("Enter second hero")
c=input("Enter third hero")
d=input("Enter fourth hero")

#Convert names to id numbers from opendota
id1=[id for id,v in IdtoName.items() if v==a]
id2=[id for id,v in IdtoName.items() if v==b]
id3=[id for id,v in IdtoName.items() if v==c]
id4=[id for id,v in IdtoName.items() if v==d]


#get matchup for individual id numbers and gather winpercents from them
#this is for id1
concatHelper1=str(id1[0])
Matchuplink1="https://api.opendota.com/api/heroes/"+concatHelper1+"/matchups"

response=requests.get(Matchuplink1)
Matchup1=json.loads(response.text)

for item in Matchup1:
    winpercent=(int(item['wins'])/int(item['games_played']))*100
    item['winpercent1']=winpercent
    del item['games_played']
    del item['wins']
    

SortedMatchup1=sorted(Matchup1, key=lambda x: x['hero_id'])
for i in SortedMatchup1:
    if i['hero_id']==id4[0]:
        SortedMatchup1.remove(i)
    if i['hero_id']==id2[0]:
        SortedMatchup1.remove(i)
    if i['hero_id']==id3[0]:
        SortedMatchup1.remove(i)
    

#this is for id2
concatHelper2=str(id2[0])
Matchuplink2="https://api.opendota.com/api/heroes/"+concatHelper2+"/matchups"

response=requests.get(Matchuplink2)
Matchup2=json.loads(response.text)

for item in Matchup2:
    winpercent=(int(item['wins'])/int(item['games_played']))*100
    item['winpercent2']=winpercent
    del item['games_played']
    del item['wins']

SortedMatchup2=sorted(Matchup2, key=lambda x: x['hero_id'])
for i in SortedMatchup2:
    if i['hero_id']==id1[0]:
        SortedMatchup2.remove(i)
    if i['hero_id']==id3[0]:
        SortedMatchup2.remove(i)
    if i['hero_id']==id4[0]:
        SortedMatchup2.remove(i)
   

#this is for id3
concatHelper3=str(id3[0])
Matchuplink3="https://api.opendota.com/api/heroes/"+concatHelper3+"/matchups"

response=requests.get(Matchuplink3)
Matchup3=json.loads(response.text)

for item in Matchup3:
    winpercent=(int(item['wins'])/int(item['games_played']))*100
    item['winpercent3']=winpercent
    del item['games_played']
    del item['wins']

SortedMatchup3=sorted(Matchup3, key=lambda x: x['hero_id'])
for i in SortedMatchup3:
    if i['hero_id']==id1[0]:
        SortedMatchup3.remove(i)
    if i['hero_id']==id2[0]:
        SortedMatchup3.remove(i)
    if i['hero_id']==id4[0]:
        SortedMatchup3.remove(i)
    
#this is for id4
concatHelper4=str(id4[0])
Matchuplink3="https://api.opendota.com/api/heroes/"+concatHelper4+"/matchups"

response=requests.get(Matchuplink3)
Matchup4=json.loads(response.text)

for item in Matchup4:
    winpercent=(int(item['wins'])/int(item['games_played']))*100
    item['winpercent4']=winpercent
    del item['games_played']
    del item['wins']

SortedMatchup4=sorted(Matchup4, key=lambda x: x['hero_id'])
for i in SortedMatchup4:
    if i['hero_id']==id1[0]:
        SortedMatchup4.remove(i)
    if i['hero_id']==id2[0]:
        SortedMatchup4.remove(i)
    if i['hero_id']==id3[0]:
        SortedMatchup4.remove(i)
    


if len(SortedMatchup1)<119:
    SortedMatchup1.insert(118,{'hero_id': 137, 'winpercent1': 50})
if len(SortedMatchup2)<119:
    SortedMatchup2.insert(118,{'hero_id': 137, 'winpercent2': 50})
if len(SortedMatchup3)<119:
    SortedMatchup3.insert(118,{'hero_id': 137, 'winpercent3': 50})
if len(SortedMatchup4)<119:
    SortedMatchup1.insert(118,{'hero_id': 137, 'winpercent4': 50})
#Now we have hero id vs winpercents for all ids
#so we need to put them in a single list
SortedMatchup=SortedMatchup1
for i in SortedMatchup:
    i['winpercent2']=SortedMatchup2[SortedMatchup.index(i)]['winpercent2']
    i['winpercent3']=SortedMatchup3[SortedMatchup.index(i)]['winpercent3']
    i['winpercent4']=SortedMatchup4[SortedMatchup.index(i)]['winpercent4']
 

#now we can make a product of all winrates to get an idea of overall winrate(not average because multiplicative result gives more accurate result for effectiveness fo a hero)
for i in SortedMatchup:
    i['winproduct']=i['winpercent1']*i['winpercent2']*i['winpercent3']*i['winpercent4']
    del i['winpercent1']
    del i['winpercent2']
    del i['winpercent3']
    del i['winpercent4']
  
SortedWinproducts=sorted(SortedMatchup, key=lambda x: x['winproduct'])
#Now we can run a loop that returns hero names for all the ids in this list


for i in SortedWinproducts:
    print(IdtoName[i['hero_id']])
