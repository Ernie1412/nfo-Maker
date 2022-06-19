# https://www.adultfilmdatabase.com 
#//p[@itemprop='name']              <--- Darsteller


import re,json
from pathlib import Path

from selenium.webdriver.common.by import By
### --------------------------------- Side scraping von allen Seiten -------------------------------------- ###
### ------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------------------- ###   
def Namensplit(txt):
    Art="";Alias="";Rolle=""
    x = re.split('\n+', txt, 3)
    name=x[0]
    if "(Credited: "in x[1]:
        Alias=x[1][0:-1].replace("(Credited: ","")
    else: x[2]=x[1]              
    if Art=="" and len(x[2])>1:Art=x[2]
    return name,Rolle,Alias,Art

def Titel_Scraping(Seite,driver):
    Name=""
    if Seite=="IAFD" or Seite=="IMDb":
        Name=driver.find_element_by_tag_name('h1').text
    return Name

def Datum_Aendern(Datum):             
        Monat={"Jan":"Januar",
               "Feb":"Feburar",
               "Mar":"März",
               "Apr":"April",
               "May":"Mai",
               "Jun":"Juni",
               "Jul":"July",
               "Aug":"August",
               "Sep":"September", 
               "Oct":"Oktober",
               "Nov":"November",
               "Dec":"Dezember"}       
        Datum=Datum.split()                       
        Tag=("0"+Datum[1].replace(",",""))[-2:]
        Datum=Tag+"."+Monat[Datum[0]]+" "+str(Datum[2])
        return Datum

def Regie_Scraping(Seite,driver):
    Regie=""
    if Seite=="IAFD":
            Regie=driver.find_element_by_xpath("//p[contains(.,'Director')]/following-sibling::p").text
    if Seite=="IMDb":
        try:
            Regie=driver.find_element_by_xpath("//a[contains(@href,'_dr')]").text
        except:    
            pass
    return Regie 

def ReleaseDatum_Scraping(Seite,driver):
    ReleaseDate="";Link2=""
    if Seite=="IAFD":
        ReleaseDate=driver.find_element_by_xpath("//p[contains(.,'Release Date')]/following-sibling::p").text
        if "No Data" not in ReleaseDate:
            Datum=Datum_Aendern(ReleaseDate)
        else: ReleaseDate=""
    if Seite=="IMDb":        
        ReleaseDate_Link=driver.find_element_by_xpath("//a[contains(@href,'releaseinfo?ref_=')]")
        ReleaseDate=ReleaseDate_Link.text                  
        try:
            DarstellerLink=driver.find_element_by_xpath("//a[contains(@href,'fullcredits/?')]")
            Link2=DarstellerLink.get_attribute("href")                            
        except:    
            pass
        infos = {
            'akaLink': ReleaseDate_Link.get_attribute("href"),
            'DarstellerLink': Link2,
            'Datum': ReleaseDate            
                }
        json.dump(infos,open(Path(__file__).absolute().parent / "JSON/url.json",'w')) 
    return ReleaseDate

def Sprache_Scraping(Seite,driver):
    Sprache=""
    if Seite=="IMDb":
            Sprache=""
    return Sprache 

def Land_Scraping(Seite,driver):
    Land=""
    if Seite=="IMDb":
        try:
            daten=[]             
            with open(Path(__file__).absolute().parent / "JSON/laender.json",'r') as file:
                daten = json.loads(file.read())
            laender=daten["laender"]
            Land=laender[driver.find_element_by_xpath("//a[contains(@href,'?country_of_origin=')]").text]                
        except:    
            pass
    return Land 
