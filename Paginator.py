class Paginator:
    def __init__(self, filename, pagelen=50):
        self.file = filename
        self.pagelen = pagelen
        self.pages = {}

    def getPage(self, number):
        try:
            file = open(self.file, 'r')
            file.readline()
            file.seek(0)
        except UnicodeDecodeError:
            return []
        lines = []

        if number not in self.pages.keys():
            offset = 0
            if len(self.pages) > 0 and number > 1:
                ll = list(self.pages.keys())
                file.seek(self.pages[ll[-1]])
                offset = ll[-1]
            for i in range(self.pagelen * offset, self.pagelen * (number)):
                line = file.readline()
                if line == '':
                    break
                lines.append(line)
                if i > self.pagelen * offset and i % (self.pagelen - 1) == 0:
                    self.pages[i//(self.pagelen - 1) + 1] = file.tell()

        else:
            file.seek(self.pages[number])
            for i in range(self.pagelen):
                line = file.readline()
                if not line:
                    break
                lines.append(line)
                if i > 0 and i % (self.pagelen - 1) == 0:
                    self.pages[number + 1] = file.tell()

        file.close()
        return lines[-self.pagelen:]

