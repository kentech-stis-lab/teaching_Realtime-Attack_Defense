#!/bin/bash
# CIC-IDS 2017/2018 데이터셋 다운로드 스크립트
#
# 사용법:
#   bash download_cicids.sh 2017    # CIC-IDS 2017 다운로드
#   bash download_cicids.sh 2018    # CSE-CIC-IDS 2018 다운로드

set -e

VERSION="${1:-2017}"
BASE_DIR="$(dirname "$0")/../data"

if [ "$VERSION" = "2017" ]; then
    TARGET_DIR="$BASE_DIR/cicids2017"
    mkdir -p "$TARGET_DIR"
    echo "[*] CIC-IDS 2017 다운로드 (Kaggle mirror 권장)"
    echo ""
    echo "방법 1) Kaggle CLI (추천):"
    echo "  pip install kaggle"
    echo "  kaggle datasets download -d dhoogla/cicids2017 -p $TARGET_DIR --unzip"
    echo ""
    echo "방법 2) HuggingFace:"
    echo "  https://huggingface.co/datasets/c01dsnap/CIC-IDS2017"
    echo ""
    echo "방법 3) 직접 다운로드:"
    echo "  http://205.174.165.80/CICDataset/CIC-IDS-2017/Dataset/MachineLearningCSV.zip"
    echo "  다운로드 후 $TARGET_DIR 에 압축 해제"
    echo ""
    echo "[*] 대상 디렉토리: $TARGET_DIR"

elif [ "$VERSION" = "2018" ]; then
    TARGET_DIR="$BASE_DIR/cicids2018"
    mkdir -p "$TARGET_DIR"
    echo "[*] CSE-CIC-IDS 2018 다운로드"
    echo ""
    echo "방법 1) AWS CLI (공식):"
    echo "  aws s3 sync --no-sign-request --region us-east-1 \\"
    echo "    \"s3://cse-cic-ids2018/Processed Traffic Data for ML Algorithms/\" \\"
    echo "    $TARGET_DIR"
    echo ""
    echo "방법 2) Kaggle:"
    echo "  kaggle datasets download -d solarmainframe/ids-intrusion-csv -p $TARGET_DIR --unzip"
    echo ""
    echo "[*] 대상 디렉토리: $TARGET_DIR"

else
    echo "[!] 사용법: bash download_cicids.sh [2017|2018]"
    exit 1
fi
