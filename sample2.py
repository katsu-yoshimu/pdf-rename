# pymupdf版 PDFファイルからテキスト抽出
import pymupdf
import pandas as pd

class extractTextFromPDFFile():
    
    def __init__(self, PDFFilePath):

        def pymupdf_extractText(PDFFilePath):

            df = pd.DataFrame([['','','','','','']])
            df.columns = ['page', 'text', 'x0', 'y0', 'x1', 'y1']

            int_page = 0
            ii_index = 0

            doc = pymupdf.open(pdf_file_name)

            for j in range(len(doc)):
                page = doc[j]
                int_page = j + 1
                pre_text_el = [0,0,0,0,"",0,0,0]
                for text_el in page.get_text("words"):
                    # 最初のデータは読み飛ばし
                    if len(pre_text_el[4]) == 0:
                        pre_text_el = list(text_el)

                    else:
                    # [5]block_no, [1]y0 が一致、かつ、
                    # 今[0]x0 と 前[2]x1 が 20ピクセル 離れていれば、
                    # [4]文字列 を結合 ＆ [2]x1 を更新
                        if text_el[5] == pre_text_el[5] and \
                           text_el[1] == pre_text_el[1] and \
                           (text_el[0] - pre_text_el[2]) < 20:
                            pre_text_el[4] = f"{pre_text_el[4]} {text_el[4]}"
                            pre_text_el[2] = text_el[2]
                    
                    # 不一致なら追加
                        else:
                            df.loc[ii_index] = [int_page,
                                                pre_text_el[4], 
                                                pre_text_el[0], pre_text_el[1],
                                                pre_text_el[2], pre_text_el[3], 
                                                ]
                            ii_index = ii_index + 1
                            pre_text_el = list(text_el)
                        
                # 最終データを追加
                if len(pre_text_el[4]) > 0:
                    df.loc[ii_index] = [int_page,
                                        pre_text_el[4], 
                                        pre_text_el[0], pre_text_el[1],
                                        pre_text_el[2], pre_text_el[3], 
                                        ]
                    ii_index = ii_index + 1
                
            doc.close()
            return df
        
        self.df = pymupdf_extractText(PDFFilePath)

    # 請求元：抽出＆編集
    def extractTextBillingSource(self):
        return None
    def editTextBillingSource(self, text):
        return text
    
    # 日付：抽出＆編集
    def extractTextDate(self):
        return None
    def editTextDate(self, text):
        return text
    
    # 金額：抽出＆編集
    def extractTextAmount(self):
        return None
    def editTextAmount(self, text):
        return text

    # テキスト表示
    def printText(self):
        text = self.extractTextBillingSource()
        if text == None:
            print(f"請求元は抽出できませんでした")
        else:
            print(f"請求元は「{text}」です。編集後は「{self.editTextBillingSource(text)}」です")
            
        text = self.extractTextDate()
        if text == None:
            print(f"日付は抽出できませんでした")
        else:
            print(f"日付は「{text}」です。編集後は「{self.editTextDate(text)}」です")

        text = self.extractTextAmount()
        if text == None:
            print(f"金額は抽出できませんでした")
        else:
            print(f"金額は「{text}」です。編集後は「{self.editTextAmount(text)}」です")


    # 座標でテキスト抽出
    def extractTextByCoordinates(self, x, y, d):
        text = None
        df = self.df

        # 1ページ AND 座標の近傍：(x-d) <= x0 <= (x+d) and (y-d) <= y0 <= (y+d) 
        df_ans = df[(df['page'] == 1) & (df['x0'] >= (x - d)) & (df['x0'] <= (x + d)) & (df['y0'] >= (y - d)) & (df['y0'] <= (y + d))]

        # テキスト抽出できない
        if len(df_ans) == 0:
            # print(f'{df_ans}')
            pass

        # テキスト抽出
        elif len(df_ans) == 1:
            # print(f'{df_ans}')
            text = df_ans.iloc[0]['text']
        
        # テキストが2件以上
        elif len(df_ans) > 1:
            # 指定した座標に一番近いテキストを選択
            def distance(x0, y0, x, y):
                return (x-x0)**2+(y-y0)**2
            df_ans.loc[:, ['distance_squared']] = distance(df_ans['x0'], df_ans['y0'], x, y)
            df_ans = df_ans.sort_values(by=["distance_squared"], ascending=True)
            # print(f'{df_ans}')
            text = df_ans.iloc[0]['text']

        return text

    # 見出しラベル指定でテキスト抽出
    def extractTextByLabel(self, label, lable_idx=0):
        text = None
        df = self.df

        df_label = df[df['text'].str.contains(label)]

        if len(df_label) == 0:
            print(f'見出しラベル[{label}]が抽出できません')
            pass

        else:
            # print(f'{df_label}')

            # 見出しラベルの文字列を返却
            text = df_label.iloc[lable_idx]['text']
            
        return text

    # 見出しラベル指定（右）でテキスト抽出
    def extractTextByLabelRight(self, label, d, lable_idx=0):
        text = None
        df = self.df

        df_label = df[df['text'].str.contains(label)]

        if len(df_label) <= lable_idx:
            print(f'見出しラベル[{label}]が抽出できません')
            pass

        else:
            # print(f'{df_label}')

            # 見出しラベルの右上(lable.x1, lable.y0)の座標
            x = df_label.iloc[lable_idx]['x1']
            y = df_label.iloc[lable_idx]['y0']

            # 1ページ AND 見出しラベルの右上(lable.x1, lable.y0)より右
            # ：x0 >= label.x1 and  (label.y0-d) <= y0 <= (label.y0+d)
            df_ans = df[(df['page'] == 1) & (df['x0'] >= x) & (df['y0'] >= (y - d)) & (df['y0'] <= (y + d))]
            
            # テキスト抽出できない
            if len(df_ans) == 0:
                # print(f'{df_ans}')
                pass
            
            # テキスト抽出
            elif len(df_ans) == 1:
                # print(f'{df_ans}')
                text = df_ans.iloc[0]['text']
            
            # テキストが2件以上
            elif len(df_ans) > 1:
                # 見出しラベルの右下の座標に一番近いテキストを選択
                def distance(x0, y0, x, y):
                    return (x-x0)**2+(y-y0)**2
                df_ans.loc[:, ['distance_squared']] = distance(df_ans['x0'], df_ans['y0'], x, y)
                df_ans = df_ans.sort_values(by=["distance_squared"], ascending=True)
                # print(f'{df_ans}')
                text = df_ans.iloc[0]['text']

        return text
    
    # 見出しラベル指定（下）でテキスト抽出
    def extractTextByLabelUnder(self, label, d, lable_idx=0):
        text = None
        df = self.df

        df_label = df[df['text'].str.contains(label)]

        if len(df_label) <= lable_idx:
            print(f'見出しラベル[{label}]が抽出できません')
            pass

        else:
            # print(f'{df_label}')

            # 見出しラベルの左下(lable.x0, lable.y1)の座標
            x = df_label.iloc[lable_idx]['x0']
            y = df_label.iloc[lable_idx]['y1']

            # 1ページ AND 見出しラベルの右下(lable.x0, lable.y1)より右
            # ：y0 >= label.y1 and  (label.x0-d) <= x0 <= (label.x0+d)
            df_ans = df[(df['page'] == 1) & (df['y0'] >= y) & (df['x0'] >= (x - d)) & (df['x0'] <= (x + d))]
            
            # テキスト抽出できない
            if len(df_ans) == 0:
                # print(f'{df_ans}')
                pass
            
            # テキスト抽出
            elif len(df_ans) == 1:
                # print(f'{df_ans}')
                text = df_ans.iloc[0]['text']
            
            # テキストが2件以上
            elif len(df_ans) > 1:
                # 見出しラベルの右下の座標に一番近いテキストを選択
                def distance(x0, y0, x, y):
                    return (x-x0)**2+(y-y0)**2
                df_ans.loc[:, ['distance_squared']] = distance(df_ans['x0'], df_ans['y0'], x, y)
                df_ans = df_ans.sort_values(by=["distance_squared"], ascending=True)
                # print(f'{df_ans}')
                text = df_ans.iloc[0]['text']

        return text

