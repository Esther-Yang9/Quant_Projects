import time

# Open the file in write mode
with open("output.txt", "w") as file:
    num = 0
    
    # Run the loop until num reaches 1000
    while num <= 5:
        data = 'Run the script'
        # Write the current value of num to the file
        file.write(data + "\n")
        
        # Increment num by 1
        num += 1
        
        # Wait for 10 seconds
        time.sleep(3)