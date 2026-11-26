"""Tạo đặc trưng cho bài toán dự đoán tương tác thuốc (DDI) từ SMILES đã chuẩn hóa.

Dùng chung cho notebooks/02_HuanLuyen_DanhGia.ipynb và notebooks/03_ToiUu_CaiTien.ipynb.

Ba cách biểu diễn một cặp thuốc (A, B):
  - "concat": [Morgan(A) ‖ MACCS(A) ‖ Morgan(B) ‖ MACCS(B)]  – 2.382 bit (cách gốc ở Bài kiểm tra 1)
  - "sum":    FP(A) + FP(B), mỗi phần tử ∈ {0, 1, 2}           – 1.191 chiều, không phụ thuộc thứ tự A/B
  - "sum_plus": "sum" trên Morgan dạng đếm + MACCS, kèm 9 đặc trưng hóa lý (tổng và |hiệu|)

Không dùng mã thuốc hay bậc (số tương tác) làm đặc trưng để tránh rò rỉ nhãn.
"""
import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import MACCSkeys, rdFingerprintGenerator

RDLogger.DisableLog("rdApp.*")
N_MORGAN, N_MACCS = 1024, 167
PHYSCHEM = ["mol_wt", "logp", "tpsa", "hbd", "hba", "rot_bonds", "rings", "arom_rings", "heavy_atoms"]


def load_data(proc_dir="../data/processed"):
    """Đọc bảng thuốc đã làm sạch và 100.000 cặp (nhãn, tập train/test, nhóm thuốc mới)."""
    drugs = pd.read_csv(f"{proc_dir}/drugs_clean.csv")
    pairs = pd.read_csv(f"{proc_dir}/dataset_pairs.csv.gz")
    return drugs, pairs


def fingerprints(drugs, radius=2, n_bits=N_MORGAN):
    """Trả về dict mã thuốc -> (Morgan nhị phân, Morgan đếm, MACCS) dạng numpy."""
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    fp_bin, fp_cnt, fp_maccs = {}, {}, {}
    for r in drugs.itertuples():
        m = Chem.MolFromSmiles(r.smiles_std)
        fp_bin[r.drugbank_id] = gen.GetFingerprintAsNumPy(m).astype(np.uint8)
        fp_cnt[r.drugbank_id] = np.minimum(gen.GetCountFingerprintAsNumPy(m), 255).astype(np.uint8)
        v = np.zeros(N_MACCS, np.uint8)
        v[list(MACCSkeys.GenMACCSKeys(m).GetOnBits())] = 1
        fp_maccs[r.drugbank_id] = v
    return fp_bin, fp_cnt, fp_maccs


def build_pairs(pairs, drugs, fps, kind="concat"):
    """Tạo ma trận đặc trưng cho các cặp theo cách biểu diễn `kind`."""
    fp_bin, fp_cnt, fp_maccs = fps
    d1, d2 = pairs.drug1.values, pairs.drug2.values
    if kind in ("concat", "sum"):
        A = np.hstack([np.stack([fp_bin[i] for i in d1]), np.stack([fp_maccs[i] for i in d1])])
        B = np.hstack([np.stack([fp_bin[i] for i in d2]), np.stack([fp_maccs[i] for i in d2])])
        if kind == "concat":
            return np.hstack([A, B])
        return (A + B).astype(np.uint8)
    if kind == "sum_plus":
        A = np.hstack([np.stack([fp_cnt[i] for i in d1]), np.stack([fp_maccs[i] for i in d1])]).astype(np.float32)
        B = np.hstack([np.stack([fp_cnt[i] for i in d2]), np.stack([fp_maccs[i] for i in d2])]).astype(np.float32)
        P = drugs.set_index("drugbank_id")[PHYSCHEM]
        pa, pb = P.loc[d1].values.astype(np.float32), P.loc[d2].values.astype(np.float32)
        return np.hstack([A + B, pa + pb, np.abs(pa - pb)])
    raise ValueError(kind)


def feature_names(kind="concat"):
    base = [f"morgan_{i}" for i in range(N_MORGAN)] + [f"maccs_{i}" for i in range(N_MACCS)]
    if kind == "concat":
        return [f"A_{n}" for n in base] + [f"B_{n}" for n in base]
    if kind == "sum":
        return [f"sum_{n}" for n in base]
    if kind == "sum_plus":
        return ([f"sum_{n}" for n in base] + [f"sum_{p}" for p in PHYSCHEM] + [f"absdiff_{p}" for p in PHYSCHEM])
    raise ValueError(kind)


def to_float32(X):
    """Ép kiểu về float32 (dùng trong Pipeline qua FunctionTransformer) để tiết kiệm bộ nhớ."""
    return np.asarray(X, dtype=np.float32)


def maccs_description(key):
    """Mẫu SMARTS (và số lần xuất hiện tối thiểu) của khóa MACCS `key` theo RDKit."""
    smarts, count = MACCSkeys.smartsPatts.get(key, ("?", 0))
    return smarts if count == 0 else f"{smarts} (>{count} lần)"


def morgan_bit_fragments(drugs, bits, radius=2, n_bits=N_MORGAN):
    """Với mỗi bit Morgan, tìm mảnh cấu trúc (SMILES) hay gặp nhất làm bật bit đó."""
    from collections import Counter
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    found = {b: Counter() for b in bits}
    for smi in drugs.smiles_std:
        m = Chem.MolFromSmiles(smi)
        ao = rdFingerprintGenerator.AdditionalOutput(); ao.AllocateBitInfoMap()
        gen.GetFingerprint(m, additionalOutput=ao)
        info = ao.GetBitInfoMap()
        for b in bits:
            for atom, rad in info.get(b, ())[:1]:
                if rad == 0:
                    frag = m.GetAtomWithIdx(atom).GetSymbol() + (" (thơm)" if m.GetAtomWithIdx(atom).GetIsAromatic() else "")
                else:
                    env = Chem.FindAtomEnvironmentOfRadiusN(m, rad, atom)
                    frag = Chem.MolToSmiles(Chem.PathToSubmol(m, env), canonical=True) if env else "?"
                found[b][frag] += 1
    return {b: (c.most_common(1)[0][0] if c else "?") for b, c in found.items()}


def cached(path, fn):
    """Trả kết quả đã lưu ở `path` nếu có; nếu chưa có thì chạy `fn()` rồi lưu lại.

    Giúp chạy lại notebook nhanh (các bước tốn thời gian chỉ chạy một lần).
    Xóa thư mục results/cache/ để chạy lại toàn bộ từ đầu.
    """
    import os, joblib
    if os.path.exists(path):
        return joblib.load(path)
    obj = fn()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(obj, path)
    return obj
