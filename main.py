from bs4 import BeautifulSoup
import requests
import re
import time
from exceptions import TopicNotFoundError, HTMLParsingError, ParseWikiError

class WikiPageFetcher:
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
        
        self.check_valid_wiki()

    def check_valid_wiki(self):
        """
        checks if page on topic page exists
        raises exception on request error
        """
        try:
            r = requests.get(self.__page_link)
            if r.status_code == 200:
                return True
            elif r.status_code in [400, 404]:
                raise requests.HTTPError(f'Wikipedia page not found: {self.__page_link}')
            elif r.status_code in [500, 501, 503, 504]:
                raise requests.HTTPError('Wikipedia seems to be down. Please try agian later')
        except requests.RequestException as err:
            raise

    def fetch_page(self):
        """
        returns page HTML content
        """
        try:
            self.__page_content = requests.get(self.__page_link).text
            return self.__page_content
        except (ValueError, requests.RequestException) as err:
            raise
        
    def get_link(self):
        """
        returns current topic wikipedia page URL
        """
        return self.__page_link
        

class ParseWikiPage:
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
                raise TopicNotFoundError('No next topic found', topic=self.__parsed_topics_list[-1])

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
                raise HTMLParsingError('No Wikipedia content found for topic', topic=self.__parsed_topics_list[-1])

            #checks if HTML is list wikipedia content
            if len(content_body.find_all('p')) == 1:
                for topic in content_body.find_all('li'):
                    if self.regex_search(topic.find_all('a')):
                        return

            for paragraph in content_body.find_all('p'):
                if self.regex_search(paragraph.find_all('a')):
                    return 

            raise TopicNotFoundError('No next topic found', topic=self.__parsed_topics_list[-1])
            
        except (requests.RequestException, HTMLParsingError, TopicNotFoundError) as err:
            raise


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
        except Exception as e:
            raise HTMLParsingError('Error parsing <a>', topic=self.__parsed_topics_list[-1])

    def all_prev_links(self):
        """
        returns all previous topics parsed through
        """
        if not self.__parsed_topics_list:
            return f'0 links found for content f{self.topic}'
        return self.__parsed_topics_list

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
            return soup
        except:
            raise HTMLParsingError('Error displaying HTML page content', topic=self.__parsed_topics_list[-1])


try:
    topic = WikiPageFetcher('spoon')
    wiki_scraper = ParseWikiPage(topic.fetch_page(), topic.topic)
    wiki_scraper.find_philosophy()
except Exception as err:
    if isinstance(err, ParseWikiError):
        print(f"Topic: {err.topic}\n", err)
    else:
        print(err)