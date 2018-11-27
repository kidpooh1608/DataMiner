from twitter_scraper import get_tweets
import json, sys
from threading import Thread, Lock
import datetime
from optparse import OptionParser

class TwitterMiner:
    mutex = Lock()

    def __init__(self):
        self.twitter_ids = {}

    def clear_twitter_ids(self):
        self.twitter_ids.clear()

    def craw_tweet(self, startId, endId, keys):
        thread_id = datetime.datetime.now()
        print("craw_tweet: ThreadID: {0}, startId: {1}, endId: {2}".format(thread_id, startId, endId))

        if endId > len(keys):
            endId = len(keys)
        for id in range(startId, endId):
            url = 'https://twitter.com/{0}'.format(list(keys)[id])
            print("craw_tweet: ThreadID: {0}, {1}:{2}".format(thread_id,id,url))
            try:
                for tweet in get_tweets(list(keys)[id], pages=25):
                    self.mutex.acquire()
                    if tweet['userID'] not in self.twitter_ids.keys():
                        self.twitter_ids[tweet['userID']] = [(tweet['entries']['urls'], tweet['entries']['hashtags'])]
                    else:
                        self.twitter_ids[tweet['userID']].append((tweet['entries']['urls'], tweet['entries']['hashtags']))
                    self.mutex.release()
            except:
                print("craw_tweet: craw_tweet warning")

    def static_var(varname, value):
        def decorate(func):
            setattr(func, varname, value)
            return func
        return decorate

    @static_var(varname="differences",value=())
    def get_userID_and_craw(self, number_id):
        '''
        :param: number_id is the number of user you want to crap
        :return: twitter_ids after collecting
        '''
        print("get_userID_and_craw: length of twitter_ids: {0}".format(len(self.twitter_ids.keys())))
        differ_len = len(self.get_userID_and_craw.differences)
        twitter_ids_len = len(self.twitter_ids.keys())
        self.get_userID_and_craw.differences = set(self.twitter_ids.keys() - self.get_userID_and_craw.differences)
        differ_len = len(self.get_userID_and_craw.differences)

        if twitter_ids_len > number_id or differ_len == 0:
            return self.twitter_ids
        else:
            print("get_userID_and_craw: length of difference: {0}".format(differ_len))

            if differ_len > 0:
                if differ_len > 10:
                    thread_num = int(differ_len/10)
                else:
                    thread_num = differ_len

                downloadthreads = []
                for i in range(0, differ_len, thread_num):
                    downloadthread = Thread(target=self.craw_tweet, args=(i, i + thread_num - 1, self.get_userID_and_craw.differences))
                    downloadthreads.append(downloadthread)
                    downloadthread.start()

                for thread in downloadthreads:
                    thread.join()

            return self.get_userID_and_craw(number_id=number_id)

    def craw_tweets(self, init_id=None, filein='909_user_ids.json', fileout='result_id20.json', number_ids=500):

        '''
        :param: init_id_from_file=False if you want to collect user id from Twitter of developerjack man. True if you want to collect
        from users which is in file
        :param: filein is a json file includes twitter ids
        :param: fileout is result json
        :param: number_ids is the number of user ids you want to craw
        '''
        if not init_id:
            with open(filein) as f:
                self.twitter_ids = json.load(f)
        else:
            try:
                print("crawing tweet_id: {0}".format(init_id))
                for tweet in get_tweets(init_id, pages=25):
                    if tweet['userID'] not in self.twitter_ids.keys():
                        self.twitter_ids[tweet['userID']] = [(tweet['entries']['urls'], tweet['entries']['hashtags'])]
                    else:
                        self.twitter_ids[tweet['userID']].append((tweet['entries']['urls'], tweet['entries']['hashtags']))
            except:
                print("craw_tweets warning")

        print("Initialize length of twitter_ids: {0}".format(len(self.twitter_ids.keys())))
        if len(self.twitter_ids.keys()) == 0:
            print("craw_tweets warning")
        elif len(self.twitter_ids.keys()) == 1:
            with open("{0}_{1}.json".format(fileout, len(self.twitter_ids.keys())), 'w') as fp:
                json.dump(self.twitter_ids, fp, indent=4)
        else:
            try:
                self.get_userID_and_craw(number_id=number_ids)
            except RecursionError as e:
                print("craw_tweets warning: {0}".format(e))
            finally:
                with open("{0}_{1}.json".format(fileout, len(self.twitter_ids.keys())), 'w') as fp:
                    json.dump(self.twitter_ids, fp, indent=4)
        return self.twitter_ids

class DataMiner():
    def __init__(self, source_data=None, out_put="/tmp"):
        self.data = {}
        self.source_data = source_data
        self.out_put = out_put

    def __iter__(self):
        return self.data

    def craw_data(self):
        if self.source_data:
            with open(self.source_data) as f:
                self.data = json.load(f)
        else:
            crawer = TwitterMiner()
            crawer.clear_twitter_ids()
            default_id = "developerjack"
            self.data = crawer.craw_tweets(init_id=default_id, fileout='{0}/craw_tweets_{1}'.format(self.out_put,default_id),
                        number_ids=500)
        return self.data

def main():
    parser = OptionParser(usage="usage: %prog [options]",
                          version="%prog 1.0")
    parser.add_option("-i", "--init",
                      action="store",
                      dest="init_user",
                      default="developerjack",
                      help="Give a twitter user you want to scrap from")
    parser.add_option("-n", "--number",
                      action="store",
                      dest="number_users",
                      default=int(500),
                      help="number of users you want to scrap")
    parser.add_option("-f", "--file",
                      action="store",
                      dest="file_in",
                      default=None,
                      help="Give input file includes users you want to scrap")
    parser.add_option("-o", "--output",
                      action="store",
                      dest="out_put",
                      default="craw_tweets_output",
                      help="output folder of json files")
    (options, args) = parser.parse_args()

    if options.file_in == None:
        crawer = TwitterMiner()
        crawer.craw_tweets(init_id=options.init_user, fileout='{0}/craw_tweets_{1}'.format(options.out_put,options.init_user),
                number_ids=int(options.number_users))
    else:
        with open(options.file_in) as f:
            _twitter_ids = json.load(f)

        crawer = TwitterMiner()
        for key in _twitter_ids:
            crawer.clear_twitter_ids()
            crawer.craw_tweets(init_id=key, fileout='{0}/craw_tweets_{1}'.format(options.out_put,key),
                        number_ids=int(options.number_users))

if __name__ == "__main__":
    main()

