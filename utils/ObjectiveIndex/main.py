# 裁判文书客观指标的检测，所有客观指标的检测方法都在这里面啊啊啊啊啊啊太长了怪我自己
# input: 数据源为xml格式的裁判文书
# 输出直接显示在页面上，为错误信息提示-->输出json给前端
# 未确定如何打分-->已解决

from xml.etree import ElementTree as etree
import re
import datetime, time
import json
import config as cf
from config import *
import sys
import numpy as np

standard = ['文首', '首部', '事实', '理由', '依据', '主文', '尾部', '落款', '附件', '其他']


def wenshu_analysis(root_node):
    wenshu = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '附件': [], '其他': []}
    # 第一次循环找到关键字节点
    test = []
    index = [-1 for i in range(10)]
    for i in range(len(root_node)):
        if root_node[i].tag == 'WS':
            wenshu['文首'].append(root_node[i])
            index[0] = i
        elif root_node[i].tag == 'DSR' or root_node[i].tag == 'SSJL':
            wenshu['首部'].append(root_node[i])
            index[1] = i
        elif root_node[i].tag == 'AJJBQK':
            wenshu['事实'].append(root_node[i])
            index[2] = i
        elif root_node[i].tag == 'CPFXGC':
            wenshu['理由'].append(root_node[i])
            index[3] = i
            for subnode in root_node[i]:
                if subnode.tag == 'FLFTYY':
                    wenshu['依据'].append(subnode)
                    index[4] = i
        elif root_node[i].tag == 'PJJG':
            wenshu['主文'].append(root_node[i])
            index[5] = i
            for subnode in root_node[i]:
                if subnode.tag == 'SSFCD':
                    index[6] = i
                    wenshu['尾部'].append(subnode)
        elif root_node[i].tag == 'WW':
            wenshu['落款'].append(root_node[i])
            index[7] = i
        elif root_node[i].tag == 'FJ':
            wenshu['附件'].append(root_node[i])
            index[8] = i
        else:
            test.append(i)
    print('结构事项顺序' + str(index))
    for i in range(len(test)):
        if test[i] > (max(index)):
            wenshu['其他'].append(root_node[i])
        else:
            print('------未知错误')
            print(root_node[i].tag)
    return wenshu, index


# 结构事项准确性
def acc_GCSX(index, wenshu_corr):
    # 篇章结构规范性结果，0表示正确，1表示缺少，2表示顺序错误
    res_score = 0
    res = [0 for i in range(9)]
    for i in range(len(index) - 1):
        if index[i] == -1:
            res[i] = 1
            wenshu_corr[standard[i]].append('篇章结构：缺少' + standard[i])
            res_score -= cf.acc_GCSX_subscore1
    lis_index = lis(index)
    # 最长递增子序列检测顺序
    for i in range(len(index) - 1):
        if index[i] != -1 and (index[i] not in lis_index):
            wenshu_corr[standard[i]].append('篇章结构：' + standard[i] + '位置错误')
            res_score -= cf.acc_GCSX_subscore2
            res[i] = 2
    print('结构事项结果，0为正确，1为缺少，2为顺序错误')
    print(res)
    res_score += cf.acc_GCSX_score
    if res_score < 0:
        res_score = 0
    return res_score, wenshu_corr, res


# 最长递增子序列
def lis(arr):
    n = len(arr)
    m = [0] * n
    for x in range(n - 2, -1, -1):
        for y in range(n - 1, x, -1):
            if arr[x] < arr[y] and m[x] <= m[y]:
                m[x] += 1
        max_value = max(m)
        result = []
        for i in range(n):
            if m[i] == max_value:
                result.append(arr[i])
                max_value -= 1
    return result


# wenshu_analysis(root_node)

# 审理经过准确性
# wenshu, _ = wenshu_analysis(root_node)

def acc_SLJG(wenshu, wenshu_corr):
    # 案件受理时间，开庭时间，适用程序，到庭情况，审理结果
    res_score = 0
    standard_SLJG = ['案件受理时间', '开庭时间', '适用程序', '到庭情况', '审理结果']
    index_SLJG = [-1 for i in range(5)]
    for node in wenshu['首部']:
        # print(node.tag)
        if node.tag == 'SSJL':
            SSJL_txt = node.get('value')
            # print('案件审理经过文本')
            # print(SSJL_txt)
            for subnode in node:
                # 受理日期
                if subnode.tag == 'SLRQ':
                    index_SLJG[0] = SSJL_txt.find('受理')
                # 开庭日期
                if subnode.tag == 'KTRQ':
                    index_SLJG[1] = SSJL_txt.find('开庭')
                # 适用程序
                if '程序' in subnode.get('nameCN'):
                    index_SLJG[2] = SSJL_txt.find(subnode.get('value'))
                # 出庭当事人信息
                if subnode.tag == 'CTDSRXX':
                    index_SLJG[3] = SSJL_txt.find('到庭')
                index_SLJG[4] = SSJL_txt.find('审理终结')
            break
    # print('案件审理经过顺序')
    # print(index_SLJG)
    for i in range(len(index_SLJG)):
        if index_SLJG[i] == -1:
            wenshu_corr['首部'].append('案件审理经过缺少' + standard_SLJG[i])
            res_score -= cf.acc_SLJG_subscore1
    lis_index = lis(index_SLJG)
    for i in range(len(index_SLJG)):
        if index_SLJG[i] != -1 and (index_SLJG[i] not in lis_index):
            wenshu_corr['首部'].append('案件审理经过中' + standard_SLJG[i] + '顺序错误')
            res_score -= cf.acc_SLJG_subscore2
    # print('案件审理经过累计错误')
    # print(wenshu_corr['首部'])
    res_score += cf.acc_SLJG_score
    if res_score < 0:
        res_score = 0
    return res_score, wenshu_corr


