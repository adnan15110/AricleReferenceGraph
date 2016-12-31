import json
import hashlib
import pdb
import pickle
import networkx as nx

class DataPreProcessor:

    def __init__(self):
        self.data=[]
        self.file_name = 'output.json'
        self.max_token = 2 # indicates how many token to consider as possible title text

        self.hash_to_title_filename='hash_to_title.json'
        self.hash_to_title = {}

        self.hash_to_info_filename='hash_to_info.json'
        self.hash_to_info = {}
        pass

    def load_data(self):
        """
        loads the json data
        [list of articles]
        """
        with open(self.file_name) as json_data:
            data = json.load(json_data)
            json_data.close()

        return data

    def contains_invalid_word_or_not(self, input_string):
        """
        return whether the input string contains such text or not
        """
        does_not_contain_words = ['acm', 'symposium', 'proceedings', 'journal','conference', 'chi']
        processed_input = input_string.lower()

        flag = False

        for word in does_not_contain_words:
            if word in processed_input:
                flag = True
                break

        return flag

    def get_article_name_from_citation_txt(self, input_string):
        """

        """
        processed_input_string = input_string.lower()
        tokens = processed_input_string.split(",")
        tokens=[tk.strip() for tk in tokens]
        tokens.sort(key = lambda s: len(s), reverse=True )

        article_name=None

        for tk in tokens[0:self.max_token]:
            if not self.contains_invalid_word_or_not(tk):
                article_name= tk
                break

        return article_name

    def get_string_token(self, input_string, token):
            """

            """
            processed_input_string = input_string.lower()
            tokens = processed_input_string.split(token)
            tokens=[tk.strip() for tk in tokens]
            tokens.sort(key = lambda s: len(s), reverse=True )

            article_name=None

            for tk in tokens[0:self.max_token]:
                if not self.contains_invalid_word_or_not(tk):
                    article_name= tk
                    break

            return article_name

    def reference_title_processor(self,ref):
        titles = []
        titles.append(self.get_string_token(ref, token=","))
        titles.append(self.get_string_token(ref, token="."))
        # titles.sort(key = lambda s: sum(c.isdigit() for c in s), reverse=False)

        titles = [x for x in titles if x is not None]

        processed_after_eleminating_digits=[]
        for title in titles:
            num_digits = sum(c.isdigit() for c in title)
            if num_digits < 4:
                processed_after_eleminating_digits.append(title)

        processed_after_eleminating_digits.sort(key = lambda s: s.count("."), reverse=False)

        if len(processed_after_eleminating_digits) >0:
            return processed_after_eleminating_digits[0]
        else:
            return None

    def get_create_hashkey(self, input_string):
        """
        creates hash keys
        """
        processed_input = input_string.lower()
        hash_key = hashlib.md5(processed_input.encode('utf-8')).hexdigest()
        return hash_key

    def save(self):

        with open(self.hash_to_info_filename, 'w') as fp:
            json.dump(self.hash_to_info, fp)

        with open(self.hash_to_title_filename, 'w') as fp:
            json.dump(self.hash_to_title, fp)

    def process(self):

        self.data = self.load_data()

        for article in self.data:
            title = article['Title']
            references=article['References']
            cited_by=article['Cited_by']

            hash_key = self.get_create_hashkey(title)

            self.hash_to_title[hash_key]=title
            self.hash_to_info[hash_key]=article

            """
            Processing reference is bit nastier
            """
            for ref in references:
                ref_title=self.reference_title_processor(ref)
                if ref_title is not None:
                    ref_hash_key = self.get_create_hashkey(ref_title)
                    self.hash_to_title[ref_hash_key] = ref_title

            for c_by in cited_by:
                c_by_title = self.get_article_name_from_citation_txt(c_by)
                if c_by_title is not None:
                    c_by_hash_key = self.get_create_hashkey(c_by_title)
                    self.hash_to_title[c_by_hash_key] = c_by_title

        self.save()

class BuildGraph:

    def __init__(self):

        self.data_processor = DataPreProcessor()
        self.data = []
        self.hash_to_title = {}
        self.in_out_graph_file_name="graph.json"
        self.in_out_graph={}

    def load_data(self):

        self.data = self.data_processor.load_data()

        with open(self.data_processor.hash_to_title_filename) as json_data:
            self.hash_to_title = json.load(json_data)
            json_data.close()


    def build_graph(self):

        for article in self.data:

            article_key = self.data_processor.get_create_hashkey(article['Title'])
            referencs_IDs = []
            cited_by_IDs = []

            if article_key in self.hash_to_title:
                #if the key is already there
                references=article['References']
                cited_by=article['Cited_by']

                for ref in references:
                    ref_title=self.data_processor.reference_title_processor(ref)
                    if ref_title is not None:
                        ref_hash_key = self.data_processor.get_create_hashkey(ref_title)
                        if ref_hash_key in self.hash_to_title:
                            referencs_IDs.append(ref_hash_key)


                for c_by in cited_by:
                    c_by_title = self.data_processor.get_article_name_from_citation_txt(c_by)
                    if c_by_title is not None:
                        c_by_hash_key = self.data_processor.get_create_hashkey(c_by_title)
                        if c_by_hash_key in self.hash_to_title:
                            cited_by_IDs.append(c_by_hash_key)


                self.in_out_graph[article_key]={"References":referencs_IDs, "Cited_by":cited_by_IDs}


    def save(self):

        with open(self.in_out_graph_file_name, 'w') as fp:
            json.dump(self.in_out_graph, fp)


    def process(self):
        self.load_data()
        self.build_graph()
        self.save()

class BuildNetworkXGraph:

    def __init__(self):
        self.graph = nx.DiGraph()
        self.graph_file_name='nx_graph.gpickle'
        self.json_graph={}
        self.hash_to_info={}
        self.hash_to_title={}

    def load_data(self):

        """
            loads all three data source required for doing anything
        """

        with open('hash_to_title.json') as json_data:
            self.hash_to_title = json.load(json_data)
            json_data.close()

        with open('hash_to_info.json') as json_data:
            self.hash_to_info = json.load(json_data)
            json_data.close()

        with open('graph.json') as json_data:
            self.json_graph = json.load(json_data)
            json_data.close()

    def buildGraph(self):
        for k,v in self.json_graph.items():

            if not self.graph.has_node(k):
                self.graph.add_node(k)

            # add references
            for ref in v['References']:
                if not self.graph.has_node(ref):
                    self.graph.add_node(ref)
                self.graph.add_edge(k,ref)


            # add cited_By
            for c_by in v['Cited_by']:
                if not self.graph.has_node(c_by):
                    self.graph.add_node(c_by)
                self.graph.add_edge(c_by,k)


    def saveGraph(self):
        #saves as pickle
        nx.write_gpickle(self.graph, self.graph_file_name)
        print("Graph saved as pickle {}".format(self.graph_file_name))

    def process(self):
        self.load_data()
        self.buildGraph()
        self.saveGraph()


if __name__ == '__main__':

    """
        Run the first part once to create the processed dictionary
        It will take bit time
    """
    # dataProcessor = DataPreProcessor()
    # dataProcessor.process()

    """
        Run the second part to create the data stucture
        It will take bit time too.

        Once it is done
        graph.json file will contain [hash] to [refernce] and [cited by]
        hash_to_title will contain [hash] to title text
        hash_to_info will contain [hash] to all information about that article

        output is simple json file

    """
    # buildGraph = BuildGraph()
    # buildGraph.process()

    """
        Convert the simple json to networkx DiGraph
    """
    buildNxGraph = BuildNetworkXGraph()
    buildNxGraph.process()
