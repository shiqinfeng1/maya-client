# -*- coding: utf8 -*-
import time,os,socket
import sys
from os import path
from subprocess import Popen
import cPickle as pickle
try: 			
    import maya.standalone 	
except: 			
    pass
import maya.cmds as cmds
import maya.mel as mel

# 在maya中执行，确保命令监听
# import maya.cmds as cmds
# if not cmds.commandPort('4434',q=True):
#     cmds.commandPort(n=':4434')


# 更改摄像头
def change_render_cam(render_cam):
    render_cam_shape = cmds.listRelatives(render_cam, shapes=1)[0]
    cam_list = cmds.ls(type='camera')
    for cam_shap in cam_list:
        if cam_shap != render_cam_shape:
            cmds.setAttr("%s.renderable"%cam_shap, 0)
        else:
            cmds.setAttr("%s.renderable"%cam_shap, 1)
    mel.eval('unifiedRenderGlobalsWindow;') #注销这一行不弹渲染窗口，对功能无影响   

# 渲染主函数
def render(startFrame = None,endFrame = None,frameStep = 1,
           camera = None,
           height = None,width = None,pixelAspectRatio = None,
           renderer = 'sw',**kwargs):

    # 解析输入参数
    startFrame           = startFrame       if startFrame not in ['None'] else None
    endFrame             = endFrame         if endFrame not in ['None'] else None
    camera               = camera           if camera not in ['None'] else None
    renderer             = renderer         if renderer not in ['None'] else None
    try:
        height           = height           if int(height) not in ['None'] else None
    except:
        height           = None
    try:
        width            = width            if int(width) not in ['None'] else None
    except:
        width            = None
    try:
        frameStep        = frameStep        if float(frameStep) not in ['None'] else 1
    except:
        frameStep        = 1
    try:
        pixelAspectRatio = pixelAspectRatio if float(pixelAspectRatio) not in ['None'] else None
    except:
        pixelAspectRatio = None


    # 获取渲染器路径
    renderer_exec_name = os.environ['MAYA_RENDER_'+os.environ['MAYA_VERSION']]
    scenepath = os.path.abspath(kwargs['scene_path'])

    cmd = [renderer_exec_name]

    # 设置起始和结束帧
    if not startFrame:
        startFrame = cmds.playbackOptions(q=True, ast=True) 
        # startFrame = cmds.getAttr('defaultRenderGlobals.startFrame')
        cmd += ['-s', str(startFrame)]
    if endFrame :
        if endFrame < startFrame:
            endFrame = startFrame
    else:
        endFrame = startFrame
    cmd += ['-e', str(endFrame)]

    if frameStep:
        cmd += ['-b', str(frameStep)]
    # 分别渲染每个渲染层。 适用于传统渲染层和渲染设置。 与渲染设置一起使用时，rs_前缀将附加到为每个图层创建的每个文件夹的名称。
    cmd += ['-rl', 'on']
    print("\nSTEP 5 起始帧: {} 结束帧: {}\n".format(startFrame,endFrame))

    # 设置摄像机
    cmd += ['-cam', 'persp']
    print("\nSTEP 8 当前使用的摄像机: {}\n".format('persp'))
    
    # 渲染器列表
    # [u'mayaSoftware', u'mayaHardware2', u'mentalRay', u'mayaVector', u'arnold'] 
    # cmd += ['-listRenderers']
 
    if renderer == 'sw':
        cmd += ['-eaa', '0'] # 软件渲染时，设置为0代表最高质量。

    # mi: Mentalray Exporter
    # mr: Mentalray renderer
    # arnold: Arnold renderer
    # mi: Mentalray Exporter
    # mr: Mentalray renderer
    # arnold: Arnold renderer
    # turtle: TURTLE frame renderer
    # default: Use the renderer stored in the Maya file
    # vr: Vector renderer
    # hw: Maya hardware renderer
    # turtlebake: TURTLE surface transfer renderer
    # hw2: Maya hardware renderer 2
    # file: Use the renderer stored in the Maya file
    # sw: Maya software renderer
    # interBatch: Interactive batch rendering

    cmd += ['-r', renderer]


    # 设置分辨率相关配置
    # -x int 设置最终图像的X分辨率
    # -y int 设置最终图像的Y分辨率
    # -percentRes float 使用分辨率的百分比渲染图像
    # -ard float 渲染图像的设备纵横比
    # -par float 渲染图像的像素长宽比
    if width:
        cmd += ['-x', str(width)]
    if height:
        cmd += ['-y', str(height)]
    if pixelAspectRatio:
        cmd += ['-par', str(pixelAspectRatio)]
    print('\nSTEP 13 设置分辨率：X={} Y={} PAR={}.\n'.format(width,height,pixelAspectRatio))

    # 设置图像输出格式  cmds.getAttr('defaultRenderGlobals.imageFormat',asString = True)
    cmd += ['-of', 'png'] 

    #  设置图片存储路径
    workspace = cmds.workspace(q=True,fullName = True)
    render_dir = '/'.join([workspace,'images'])
    cmd += ['-rd', '/Users/shiqinfeng/Documents/maya/projects/default/images']  
    
    cmd += [scenepath]
    print('# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #') 
    print('STEP 15 开始执行渲染任务: %s\n' %(cmd))
    # 通过Render命令执行渲染
    p = Popen(cmd)
    stdout, stderr = p.communicate()

    print('# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #') 

# 渲染入口函数
def tryRender(**kwargs):
    	
    # 在mayapy解释器中初始化渲染环境
    print("Initialize MAYA Render Env ...")		
    # Start Maya in batch mode
    try:
       maya.standalone.initialize('Python')
    except: 
       print "standalone already running"
    print("Initialize OK.")	

    # 执行渲染
    render(**kwargs)

    # 退出渲染环境
    cmds.quit(force = True,exitCode = 0,abort = True)

    print("\n\n\nStart Uninitialize version = {}".format(float(cmds.about(v=True))))
    # Starting Maya 2016, we have to call uninitialize to properly shutdown
    if float(cmds.about(v=True)) >= 2016.0:
        maya.standalone.uninitialize()
        print("Uninitialize OK.\n\n\n")
    
    print("渲染结束.")
    



