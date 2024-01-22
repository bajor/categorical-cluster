# TODO:
- create record id to assign at the end
- and result should be initial list with labels
- write it generic - you pass dataframe and columns to cluster on - I return dataframe with new column - label
    - but do it in a way: 1 convert dataframe to list of lists -> convert them
    - 2 methods, one - you pass a dataframe and columns, 2 - you pass list of lists

- first - prepare map as 1 step, then cluster as 2 step
- plot should not save to csv but to some variable
- plot and dataset should be optional, preferably in separate package. Maybe even just laying in the separete repo and link in readme to it.
- tests
- docstrings

# TODO big picture:

- enable multiprocessing, rewrite into maps:

```
    jesli nie bedzie innych pomysłów na zrównoleglenie tego to można na każdej iteracji robić map and reduce - czyli:
    dla każdego klastra porównujemy go do wszystkich innych klastrów - map
    następnie znowu map - patrzymy który z kolejnych klastrów jest najbardziej spójny - zostawiamy najbardziej spójne, jeśli mamy pary np. (1,3) o spójności 93% i parę (3,5) o spójności 50% - łączymy parę 1 i 3 razem tworząc nowy klaster a z elementem 5 nic nie robimy (zostawiamy na kolejną iterację).
```