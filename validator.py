class Node:
    def __init__(self) :
        self.next = [None]*10;
        self.exists = False;

class Validator:
    def __init__(self):
        self.root = Node()
        

    def add_voter(self, id):
        id = str(id)
        crawler = self.root
        for n in id :
            if  crawler.next[int(n)] is None :
                crawler.next[int(n)] = Node()
            crawler = crawler.next[int(n)]
        crawler.Exists = True;

    def has_voted(self, id):

        crawler = self.root
        for n in str(id):
            
            if crawler.next[int(n)] is None : 
                return False
            crawler = crawler.next[int(n)]
        return True


validator = Validator()

if __name__ == "__main__" :
    validator.add_voter(123456789198)
    validator.add_voter(123214345086)
    validator.add_voter(756483947583)
    print(validator.has_voted(123214345086))
    
    print(validator.has_voted(122214345086))
