# -*- coding: utf-8 -*-
"""
@Title:Course.Experiment.e-commerence.CRMsystem
@Coauthor: joeyzong256@github
Created on Thu Nov 1 12:45:13 2023
"""

#配置————————————————————————————————————————————————
usesample=True #购物车使用测试数据 打开:True
searchratio=20 #匹配指数，已实现自动分配
design=10 #界面配色 0-13 推荐:10
#后端————————————————————————————————————————————————

"""
Created on Thu Nov 1 14:30:42 2023

1.货物信息表 flist=[[fnid->str,fid->str,fname->str,fprice->str]]
    √ def flist_read():#读取货物信息表，需要先运行
        #ret:[[fnid->str,fid->str,fname->str,fprice->str]]
    √ def flist_nid(nid->str):#按内部序号查找
        #ret:[fnid->str,fid->str,fname->str,fprice->str] or []
    √ def flist_id(id->str):#按实际序号查找
        #ret:[fnid->str,fid->str,fname->str,fprice->str] or []
    √ def flist_name(name->str):#按名字模糊搜索，返回多个
        #ret:list=[[fnid->str,fid->str,fname->str,fprice->str]]
        #history:def flist_name_beta1 算法优化显示顺序
2.CRM决策树 crmtree=crmtree->sklearn.tree
    √ def crmtree_read():#读取决策树 @数据端
        #ret:crmtree->sklearn.tree
"""

import csv
def flist_read():#读取货物信息表，需要先运行

    filename='foodlist2.csv'
    data = []
    with open(filename) as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        #header = next(csv_reader)        # 读取第一行每一列的标题
        for row in csv_reader:            # 将csv 文件中的数据保存到data中
            data.append(row)           # 选择某一列加入到data数组中
    i=0
    while(i<len(data)):
            if(data[i]==[]):
                del data[i]
            else: i+=1
    return data

flist=flist_read()

def flist_nid(fnid):
    for i in range(len(flist)):
        if flist[i][0] == fnid:
            return flist[i][:]
    return None

def flist_id(fid):
    for i in range(len(flist)):
        if flist[i][1] == fid:
            return flist[i][:]
    return None
 
from fuzzywuzzy import fuzz

def flist_name_beta1(name):#按名字模糊搜索，返回多个
    matches = []
    for item in flist:
        ratio = fuzz.ratio(name, item[2])#计算文本相似度
        if ratio > searchratio:#相似度
            matches.append(item)
    return matches

def flist_name(name):#按名字模糊搜索，返回多个，按相似度排列
    table = []
    for i in range(len(flist)):
        r=fuzz.ratio(name, flist[i][2])
        table.append([flist[i][0][:],r])
    table=sorted(table, key=lambda x:x[1],reverse=True)[:100]
    outputs=[]
    for i in range(len(table)):
        outputs.append(flist_nid(table[i][0]))
    return outputs

import pickle
def crmtree_read():#读取决策树 @只在数据端
        with open('tree.pkl', 'rb') as f:
            return pickle.load(f)
    
select_sheet=[[]] #[fno,fname,fnum,fprice]
search_sheet=[[]] #[fno,fname,fprice]
recommand_sheet=[[]] #[fno,fname,fprice]

#算法————————————————————————————————————————————————
"""
Created on Thu Nov 1 16:21:32 2023

1.搜索算法
    !required pack:fuzzywuzzy,
    def search(name->str):#按照输入的字符串更新搜索表
        #ret:[[fnid->str,fid->str,fname->str,fprice->str]]
2.推荐算法
    !required pack:sklearn,numpy
    !required model:tree.pkl->sklearn.tree
    def predict():#按照购物车select_sheet中的货物更新推荐表recommand_sheet
        #ret:[[fnid->str,fid->str,fname->str,fprice->str]]
        #history:def predict_beta1 算法优化,提供少元素组合推荐
"""

import numpy as np
import sklearn.tree

CRMtree=crmtree_read()

def search(name):
    search_sheet[0]=flist_name(name)
    return search_sheet[0][:]

