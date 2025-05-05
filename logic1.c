#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_STOCK 999

struct dados_produto {
    char nome[50];
    char descricao[500];
    float preco;
    int quantidade;
} stock[MAX_STOCK];

// salvar para o producto.txt
__declspec(dllexport)
void salvar_produto(const char* nome, float preco, int quantidade, const char* descricao) {
    FILE *f = fopen("produto.txt", "a");
    if (!f) {
        perror("Erro ao abrir o arquivo para escrita");
        return;
    }

    fprintf(f, "%s\n", nome);
    fprintf(f, "%.2f\n", preco);
    fprintf(f, "%d\n", quantidade);
    fprintf(f, "%s\n", descricao);
    fprintf(f, "---\n");

    fclose(f);
}

// ler do produto.txt
void inserirproduto() {
    FILE *f = fopen("produto.txt", "r");
    if (!f) {
        perror("Erro ao abrir o arquivo para leitura");
        return;
    }

    char line[128];
    int index = 0;

    while (fgets(line, sizeof(line), f) && index < MAX_STOCK) {
        line[strcspn(line, "\n")] = 0; 
        strcpy(stock[index].nome, line);

        if (!fgets(line, sizeof(line), f)) break;
        stock[index].preco = atof(line); // atof para float

        if (!fgets(line, sizeof(line), f)) break;
        stock[index].quantidade = atoi(line);

        if (!fgets(line, sizeof(line), f)) break;
        line[strcspn(line, "\n")] = 0;
        strcpy(stock[index].descricao, line);

        // Lê a linha de separação "---"
        if (!fgets(line, sizeof(line), f)) break;

        index++;
    }

    fclose(f);

    // printar os produtos lidos
    for (int i = 0; i < index; i++) {
        printf("Produto %d:\n", i + 1);
        printf("Nome: %s\nPreço: %.2f\nQuantidade: %d\nDescrição: %s\n\n",
               stock[i].nome, stock[i].preco, stock[i].quantidade, stock[i].descricao);
    }
}
