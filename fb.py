import requests
import json
import os , time
from bs4 import BeautifulSoup

class FB:
    def __init__(self):
        # session start
        self.session = requests.session()
        # m.facebook.com URL to get non script access to facebook
        # non-script access to bypass encpass: encryption
        self.domain = "facebook.com"
        self.home_url = "https://m.facebook.com"
        # api to send login data , non-script based
        self.login_url = f"{self.home_url}/login/device-based/regular/login/?refsrc=deprecated&lwv=100&refid=8"
        #cookies file
        self.c_file = "cookies.log"
        # different access routes for information and manupulation
        # $ OWN PROFILE LINK $ 
        self.own_info_url = f"{self.home_url}/profile.php"
        # $ OWN PAGES $
        self.pages = f"{self.home_url}/pages"
    
    def _save_cokies(self,cookie):
        file = open(self.c_file,"w+")
        data = json.dumps(cookie)
        file.write(data)
        file.close()

    def _load_cokies(self):
        if not os.path.exists(self.c_file):
            file = open(self.c_file,"w")
            file.close()
            return False
        file = open(self.c_file,"r")
        data = json.loads(file.read())
        file.close()
        self.session.get(self.home_url)
        for each in data:
            self.session.cookies[each] = data[each]
        print("[+] Successfully loaded cookies")
        verification = self.verify_login()
        if(not verification):
            return False
        else:
            return True
        

    def get_own_name(self):
        data = self.session.get(self.own_info_url)
        # scrap data
        try:
            soup = BeautifulSoup(data.text,'html.parser')
            profile_div = soup.find("div",{"id":"m-timeline-cover-section"})
            self.name = profile_div.find_all("strong")[0].get_text()
            return self.name
        except:
            return False
    
    
    def verify_login(self):
        name = self.get_own_name()
        if(name):
            print("[+] Cookies verified")
            return True
        else:
            print("[-] Cookies Failed Not logged in, re-login")
            return False

    def login(self,user,password):
        print("[+] Attempting LOGIN! ")
        home_data = self.session.get(self.home_url)
        soup = BeautifulSoup(home_data.content, 'html.parser')
        # gets hidden input fields for login 
        form = soup.find("form")
        inputs = form.find_all("input")
        post_data = {}
        for each in inputs:
            try:
                post_data[each["name"]] = each["value"]
            except:
                pass
        # add user and pass
        post_data["email"] = user
        post_data["pass"] = password
        #sending request
        # verifying password if c_user in cookies then pasword right
        old_cookies = (self.session.cookies.get_dict())
        self.session.post(self.login_url,data=post_data)
        time.sleep(0.5)
        new_cookies = (self.session.cookies.get_dict())
        if "c_user" in new_cookies:
            self._save_cokies(new_cookies)
            print("[+] Successfully logged in and saved cookies")
        else:
            print("[-] Wrong Username or password")
            return False

    def HandleSession(self,user,password):
        #load cookies and verify if exists .. if failed login using credentials ...re login
        load_existing_session = self._load_cokies()
        if(load_existing_session):
            return True
        else:
            self.login(user,password)  

    def getPagesList(self):
        data = self.session.get(self.pages)
        # scrap pages
        soup = BeautifulSoup(data.content,'html.parser')
        own_pages_div = soup.find_all("div",{"class":"bv","class":"bw"})[0]
        pages_link = own_pages_div.find_all("tr")
        self.pages_dict = {}
        for each_page in pages_link:
            page = each_page.find_all("a")[1]
            page_name = page.get_text()
            self.pages_dict[page_name] = page["href"].replace("/","")
        return self.pages_dict

    # to avoid repeating this line of code
    def get_hidden_input(self,inputs):
        post_data = {}
        for each in inputs:
            if(each["type"]=="hidden"):
                try:
                    post_data[each["name"]] = each["value"]
                except:
                    post_data[each["name"]] = ""
        return post_data

    # for_ to distinguish for page vs for profile
    # for_ for page needs to be supplied with page username
    # type_ to change post_data value for recursive request from image upload
    def self_post(self,text,for_="self",type_="text"):
        if for_ == "self":
            data = self.session.get(self.own_info_url)
        else:
            pages = self.getPagesList()
            pages_username = list(pages.values())
            if for_ in pages_username:
                url = self.home_url + f"/{for_}"
                data = self.session.get(url)
                print("[+] Page access verified")
            else:
                print("[-] Page specified either no admin access or doesn't exists")
                return False
        # get data of form feild in own page
        soup = BeautifulSoup(data.content,'html.parser')
        form = soup.find("form",{"id":"mbasic-composer-form"})
        url_to_post = self.home_url + form["action"]
        inputs = form.find_all("input")
        post_data = self.get_hidden_input(inputs)
        # Get button value get first tr and try
        # display successfully posted if its a text post
        display_message = False
        if type_ == "text":
            post_data["view_post"] = "Post"
            display_message = True
        elif type_ == "image":
            post_data["view_photo"] = "Photo"
        else:
            print("[-] Wrong post type supplied")
            return False
        # text to post
        post_data["xc_message"] = text
        # Hitting The Api
        data = self.session.post(url_to_post,data=post_data)
        if display_message:
            print("[+] Successfully Posted your text in to your timeline")
        return data

    def verify_image_location(self,image):
        if os.path.exists(image):
            return True
        else:
            return False

    def self_image_post(self,text,image,for_="self"):
        # verify image exists
        if not self.verify_image_location(image):
            print("[-] Verify Image Location")
            return False
        # opening image in postable format
        image_post = {"file1":open(image,'rb')} 
        # get image upload area
        data = self.self_post(text,type_="image",for_=for_)
        # scrap image upload location
        soup = BeautifulSoup(data.content,'html.parser')
        form = soup.find("form")
        url_to_post = self.home_url + form["action"]
        # get hidden and submit input
        inputs = form.find_all("input")
        post_data = {}
        for each in inputs:
            if((each["type"]=="hidden") or (each["type"]=="submit")):
                try:
                    post_data[each["name"]] = each["value"]
                except:
                    post_data[each["name"]] = ""
        # Hit API again
        print("[+] Attempting to upload given image")
        data = self.session.post(url_to_post,data=post_data,files=image_post)
        # creating soup of 2nd redirect
        soup = BeautifulSoup(data.content,'html.parser')
        form = soup.find("form")
        url_to_post = self.home_url + form["action"]
        # scrapping CSRF input yet again
        inputs = form.find_all("input")
        post_data = self.get_hidden_input(inputs)
        post_data["view_post"] = "Post"
        # adding text
        post_data["xc_message"] = text
        # Finalizing upload
        data = self.session.post(url_to_post,data=post_data)
        print(f"[+] Successfully posted {image}")
        return True




# user = "user"
# password = "pass"
# x = FB()
# x.HandleSession(user,password)

# get own profile name
# print(x.get_own_name())

# get pages list
# print(x.getPagesList())

# OWN PROFILE
# x.self_post("dsfsdfdsf")
# x.self_image_post("kalyan","images.png")

# PAGE
# x.self_post("dsfsdfdsf",for_="Test-107071288636127")
# x.self_image_post("actum vectum","images.png",for_="Test-107071288636127")