def predict_beta1():
    def predict_one(inputs):
        inputs_=[]#生成独热编码    
        for i in range(1126):
            inputs_.append(0)
        for i in range(len(inputs)):
            inputs_[inputs[i]]=1
        inputs_=np.array(inputs_)
        X_new=np.array([inputs_])
        y_new=CRMtree.predict(X_new)#预测新样本
        X_new=X_new[0]
        outnid=str(y_new[0])
        return outnid
    
    inputs=[]
    predicts=[]
    for i in range(len(select_sheet[0])):
        inputs.append(int(select_sheet[0][i][0]))
    for i in range(10):
        p=predict_one(inputs)
        if(int(p) in inputs):
            break
        else: 
            predicts.append(flist_nid(p))
            inputs.append(int(p))
    recommand_sheet[0]=predicts
    return predicts[:]

def predict():
    
    predictset=select_sheet[0][:]
    for i in range(len(predictset)):
        predictset[i]=int(predictset[i][0])
    
    predicts=[[]]
    
    def predict_one(inputs):
        inputs_=[]#生成独热编码    
        for i in range(1126):
            inputs_.append(0)
        for i in range(len(inputs)):
            inputs_[inputs[i]]=1
        inputs_=np.array(inputs_)
        X_new=np.array([inputs_])
        y_new=CRMtree.predict(X_new)#预测新样本
        X_new=X_new[0]
        outnid=str(y_new[0])
        return outnid
    
    def predict_thorgh(inputs):
        _inputs=inputs[:]
        
        for i in range(10):
            p=int(predict_one(_inputs))
            if(((p in _inputs) or (p in predicts[0]))==False):
                predicts[0].append(int(p))
                _inputs.append(int(p))
        return predicts[0][:]
    
    if(len(select_sheet[0])>2):
        for i in range(len(predictset)):
            _inputs=predictset[:]
            del _inputs[i]
            for j in range(len(_inputs)):
                __inputs=_inputs[:]
                del __inputs[j]
                predict_thorgh(__inputs)
    else: (predict_thorgh(predictset))
    
    predicts=predicts[0]
    for i in range(len(predicts)):
        predicts[i]=flist_nid(str(predicts[i]))
    
    recommand_sheet[0]=predicts
    return predicts[:]
    

