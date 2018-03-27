# coding=utf-8
import requests
from bs4 import BeautifulSoup

import json
from janome.tokenizer import Tokenizer
import json
from requests_oauthlib import OAuth1Session
from summpy.lexrank import summarize

# twitterAPI
oath_key_dict = {
    "consumer_key": "2qimKikZwCOJXG0wxJ0lzkcM6",
    "consumer_secret": "MHAjJsYvGCF0mVkgs9w0tJh0fJf0ZpBMKqUMiqTUzQmqYoIFA2",
    "access_token": "157729228-r5JXs6Mi79rEgPAd1AyS9w5l7BaUADzrmLpc9JiR",
    "access_token_secret": "Dm0C0ZPCBCDcNARnAaJvUDxEk88o1pbTtWuZgvILzFG2u"
}

research_ids = ["get2ch_soccer", "BaseballNEXT", "gorin"]
pattern = r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)"
rss_news = [r"https://headlines.yahoo.co.jp/rss/jsportsv-c_spo.xml",
            r"https://headlines.yahoo.co.jp/rss/soccerk-c_spo.xml",
            r"https://headlines.yahoo.co.jp/rss/bfj-c_spo.xml",
            r"https://headlines.yahoo.co.jp/rss/nallabout-c_spo.xml",
            r"https://headlines.yahoo.co.jp/rss/asahik-c_spo.xml",
            r"https://headlines.yahoo.co.jp/rss/baseballk-c_spo.xml"]
news_dict = {}


def create_oath_session(oath_key_dict):
    oath = OAuth1Session(
        oath_key_dict["consumer_key"],
        oath_key_dict["consumer_secret"],
        oath_key_dict["access_token"],
        oath_key_dict["access_token_secret"]
    )
    return oath


