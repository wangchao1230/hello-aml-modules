import torch
import torch.nn as nn
import torch.nn.functional as F


class FastText(nn.Module):
    def __init__(self, vocab_size, n_class, embed_dim=128, ):
        super(FastText, self).__init__()

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embed_dim,
        )
        self.fc = nn.Linear(in_features=embed_dim, out_features=n_class)

    def forward(self, x):
        x = self.embedding(x)  # [batch, seq_len, embed_dim]
        x = F.avg_pool2d(x, (x.shape[-2], 1))  # [batch, 1, embed_dim]
        x = x.squeeze()  # [batch, embed_dim]
        x = self.fc(x)  # [batch, n_class]
        x = torch.sigmoid(x)  # [batch, n_class]
        return x