def con_pun_DSR(DSR_txt, wenshu_corr):
    res_score = 0
    if re.match(r'^原告.*', DSR_txt):
        if DSR_txt[DSR_txt.index('原告') + 2] != '：':
            wenshu_corr['首部'].append('标点符号：' + DSR_txt + '原告后应为冒号')
            res_score -= 1
    if re.match(r'^被告.*', DSR_txt):
        if DSR_txt[DSR_txt.index('被告') + 2] != '：':
            wenshu_corr['首部'].append('标点符号：' + DSR_txt + '被告后应为冒号')
            res_score -= 1
    if re.match(r'^[\u4e00-\u9fa5]{0,6}人.*', DSR_txt):
        if DSR_txt[DSR_txt.index('人') + 1] != '：':
            wenshu_corr['首部'].append('标点符号：' + DSR_txt + '其他诉讼参与人后应为冒号')
            res_score -= 1
    return res_score, wenshu_corr


# 当事人信息准确性
def acc_CSR(wenshu, wenshu_corr):
    standard_DSR = ['诉讼身份', '姓名', '性别', '出生年月日', '民族', '籍贯', '住址', '公民身份证号']
    res_score = 0
    if len(wenshu['首部']) == 0:
        return res_score, wenshu_corr
    for node in wenshu['首部']:
        if node.tag == 'DSR':
            for subnode in node:
                # 没有加入YSF,DLR,QSF筛选
                DSR_txt = subnode.get('value')
                # print('当事人信息')
                # print(DSR_txt)
                index_DSR = [-1 for i in range(8)]
                # if re.search(r'(男|女)',DSR_txt):
                #     index_DSR [2] = re.search(r'(男|女)',DSR_txt).start()
                for i in range(len(subnode)):
                    # 诉讼身份
                    if subnode[i].tag == 'SSSF':
                        if subnode[i].get('value') == '委托代理人':
                            wenshu_corr['首部'].append('委托代理人应更改为委托诉讼代理人')
                            res_score -= cf.acc_CSR_subscore2
                        index_DSR[0] = DSR_txt.index(subnode[i].get('value'))
                    # 诉讼参与人
                    elif subnode[i].tag == 'SSCYR':
                        index_DSR[1] = DSR_txt.index(subnode[i].get('value'))
                    # 单位职务分组
                    elif subnode[i].tag == 'DWZWFZ':
                        for tmp in subnode[i]:
                            if tmp.tag == 'ZW' and tmp.get('value') == '律师':
                                wenshu_corr['首部'].append('律师应更改为法律工作者')
                                res_score -= cf.acc_CSR_subscore2
                    elif subnode[i].tag == 'XB':
                        index_DSR[2] = re.search(r'(男|女)', DSR_txt).start()
                    elif subnode[i].tag == 'CSRQ':
                        try:
                            index_DSR[3] = DSR_txt.index(subnode[i].get('value'))
                        except ValueError as e:
                            print(e)
                # 检测顺序
                lis_index = lis(index_DSR)
                error_txt = []
                for i in range(4):
                    if index_DSR[i] == -1:
                        error_txt.append(standard_DSR[i])
                    if index_DSR[i] != -1 and (index_DSR[i] not in lis_index):
                        wenshu_corr['首部'].append(
                            '当事人信息“' + DSR_txt + '”中' + standard_DSR[i] + '顺序错误，应该按照，诉讼身份，姓名，性别，出生年月日顺序书写')
                        res_score -= cf.acc_CSR_subscore2
                if error_txt != '':
                    wenshu_corr['首部'].append('当事人信息“' + DSR_txt + '”中缺少' + (','.join(error_txt)))
                    res_score -= cf.acc_CSR_subscore1
        break
    res_score += cf.acc_CSR_score
    if res_score < 0:
        res_score = 0
    return res_score, wenshu_corr


# acc_SLJG(wenshu, wenshu_corr)

# acc_DSR(wenshu,wenshu_corr)


# 事实描述简明性
# 对于过长的段落应该提示读者不应过长，但是怎么设定阈值未知
def con_pun_YGSCD(YGSCD_txt, wenshu_corr):
    res_score = 0
    pun_mao = [i.end() for i in re.finditer(r'.*原告[\u4e00-\u9fa5]{0,4}(向本院提出)*诉讼请求*(如下)*', YGSCD_txt)]
    for i in pun_mao:
        if YGSCD_txt[i] != '：':
            wenshu_corr['事实'].append('标点符号：原告诉讼请求后应为冒号')
            res_score -= 1
    return res_score, wenshu_corr


