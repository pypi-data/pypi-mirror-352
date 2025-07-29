# Fourier Sliced-Wasserstein (FSW) embedding — a PyTorch-based library

This package provides an implementation of the **Fourier Sliced-Wasserstein (FSW) embedding** for multisets and measures, introduced in our [ICLR 2025 paper](https://iclr.cc/virtual/2025/poster/30562):

> **Fourier Sliced-Wasserstein Embedding for Multisets and Measures**  
> Tal Amir, Nadav Dym  
> *International Conference on Learning Representations (ICLR), 2025*

---

## 🔧 Installation

To install the package:

```bash
pip install fswlib
```

This package includes an optional custom CUDA extension. When working with sparse weight matrices (e.g., sparse graphs), it can be approximately 2× faster than the pure-PyTorch version.  
To compile it, run:

```bash
fswlib-build
```

---

## 📘 Basic Usage Example

```python
import torch

from fswlib import FSWEmbedding

dtype=torch.float32
device = 'cuda' if torch.cuda.is_available() else 'cpu'

d = 15  # dimension of input multiset elements
n = 50  # multiset size
m = 123 # embedding output dimension

# If False, input multisets are treated as uniform distributions over their elements,
# making the embedding invariant to the multiset size.
encode_total_mass = True

# Generate an embedding module
embed = FSWEmbedding(d_in=d, d_out=m, encode_total_mass=encode_total_mass, device=device, dtype=dtype)

print(f"Dimension of multiset elements: {d}\nEmbedding dimension: {m}")

print(f'\nOne input multiset X of size {n}:')

# Generate a multiset
X = torch.randn(size=(n,d), dtype=dtype, device=device)
print('Shape of X: ', X.shape)

X_emb = embed(X)
print('Shape of embed(X): ', X_emb.shape)

# Supports any number of batch dimensions:
batch_dims = (5,3,4)
batch_dim_str = "×".join(str(d) for d in batch_dims)
print(f'\nA batch Xb of {batch_dim_str} input multisets, each is of size {n}: ')

# Generate a batch of multisets
Xb = torch.randn(size=batch_dims+(n,d), dtype=dtype, device=device)
print('Shape of Xb: ', Xb.shape)

Xb_emb = embed(Xb)
print('Shape of embed(Xb): ', Xb_emb.shape)
```

Output:
```
Dimension of multiset elements: 15
Embedding dimension: 123

One input multiset X of size 50:
Shape of X:  torch.Size([50, 15])
Shape of embed(X):  torch.Size([123])

A batch Xb of 5×3×4 input multisets, each is of size 50:
Shape of Xb:  torch.Size([5, 3, 4, 50, 15])
Shape of embed(Xb):  torch.Size([5, 3, 4, 123])
```

---

## 📄 Citation

If you use this library in your research, please cite our paper:

```bibtex
@inproceedings{amir2025fsw,
  title={Fourier Sliced-{W}asserstein Embedding for Multisets and Measures},
  author={Tal Amir and Nadav Dym},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2025}
}
```

---

## 🔗 Links

- **Paper**: [ICLR 2025](https://iclr.cc/virtual/2025/poster/30562)  
- **Code**: [GitHub repository](https://github.com/tal-amir/fswlib)

---

## 👨🏻‍🔧 Maintainer

This library is maintained by [**Tal Amir**](https://tal-amir.github.io)  
Contact: [talamir@technion.ac.il](mailto:talamir@technion.ac.il)

