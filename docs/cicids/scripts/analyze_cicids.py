"""
CIC-IDS 2017 / 2018 데이터셋 로드 및 공격 유형 분류 스크립트

사용법:
    python analyze_cicids.py --data_dir ./data/cicids2017
    python analyze_cicids.py --data_dir ./data/cicids2018 --version 2018
"""

import argparse
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ──────────────────────────────────────────────
# 1. 데이터셋 버전별 설정
# ──────────────────────────────────────────────

CONFIG = {
    "2017": {
        "label_col": "Label",
        "encoding": "utf-8",
        # Web Attack 라벨에 en-dash(\u2013) 사용 — 인코딩 깨질 수 있음
        "web_attack_labels": {
            "Web Attack \u2013 Brute Force": "Web Attack - Brute Force",
            "Web Attack \u2013 XSS": "Web Attack - XSS",
            "Web Attack \u2013 Sql Injection": "Web Attack - SQL Injection",
            # fallback: 이미 정리된 라벨
            "Web Attack - Brute Force": "Web Attack - Brute Force",
            "Web Attack - XSS": "Web Attack - XSS",
            "Web Attack - Sql Injection": "Web Attack - SQL Injection",
        },
        "benign_label": "BENIGN",
        "category_map": {
            "BENIGN": "Benign",
            "FTP-Patator": "Brute Force",
            "SSH-Patator": "Brute Force",
            "DoS slowloris": "DoS",
            "DoS Slowhttptest": "DoS",
            "DoS Hulk": "DoS",
            "DoS GoldenEye": "DoS",
            "Heartbleed": "DoS",
            "Web Attack - Brute Force": "Web Attack",
            "Web Attack - XSS": "Web Attack",
            "Web Attack - SQL Injection": "Web Attack",
            "Infiltration": "Infiltration",
            "Bot": "Bot",
            "PortScan": "PortScan",
            "DDoS": "DDoS",
        },
        # 수업 실습 대상 (Juice Shop 재현 가능)
        "lab_targets": [
            "Web Attack - Brute Force",
            "Web Attack - XSS",
            "Web Attack - SQL Injection",
        ],
    },
    "2018": {
        "label_col": "Label",
        "encoding": "utf-8",
        "web_attack_labels": {},  # 2018은 깨지지 않음
        "benign_label": "Benign",
        "category_map": {
            "Benign": "Benign",
            "FTP-BruteForce": "Brute Force",
            "SSH-Bruteforce": "Brute Force",
            "DoS attacks-Hulk": "DoS",
            "DoS attacks-GoldenEye": "DoS",
            "DoS attacks-Slowloris": "DoS",
            "DoS attacks-SlowHTTPTest": "DoS",
            "DDoS attacks-LOIC-HTTP": "DDoS",
            "DDoS attack-LOIC-UDP": "DDoS",
            "DDoS attack-HOIC": "DDoS",
            "Brute Force -Web": "Web Attack",
            "Brute Force -XSS": "Web Attack",
            "SQL Injection": "Web Attack",
            "Infilteration": "Infiltration",
            "Bot": "Bot",
        },
        "lab_targets": [
            "Brute Force -Web",
            "Brute Force -XSS",
            "SQL Injection",
        ],
    },
}


# ──────────────────────────────────────────────
# 2. 데이터 로드
# ──────────────────────────────────────────────

def load_csvs(data_dir: str, version: str) -> pd.DataFrame:
    """디렉토리 내 모든 CSV를 읽어 하나의 DataFrame으로 합침."""
    cfg = CONFIG[version]
    csv_files = sorted(Path(data_dir).glob("*.csv"))

    if not csv_files:
        print(f"[!] '{data_dir}'에 CSV 파일이 없습니다.")
        sys.exit(1)

    frames = []
    for f in csv_files:
        print(f"  Loading {f.name} ...", end=" ")
        df = pd.read_csv(f, skipinitialspace=True, low_memory=False,
                         encoding=cfg["encoding"], on_bad_lines="skip")
        df.columns = df.columns.str.strip()
        print(f"({len(df):,} rows)")
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)

    # inf → NaN 처리
    combined.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Web Attack 라벨 정규화 (2017 en-dash / replacement char 문제)
    # U+FFFD(\xef\xbf\xbd), en-dash(\u2013), 기타 깨진 문자를 모두 하이픈으로 치환
    combined[cfg["label_col"]] = combined[cfg["label_col"]].apply(
        lambda x: re.sub(r'Web Attack\s*[^\w\s]+\s*', 'Web Attack - ',
                         str(x).strip()) if 'Web Attack' in str(x) else str(x).strip()
    )
    if cfg["web_attack_labels"]:
        combined[cfg["label_col"]] = combined[cfg["label_col"]].replace(
            cfg["web_attack_labels"]
        )

    # 공백 제거
    combined[cfg["label_col"]] = combined[cfg["label_col"]].str.strip()

    return combined


# ──────────────────────────────────────────────
# 3. 분석 함수
# ──────────────────────────────────────────────