#前端——————————————————————————————————————————————————
"""
Created on Thu Nov 1 12:45:13 2023

def _update_atree_(info):#将info的显示到货架
    #info->[[fnid->str,fid->str,fname->str,fprice->str]]
def _update_ctree_(info):#将info显示到购物车
    #info->[[fnid->str,fid->str,fname->str,fprice->str]]
serv_search():#按照搜索框中的搜索并显示在货架
    #ret:None @前端 会修改 search_sheet
serv_add():#将货架选中货物加入到购物车
    #ret:None @前端 会修改 select_sheet
serv_del():#从购物车中删除选中货物
    #ret:None @前端 会修改 select_sheet
serv_recommand():#按照购物车中的货物获取推荐显示在货架
    #ret:None @前端，会修改 recommand_sheet
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tkb

#窗口设计
root = tk.Tk()
root.title("CRMsystem by 21013122,23,24") #窗口标题
root.geometry("500x350") #窗口大小
root.resizable(False, False) #窗口大小不可改变
#bs_root.config(bg="blue") #背景颜色

#界面配色
stylename=['cyborg', 'journal', 
'darkly', 'flatly', 'solar', 
'minty', 'litera', 'united', 
'pulse', 'cosmo', 'lumen', 'yeti', 
'superhero', 'sandstone']
style = tkb.Style()
style = tkb.Style(theme=stylename[design])
TOP6 = style.master

#搜索框
search_label=tk.Label(text="搜索:")
search_label.place_configure(x=10,y=10)
search_entry = tk.Entry(root,width=30)
search_entry.place_configure(x=60,y=10)

#添加表
atable=[[]]
atree = ttk.Treeview(root, columns=("fno","fname","fprice"), show="headings",height=11)  
atree.heading("fno", text="编号")  
atree.column(0, width=40)
atree.heading("fname", text="名称")
atree.column(1, width=180)
atree.heading("fprice", text="价格") 
atree.column(2, width=45)
#tree.columnconfigure(3, weight=1)
atree.place_configure(x=10,y=80)

def _update_atree_(info):
    for child in atree.get_children():
        atree.delete(child)
    for i in range(len(info)):
        row=info[i]
        atree.insert("", "end", values=row)
        
#购物车
cmenu=tk.LabelFrame(height=330,width=200,text="购物车")#菜单框架
cmenu.place(x=285,y=0)
ctree = ttk.Treeview(root, columns=("fno","fname","fnum","fprice"), show="headings",height=14)  
ctree.heading("fno", text="编号")  
ctree.column(0, width=34)
ctree.heading("fname", text="名称")
ctree.column(1, width=80)
ctree.heading("fnum", text="个数") 
ctree.column(2, width=34)
ctree.heading("fprice", text="价格") 
ctree.column(3, width=34)
#tree.columnconfigure(3, weight=1)
ctree.place_configure(x=290,y=20)

def _update_ctree_(info):
    for child in ctree.get_children():
        ctree.delete(child)
    for i in range(len(info)):
        row=info[i]
        ctree.insert("", "end", values=row[:2]+[""]+[row[-1]])

#搜索按钮
def serv_search():
    search_sheet[0]=flist_name(search_entry.get())
    atable[0]=search_sheet[0]
    rs=[]
    for i in range(len(search_sheet[0])):
        rs.append(search_sheet[0][i][1:4])
    _update_atree_(rs)
    return
search_botton = tk.Button(root, text="搜索", command=serv_search,width=7)
search_botton.place_configure(x=10,y=45)

#添加搜索到购物车按钮
def serv_add():
    selected_item = atree.selection()[0]
    item_fid = atree.item(selected_item)['values'][0]
    select_sheet[0].append(flist_id(str(item_fid)))
    rs=[]
    for i in range(len(select_sheet[0])):
        rs.append(select_sheet[0][i][1:4])
    _update_ctree_(rs)
    return
add_botton = tk.Button(root, text="添加", command=serv_add,width=7)
add_botton.place_configure(x=80,y=45)

def serv_recommand():
    atable[0]=predict()
    rs=[]
    for i in range(len(recommand_sheet[0])):
        rs.append(recommand_sheet[0][i][1:4])
    _update_atree_(rs)
    return
recommand_botton = tk.Button(root, text="推荐", command=serv_recommand,width=7)
recommand_botton.place_configure(x=220,y=45)

#从购物车删除按钮
def serv_del():
    selected_item = ctree.selection()[0]
    item_fid = ctree.item(selected_item)['values'][0]
    for i in range(len(select_sheet[0])):
        if(select_sheet[0][i][1]==str(item_fid)):
            del select_sheet[0][i]
            break
    rs=[]
    for i in range(len(select_sheet[0])):
        rs.append(select_sheet[0][i][1:4])
    _update_ctree_(rs)
    return
del_botton = tk.Button(root, text="删除", command=serv_del,width=7)
del_botton.place_configure(x=150,y=45)

#测试————————————————————————————————————————
'''
Created on Thu Nov  2 13:25:42 2023
1.测试样例 testnum 基于150层CART树 似然值/预测值
'''
usesample=usesample #购物车使用测试数据 打开:True
testnum=[[111,122,210,277,702,815,1109],
         [114,115,284,307,310,318,1073,1087,1112],
         [78,113,190,274,289,323,444,528,964,973,1005,1125],
         [324,445,624,773,782,1115,1116,1117,1122],
         [52,96,97,275,458,530,697,701,936],
         [112,122,127,438,444,497,529,724,850,865,869,987]]

covernum=3

import random
if(usesample==True):
    testset=random.choice(testnum)
    for i in range(covernum):
        covered=random.randint(0, len(testset)-1)
        label=testset[covered]
        del testset[covered]
    select_sheet=[[]] #[fno,fname,fnum,fprice]
    for i in range(len(testset)):
        select_sheet[0].append(flist_nid(str(testset[i])))
    rs=[]
    for i in range(len(select_sheet[0])):
        rs.append(select_sheet[0][i][1:4])
    _update_ctree_(rs)

#运行————————————————————————————————————————
root.mainloop()
