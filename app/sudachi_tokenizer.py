from sudachipy import dictionary, tokenizer


class SudachiTokenizer(object):

    def __init__(self):
        self.tokenizer_obj = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.C

    @staticmethod
    def filter_word(tk):
        part_of_speech = tk.part_of_speech()

        if '数詞' in part_of_speech:
            return False
        elif '名詞' in part_of_speech:
        # elif '名詞' in part_of_speech or '動詞' in part_of_speech or '形容詞' in part_of_speech:
            return True

    def wakati_to_token(self, text):
        tk_list = list(self.tokenizer_obj.tokenize(text, self.mode))
        return tk_list

    @staticmethod
    def token_to_words(token_list):
        return [t.surface() for t in token_list]

    def token_to_normalized_form(self, token_list, if_filter=True):
        res = []
        for t in token_list:
            w = t.normalized_form()
            if if_filter:
                if not self.filter_word(t):
                    w = '-'
            res.append(w)
        return res

    @staticmethod
    def split_text(txt, txt_chunk_length_th=10000):
        sts = txt.split()
        txt_chunks = []
        txt_chunk = ''
        for s in sts:
            if len(txt_chunk) > txt_chunk_length_th - len(s):
                txt_chunks.append(txt_chunk)
                txt_chunk = s
            else:
                txt_chunk += '\n' + s
        txt_chunks.append(txt_chunk)
        return txt_chunks

    def tokenize(self, txt, auto_split):
        try:
            tks = self.tokenizer_obj.tokenize(txt)
            return tks
        except Exception as e:
            if auto_split:
                tks = []
                txt_chunks = self.split_text(txt)
                for t in txt_chunks:
                    tks += self.tokenizer_obj.tokenize(t)
                return tks
            else:
                raise e

    def wakati(self, txt, auto_split=True):
        # tk_list = list(self.tokenizer_obj.tokenize(txt, self.mode))
        tk_list = self.tokenize(txt, auto_split=auto_split)

        words = []
        for tk in tk_list:
            if self.filter_word(tk):
                words.append(tk.normalized_form())

        return words

    def wakati_no_filter(self, txt, auto_split=True):
        tk_list = self.tokenize(txt, auto_split=auto_split)
        words = [t.normalized_form() for t in tk_list]
        return words
