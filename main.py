from bs4 import BeautifulSoup
import requests
import re
import time


class WikiPageFetcher():
    """
    fetches and scrapes topic data from Wikipedia website
    """
    __page_content = None

    def __init__(self, topic): 
        """
        fetches topic wikipedia page 
        checks if topic is valid wikipedia page
        """
        self.topic = topic
        self.__page_link = f"https://en.wikipedia.org/wiki/{topic}"
        
        if not self.check_valid_wiki():
            raise ValueError(f'Wikipedia Page Not Found {self.__page_link}')

    def check_valid_wiki(self):
        """
        checks if page on topic page exists
        returns False if does not exist
        """
        try:
            r = requests.get(self.__page_link)
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            return False

    def fetch_page(self):
        """
        returns page HTML content
        """
        try:
            self.__page_content = requests.get(self.__page_link).text
            return self.__page_content
        except (ValueError, requests.exceptions.RequestException) as e:
            return e
        
    def get_link(self):
        """
        returns current topic wikipedia page URL
        """
        return self.__page_link
        

class ParseWikiPage():
    """
    parse over fetched wikipedia page content html returned from WikiPageFetcher class
    """
    __next_link = None

    def __init__(self, page_content, original_topic):
        self.__page_content = page_content
        self.__parsed_topics_list = [original_topic] #array of original and subsequent topics

    def find_philosophy(self):
        """
        checks if 'philosophy' has been found
        fetches next topic wikipedia page if not philosophy
        """
        loop_count = 0
        while not self.__parsed_topics_list[-1] == 'philosophy':
            #compare loop count to topic count; if loop count > topic_count; break
            if loop_count > len(self.__parsed_topics_list):
                raise BaseException('ParseWikiError: No more topics being found')

            time.sleep(2) #REQUEST DELAY

            self.__page_content = WikiPageFetcher(self.__parsed_topics_list[-1]).fetch_page()

            self.find_next_topic(self.__parsed_topics_list[-1])
            loop_count += 1
            print(self.__parsed_topics_list[-1])

        print(f"Complete, Topic count to philosophy: {len(self.__parsed_topics_list)}")

    def find_next_topic(self, current_topic):
        """
        searches for next link in current topics wikipedia page HTML
        """
        try:
            soup = BeautifulSoup(self.__page_content, 'html.parser')
            content_body = soup.find(id='mw-content-text')

            if not content_body:
                #STRANGE HTML ERROR? 
                raise BaseException('ParseWikiError: No Topic Content Found.') #BaseException correct error?

            #checks if HTML is list wikipedia content
            if len(content_body.find_all('p')) == 1:
                for topic in content_body.find_all('li'):
                    if self.regex_search(topic.find_all('a')):
                        break

            for paragraph in content_body.find_all('p'):
                if self.regex_search(paragraph.find_all('a')):
                    break

            raise BaseException('No next topic found?')
            
        except BaseException as e:
            self.view_page_body()
            return BaseException('Fetch Link Error: Could not get next link from Topic content')


    def regex_search(self, a_tag_list):
        """
        regex method to find next valid topic
        searches '/wiki/{word}' returns first valid <a/> tag
        """
        if not a_tag_list:
            return False
        try:
            for a_tag in a_tag_list: #parse over each <a/> tag
                if re.search('wiki/[aA-zZ]', a_tag.get('href')) and a_tag.string not in self.__parsed_topics_list and a_tag.string != None and 'Help' not in a_tag.get('href'):
                    #remove NON-letter characters?
                    self.__next_link = f"https://en.wikipedia.org{a_tag.get('href')}"
                    self.__parsed_topics_list.append(a_tag.string)
                    return a_tag
            return False    
        except BaseException as e:
            #WHAT OCCURS HERE>????
            #HANDLE NO NEXT TOPIC?
            #ITERATE UNTIL NEXT TOPIC FOUND?
            print('exception raised in regex parsewiki regex search function')
            raise ValueError(e)


    def all_prev_links(self):
        """
        returns all previous topics parsed through
        """
        if not self.__links_list:
            return f'0 links found for content f{self.topic}'
        return self.__links_list

    def get_prev_link(self):
        """
        returns link to previous topic before current
        fallback if current topic NULL
        """
        if self.__next_link:
            return self.__links_list[-1]
        
    def get_next_link(self):
        """
        returns URL for next topic
        """
        if self.__next_link:
            return self.__next_link

    def view_page_body(self):
        """
        displays raw HTML of current topic
        """
        try:
            soup = BeautifulSoup(self.__page_content, 'html.parser')
            content_body = soup.find_all('p')
        except:
            return 'Error viewing page'


topic = WikiPageFetcher('football')

scraper = ParseWikiPage(topic.fetch_page(), topic.topic)

scraper.find_philosophy()