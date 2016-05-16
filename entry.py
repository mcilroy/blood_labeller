class Entry:
    def __init__(self, file_name, index_in_array, type, cutoff, more_than_one, no_cell, obstructions, processed):
        self.file_name = file_name
        self.index_in_array = index_in_array
        self.type = type
        self.cutoff = cutoff
        self.more_than_one = more_than_one
        self.no_cell = no_cell
        self.obstructions = obstructions
        self.processed = processed
