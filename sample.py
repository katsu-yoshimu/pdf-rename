from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.pdfpage import PDFPage
from pdfminer3.layout import LAParams, LTTextContainer
import pandas as pd

# PDFファイルからテキスト抽出する基底クラス
class extractTextFromPDF():
    def __init__(self, PDFFilePath):

        def pdfminer_config(line_overlap, word_margin, char_margin,line_margin, detect_vertical):
            laparams = LAParams(line_overlap=line_overlap,
                                word_margin=word_margin,
                                char_margin=char_margin,
                                line_margin=line_margin,
                                detect_vertical=detect_vertical)
            resource_manager = PDFResourceManager()
            device = PDFPageAggregator(resource_manager, laparams=laparams)
            interpreter = PDFPageInterpreter(resource_manager, device)
            return (interpreter, device)

        def pdfminer_extractText(PDFFilePath):

            list = ['','','','','','','','']
            df = pd.DataFrame([list])
            df.columns = ['page', 'text', 'x0', 'y0', 'x1', 'y1', 'width', 'height']

            int_page = 0
            ii_index = 0

            with open(PDFFilePath, 'rb') as fp:
                interpreter, device = pdfminer_config(line_overlap=0.1, 
                                                    word_margin=0.1,
                                                    char_margin=0.1, 
                                                    line_margin=0.1, 
                                                    detect_vertical=False)
                for page in PDFPage.get_pages(fp):
                    int_page = int_page + 1
                    interpreter.process_page(page)
                    layout = device.get_result()
                    for lt in layout:
                        # LTTextContainerの場合だけデータ追加
                        if isinstance(lt, LTTextContainer):
                            df.loc[ii_index] = [int_page, lt.get_text().strip(), 
                                                lt.x0, lt.y0, lt.x1, lt.y1, 
                                                lt.width, lt.height]
                            ii_index = ii_index + 1
            device.close()
            return df
        
        self.df = pdfminer_extractText(PDFFilePath)

    # 座標でテキスト抽出
    def extractTextByCoordinates(self, x, y, d):
        text = None
        df = self.df

        # 1ページ AND 座標の近傍
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
    
    # 見出しラベルでテキスト抽出   # ToDo:見出し"Total"は２つある。見出しラベルの座標を指定した方がよいかも？他のパターンを確認して判定
    def extractTextByLabel(self, label, d):
        text = None
        df = self.df

        df_label = df[df['text'].str.contains(label)]

        if len(df_label) == 0:
            print(f'見出しラベル[{label}]が抽出できません')
            pass

        else:
            # print(f'{df_label}')

            # 見出しラベルの右下の座標
            x = df_label.iloc[0]['x1']
            y = df_label.iloc[0]['y0']

            # 1ページ AND 見出しラベルの右下より右
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

# elogi用のクラスを基底クラスを継承して実装
class extractTextFromPDFFile_elogi(extractTextFromPDF):
    # 請求元：抽出＆編集
    def extractTextBillingSource(self):
        return self.extractTextByCoordinates(x=361.502, y=661.294, d=5)
    def editTextBillingSource(self, text):
        return text.replace(" ", "") # スペースを削除した（仮実装）
    
    # 日付：抽出＆編集
    def extractTextDate(self):
        return self.extractTextByLabel(label="Date:", d=5)  # ToDo:見出しラベルの座標を指定した方がよいかも？
    def editTextDate(self, text): # ToDo：日付型エラーの検出
        d = text.split("/")
        if len(d[0]) == 1:
            d[0] = "0" + d[0]
        if len(d[1]) == 1:
            d[1] = "0" + d[1]
        return d[2] + d[0] + d[1]
    
    # 金額：抽出＆編集
    def extractTextAmount(self):
        return self.extractTextByLabel(label="Total", d=5)  # ToDo:見出しラベルの座標を指定した方がよいかも？
    def editTextAmount(self, text): # ToDo：数値型エラーの検出
        return text.lstrip("¥").replace(",", "")

# elogi用のクラスをインスタンス化して実行
p = extractTextFromPDFFile_elogi('../input/elogi_invoice_first_payment-29.pdf') # 正常読込可能
# p = extractTextFromPDFFile_elogi('../input/hoge.pdf') # FileNotFoundError: [Errno 2] No such file or directory: '../input/hoge.pdf'
# p = extractTextFromPDFFile_elogi('../input/memo.txt') # PDFSyntaxError: No /Root object! - Is this really a PDF?
p.printText()
print(p.df)