##############################################################
#   Creates schematic for the complex model of any size      #
#   based on data taken from a csv file                      #
##############################################################

######## Code by Chris Vail ########

# Program takes in a very specifically laid out csv file.
# First line contains headers for capacitors for human readability
# Next lines contain information about capacitor values going across each section e.g. C1 -> C5
# One line per layer.
# Next line contains header information for human readability
# Finally the remaining lines have time on the left followed by (S1R1 -> S10R1) -> (S1R5 -> S10R5)   

# The program outputs a file which should include a .asc ending which is readable by LTSpice

# Imports argv to get commandline arguments
from sys import argv
import csv
from templatebuilder import TemplateBuilder


def generate_schematic(inpt_file, outpt_file, setup_file="config/generator_config.txt"):
    if inpt_file[-4:] != ".csv" or outpt_file[-4:] != ".asc" or setup_file[-4:] != ".txt":
        raise ValueError("Incorrect File types")
    main(inpt_file, outpt_file, setup_file)

    return 0
    

def main(inpt_file, outpt_file, setup_file):

    """ 
    Structures the flow of the program.
    Reads in data from the import file and writes the resultant schematic to the output file.
    Notably will automatically overwrite the output file.
    Takes no inputs and returns no output 
    """

    # Reads in values from configuration file
    v_string, parasiticResistance, timeStart, timeStop, timeStep, compression = setup(setup_file)

    # Reads and organises data from the input file
    capacitorValues, resistorValues = read_data(inpt_file)
    # Calculates equations of straight lines between resistor values in time
    resistorValues = process_resistorValues(resistorValues)
    # Converts line equations into a single if/elif/else statement for each resistor
    resistorValues = gen_resistor_strings(resistorValues, len(capacitorValues[0]), len(capacitorValues))
    # Combines the resistor values and capacitor values into one list
    data = [resistorValues[x] + capacitorValues[x] for x in range(len(capacitorValues))]

    # Opens output file for writing
    with open(outpt_file, 'w') as output:
        
        # Writes in standard header for schematic
        output.writelines(["Version 4\n", "SHEET 1 880 680\n"])

        # Writes in wires and a voltage source connecting the top to the bottom of the stack of sections
        output.writelines(["WIRE 0 0 -480 0\n", 
                           "WIRE -480 0 -480 " + str(352 * len(data) + 96) + "\n",
                           "WIRE 0 " + str(352 * len(data) + 96) + " -480 " + str(352 * len(data) + 96) + "\n",
                           "WIRE 0 " + str(352 * len(data)) + " 0 " + str(352 * len(data) + 96) + "\n",
                           "SYMBOL voltage -480 " + str(352 * len(data) - 32) + " R0\n",
                           "SYMATTR InstName V1\n", 
                           "SYMATTR Value " + v_string + "\n",
                           "SYMATTR SpiceLine Rser=" + parasiticResistance + "\n",
                           "FLAG 0 " + str(352 * len(data) + 96) + " 0\n"])

        # Uses resistor and capacitor data to create and write each section to the output file
        for index, template in enumerate(data):
            for line in create_section_text(template, index):
                output.write(line)

        # Sets positioning of SPICE directives so they can be read clearly off of the schematic
        op_x = -512
        op_y = 352 * len(data) + 128
        # Directive specifying running parameter
        output.write("TEXT " + str(op_x) + " " + str(op_y) + " Left 2 !.tran 0 "
                     + timeStop + " " + timeStart + " " + timeStep + " startup\n")
        # Directive specifying calculation tolerences
        output.write("TEXT " + str(op_x) + " " + str(op_y + 48)
                     + " Left 2 !.options gmin=1E-24 abstol=1E-18 reltol=1E-6 vntol=1E-6 plotwinsize=" + compression + "\n")


def read_data(inpt_file):

    """ 
    Reads the data from the input file and returns an organised list of values

    Only to be used by this program and should never be imported elsewhere

    Args: None

    Returns: A list containing 2 lists
                - Values for capacitors
                - Values for resistors
    """

    # Stores values for capacitors and resistors separately
    sec_val = [[], []]
    # Used to keep track of whether to add values to resistors or capacitors
    headerCount = 0
    # Attempts to open file and read in values and raises value error if it cant
    try:
        with open(inpt_file, 'r') as inpt:
            # Creates a csv reader object which deals with csv format
            reader = csv.reader(inpt, dialect="excel")
            for line in reader:
                # Skip headings
                if (line[0][0]).isalpha():
                    headerCount += 1
                     
                # Creates a list of values and adds them
                else:
                    # Values are for capacitors
                    if headerCount == 1:
                        sec_val[0].append([x for x in line if x != ""])
                    # Values are for resistors
                    else:
                        sec_val[1].append([x for x in line if x != ""])

    # Raises error if file not found
    except FileNotFoundError as e:
        print(inpt_file)
        raise ValueError("Input file does not exist\nMake sure you include the file extension") from e

    return sec_val


def create_section_text(values, depth):

    """ 
    Takes resistor and capacitance values and the layer of the section and returns a list of strings which detail
    the section in a format readable by LTSpice.

    Args:
        values - List of numbers as strings or numbers. Sorted resistors are first followed by capacitors. There should
                 be the same number of capacitors as there are resistors

        depth - How many other sections are above this one

    Output:
        List of strings which detail part of the overall circuit
    """

    # Creates an object that creates sections
    builder = TemplateBuilder(values, depth)

    # Returns what the object builds
    return builder.build_section()


