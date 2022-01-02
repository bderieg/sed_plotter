import galaxy

LINES_PER_DATA_SET = 7


# Converts a number of the form 6.00E+12 (for example) into an int data type
def scientific_to_normal(sci_form):
    final = ""
    after_decimal = 0
    hit_decimal = False
    hit_e = False
    num_zeros = ""
    c = 0

    # Get value before E marker
    while not hit_e:
        if (sci_form[c] != ".") and (sci_form[c] != "E"):
            final += sci_form[c]
            if hit_decimal:
                after_decimal += 1
        if sci_form[c] == ".":
            hit_decimal = True
        if sci_form[c] == "E":
            hit_e = True
            c += 1
        c += 1

    # Add 0s
    c -= 1
    while c < len(sci_form):
        num_zeros += sci_form[c]
        c += 1
    num_zeros = int(num_zeros)
    num_zeros -= after_decimal
    if num_zeros > 0:  # If power larger than 0
        for j in range(num_zeros):
            final += "0"
        final = int(final)
    else:  # If power smaller than 0
        j = 0
        final = float(final)
        while j > num_zeros:
            final /= 10
            j -= 1

    return final


# Puts data from the nth galaxy data set in a Galaxy class (returns Galaxy)
def get_set_n(n, curr_file):  # Assumes LINES_PER_DATA_SET (constant) lines of data per galaxy
    galaxy_name = ""
    frequency_list = []
    telescope_list = []
    flux_list = []
    unc_upper_list = []
    unc_lower_list = []
    curr_line = curr_file.readline()
    curr_str = ""
    i = 0  # counter
    w = 0  # counter to determine width

    # Find nth data set
    for j in range(n):
        for k in range(LINES_PER_DATA_SET + 1):
            curr_line = curr_file.readline()

    # Set constant MAX_WIDTH based on number of commas in this row
    curr_char = curr_line[i]
    MAX_WIDTH = len(curr_line) - 1

    # Iterate until galaxy name found
    while (curr_char == ",") or (curr_char == " ") or (curr_char == "\n") or (curr_char == ""):
        if i < len(curr_line):
            curr_char = curr_line[i]
            i += 1
        else:
            i = 0
            curr_line = curr_file.readline()
            curr_char = curr_line[i]
            i += 1

    # Get galaxy name
    i = 0
    while curr_char != ",":
        curr_char = curr_line[i]
        if curr_char != ",":
            galaxy_name += curr_char
        i += 1

    # Iterate until beginning of frequency list
    i += 1
    curr_char = curr_line[i]
    while curr_char != ",":
        curr_char = curr_line[i]
        i += 1

    # Populate frequency list
    curr_char = curr_line[i]
    while i < (len(curr_line) - (MAX_WIDTH - w)):
        while (curr_char != ",") and (curr_char != "") and (curr_char != "\n"):
            curr_char = curr_line[i]
            if (curr_char != ",") and (curr_char != "") and (curr_char != "\n"):
                curr_str += curr_char
            i += 1
        int_to_add = scientific_to_normal(curr_str)
        frequency_list.append(int_to_add)
        w += 1
        curr_str = ""
        if i < len(curr_line):
            curr_char = curr_line[i]
    curr_line = curr_file.readline()

    # Iterate until beginning of telescope list
    i = 1
    curr_char = curr_line[i]
    while curr_char != ",":
        curr_char = curr_line[i]
        i += 1

    # Populate telescope list
    curr_char = curr_line[i]
    while i < (len(curr_line) - (MAX_WIDTH - w)):
        while (curr_char != ",") and (curr_char != "") and (curr_char != "\n"):
            curr_char = curr_line[i]
            if (curr_char != ",") and (curr_char != "") and (curr_char != "\n"):
                curr_str += curr_char
            i += 1
        telescope_list.append(curr_str)
        curr_str = ""
        if i < len(curr_line):
            curr_char = curr_line[i]
    curr_line = curr_file.readline()

    # Iterate until beginning of flux list
    i = 1
    curr_char = curr_line[i]
    while curr_char != ",":
        curr_char = curr_line[i]
        i += 1

    # Populate flux list
    curr_char = curr_line[i]
    while i < (len(curr_line) - (MAX_WIDTH - w)):
        while (curr_char != ",") and (curr_char != "") and (curr_char != "\n"):
            curr_char = curr_line[i]
            if (curr_char != ",") and (curr_char != "") and (curr_char != "\n"):
                curr_str += curr_char
            i += 1
        flux_list.append(float(curr_str))
        curr_str = ""
        if i < len(curr_line):
            curr_char = curr_line[i]
    curr_line = curr_file.readline()

    # Iterate until beginning of upper uncertainty list
    i = 1
    curr_char = curr_line[i]
    while curr_char != ",":
        curr_char = curr_line[i]
        i += 1

    # Populate upper uncertainty list
    curr_char = curr_line[i]
    while i < (len(curr_line) - (MAX_WIDTH - w)):
        while (curr_char != ",") and (curr_char != "") and (curr_char != "\n"):
            curr_char = curr_line[i]
            if (curr_char != ",") and (curr_char != "") and (curr_char != "\n"):
                curr_str += curr_char
            i += 1
        if ('none' in curr_str) or ('None' in curr_str):
            unc_upper_list.append(0.0)
        elif 'E' in curr_str:
            to_add = scientific_to_normal(curr_str)
            unc_upper_list.append(to_add)
        else:
            unc_upper_list.append(float(curr_str))
        curr_str = ""
        if i < len(curr_line):
            curr_char = curr_line[i]
    curr_line = curr_file.readline()

    # Iterate until beginning of lower uncertainty list
    i = 1
    curr_char = curr_line[i]
    while curr_char != ",":
        curr_char = curr_line[i]
        i += 1

    # Populate lower uncertainty list
    curr_char = curr_line[i]
    while i < (len(curr_line) - (MAX_WIDTH - w)):
        while (curr_char != ",") and (curr_char != "") and (curr_char != "\n"):
            curr_char = curr_line[i]
            if (curr_char != ",") and (curr_char != "") and (curr_char != "\n"):
                curr_str += curr_char
            i += 1
        if ('none' in curr_str) or ('None' in curr_str):
            unc_lower_list.append(0.0)
        elif 'E' in curr_str:
            to_add = scientific_to_normal(curr_str)
            unc_lower_list.append(to_add)
        else:
            unc_lower_list.append(float(curr_str))
        curr_str = ""
        if i < len(curr_line):
            curr_char = curr_line[i]
    curr_line = curr_file.readline()

    # Get redshift
    i = 1
    curr_char = curr_line[i]
    while curr_char != ",":
        curr_char = curr_line[i]
        i += 1
    curr_char = curr_line[i]
    curr_str = ""
    while curr_char != ",":
        curr_str += curr_char
        i += 1
        curr_char = curr_line[i]
    if 'E' in curr_str:
        z = scientific_to_normal(curr_str)
    else:
        z = float(curr_str)
    curr_line = curr_file.readline()

    # Get distance
    i = 1
    curr_char = curr_line[i]
    while curr_char != ",":
        curr_char = curr_line[i]
        i += 1
    curr_char = curr_line[i]
    curr_str = ""
    while curr_char != ",":
        curr_str += curr_char
        i += 1
        curr_char = curr_line[i]
    if 'E' in curr_str:
        distance = scientific_to_normal(curr_str)
    else:
        distance = float(curr_str)

    # Create galaxy and return it
    g = galaxy.Galaxy(galaxy_name, frequency_list, telescope_list, flux_list,
                      unc_upper_list, unc_lower_list, z, distance)
    return g
