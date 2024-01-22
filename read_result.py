import pickle


filename = "output.p"

with open(filename, 'rb') as file:
    data = pickle.load(file)

print(data[1])