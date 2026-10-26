"""
Trích xuất bảng thuốc và danh sách cặp tương tác từ file DrugBank `full database.xml`.

Cách dùng:
    python src/extract_drugbank.py "duong/dan/full database.xml" data/raw

Đầu ra (trong thư mục data/raw):
    drugs.csv          - mỗi dòng 1 thuốc: drugbank_id, name, type, groups, smiles,
                         inchikey, mol_weight, n_interactions
    ddi_pairs.csv.gz   - mỗi dòng 1 cặp tương tác duy nhất (drug1 < drug2)
    meta.txt           - phiên bản DrugBank, ngày xuất, thống kê

Ghi chú:
- File XML ~1,6 GB nên được đọc theo kiểu streaming (lxml.iterparse): xử lý xong
  thẻ <drug> nào thì giải phóng bộ nhớ của thẻ đó.
- Thẻ <drug> còn xuất hiện lồng bên trong (ví dụ trong <pathways>), nên chỉ xử lý
  thẻ <drug> cấp 1 (con trực tiếp của <drugbank>).
- Mỗi tương tác được DrugBank ghi ở cả hai thuốc (A->B và B->A); ở đây gộp lại
  thành một cặp không thứ tự (A, B) với A < B.
"""
import csv
import gzip
import os
import sys
import time

from lxml import etree

NS = "{http://www.drugbank.ca}"


def main(src: str, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    drugs, pairs = [], set()
    n_entries, depth, meta = 0, 0, None

    for event, el in etree.iterparse(src, events=("start", "end"), tag=f"{NS}drug", huge_tree=True):
        if event == "start":
            depth += 1
            if meta is None:
                root = el.getparent()
                meta = (root.get("version"), root.get("exported-on"))
            continue
        depth -= 1
        if depth != 0:  # thẻ <drug> lồng bên trong -> bỏ qua
            continue

        pid = el.findtext(f"{NS}drugbank-id[@primary='true']")
        name = el.findtext(f"{NS}name")
        groups = [g.text for g in el.findall(f"{NS}groups/{NS}group")]
        props = {}
        for p in el.findall(f"{NS}calculated-properties/{NS}property"):
            props[p.findtext(f"{NS}kind")] = p.findtext(f"{NS}value") or ""
        partners = [i.findtext(f"{NS}drugbank-id")
                    for i in el.findall(f"{NS}drug-interactions/{NS}drug-interaction")]
        n_entries += len(partners)
        for other in partners:
            if other and other != pid:
                pairs.add((pid, other) if pid < other else (other, pid))
        drugs.append([pid, name, el.get("type"), ";".join(groups), props.get("SMILES", ""),
                      props.get("InChIKey", ""), props.get("Molecular Weight", ""), len(partners)])

        # giải phóng bộ nhớ của phần tử đã xử lý
        el.clear()
        while el.getprevious() is not None:
            del el.getparent()[0]
        if len(drugs) % 2000 == 0:
            print(f"{len(drugs)} thuốc, {len(pairs)} cặp, {time.time() - t0:.0f}s", flush=True)

    with open(os.path.join(out_dir, "drugs.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["drugbank_id", "name", "type", "groups", "smiles", "inchikey", "mol_weight", "n_interactions"])
        w.writerows(drugs)
    with gzip.open(os.path.join(out_dir, "ddi_pairs.csv.gz"), "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["drug1", "drug2"])
        w.writerows(sorted(pairs))
    with open(os.path.join(out_dir, "meta.txt"), "w") as f:
        f.write(f"version={meta[0]}\nexported_on={meta[1]}\ndrugs={len(drugs)}\n"
                f"interaction_entries={n_entries}\nunique_pairs={len(pairs)}\n")
    print(f"Xong: {len(drugs)} thuốc, {n_entries} bản ghi tương tác, {len(pairs)} cặp duy nhất "
          f"({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit('Cách dùng: python src/extract_drugbank.py "full database.xml" data/raw')
    main(sys.argv[1], sys.argv[2])