def con_pun_BGBCD(BGBCD_txt, wenshu_corr):
    res_score = 0
    pun_mao = [i.end() for i in re.finditer(r'.*被告[\u4e00-\u9fa5]{0,4}辩称(如下)*', BGBCD_txt)]
    for i in pun_mao:
        if BGBCD_txt[i] != '，':
            wenshu_corr['事实'].append('标点符号：被告辩称后应为逗号')
            res_score -= 1
    return res_score, wenshu_corr


def con_pun_CMSSD(CMSSD_txt, wenshu_corr):
    res_score = 0
    pun_mao = [i.end() for i in re.finditer(r'.*本院认定(如下)*', CMSSD_txt)]
    for i in pun_mao:
        if CMSSD_txt[i] != '：':
            wenshu_corr['事实'].append('标点符号：本院认定后应为冒号')
            res_score -= 1
    return res_score, wenshu_corr


def con_pun(wenshu, wenshu_corr):
    res_score = 0
    AJJBQK = wenshu['事实'][0]
    for node in AJJBQK:
        # 原告诉称段
        if node.tag == 'YGSCD':
            YGSCD_txt = node.get('value')
            tmp_score, wenshu_corr = con_pun_YGSCD(YGSCD_txt, wenshu_corr)
            res_score += tmp_score
        # 被告辩称段
        elif node.tag == 'BGBCD':
            BGBCD_txt = node.get('value')
            tmp_score, wenshu_corr = con_pun_BGBCD(BGBCD_txt, wenshu_corr)
            res_score += tmp_score
        # 查明事实段
        elif node.tag == 'CMSSD':
            CMSSD_txt = node.get('value')
            tmp_score, wenshu_corr = con_pun_CMSSD(CMSSD_txt, wenshu_corr)
            res_score += tmp_score
    if len(wenshu['理由'])!=0:
        CPFXGC_txt = wenshu['理由'][0].get('value')
        tmp_score, wenshu_corr = con_pun_CPFXGC(CPFXGC_txt, wenshu_corr)
        res_score += tmp_score
    PJJG_node = wenshu['主文'][0]
    PJJG_txt = PJJG_node.get('value')
    tmp_score, wenshu_corr = con_pun_PJJG(PJJG_txt, wenshu_corr)
    res_score += tmp_score
    for node in wenshu['首部']:
        if node.tag == 'DSR':
            for subnode in node:
                # 没有加入YSF,DLR,QSF筛选
                DSR_txt = subnode.get('value')
                tmp_score, wenshu_corr = con_pun_DSR(DSR_txt, wenshu_corr)
                res_score += tmp_score
    res_score = res_score + cf.con_pun_score
    if res_score < 0:
        res_score = 0
    return res_score, wenshu_corr


def con_num(wenshu, wenshu_corr):
    res_score = 0
    if len(wenshu['落款']) == 0:
        return cf.con_num_score, wenshu_corr
    else:
        WW_txt = wenshu['落款'][0].get('value')
        if re.search(r'[0-9]', WW_txt):
            res_score -= cf.con_num_subscore
            wenshu_corr['落款'].append('数字使用一致性：落款时间应为大写')
        res_score += cf.con_num_score
        if res_score < 0:
            res_score = 0
        return res_score, wenshu_corr


def rea_SSMS(wenshu, wenshu_corr):
    res_score = 1
    # 案件基本情况
    AJJBQK = wenshu['事实'][0]
    YGSCD_len, BGBCD_len, CMSSD_len, ZJD_len = 0, 0, 0, 0
    for node in AJJBQK:
        # 原告诉称段
        if node.tag == 'YGSCD':
            YGSCD_txt = node.get('value')
            YGSCD_len = len(YGSCD_txt)
        # 被告辩称段
        elif node.tag == 'BGBCD':
            BGBCD_txt = node.get('value')
            BGBCD_len = len(BGBCD_txt)
        # 查明事实段
        elif node.tag == 'CMSSD':
            CMSSD_txt = node.get('value')
            CMSSD_len = len(CMSSD_txt)
        # 证据段
        elif node.tag == 'ZJD':
            ZJD_txt = node.get('value')
            ZJD_len = len(ZJD_txt)
    if YGSCD_len != 0 and YGSCD_len < cf.rea_YGSCD_threshold:
        res_score += cf.rea_SSMS_subscore
    if BGBCD_len != 0 and BGBCD_len < cf.rea_BGBCD_threshold:
        res_score += cf.rea_SSMS_subscore
    if CMSSD_len != 0 and CMSSD_len < cf.rea_CMSSD_threshold:
        res_score += cf.rea_SSMS_subscore
    if ZJD_len != 0 and ZJD_len < cf.rea_ZJD_threshold:
        res_score += cf.rea_SSMS_subscore
    return res_score, wenshu_corr


# rea_SSMS(wenshu)
def con_pun_CPFXGC(CPFXGC_txt, wenshu_corr):
    res_score = 0
    if '本院认为' in CPFXGC_txt:
        if CPFXGC_txt[CPFXGC_txt.index('本院认为') + 4] != '，':
            wenshu_corr['理由'].append('标点符号：本院认为后应该为逗号')
            res_score -= 1
    return res_score, wenshu_corr


