#!/usr/bin/env python3
"""
extract_table_from_pdf.py

Illustration of how to take character‐level PDFMiner output and group it
into rows and columns, then save as CSV or Excel.

Usage:
    python3 extract_table_from_pdf.py input.pdf output.xlsx

Dependencies: pdfminer.six, pandas, openpyxl
    pip install pdfminer.six pandas openpyxl
"""

import sys
import os
from typing import List, Dict, Any, Tuple
import pandas as pd

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTChar, LTAnno

# -----------------------------------------------------------------------------------
def extract_chars(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Return a list of dicts, one per LTChar, containing page, char, x0, y0, x1, y1.
    """
    records: List[Dict[str, Any]] = []

    with open(pdf_path, "rb") as fp:
        parser = PDFParser(fp)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page_number, page in enumerate(PDFPage.create_pages(doc), start=1):
            interpreter.process_page(page)
            layout = device.get_result()

            def recurse(obj):
                if isinstance(obj, LTChar):
                    # record every non‐whitespace character
                    txt = obj.get_text()
                    if not txt.isspace():  # skip pure spaces/newlines
                        records.append({
                            "page": page_number,
                            "char": txt,
                            "x0": round(obj.x0, 3),
                            "y0": round(obj.y0, 3),
                            "x1": round(obj.x1, 3),
                            "y1": round(obj.y1, 3),
                        })
                else:
                    try:
                        for child in obj:
                            recurse(child)
                    except Exception:
                        pass

            for element in layout:
                recurse(element)

    return records


# -----------------------------------------------------------------------------------
def cluster_rows(chars: List[Dict[str, Any]], y_tolerance: float = 2.0) -> List[List[int]]:
    """
    Group all character‐indices (in the `chars` list) into “rows” based on y1.
    Returns a list of clusters; each cluster is a list of integer indices into `chars`.

    y_tolerance: any two characters whose y1 differ by <= this amount → same row.
    """
    # First, collect (index, y1) pairs and sort by y1 DESC (top of page first)
    indexed = [(i, c["y1"]) for i, c in enumerate(chars)]
    indexed.sort(key=lambda x: x[1], reverse=True)

    row_clusters: List[List[int]] = []
    for idx, y1 in indexed:
        placed = False
        # Try to put this character into an existing row cluster
        for cluster in row_clusters:
            # `cluster` is a list of indices; check the y1 of the first char in that cluster
            first_idx = cluster[0]
            if abs(chars[first_idx]["y1"] - y1) <= y_tolerance:
                cluster.append(idx)
                placed = True
                break
        if not placed:
            row_clusters.append([idx])

    # Now each cluster is a “row” of character‐indices; we can return them
    return row_clusters


# -----------------------------------------------------------------------------------
def cluster_columns_for_row(
    chars: List[Dict[str, Any]],
    row_indices: List[int],
    x_tolerance: float = 2.0
) -> List[List[int]]:
    """
    Given a list of indices (all on the same row), group them into columns.
    We sort by x0 and say: “If the next character’s x0 is more than x_tolerance away
    from the previous cluster’s right‐edge, start a new column.”

    Returns: a list of clusters (one cluster = list of indices belonging to that column).
    """
    # Build a list of (idx, x0, x1), sorted by x0 ascending
    slice_info: List[Tuple[int, float, float]] = []
    for i in row_indices:
        slice_info.append((i, chars[i]["x0"], chars[i]["x1"]))
    slice_info.sort(key=lambda x: x[1])  # sort by x0

    col_clusters: List[List[int]] = []
    for idx, x0, x1 in slice_info:
        if not col_clusters:
            col_clusters.append([idx])
        else:
            # Look at the rightmost x1 of the last cluster
            last_cluster = col_clusters[-1]
            rightmost = max(chars[j]["x1"] for j in last_cluster)
            if x0 - rightmost <= x_tolerance:
                # This char overlaps (or is very close) with previous cluster horizontally
                last_cluster.append(idx)
            else:
                # Far enough that we treat it as a new column
                col_clusters.append([idx])

    return col_clusters


# -----------------------------------------------------------------------------------
def rows_and_columns_from_chars(
    chars: List[Dict[str, Any]]
) -> List[List[str]]:
    """
    Given all character records on a single page, return a 2D list:
        [ [cell1_row1, cell2_row1, ...],
          [cell1_row2, cell2_row2, ...],
          ... ]

    Steps:
      1) cluster_rows → list of “rows” (each row is a list of character‐indices)
      2) for each row, cluster_columns_for_row → list of “columns” (each a list of indices)
      3) within each column, sort indices by x0, concatenate chars in that order
    """
    table_rows: List[List[str]] = []

    # Cluster characters into rows (by y1)
    row_clusters = cluster_rows(chars)

    for row_idx_list in row_clusters:
        # For each row, cluster into columns
        col_clusters = cluster_columns_for_row(chars, row_idx_list)

        # Now build a list-of-strings for each column in that row
        row_cells: List[str] = []
        for col in col_clusters:
            # Sort all char‐indices in this column by x0 so they read left→right
            sorted_col = sorted(col, key=lambda i: chars[i]["x0"])
            cell_text = "".join(chars[i]["char"] for i in sorted_col)
            row_cells.append(cell_text.strip())

        table_rows.append(row_cells)

    return table_rows


# -----------------------------------------------------------------------------------
def convert_pdf_to_table_dataframe(pdf_path: str) -> pd.DataFrame:
    """
    Extract all chars, group into rows/columns, then return a DataFrame.
    Each row of the DataFrame is one “table row,” with columns named “col_1, col_2, ...”.
    """
    chars = extract_chars(pdf_path)
    if not chars:
        return pd.DataFrame()

    # Process page by page. Here we do everything in one DF with a 'page' column.
    # You could also split by page if needed.
    df_list: List[pd.DataFrame] = []
    for page_number in sorted({c["page"] for c in chars}):
        page_chars = [c for c in chars if c["page"] == page_number]

        # Group into rows & columns
        table_rows = rows_and_columns_from_chars(page_chars)

        # Build a DataFrame; pad shorter rows so the table is rectangular
        max_cols = max(len(r) for r in table_rows) if table_rows else 0
        normalized = [row + [""]*(max_cols - len(row)) for row in table_rows]

        page_df = pd.DataFrame(normalized, columns=[f"col_{i+1}" for i in range(max_cols)])
        page_df.insert(0, "page", page_number)
        df_list.append(page_df)

    # Concatenate all pages’ tables
    result_df = pd.concat(df_list, ignore_index=True)
    return result_df


# -----------------------------------------------------------------------------------
def pdf_to_excel(input_pdf):
    input_pdf = file
    ext = input_pdf.split('.')[-1]
    output_xlsx = f"{input_pdf[:-len(ext)]}.xlsx"
    if not os.path.isfile(input_pdf):
        print(f"ERROR: PDF not found: {input_pdf}")
        sys.exit(1)
    table_df = convert_pdf_to_table_dataframe(input_pdf)
    return table_df


