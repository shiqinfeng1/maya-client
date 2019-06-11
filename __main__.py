import platform
import os
from subprocess import PIPE, Popen

# mayapy安装路径
# Windows：C:\Program Files\Autodesk\<版本>\bin\mayapy.exe
# Linux（在 Shell 中）：/usr/Autodesk/<版本>/bin/mayapy
# Mac OS X（在终端中）：/Applications/Autodesk/<版本>/Maya.app/Contents/bin/mayapy

MayaVersion = []

# 找到指定路径下的第一级文件夹，并返回文件夹名字。
def traversalDir_FirstDir(path):
    list = []
    if (os.path.exists(path)):
        files = os.listdir(path)
        for file in files:
            m = os.path.join(path,file)
            if (os.path.isdir(m)):
                h = os.path.split(m)
                list.append(h[1])
        return list

# 根据当前系统类型检查mayapy的安装情况，并保存安装路径到MayaPath
def SetupMayapy():
    path=''
    sysstr = platform.system()
    if(sysstr =="Windows"):
        path = 'C:\\Program Files\\Autodesk\\'
        dirs = traversalDir_FirstDir(path)
        if dirs == []:
            print ("No Such Path or No subDir:",path)
            return False
        for mulu in dirs:
            if mulu in ['maya2016','maya2017','maya2018','maya2019','maya2020']:
                MayaVersion.append(mulu)
                os.environ['MAYA_LOCATION'] = path+mulu
                os.environ['MAYA_BIN_'+mulu] = os.environ['MAYA_LOCATION'] + '\\bin\\maya'
                os.environ['MAYA_PY_'+mulu] = os.environ['MAYA_LOCATION'] + '\\bin\\mayapy.exe'
                os.environ['MAYA_RENDER_'+mulu] = os.environ['MAYA_LOCATION'] + '\\bin\\Render.exe'

                print ("Match Maya Version In this Machine:",sysstr,". ###Current Version###:",mulu)

    elif(sysstr == "Linux"):
        path = '/usr/Autodesk/'
        dirs = traversalDir_FirstDir(path)
        if dirs == []:
            print ("No Such Path or No subDir:",path)
            return False
        for mulu in dirs:
            if mulu in ['maya2016','maya2017','maya2018','maya2019','maya2020']:
                MayaVersion.append(mulu)
                os.environ['MAYA_LOCATION'] = path+mulu
                os.environ['MAYA_BIN_'+mulu] = os.environ['MAYA_LOCATION'] + '/bin/maya'
                os.environ['MAYA_PY_'+mulu] = os.environ['MAYA_LOCATION'] + '/bin/mayapy'
                os.environ['MAYA_RENDER_'+mulu] = os.environ['MAYA_LOCATION'] + '/bin/Render'
                
                print ("Match Maya Version In this Machine:",sysstr,". ###Current Version###:",mulu)

    elif(sysstr == "Darwin"):
        path = '/Applications/Autodesk/'
        dirs = traversalDir_FirstDir(path)
        if dirs == []:
            print ("No Such Path or No subDir:",path)
            return False
        for mulu in dirs:
            if mulu in ['maya2016','maya2017','maya2018','maya2019','maya2020']:
                MayaVersion.append(mulu)
                os.environ['MAYA_VERSION'] = mulu
                os.environ['MAYA_LOCATION'] = path+mulu
                os.environ['MAYA_BIN_'+mulu] = os.environ['MAYA_LOCATION'] + '/Maya.app/Contents/bin/maya'
                os.environ['MAYA_PY_'+mulu] = os.environ['MAYA_LOCATION'] + '/Maya.app/Contents/bin/mayapy'
                os.environ['MAYA_RENDER_'+mulu] = os.environ['MAYA_LOCATION'] + '/Maya.app/Contents/bin/Render'
                
                print ("Match Maya Version In this Machine:",sysstr,". ###Current Version###:",mulu)

    else:
        print ("Unknow System:",sysstr)
        return False
     
    return True 

def main():
    
    # 配置maya环境参数
    if SetupMayapy() == False:
        return 
    
    # TODO：读取maya项目相关的信息， 检查是否适配本地maya支持的渲染器
  
    # TODO：获取项目要求的maya版本
    mayaVersion = 'maya2018'  # 暂时写死

    # 判断该版本是否在本地已安装的版本中
    if mayaVersion not in MayaVersion:
        print ("NotMatch Maya Version:",mayaVersion)
        return 
    
    # TODO：构造参数。参数来源：1.命令行参数；2.UI输入
    # 这里为了方便测试，用list表示
    # '-o', '--scene_path'
    # '-s', '--startFrame',type='int'
    # '-e', '--endFrame',type='int'
    # '-m', '--frameStep',type='float'
    # '-d', '--render_dir'
    # '-n', '--filename'
    # '-l', '--renderLayer'
    # '-c', '--camera'
    # '-t', '--height', type='int'
    # '-w', '--width', type='int'
    # '-p', '--pixelAspectRatio', type='float'
    # '-r', '--renderer,default='sw'
    settings = [
        # '-o test-mb/GPUTest_766.mb',
        '-o test-mb/ceshi.mb',
        # '-o test-mb/test-mb-file-girl/girlrig.mb',
        '-r arnold',  # mr sw   hw hw2 vr  arnold
    ]

    # 生成可执行的命令  'render-with-window/render.py'
    cmdLine = ' '.join([os.environ['MAYA_PY_'+mayaVersion], 'render/entry.py'] + settings)

    #创建子进程,异步执行命令
    popen = Popen(
        args=cmdLine,    # args='r"绝对路径"', 
        # stdout = PIPE,    #重定向输出的设备。把程序里的结果不输入屏幕上，而是重定向到终端上。
        # stderr = PIPE,    
        shell=True,
    )
    # 如果在上面的Popen中指定stdout，stderr, 则需要通过popen.communicate获取打印输出。
    # 如果上面没有重定向，则popen没有输出
    # output=标准输出的内容    err=标准错误的内容
    # 注意： communicate会阻塞主进程运行
    output, err = popen.communicate()    
    print(":-------------------------:")
    print("Output:",output)
    print(":-------------------------:")
    print("Err:",err)
    print(":-------------------------:")

if __name__ == '__main__':
    main()