# 争议焦点条理性
def rea_ZYJD(wenshu, wenshu_corr):
    res_score = 0
    SSJL_txt = ''
    if len(wenshu['首部']) != 0:
        for node in wenshu['首部']:
            if node.tag == 'SSJL':
                SSJL_txt = node.get('value')
                break
        if '简易程序' in SSJL_txt:
            wenshu_corr['理由'].append('简易程序不需要争议焦点检测')
            res_score += cf.rea_ZYJD_score
            return res_score, wenshu_corr
    if len(wenshu['理由']) == 0:
        return res_score, wenshu_corr
    CPFXGC_txt = wenshu['理由'][0].get('value')
    if not re.match(r'.*(争议焦点|本案焦点|焦点).*', CPFXGC_txt):
        wenshu_corr['理由'].append('未归纳案件争议焦点')
    else:
        res_score += cf.rea_ZYJD_score
    return res_score, wenshu_corr


# rea_ZYJD(wenshu, wenshu_corr)
# 判断判决内容中标点符号使用一致性
def con_pun_PJJG(PJJG_txt, wenshu_corr):
    res_score = 0
    # 返回所有匹配的位置
    print('判决结果')
    print(PJJG_txt)
    print(wenshu_corr)
    punc_mao = [i.start() for i in re.finditer(r'(判决|裁定)如下', PJJG_txt)]
    for punc in punc_mao:
        if PJJG_txt[punc + 4] != '：':
            wenshu_corr['主文'].append('标点错误：判决（裁定）如下后应该使用冒号')
            res_score -= 1
    punc_fen = [i.start() for i in re.finditer(r'(二|三|四|五|六|七|八|九|十)、', PJJG_txt)]
    print('分号位置:' + str(punc_fen))
    for punc in punc_fen:
        if PJJG_txt[punc - 1] != '；':
            wenshu_corr['主文'].append('标点错误：分项之前应该使用分号')
            res_score -= 1
    punc_dun = [i.start() for i in re.finditer(r'(一|二|三|四|五|六|七|八|九|十)[^\w\u4e00-\u9fa5]+', PJJG_txt)]
    for punc in punc_dun:
        if PJJG_txt[punc + 1] != '、':
            wenshu_corr['主文'].append('标点错误：分项之后应该用顿号')
            res_score -= 1

    return res_score, wenshu_corr


# 判决内容说明完整性
def com_PJNR(wenshu, wenshu_corr):
    # 判决金额，判决执行期限
    res_score = 0
    standard_PJNR = ['数量', '金额类型', '判决执行期限', '义务人']
    if len(wenshu['主文']) != 0:
        PJJG_node = wenshu['主文'][0]
        PJJG_txt = PJJG_node.get('value')
        # 判决结果中包不包含金额
        flag_ = 0
        for node in PJJG_node:
            # 判决结果内容
            if node.tag == 'PJJGNR':
                # 判决结果内容是不是涉及金额
                flag = 0
                PJJGNR_txt = node.get('value')
                print(PJJGNR_txt)
                index_PJNR = [-1 for i in range(4)]
                for subnode in node:
                    if subnode.tag == 'PJJE':
                        for i in range(len(subnode)):
                            if subnode[i].tag == 'JE':
                                # print('jine')
                                index_PJNR[0] = 1
                            elif subnode[i].tag == 'JELX':
                                index_PJNR[1] = 1
                        flag = 1
                        flag_ = 1
                    if flag == 1 and subnode.tag == 'PJZXQX':
                        index_PJNR[2] = 1
                    if flag == 1 and subnode.tag == 'YWR':
                        index_PJNR[3] = 1
                if flag == 1:
                    print(index_PJNR)
                    for i in range(4):
                        if index_PJNR[i] == -1:
                            wenshu_corr['主文'].append('判决内容说明完整性' + PJJGNR_txt + '中缺少' + standard_PJNR[i])
                            res_score-=1
        if flag_ == 1 and not (
                re.match(r'.*应当按照《中华人民共和国民事诉讼法》第二百五十三条的规定，加倍支付延迟履行期间的债务利息.*', PJJG_txt)):
            wenshu_corr['主文'].append('判决结果告知缺失')
            res_score-=2
        res_score += cf.com_PJNR_score
        if res_score<0:
            res_score = 0
        return res_score, wenshu_corr
    else:
        return res_score, wenshu_corr


# com_PJNR(wenshu, wenshu_corr)
# 诉费承担完整性
def com_SFCD(wenshu, wenshu_corr):
    res_score = 0
    if len(wenshu['尾部']) == 0:
        return res_score, wenshu_corr
    SSFCD_node = wenshu['尾部'][0]
    # 是否多人承担诉讼费用
    count = 0
    # 诉讼费金额
    ssf_sum = 0
    ssf_item = 0
    for node in SSFCD_node:
        if node.tag == 'SSFCDJL':
            for subnode in node:
                # 诉讼费总金额
                if subnode.tag == 'SSFZJE':
                    ssf_sum = float(subnode.get('value').split('元')[0])
                if subnode.tag == 'SSFCDFZ':
                    # 承担人
                    for ssubnode in subnode:
                        if ssubnode.tag == 'CDR':
                            count += 1
                            for sssubnode in ssubnode:
                                if sssubnode.tag == 'CDJE':
                                    ssf_item += float(sssubnode.get('value').split('元')[0])
    if count > 1 and ssf_sum != ssf_item:
        wenshu_corr['主文'].append('诉费承担完整性：未分别说明承担人各自承担金额')
        return 1, wenshu_corr
    else:
        return cf.com_SFCD_score, wenshu_corr


