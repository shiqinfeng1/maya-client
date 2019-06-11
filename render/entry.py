# -*- coding: utf8 -*-
import optparse
import pprint
import os,socket
import cPickle as pickle
import mayarender
import mayacmds

# 渲染入口
def render(**kwargs):
    
    # # 获取待渲染文件的路径
    # scene_path = os.path.abspath(kwargs['scene_path'])

    # # 生成临时文件路径：set mel path & render frame tmp path
    # _scriptpath = '/'.join([os.path.dirname(scene_path),'%s_%s.mel' % (socket.gethostname(),scene_path.replace('/','_').replace(':','_'))])
    # tmp_frame_path = '/'.join([os.path.dirname(scene_path),'%s_%s_%s' % (socket.gethostname(),scene_path.replace('/','_').replace(':','_'),'frame_tmp')])

    # # 配置用maya打开临时文件的命令
    # cmd = os.environ['MAYA_BIN_'+os.environ['MAYA_VERSION']]
    # cmd += ' -file "%s" -script "%s"' %(scene_path,_scriptpath)

    # 尝试渲染文件。tryRender将在tmp_frame_path中保存当前渲染状态
    print("\n/:============:/\nTry To Render...\nCmd = {}".format(kwargs))
    mayacmds.tryRender(**kwargs)
    print("/:============:/\n")
    
    # # write mel
    # try:
    #     _script = open(_scriptpath,'w')
    #     _script.write(_cmd)
    #     _script.close()
    # except:
    #     raise Exception('can not write start mel in path: %s' % os.path.dirname(_scriptpath))

    # # write frame tmp
    # if not os.path.isfile(tmp_frame_path):
    #     data_file = open(tmp_frame_path,'wb')
    #     pickle.dump({},data_file)
    #     data_file.close()
    
    # # run cmd
    # out = os.system(cmd)
    # print("RUNNING CMD:",cmd,"\nEXPORT: ",out)

    # # get frame render tmp
    # if os.path.isfile(tmp_frame_path):
    #     print tmp_frame_path
    #     _info_file = open(tmp_frame_path,'rb')
    #     _info = pickle.load(_info_file)
    #     _info_file.close()

    #     if isinstance(_info.get('frame'),(int,float)):
    #         if _info.get('completed'):
    #             _info['frame'] = _info.get('frame') + _info.get('frameStep')

    #         if _info.get('frame') < _info.get('endFrame'):
    #             if _info.get('try') > 2 and not _info.get('completed'):
    #                 raise Exception('frame: % render fail,' % _info.get('frame'))
    #             else:
    #                 kwargs['startFrame'] = _info.get('frame')
    #                 kwargs['endFrame'] = _info.get('endFrame')
    #                 kwargs['frameStep'] = _info.get('frameStep')

    #                 render(scene_path = scene_path,
    #                         **kwargs)

    #     else:
    #         raise Exception('open maya fail with scene :%s' % scene_path)

    # else:
    #     logging.warning('can not find frame tmp file,please chick render output')

    # # remove mel,tmp
    # try:
    #     if os.path.isfile(_scriptpath):
    #         os.remove(_scriptpath)
    # except:
    #     pass
    # try:
    #     if os.path.isfile(tmp_frame_path):
    #         os.remove(tmp_frame_path)
    # except:
    #     pass


if __name__ == '__main__':
    
    # 定义脚本输入参数
    parser = optparse.OptionParser()
    parser.add_option('-o', '--scene_path')
    parser.add_option('-s', '--startFrame',type='int')
    parser.add_option('-e', '--endFrame',type='int')
    parser.add_option('-m', '--frameStep',type='float')
    parser.add_option('-d', '--render_dir')
    parser.add_option('-n', '--filename')
    parser.add_option('-l', '--renderLayer')
    parser.add_option('-c', '--camera')
    parser.add_option('-t', '--height', type='int')
    parser.add_option('-w', '--width', type='int')
    parser.add_option('-p', '--pixelAspectRatio', type='float')
    parser.add_option('-r', '--renderer', default='sw')
    option,args = parser.parse_args()

    print('+------------------+')
    pp = pprint.PrettyPrinter(indent=4)
    print('参数解析结果:')
    pp.pprint(option.__dict__)
    pp.pprint(args)
    print('+------------------+')
    if option.__dict__.get('scene_path'): 
        render(**option.__dict__)
    else:
        raise Exception('Can Not Find <scene_path>. Oops!!! ')
