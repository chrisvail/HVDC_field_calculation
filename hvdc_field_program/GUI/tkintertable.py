import tkinter as tk
from tkinter import ttk


class HeaderCell(tk.Frame):
    
    def __init__(self, parent, text):
        tk.Frame.__init__(self, parent)
        self.text = tk.StringVar(self)
        self.text.set(text)
        label = tk.Label(self, textvariable=self.text, bg="#D3D3D3", relief=tk.SUNKEN, padx=5, pady=2)      #font=("Verdana", 12), 
        label.pack(side="top", fill="both", expand=True)


    def __repr__(self):
        return "HeaderCell({})".format(self.text)

class DataCell(tk.Frame):
    
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.value = tk.StringVar(self)

        entry = tk.Entry(self, textvariable=self.value, width=12)       #font=("Verdana", 8), 
        entry.pack(side="top", fill="both", expand=True, ipady=3)

    
    def __repr__(self):
        return "DataCell({})".format(self.value.get())


class TkTable(tk.Frame):
    
    def __init__(self, parent, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.colHeader = False
        self.rowHeader = False
        self.columns = 1
        self.rows = 1
        self.table = [[DataCell(self)]]
        
        self._map()


    def get_values(self):

        values = []
        for row in self.table:
            newRow = []
            for cell in row:
                try:
                    newRow.append(cell.value.get())
                except AttributeError:      # Header cell
                    pass

            if newRow != []:
                values.append(newRow)

        return values


    def append_row_data(self, headers=["--No Header--"]):
        
        number = len(headers) if isinstance(headers, list) else headers
        addHeader = isinstance(self.table[-1][0], HeaderCell)

        for i in range(number):
            newRow = [DataCell(self) for x in range(self.columns)]

            if addHeader:
                newRow = [HeaderCell(self, headers[i])] + newRow

            self.table.append(newRow)
        
        for y, row in enumerate(self.table):
            if y < self.rows:
                continue
            for x, cell in enumerate(row):
                cell.grid(row=y, column=x, sticky=tk.NSEW)

        self.rows += number

    
    def add_header(self, values, index=0):

        if len(values) != self.columns:
            raise ValueError("Incorrect number of values")

        elif self.colHeader:
            return

        newHeaders = [[HeaderCell(self, str(x)) for x in values]]

        if isinstance(self.table[-1][0], HeaderCell):
            newHeaders = [[tk.Frame(self)] + newHeaders[0]]
        
        self._unmap()
        self.table = self.table[:index] + newHeaders + self.table[index:]
        self._map()

        self.colHeader = True


    def add_column(self, headers=[], number=-1):
        
        if self.colHeader and len(headers) == 0:
            print(self.colHeader, headers, number)
            raise ValueError("Not enough headers have been given")
        
        elif len(headers) == 0 and not self.colHeader:
            number = 1 if number == -1 else number

        else:
            number = len(headers)
        

        for i, row in enumerate(self.table):
            if isinstance(row[-1], HeaderCell):
                for j in range(number):
                    self.table[i].append(HeaderCell(self, headers[j]))

                    self.table[i][-1].grid(row=i, column=self.columns + self.rowHeader + j, sticky=tk.NSEW)

                
            else:
                for j in range(number):                   
                    self.table[i].append(DataCell(self))
                    self.table[i][-1].grid(row=i, column=self.columns + self.rowHeader + j, sticky=tk.NSEW)

        self.columns += number


    def add_row_headers(self, headers=[]):

        if self.rowHeader:
            return

        self._unmap()

        headerCount = 0
        for i, row in enumerate(self.table):
            if isinstance(row[-1], DataCell):
                self.table[i] = [HeaderCell(self, headers[headerCount])] + self.table[i]
                headerCount += 1

            else:
                self.table[i] = [tk.Frame(self)] + self.table[i]

        self._map()
        self.rowHeader = True


    def remove_row(self):

        if self.rows == 1:
            return

        self._unmap()
        self.table = self.table[:-1]
        self._map()
        self.rows += -1


    def remove_column(self):

        if self.columns == 1:
            return

        self._unmap()
        
        for i, row in enumerate(self.table):
            self.table[i] = row[:-1]

        self._map()
        self.columns += -1


    def _reset(self):
        self._unmap()

        self.colHeader = False
        self.rowHeader = False
        self.columns = 1
        self.rows = 1
        self.table = [[DataCell(self)]]
        
        self._map()
        
    
    def _unmap(self):
        for row in self.table:
            for cell in row:
                cell.grid_forget()

    
    def _map(self):
        for y, row in enumerate(self.table):
            for x, cell in enumerate(row):
                cell.grid(row=y, column=x, sticky=tk.NSEW)


if __name__ == "__main__":

    root = tk.Tk()

    table = TkTable(root) #, ("Time", "Layer 1", "Layer 2", "Layer 3", "Layer 4", "Layer 5"))
    table.pack(padx=10, pady=10)

    button = tk.Button(root, text="Print values", command=lambda: print(table.get_values()))
    button.pack()

    b2 = tk.Button(root, text="Add line", command=table.append_row_data)
    b2.pack()

    b21 = tk.Button(root, text="Add 5 lines", command=lambda: table.append_row_data(["1", "2", "3", "4", "5"]))
    b21.pack()

    b3 = tk.Button(root, text="Add Headers", command=lambda: table.add_header(["H{}".format(x) for x in range(table.columns)]))
    b3.pack()

    b4 = tk.Button(root, text="Add column", command=lambda: table.add_column(["Col"]))
    b4.pack()

    b5 = tk.Button(root, text="Add row headers", command=lambda: table.add_row_headers(["C{}".format(x) for x in range(len(table.table) - table.colHeader)]))
    b5.pack()

    b6 = tk.Button(root, text="Reset", command=table._reset)
    b6.pack()

    b7 = tk.Button(root, text="Remove Row", command=table.remove_row)
    b7.pack()

    b8 = tk.Button(root, text="Remove Column", command=table.remove_column)
    b8.pack()

    root.mainloop()