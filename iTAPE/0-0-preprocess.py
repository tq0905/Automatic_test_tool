import argparse
import json, re
import random
import copy
import nltk
from tqdm import tqdm


'''
1.1用占位符替换body中的杂项信息： url、超链接、图像、 代码片段和以未选中的Markdown复选框开头的行
输入：某个issue的body
输出：将body中杂项信息替换为占位符后的body + 占位符数目
'''
def improve_body(origin_str, return_max_cnt = False):
    maxcnt = 0 #占位符的数目

    #(1)将代码片段转换为占位符 “phofcode"
    search = re.compile("```(?:.|\n)+?```") #re.compile()将正则表达式转化为对象，多次调用一个正则表达式就重复利用这个正则对象-》re.search(pattern, string)的调用方式就转换为 pattern.search(string)的调用方式
    if return_max_cnt:
        maxcnt = max(maxcnt, len(search.findall(origin_str)))
    origin_str = search.sub(" phofcode ", origin_str)#re.sub(pattern, repl, string),pattern：正则表达式，被正则表达式搜索到的目标要被替换成为的结果，string:搜索范围

    #(2)将图像转换为占位符 text+"phofimage"
    search = re.compile("\!\[(.*?)\]\(.+?\)")
    if return_max_cnt:
        maxcnt = max(maxcnt, len(search.findall(origin_str)))
    origin_str = search.sub(lambda x: " " + x.group(1) + " phofimage ", origin_str)#group(1) 列出第一个括号匹配部分

    #(3)将hyper link转化为占位符 text+"phofhyperlink"
    search = re.compile("(?<!\!)\[(.*?)\]\(.+?\)")
    if return_max_cnt:
        maxcnt = max(maxcnt, len(search.findall(origin_str)))
    origin_str = search.sub(lambda x: " " + x.group(1) + " phofhyperlink ", origin_str)

    #(4)将URL转换为占位符 “phofurl"
    search = re.compile("(https?|ftp)://[^\s/$.?#].[^\s]*")
    if return_max_cnt:
        maxcnt = max(maxcnt, len(search.findall(origin_str)))
    origin_str = search.sub(" phofurl ", origin_str)

    #(5)将markdown中以未选中的选框开头的行，删除（替换为“”）
    search = re.compile("- +\[ \].*") #line with unchecked tickbox in markdown (template provided useless desc) -> (remove)
    origin_str = search.sub("", origin_str)

    #(6)避免***abc***被NLTK识别为令牌
    search = re.compile("(\*{1,})([^\s]+?)(\*{1,})")
    origin_str = search.sub(lambda x: " " + x.group(1) + " " + x.group(2) + " " + x.group(3) + " ", origin_str)

    #(7)删除换行符
    search = re.compile("(\n\r)|(\r\n)|(\n)")
    if return_max_cnt:
        maxcnt = max(maxcnt, len(search.findall(origin_str)))
    origin_str = search.sub(" ", origin_str)
    
    if return_max_cnt:
        return origin_str, maxcnt
    else:
        return origin_str, 0

'''
1.2过滤掉body不合适的issue样本：body长度不合适 or 在markdown的代码区域的外含有HTML标签
输入：某个issue的body + body的词语list
输出：当body不合适（该issue样本应该被丢弃），返回TRUE，否则FALSE
'''
def filter_body(issue_body, issue_body_tokenize):
    length = len(issue_body_tokenize)
    if length < 30:
        return True
    if length > 300:
        return True
    if len(re.findall("<[^<]+?>", issue_body)) > 0:
        return True
    return False

'''
1.3去掉title中的tag标签和markdown重点标记符”**"
输入：某个issue的title
输出：修正后的title
'''
def improve_title(issue_title): 
    original_len = len(issue_title)
    #移除在title开头的 “[tag]”
    issue_title = re.sub("^(\s*\[.*?\])+", "", issue_title)
    #去掉“tag: "：寻找冒号所在的位置，并且要小于1/2的titile长度才能判定为符合情况
    pos = issue_title.find(": ")
    if -1 < pos < len(issue_title) - original_len / 2:
        issue_title = issue_title[pos + 1:].strip() #strip()：移除字符串收尾的空格
    # 再次移除”[tag]"
    issue_title = re.sub("^(\s*\[.*?\])+", "", issue_title)
    #移除markdown的重点标记符“**”
    issue_title = re.sub("(\*{1,})(.+?)(\*{1,})", lambda x: x.group(2), issue_title)
    return issue_title.strip()

def main():
    print ("loading json data... (this should take several minutes...)")
    with open("data/github.json") as f:
        all_issues = json.load(f)

    #1.数据预处理：去除难以标记的样本并裁剪数据中的杂项内容
    print ("preprocessing...")
    preprocessed_issues = []#储存预处理之后的样本list
    for idx, issue in enumerate(tqdm(all_issues)):
        #扫描所有issue样本
        #1.1用占位符替换body中的杂项信息： url、超链接、图像、 代码片段和以未选中的Markdown开头的行复选框
        issue['body'], _ = improve_body(issue['body'])
        # 1.2过滤掉body不合适的issue样本：body长度不合适 or 在markdown的代码区域的外含有HTML标签
        #fiter_body()返回结果为true，issue应被过滤，跳过当前循环，扫描下一个issue(idx+1)
        issue_body_tokenize = nltk.word_tokenize(issue['body'])# nltk.word_tokenize（string）：以空格形式实现分词
        if filter_body(issue['body'], issue_body_tokenize):
            continue
        #1.3去掉title中的“tag： ”,“[tag]",和markdown重点标记符”**"
        issue['title'] = improve_title(issue['title'])
        #1.4将预处理之后的issue存入preprocessed_issues
        preprocessed_issues.append(issue)
    with open("data/preprocessed_issues.json", "w") as f:
         json.dump(preprocessed_issues, f)
    print ("preprocess finish. Begin to obtain", len(preprocessed_issues), "handlable issues.")

    #2.将预处理之后的数据集分为8：1:1
    # to provide unified boundary and perform fair comparison between different refinement strategy
    sep1 = int(len(preprocessed_issues) * 0.8)
    sep2 = int(len(preprocessed_issues) * 0.9)

if __name__ == "__main__":
    main()