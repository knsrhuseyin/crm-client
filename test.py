def trier_pile(pile):
    """Trie une pile dans l'ordre croissant en utilisant une seule pile auxiliaire."""
    temp = []  # pile temporaire

    while pile:
        # Retirer le sommet de la pile principale
        x = pile.pop()

        # Déplacer les éléments plus grands de temp vers pile
        while temp and temp[-1] > x:
            pile.append(temp.pop())

        # Placer x dans la pile temporaire à la bonne position
        temp.append(x)

    # Remettre les éléments triés dans la pile principale
    while temp:
        pile.append(temp.pop())

    return pile


# Exemple d'utilisation
pile = [34, 3, 31, 98, 92, 23]  # Le sommet de la pile est à la fin (23)
print("Pile avant tri :", pile)

pile_triee = trier_pile(pile)
print("Pile après tri :", pile_triee)