import os


def write_generator_file(generatordata):

    lines = ["Setup for complex_generator.py:\n",
             "\n",
             "Dictates the values of the voltage source. \n",
             "There are 2 modes var and const:\n",
             "    const: 1 constant voltage given after comma.\n",
             "    var: A variable piecewise linear function. Takes time voltage pairs separated by a space. \n",
             "         The voltage output is interpolated between pairs.\n",
             "Examples\n",
             "    const, 262.5k  ---  Constant value of 262.5kV \n",
             "    var, 0 0 1 400k 14400 400k 14401 0  ---  Voltage starts at 0V and rises to 400kV over 1 second.\n",
             "                                             The voltage stays at 400kV for 4 hours then it drops\n",
             "                                             back to 0V over 1 second.\n",
             "\n",
             "voltage = {}\n",
             "\n",
             "The value of the resistance in series with the voltage source. Defaults to 0 if left out.\n",
             "parasitic resistance = {}\n",
             "\n",
             "Time to start saving data, the end of the simulation and the maximum time step.\n",
             "time start = {}\n",
             "time stop = {}\n",
             "time step = {}\n",
             "\n",
             "The number of consecutive points that can be combined in the export file. Larger numbers result in a \n",
             "smaller export file. Defaults to 16 if left out.\n",
             "compression = 1"]
    with open("generator_config.txt", "w") as output:
        for line in lines:
            if line.split("=")[0] == "voltage ":
                line = line.format(generatordata["voltage"])
            
            elif line.split("=")[0] == "parasitic resistance ":
                line = line.format(generatordata["parasitic resistance"])

            elif line.split("=")[0] == "time start ":
                line = line.format(generatordata["sim timings"][0][0])

            elif line.split("=")[0] == "time stop ":
                line = line.format(generatordata["sim timings"][1][0])
            
            elif line.split("=")[0] == "time step ":
                line = line.format(generatordata["sim timings"][2][0])
            
            elif line.split("=")[0] == "compression ":
                line = line.format(generatordata["compression"])
                
            
            output.write(line)


        
    
        

def write_iteration_file(iterationdata):

    lines = ["Setup for iteration.py:\n",
             "File location holding time-temperature data for each layer of the cable. Ensure any slashes are forward '/'.\n",
             "temperature data csv = {}\n",
             "\n",
             "Format of the output files where {} is the number of the iteration\n",
             "output file name format = {}\n",
             "\n",
             "Number of times that the program is rerun\n",
             "number of iterations = {}\n",
             "\n",
             "Data for the radii of the layers in the form: start, stop, difference\n",
             "radius data = {}\n",
             "\n",
             "Data for the resistors R1 --> R5\n",
             "resistivty data = {}\n",
             "temperature coefficient of resistivity data = {}\n",
             "\n",
             "Value used in the field dependancy of resistance\n",
             "gamma = {}\n",
             "\n",
             "File containing the capacitance values as required by complex_generator.py\n",
             "capacitances = {}\n",
             "\n",
             "Comma separated list of times which are of interest. The field at these points will be output in a smaller csv file.\n",
             "times = {}"]

    with open("iteration_config.txt", "w") as output:
        for line in lines:
            if line.split("=")[0] == "temperature data csv ":
                line = line.format(iterationdata["tempdata"])
            
            elif line.split("=")[0] == "output file name format ":
                line = line.format(iterationdata["outputFileName"])

            elif line.split("=")[0] == "number of iterations ":
                line = line.format(iterationdata["iterations"])

            elif line.split("=")[0] == "radius data ":
                line = line.format(iterationdata["radius"])

            elif line.split("=")[0] == "resistivty data ":
                line = line.format(iterationdata["resistivity"])

            elif line.split("=")[0] == "temperature coefficient of resistivity data ":
                line = line.format(iterationdata["alpha"])

            elif line.split("=")[0] == "gamma ":
                line = line.format(iterationdata["gamma"])

            elif line.split("=")[0] == "capacitances ":
                line = line.format(iterationdata["capacitance"])

            elif line.split("=")[0] == "times ":
                line = line.format(iterationdata["times"])

            output.write(line)