# com_SFCD(wenshu, wenshu_corr)
# 加载案由列表
def load_ay():
    # 处理得到案由列表
    # ay_file = open('D:/NJU/final_project/data/anyou.txt', 'r', encoding='utf-8')
    # ay_out = open('D:/NJU/final_project/data/AY.txt', 'w', encoding='utf-8')
    # for line in ay_file.readlines():
    #     if '、' in line:
    #         ay_out.write(''.join(line.split('、',1)[1]))
    #     else:
    #         ay_out.write(line)
    # ay_file.close()
    # ay_out.close()
    ay_file = open('D:/NJU/final_project/data/AY.txt', 'r', encoding='utf-8')
    ay_list = []
    for line in ay_file.readlines():
        ay_list.append(line.split('\n')[0])
    ay_file.close()
    # print(ay_list)
    return ay_list


anyou_list = load_ay()


# 案由信息真实性
def aut_AY(wenshu, wenshu_corr):
    res_score = 0
    ay_test = ''
    for node in wenshu['首部']:
        if node.tag == 'SSJL':
            for subnode in node:
                if subnode.tag == 'AY':
                    ay_test = subnode.get('value')
                    break
            break
    if ay_test == '':
        wenshu_corr['首部'].append('真实性：未标明案由')
    if ay_test not in anyou_list:
        wenshu_corr['首部'].append('真实性：案由不在列表中，可能为编造案由')
        res_score += 2
    else:
        res_score += 5
    return res_score, wenshu_corr


# aut_AY(root_node,wenshu_corr)
# 裁判依据引用规范

def aut_CPYJ(wenshu, wenshu_corr):
    res_score = 0
    if (len(wenshu['理由'])) == 0:
        wenshu_corr['理由'].append('缺少理由')
    else:
        CPFXGC_node = wenshu['理由'][0]
        CPFXGC_txt = CPFXGC_node.get('value')
        res_score += cf.aut_CPYJ_score
        if re.match(r'.*指导性文件.*', CPFXGC_txt):
            wenshu_corr['理由'].append('裁判依据引用规范：指导性文件不可做为判决依据')
            res_score -= 1
        if re.match(r'.*会议纪要.*', CPFXGC_txt):
            wenshu_corr['理由'].append('裁判依据引用规范：会议纪要不可做为判决依据')
            res_score -= 1
        if re.match(r'.*指导性案例.*', CPFXGC_txt):
            wenshu_corr['理由'].append('裁判依据引用规范：指导性案例不可做为判决依据')
            res_score -= 1
        if res_score < 0:
            res_score = 0

    return res_score, wenshu_corr


# 日期转换函数,返回datetime类型
def date_change(date_txt):
    fmt = '%Y年%m月%d日'
    time_tuple = time.strptime(date_txt, fmt)
    year, month, day = time_tuple[:3]
    a_date = datetime.date(year, month, day)
    return a_date


# 案件信息延迟性，案件发生到立案日期
# 受理日期到结案日期
def del_date(root_node, wenshu_corr):
    date_dic = {'案件发生时间': '', '案件受理时间': '', '案件结案时间': ''}
    res = {'案件信息延迟性': -1, '文书信息延迟性': -1}
    date_list = []
    del_date_score = 0
    for node in root_node:
        if node.tag == 'SSJL':
            for subnode in node:
                if subnode.tag == 'SLRQ':
                    SLRQ_txt = subnode.get('value')
                    if re.match(r'[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日', SLRQ_txt):
                        date_dic['案件受理时间'] = date_change(SLRQ_txt)
                    break
        if node.tag == 'WW':
            for subnode in node:
                if subnode.tag == 'CPSJ':
                    for subsubnode in subnode:
                        if subsubnode.tag == 'CUS_JANYR':
                            JARQ_txt = subnode.get('value')
                            if re.match(r'[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日', JARQ_txt):
                                date_dic['案件结案时间'] = date_change(JARQ_txt)
                    break
        if node.tag == 'CUS_SJ':
            for subnode in node:
                if subnode.tag == 'CUS_JTSJ':
                    tmp_date_txt = subnode.get('value')
                    if re.match(r'[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日', tmp_date_txt):
                        date_list.append(date_change(tmp_date_txt))
    if len(date_list) != 0:
        date_dic['案件发生时间'] = min(date_list)
    if date_dic['案件受理时间'] == '':
        wenshu_corr['其他']['延迟性'] = '缺少案件受理时间'
    if date_dic['案件结案时间'] == '':
        wenshu_corr['其他']['延迟性'] = '缺少案件结案时间'
    if date_dic['案件受理时间'] != '' and date_dic['案件发生时间'] != '':
        Expenses_days = (date_dic['案件受理时间'] - date_dic['案件发生时间'])
        del1 = Expenses_days.days
        if (1 < del1 < 10000):
            if del1 < cf.del_date_AJXX_threshold1:
                del_date_score += cf.del_date_subsocre1
            elif del1 < cf.del_date_AJXX_threshold2:
                del_date_score += cf.del_date_subscore2
            else:
                del_date_score += cf.del_date_subscore3
        else:
            wenshu_corr['其他']['延迟性'] = '案发时间到受理时间过长，识别失败，受理时间为' + str(date_dic['案件受理时间']) \
                                       + '案件发生时间为' + str(date_dic['案件发生时间'])
    if date_dic['案件结案时间'] != '' and date_dic['案件受理时间'] != '':
        Expenses_days_ = (date_dic['案件结案时间'] - date_dic['案件受理时间'])
        del2 = Expenses_days_.days
        if (1 < del2 < 10000):
            if del2 < cf.del_date_WSXX_threshold1:
                del_date_score += cf.del_date_subsocre1
            elif del2 < cf.del_date_WSXX_threshold2:
                del_date_score += cf.del_date_subscore2
            else:
                del_date_score += cf.del_date_subscore3
        else:
            wenshu_corr['其他']['延迟性'] = '受理时间到结案时间，识别失败，受理时间为' + str(date_dic['案件受理时间']) \
                                       + '结案时间为' + str(date_dic['案件结案时间'])

    return del_date_score, wenshu_corr


