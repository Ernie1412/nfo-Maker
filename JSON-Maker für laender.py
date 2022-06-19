import os,json
pfad = os.path.dirname(os.path.abspath(__file__))
daten={
    "laender":{
                "France":"Frankreich",
                "Italy":"Italien",
                "Netherlands":"Niederlande",
                "Sweden":"Schweden",
                "Denmark":"Dänemark",
                "Argentina":"Agentinien",
                "Brazil":"Brasilien",
                "Bulgaria":"Bulgarien",
                "Canada":"Kanada",
                "Germany":"Deutschland",
                "Hungary":"Ungarn",
                "Japan":"Japan",
                "Poland":"Polen",
                "Spain":"Spanien",
                "Ukraine":"Ukraine",
                "USA":"USA",
                "UK":"Großbritannien",
                "West Germany":"Deutschland",
                "United States":"USA",
                "World-wide":"Weltweit",
                "Europe":"Europa",
                "Australia":"Australien",
                "Finland":"Finnland",
                "Venezuela":"Venezuela",
                "Russia":"Russland"
                },
    "sprachen":{
                "1":"deutsch",
                "2":"italienisch",
                "3":"englisch",
                "4":"französisch",
                "5":"spanisch",
                "6":"japanisch",
                "7":"portogiesisch",
                "8":"russisch",
                "9":"polnisch",
                "10":"niederländisch",
                "11":"norwegisch",    
    }
    }

json.dump(daten,open(pfad+"\\JSON\\laender.json",'w'),indent=4, sort_keys=True)
d=[]
with open(pfad+"\\JSON\\laender.json",'r') as file:
            d = json.loads(file.read())
laender=d["laender"]
print(d)