from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import bs4, re, time, json, datetime
from optparse import OptionParser

def collect_user_id_from_follower(login_url='https://twitter.com/login', url="SproutSocial",
                                  page_down=5):

    _url = "https://twitter.com/{0}/followers".format(url)
    print("login_url: {0}\nurl: {1}\npage_down: {2}".format(login_url, _url, page_down))

    browser = webdriver.Firefox()
    try:
        #browser = webdriver.Firefox()
        browser.get(login_url)
        login_xpath = "/html/body/div[1]/div[2]/div/div/div[1]/form/fieldset/div[1]/input"
        pass_xpath = "/html/body/div[1]/div[2]/div/div/div[1]/form/fieldset/div[2]/input"
        press_xpath = "/html/body/div[1]/div[2]/div/div/div[1]/form/div[2]/button"

        browser.find_element_by_xpath(login_xpath).send_keys('danhvo.uit@gmail.com')
        browser.find_element_by_xpath(pass_xpath).send_keys('phe123')
        browser.find_element_by_xpath(press_xpath).click()
        browser.get(_url)
        time.sleep(5)
        html = browser.find_element_by_tag_name('html')

        for i in range(0, page_down):
            print("PAGE_DOWN: {0}th".format(i))
            html.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

        html = browser.page_source
        tag = int(datetime.datetime.now().timestamp())
        with open('soup_{0}.html'.format(tag), 'w') as the_file:
            the_file.write(html)
    except Exception as e:
        print(e.message)
    finally:
        browser.close()

    twitter_ids = {}
    soup = bs4.BeautifulSoup(open('soup_{0}.html'.format(tag)), features="lxml")
    for link in soup.findAll('a', attrs={'class': re.compile("ProfileNameTruncated-link"), 'href': re.compile('\w')}):
        if link.get('href') not in twitter_ids.keys():
            twitter_ids[link.get('href').replace("/", "")] = []

    with open("{0}_followers_{1}_{2}.json".format(url,tag, len(twitter_ids.keys())),
              'w') as fp:
        json.dump(twitter_ids, fp, indent=4)

    print(twitter_ids)

def main():
    parser = OptionParser(usage="usage: %prog [options]",
                          version="%prog 1.0")
    parser.add_option("-u", "--url",
                      action="store",
                      dest="url",
                      default="SproutSocial",
                      help="twitter page you want to get followers.         Example: -u SproutSocial ")
    parser.add_option("-l", "--login_url",
                      action="store",
                      dest="login_url",
                      default='https://twitter.com/login',
                      help="login page")
    parser.add_option("-p", "--pageDown",
                      action="store",
                      dest="page_down",
                      default=int(5),
                      help="the number of page_down pressing", )
    (options, args) = parser.parse_args()

    collect_user_id_from_follower(login_url=options.login_url,
                                  url=options.url,
                                  page_down=int(options.page_down))

if __name__ == "__main__":
    main()

