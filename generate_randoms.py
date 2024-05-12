import sys
import random

def generate_random_numbers(count, filename):
    with open(filename, 'w') as file:
        numbers = [str(random.randint(1, count)) for _ in range(count)]
        file.write('\n'.join(numbers))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <number_of_elements> <filename>")
    else:
        try:
            num_elements = int(sys.argv[1])
            file_name = sys.argv[2]
            generate_random_numbers(num_elements, file_name)
            print(f"Generated {num_elements} random numbers in {file_name}")
        except ValueError:
            print("Please ensure that the number of elements is an integer.")
