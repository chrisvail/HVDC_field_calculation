import csv

class GraphGetter:

    def __init__(self, file, compression=1):
        self.xCoord = []
        self.yCoord = []
    
        if file != "":
            with open(file, "r") as infile:
                dialect = csv.Sniffer().sniff(infile.read(5000))
                infile.seek(0)
                reader = csv.reader(infile, dialect)
                length = 0
                
                for line in reader:
                    line = [x for x in line]
                    if length == 0:
                        length = len(line) - 1
                        self.yCoord = [[] for x in range(length)]

                    for index, value in enumerate(line):
                        if index == 0:
                            self.xCoord.append(value)
                        else:
                            self.yCoord[index - 1].append(value)


    def __len__(self):
        return len(self.xCoord)

    def __repr__(self):
        return "GraphGetter(file)"

    def get_plots(self):

        if self.xCoord == [] or self.yCoord == []:
            return (0, 1), (0, 1)

        for coords in self.yCoord:
            yield self.xCoord, coords


