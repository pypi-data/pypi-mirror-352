class GFCipher:
    def caesar_encode(self, text, shift=3):
        res = ''
        for i in text:
            if i == ' ':
                res += ' '
            elif i.isupper():
                res += chr((ord(i) - ord('A') + shift) % 26 + ord('A'))
            elif i.islower():
                res += chr((ord(i) - ord('a') + shift) % 26 + ord('a'))
            else:
                res += i
        return res
    def caesar_decode(self, text, shift=3):
        res = ''
        for i in text:
            if i == ' ':
                res += ' '
            elif i.isupper():
                res += chr((ord(i) - ord('A') - shift) % 26 + ord('A'))
            elif i.islower():
                res += chr((ord(i) - ord('a') - shift) % 26 + ord('a'))
            else:
                res += i
        return res
    def a1z26_encode(self, text):
        res=''
        for i in text:
            if i==" ":
                if res.endswith('-'):
                    res=res[:-1]
                res+=" "
            elif i.isalpha():
                res+=str(ord(i.lower()) - ord('a') + 1)+"-"
            else:
                if res.endswith('-'):
                    res=res[:-1]
                res+=i
        if res.endswith('-'):
            res=res[:-1]
        return res
    def a1z26_decode(self, text):
        res=''
        text = text.split(' ')
        for word in text:
            splitted_word = word.split('-')
            for spart_word in splitted_word:
                ltr_idx = 0
                while ltr_idx< len(spart_word):
                    if spart_word[ltr_idx].isdigit():
                        if ltr_idx+1<len(spart_word):
                            if spart_word[ltr_idx+1].isdigit():
                                res+=chr(int(spart_word[ltr_idx]+spart_word[ltr_idx+1])+64)
                                ltr_idx+=1
                            else:
                                res+=chr(int(spart_word[ltr_idx])+64)
                        else: 
                            res+=chr(int(spart_word[ltr_idx])+64)
                    else:
                        res+=spart_word[ltr_idx]
                    ltr_idx+=1
            res+=" "
        return res
    def atbash_encode(self, text):
        res = ''
        for i in text:
            if i.isalpha():
                if i.isupper():
                    res+=chr(155-ord(i))
                elif i.islower():
                    res+=chr(219-ord(i))
            else:
                res+=i
        return res
    def atbash_decode(self, text):
        res = ''
        for i in text:
            if i.isalpha():
                if i.isupper():
                    res+=chr(155-ord(i))
                elif i.islower():
                    res+=chr(219-ord(i))
            else:
                res+=i
        return res
    def vigenere_encode(self, text, key):
        text = text.upper()
        key = key.upper()
        res = ''
        cnt = 0
        for i in text:
            if i.isalpha():
                ltr_key = key[cnt%len(key)]
                x = ((ord(i)-ord('A'))+(ord(ltr_key)-ord('A')))%26
                res+=chr(x+ord('A'))
                cnt+=1
            else:
                res+=i
        return res
    def vigenere_decode(self, text, key):
        text = text.upper()
        key = key.upper()
        res = ''
        cnt = 0
        for i in text:
            if i.isalpha():
                ltr_key = key[cnt%len(key)]
                x = ((ord(i)-ord('A'))-(ord(ltr_key)-ord('A')))%26
                res+=chr(x+ord('A'))
                cnt+=1
            else:
                res+=i
        return res
