# PayPay Mobile SDK

PayPay Mobile API用のPython SDK（AWS CAPTCHA自動解決機能付き）

## 📦 インストール

```bash
pip install paypay-mobile
```

## 🚀 使い方

```python
from paypay_mobile import PayPay

# ログイン
paypay = PayPay("080-1234-5678", "password")
url = input("OAuth URL: ")
paypay.login(url)

# 残高確認
balance = paypay.get_balance()
print(f"残高: ¥{balance.all_balance:,}")

# 送金
result = paypay.send_money(amount=100, receiver_id="user_id")

# リンク作成
link = paypay.create_link(amount=500, passcode="1234")
```

## ✨ 機能

- ログイン（電話番号/パスワード、トークン）
- AWS CAPTCHA自動解決
- 送金リンク（作成/受取/拒否/キャンセル）
- P2P送金
- 残高・履歴確認
- チャット・メッセージ
- ユーザー検索
- QRコード生成・読取

## 📁 ファイル構成

```
paypay_minimal/
├── paypay_mobile/          # メインパッケージ
│   ├── __init__.py
│   ├── paypay.py          # PayPayクラス
│   ├── aws_solver.py      # CAPTCHA解決
│   ├── models.py          # データモデル
│   └── exceptions.py      # 例外
├── example.py             # サンプルコード
├── README.md              # 英語ドキュメント
├── README_JP.md           # 日本語ドキュメント（このファイル）
├── pyproject.toml         # パッケージ設定
└── LICENSE                # ライセンス
```

## 🔧 PyPIへの公開

```bash
# ビルド
pip install build twine
python -m build

# アップロード
python -m twine upload dist/*
```

## 📖 詳細ドキュメント

詳しい使い方は `README.md` と `example.py` を参照してください。

## ⚠️ 注意

- 非公式SDK（PayPay社の公式サポートなし）
- 利用規約を遵守してください
- 認証情報を安全に管理してください

## 📜 ライセンス

MIT License

## 🙏 謝辞

- [PayPaython-mobile](https://github.com/taka-4602/PayPaython-mobile)
- [paypaypy](https://github.com/suimin-1729/paypaypy)