### ------------------------- AKA und Datum von Webside laden ---------------------------------------- ###
def AKA_Scraping(Seite,driver):
    Titel_art={
        "(original title)": "Original Titel",
        "alternative title)":"Alternativer Titel",
        "video title)":"Video Titel",
        "French title)":"französischer Titel",
        "English title)":"englischer Titel",
        "series title)":"Serien Titel",
        "reissue title)":"Neuauflagentitel",
        "original subtitled version)":"Original untertitelte Version",
        "cable TV title)":"Kabel TV Titel",
        "dubbed version)":"Dubbed Version",
        "long title)":"Langer Titel",
        "short title)":"kurzer Titel"}
    Also_Known_As=[];daten=[]    
    with open(Path(__file__).absolute().parent / "JSON/laender.json",'r') as file:
        daten = json.loads(file.read())
    laender=daten["laender"]
    ### ------------------------- alles von IAFD------------------------------------------------------ ###         
    if Seite=="IAFD":
        Also_Known_As=[]
        aka=driver.find_elements_by_xpath("//b[contains(.,'Also Known As')]/following-sibling::dd")
        for d in aka:
            for land in laender:        
                if " ("+land in d.text:
                    LandAKA=laender[land].strip()
                    Titel=d.text.replace("("+land,"").replace(")","")
                    break
                else:
                    Titel=d.text
                    LandAKA="" 
            Also_Known_As.append((Titel,"",LandAKA))
    ### ------------------------- alles von IMDb------------------------------------------------------ ###
    if Seite=="IMDb":                    
        # try:
        #     ReleaseDate=driver.find_element_by_xpath("//td[@class='release-date-item__date']").text
        # except:
        #     pass           
        try:
            AlsoKnownAs=driver.find_element_by_xpath("//div[@class='soda even']")
        except: 
            AlsoKnownAs=driver.find_elements_by_xpath("//h4[@id='akas']//following-sibling::table/tbody/tr")
            for i,a in enumerate(AlsoKnownAs):
                Land_Titel=a.find_element(By.XPATH, '//tr['+str(i+1)+']/td[@class="aka-item__name"]').text
                AKA_Titel=a.find_element(By.XPATH, '//tr['+str(i+1)+']/td[@class="aka-item__title"]').text
                AKA_complete=Land_Titel.split(" (")
                Land_AKA="";Art=""
                if AKA_complete[0][0]=="(" and AKA_complete[0][-1]==")":        
                    Art=Titel_art[AKA_complete[0]]        
                elif AKA_complete[0][0]!="(" and AKA_complete[0][-1]!=")" and len(AKA_complete)>1:
                    Land_AKA=laender[AKA_complete[0]]
                    Art=Titel_art[AKA_complete[1]]
                else:
                    Land_AKA=laender[AKA_complete[0]]                        
                Also_Known_As.append((AKA_Titel,Art,Land_AKA))
            pass
    return Also_Known_As
### ------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------------Szenen Infos holen -------------------------------------- ###
def Szenen_Scraping(Seite,driver):
    Szenen=[]
### ------------------------------------------------IAFD, IMDb hat keine Szenen Infos --------------------- ###
    if Seite=="IAFD":            
        Szenen_INT=driver.find_elements_by_xpath("//li[@class='w' or @class='g']")
        for i,Szene in enumerate(Szenen_INT):                
            s=Szene.text.split(". ")               
            s[0]=s[0].replace("Scene","Szene").replace(". ","") # von Scene zu Szene(deutsch) und Punkt weglassen
            Szenen.append((s[0],"","",s[1]))                           
    return Szenen
### -------------------------------------------------------------------------------------------------------- ###
### ----------------------------------------------Label + Distru von Side holen----------------------------- ###
def Label_Scraping(Seite,driver):
    Label=""
### ------------------------------------------------IAFD --------------------------------------------------- ###
    if Seite=="IAFD":
        try:
            Studio=driver.find_element_by_xpath("//p[contains(.,'Studio')]/following-sibling::p").text+"  " # Label
        except: Studio=""        
        Label=driver.find_element_by_xpath("//p[contains(.,'Distributor')]/following-sibling::p").text      # Distru
        if Studio!=Label:Distributor=Studio+"("+Label+")" 
### ------------------------------------------------IMDb --------------------------------------------------- ###
    if Seite=="IMDb":
        try:
            Studio=driver.find_element_by_xpath("//li[@data-testid='title-details-companies']")             # Label
            Studio1=Studio.find_element(By.TAG_NAME, 'li')
            Label=Studio1.text
        except:    
            pass          
    return Label
### -------------------------------------------------------------------------------------------------------- ###
### ------------------------------------Infos über Darsteller von Side holen ------------------------------- ###
def Darsteller_Scraping(Seite,driver):
    ergebnis=[]
### ------------------------------------------------IAFD --------------------------------------------------- ###
    if Seite=="IAFD":
        Performer=driver.find_elements_by_xpath("//div[@class='col-sm-12']/div/p")          # Darstellernamen
        for reihe,Performer_single in enumerate(Performer):
            block=Namensplit(Performer_single.text)                                    # Alias und Handlungsart splitten
            ergebnis.append(block) 
### ------------------------------------------------ IMDb -------------------------------------------------- ###
    if Seite=="IMDb":
        Darstellers=driver.find_elements_by_xpath("//tr[@class='odd' or @class='even']")    # Darstellernamen
        for i,a in enumerate(Darstellers):
            name=a.find_element(By.CSS_SELECTOR, 'img')                
            Rolle_Alias=a.find_element(By.CSS_SELECTOR, 'td.character').text.replace("(uncredited)","").split(" (as ")   # Rollenname und Alias splitten    
            if Rolle_Alias[0]=="":
                Rolle="";Alias=""
            elif Rolle_Alias[0][-1]==")":
                Rolle="";Alias=Rolle_Alias[0][4:-1]
            elif len(Rolle_Alias)==1:
                Rolle=Rolle_Alias[0];Alias=""
            else:
                Rolle=Rolle_Alias[0];Alias=Rolle_Alias[1][:-1]                               
            ergebnis.append((name.get_attribute("title"),Rolle,Alias,""))                          
    return ergebnis
### -------------------------------------------------------------------------------------------------------- ###
### --------------------------------- ENDE --------------------------------------###
### -----------------------------------------------------------------------------###        
      