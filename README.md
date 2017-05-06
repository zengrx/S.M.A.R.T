#MalwareScan
#恶意文件分析工具
--------
- MalwareScan是一个静态恶意文件分析工具，目前正在整合SSMA代码
- 预计完成时包括
扫描模块，检查模块，分类模块及网络模块        
具备全盘扫描，快速扫描，pe文件分析，可疑脚本分析，上传可疑文件样本等功能         
使用clamav和yara进行扫描及样本匹配，样本可上传至viurstotal进行分析
- 计划使用机器学习对恶意文件进行分类，通过二进制内容转换为灰阶图像进行处理，最终生成样本矩阵
- 使用对于操作码的n元语对.asm文件进行分析

--------
- 在windows中的使用
因为需要使用magic模块，选择32位python2.7版本     
pip install python-magic     
在 http://sourceforge.NET/projects/gnuwin32/files/file/5.03/ 下载 file-5.03-setup.exe     
安装至 C:\GnuWin32     
环境变量Path里添加 C:\GnuWin32\bin      
删除 C:\GnuWin32\share\misc\magic.mgc     
python代码里使用Magic时 指明magic信息文件，否则会报错
      m = Magic(magic_file="C:\GnuWin32\share\misc", mime=False)  
      file_type = m.from_file(file_path)  
- 12月22日更新64位python2.7版本magic模块使用，win7下已验证64位可用

- 需要注意在linux版本与windows版本中编码的不同

- 目前已使用sqlite3为工程数据库，也需要注意编码问题

--------
- 发布版本    
目前使用pyinstaller发布windows64位（PE32+）版本成功
命令为 pyinstaller -w -p path/to/python27; -i path/to/main_icon.ico main.py