class parserSBOL:
    def __init__(self, rows: int, columns: int):
        self.MAX_WELLS = rows*columns
        self.WELLS = []
        alpha = 'A'
        for row in range(1, rows):
            for column in range(1, columns):
                self.WELLS.append(str(alpha)+str(column))
            alpha = chr(ord(alpha)+1)
