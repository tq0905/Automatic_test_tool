import json, re
import random
import copy
import nltk
from tqdm import tqdm

'''
3.1启发式规则1：过滤title单词数<5 or >15，或title含有url的issue
输入：某个issue的title和title的单词list
输出：当issue需要被过滤，返回TRUE，否则FALSE
'''
def rule1checker(issue_title, issue_title_word):
    length = len(issue_title_word)
    if length < 5:
        return True
    if length > 15:
        return True
    if len(re.findall("(https?|ftp)://[^\s/$.?#].[^\s]*", issue_title)) > 0:
        return True
    return False

'''
3.2启发式规则2：过滤title中超过70%的单词无法在body中找到的issue
输入：某个issue的title和body各自的的单词list
输出：当issue需要被过滤，返回TRUE，否则FALSE
'''
def rule2checker(issue_title_words, issue_body_words):
    body_words_set = set(issue_body_words)
    cnt_each = 0
    for word in issue_title_words:
        if word in body_words_set:
            cnt_each += 1
    if cnt_each <= len(issue_title_words) * 0.3:
        return True
    return False

'''
3.3启发式规则3：过滤掉title中存在一个超过其70%长度的子序列，能够完全匹配body中某个句子的issue
输入：某个issue的title和body各自的的单词list
输出：当issue需要被过滤，返回TRUE，否则FALSE
'''
def rule3checker(issue_title_tokenize, issue_body_tokenize):
    title_words = [x.lower() for x in issue_title_tokenize]
    body_words = [x.lower() for x in issue_body_tokenize]
    exp = ""
    # build substring location RE: (\s+AA)(\s+BB)(\s+CC)(\s+DD) to match AA BB CC (more postfix in title), BB CC DD (more prefix in title), AA BB DD (more tokens, such as punctuations, in title) etc. in body.
    for _ in title_words:
        _ = re.escape(_)
        exp += "(" + "\s+" + _ + ")?"
    re_iter = re.compile(exp)
    each_cnt = 0
    for s in re_iter.finditer(" " + " ".join(body_words)):
        each_each_cnt = 0
        for _ in s.groups():
            if _ is not None:
                each_each_cnt += 1
        each_cnt = max(each_cnt, each_each_cnt)
    if each_cnt >= len(title_words) * 0.7:
        return True
    return False

'''
输入：字符串string
输出：一个result字典：字典的每个key是版本号，其内储存一个[序号，版本号出现次数]的list
'''
def get_version_list(string):
    # e.g.  v1  V1.1  2.3  py3.6  1.2.3-alpha1  3.1rc  v2-beta3
    result = {}
    for item in re.findall("(?<=\W)((([vV][0-9]+)|([a-zA-Z_]*[0-9]+\w*(\.[a-zA-Z_]*[0-9]\w*)))([\.-]\w+)*)(?=\W)",string):
        key = item[0].strip()
        if key not in result:
            result[key] = [len(result), 0]  # order, term-freq
        result[key][1] += 1
    return result

'''
输入：字符串string
输出：一个result字典：字典的每个key是标识符，其内储存一个[序号，标识符出现次数]的list
'''
def get_identifier_list(string):
    # e.g.  smallCamelCase  BigCamelCase  _underline_name_  test_123  func123Test
    result = {}
    for item in re.findall("(?<=\W)(([A-Z]*[a-z_][a-z0-9_]*)([A-Z_][a-z0-9_]*)+)(?=\W)", string):
        key = item[0].strip()
        if key not in result:
            result[key] = [len(result), 0]  # order, term-freq
        result[key][1] += 1
    return result


def main():
    with open("data/preprocessed_issues.json") as f:
        preprocessed_issues = json.load(f)

    # 2.将预处理之后的数据集分为8：1:1
    # 提供统一的边界，对不同的细化策略进行公平比较
    sep1 = int(len(preprocessed_issues) * 0.8)
    sep2 = int(len(preprocessed_issues) * 0.9)

    print("applying refinement rules...")
    valid_issues=[]
    valid_issues_train = []
    valid_issues_val = []
    valid_issues_test = []

    for idx, issue in enumerate(tqdm(preprocessed_issues)):
        issue_body_tokenize = nltk.word_tokenize(issue['body'])
        issue_title_tokenize = nltk.word_tokenize(issue['title'])
        # 将所有单词转化为小写
        issue_title_words = [x.lower() for x in issue_title_tokenize if re.match("\S*[A-Za-z0-9]+\S*", x)]
        issue_body_words = [x.lower() for x in issue_body_tokenize if re.match("\S*[A-Za-z0-9]+\S*", x)]
        # # 3.样本细化：使用三个启发式的规则
        # 当某个issue符合任何一个rule，该issue被过滤,跳过当前循环，扫描下一个issue
        if (rule1checker(issue['title'], issue_title_words)) \
                or (rule2checker(issue_title_words, issue_body_words)) \
                or (rule3checker(issue_title_tokenize, issue_body_tokenize)):
            continue
        # 4.1在issue里添加新的key“_spctok"，value为一个下属字典。下属字典有两个key:"ver""idt"，value分别为该issue的body中版本号和标识符的result字典
        issue["_spctok"] = {}
        issue["_spctok"]["ver"] = get_version_list(" " + issue['body'] + " ")
        issue["_spctok"]["idt"] = get_identifier_list(" " + issue['body'] + " ")
        # 4.2在每个版本号和标识符前后分别加上tag
        # 4.2.1在每个版本号前后非别加上"verid40" 和 "verid0"
        version_list = issue["_spctok"]["ver"]
        for version, stat in sorted(version_list.items(), key=lambda x: (len(x[0]))):
            issue['body'] = re.sub(re.escape(version), " verid40 " + version + " verid0 ", issue['body'],flags=re.IGNORECASE)
            issue['title'] = re.sub(re.escape(version), " " + version + " ", issue['title'], flags=re.IGNORECASE)
        # 4.2.2在每个标识符前后非别加上"idtid40" 和 "idtid0"
        identifier_list = issue["_spctok"]["idt"]
        for idt, stat in sorted(identifier_list.items(), key=lambda x: (len(x[0]))):
            issue['body'] = re.sub(re.escape(idt), " idtid40 " + idt + " idtid0 ", issue['body'], flags=re.IGNORECASE)
            issue['title'] = re.sub(re.escape(idt), " " + idt + " ", issue['title'], flags=re.IGNORECASE)
        # 最后小写化
        issue['body'] = " ".join(nltk.word_tokenize(issue['body'], preserve_line=False)).strip().lower()
        issue['title'] = " ".join(nltk.word_tokenize(issue['title'], preserve_line=False)).strip().lower()
        if idx < sep1:
            valid_issues_train.append(issue)
        elif idx < sep2:
            valid_issues_val.append(issue)
        else:
            valid_issues_test.append(issue)
        valid_issues.append(issue)
    print("refinement and tagging finish. obtain", len(valid_issues),"good issues for txt.")

    #储存
    save=[valid_issues_train, valid_issues_val, valid_issues_test]
    with open("data/good_issues.json", "w") as f:
        json.dump(save, f)
    print("refining and tagging success. good sample set is saved to data/" + str(
        len(valid_issues_train) + len(valid_issues_val) + len(
            valid_issues_test)) + "good_issues.json'")

if __name__ == "__main__":
    main()