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

def checkState():
    # check if there are unsaved changes
    fileCheckState = cmds.file(q=True, modified=True)

    # if there are, save them first ... then we can proceed 
    if fileCheckState:
        cmds.SaveScene()

def open_scene(path = None):
    if os.path.exists(path):
        checkState()
        insert_recent_file(path)
        opend = cmds.file(path, o = True, f = True, esn = True)
        print("已打开文件: {}".format(opend))
        return opend

def list_referenced_files():
    results = []
    links = cmds.filePathEditor(query=True, listDirectories="")
    if links == None:
        return
    for link in links:
        pairs =  cmds.filePathEditor(query=True, listFiles=link, withAttribute=True, status=True)
        '''
        paris: list of strings ["file_name node status ...", "file_name node status ...",...]
        we need to make this large list of ugly strings (good inforamtion seperated by white space) into a dictionry we can use
        '''        
        l = len(pairs)
        items = l/3
        order = {}
        index = 0
        
        '''
        order: dict of {node: [file_name, status],...}
        '''
        
        for i in range(0,items):
            order[pairs[index+1]] = [os.path.join(link,pairs[index]),pairs[index+1],pairs[index+2]]
            index = index + 3  
                    
        for key in order:            
            # for each item in the dict, if the status is 0, repath it
            if order[key][2] == "1": 
                results.append([order[key][0],cmds.nodeType(order[key][1])])
                    
    return results 

def scene_resolution():
    return [cmds.getAttr("defaultResolution.width"),cmds.getAttr("defaultResolution.height")]

# 根据类型查找图片格式，默认为png格式
def getFormatType(fmt):
    format_dir = {'JPEG':'jpg','Tiff':'tiff',
                  'Maya IFF':'iff','Targa':'tga',
                  'PNG':'png','Custom Image Format':'exr',
                 }
    return format_dir.get(fmt) if format_dir.get(fmt) != None else 'png'

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

def insert_recent_file(path):
    cmds.optionVar(stringValueAppend=('RecentFilesList', path))

def playback_selection_range():
    aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
    time_selection = cmds.timeControl( aPlayBackSliderPython, q=True,rng=True )[1:-1]
    start = round(float(time_selection.split(":")[0]))
    end = round(float(time_selection.split(":")[1]))
    
    if start+1 == end:
        start = cmds.playbackOptions( q=True,min=True )
        end  = cmds.playbackOptions( q=True,max=True )
        return [start, end]
    else:
        return [start, end]    

