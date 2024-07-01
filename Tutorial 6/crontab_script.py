import time

# Open the file in write mode
with open("output.txt", "w") as file:
    data = 'Run the script'
    # Write the current value of num to the file
    file.write(data + "\n")