class extractTextFromPDFFile_elogi(extractTextFromPDFFile):
    # 請求元：抽出＆編集（例：抽出「mipick CO., LTD.」、編集なし）
    def extractTextBillingSource(self):
        return self.extractTextByCoordinates(x=361, y=167, d=5)
    
    # 日付：抽出＆編集（例：抽出「Date: 12/23/2024」、編集「20241223」）
    def extractTextDate(self):
        return self.extractTextByLabel("Date:")
    def editTextDate(self, text):
        d = text.lstrip("Date: ")
        d = d.split("/")
        if len(d[0]) == 1:
            d[0] = "0" + d[0]
        if len(d[1]) == 1:
            d[1] = "0" + d[1]
        return d[2] + d[0] + d[1]
    
    # 金額：抽出＆編集（例：抽出「¥20,013」、編集「20013」）
    def extractTextAmount(self):
        return self.extractTextByCoordinates(x=151, y=240, d=5)
    def editTextAmount(self, text): # ToDo：数値型エラーの検出
        return text.lstrip("¥").replace(",", "")

class extractTextFromPDFFile_rakuten(extractTextFromPDFFile):
    # 請求元：抽出＆編集（例：抽出「楽天モバイル株式会社」、編集なし）
    def extractTextBillingSource(self):
        return self.extractTextByCoordinates(x=478, y=114, d=5)
    
    # 日付：抽出＆編集（例：抽出「：2024/10/04」、編集「20241004」）
    def extractTextDate(self):
        return self.extractTextByCoordinates(x=504, y=98, d=5)
    def editTextDate(self, text):
        d = text.lstrip("：")
        d = d.split("/")
        if len(d[1]) == 1:
            d[1] = "0" + d[1]
        if len(d[2]) == 1:
            d[2] = "0" + d[2]
        return d[0] + d[1] + d[2]
    
    # 金額：抽出＆編集（例：抽出「1,081円」、編集「1081」）
    def extractTextAmount(self):
        return self.extractTextByLabelRight(label="請求合計額（税込）", d=5)
    def editTextAmount(self, text):
        return text.rstrip("円").replace(",", "")

