from Tools.WebScraping.Spyder.Spyder import Spyder
from Tools.WebScraping.scraping_functions import *
from time import sleep, perf_counter
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.proxy import Proxy, ProxyType
from bs4 import BeautifulSoup
import selenium.webdriver
import re


def create_dict(name, friends):
    """
    returns {name: friends}
    """
    to_return = dict()
    to_return[name] = friends
    return to_return


long_sleep = 5
short_sleep = 0.2

fp_profile = FirefoxProfile()
fp_profile.set_preference('dom.webnotifications.enabled', False)

scraped_links = []


class FacebookSpyder(Spyder):
    def __init__(self, close_browser=True, maximize_window=False, starting_url=None, custom_profile=fp_profile):
        """
        :param starting_url: what poor soul gets to be the beginning of the friends scraper
        """
        super().__init__(close_browser, maximize_window, custom_profile=custom_profile)

        self.starting_url = None
        self.logged_in = False

        if starting_url is not None:
            self.starting_url = starting_url

        self.user_name = "aboden3al@gmail.com"
        self.password = "SpEcTaCuLaRpAsSwOrD123"

    def __login_type1(self):
        """
        to login if facebook shows its classic login page
        """
        _username = self.sel_browser.find_element_by_xpath("//input[@id = 'email']")
        _password = self.sel_browser.find_element_by_xpath("//input[@id = 'pass']")

        _username.click()
        send_keys_slowly(_username, self.user_name)

        sleep(short_sleep * 2)

        _password.click()
        send_keys_slowly(_password, self.password)

        sleep(short_sleep)

        _password.send_keys(Keys.ENTER)

    def __login_type2(self):
        """
        to login if facebook shows its more modern login page
        """
        _username = self.sel_browser.find_element_by_xpath("//input[@name = 'email']")
        _password = self.sel_browser.find_element_by_xpath("//input[@name = 'pass']")

        _username.click()
        send_keys_slowly(_username, self.user_name)

        sleep(short_sleep * 2)

        _password.click()
        send_keys_slowly(_password, self.password)

        sleep(short_sleep)

        _password.send_keys(Keys.ENTER)

    def login(self):
        """
        Logs into my throwaway account on facebook.
        username: abodena3al@gmail.com
        password: azzuz1899
        :return: None
        """
        self.sel_browser.get(r"https://www.facebook.com")

        sleep(long_sleep)
        try:
            self.__login_type1()

        except NoSuchElementException:
            self.__login_type2()

        finally:
            self.logged_in = True

    def check_logged_in(self):
        bs_obj = BeautifulSoup(self.sel_browser.page_source, features="lxml")
        if bs_obj.find('a', {'role': 'button', 'href': '/login/'}) is not None:
            return False
        return True

    def search(self, thing_to_search):
        """
        Enters something to use facebook's search bar to look for
        :param thing_to_search: string of text
        :return: None
        """

        search_bar = self.sel_browser.find_element_by_xpath("//input[@aria-label = 'Search']")

        search_bar.click()

        sleep(generate_random_number("MID"))

        send_keys_slowly(search_bar, thing_to_search)

        sleep(generate_random_number("SMALL"))

        search_bar.send_keys(Keys.ENTER)

    def get_name(self):
        """
        get name of current person
        """
        bs_obj = BeautifulSoup(self.sel_browser.page_source, features="lxml")
        name = bs_obj.find('span', {'id': 'fb-timeline-cover-name'}).find('a').getText()
        return name

    def has_friends(self):
        """
        Determines whether current person has visible friends or not.
        :return: Boolean (True for yes)
        """
        bs_obj = BeautifulSoup(self.sel_browser.page_source, features="lxml")
        for tag in bs_obj.findAll('div', {'class': '_4-y-'}):
            if tag.getText() == "No friends to show":
                return False

        # if self._check_special_page():
        #     return False

        else:
            print("Has Friends")
            return True

    def find_friends_page(self):
        """
        Navigates to current person's friends page.
        :return: None
        """
        try:
            page = self.sel_browser.find_element_by_xpath("//a[@data-tab-key = 'friends']")
            page.click()
        except ElementClickInterceptedException:
            self.dismiss_alert()
            self.find_friends_page()

    def _check_special_page(self):
        """
        return True if page has "followers" instead of friends.
        """
        bs_obj = BeautifulSoup(self.sel_browser.page_source, features="lxml")
        _followers_span = bs_obj.find("span", {'class': 'fwn fcg'})
        if _followers_span is not None:
            if re.match("[0-9].* followers$", _followers_span.getText()):
                print("Found Special page. Skipping")
                return True
        else:
            return False

    def load_all_friends(self):
        """
        need to scroll down until all friends of current person are found.
        that's usually where "More About Name Surname" h3 tag is shown, so I'll just scroll down to that.
        :return: None
        """

        # to check if stuck somewhere
        _timeout = 5  # seconds

        try:
            the_one_true_header = None  # since there are multiple false h3 tags.
            # the_one_true_div = None     # this gets the final list of elements in a special kind of page (see donald)
            while True:

                headers = self.sel_browser.find_elements_by_xpath("//h3[@class = 'uiHeaderTitle']")

                for h in headers:
                    if re.match("More About .*", h.text) is not None:
                        the_one_true_header = h
                        # print("Found Em!")
                        break

                if the_one_true_header is not None:
                    break

                _scroll_amount_start = self.sel_browser.execute_script("return window.scrollY;")
                self.scroll_page_smoothly(250, round(random.uniform(7, 10), 2))
                _scroll_amount_end = self.sel_browser.execute_script("return window.scrollY;")

                # FIXME: prone to skipping valid people here.
                _counter_1a = perf_counter()

                if round(_counter_1a % _timeout) == 0:
                    # print(f"reset at {round(_counter_1a)} seconds")
                    if _scroll_amount_start == _scroll_amount_end:
                        print("at bottom of page")
                        break

            # regy = re.match(r"More About .*", the_one_true_header.text)

            # print(f"Regex works {regy}" if regy is not None else "Regex doesn't work")

        except Exception as e:
            print(e)

    def scrape_friends(self):
        """
        return a dict of form (name: link)
        :return: list of friends as BeautifulSoup objects
        """
        bs = BeautifulSoup(self.sel_browser.page_source, features="lxml")

        bs_friends = bs.findAll("li", attrs={'class': '_698'})

        big_dict = dict()

        for friend in bs_friends:
            name = friend.find("div", attrs={'class': 'fsl fwb fcb'}).find("a").getText()
            link = friend.find("div", attrs={'class': 'fsl fwb fcb'}).find("a")['href']

            big_dict[name] = link

        return big_dict

    def __scrape_facebook(self, layers):
        """
        Using multi-threading, with a maximum of 10 threads, scrape every friend in a layer then move on to the next
        layer, getting info from three lists: Pending, Scraping, and Scraped.
        :param layers: how many layers to go down. p1 > p1's > p1's p's > etc..
        :return: I have no clue but it's a list of sorts?
        """
        # Loop:
        # at friends page of someone.
        # get all their friends' NAMES and LINKS.
        # for each friend, repeat loop.
        # end loop

        # make sure there's a list each person's friend names, in which they are saved. (maybe FIXME)

        pass


