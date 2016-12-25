import scrapy
import coloredlogs
coloredlogs.install(level='WARNING')
import pdb, json, hashlib
import urllib.parse as urlparse
from scrapy.shell import inspect_response
from scrapy.loader import ItemLoader
from DataCollector.items import ResearchPaperItem

class ArticleReferenceSpider(scrapy.Spider):
    """
    crawls the ACM digital library upto 6 level depth and collect
    information regarding the reference and cited by references.

    """
    name = "ArticleReferenceSpider"

    allowed_domains = ["acm.org"]
    start_urls =['http://dl.acm.org/citation.cfm?id=2488205&preflayout=flat']

    #allowed_domains = ["wikipedia.org"]
    #start_urls = ['https://en.wikipedia.org/wiki/List_of_colleges_and_universities_in_the_United_States_by_endowment']


    def __init__(self):
        super(ArticleReferenceSpider, self).__init__()
        self.logger.warn("Starting the crawling procedure")
        self.link_completed={} # {url_hash:{title:"", url:""}}
        # self.title_hash_to_title={}
        # self.title_hash_to_id={}

        self.site_name = 'http://dl.acm.org/'
        self.threshould_length = 40
        self.url_params = {
            'preflayout':'flat'
        }

        self.cited_by_limit = 50
        self.reference_by_limit = 50

        self.allowed_depth = 5

        self.item_x_paths={
            'title' :"string(//div[@id='divmain']//h1[@class='mediumb-text'])",
            'abstract' : "string((//div[@class='flatbody'])[1])",
            'authors' : "//div[@id='divmain']//a[@title='Author Profile Page']//text()", #  list of authors
            'published_in' : "(//div[@class='flatbody'])[6]//td[contains(.,'Title')]/following-sibling::td//text()",
            'publication_date': "(//div[@class='flatbody'])[6]//td[contains(.,'Publication Date')]/following-sibling::td//text()",
            'references': "//div[@class='flatbody'][3]//td/div[not (@class='abstract')]//text()",
            'references_links':"(//div[@class='flatbody'])[3]//td/div[not (@class='abstract')]/a/@href",
            'cited_by': "//div[@class='flatbody'][4]//td/div[not (@class='abstract')]//text()",
            'cited_by_links':"//div[@class='flatbody'][4]//td/div[not (@class='abstract')]//a//@href",
        }


        self.custom_preprocessor={
                'abstract': lambda abs_list: ''.join([x.strip() for x in abs_list]),
                'authors': lambda author_list: ','.join(author_list),
                'replace_non_ascii': lambda x : ''.join([i if ord(i) < 128 else ' ' for i in x]),
                'published_in_preprocessor' : self.published_in_preprocessor,
                'publication_date_preprocessor': self.publication_date_preprocessor,
                'references_preprocessor':self.reference_preprocessor,
                'references_link_preprocesssor':self.reference_link_preprocessor,
                'cited_by_preprocessor':self.cited_by_preprocessor,
                'cited_by_link_preprocessor':self.cited_by_link_preprocessor,
        }

    def parse(self, response):
        item = ResearchPaperItem()

        item['ID'] = self.get_or_create_id(response.url)
        item['Link'] = response.url
        item['Title'] = response.xpath(self.item_x_paths['title']).extract_first()
        item['Abstract'] = self.custom_preprocessor['abstract'](response.xpath(self.item_x_paths['abstract']).extract())
        item['Authors'] =  self.custom_preprocessor['authors'](
            response.xpath(self.item_x_paths['authors']).extract())
        item['Published_in'] = self.custom_preprocessor['published_in_preprocessor'](
            response.xpath(self.item_x_paths['published_in']).extract())
        item['Publication_date'] = self.custom_preprocessor['publication_date_preprocessor'](
            response.xpath(self.item_x_paths['publication_date']).extract())
        item['References'] = self.custom_preprocessor['references_preprocessor'](
            response.xpath(self.item_x_paths['references']).extract())
        references_links = self.custom_preprocessor['references_link_preprocesssor'](
            response.xpath(self.item_x_paths['references_links']).extract())
        item['Cited_by'] = self.custom_preprocessor['cited_by_preprocessor'](
            response.xpath(self.item_x_paths['cited_by']).extract())
        cited_by_links= self.custom_preprocessor['cited_by_link_preprocessor'](
            response.xpath(self.item_x_paths['cited_by_links']).extract())

        self.link_completed[item['ID']]= item['Link']

        if response.meta['depth']:
            self.logger.warn("Depth: {}  => {} ".format(response.meta['depth'],response.url))
            depth = response.meta['depth']
            depth+=1
        else:
            self.logger.warn("Depth: {}  => {} ".format(response.meta['depth'],response.url))
            depth=0

        if depth<self.allowed_depth:
            for link in references_links[0:self.reference_by_limit]:
                if self.get_or_create_id(link) not in self.link_completed.keys():
                    yield scrapy.Request(link, callback=self.parse, meta={'depth': depth})

            for link in cited_by_links[0:self.cited_by_limit]:
                if self.get_or_create_id(link) not in self.link_completed.keys():
                    yield scrapy.Request(link, callback=self.parse, meta={'depth': depth})


        yield item

    def get_hash(self, x):
        hash_object = hashlib.md5(x.encode())
        return hash_object.hexdigest()

    def get_or_create_id(self, url):
        parsed = urlparse.urlparse(url)
        id_field = urlparse.parse_qs(parsed.query)['id']

        if len(id_field)>0:
            return id_field[0]
        else:
            hash_object = hashlib.md5(url.encode())
            return hash_object.hexdigest()

    def published_in_preprocessor(self, iput):

        exclude_list={
            'table of contents':1,
            'archive':2
            }

        non_ascii_removed_str_list = [self.custom_preprocessor['replace_non_ascii'](x) for x in iput]
        non_ascii_removed_str_list = [x.strip() for x in non_ascii_removed_str_list]

        oput=[]

        for x in non_ascii_removed_str_list:
            if x is "":
                pass
            elif x in exclude_list.keys():
                pass
            else:
                oput.append(x)

        oput = [x.replace('"','') for x in oput]

        return " ".join(oput)

    def publication_date_preprocessor(self,iput):
        if len(iput)>0:
            return iput[0].strip()
        else:
            return 'unavailable'

    def reference_preprocessor(self,iput):
        if len(iput) > 0:
            non_ascii_removed_str_list = [self.custom_preprocessor['replace_non_ascii'](x) for x in iput]
            oput = [ x.strip() if len(x) > self.threshould_length  else "" for x  in non_ascii_removed_str_list]
            oput = [x for x in filter(None, oput)]
            oput = [x.replace('"','') for x in oput]
            return oput
        else:
            return list([])

    def reference_link_preprocessor(self, iput):
        if len(iput) > 0:
            links = [ x if 'citation' in x else '' for x in iput]
            links = [x for x in filter(None, links)]
            links = [self.site_name+x for x in links]
            # remove CFTOKEN
            links = [x.split('&CFID')[0] for x in links]
            # add flat get token
            links = [x+"&preflayout=flat" for x in links]
            return links

        else:
            return list([])

    def cited_by_preprocessor(self,iput):
        if len(iput) > 0:
            non_ascii_removed_str_list = [self.custom_preprocessor['replace_non_ascii'](x) for x in iput]
            oput = [ x.strip() if len(x) > self.threshould_length  else "" for x  in non_ascii_removed_str_list]
            oput = [x for x in filter(None, oput)]
            oput = [x.replace('"','') for x in oput]
            return oput
        else:
            return list([])

    def cited_by_link_preprocessor(self, iput):
        if len(iput) > 0:
            links = [ x if 'citation' in x else '' for x in iput]
            links = [x for x in filter(None, links)]
            links = [self.site_name+x for x in links]
            # remove CFTOKEN
            links = [x.split('&CFID')[0] for x in links]
            # add flat get token
            links = [x+"&preflayout=flat" for x in links]
            return links

        else:
            return list([])

    def closed(self, reason):
        """
            do stuffs for writing files
        """

        with open('urls.json', 'w') as f:
            json.dump(self.link_completed, f)
        f.close()

        # with open('ALL_ITEMS.json', 'w') as f:
        #     json.dump(self.all_items, f)
        # f.close()
        #
        # with open('title_hash_to_id.json', 'w') as f:
        #     json.dump(self.title_hash_to_id, f)
        # f.close()

        self.logger.warn("Completed writing the scolled url to Json file")
