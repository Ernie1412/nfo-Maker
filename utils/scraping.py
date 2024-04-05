import re,json
from pathlib import Path

from lxml import html
from playwright.sync_api import sync_playwright


from collections import namedtuple
WebDriverResult = namedtuple('WebDriverResult', ['driver', 'status_bar'])

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

### --------------------------------- Side scraping von allen websiten -------------------------------------- ###
### ------------------------------------------------------------------------------------------------------- ###
### ------------------------------------------------------------------------------------------------------- ###   
class Scraping():
    def block_banner(self, route):  
            if "revive.iafd.com/www/delivery/asyncspc.php?" in route.request.url:            
                route.abort()
            else:
                route.continue_()

    def open_url(self, url):
        with sync_playwright() as p:            
            page_content: str=None  
            errview: str=""         
            browser = p.chromium.launch(headless=False)
            page = browser.new_page() 
            page.set_extra_http_headers(HEADERS) 
            page.route("**/*", lambda route: self.block_banner(route))
            try:                               
                page.goto(url, wait_until="domcontentloaded")
                page.query_selector("div.col-xs-12 > h1")                
            except Exception as e: 
                errview = f"TimeOutError: {e}"
            else:
                if any(keyword in page.content() for keyword in ["500 - Internal server error"]):
                    return "Error: 500 - Internal server error", page_content
                if any(keyword in page.content() for keyword in ["The page you requested was removed", "invalid or outdated page"]):
                    self.search_methode=True
                    return "invalid", None                           
                page_content = html.fromstring(page.content()) 
            finally:
                browser.close()
            return page_content
    def get_movie_title(self, website, content):
        text: str=""
        serie: str=""
        if website=="IAFD" or website=="IMDb":        
            text = self.get_text_from_xpath('//h1', content)
        if text[len(text):-1].isdigit():
                serie=text[:text[:-1].rfind(" ")]
        return text, serie

    def get_text_from_xpath(self, xpath_tag, content):
        element=content.xpath(xpath_tag)
        text = element[0].text_content().strip() if len(element)>0 else ""        
        return text

    def change_date(self, date):             
            mounths={"Jan":"Januar",
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
            date=date.split()                       
            day=("0"+date[1].replace(",",""))[-2:]
            date=day+"."+mounths[date[0]]+" "+str(date[2])
            return date

    def get_regie(self, website, content):
        regie: str=""
        if website=="IAFD":
                regie = self.get_text_from_xpath("//p[contains(.,'Director')]/following-sibling::p | //p[contains(.,'Directors')]/following-sibling::p", content)
        if website=="IMDb":
            try:
                regie = self.get_text_from_xpath("//a[contains(@href,'_dr')]", content)
            except:    
                pass
        return regie

    def get_releasedate(self, website, content):
        release_date: str=""
        artist_link: str=""
        if website=="IAFD":
            release_date = self.get_text_from_xpath("//p[contains(.,'Release Date')]/following-sibling::p", content)
            if "No Data" not in release_date:
                date = self.change_date(release_date)
            else: release_date=""
        if website=="IMDb":        
            release_date = self.get_text_from_xpath("//a[contains(@href,'releaseinfo?ref_=')]", content)                          
            try:
                artist_link_element=content.xpath("//a[contains(@href,'fullcredits/?')]")
                artist_link=artist_link_element.get_attribute("href")                            
            except:    
                pass
            infos = {
                'akaLink': "",
                'DarstellerLink': artist_link,
                'Datum': release_date            
                    }
            json.dump(infos, open(Path(__file__).absolute().parent / "JSON/url.json",'w')) 
        return release_date

    def get_language(self, website ,content):
        language=""
        if language=="IMDb":
            language=""
        return language 

    def get_country(self, website, content):
        country_german: str=""
        if website=="IMDb":
            try:
                daten: list=[]             
                with open(Path(__file__).absolute().parent / "JSON/laender.json",'r') as file:
                    daten = json.loads(file.read())
                laender=daten["laender"]
                country_english = self.get_text_from_xpath("//a[contains(@href,'?country_of_origin=')]", content)
                country_german=laender[country_english]                
            except:    
                pass
        return country_german 
    ### ------------------------- AKA und Datum von Webside laden ---------------------------------------- ###
    def get_aka(self, website, content):
        title_type = self.get_title_type()
        also_known_as: list=[]
        daten: list=[]    
        with open(Path(__file__).parents[1] / "JSON/laender.json",'r') as file:
            daten = json.loads(file.read())
        countries = daten["laender"]
        ### ------------------------- alles von IAFD------------------------------------------------------ ###         
        if website=="IAFD":
            also_known_as: list=[]
            akas = content.xpath("//b[contains(.,'Also Known As')]/following-sibling::dd")        
            for aka in akas:
                aka_single = aka.text_content().strip()
                for country in countries:
                    country_text = f" ({country}"        
                    if country_text in aka_single:
                        also_know_as_country = countries[country].strip()
                        title = aka_single.replace(country_text, "").replace(")", "")
                        break
                    else:
                        title = aka_single
                        LandAKA = "" 
                also_known_as.append((title,"",LandAKA))
        ### ------------------------- alles von IMDb------------------------------------------------------ ###
        if website=="IMDb": 
            try:
                also_known_as=self.get_text_from_xpath("//div[@class='soda even']", content)
            except: 
                also_known_as=self.get_text_from_xpath("//h4[@id='akas']//following-sibling::table/tbody/tr", content)
                for i,aka in enumerate(also_known_as):
                    country_from_title=self.get_text_from_xpath('//tr['+str(i+1)+']/td[@class="aka-item__name"]', aka)
                    aka_title=self.get_text_from_xpath('//tr['+str(i+1)+']/td[@class="aka-item__title"]', aka)
                    AKA_complete=country_from_title.split(" (")
                    Land_AKA=""
                    Art=""
                    if AKA_complete[0][0]=="(" and AKA_complete[0][-1]==")":        
                        Art=title_type[AKA_complete[0]]        
                    elif AKA_complete[0][0]!="(" and AKA_complete[0][-1]!=")" and len(AKA_complete)>1:
                        Land_AKA=self.laender[AKA_complete[0]]
                        Art=title_type[AKA_complete[1]]
                    else:
                        Land_AKA=self.laender[AKA_complete[0]]                        
                    also_known_as.append((aka_title,Art,Land_AKA))
                pass
        return also_known_as

    def get_title_type(self):
        return {
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
    ### ------------------------------------------------------------------------------------------------------- ###
    ### ----------------------------------------------Szenen Infos holen -------------------------------------- ###
    def get_scenen(self, website ,content):
        scene_list=[]
    ### ------------------------------------------------IAFD, IMDb hat keine Szenen Infos --------------------- ###
        if website=="IAFD":            
            scenen = content.xpath("//div[@id='sceneinfo']/table[@class='table']/tbody/tr/td[@colspan='3']")
            for i, scene in enumerate(scenen, start=1): 
                scene_list.append({'nr': f"Szene {i}", 'name': scene.text_content().strip()})                           
        return scene_list
    ### -------------------------------------------------------------------------------------------------------- ###
    ### ----------------------------------------------Label + Distru von Side holen----------------------------- ###
    def get_label(self, website ,content):
        label=""
    ### ------------------------------------------------IAFD --------------------------------------------------- ###
        if website=="IAFD":
            try:
                studio = self.get_text_from_xpath("//p[contains(.,'Studio')]/following-sibling::p", content)+"  " # Label
            except: studio=""        
            label = self.get_text_from_xpath("//p[contains(.,'Distributor')]/following-sibling::p", content)      # Distru
            if studio != label:
                distributor = f"{studio}({label})" 
    ### ------------------------------------------------IMDb --------------------------------------------------- ###
        if website=="IMDb":
            try:
                studio = self.get_text_from_xpath("//li[@data-testid='title-details-companies']", content)             # Label
                studio1 = self.get_text_from_xpath( 'li', studio)
                label = studio1
            except:    
                pass          
        return label
    ### -------------------------------------------------------------------------------------------------------- ###
    ### ------------------------------------Infos über Darsteller von Side holen ------------------------------- ###
    def get_performers(self, website, content):
        if website == "IAFD":        
            performers = []            
            artists = content.xpath("//div[contains(@class,'castbox')]/p/a/br")
            aliases = content.xpath("//div[contains(@class,'castbox')]/p")

            for artist, alias in zip(artists, aliases):            
                name = artist.tail.strip()  
                alias_name = alias.xpath("./i/text()")[0] if alias.xpath("./i/text()") else ""            
                if alias_name:
                    br = alias.xpath("./br[2]")
                else:
                    br = alias.xpath("./br[1]")                    
                skill = br[0].tail.strip() if br[0].tail else ""                 
                performers.append({"name": name, "skill": skill, "alias": alias_name})
            return performers
      