class extractTextFromPDFFile_amazon(extractTextFromPDFFile):
    # 請求元：抽出＆編集（例：抽出「アマゾンジャパン合同会社」、編集なし）
    def extractTextBillingSource(self):
        return self.extractTextByLabelUnder(label="発行者", d=5, lable_idx=1)
    
    # 日付：抽出＆編集（例：抽出「2024-10-27」、編集「20241027」）
    def extractTextDate(self):
        return self.extractTextByLabelRight(label="請求書発行日", d=5)
    def editTextDate(self, text):
        d = text.split("-")
        if len(d[1]) == 1:
            d[1] = "0" + d[1]
        if len(d[2]) == 1:
            d[2] = "0" + d[2]
        return d[0] + d[1] + d[2]
    
    # 金額：抽出＆編集（例：抽出「￥1,290」、編集「1290」）
    def extractTextAmount(self):
        return self.extractTextByLabelRight(label="合計", d=5)
    def editTextAmount(self, text):
        return text.lstrip("￥").replace(",", "")

class extractTextFromPDFFile_softbank(extractTextFromPDFFile):
    # 請求元：抽出＆編集（例：抽出「ソフトバンク株式会社（ワイモバイル）」、編集「ソフトバンク株式会社」）
    def extractTextBillingSource(self):
        return self.extractTextByCoordinates(x=395, y=69, d=5)
    def editTextBillingSource(self, text):
        return text.rstrip("（ワイモバイル）")
        
    # 日付：抽出＆編集（例：抽出「発行日２０２４年 １０月 １１日」、編集「20241011」）
    def extractTextDate(self):
        return self.extractTextByCoordinates(x=395, y=58, d=5)
    def editTextDate(self, text):
        d = text.lstrip("発行日")
        d = d.split(" ")
        d[0] = d[0].rstrip("年")
        d[1] = d[1].rstrip("月")
        d[2] = d[2].rstrip("日")

        # 2バイト数字を1バイト数字に変換
        z_digit = '１２３４５６７８９０'
        h_digit = '1234567890'
        z2h_digit = str.maketrans(z_digit, h_digit)
        d[0]=d[0].translate(z2h_digit)
        d[1]=d[1].translate(z2h_digit)
        d[2]=d[2].translate(z2h_digit)

        # 桁合わせ
        if len(d[1]) == 1:
            d[1] = "0" + d[1]
        if len(d[2]) == 1:
            d[2] = "0" + d[2]

        return d[0] + d[1] + d[2]
    
    # 金額：抽出＆編集（例：抽出「10,786」、編集「10786」）
    def extractTextAmount(self):
        return self.extractTextByLabelRight(label="ご請求金額", d=5)
    def editTextAmount(self, text):
        return text.replace(",", "")

