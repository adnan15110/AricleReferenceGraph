Project Goal:

I would need a python script which starts crawling the information from the following page:
http://dl.acm.org/citation.cfm?id=2488205&CFID=875547729&CFTOKEN=93609255&preflayout=flat

Especially the section "references" and "cited by".

The idea would be to start with an document (page / scientific paper) and build up a network graph with the references connected to this paper and also the papers who cited this paper. This process should then be extended to all papers to a crawling depth of 6 elements.

You can see a picture were I tried to visualize the crawling documents.

The crawled information for each element must be at least the name, Title, Date, Journal, abstract

Example starting point would be
http://dl.acm.org/citation.cfm?id=2488205&CFID=875547729&CFTOKEN=93609255&preflayout=flat

If for example a element in references section has no link only text, then the information should still be scrapped and the crawling part ends at this point.

The graph should be build using the networkx library from python.
For the scrapping the python library scrape should be used.

A visualization of the graph is not necessary. Only the crawling part and the network build part should be developed.


Libraries Used:
1.Scrapy
2.NetworkX
