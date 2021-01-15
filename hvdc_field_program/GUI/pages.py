import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename, askdirectory
from GUI.tkintertable import TkTable
import os
import csv
from decimal import Decimal as d


class GeneratorConfig(tk.Frame):

    def __init__(self, parent, cont, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        
        title = tk.Label(self, text="Model configuration", font=("Verdana", 12))
        title.grid(row=0, columnspan=4, column=0, sticky=tk.W, pady=5)

        self.vType = tk.StringVar(self)
        self.vType.set("Constant")
        self.vType.trace("w", self.swap_voltage_input)
        vTypeLbl = tk.Label(self, text="Voltage type: ")
        vTypeOp = tk.OptionMenu(self, self.vType, "Constant", "Variable", "File")
        vTypeLbl.grid(row=5, column=0, stick=tk.NW, pady=5)
        vTypeOp.grid(row=5, column=7, sticky=tk.NW, pady=5)

        self.voltageTable = TkTable(self, padx=20, pady=5)
        self.voltageTable.add_row_headers(["Voltage"])
        self.voltageTable.grid(row=5, rowspan=5, column=1, columnspan=4, sticky=tk.W)

        self.voltageFileFrame = tk.Frame(self, pady=5)
        self.voltageFile = tk.StringVar(self)
        loadVoltageFile = tk.Button(self.voltageFileFrame, text="Load Voltage File", padx=5, command=self._loadFile)
        voltageFileLabel = tk.Label(self.voltageFileFrame, textvariable=self.voltageFile, wraplength=250, justify=tk.LEFT)
        loadVoltageFile.grid(row=0, column=0, sticky=tk.W)
        voltageFileLabel.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        

        pResistanceLbl = tk.Label(self, text="Parasitic resistance: ")
        self.pResistance = tk.StringVar(self)
        pResistanceEntry = tk.Entry(self, textvariable=self.pResistance)
        pResistanceLbl.grid(row=11, column=0, sticky=tk.W, pady=5)
        pResistanceEntry.grid(row=11, column=1, sticky=tk.W, padx=20, pady=5)

        pTimingsLbl = tk.Label(self, text="Timings: ")
        self.timingTable = TkTable(self, padx=20, pady=5)
        self.timingTable.append_row_data(2)
        self.timingTable.add_row_headers(["Start time", "Stop time", "Maximum timestep"])
        pTimingsLbl.grid(row=12, column=0, sticky=tk.NW, pady=5)
        self.timingTable.grid(row=12, rowspan=5, column=1, columnspan=4, sticky=tk.NW)

        compressionLbl = tk.Label(self, text="Compression: ")
        self.compression = tk.StringVar(self)
        compressionEntry = tk.Entry(self, textvariable=self.compression)
        compressionLbl.grid(row=18, column=0, sticky=tk.W, pady=5)
        compressionEntry.grid(row=18, column=1, sticky=tk.W, padx=20, pady=5)


    def _loadFile(self):
        self.voltageFile.set(askopenfilename(initialdir=os.path.expanduser("~"), title="Select file", filetypes=(("CSV files", ("*.csv", "*.txt")), ("All files", "*.*"))))


    def swap_voltage_input(self, *args):

        if self.vType.get() == "File":
            self.voltageTable.grid_forget()
            self.voltageFileFrame.grid(row=5, rowspan=5, column=1, columnspan=4, sticky=tk.W, padx=20)

        else:
            self.voltageFileFrame.grid_forget()
            if self.vType.get() == "Constant":
                
                self.voltageTable._reset()
                self.voltageTable.add_row_headers(["Voltage"])
                self.voltageTable.grid(row=5, rowspan=5, column=1, columnspan=4, sticky=tk.W)
            
            else:
                self.voltageTable._reset()
                self.voltageTable.add_column()
                self.voltageTable.append_row_data(9)
                self.voltageTable.add_header(("Time", "Voltage"))
                self.voltageTable.add_row_headers([x for x in range(1, 11)])

                self.voltageTable.grid(row=5, rowspan=5, column=1, columnspan=4, sticky=tk.W)


    def get_data(self):

        if self.vType.get() == "File":
            voltage = "var, {}"
            with open(self.voltageFile.get(), "r") as file:
                csvreader = csv.reader(file, "excel")
                voltage = voltage.format(" ".join(["{} {}".format(*x) for x in csvreader]))
                

        elif self.vType.get() == "Constant":
            voltage = "const, {}".format(self.voltageTable.get_values()[0][0])
        else:
            voltage = "var, {}".format(" ".join(["{} {}".format(*x) for x in self.voltageTable.get_values()]))

        values = {
            "voltage":voltage,
            "parasitic resistance":self.pResistance.get(),
            "sim timings":self.timingTable.get_values(),
            "compression":self.compression.get()
        }
        return values


    def load_values(self, file):

        with open(file, "r") as f:
            for line in f:
                # Parses line 
                line = [x.strip() for x in line.split('=')]
                
                if line[0] == "voltage":
                    v_type = [x.strip() for x in line[1].split(',')]

                    if v_type[0] == "const":
                        self.vType.set("Constant")
                        self.voltageTable.table[0][1].value.set(v_type[1])
                    elif v_type[0] == "var":
                        points = v_type[1].strip(" ").split(" ")
                        new_points = []
                        for ind, p in enumerate(points):
                            if ind % 2 == 0:
                                new_points.append([p])
                            else:
                                new_points[-1].append(p)
                        
                        new_file = file.split("/")
                        new_file[-1] = new_file[-1].replace("setup", "config")
                        new_file = "/".join(new_file)
                        new_file = new_file.replace("generator_config", "voltage_file")   
                        points = [(points[i], points[i + 1]) for i in range(0, len(points), 2)]
                        with open(new_file, "w", newline="") as f:
                            csvwriter = csv.writer(f, "excel")
                            for line in points:
                                csvwriter.writerow(line)

                        self.vType.set("File")
                        self.voltageFile.set(new_file)
                        

                elif line[0] == "parasitic resistance":
                    self.pResistance.set(line[1])
                
                elif line[0] == "time start":
                    self.timingTable.table[0][1].value.set(line[1])

                elif line[0] == "time stop":
                    self.timingTable.table[1][1].value.set(line[1])
                
                elif line[0] == "time step":
                    self.timingTable.table[2][1].value.set(line[1])

                elif line[0] == "compression":
                    self.compression.set(line[1])





class IteratorConfig(tk.Frame):

    def __init__(self, parent, cont, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.prevResistorNumber = 5
        self.pastResistivity = []
        self.pastAlpha = []

        title = tk.Label(self, text="Calculation configuration", font=("Verdana", 12))
        title.grid(row=0, columnspan=4, column=0, sticky=tk.W, pady=5)

        self.resistorNumber = tk.IntVar(self)
        self.resistorNumber.set(self.prevResistorNumber)
        resistorNumberLbl = tk.Label(self, text="Number of resistors")
        resistorNumberSpin = tk.Spinbox(self, from_=1, to=8, textvariable=self.resistorNumber)
        resistorNumberLbl.grid(row=1, column=0, sticky=tk.W, pady=5)
        resistorNumberSpin.grid(row=1, column=1, sticky=tk.W, padx=20, pady=5)

        self.outputName = tk.StringVar(self)
        outputNameLbl = tk.Label(self, text="Output file name: ")
        outputNameEntry = tk.Entry(self, textvariable=self.outputName, width=50)
        outputNameLbl.grid(row=4, column=0, sticky=tk.W, pady=5)
        outputNameEntry.grid(row=4, column=1, sticky=tk.W, padx=20, pady=5)

        self.outputFolder = tk.StringVar(self)
        self.outputFolder.set("")
        outputFolderLbl = tk.Label(self, text="Output folder: ")
        outputFolderLbl.grid(row=5, column=0, sticky=tk.W, pady=5)

        outputFolderFrame = tk.Frame(self)
        outputFolderText = tk.Label(outputFolderFrame, textvariable=self.outputFolder, width=75)
        outputFolderBtn = tk.Button(outputFolderFrame, text="Load Folder", padx=10, command=self._loadOutFolder)
        outputFolderBtn.pack(side=tk.LEFT)
        outputFolderText.pack(side=tk.LEFT)
        outputFolderFrame.grid(row=5, column=1, columnspan=5, sticky=tk.W, padx=20, pady=5)
        

        self.iterationNumber = tk.StringVar(self)
        self.iterationNumber.set(5)
        iterationLbl = tk.Label(self, text="Number of iterations: ")
        iterationSpin = tk.Spinbox(self, from_=1, to=20, textvariable=self.iterationNumber)
        iterationLbl.grid(row=6, column=0, sticky=tk.W, pady=5)
        iterationSpin.grid(row=6, column=1, sticky=tk.W, padx=20, pady=5)

        radiusLbl = tk.Label(self, text="Radius data: ")
        self.radiusTable = TkTable(self, padx=20, pady=5)
        self.radiusTable.append_row_data(2)
        self.radiusTable.add_row_headers(["Conductor screen radius", "Insulation screen radius", "Number of layers"])
        radiusLbl.grid(row=7, column=0, sticky=tk.NW, pady=5)
        self.radiusTable.grid(row=7, rowspan=3, column=1, columnspan=2, sticky=tk.NW, pady=5)

        self.resistivityTable = TkTable(self, padx=20, pady=5)
        self.resistivityTable.add_column(number=4)
        self.resistivityTable.add_header(["R{}".format(x + 1) for x in range(5)])
        self.resistivityTable.append_row_data()
        self.resistivityTable.add_row_headers(["Resistivity", "Temperature \nCoefficient of \nResistivity"])
        self.resistivityTable.grid(row=11, rowspan=2, column=1, columnspan=9, sticky=tk.NSEW, pady=5)
        self.resistorNumber.trace("w", self.update_resistor_numbers)        # Function only works if the table has been created

        self.gamma = tk.StringVar(self)
        gammaLbl = tk.Label(self, text="Gamma: ")
        self.gammaEntry = tk.Entry(self, textvariable=self.gamma)
        gammaLbl.grid(row=13, column=0, sticky=tk.W, pady=5)
        self.gammaEntry.grid(row=13, column=1, sticky=tk.W, padx=20, pady=5)

        self.capacitanceFile = tk.StringVar(self)
        capacitanceFileLbl = tk.Label(self, text="Capacitance file: ")
        self.capacitanceFileEntry = tk.Entry(self, textvariable=self.capacitanceFile)
        capacitanceFileBtn = tk.Button(self, text="Load File", padx=5, command=self._loadCapacitanceFile)
        capacitanceFileLbl.grid(row=14, column=0, sticky=tk.W, pady=5)
        self.capacitanceFileEntry.grid(row=14, column=1, columnspan=2, sticky=tk.EW, padx=20, pady=5)
        capacitanceFileBtn.grid(row=14, column=3, sticky=tk.W, pady=5)

        self.tempdataFile = tk.StringVar(self)
        tempdataFileLbl = tk.Label(self, text="Temperature data file: ")
        self.tempdataFileEntry = tk.Entry(self, textvariable=self.tempdataFile)
        tempdataFileBtn = tk.Button(self, text="Load File", padx=5, command=self._loadTempdataFile)
        tempdataFileLbl.grid(row=15, column=0, sticky=tk.W, pady=5)
        self.tempdataFileEntry.grid(row=15, column=1, columnspan=2, sticky=tk.EW, padx=20, pady=5)
        tempdataFileBtn.grid(row=15, column=3, sticky=tk.W, pady=5)

        timesNote = tk.Label(self, text="Enter a comma separated list of times")
        timesNote.grid(row=16, column=1, columnspan=2, sticky=tk.W, padx=20)
        self.times = tk.StringVar(self)
        timesLbl = tk.Label(self, text="Times of interest: ")
        self.timesEntry = tk.Entry(self, textvariable=self.times)
        timesLbl.grid(row=17, column=0, sticky=tk.W, pady=5)
        self.timesEntry.grid(row=17, column=1, columnspan=2, sticky=tk.EW, padx=20, pady=5)


    def update_resistor_numbers(self, *args):
        
        newResNumber = self.resistorNumber.get()
        if newResNumber == "": return

        res, alpha = self.resistivityTable.get_values()
        for i, (r, a) in enumerate(zip(res, alpha)):
            if i < len(self.pastResistivity):
                if self.pastResistivity[i] != r:
                    self.pastResistivity[i] = r
                if self.pastAlpha[i] != a:
                    self.pastAlpha[i] = a
            else:
                self.pastResistivity.append(r)
                self.pastAlpha.append(a)


        self.resistivityTable._reset()
        self.resistivityTable.add_column(number=newResNumber - 1)
        self.resistivityTable.append_row_data()
        self.resistivityTable.add_header([f"R{x + 1}" for x in range(newResNumber)])
        self.resistivityTable.add_row_headers(["Resistivity", "Temperature \nCoefficient of \nResistivity"])

        for i in range(self.resistivityTable.columns if self.resistivityTable.columns < len(self.pastAlpha) else len(self.pastAlpha)):
            self.resistivityTable.table[1][i + 1].value.set(self.pastResistivity[i])
            self.resistivityTable.table[2][i + 1].value.set(self.pastAlpha[i])


    def _loadCapacitanceFile(self):
        self.capacitanceFile.set(askopenfilename(initialdir=os.path.expanduser("~"), title="Select file", filetypes=(("CSV files", ("*.csv", "*.txt")), ("All files", "*.*"))))


    def _loadTempdataFile(self):
        self.tempdataFile.set(askopenfilename(initialdir=os.path.expanduser("~"), title="Select file", filetypes=(("CSV files", ("*.csv", "*.txt")), ("All files", "*.*"))))


    def get_data(self):

        radius = self.radiusTable.get_values()
        if radius[0][0] != "":
            radius = tuple(d(x[0]) for x in radius)
            radius = (radius[0], radius[1], (radius[1] - radius[0]) / radius[2])
        else:
            radius = (0, 0, 0)

        if self.outputFolder.get() != "":
            output = self.outputFolder.get() + "/" + self.outputName.get()
        else:
            output = self.outputName.get()

        values = {
            "tempdata":self.tempdataFile.get(),
            "capacitance":self.capacitanceFile.get(),
            "outputFileName":output,
            "iterations":self.iterationNumber.get(),
            "radius":",".join([str(x) for x in radius]),
            "resistivity":",".join(tuple(self.resistivityTable.get_values()[0])),
            "alpha":",".join(tuple(self.resistivityTable.get_values()[1])),
            "gamma":self.gamma.get(),
            "times":self.times.get()
        }
        return values

    
    def load_values(self, file):

        with open(file, "r") as f:
            for line in f:
                # Parses line 
                line = [x.strip() for x in line.split('=')]
                # For each line with data, process and store the data
                if line[0] == "temperature data csv":
                    self.tempdataFile.set(line[1])
                elif line[0] == "output file name format":
                    self.outputName.set(line[1])
                elif line[0] == "number of iterations":
                    self.iterationNumber.set(int(line[1]))
                elif line[0] == "radius data":
                    start, stop, step = [d(x) for x in line[1].split(',')]
                    self.radiusTable.table[0][1].value.set(start)
                    self.radiusTable.table[1][1].value.set(stop)
                    self.radiusTable.table[2][1].value.set((stop - start) / step)
                elif line[0] == "resistivty data":
                    resistivity_data = [d(x) for x in line[1].split(',')]
                    self.resistorNumber.set(len(resistivity_data))
                    for i, value in enumerate(resistivity_data):
                        self.resistivityTable.table[1][i + 1].value.set(value)
                elif line[0] == "temperature coefficient of resistivity data":
                    for i, value in enumerate([d(x) for x in line[1].split(',')]):
                        self.resistivityTable.table[2][i + 1].value.set(value)
                elif line[0] == "gamma":
                    self.gamma.set(d(line[1]))
                elif line[0] == "capacitances":
                    self.capacitanceFile.set(line[1])
                elif line[0] == "times":
                    self.times.set(line[1])


    def _loadOutFolder(self):
        self.outputFolder.set(askdirectory(initialdir=os.path.expanduser("~"), title="Select folder"))