# 渲染主函数
def render(startFrame = None,endFrame = None,frameStep = 1,
           render_dir = None,
           renderLayer = None,camera = None,
           renderer = 'sw',**kwargs):

    # 解析输入参数
    startFrame           = startFrame       if startFrame not in ['None'] else None
    endFrame             = endFrame         if endFrame not in ['None'] else None
    render_dir           = render_dir       if render_dir not in ['None'] else None
    renderLayer          = renderLayer      if renderLayer not in ['None'] else None
    camera               = camera           if camera not in ['None'] else None
    renderer             = renderer         if renderer not in ['None'] else None

    # 渲染相关设置
    scenepath = os.path.abspath(kwargs['scene_path'])
    print("\nSTEP 0 获取场景路径: {}\n".format(scenepath))
    workspace = cmds.workspace(q=True,fullName = True)  # /maya/projects/default
    print("\nSTEP 1 获取工作空间: {}\n".format(workspace))

    if not render_dir:
        render_dir = '/'.join([workspace,'images'])
        print("\nSTEP 2.1 设置渲染图片路径: {}\n".format(render_dir))
    if not os.path.isdir(render_dir):
        try:
            os.makedirs(render_dir)
            print("\nSTEP 2.2 新建图片路径: {}\n".format(render_dir))
        except:
            raise Exception('can not make Folder named: %s ' % render_dir)
    
    
    open_scene(scenepath)
    refs = list_referenced_files()
    print("\nSTEP 4 场景相关文件: {} \n".format(refs))
    # 设置起始和结束帧
    if not startFrame:
        startFrame = int(cmds.currentTime(query = True))
    
    if (not endFrame) or (endFrame < startFrame):
        endFrame = startFrame
    # startFrame,endFrame = playback_selection_range()
    print("\nSTEP 5 起始帧: {} 结束帧: {}\n".format(startFrame,endFrame))

    # 设置渲染层， 不同的渲染器对渲染层有不同的配置参数 
    if not renderLayer:
        renderLayer = cmds.editRenderLayerGlobals(q = True,currentRenderLayer = True)
        print("\nSTEP 6.1 未指定渲染层，获取当前渲染层: {}\n".format(renderLayer))

    elif renderLayer not in cmds.ls(type = 'renderLayer'):
        renderLayer = cmds.editRenderLayerGlobals(q = True,currentRenderLayer = True)
        print('\nSTEP 6.2 指定的渲染层不在当前maya环境上, 使用默认的渲染层: %s\n' %(renderLayer))

    else:
        if cmds.editRenderLayerGlobals(q = True,currentRenderLayer = True) != renderLayer:
            cmds.editRenderLayerGlobals(currentRenderLayer = renderLayer)
        print('\nSTEP 6.3 指定的渲染层在当前maya环境上,但不是当前默认渲染层，设置为默认渲染层: %s\n' %(renderLayer))

    # 设置摄像机
    render_cam = 'persp'     
    change_render_cam(render_cam)
    print("\nSTEP 7 设置默认摄像机: {}\n".format(render_cam))
    # get camera  获取摄像机
    if not camera:
        _cameras = [i for i in cmds.listCameras(p = True) if cmds.getAttr('%s.renderable' % i)]
        if _cameras:
            camera = _cameras[0]
        else:
            camera = 'persp'
    print("\nSTEP 8 当前使用的摄像机: {}\n".format(camera))

    #打印当前渲染器设置
    # render_glob = "defaultRenderGlobals"
    # list_Attr = cmds.listAttr(render_glob, r=True, s=True)
    # print("\n")
    # for attr in list_Attr:
    #     get_attr_name = "%s.%s"%(render_glob, attr)
    #     print("STEP 9 默认Render的全局配置信息: {} = {}".format(get_attr_name, cmds.getAttr(get_attr_name)))
    # print("\n")

    # load renderer  加载渲染器
    currenders = cmds.renderer(q=True, namesOfAvailableRenderers=True)
    print('\nSTEP 9 当前可用的渲染器有: {} \n'.format(currenders))

    print("\nSTEP 10 当前插件路径: {} \n".format(os.environ['MAYA_PLUG_IN_PATH']))
    cmds.loadPlugin( allPlugins=True )
    
    if renderer:
        if renderer:
            if renderer != cmds.getAttr('defaultRenderGlobals.currentRenderer'):
                renderer_dict = {'vray':'vrayformaya',
                             'arnold':'mtoa',
                             'mentalRay':'Mayatomr'}
                for key in renderer_dict.keys():
                    if renderer == key:
                        if not cmds.pluginInfo(renderer_dict[key], q=True, l=True):
                            try:
                                cmds.loadPlugin(renderer_dict[key])
                                break
                            except:
                                raise Exception('can not load vray renderer')
        try:
            cmds.setAttr('defaultRenderGlobals.currentRenderer',renderer,type = 'string')
        except:
            raise Exception('error: set currentRenderer %s fail' % renderer)
    else:
        renderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
        print('\nSTEP 12 指定的渲染器位当前默认渲染器: %s\n' %(renderer))

        
    w, h = scene_resolution()
    print('\nSTEP 13 当前图片分辨率：X={} Y={} .\n'.format(w,h))

    # 设置图像输出格式  cmds.getAttr('defaultRenderGlobals.imageFormat',asString = True)
    _format = getFormatType("PNG")
    print('\nSTEP 14 设置输出图像的格式: %s\n' %(_format))

    print('# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #') 
    print('STEP 15 开始执行渲染任务...\n')

    cd = int(endFrame) + 1
    for i in range(int(startFrame), int(cd)):
        cmds.currentTime(i, u = True)
        if renderer == 'sw':
            cmds.render()
        elif renderer == 'mr':
            out = cmds.Mayatomr(preview = True, camera = camera)
            print("cmds.Mayatomr:",out)
        else:
            pass

    if renderer == 'vray':
        cmds.setAttr ('defaultRenderGlobals.animation', 1 )
        cmds.setAttr ('defaultRenderGlobals.startFrame', startFrame )
        cmds.setAttr ('defaultRenderGlobals.endFrame', endFrame )
        print(cmds.setAttr ('vraySettings.animBatchOnly', 0))
        
        out = pm.vrend(preview = True,camera = camera)
        print("pm.vrend:",out)
    
    elif renderer == 'arnold':
        for i in range(startFrame,endFrame+1,1):
            cmds.currentTime(i)
            out = cmds.arnoldRender(seq=str(i),camera = camera )
        print("cmds.arnoldRender:",out)

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
    



