# -*- coding: utf-8 -*-  
import os,os.path  
import pefile  
def parsePe(filePath,dllDict):  
    pe = pefile.PE(filePath)  
    for importeddll in pe.DIRECTORY_ENTRY_IMPORT:  
        #print '----------------'+importeddll.dll+'--------------------------'  
        dllDict[importeddll.dll]=None  
        num=0  
        funcList=list()  
        for importedapi in importeddll.imports:  
            num+=1  
            funcList.append(importedapi.name)  
            #print importedapi.name  
        dllDict[importeddll.dll]=funcList  
def traversalFiles(filePath,dllDict):  
    #print filePath  
    if os.path.isfile(filePath):  
        if os.path.basename(filePath).endswith('.exe'):  
            #print filePath  
            parsePe(filePath,dllDict)  
    else:  
        for item in os.listdir(filePath):  
            #print item  
            subpath = filePath+os.path.sep+item  
            traversalFiles(subpath,dllDict)  
def main():  
    dirPath=raw_input("input the dir or file of PE_file address=>")  
    importDllDic=dict();  
    while True:  
        if os.path.isdir(dirPath)==False and os.path.isfile(dirPath)==False:  
            dirPath=raw_input("the dir that you input is empty,please input again=>")  
            continue  
        else:  
            break  
    #destDirPath = u'F:\\Ω‚ŒˆPE'  
    traversalFiles(dirPath,importDllDic)  
    for key in importDllDic:  
        print '\n'+key,importDllDic[key]  
if __name__=='__main__':  
    main()  