def summarize_labels(df: pd.DataFrame, version: str) -> pd.DataFrame:
    """라벨별 건수 + 비율 + 상위 카테고리 매핑."""
    cfg = CONFIG[version]
    label_col = cfg["label_col"]

    counts = df[label_col].value_counts().reset_index()
    counts.columns = ["Label", "Count"]
    counts["Ratio(%)"] = (counts["Count"] / counts["Count"].sum() * 100).round(3)
    counts["Category"] = counts["Label"].map(cfg["category_map"]).fillna("Unknown")
    counts["Lab_Target"] = counts["Label"].isin(cfg["lab_targets"])

    return counts


def extract_web_attacks(df: pd.DataFrame, version: str) -> pd.DataFrame:
    """수업 실습 대상 (Web Attack) 레코드만 추출."""
    cfg = CONFIG[version]
    label_col = cfg["label_col"]
    mask = df[label_col].isin(cfg["lab_targets"])
    return df[mask].copy()


def describe_web_attacks(web_df: pd.DataFrame, version: str):
    """Web Attack 레코드의 주요 feature 통계."""
    cfg = CONFIG[version]
    label_col = cfg["label_col"]

    # 2017/2018 공통으로 존재하는 주요 feature
    key_features_2017 = [
        "Destination Port", "Flow Duration",
        "Total Fwd Packets", "Total Backward Packets",
        "Flow Bytes/s", "Flow Packets/s",
        "Fwd Packet Length Mean", "Bwd Packet Length Mean",
    ]
    key_features_2018 = [
        "Dst Port", "Flow Duration",
        "Tot Fwd Pkts", "Tot Bwd Pkts",
        "Flow Byts/s", "Flow Pkts/s",
        "Fwd Pkt Len Mean", "Bwd Pkt Len Mean",
    ]

    features = key_features_2017 if version == "2017" else key_features_2018
    available = [f for f in features if f in web_df.columns]

    if not available:
        print("[!] 주요 feature 컬럼을 찾을 수 없습니다.")
        print(f"    사용 가능한 컬럼: {list(web_df.columns[:10])} ...")
        return None

    stats = web_df.groupby(label_col)[available].describe()
    return stats


# ──────────────────────────────────────────────
# 4. 출력
# ──────────────────────────────────────────────

def print_section(title: str):
    width = 60
    print(f"\n{'='*width}")
    print(f"  {title}")
    print(f"{'='*width}")


def main():
    parser = argparse.ArgumentParser(
        description="CIC-IDS 2017/2018 데이터셋 공격 유형 분류 스크립트"
    )
    parser.add_argument("--data_dir", required=True, help="CSV 파일이 있는 디렉토리")
    parser.add_argument("--version", choices=["2017", "2018"], default="2017",
                        help="데이터셋 버전 (default: 2017)")
    parser.add_argument("--export", default=None,
                        help="Web Attack 레코드를 CSV로 내보낼 경로 (선택)")
    args = parser.parse_args()

    # ── 로드 ──
    print_section(f"CIC-IDS {args.version} 데이터 로드")
    df = load_csvs(args.data_dir, args.version)
    print(f"\n  전체 레코드 수: {len(df):,}")

    # ── 전체 라벨 분포 ──
    print_section("전체 공격 유형 분포")
    summary = summarize_labels(df, args.version)
    print(summary.to_string(index=False))

    # ── 카테고리별 요약 ──
    print_section("카테고리별 요약")
    cat_summary = summary.groupby("Category").agg(
        Count=("Count", "sum"),
    ).sort_values("Count", ascending=False)
    cat_summary["Ratio(%)"] = (cat_summary["Count"] / cat_summary["Count"].sum() * 100).round(2)
    print(cat_summary.to_string())

    # ── Web Attack 상세 ──
    print_section("수업 실습 대상: Web Attack 상세")
    web_df = extract_web_attacks(df, args.version)
    print(f"  Web Attack 레코드 수: {len(web_df):,}")

    if len(web_df) > 0:
        label_col = CONFIG[args.version]["label_col"]
        print(f"\n  유형별 분포:")
        print(web_df[label_col].value_counts().to_string())

        print_section("Web Attack 주요 Feature 통계")
        cfg = CONFIG[args.version]
        key_features_2017 = [
            "Destination Port", "Flow Duration",
            "Total Fwd Packets", "Total Backward Packets",
            "Flow Bytes/s", "Flow Packets/s",
        ]
        key_features_2018 = [
            "Dst Port", "Flow Duration",
            "Tot Fwd Pkts", "Tot Bwd Pkts",
            "Flow Byts/s", "Flow Pkts/s",
        ]
        features = key_features_2017 if args.version == "2017" else key_features_2018
        available = [f for f in features if f in web_df.columns]

        for label in web_df[label_col].unique():
            print(f"\n  [{label}]")
            subset = web_df[web_df[label_col] == label]
            for feat in available:
                col = pd.to_numeric(subset[feat], errors="coerce").dropna()
                if len(col) > 0:
                    print(f"    {feat}: mean={col.mean():.2f}, std={col.std():.2f}, "
                          f"min={col.min():.2f}, max={col.max():.2f}")

    # ── 내보내기 ──
    if args.export and len(web_df) > 0:
        web_df.to_csv(args.export, index=False)
        print(f"\n  [+] Web Attack 레코드 저장: {args.export}")

    print(f"\n{'='*60}")
    print("  완료!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
