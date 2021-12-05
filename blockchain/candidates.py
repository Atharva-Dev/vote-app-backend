class Candidate:
    id = 0
    def __init__(self, name) -> None:
        self.name = name
        self.id = Candidate.id;
        Candidate.id += 1
    
    def getId(self) :
        return self.id
    
    def __str__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def getTotalCandidates():
        return Candidate.id

if __name__ == "__main__":
    c1 = Candidate("c1")
    c2 = Candidate("c2")
    c3 = Candidate("c3")
    print(c1)
    print(c2)
    print(c3)
    print(Candidate.getTotalCandidates())

