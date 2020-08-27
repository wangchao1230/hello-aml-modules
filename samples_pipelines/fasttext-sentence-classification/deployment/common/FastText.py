import torch
import torch.nn as nn
import torch.nn.functional as F


class FastText(nn.Module):
    def __init__(self, vocab_size, class_num, dropout=0.5, embed_dim=300, hidden_size=256, ngram_size=200000):
        super(FastText, self).__init__()

        self.embedding = nn.Embedding(num_embeddings=vocab_size, embedding_dim=embed_dim, padding_idx=0)
        self.embedding_bigram = nn.Embedding(num_embeddings=ngram_size, embedding_dim=embed_dim)
        self.embedding_trigram = nn.Embedding(num_embeddings=ngram_size, embedding_dim=embed_dim)
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(embed_dim * 3, hidden_size)
        self.fc2 = nn.Linear(hidden_size, class_num)

    def forward(self, x):
        word_feature = self.embedding(x[0])
        bigram_feature = self.embedding_bigram(x[1])
        trigram_feature = self.embedding_trigram(x[2])
        x = torch.cat((word_feature, bigram_feature, trigram_feature), -1)
        x = x.mean(dim=1)
        x = self.dropout(x)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        return x
