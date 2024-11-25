from bs4 import BeautifulSoup
import requests
import re
import time


class Topic: #UREQUIRED?
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


#Requests Topic, throws error if topic not exist
class WikiPageFetcher():
    """Scrapes topic data from Wikipedia website"""
    __page_content = None #stores html text as string? list?

    def __init__(self, topic): #Parse topic name
        self.topic = topic
        self.__page_link = f"https://en.wikipedia.org/wiki/{topic}"
        
        if not self.check_valid_wiki():
            raise ValueError(f'Wikipedia Page Not Found {self.__page_link}')

    def check_valid_wiki(self): #returns False if Topic page does not exist
        try:
            r = requests.get(self.__page_link)
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            return False
        
    def fetch_page(self): #fetches page html content
        try:
            self.__page_content = requests.get(self.__page_link).text
            return self.__page_content #returns page html/text
        except (ValueError, requests.exceptions.RequestException) as e:
            return e
        
    def get_link(self): #Returns Topic URL
        return self.__page_link
        

class ParseWikiPage():
    """parse over wikipedia page content html"""
    __next_link_topic = None #stores next link topic name? #or just store in parsed_topics_list?
    __next_link = None

    def __init__(self, page_content, original_topic):
        self.__page_content = page_content
        self.__parsed_topics_list = [original_topic] #array containing, initial and subsequent topics completing at philosophy

    def find_philosophy(self):
        """iterates through topics breaks at philosophy"""
        while not self.__parsed_topics_list[-1] == 'philosophy': #check last index not philosophy
            time.sleep(2)
            #loop until find philosophy 
            #generate new requests for latest link? #call WikiPageFetcher class inside this class?
            self.find_next_topic(self.__parsed_topics_list[-1])
            print(self.__parsed_topics_list[-1])


    def find_next_topic(self, current_topic):
        try:
            soup = BeautifulSoup(self.__page_content, 'html.parser')
            content_body = soup.find(id='mw-content-text')

            if not content_body: #no content found in targeted div? TRY OTHER DIV?
                #find next link in current link?
                raise BaseException('ParseWiki: No Topic Content Found.')

            for paragraph in content_body.find_all('p'):
                #parse array of <a/>
                if self.regex_search(paragraph.find_all('a')):
                    break

        except BaseException as e:
            return 'Fetch Link Error: Could not get next link from Topic content'


    def regex_search(self, a_tag_list):
        """regex method to find /wiki/{word} returning first valid <a/>"""

        if not a_tag_list:
            return False
        try:
            for tag in a_tag_list: #parse over each <a/> tag
                if re.search('wiki/[aA-zZ]', tag.get('href')) and tag.string not in self.__parsed_topics_list:
                    self.__next_link_topic = tag.string
                    self.__next_link = f"https://en.wikipedia.org{tag.get('href')}"
                    self.__parsed_topics_list.append(tag.string)
                    return tag
            return False    
        except BaseException as e:
            #HANDLE NO NEXT TOPIC?
            #ITERATE UNTIL NEXT TOPIC FOUND?
            print('exception raised in regex parsewiki regex search function')
            raise ValueError(e)


    def all_prev_links(self):
        if not self.__links_list:
            return f'0 links found for content f{self.topic}'
        return self.__links_list

    def get_prev_link(self):
        if self.__next_link:
            return self.__links_list[-1]
        
    def get_next_link(self):
        if self.__next_link:
            return self.__next_link

    def view_page_body(self):
        try:
            soup = BeautifulSoup(self.__page_content, 'html.parser')
            content_body = soup.find_all('p')
            print(content_body)
        except:
            return 'Error viewing page'



topic = WikiPageFetcher('spoon')

links_to_philosophy = ParseWikiPage(topic.fetch_page(), topic.topic)
#ParseWikiPage class returns full list of topics to philosophy?

links_to_philosophy.find_philosophy()