# del_date(root_node, wenshu_corr)
# 遍历所有的节点
def walkData(root_node, level, result_list):
    temp_list = [level, root_node.tag, root_node.attrib]
    result_list.append(temp_list)

    # 遍历每个子节点
    children_node = list(root_node)
    if len(children_node) == 0:
        return result_list
    for child in children_node:
        walkData(child, level + 1, result_list)
    return result_list


def met_CSR(wenshu, wenshu_corr):
    res_score = 0
    for node in wenshu['首部']:
        if node.tag == 'DSR':
            CSR_count = []
            for subnode in node:
                if subnode.tag == 'DLR' or subnode.tag == 'QSF' or subnode.tag == 'YSF':
                    result_list = []
                    level = 1
                    result_list = walkData(subnode, level, result_list)
                    CSR_count.append(len(result_list))
    if len(CSR_count) == 0:
        wenshu['首部'].append('未检测到当事人')
    else:
        count = 0
        for i in CSR_count:
            if i > cf.met_CSR_threshold:
                count += 1
        res_score += cf.met_subscore * (count / len(CSR_count))
    return res_score, wenshu_corr


# met_CSRXX(root_node,wenshu_corr)
# 事实描述部分细致性
def met_AJJBQK(wenshu, wenshu_corr):
    res_score = 1
    if len(wenshu['事实']) != 0:
        root = wenshu['事实'][0]
        result_list = []
        level = 1
        result_list = walkData(root, level, result_list)
        AJJBQK_count = len(result_list)
        if AJJBQK_count > cf.met_AJJBQK_threshold:
            res_score = cf.met_subscore
    else:
        wenshu_corr['事实'].append('未检测到案件基本情况')
    return res_score, wenshu_corr


# 理由部分细致性

def met_CPFXGC(wenshu, wenshu_corr):
    res_score = 0
    if len(wenshu['理由']) != 0:
        root = wenshu['理由'][0]
        result_list = []
        level = 1
        result_list = walkData(root, level, result_list)
        CPFXGC_count = len(result_list)
        if CPFXGC_count > cf.met_CPFXGC_threshold:
            res_score += cf.met_subscore
        # print(CPFXGC_count)
    else:
        wenshu_corr['理由'].append('未检测到裁判分析过程')
    return res_score, wenshu_corr


# met_AJJBQK(wenshu,wenshu_corr)
#
# met_CPFXGC(wenshu,wenshu_corr)

