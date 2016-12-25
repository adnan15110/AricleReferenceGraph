item_x_paths={
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

a = response.xpath(item_x_paths['cited_by_links']).extract()
site_name = 'http://dl.acm.org/'
def cited_by_link_preprocessor(iput):
    if len(iput) > 0:
        links = [ x if 'citation' in x else '' for x in iput]
        links = [x for x in filter(None, links)]
        links = [site_name+x for x in links]
        # remove CFTOKEN
        links = [x.split('&CFID')[0] for x in links]
        # add flat get token
        links = [x+"&preflayout=flat" for x in links]
        return links

    else:
        return list([])
cited_by_link_preprocessor(a)

        # if response.meta['depth']:
        #     self.logger.warn("Depth: {}  => {} ".format(response.meta['depth'],response.url))
        #     depth = response.meta['depth']
        #     depth+=1
        # else:
        #     self.logger.warn("Depth: {}  => {} ".format(response.meta['depth'],response.url))
        #     depth=0
        #
        # if depth<6:
        #     yield scrapy.Request(self.urls[depth],
        #                          callback=self.parse,
        #                          meta={'depth': depth})



        # """
        # scrapy shell -s USER_AGENT='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36' 'http://dl.acm.org/citation.cfm?id=2488205&preflayout=flat'
        # """


scrapy shell -s USER_AGENT='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36' 'http://dl.acm.org/citation.cfm?id=1098650&preflayout=flat'