def linear_interpolate(x1, y1, x2, y2):

    """  
    Calculates the gradient between points (x1, y1) and (x2, y2).
    Notably can't deal with perfectly vertical lines.

    Args: 
        x1, y1 - x and y coordinate of one point on the line
        x2, y2 - x and y coordinate of a differ point on the line

    Returns a list: [m, c] where m and c are from the equation y = mx + c
    """

    # Converts all the points to floats. Could be improved by using the fraction or decimal data type
    # The imprecision of floats was considered acceptable for the project    
    x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)

    # Finds the difference between the x and y values
    dx = x1 - x2
    dy = y1 - y2

    # Calculates the gradient
    m = dy / dx

    # Calculates the translation
    c = ((y2 * x1) - (y1 * x2)) / (x1 - x2)

    return m, c


def process_resistorValues(values):

    """  
    Takes a table of time against resistances and converts it into a series of line segment values

    Args:
        values - a list of lists where the first column is time and the rest are resistance values

    Returns the same list however instead of resistance values it has (m, c) tuples decribing the 
    line between consecutive values.
    """

    # List used to store the updated table
    update = []

    # Loops through each line of the list except the first one. This means all consecutive pairs are considered
    for i in range(1, len(values)):

        # First value on each line is the time so this is initialised.
        # line stores the data for the row.
        line = [values[i][0]]

        # Loops through all resistors.
        for j in range(1, len(values[0])):

            # Uses linear_interpolate to calculate the straight line segment between each pair of resistances
            line.append(linear_interpolate(values[i][0], values[i][j], values[i - 1][0], values[i - 1][j]))

        # Adds the new line to the table
        update.append(line)

    # Returns the updated table
    return update


def gen_resistor_strings(values, sections, layers):

    """  
    Takes a table of time against linear equations and returns nested if statement as a string.
    The if statment combines the equations to give an approximate function in time. 

    Args:
        values - a list of lists where the first column is time and the rest are m, c tuples from y = m*x + c
        sections - the number or resistors there are in each layer
        layers - number of layers in the model

    Returns a list of resistance functions for each resistor in each layer
    """

    # Stores width of the table to avoid multiple calls to len
    width = len(values[0]) - 1
    # Counts the number of brackets required
    bcount = 0

    # Stores string for each resistor.
    # Initialised with R = for LTSpice resistor value
    strings = ["R = " for _ in range(width)]
    times = ["" for _ in range(width)]


    for line in values:
        # Stores the current time as a float and adds 1 to the bracket count
        time = float(line[0])
        bcount += 1

        # Loops through each linear approximation and adds it to the nested if statements
        for index, val in enumerate(line[1:]):
            strings[index] += "".join(["If(time < ", str(time), ", ", str(val[0]), " * time + ", str(val[1]), ", "])

            # Stores latest end value
            times[index] = (time * val[0]) + val[1]

    # Adds constant at the end and adds all brackets required
    for i in range(width):
        strings[i] += str(times[i]) + ")" * bcount

    # Rearranges the table so it is the same format as the capacitor table
    reformat = [["" for x in range(sections)] for i in range(layers)]
    for index, value in enumerate(strings):
        reformat[index % layers][index // layers] = value

    # returns strings in reformated table
    return reformat


def setup(file):

    """  
    Extracts useful information from the setup file and returns a list of values

    Only to be used by this program and should never be imported elsewhere

    Args: None

    Returns a list containing:
        voltage string - a sting that defines the LTSpice voltage values
        parasitic resistance - resistance in series with the voltage source
        time start - time to start saving simulation data
        time stop - time to stop the simulation
        time step - the maximum amount of time LTSpice is allowed to to take between steps
        compression - the amount of data points LTSpice can combine into a single point
    """

    # Initialising the return list as order of values added may change 
    s = ["" for _ in range(6)]

    # Reads through lines of file and extracts data from specific lines
    with open(file, 'r') as inpt:
        for line in inpt:
            line = [x.strip() for x in line.split('=')]

            if line[0] == "voltage":
                v_type = [x.strip() for x in line[1].split(',')]

                if v_type[0] == "const":
                    s[0] = v_type[1]
                
                elif v_type[0] == "var":
                    s[0] = "PWL( " + v_type[1] + ")"

            elif line[0] == "parasitic resistance":
                s[1] = line[1]
            
            elif line[0] == "time start":
                s[2] = line[1]

            elif line[0] == "time stop":
                s[3] = line[1]
            
            elif line[0] == "time step":
                s[4] = line[1]

            elif line[0] == "compression":
                s[5] = line[1]

    # Sets default values for parasitic resistance and compression
    if s[1] == "":
        s[1] == "0"
    if s[5] == "":
        s[5] == "16"

    return s

# Only runs program if its called as a script
if __name__ == '__main__':
    flag = True
    # Checks for correct number of commandline arguments and prompts user if they arent given
    if len(argv) != 4:
        if len(argv) == 3:
            argv.append("config/generator_config.txt")
        
        else:
            flag = False
            print("Incorrect arguments.")
            print("Run program using: python complex_generator.py [input file name as one word] [output file name as one word] [Optional Setup file name as one word]")

    # Checks for the arguments having the correct file extensions
    if argv[1][-4:] != ".csv" or argv[2][-4:] != ".asc" or argv[3][-4:] != ".txt":
        flag = False
        print("Incorrect arguments. \nPlease make sure the specified files have the correct file extension\n\te.g. python complex_generator.py input.csv output.asc setup.txt")

    # Runs program only if tests have passed
    if flag:
        # Runs main function if the program is run as a script
        main(*argv[1:4])

    else: print(argv)