class SportsLive:
    def __init__(self, parent=None):
        pass

    '''
    形態素解析
    '''
    @staticmethod
    def morphological_analysis(text):
        txt = text
        t = Tokenizer()
        word_dic = {}
        lines = txt.split("\r\n")
        for line in lines:
            blog_txt = t.tokenize(line)
            for w in blog_txt:
                word = w.surface
                ps = w.part_of_speech
                if ps.find('名詞') < 0:
                    continue
                if word not in word_dic:
                    word_dic[word] = 0
                word_dic[word] += 1

        keys = sorted(word_dic.items(), key=lambda x: x[1], reverse=True)
        keyword = ''
        for word, cnt in keys[:4]:
            print("{0} ".format(word))
            keyword += "{0} ".format(word)

        return keyword

    def score_check(self, keyword):
        data = []

        try:
            target_url = 'https://sports.yahoo.co.jp/search/text?query=' + keyword
            resp = requests.get(target_url)
            soup = BeautifulSoup(resp.text, "html.parser")

            tables = soup.find_all("p", class_="siteUrl")

            for table in tables:
                geturl = table.text
                geturl = geturl.rstrip(' － キャッシュ')

                data.append(geturl)
        except:
            pass
        score = ''

        try:
            for url in data:
                if 'game' in url:
                    score = self.get_score(url)
                    break
                else:
                    continue

        except:
            pass

        return score

    def twitter_check(self, keyword, debug=False):
        keyword_list = keyword.split(' ')
        tweet_list = []
        output_list = []
        json_dict = {}

        for keyword in keyword_list:
            if keyword == "":
                break

            for research_id in research_ids:
                tweets = self.tweet_search(keyword, oath_key_dict, research_id)

                for tweet in tweets["statuses"]:
                    text = tweet['text']
                    text = self.tweet_analysis(text)
                    if not text[0] in outtext:
                        outtext += text[0] + '<br>'

                outtext2 += outtext[:600]
                outtext = ''

            outtext2 = outtext2.replace(keyword, '<font color="red">' + keyword + '</font>')

        return outtext2

    def news_check(self, keyword, debug=False):
        keyword = keyword.split(' ')
        output_text = ""
        json_dict = {}

        for rss in rss_news:
            resp = requests.get(rss)
            soup = BeautifulSoup(resp.text, "html.parser")

            titles = soup.find_all("title")
            links = soup.find_all("link")

            for title, link in zip(titles, links):
                news_dict.update({title.next: str(link.next).replace('\n', '').replace(' ', '')})

        for key in keyword:
            if key == "":
                break

            news_key_list = [l for l in news_dict.keys() if key in l]
            print(news_key_list)

            for list_key in news_key_list:
                text = ""
                resp = requests.get(news_dict[list_key])
                soup = BeautifulSoup(resp.text, "html.parser")

                for s in soup.find_all("p", class_="ynDetailText"):
                    text += s.get_text()
                analysis_text = self.tweet_analysis(text)

                if debug:
                    # タイトル：｛リンク，全文，要約｝
                    json_dict.update({list_key:
                    {
                        'link':news_dict[list_key],
                        'text':text,
                        'a_text':analysis_text,
                    }}
                    )

                output_text += '<br>'.join(analysis_text)

        json_dict.update({"result_text":output_text})

        encode_json_data = json.dumps(json_dict)

        return encode_json_data

    @staticmethod
    def tweet_search(search_word, oath_key_dict, account):
        url = "https://api.twitter.com/1.1/search/tweets.json?"
        params = {
            "q": search_word,
            "from":account,
            "lang": "ja",
            "result_type": "recent",
            "count": "100"
        }

        oath = create_oath_session(oath_key_dict)
        responce = oath.get(url, params=params)
        if responce.status_code != 200:
            print("Error code: %d" % (responce.status_code))
            return None
        tweets = json.loads(responce.text)

        return tweets

    @staticmethod
    def get_score(url):
        target_url = url
        resp = requests.get(target_url)
        soup = BeautifulSoup(resp.text)

        if 'baseball' in url:
            score_table = soup.find('table', {'width': "100%", 'cellpadding': "0", 'cellspacing': "0", 'border': "0"})
            rows = score_table.findAll("tr")
            score = []
            text = '最新の試合の結果は' + '\n'

            try:
                for row in rows:
                    csvRow = []
                    for cell in row.findAll(['td', 'th']):
                        csvRow.append(cell.get_text())
                    score.append(csvRow)

                    text += '\t|'.join(csvRow) + '\n'

            finally:
                return text

        elif 'soccer' in url:
            hometeam = soup.find_all('div', class_="homeTeam team")
            hometotal = soup.find_all("td", class_="home goal")
            home1st = soup.find_all("td", class_="home first")
            home2nd = soup.find_all("td", class_="home second")
            awayteam = soup.find_all('div', class_="awayTeam team")
            awaytotal = soup.find_all("td", class_="away goal")
            away1st = soup.find_all("td", class_="away first")
            away2nd = soup.find_all("td", class_="away second")

            for homename, awayname, homegoal, awaygoal in zip(hometeam, awayteam, hometotal, awaytotal):
                text = '最新の試合の結果は' + '\n' + str(homename.text.replace('\n', '')) + \
                       '-' + str(awayname.text.replace('\n', '')) + '\n'

                if len(home1st[0].text) > -1:
                    text += home1st[0].text + '前半' + away1st[0].text + '\n'

                if len(home2nd[0].text) > -1:
                    text += home2nd[0].text + '後半' + away2nd[0].text + '\n'

                if len(homegoal) > -1:
                    text += homegoal.text + ' - ' + awaygoal.text

                return text

    @staticmethod
    def tweet_analysis(text):
        sentences, debug_info = summarize(
            text, sent_limit=5, continuous=True, debug=True
        )

        return sentences


def main():
    SL = SportsLive()

    print(SL.news_check(SL.morphological_analysis('羽生のオリンピック')))
    print(SL.news_check(SL.morphological_analysis('宇野昌磨の記録'), debug=True))


if __name__ == '__main__':
    main()
