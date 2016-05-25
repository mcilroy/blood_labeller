class Entry:
    def __init__(self, file_name, index_in_array, cell_type, cutoff, more_than_one, obstructions, processed, modified):
        self.file_name = file_name
        self.index_in_array = index_in_array
        self.cell_type = cell_type
        self.cutoff = cutoff
        self.more_than_one = more_than_one
        self.obstructions = obstructions
        self.processed = processed
        self.modified = modified

    @property
    def index_in_array(self):
        return self.index_in_array

    @property
    def modified(self):
        return self.modified