# AGENTS Guidelines

Setelah selesai menulis atau mengubah kode Python, **wajib** jalankan langkah berikut untuk file yang diubah (`[files]`) dengan urutan ini:

1. `uv run -m ruff format [files]`
2. `uv run -m ruff check --fix [files]`
3. `uv run -m basedpyright [files]`
4. `uv run -m pytest`

## Aturan

- `[files]` berarti daftar file Python yang baru ditulis/diubah pada task tersebut.
- Jangan lewati langkah mana pun.
- Jika ada error pada langkah mana pun, perbaiki lalu ulangi dari langkah 1 sampai 4.
