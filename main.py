from bs4 import BeautifulSoup
import requests
import re


class Topic:
    """Get Wikipedia topic information"""
    def __init__(self, topic_name):
        self.__topic_name = topic_name
        self.__link = f"https://en.wikipedia.org/wiki/{topic_name}"

    def checkValid(self):
        return requests.get(self.__link).status_code

    def getTopicName(self):
        return self.__topic_name
    
    def getLink(self):
        return self.__link


#class to define topic, check wiki page valid and get page
class WikiPageFetcher():
    """Scrapes data from Wikipedia website"""
    __page_content = None #variable to store static html for bs4

    def __init__(self, topic): #obj only takes Topic name i.e football
        self.topic = topic
        self.__page_link = f"https://en.wikipedia.org/wiki/{topic}"
        
        if not self.check_page_valid():
            raise ValueError('Invalid Wikipedia Page')

    def check_page_valid(self):
        """returns false if request does not return 200 status to __page_link request"""
        try:
            r = requests.get(self.__page_link)
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            return False
        
    def fetch_page(self):
        try:
            self.__page_content = requests.get(self.__page_link).text
            return self.__page_content
        except (ValueError, requests.exceptions.RequestException) as e:
            return e
        

class ParseWikiPage():
    """parse over wikipedia page html"""
    __links_list = [] #store all previous links
    __next_link_topic = None #variable store topic of first link in page

    def __init__(self, page_content):
        self.__page_content = page_content

    def first_content_link(self):
        try:
            soup = BeautifulSoup(self.__page_content, 'html.parser') 
            content_body = soup.find('div', {'id': 'mw-content-text'})

            #GET 'MW-CONTENT-PARSER CLASS!!!!
            soup.find(id='mw-content-text')

            if not content_body:
                raise BaseException('ParseWiki: No Topic Content Found.')

            for paragraph in content_body.find_all('p'):
                #parse each <a/> in each paragraph to regex search method
                if self.regex_search(paragraph.find_all('a')):
                    break
            
            if self.__next_link_topic:
                #successfully located next topic?
                print(self.__next_link_topic)
            else:
                raise BaseException('ParseWikiPage: No Next Link Found')

        except BaseException as e:
            print(e)
            return 'soup error'

    def view_page_body(self):
        try:
            soup = BeautifulSoup(self.__page_content, 'html.parser')
            content_body = soup.find_all('p')
            print(content_body)
        except:
            return 'Error viewing page'

    def regex_search(self, a_tag_list):
        """regex method to find /wiki/{word} returning first relevent <a/> (hopefully)"""
        try:
            #print(a_tag_list)
            for tag in a_tag_list:
                if re.search('wiki/[aA-zZ]', tag.get('href')):
                    self.__next_link_topic = tag.string
                    return tag
            raise BaseException('No Next Link Found')
        except BaseException as e:
            raise ValueError(e)

    def append_link(self, link):
        if self.__next_link in self.__links_list:
            pass
        self.__links_list.append(link)

    def get_links_list(self):
        return self.__links_list        

#testing
wikipedia_page = WikiPageFetcher('spoon').fetch_page()

ParseWikiPage(wikipedia_page).first_content_link()
