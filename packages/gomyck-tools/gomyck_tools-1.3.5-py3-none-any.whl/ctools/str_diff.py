# import difflib
#
# s1 = '12-23'
# s2 = '00-11'
# s3 = '2023-05-05 12:00:00-2023-05-06 23:00:00 剩余4'
#
# sm = difflib.SequenceMatcher(None, s1, s3)
#
# print(sm.ratio()) # 输出相似度得分


from fuzzywuzzy import fuzz

s1 = '12-23'
s2 = '00-11'
s3 = '2023-05-05 12:00:00-2023-05-06 23:00:00 剩余4'
s4 = '2023-04-28 00:00:00-2023-04-28 11:00:00 剩余12'
score = fuzz.ratio(s2, s4)

print(score) # 输出相似度得
