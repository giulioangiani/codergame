#include <bits/stdc++.h>

using namespace std;

struct node {
    int info;
    node* dx;
    node* sx;
};

// prototipi
int contanodi(node* p);
void inserisciPerfettamenteBilanciato(node* &p, int val);
void preorder(node* p);

using namespace std;

int main() {
	node* root = NULL;
	int N, X;
	cin >> N;
	for (int i=0; i<N; i++) {
		cin >> X;
        inserisciPerfettamenteBilanciato(root, X);
    }
    preorder(root); cout << endl;

    return 0;
}


// funzione per inserimento calcolo della profondità di un albero binario
int contanodi(node* p) {
    if (p==NULL) return 0;
    else return 1+contanodi(p->sx)+contanodi(p->dx);
}


void inserisciPerfettamenteBilanciato(node* &p, int val) {

    if (p == NULL) {
        p = new node();
        p->info = val;
        p->dx = p->sx = NULL;
    }
    else {
        if (contanodi(p->dx) >= contanodi(p->sx)) {
            // inserisco a sinistra
            inserisciPerfettamenteBilanciato(p->sx, val);
        }
        else {
            // inserisco a destra
            inserisciPerfettamenteBilanciato(p->dx, val);
        }
    }
}

void preorder(node* p) {
    if (p) {
        cout << p->info << " ";
        preorder(p->sx);
        preorder(p->dx);
    }
}

