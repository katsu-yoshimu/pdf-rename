# pdf-rename

## インストール方法

```cmd
cd %適当なディレクトリ%
git clone https://github.com/katsu-yoshimu/pdf-rename.git
cd pdf-rename
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

※前提※ Windows PC に python 3 インストール済

## サンプルのディレクトリ、ファイル構成

```text:dir
　pdf-rename
　 +- sample.py
　 +- requirements.txt
  input
　 +- elogi_invoice_first_payment-29.pdf  ← ご提供いただいたPDF
　 +- memo.txt                            ← 適当なテキストファイル（PDF解析エラーの確認用）
```

PDFは機密事項のため「input」ディレクトリはご自分で準備ください。

## 実行方法

```cmd
cd %適当なディレクトリ%
cd pdf-rename
python sample.py
```

## 実行結果

```text
請求元は「mipick CO., LTD.」です。編集後は「mipickCO.,LTD.」です
日付は「11/13/2024」です。編集後は「20241113」です
金額は「¥12,550」です。編集後は「12550」です
   page                    text       x0       y0          x1          y1       width     height
0     1                 初回請求領収書   51.591  741.（機密事項のため、以下、省略）
```

※PDFファイルのリネームはなし。PDFファイルからテキスト抽出と編集のみ実施

## 補足

- extractTextFromPDFFile クラスを継承して、パターンごとにextractTextFromPDFFile_elogcクラスの請求元、日付、金額の抽出、編集メソッドを編集して、対応できるように考慮しています。

- 編集メソッドは仮実装です。請求元は全てのスペースを削除しています（スペースの削除要否は未確認）。日付、金額は編集不可の場合の実装はしていません。

- 新しいパターンのPDFファイルを「p=extractTextFromPDFFile(PDFファイルパス)」で解析後に「p.df」の内容を確認して、抽出すべきテキストの座標、見出しラベルを確認して、新しいパターン用のクラスを実装するとよいです。

## イメージ：クラス継承して差分で実装する

```python:クラス継承のイメージ
class 親クラス():
    def 全テキスト抽出():
        text = self.日付テキスト抽出(座標など)
        text = self.日付テキスト編集(text)
        print(f'日付は「{text}」です。編集後は「{日付テキスト編集(text)}」です') ← これを項目数分繰り返す

    def 日付テキスト抽出(座標など):
        return テキスト

    def 日付テキスト編集(text):
        return テキスト

class 子クラス(親クラス):
    def 日付テキスト編集(text):
        textを/で分割
            [0]:1-12のはず。頭0の2桁数値の文字列に変換
            [1]:1-31のはず。頭0の2桁数値の文字列に変換
            [2]:西暦4桁数値はず。そのまま4桁数値の文字列に変換
        日付テキスト = [2] + [0] + [1]
        return 日付テキスト

実装インスタンス = 子クラス()
実装インスタンス.全テキスト抽出()
```

- 参考：[【Quiita】Python : クラスの継承](https://qiita.com/nyunyu122/items/9d7395f3d4de4190a991)

## イメージ：プログラム構成

1. PDFファイル解析（基盤処理）

    - IN：
        - PDFファイルパス
    - OUT：
        - PDF解析データ（pandas型）
            - page
            - text
            - x0 （左下、ページ右下が原点）
            - y0 （左下、同上）
            - x1 （右上、同上）
            - y1 （右上、同上）
            - width
            - height
    - 例外：
        - PDFファイル読込エラー
            FileNotFoundError: [Errno 2] No such file or directory: '../INPUT/elogi_invoice_first_payment-XX.pdf'
        - PDFファイル解析エラー
            PDFSyntaxError: No /Root object! - Is this really a PDF?

2. 座標でテキスト抽出（基盤処理）

    - IN：
        - PDF解析データ（pandas型）
        - 座標(x, y)
        - 探索範囲（5ピクセルにするとサンプルPDFは1件のみ抽出できた）
    - OUT：
        - テキスト
    - 例外：
        - 抽出なし

3. 請求元：テキスト抽出

    - IN：
        - PDF解析データ（pandas型）
        - 請求元の抽出情報（探索タイプ＝座標、座標x、座標y、編集方法）
        - 探索範囲
    - OUT：
        - テキスト
    - 例外：
        - 抽出なし
  
4. 請求元：テキスト編集

    - IN：テキスト
    - OUT：テキスト（前後空白削除した編集後）

5. 見出しラベルでテキスト抽出（基盤処理）

    - IN：
        - PDF解析データ（pandas型）
        - 見出しラベル
        - 探索範囲
    - OUT：
        - テキスト
    - 例外：
        - 抽出なし（見出しラベル）
        - 抽出なし（テキスト）

6. 請求日：テキスト抽出

    - IN：
        - PDF解析データ（pandas型）
        - 請求日の抽出情報（探索タイプ＝見出しラベル、見出しラベル、編集方法）
        - 探索範囲
    - OUT：
        - テキスト
    - 例外：
        - 抽出なし（見出しラベル）
        - 抽出なし（テキスト）

7. 請求日：日付編集

    - IN：
        - テキスト
    - OUT：
        - 日付
    - 例外：
        - 日付型変換エラー
  
8. 金額：テキスト抽出（見出しラベル指定）

    - IN：
        - PDF解析データ（pandas型）
        - 金額の抽出情報（探索タイプ＝見出しラベル、見出しラベル、編集方法）
        - 探索範囲
    - OUT：
        - テキスト
    - 例外：
        - 抽出なし（見出しラベル）
        - 抽出なし（テキスト）

9. 金額：数値編集

    - IN：
        - テキスト
    - OUT：
        - 数値
    - 例外：
        - 数値型変換エラー

10. ファイル名変更
    - IN：
        - PDFファイルパス
        - 請求元
        - 請求日
        - 金額
    - OUT：
        - PDFファイルパス（ファイル名変更後）
    - 例外：
        - PDFファイル読込エラー
        - PDFファイル（ファイル名変更後）重複エラー
        - PDFファイル（ファイル名変更後）書込権限エラー
  
11. 1 から 10 の制御
    - IN：
        - PDFファイルパス
        - パターンID
    - OUT：
        - PDFファイル名（変更後）
    - 例外：
        - パターン情報なし

12. パターンファイル読込
    - IN：
        - パターンファイル
    - OUT：
        - パターン情報
            - パターンID
                - 請求元（探索タイプ＝座標、座標x、座標y、編集方法）
                - 日付（探索タイプ＝ラベル、ラベル名、日付編集方法）
                - 金額（探索タイプ＝ラベル、ラベル名、金額編集方法）
                - 探索範囲
    - 例外：
        - パターンファイル読込エラー
  
13. PDFファイルごとに、パターン判定 ＆ 11. の呼び出し