class extractTextFromPDFFile_nttcom(extractTextFromPDFFile):
    # 請求元：抽出＆編集（例：抽出「取引日:2024/09/30 ＮＴＴコミュニケーションズ株式会社」、編集「ＮＴＴコミュニケーションズ株式会社」）
    def extractTextBillingSource(self):
        return self.extractTextByLabel(label="取引日:")
    def editTextBillingSource(self, text):
        s = text.split(" ")
        return s[1]
    
    # 日付：抽出＆編集（例：抽出「2024 10 14」、編集「20241014」）
    def extractTextDate(self):
        return self.extractTextByCoordinates(x=473, y=77, d=5)
    def editTextDate(self, text):
        d = text.split(" ")
        if len(d[1]) == 1:
            d[1] = "0" + d[1]
        if len(d[2]) == 1:
            d[2] = "0" + d[2]
        return d[0] + d[1] + d[2]
    
    # 金額：抽出＆編集（例：抽出「333」、編集「333」）
    def extractTextAmount(self):
        return self.extractTextByLabelRight(label="　・・・契約番号計・・・", d=5)
    def editTextAmount(self, text):
        return text.replace(",", "")


# elogi用のクラスをインスタンス化して実行
pdf_file_name = "../input/elogi_invoice_first_payment-26.pdf"
p = extractTextFromPDFFile_elogi(pdf_file_name)
print(f'---------- {pdf_file_name} ----------')
p.printText()

# 楽天モバイル用のクラスをインスタンス化して実行
pdf_file_name = "../input/20241004_楽天モバイル_1081.pdf"
print(f'---------- {pdf_file_name} ----------')
p = extractTextFromPDFFile_rakuten(pdf_file_name)
p.printText()

# amazon用のクラスをインスタンス化して実行
pdf_file_name = "../input/20241027_アマゾンジャパン_1419.pdf"
p = extractTextFromPDFFile_amazon(pdf_file_name)
print(f'---------- {pdf_file_name} ----------')
p.printText()

# ソフトバンク用のクラスをインスタンス化して実行
pdf_file_name = "../input/20241011_ソフトバンク_10786.PDF"  # 以前の方法ではテキストが読み取れない
p = extractTextFromPDFFile_softbank(pdf_file_name)
print(f'---------- {pdf_file_name} ----------')
p.printText()

# NTTコム用のクラスをインスタンス化して実行
pdf_file_name = "../input/20241014_NTTコミュニケーションズ_333.pdf"  # 以前の方法ではテキストが読み取れない
p = extractTextFromPDFFile_nttcom(pdf_file_name)
print(f'---------- {pdf_file_name} ----------')
p.printText()