def baba(filepath):
    xml_file = etree.parse(filepath)
    root_node = xml_file.getroot()[0]
    # wenshu_content = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '其他': []}
    wenshu_corr = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '附件': [], '其他': []}
    wenshu, index = wenshu_analysis(root_node)
    res, wenshu_corr = acc_GCSX(index, wenshu_corr)
    print('yeyzaizhe 111111')
    print(wenshu_corr)
    if len(wenshu['首部']) != 0:
        wenshu_corr = acc_CSR(wenshu, wenshu_corr)
        print('yeyzaizhe 2222222211111')
        print(wenshu_corr)
        wenshu_corr = acc_SLJG(wenshu, wenshu_corr)
        print('yeyzaizhe333333333')
        print(wenshu_corr)
    if len(wenshu['事实']) != 0:
        AJJBQK_len, YGSCD_len, BGBCD_len, CMSSD_len, ZJD_len = rea_SSMS(wenshu)
        print('yeyzaizhe 44444444')
        print(wenshu_corr)
    if len(wenshu['理由']) != 0:
        CPFXGC_count = met_CPFXGC(wenshu)
        wenshu_corr = rea_ZYJD(wenshu, wenshu_corr)
        print('yeyzaizhe 5555555')
        print(wenshu_corr)
        wenshu_corr = aut_CPYJ(wenshu, wenshu_corr)
        print('yeyzaizhe 566666666666')
        print(wenshu_corr)
    if len(wenshu['主文']) != 0:
        wenshu_corr = com_PJNR(wenshu, wenshu_corr)
        print('babazaizhe 777777777777777a')
        print(wenshu_corr)
    if len(wenshu['尾部']) != 0:
        wenshu_corr = com_SFCD(wenshu, wenshu_corr)
        print('babazaizhe 8888888888888888')
        print(wenshu_corr)

    wenshu_corr = aut_AY(root_node, wenshu_corr)
    date_AJFS, date_SLRQ, date_JARQ = del_date(root_node)
    AJJBQK_count = met_AJJBQK(wenshu)
    CSR_count = met_CSR(root_node)
    print('文书解析内容')
    print(wenshu)
    print('错误提醒')
    print(wenshu_corr)
    print('延迟性')
    print('时间间隔' + str(date_AJFS), str(date_SLRQ), str(date_JARQ))
    print('细致性\n' + '裁判分析过程细致性：' + str(CPFXGC_count) + '案件基本情况细致性：' + str(AJJBQK_count) + '参诉人细致性：' + str(CSR_count))
    print('简明性' + str(AJJBQK_len), str(YGSCD_len), str(BGBCD_len), str(CMSSD_len), str(ZJD_len))
    wenshu_corr['延迟性'] = [str(date_AJFS), str(date_SLRQ), str(date_JARQ)]
    wenshu_corr['细致性'] = [CPFXGC_count, AJJBQK_count, CSR_count]
    wenshu_corr['简明性'] = [AJJBQK_len, YGSCD_len, BGBCD_len, CMSSD_len, ZJD_len]
    outfile = '../../report/test.json'
    with open(outfile, 'w', encoding='utf-8') as f:
        json.dump(wenshu_corr, f, ensure_ascii=False)


# filepath 待测文书路径
# index_dic 要检测指标，字典类型

names = locals()


def get_wenshu_content(wenshu):
    wenshu_content = {'文首': '', "首部": '', "事实": '', "理由": '', "主文": '', '落款': ''}
    for i in wenshu_content:
        if len(wenshu[i]) != 0:
            for node_i in range(len(wenshu[i])):
                wenshu_content[i] += wenshu[i][node_i].get('value') + '\n'
    wenshu['其他'] = '其他意见'
    return wenshu_content


# filepath: 文书路径
# object_list:使用到的客观指标列表
# wenshu_corr：文书修改建议字典

def objective_measure(filepath, object_list, wenshu_corr):
    object_score = 0
    object_score_dict = {}
    xml_file = etree.parse(filepath)
    root_node = xml_file.getroot()[0]
    wenshu, index = wenshu_analysis(root_node)
    wenshu_content = get_wenshu_content(wenshu)
    res = []
    index_res = []
    for index_name in object_index.keys():
        if index_name in object_list and index_name != 'del_date' and index_name != 'acc_GCSX':
            tmp_score, wenshu_corr = globals().get('%s' % index_name)(wenshu, wenshu_corr)
            print(tmp_score)
            object_score_dict[index_name] = [tmp_score, names[index_name + '_score']]
            res.append(tmp_score)
            object_score += tmp_score
        elif index_name == 'del_date' and index_name in object_list:
            tmp_score, wenshu_corr = globals().get('%s' % index_name)(root_node, wenshu_corr)
            object_score += tmp_score
            object_score_dict[index_name] = [tmp_score, names[index_name + '_score']]
            res.append(tmp_score)
        elif index_name == 'acc_GCSX' and index_name in object_list:
            tmp_score, wenshu_corr, index_res = globals().get('%s' % index_name)(index, wenshu_corr)
            object_score += tmp_score
            object_score_dict[index_name] = [tmp_score, names[index_name + '_score']]
            res.append(tmp_score)
        else:
            tmp_score = names[index_name + '_score']
            object_score += tmp_score
            res.append(tmp_score)
    print(object_score)
    # object_score客观总分
    # wenshu_corr文书每一段的详细错误说明
    # wenshu_content 文书每一段落内容
    # object_score_dict每个指标的具体得分
    # index_res篇章完整性结果
    return object_score, wenshu_corr, object_score_dict, wenshu_content, index_res

