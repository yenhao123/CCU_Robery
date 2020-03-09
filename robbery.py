#!/usr/bin/env python
# coding: utf-8

# In[24]:


import requests
import os
import re
import time
import prettytable as pt
from bs4 import BeautifulSoup

#搶課機器人(博雅通識) : 網頁架構變動的情況下,程序可能失效。

#登錄
userid = '407410044'
userpwd = '2201726'

def login():    
  url = 'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/bookmark.php'  
  params = {'id': userid,'password' : userpwd}
  res = requests.post(url , params)
  res.encoding = res.apparent_encoding
  tmp=re.findall('Add_Course00.cgi?.*' , res.text)[0]
  print(tmp)
  session_id = re.findall('Add_Course00.cgi?.*' , res.text)[0][28:-3]
  return session_id

#選擇課程
def selectCourse(session_id , dept , grade , cge_cate , cge_subcate , course_id , course_cate , done):
  
  if course_id in done:
    return None
  data = {
    'session_id': session_id,
    'dept': dept, 
    'grade': grade, 
    'cge_cate': cge_cate,
    'cge_subcate': cge_subcate, 
    'course': course_id,
    course_id : course_cate,
    'SelectTag': '1', 
  }
  #post will submit i dont understand
  text = requests.post(f'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi',data)
  text.encoding = text.apparent_encoding 
  return text

#課程搜尋
def searchCourse(session_id , dept , grade , cge_cate , cge_subcate , clist , others):
    page = 0  
    data = {
        'session_id' : session_id,
        'dept': dept,
        'grade': grade,
        'cge_cate': cge_cate,
        'cge_subcate': cge_subcate,
        'page':str(page)
    }
    text = requests.post(f'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi',data)
    text.encoding = text.apparent_encoding
    soup = BeautifulSoup(text.text , 'html.parser')
    #爬取頁數
    try:
      totalPages = int(soup.find('form' , {'name':'NextForm'}).findAll('a')[-1].text.split(' ')[1])
    except:
      totalPages = 1

    for page in range(totalPages):
      text = requests.get(f'https://kiki.ccu.edu.tw/~ccmisp06/cgi-bin/class_new/Add_Course01.cgi?session_id={session_id}&use_cge_new_cate=1&m=0&dept={dept}&grade={grade}&page={page+1}&cge_cate={cge_cate}&cge_subcate={cge_subcate}')
      text.encoding = text.apparent_encoding
      soup = BeautifulSoup(text.text , 'html.parser')
      #find all course
      textList = soup.find('form' , {'action':'Add_Course01.cgi'}).find('table').find('tr').findAll('tr')[1:]
      for text in textList:
        try:
          courseinfo = text.findAll('th')
          courseid = courseinfo[0].input.attrs['value']
          current = courseinfo[1].text
          remaining = courseinfo[2].text
          course = courseinfo[3].text
          teacher = courseinfo[4].text
          credit = courseinfo[6].text
          time = courseinfo[8].text
          classroom = courseinfo[9]
        except:
            continue
        if int(remaining) != 0:
          clist.append((course , courseid , current , remaining , credit , cge_subcate,time))
        else:
          others.append((course , courseid , current , remaining , credit , cge_subcate,time))

if __name__ == '__main__':
    
    time_inv = 0
    done = []
    
    while(time_inv < 5):
        
        time1 = time.time()
        
        #login
        session_id=login()
        
        #通識課程參數
        dept = 'I001'
        grade = '1'
        cge_cate = '2'
        cge_subcate = ['0' , '1' , '2' , '3' , '4' , '5' , '6']
        course_cate = '3'
        
        #爬取所有博雅通識課程訊息
        clist = []
        others = []
        for subcate in cge_subcate:
            searchCourse(session_id  , dept , grade , cge_cate , subcate , clist , others)
            clist.sort(key = lambda x : int(x[3]))
        
        #鎖定需要課程
        tb = pt.PrettyTable()
        tb.field_names = ['剩餘名額' , '課程名稱' , '課程編號' , '目前選修人數' , '學分數' , '通識類別' , '時間']
        #1.探索音樂治療['7304038_01']、影像美學['7304041_01'],心理學在社區服務應用['7401017_01']
        focus=['7304038_01' , '7304041_01','7401017_01']
        for i in range(len(clist)):
            if clist[i][1] in focus:
                tb.add_row([clist[i][3] , clist[i][0] , clist[i][1] , clist[i][2] , clist[i][4] , clist[i][5] , clist[i][6]])
                text=selectCourse(session_id , dept , grade , cge_cate , clist[i][5] , clist[i][1] , course_cate , done)
                if text != None:
                    done.append(focus[0])
                    
        for i in range(len(others)):
            if others[i][1] in focus:
                tb.add_row([others[i][3] , others[i][0] , others[i][1] , others[i][2] , others[i][4] , others[i][5] , others[i][6]])
        
        #關注列表
        print(tb)
        
        #已提交選課表
        print("已繳交提交表單選課")
        for i in range(len(done)):
            print(done[i])
        
        time2 = time.time()
        time_inv = time2 - time1


# In[ ]:




