import pickle


filename = "output.p"

with open(filename, "rb") as file:
    data = pickle.load(file)

for d in data[4]:
    print(d)