def objective_measure1(filepath, object_list, wenshu_corr):
    object_score = 0
    object_score_dict = {}
    xml_file = etree.parse(filepath)
    root_node = xml_file.getroot()[0]
    wenshu, index = wenshu_analysis(root_node)
    wenshu_content = get_wenshu_content(wenshu)
    res = []
    index_res = []
    for index_name in object_index.keys():
        if index_name in object_list and index_name != 'del_date' and index_name != 'acc_GCSX':
            tmp_score, wenshu_corr = globals().get('%s' % index_name)(wenshu, wenshu_corr)
            print(tmp_score)
            object_score_dict[index_name] = [tmp_score, names[index_name + '_score']]
            res.append(tmp_score)
            object_score += tmp_score
        elif index_name == 'del_date' and index_name in object_list:
            tmp_score, wenshu_corr = globals().get('%s' % index_name)(root_node, wenshu_corr)
            object_score += tmp_score
            object_score_dict[index_name] = [tmp_score, names[index_name + '_score']]
            res.append(tmp_score)
        elif index_name == 'acc_GCSX' and index_name in object_list:
            tmp_score, wenshu_corr, index_res = globals().get('%s' % index_name)(index, wenshu_corr)
            object_score += tmp_score
            object_score_dict[index_name] = [tmp_score, names[index_name + '_score']]
            res.append(tmp_score)
        else:
            tmp_score = names[index_name + '_score']
            object_score += tmp_score
            res.append(tmp_score)
    print(object_score)
    # object_score客观总分
    # wenshu_corr文书每一段的详细错误说明
    # wenshu_content 文书每一段落内容
    # object_score_dict每个指标的具体得分
    # index_res篇章完整性结果
    return object_score, wenshu_corr, object_score_dict, wenshu_content, index_res,res


# if __name__ == '__main__':
#     filepath = 'D:/NJU/final_project/data/example/0.xml'
#     xml_file = etree.parse(filepath)
#     root_node = xml_file.getroot()[0]
#     # del_date(root_node)
#     # met_CSR(root_node)
#     wenshu_corr = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '附件': [], '其他': {}}
#     wenshu, index = wenshu_analysis(root_node)
# 单个函数测试
# aut_AY(root_node,wenshu_corr)
# aut_CPYJ(wenshu,wenshu_corr)
# con_pun(wenshu,wenshu_corr)
# rea_ZYJD(wenshu,wenshu_corr)
# acc_GCSX(index,wenshu_corr)
# acc_SLJG(wenshu,wenshu_corr)
# acc_CSR(wenshu,wenshu_corr)
# rea_SSMS(wenshu)
# index_dic = {
#     "met_CSR_": 1,
#     "met_AJJBQK_": 1,
#     "met_CPFXGC_": 1,
#     "del_date_": 1,
#     "aut_AY_": 1,
#     "aut_CPYJ_": 1,
#     "com_PJNR_": 1,
#     "com_SFCD_": 1,
#     "con_num_": 1,
#     "con_pun_": 1,
#     "rea_SSMS_": 1,
#     "rea_ZYJD_": 1,
#     "acc_GCSX_": 1,
#     "acc_SLJG_": 1,
#     "acc_CSR_": 1,
# }
# object_index = {
#     "met_CSR_": 1,
#     "met_AJJBQK_": 1,
#     "met_CPFXGC_": 1,
#     "del_date_": 1,
#     "aut_AY_": 1,
#     "aut_CPYJ_": 1,
#     "com_PJNR_": 1,
#     "com_SFCD_": 1,
#     "con_num_": 1,
#     "con_pun_": 1,
#     "rea_SSMS_": 1,
#     "rea_ZYJD_": 1,
#     "acc_GCSX_": 1,
#     "acc_SLJG_": 1,
#     "acc_CSR_": 1}

def test_object_time():
    # 100篇文章测试
    object_list = ["met_CSR",
                   "met_AJJBQK",
                   "met_CPFXGC",
                   "del_date",
                   "aut_AY",
                   "aut_CPYJ",
                   "com_PJNR",
                   "com_SFCD",
                   "con_num",
                   "con_pun",
                   "rea_SSMS",
                   "rea_ZYJD",
                   "acc_GCSX",
                   "acc_SLJG",
                   "acc_CSR"]
    path_file = open('G:/judicial_data/民事一审案件.tar/民事一审案件/path_min_pan_filter_len.txt', 'r', encoding='utf-8')
    res_file = open('../../data/object_tmp.csv', 'w', encoding='utf-8')
    time_file = open('../../data/object_time_tmp.csv', 'w', encoding='utf-8')
    count = 0
    tmp = []
    time_res = []
    for path in path_file.readlines():
        time_start = time.time()
        count += 1
        if count > 100:
            break
        path = 'G:/judicial_data/民事一审案件.tar/民事一审案件/msys_all/' + path.strip()
        print('待检测文书名称为：' + path)
        wenshu_corr = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '附件': [],
                       '其他': {}}
        object_score, wenshu_corr, object_score_dic, wenshu_content, index_res, res = objective_measure1(path,
                                                                                                        object_list,
                                                                                                        wenshu_corr)
        print(object_score)
        # tmp.append(res)
        res.append(str(object_score))
        res.append(path.split('/')[-1])
        res.append(str(object_score_dic))
        res_file.write('\t'.join(str(res)) + '\n')
        time_end = time.time()
        cost = time_end - time_start
        time_res.append(cost)
        # time_file.write(str(cost)+'\n')
    # c = np.array(tmp)
    # mean = c.mean(axis=0)
    # max = c.max(axis=0)
    # min = c.min(axis=0)
    # std = c.std(axis=0)
    # print(mean)
    # print(min)
    # print(max)
    # print(std)
    # print(time_res)

#
if __name__ == '__main__':
    test_object_time()
# object_score, wenshu_corr, object_score_dic, wenshu_content, index_res = objective_measure(filepath, index_dic,
#                                                                                            object_index,
#                                                                                            wenshu_corr)