class FriendSpyder(FacebookSpyder):
    def __init__(self):
        # FIXME: nothing is loading anymore when useragent is changed
        special_profile = FirefoxProfile()
        # to stop annoying facebook notifications which block elements from being clicked
        special_profile.set_preference("dom.webnotifications.enabled", False)
        # special_profile.set_preference("general.useragent.override", random_useragent())

        super().__init__(close_browser=False, custom_profile=special_profile)

        self.idle = True
        # self.open_new_window()
        # self.window = self.sel_browser.current_window_handle

    def activate(self, new_url):
        """
        designed to work with a multi-threaded approach. can be used standalone as well.
        :return: None
        """
        try:
            # browser saves scroll height between people's pages otherwise. (probably got me banned)
            self.current_scroll_amount = 0

            if not self.logged_in:
                self.login()
                sleep(4)
                if not self.check_logged_in():
                    self.login()
                    sleep(4)

            self.sel_browser.get(new_url)
            sleep(3)

            _name = self.get_name()

            self.find_friends_page()
            sleep(generate_random_number("BIG") * 2)

            if not self.has_friends():
                return None

            self.load_all_friends()

            _scraped_friends = self.scrape_friends()

            sleep(1)

            print(f"Scraped {len(_scraped_friends.keys())} friends from {_name}")

            return create_dict(_name, _scraped_friends)
        except Exception as e:
            print(f"Encountered Exception, {e}")
            return None
