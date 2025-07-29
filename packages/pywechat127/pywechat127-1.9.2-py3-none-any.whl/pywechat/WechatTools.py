'''
WechatTools
---------------
该模块中封装了一系列关于PC微信自动化的工具,主要用来辅助WechatAuto模块下的各个函数与方法的实现\n
---------------
类:\n
Tools:一些关于PC微信自动化过程中的工具,可以用于二次开发\n
API:打开指定公众号与微信小程序以及视频号,可为微信内部小程序公众号自动化操作提供便利\n
------------------------------------
函数:\n
函数为上述模块内的所有方法\n
--------------------------------------
使用该模块的方法时,你可以:\n
----------------------------
#打开指定微信小程序
```
from pywechat.WechatTools import API
API.open_wechat_miniprogram(name='问卷星')
```
或者:\n
```
from pywechat import open_wechat_miniprogram
open_wechat_miniprogram(name='问卷星')
```
#从界面内拉取200条消息
```
from pywechat import pull_messages
message_contents,message_senders,message_types=pull_messages(friend='文件传输助手',number=200)
```
或者:\n
```
from pywechat.WechatTools import Tools
message_contents,message_senders,message_types=Tools.pull_messages(friend='文件传输助手',number=200)
```
'''
############################依赖环境###########################
import os
import re
import time
import winreg
import win32api
import pyautogui
import win32gui
import win32con
import subprocess
import win32com.client
import psutil
from pywinauto import mouse,Desktop
from pywinauto.controls.uia_controls import ListItemWrapper
from pywinauto.controls.uia_controls import ListViewWrapper
from .Errors import NetWorkNotConnectError
from .Errors import NoSuchFriendError
from .Errors import ScanCodeToLogInError
from .Errors import NoResultsError,NotFriendError,NotInstalledError
from .Errors import ElementNotFoundError
from .Errors import WrongParameterError
from pywinauto.findwindows import ElementNotFoundError
from .Uielements import (Login_window,Main_window,SideBar,
Independent_window,Buttons,Texts,Menus,TabItems,MenuItems,Edits,Windows)
from .WinSettings import Systemsettings 
##########################################################################################
Login_window=Login_window()#登录主界面内的UI
Main_window=Main_window()#微信主界面内的UI
SideBar=SideBar()#微信主界面侧边栏的UI
Independent_window=Independent_window()#一些独立界面
Buttons=Buttons()#微信内部Button类型UI
Texts=Texts()#微信内部Text类型UI
Menus=Menus()#微信内部Menu类型UI
TabItems=TabItems()#微信内部TabItem类型UI
MenuItems=MenuItems()#w微信内部MenuItems类型UI
Edits=Edits()#微信内部Edit类型Ui
Windows=Windows()#微信内部Window类型UI
pyautogui.FAILSAFE=False#防止鼠标在屏幕边缘处造成的误触

class Tools():
    '''该类中封装了一些关于PC微信的工具\n
    ''' 

    @staticmethod
    def is_wechat_running():
        '''
        该方法通过检测当前windows系统的进程中\n
        是否有WeChat.exe该项进程来判断微信是否在运行
        '''
        wmi=win32com.client.GetObject('winmgmts:')
        processes=wmi.InstancesOf('Win32_Process')
        for process in processes:
            if process.Name.lower()=='Wechat.exe'.lower():
                return True
        return False
    
    

    @staticmethod
    def language_detector():
        """
        该方法通过查询注册表来检测当前微信的语言版本\n
        """
        #微信3.9版本的一般注册表路径
        reg_path=r"Software\Tencent\WeChat"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                value=winreg.QueryValueEx(key,"LANG_ID")[0]
                language_map={
                    0x00000009: '英文',
                    0x00000004: '简体中文',
                    0x00000404: '繁体中文'
                }
                return language_map.get(value)
        except FileNotFoundError:
            raise NotInstalledError
            
    @staticmethod
    def find_wechat_path(copy_to_clipboard:bool=True):
        '''该方法用来查找微信的路径,无论微信是否运行都可以查找到\n
            copy_to_clipboard:\t是否将微信路径复制到剪贴板\n
        '''
        if is_wechat_running():
            wmi=win32com.client.GetObject('winmgmts:')
            processes=wmi.InstancesOf('Win32_Process')
            for process in processes:
                if process.Name.lower() == 'WeChat.exe'.lower():
                    exe_path=process.ExecutablePath
                    if exe_path:
                        # 规范化路径并检查文件是否存在
                        exe_path=os.path.abspath(exe_path)
                        wechat_path=exe_path
            if copy_to_clipboard:
                Systemsettings.copy_text_to_windowsclipboard(wechat_path)
                print("已将微信程序路径复制到剪贴板")
            return wechat_path
        else:
            #windows环境变量中查找WeChat.exe路径
            wechat_environ_path=[path for path in dict(os.environ).values() if 'WeChat.exe' in path]#
            if wechat_environ_path:
                if copy_to_clipboard:
                    Systemsettings.copy_text_to_windowsclipboard(wechat_environ_path[0])
                    print("已将微信程序路径复制到剪贴板")
                return wechat_environ_path[0]
            if not wechat_environ_path:
                try:
                    reg_path=r"Software\Tencent\WeChat"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        Installdir=winreg.QueryValueEx(key,"InstallPath")[0]
                    wechat_path=os.path.join(Installdir,'WeChat.exe')
                    if copy_to_clipboard:
                        Systemsettings.copy_text_to_windowsclipboard(wechat_path)
                        print("已将微信程序路径复制到剪贴板")
                    return wechat_path
                except FileNotFoundError:
                    raise NotInstalledError
        
    @staticmethod
    def is_VerticalScrollable(List:ListViewWrapper):
        '''
        该方法用来判断微信内的列表是否可以垂直滚动\n
        说明:\t微信内的List均为UIA框架,无句柄,停靠在右侧的scrollbar组件无Ui\n
        且列表还只渲染可见部分,因此需要使用UIA的iface_scorll来判断\n
        Args:
            List:微信内control_type为List的列表
        '''
        try:
            #如果能获取到这个属性,说明可以滚动
            List.iface_scroll.CurrentVerticallyScrollable
            return True
        except Exception:#否则会引发NoPatternInterfaceError,此时返回False
            return False
        
    
    @staticmethod
    def set_wechat_as_environ_path():
        '''该方法用来自动打开系统环境变量设置界面,将微信路径自动添加至其中\n'''
        os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})
        subprocess.Popen(["SystemPropertiesAdvanced.exe"])
        time.sleep(2)
        systemwindow=win32gui.FindWindow(None,u'系统属性')
        if win32gui.IsWindow(systemwindow):#将系统变量窗口置于桌面最前端
            win32gui.ShowWindow(systemwindow,win32con.SW_SHOW)
            win32gui.SetWindowPos(systemwindow,win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)    
        pyautogui.hotkey('alt','n',interval=0.5)#添加管理员权限后使用一系列快捷键来填写微信刻路径为环境变量
        pyautogui.hotkey('alt','n',interval=0.5)
        pyautogui.press('shift')
        pyautogui.typewrite('wechatpath')
        try:
            Tools.find_wechat_path()
            pyautogui.hotkey('Tab',interval=0.5)
            pyautogui.hotkey('ctrl','v')
            pyautogui.press('enter')
            pyautogui.press('enter')
            pyautogui.press('esc')
        except Exception:
            pyautogui.press('esc')
            pyautogui.hotkey('alt','f4')
            pyautogui.hotkey('alt','f4')
            raise NotInstalledError
 
    @staticmethod
    def judge_wechat_state():
        '''该方法用来判断微信运行状态'''
        time.sleep(1.5)
        if Tools.is_wechat_running():
            window=win32gui.FindWindow(Main_window.MainWindow['class_name'],Main_window.MainWindow['title'])
            if win32gui.IsIconic(window):
                return '主界面最小化'
            elif win32gui.IsWindowVisible(window):
                return '主界面可见'
            else:
                return '主界面不可见'
        else:
            return "微信未打开"
        
    @staticmethod
    def judge_independant_window_state(window:dict):
        '''该方法用来判断微信内独立于微信主界面的窗口的状态\n'''
        time.sleep(1)
        handle=win32gui.FindWindow(window.get('class_name'),None)
        if win32gui.IsIconic(handle):
            return '界面最小化'
        elif win32gui.IsWindowVisible(handle):  
            return '界面可见'
        else:
            return '界面未打开,需进入微信打开'
       
        
    @staticmethod
    def move_window_to_center(Window:dict=Main_window.MainWindow,Window_handle:int=0):
        '''该方法用来将已打开的界面移动到屏幕中央并返回该窗口的windowspecification实例,使用时需注意传入参数为窗口的字典形式\n
        需要包括class_name与title两个键值对,任意一个没有值可以使用None代替\n
        Args:
            Window:\tpywinauto定位元素kwargs参数字典
            Window_handle:\t窗口句柄\n
        '''
        desktop=Desktop(**Independent_window.Desktop)
        class_name=Window['class_name']
        title=Window['title'] if 'title' in Window else None
        if Window_handle==0:
            handle=win32gui.FindWindow(class_name,title)
        else:
            handle=Window_handle
        screen_width,screen_height=win32api.GetSystemMetrics(win32con.SM_CXSCREEN),win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        window=desktop.window(handle=handle)
        window_width,window_height=window.rectangle().width(),window.rectangle().height()
        new_left=(screen_width-window_width)//2
        new_top=(screen_height-window_height)//2
        win32gui.SetWindowPos(
            handle,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE |
            win32con.SWP_NOSIZE |
            win32con.SWP_SHOWWINDOW
        )
        if screen_width!=window_width:
            win32gui.MoveWindow(handle, new_left, new_top, window_width, window_height, True)
        return window
    
    @staticmethod 
    def open_wechat(wechat_path:str=None,is_maximize:bool=True):
        '''
        该方法用来打开微信\n
        Args:
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。
        微信的打开分为四种情况:\n
        1.未登录,此时调用该函数会启动wechat_path路径下的wechat.exe,在弹出的登录界面中点击进入微信打开微信主界面\n
        启动并点击登录进入微信(注:需勾选自动登录按钮,否则启动后为扫码登录)\n
        2.未登录但已弹出微信的登录界面,此时会自动点击进入微信打开微信\n
        注意:未登录的情况下打开微信需要在手机端第一次扫码登录后勾选自动登入的选项,否则启动微信后\n
        聊天界面没有进入微信按钮,将会触发异常提示扫码登录\n
        3.已登录，主界面最小化在状态栏，此时调用该函数会直接打开后台中的微信。\n
        4.已登录，主界面关闭，此时调用该函数会打开已经关闭的微信界面。
        '''
        max_retry_times=40
        retry_interval=0.5
        wechat_path=wechat_path
        #处理登录界面的闭包函数，点击进入微信，若微信登录界面存在直接传入窗口句柄，否则自己查找
        def handle_login_window(wechat_path=wechat_path,is_maximize=is_maximize,max_retry_times=max_retry_times,retry_interval=retry_interval):
            counter=0
            if wechat_path:#看看有没有传入wechat_path
                subprocess.Popen(wechat_path)
            if not wechat_path:#没有传入就自己找
                wechat_path=Tools.find_wechat_path(copy_to_clipboard=False)
                subprocess.Popen(wechat_path)
            #没有传入登录界面句柄，需要自己查找(此时对应的情况是微信未启动)
            login_window_handle= win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
            while not login_window_handle:
                login_window_handle= win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
                if login_window_handle:
                    break
                counter+=1
                time.sleep(0.2)
                if counter>=max_retry_times:
                    raise NoResultsError(f'微信打开失败,请检查网络连接或者微信是否正常启动！')
            #移动登录界面到屏幕中央
            login_window=Tools.move_window_to_center(Login_window.LoginWindow,login_window_handle)
            #点击登录按钮,等待主界面出现并返回
            try:
                login_button=login_window.child_window(**Login_window.LoginButton)
                login_button.set_focus()
                login_button.click_input()
                main_window_handle = 0
                while not main_window_handle:
                    main_window_handle=win32gui.FindWindow(Main_window.MainWindow['class_name'],None)
                    if main_window_handle:
                        break
                    counter+=1
                    time.sleep(retry_interval)
                    if counter >= max_retry_times:
                        raise NetWorkNotConnectError
                main_window=Tools.move_window_to_center(Window_handle=main_window_handle)
                if is_maximize:
                    main_window.maximize()
                NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                if NetWorkErrotText.exists():
                    main_window.close()
                    raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                return main_window 
            except ElementNotFoundError:
                raise ScanCodeToLogInError
         #最多尝试40次，每次间隔0.5秒，40秒内无法打开微信则抛出异常
        
        #open_wechat函数的主要逻辑：
        if Tools.is_wechat_running():#微信如果已经打开无需登录可以直接连接
            #同时查找主界面与登录界面句柄，二者有一个存在都证明微信已经启动
            main_window_handle=win32gui.FindWindow(Main_window.MainWindow['class_name'],None)
            login_window_handle=win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
            if main_window_handle:
                #威信运行时有最小化，主界面可见未关闭,主界面不可见关闭三种情况
                if win32gui.IsWindowVisible(main_window_handle):#主界面可见包含最小化
                    if win32gui.IsIconic(main_window_handle):#主界面最小化
                        win32gui.ShowWindow(main_window_handle,win32con.SW_SHOWNORMAL)
                        main_window=Tools.move_window_to_center(Window_handle=main_window_handle) 
                        if is_maximize:
                            main_window.maximize()
                        NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                        if NetWorkErrotText.exists():
                            main_window.close()
                            raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                        return main_window
                    else:#主界面存在且未最小化
                        main_window=Tools.move_window_to_center(Window_handle=main_window_handle)
                        if is_maximize:
                            main_window.maximize()
                        NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                        if NetWorkErrotText.exists():
                            main_window.close()
                            raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                        return main_window
                else:#主界面不可见
                    #打开过主界面，关闭掉了，需要重新打开 
                    win32gui.ShowWindow(main_window_handle,win32con.SW_SHOWNORMAL)
                    main_window=Tools.move_window_to_center(Window_handle=main_window_handle)
                    if is_maximize:
                        main_window.maximize()
                    NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                    if NetWorkErrotText.exists():
                        main_window.close()
                        raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                    return main_window
            if login_window_handle:#微信启动了，但是.是登录界面在桌面上，不是主界面
                #处理登录界面
                return handle_login_window()
        else:#微信未启动，需要先使用subprocess.Popen启动微信弹出登录界面后点击进入微信
            #处理登录界面
            return handle_login_window()
                                
    @staticmethod
    def open_settings(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用来打开微信设置界面。\n
        Args:
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:微信界面是否全屏,默认全屏。\n
            close_wechat:任务结束后是否关闭微信,默认关闭\n
        '''   
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        setting=main_window.child_window(**SideBar.SettingsAndOthers)
        setting.click_input()
        settings_menu=main_window.child_window(**Main_window.SettingsMenu)
        settings_button=settings_menu.child_window(**Buttons.SettingsButton)
        settings_button.click_input()
        if close_wechat:
            main_window.close() 
        time.sleep(1)
        desktop=Desktop(**Independent_window.Desktop)
        settings_window=desktop.window(**Independent_window.SettingWindow)
        return settings_window
    
    @staticmethod                    
    def open_dialog_window(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5): 
        '''
        该方法用于打开某个好友的聊天窗口\n
        Args:
            friend:\t好友或群聊备注名称,需提供完整名称\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                  尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                  传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
            search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
        Returns:
            (edit_area,main_window):\nedit_area:主界面右侧下方消息编辑区域,main_window:微信主界面
        '''
        def is_in_searh_result(friend,search_result):#查看搜索列表里有没有名为friend的listitem
            listitem=search_result.children(control_type="ListItem")
            names=[item for item in listitem if item.descendants(title=friend,control_type='Button')]
            names=[item.window_text() for item in names]
            if friend in names:
                return True
            else:
                return False
        #如果search_pages不为0,即需要在会话列表中滚动查找时，使用find_friend_in_Messagelist方法找到好友,并点击打开对话框
        if search_pages:
            chat,main_window=Tools.find_friend_in_MessageList(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
            chat_button=main_window.child_window(**SideBar.Chats)
            if is_maximize:
                main_window.maximize()
            if chat:#chat不为None,即说明find_friend_in_MessageKist找到了聊天窗口chat,直接返回结果
                return chat,main_window
            else:  #chat为None没有在会话列表中找到好友,直接在顶部搜索栏中搜索好友
                #先点击侧边栏的聊天按钮切回到聊天主界面
                #顶部搜索按钮搜索好友
                search=main_window.child_window(**Main_window.Search).wait(wait_for='visible',retry_interval=0.1,timeout=3)
                search.click_input()
                Systemsettings.copy_text_to_windowsclipboard(friend)
                pyautogui.hotkey('ctrl','v')
                search_results=main_window.child_window(**Main_window.SearchResult)
                time.sleep(1)
                if is_in_searh_result(friend=friend,search_result=search_results):
                    result=search_results.children(control_type='ListItem',title=friend)[0]
                    result.click_input()
                    chat=main_window.child_window(title=friend,control_type='Edit')
                    return chat,main_window #同时返回搜索到的该好友的聊天窗口与主界面！若只需要其中一个需要使用元祖索引获取。
                else:#搜索结果栏中没有关于传入参数friend好友昵称或备注的搜索结果，关闭主界面,引发NoSuchFriend异常
                    chat_button.click_input()
                    main_window.close()
                    raise NoSuchFriendError
        else: #searchpages为0，不在会话列表查找
            #这部分代码先判断微信主界面是否可见,如果可见不需要重新打开,这在多个close_wechat为False需要进行来连续操作的方式使用时要用到
            main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
            chat_button=main_window.child_window(**SideBar.Chats)
            message_list_pane=main_window.child_window(**Main_window.ConversationList)
            #先看看当前聊天界面是不是好友的聊天界面
            current_chat=main_window.child_window(**Main_window.CurrentChatWindow)
            #如果当前主界面是某个好友的聊天界面且聊天界面顶部的名称为好友名称，直接返回结果
            if current_chat.exists() and friend==current_chat.window_text():
                chat=current_chat
                chat.click_input()
                return chat,main_window
            else:#否则直接从顶部搜索栏出搜索结果
                #如果会话列表不存在或者不可见的话才点击一下聊天按钮
                if not message_list_pane.exists():
                    chat_button.click_input()
                if not message_list_pane.is_visible():
                    chat_button.click_input()        
                search=main_window.child_window(**Main_window.Search)
                search.click_input()
                Systemsettings.copy_text_to_windowsclipboard(friend)
                pyautogui.hotkey('ctrl','v')
                search_results=main_window.child_window(**Main_window.SearchResult)
                time.sleep(1)
                if is_in_searh_result(friend=friend,search_result=search_results):
                    result=search_results.children(control_type='ListItem',title=friend)[0]
                    result.click_input()
                    chat=main_window.child_window(title=friend,control_type='Edit')
                    return chat,main_window #同时返回该好友的聊天窗口与主界面！若只需要其中一个需要使用元祖索引获取。
                else:
                    chat_button.click_input()
                    main_window.close()
                    raise NoSuchFriendError


    @staticmethod
    def find_friend_in_MessageList(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5):
        '''
        该方法用于在会话列表中查询是否存在待查询好友。\n
        Args:
            friend:\t好友或群聊备注名称,需提供完整名称\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
            search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
        若存在:返回值为 (chat,main_window) 同时返回好友聊天界面与主界面\n
        否则:返回值为 (None,main_window)只返回主界面\n
        '''
        def get_window(friend):
            '''
            用来返回会话列表中满足条件的好友,如果好友是最后一个返回其在会话列表中的索引
            '''
            message_list=message_list_pane.children(control_type='ListItem')
            buttons=[friend.children()[0].children()[0] for friend in message_list]
            friend_button=None
            for i in range(len(buttons)):
                if friend==buttons[i].texts()[0]:
                    friend_button=buttons[i]
                    break
            if i==len(buttons)-1:
                return friend_button,i
            else:
                return friend_button,None
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        #先看看当前微信右侧界面是不是聊天界面可能存在不是聊天界面的情况比如是纯白色的微信的icon
        current_chat=main_window.child_window(**Main_window.CurrentChatWindow)
        chat_button=main_window.child_window(**SideBar.Chats)
        message_list_pane=main_window.child_window(**Main_window.ConversationList)
        if not message_list_pane.exists():
            chat_button.click_input()
        if not message_list_pane.is_visible():
            chat_button.click_input()
        rectangle=message_list_pane.rectangle()
        scrollable=Tools.is_VerticalScrollable(message_list_pane)
        if is_maximize:
            activateScollbarPosition=(rectangle.right-5, rectangle.top+20)
        if not is_maximize:
            activateScollbarPosition=(rectangle.right-4, rectangle.top+20)
        if current_chat.exists():#如果当前微信主界面右侧是聊天界面，
            if current_chat.window_text()==friend:#如果当前主界面是某个好友的聊天界面且聊天界面顶部的名称为好友名称，直接返回结果
                chat=current_chat
                chat.click_input()
                return chat,main_window
            else:#否则在消息列表中查找
                message_list=message_list_pane.children(control_type='ListItem')
                if len(message_list)==0:
                    return None,main_window
                if not scrollable:#消息列表中好友数量小于10，无法滚动，直接在消息列表中查找
                    friend_button,index=get_window(friend)
                    if friend_button:
                        if index:
                            #最后一个
                            rec=friend_button.rectangle()
                            mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                            chat=main_window.child_window(title=friend,control_type='Edit')
                        else:
                            friend_button.click_input()
                            chat=main_window.child_window(title=friend,control_type='Edit')
                        return chat,main_window
                    else:
                        return None,main_window
                if scrollable:#会话列表可以滚动，滚动查找
                    rectangle=message_list_pane.rectangle()
                    mouse.click(coords=activateScollbarPosition)
                    pyautogui.press('Home')
                    for _ in range(search_pages):
                        friend_button,index=get_window(friend)
                        if friend_button:
                            if index:
                                rec=friend_button.rectangle()
                                mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                                chat=main_window.child_window(title=friend,control_type='Edit')
                            else:
                                friend_button.click_input()
                                chat=main_window.child_window(title=friend,control_type='Edit') 
                            break
                        else:
                            pyautogui.press("pagedown")
                            time.sleep(0.5)
                    #看看是否找到了好友
                    chat=main_window.child_window(title=friend,control_type='Edit')
                    if chat.exists():
                        return chat,main_window
                    else:
                        return None,main_window
                    
        else:#右侧不是聊天界面，可能刚进入微信右侧是纯白色icon或者右侧是无法发送消息的公众号界面等，这时直接在消息列表中滚动查找
            message_list=message_list_pane.children(control_type='ListItem')
            if len(message_list)==0:
                return None,main_window
            if not scrollable:
                friend_button,index=get_window(friend)
                if friend_button:
                    if index:
                        rec=friend_button.rectangle()
                        mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                        chat=main_window.child_window(title=friend,control_type='Edit')
                    else:
                        friend_button.click_input()
                        chat=main_window.child_window(title=friend,control_type='Edit')
                    return chat,main_window
                else:
                    return None,main_window
            if scrollable:
                rectangle=message_list_pane.rectangle()
                mouse.click(coords=activateScollbarPosition)
                pyautogui.press('Home')
                for _ in range(search_pages):
                    friend_button,index=get_window(friend)
                    if friend_button:
                        if index:
                            rec=friend_button.rectangle()
                            mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                            chat=main_window.child_window(title=friend,control_type='Edit')
                        else:
                            friend_button.click_input()
                            chat=main_window.child_window(title=friend,control_type='Edit')  
                        break
                    else:
                        pyautogui.press("pagedown")
                        time.sleep(0.5)
                mouse.click(coords=activateScollbarPosition)
                pyautogui.press('Home')
                chat=main_window.child_window(title=friend,control_type='Edit')
                if chat.exists():
                    return chat,main_window
                else:
                    return None,main_window
    @staticmethod
    def open_friend_settings(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5):
        '''
        该方法用于打开好友设置界面\n
        Args:
            friend\t:好友备注名称,需提供完整名称\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
            search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
        '''
        main_window=Tools.open_dialog_window(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
        
        try:
            ChatMessage=main_window.child_window(**Buttons.ChatMessageButton)
            ChatMessage.click_input()
            friend_settings_window=main_window.child_window(**Main_window.FriendSettingsWindow)
        except ElementNotFoundError:
            main_window.close()
            raise NotFriendError(f'非正常好友,无法打开设置界面！')
        return friend_settings_window,main_window
 
    @staticmethod
    def open_contacts_settings(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用于打开通讯录设置界面\n
        Args:
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
            close_wechat:\t任务结束后是否关闭微信,默认关闭\n
        '''
        
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        desktop=Desktop(**Independent_window.Desktop)
        contacts=main_window.child_window(**SideBar.Contacts)
        contacts.set_focus()
        contacts.click_input()
        cancel_button=main_window.child_window(**Buttons.CancelButton)
        if cancel_button.exists():
            cancel_button.click_input()
        ContactsLists=main_window.child_window(**Main_window.ContactsList)
        #############################
        rec=ContactsLists.rectangle()
        mouse.click(coords=(rec.right-5,rec.top))
        pyautogui.press('Home')
        pyautogui.press('pageup')
        contacts_settings=main_window.child_window(**Buttons.ContactsManageButton)#通讯录管理窗口按钮 
        contacts_settings.set_focus()
        contacts_settings.click_input()
        contacts_settings_window=desktop.window(**Independent_window.ContactManagerWindow)
        if close_wechat:
            main_window.close()
        return contacts_settings_window,main_window
    
    @staticmethod
    def open_friend_settings_menu(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5):
        '''
        该方法用于打开好友设置界面\n
        Args:
            friend:\t好友备注名称,需提供完整名称\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
            search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
        '''
        friend_settings_window,main_window=Tools.open_friend_settings(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
        friend_button=friend_settings_window.child_window(title=friend,control_type="Button",found_index=0)
        friend_button.click_input()
        profile_window=friend_settings_window.child_window(class_name="ContactProfileWnd",control_type="Pane",framework_id='Win32')
        more_button=profile_window.child_window(**Buttons.MoreButton)
        more_button.click_input()
        friend_menu=profile_window.child_window(control_type="Menu",title="",class_name='CMenuWnd',framework_id='Win32')
        return friend_menu,friend_settings_window,main_window
         
    @staticmethod
    def open_collections(wechat_path:str=None,is_maximize:bool=True):
        '''
        该方法用于打开收藏界面\n
        Args:
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        
        collections_button=main_window.child_window(**SideBar.Collections)
        collections_button.click_input()
        return main_window
    
    @staticmethod
    def open_group_settings(group_name:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5):
        '''
        该方法用来打开群聊设置界面\n
        Args:
            group_name:\t群聊备注名称,需提供完整名称\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
            search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
        '''
        main_window=Tools.open_dialog_window(friend=group_name,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
        ChatMessage=main_window.child_window(**Buttons.ChatMessageButton)
        ChatMessage.click_input()
        group_settings_window=main_window.child_window(**Main_window.GroupSettingsWindow)
        group_settings_window.child_window(**Texts.GroupNameText).click_input()
        return group_settings_window,main_window

    @staticmethod
    def open_wechat_moments(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用于打开微信朋友圈\n
        Args:
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
            close_wechat:\t任务结束后是否关闭微信,默认关闭\n
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        moments_button=main_window.child_window(**SideBar.Moments)
        moments_button.click_input()
        moments_window=Tools.move_window_to_center(Independent_window.MomentsWindow)
        moments_window.child_window(**Buttons.RefreshButton).click_input()
        if close_wechat:
            main_window.close()
        return moments_window
    
    @staticmethod
    def open_chat_files(wechat_path:str=None,wechat_maximize:bool=True,is_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用于打开聊天文件\n
        Args:
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            wechat_maximize:微信界面是否全屏,默认全屏\n
            is_maximize:\t聊天文件界面是否全屏,默认全屏。\n
            close_wechat:\t任务结束后是否关闭微信,默认关闭\n
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
        moments_button=main_window.child_window(**SideBar.ChatFiles)
        moments_button.click_input()
        desktop=Desktop(**Independent_window.Desktop)
        filelist_window=desktop.window(**Independent_window.ChatFilesWindow)
        if is_maximize:
            filelist_window.maximize()
        if close_wechat:
            main_window.close()
        return filelist_window
    
    @staticmethod
    def open_friend_profile(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5):
        '''
        该方法用于打开好友个人简介界面\n
        Args:
            friend:\t好友备注名称,需提供完整名称\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t信界面是否全屏,默认全屏。\n
            search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
        '''
        friend_settings_window,main_window=Tools.open_friend_settings(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
        friend_button=friend_settings_window.child_window(title=friend,control_type="Button",found_index=0)
        friend_button.click_input()
        profile_window=friend_settings_window.child_window(class_name="ContactProfileWnd",control_type="Pane",framework_id='Win32')
        return profile_window,main_window
    
    @staticmethod
    def open_contacts(wechat_path:str=None,is_maximize:bool=True):
        '''
        该方法用于打开微信通信录界面\n
        Args:
            friend:\t好友或群聊备注名称,需提供完整名称\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        contacts=main_window.child_window(**SideBar.Contacts)
        contacts.set_focus()
        contacts.click_input()
        cancel_button=main_window.child_window(**Buttons.CancelButton)
        if cancel_button.exists():
            cancel_button.click_input()
        ContactsLists=main_window.child_window(**Main_window.ContactsList)
        rec=ContactsLists.rectangle()
        mouse.click(coords=(rec.right-5,rec.top))
        pyautogui.press('Home')
        pyautogui.press('pageup')
        return main_window

    @staticmethod
    def open_chat_history(friend:str,TabItem:str=None,search_pages:int=5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用于打开好友聊天记录界面\n
        Args:
            friend:\t好友备注名称,需提供完整名称\n
            TabItem:\t点击聊天记录顶部的Tab选项,默认为None,可选值为:文件,图片与视频,链接,音乐与音频,小程序,视频号,日期\n
            search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
            close_wechat:\t任务结束后是否关闭微信,默认关闭\n
        '''
        tabItems={'文件':TabItems.FileTabItem,'图片与视频':TabItems.PhotoAndVideoTabItem,'链接':TabItems.LinkTabItem,'音乐与音频':TabItems.MusicTabItem,'小程序':TabItems.MiniProgramTabItem,'视频号':TabItems.ChannelTabItem,'日期':TabItems.DateTabItem}
        if TabItem:
            if TabItem not in tabItems.keys():
                raise WrongParameterError('TabItem参数错误!')
        main_window=Tools.open_dialog_window(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
        chat_toolbar=main_window.child_window(**Main_window.ChatToolBar)
        chat_history_button=chat_toolbar.child_window(**Buttons.ChatHistoryButton)
        if not chat_history_button.exists():
            #公众号没有聊天记录这个按钮
            main_window.close()
            raise NotFriendError(f'非正常好友!无法打开聊天记录界面')
        chat_history_button.click_input()
        if close_wechat:
            main_window.close()
        chat_history_window=Tools.move_window_to_center(Independent_window.ChatHistoryWindow)
        if TabItem:
            chat_history_window.child_window(**tabItems[TabItem]).click_input()
        return chat_history_window,main_window

    @staticmethod
    def open_program_pane(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用来打开小程序面板\n
        Args:
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t小程序面板界面是否全屏,默认全屏。\n
            wechat_maximize:\t微信主界面是否全屏,默认全屏\n
            close_wechat:\t任务结束后是否关闭微信,默认关闭\n
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
        program_button=main_window.child_window(**SideBar.Miniprogram_pane)
        program_button.click_input()
        if close_wechat:
            main_window.close()
        program_window=Tools.move_window_to_center(Independent_window.MiniProgramWindow)
        if is_maximize:
            program_window.maximize()
        return program_window
    
    @staticmethod
    def open_top_stories(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用于打开看一看\n
        Args:
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t看一看界面是否全屏,默认全屏。\n
            wechat_maximize:\t微信主界面是否全屏,默认全屏\n
            close_wechat:\t任务结束后是否关闭微信,默认关闭\n
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
        
        top_stories_button=main_window.child_window(**SideBar.Topstories)
        top_stories_button.click_input()
        desktop=Desktop(**Independent_window.Desktop)
        top_stories_window=desktop.window(**Independent_window.TopStoriesWindow)
        if is_maximize:
            top_stories_window.maximize()
        if close_wechat:
            main_window.close()
        return top_stories_window

    @staticmethod
    def open_search(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用于打开搜一搜\n
        Args:
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t搜一搜界面是否全屏,默认全屏。\n
            wechat_maximize:\t微信主界面是否全屏,默认全屏\n
            close_wechat:\t任务结束后是否关闭微信,默认关闭\n
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
        
        search_button=main_window.child_window(**SideBar.Search)
        search_button.click_input()
        desktop=Desktop(**Independent_window.Desktop)
        search_window=desktop.window(**Independent_window.SearchWindow)
        if is_maximize:
            search_window.maximize()
        if close_wechat:
            main_window.close()
        return search_window    

    @staticmethod
    def open_channels(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用于打开视频号\n
        Args: 
            wechat_path:\\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t视频号界面是否全屏,默认全屏。\n
            wechat_maximize:\t微信主界面是否全屏,默认全屏\n
            close_wechat:\t任务结束后是否关闭微信,默认关闭\n  
        '''
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
        
        channel_button=main_window.child_window(**SideBar.Channel)
        channel_button.click_input()
        desktop=Desktop(**Independent_window.Desktop)
        channel_window=desktop.window(**Independent_window.ChannelWindow)
        if is_maximize:
            channel_window.maximize()
        if close_wechat:
            main_window.close()
        return channel_window
    
    @staticmethod
    def pull_messages(friend:str,number:int,parse:bool=True,search_pages:int=5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[str,str,str]|list[ListItemWrapper]:
        '''该方法用来从主界面右侧的聊天区域内获取指定条数的聊天记录消息\n
        Args:
            friend:\t好友或群聊备注\n
            number:\t聊天记录条数\n
            parse:\t是否解析聊天记录为文本(主界面右侧聊天区域内的聊天记录形式为ListItem),设置为False时返回的类型为ListItem\n
            search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为10,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏法搜索好友信息打开聊天界面\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信主界面是否全屏,默认全屏。\n
            close_wechat:\t任务结束后是否关闭微信,默认关闭\n
        Returns:
            (message_contents,message_senders,message_types):\t消息内容,发送消息对象,消息类型\n
            消息具体类型:\t{'文本','图片','视频','语音','文件','动画表情','视频号','链接','卡片链接','微信转账'}\n
            list[ListItemWrapper]:\t聊天消息的ListItem形式
        '''
        message_contents=[]
        message_senders=[]
        message_types=[]
        friendtype='好友'#默认是好友
        main_window=Tools.open_dialog_window(friend=friend,search_pages=search_pages,wechat_path=wechat_path,is_maximize=is_maximize)[1]
        chat_history_button=main_window.child_window(**Buttons.ChatHistoryButton)
        if not chat_history_button.exists():#没有聊天记录按钮是公众号或其他类型的东西
            raise NotFriendError(f'{friend}不是好友，无法获取聊天记录！')
        chatList=main_window.child_window(**Main_window.FriendChatList)#聊天区域内的消息列表
        scrollable=Tools.is_VerticalScrollable(chatList)
        viewMoreMesssageButton=main_window.child_window(**Buttons.CheckMoreMessagesButton)#查看更多消息按钮
        if len(chatList.children(control_type='ListItem'))==0:#没有聊天记录直接返回空列表
            if parse:
                return message_contents,message_senders,message_types
            else:
                return []
        video_call_button=main_window.child_window(**Buttons.VideoCallButton)
        if not video_call_button.exists():##没有视频聊天按钮是群聊
            friendtype='群聊'
        #if message.descendants(conrol_type)是用来筛选这个消息(control_type为ListItem)内有没有按钮(消息是人发的必然会有头像按钮这个UI,系统消息比如'8:55'没有这个UI)
        ListItems=[message for message in chatList.children(control_type='ListItem') if message.descendants(control_type='Button')]
        ListItems=[message for message in ListItems if message.window_text()!=Buttons.CheckMoreMessagesButton['title']]#产看更多消息内部也有按钮,所以需要筛选一下
        #点击聊天区域侧边栏和头像之间的位置来激活滑块,不直接main_window.click_input()是为了防止点到消息
        x,y=chatList.rectangle().left+8,(main_window.rectangle().top+main_window.rectangle().bottom)//2#
        if len(ListItems)>=number:#聊天区域内部不需要遍历就可以获取到的消息数量大于number条
            ListItems=ListItems[-number:]#返回从后向前数number条消息
        if len(ListItems)<number:#
            ##########################################################
            if scrollable:
                mouse.click(coords=(chatList.rectangle().right-10,chatList.rectangle().bottom-5))
                while len(ListItems)<number:
                    chatList.iface_scroll.SetScrollPercent(verticalPercent=0.0,horizontalPercent=1.0)#调用SetScrollPercent方法向上滚动,verticalPercent=0.0表示直接将scrollbar一下子置于顶部
                    mouse.scroll(coords=(x,y),wheel_dist=1000)
                    ListItems=[message for message in chatList.children(control_type='ListItem') if message.descendants(control_type='Button')]
                    ListItems=[message for message in ListItems if message.window_text()!=Buttons.CheckMoreMessagesButton['title']]
                    if not viewMoreMesssageButton.exists():#向上遍历时如果查看更多消息按钮不在存在说明已经到达最顶部,没有必要继续向上,直接退出循环
                        break
                ListItems=ListItems[-number:] 
            else:#无法滚动,说明就这么多了,有可能是刚添加好友或群聊或者是清空了聊天记录,只发了几条消息
                ListItems=ListItems[-number:] 
        #######################################################
        if close_wechat:
            main_window.close()
        if parse:
            for ListItem in ListItems:
                message_sender,message_content,message_type=Tools.parse_message_content(ListItem=ListItem,friendtype=friendtype)
                message_senders.append(message_sender)
                message_contents.append(message_content)
                message_types.append(message_type)
            return message_contents,message_senders,message_types
        else:
            return ListItems
    
    @staticmethod
    def parse_message_content(ListItem:ListItemWrapper,friendtype:str)->tuple[str,str,str]:
        '''
        该方法用来将主界面右侧聊天区域内的单个ListItem消息转换为文本,传入对象为Listitem\n
        Args:
            ListItem:主界面右侧聊天区域内ListItem形式的消息\n
            friendtype:聊天区域是群聊还是好友\n 
        Returns:
            message_sender:\t发送消息的对象\n
            message_content:\t发送的消息\n
            message_type:\t消息类型,具体类型:\n{'文本','图片','视频','语音','文件','动画表情','视频号','链接','聊天记录','引用消息','卡片链接','微信转账'}\n
        '''
        language=Tools.language_detector()
        message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
        message_content=''
        message_type=''
        #至于消息的内容那就需要仔细判断一下了
        #微信在链接的判定上比较模糊,音乐和链接最后统一都以卡片的形式在聊天记录中呈现,所以这里不区分音乐和链接,都以链接卡片的形式处理
        specialMegCN={'[图片]':'图片','[视频]':'视频','[动画表情]':'动画表情','[视频号]':'视频号','[链接]':'链接','[聊天记录]':'聊天记录'}
        specialMegEN={'[Photo]':'图片','[Video]':'视频','[Sticker]':'动画表情','[Channel]':'视频号','[Link]':'链接','[Chat History]':'聊天记录'}
        specialMegTC={'[圖片]':'图片','[影片]':'视频','[動態貼圖]':'动画表情','[影音號]':'视频号','[連結]':'链接','[聊天記錄]':'聊天记录'}
        #不同语言,处理消息内容时不同
        if language=='简体中文':
            pattern=r'\[语音\]\d+秒'
            if ListItem.window_text() in specialMegCN.keys():#内容在特殊消息中
                message_content=specialMegCN.get(ListItem.window_text())
                message_type=specialMegCN.get(ListItem.window_text())
            else:#文件,卡片链接,语音,以及正常的文本消息
                if re.match(pattern,ListItem.window_text()):#匹配是否是语音消息
                    try:#是语音消息就定位语音转文字结果
                        if friendtype=='群聊':
                            audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                        else:
                            audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                    except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                        message_content=ListItem.window_text()
                        message_type='文本'
                elif ListItem.window_text()=='[文件]':
                    filename=ListItem.descendants(control_type='Text')[0].window_text()
                    stem,extension=os.path.splitext(filename)
                    #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                    if not extension:
                        filename=ListItem.descendants(control_type='Text')[1].window_text()
                    message_content=f'{filename}'
                    message_type='文件'
                elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                    cardContent=ListItem.descendants(control_type='Text')
                    cardContent=[link.window_text() for link in cardContent]
                    message_content='卡片链接内容:'+','.join(cardContent)
                    message_type='卡片链接'
                    if ListItem.window_text()=='微信转账':
                        index=cardContent.index('微信转账')
                        message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                        message_type='微信转账'
                    if "引用  的消息 :" in ListItem.window_text():
                        splitlines=ListItem.window_text().splitlines()
                        message_content=f'{splitlines[0]}\t引用消息内容:{splitlines[1:]}'
                        message_type='引用消息'
                    if '小程序' in cardContent:
                        message_content='小程序内容:'+','.join(cardContent)
                        message_type='小程序'

                else:#正常文本
                    message_content=ListItem.window_text()
                    message_type='文本'
                
        if language=='英文':
            pattern=r'\[Audio\]\d+s'
            if ListItem.window_text() in specialMegEN.keys():
                message_content=specialMegEN.get(ListItem.window_text())
                message_type=specialMegEN.get(ListItem.window_text())
            else:#文件,卡片链接,语音,以及正常的文本消息
                if re.match(pattern,ListItem.window_text()):#匹配是否是语音消息
                    try:#是语音消息就定位语音转文字结果
                        if friendtype=='群聊':
                            audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                        else:
                            audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                    except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                        message_content=ListItem.window_text()
                        message_type='文本'
                elif ListItem.window_text()=='[File]':
                    filename=ListItem.descendants(control_type='Text')[0].window_text()
                    stem,extension=os.path.splitext(filename)
                    #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                    if not extension:
                        filename=ListItem.descendants(control_type='Text')[1].window_text()
                    message_content=f'{filename}'
                    message_type='文件'

                elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                    cardContent=ListItem.descendants(control_type='Text')
                    cardContent=[link.window_text() for link in cardContent]
                    message_content='卡片链接内容:'+','.join(cardContent)
                    message_type='卡片链接'
                    if ListItem.window_text()=='Weixin Transfer':
                        index=cardContent.index('Weixin Transfer')
                        message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                        message_type='微信转账'
                    if "Quote 's message:" in ListItem.window_text():
                        splitlines=ListItem.window_text().splitlines()
                        message_content=f'{splitlines[0]}\t引用消息内容:{splitlines[1:]}'
                        message_type='引用消息'
                    if 'Mini Programs' in cardContent:
                        message_content='小程序内容:'+','.join(cardContent)
                        message_type='小程序'
                    
                else:#正常文本
                    message_content=ListItem.window_text()
                    message_type='文本'
        
        if language=='繁体中文':
            pattern=r'\[語音\]\d+秒'
            if ListItem.window_text() in specialMegTC.keys():
                message_content=specialMegTC.get(ListItem.window_text())
                message_type=specialMegTC.get(ListItem.window_text())
            else:#文件,卡片链接,语音,以及正常的文本消息
                if re.match(pattern,ListItem.window_text()):#匹配是否是语音消息
                    try:#是语音消息就定位语音转文字结果
                        if friendtype=='群聊':
                            audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                        else:
                            audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                            message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                            message_type='语音'
                    except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                        message_content=ListItem.window_text()
                        message_type='文本'

                elif ListItem.window_text()=='[檔案]':
                    filename=ListItem.descendants(control_type='Text')[0].window_text()
                    stem,extension=os.path.splitext(filename)
                    #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                    if not extension:
                        filename=ListItem.descendants(control_type='Text')[1].window_text()
                    message_content=f'{filename}'
                    message_type='文件'
        
                elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                    cardContent=ListItem.descendants(control_type='Text')
                    cardContent=[link.window_text() for link in cardContent]
                    message_content='卡片链接内容:'+','.join(cardContent)
                    message_type='卡片链接'
                    if ListItem.window_text()=='微信轉賬':
                        index=cardContent.index('微信轉賬')
                        message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                        message_type='微信转账'
                    if "引用  的訊息 :" in ListItem.window_text():
                        splitlines=ListItem.window_text().splitlines()
                        message_content=f'{splitlines[0]}\t引用消息内容:{splitlines[1:]}'
                        message_type='引用消息'
                    if '小程式' in cardContent:
                        message_content='小程序内容:'+','.join(cardContent)
                        message_type='小程序'
                else:#正常文本
                    message_content=ListItem.window_text()
                    message_type='文本'

        return message_sender,message_content,message_type
    
    @staticmethod
    def pull_latest_message(chatList:ListViewWrapper)->tuple[str,str]|tuple[None,None]:#获取聊天界面内的聊天记录
        '''
        该方法用来获取聊天界面内的最新的一条聊天消息(非时间戳或系统消息:以下是新消息)\n
        返回值为最新的消息内容以及消息发送人,需要注意的是如果界面内没有消息或最新消息是系统消息\n
        那么返回None,None,该方法可以用来配合自动回复方法使用\n
        Args:
            chatList:打开好友的聊天窗口后的右侧聊天列表,该函数主要用内嵌于自动回复消息功能中使用\n
                因此传入的参数为主界面右侧的聊天列表,也就是Main_window.FriendChatList\n
            
        Returns:
            (content,sender):消息发送人\t最新的新消息内容
        Examples:
            ```
            from pywechat import Tools,Main_window,pull_latest_message
            edit_area,main_window=Tools.open_dialog_window(friend='路人甲')
            content,sender=pull_latest_message(chatList=main_window.child_window(**Main_window.FriendChatList))
            print(content,sender)
            ```
        '''
        #筛选消息，每条消息都是一个listitem
        if chatList.exists():
            if chatList.children():#如果聊天列表存在(不存在的情况:清空了聊天记录)
                ###################
                if chatList.children()[-1].descendants(control_type='Button') and chatList.children()[-1].window_text()!='':#必须是非系统消息也就是消息内部含有发送人按钮这个UI
                    content=chatList.children()[-1].window_text()
                    sender=chatList.children()[-1].descendants(control_type='Button')[0].window_text()
                    return content,sender
        return None,None

    @staticmethod
    def find_current_wxid():
        """
        该方法通过内存映射文件来检测当前登录的wxid,使用时必须登录微信,否则返回空字符串\n
        """
        wechat_process=None
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name']=='WeChat.exe':
                wechat_process=process
                break
        if not wechat_process:
            return ''
        #只要微信登录了,就一定会用到本地聊天文件保存位置:Wechat Files下的一个wxid开头的文件下的数据,
        #这个文件夹里包含了聊天纪录数据,联系人等库,聊天文件等内容
        wxid_pattern=re.compile(r"wxid_\w+\d+")   
        #wechat_process是进程句柄,通过这个进程句柄的memory_maps方法可以实现
        #内存映射文件检测
        for mem_map in wechat_process.memory_maps():
            match=wxid_pattern.search(mem_map.path)
            if match and "WeChat Files" in mem_map.path:
                return match.group()
        return ''

    @staticmethod
    def where_database_folder(open_folder:bool=False):
        '''
        该方法用来获取微信数据库存放路径,当微信未登录时只返回根目录,当微信登录时返回数据库存放路径\n
        Args:
            open_folder:\t是否打开数据库存放路径,默认不打开
        Returns:
            folder_path:\t数据库存放路径
        '''
        folder_path=''
        reg_path=r"Software\Tencent\WeChat"
        wxid=find_current_wxid()
        try:
            #查注册表
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                value=winreg.QueryValueEx(key,"FileSavePath")[0]
            if value=='MyDocument:':
                #注册表的值是MyDocument:的话路径是在c:\Users\用户名\Documents\WeChat Files\wxid_abc12356\FileStorage\Files下
                #wxid是当前登录的微信号,通过内存映射文件获取，必须是登录状态，不然最多只能获取到WCchat Files
                Userdocumens=os.path.expanduser(r'~\Documents')#c:\Users\用户名\Documents\
                root_dir=os.path.join(Userdocumens,'WeChat Files')#微信聊天记录存放根目录
                if wxid:#如果wxid不为空,那么可以继续获取到
                    folder_path=os.path.join(root_dir,wxid,'Msg')
                else:
                    folder_path=root_dir
            else:
                root_dir=os.path.join(value,r'\WeChat Files')
                if wxid:
                    folder_path=os.path.join(root_dir,wxid,'Msg')
                else:
                    folder_path=root_dir
                    wxid_dirs=[os.path.join(folder_path,dir) for dir in os.listdir(folder_path) if re.match(r'wxid_\w+\d+',dir)]
                    if len(wxid_dirs)==1:
                        folder_path=os.path.join(root_dir,wxid_dirs[0],'Msg')
                    if len(wxid_dirs)>1:
                        print(f'该设备登录过{len(wxid_dirs)}个微信账号,未登录微信只能获取到根目录!\n请登录后重试!')
                        print(f'当前设备所有登录过的微信账号存放数据的文件夹路径为:\n{wxid_dirs}')
            if open_folder:
                os.startfile(folder_path)
            return folder_path
        except Exception:#注册表查询失败,未安装微信或者注册表被删除了
            raise NotInstalledError

    @staticmethod
    def where_chatfiles_folder(open_folder:bool=False):
        '''
        该方法用来获取微信聊天文件存放路径,当微信未登录时只返回根目录,当微信登录时返回聊天文件存放路径\n\n
        Args:
            open_folder:\t是否打开聊天文件存放路径,默认不打开
        Returns:
            folder_path:\t聊天文件存放路径
        '''
        folder_path=''
        reg_path=r"Software\Tencent\WeChat"
        wxid=find_current_wxid()
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                value=winreg.QueryValueEx(key,"FileSavePath")[0]
            if value=='MyDocument:':#注册表的值是MyDocument:的话
                #路径是在c:\Users\用户名\Documents\WeChat Files\wxid_abc12356\FileStorage\Files下
                #wxid是当前登录的微信号,通过内存映射文件获取，必须是登录状态，不然最多只能获取到WCchat Files
                Userdocumens=os.path.expanduser(r'~\Documents')#c:\Users\用户名\Documents\
                root_dir=os.path.join(Userdocumens,'WeChat Files')#微信聊天记录存放根目录
                if wxid:#如果wxid不为空,那么可以继续获取到
                    folder_path=os.path.join(root_dir,wxid,'FileStorage','File')
                else:
                    folder_path=root_dir
            else:
                root_dir=os.path.join(value,r'\WeChat Files')
                if wxid:
                    folder_path=os.path.join(root_dir,wxid,'FileStorage','File')
                else:
                    folder_path=root_dir
                    wxid_dirs=[os.path.join(folder_path,dir) for dir in os.listdir(folder_path) if re.match(r'wxid_\w+\d+',dir)]
                    if len(wxid_dirs)==1:
                        folder_path=os.path.join(root_dir,wxid_dirs[0],'FileStorage','File')
                    if len(wxid_dirs)>1:
                        print(f'当前设备登录过{len(wxid_dirs)}个微信账号,未登录微信只能获取到根目录!请登录后尝试!')
                        print(f'当前设备所有登录过的微信账号存放数据的文件夹路径为:\n{wxid_dirs}')
            if open_folder:
                os.startfile(folder_path)
            return folder_path
        except Exception:
            raise NotInstalledError
    
    @staticmethod
    def NativeSaveFile(folder_path):
        '''
        该方法用来处理微信内部点击另存为后弹出的windows本地保存文件窗口\n
        Args:
            folder_path:保存文件的文件夹路径
        '''
        desktop=Desktop(**Independent_window.Desktop)
        save_as_window=desktop.window(**Windows.NativeSaveFileWindow)
        confirm_save=save_as_window.child_window(control_type='Button',found_index=0)
        path_bar=save_as_window.child_window(class_name='ToolbarWindow32',control_type='ToolBar',auto_id='1001')
        if re.search(r':\s*(.*)',path_bar.window_text()).group(1)!=folder_path:
            rec=path_bar.rectangle()
            mouse.click(coords=(rec.right-5,int(rec.top+rec.bottom)//2))
            pyautogui.press('backspace')
            pyautogui.hotkey('ctrl','v',_pause=False)
            pyautogui.press('enter')
            time.sleep(0.5)
        pyautogui.hotkey('alt','s')
        time.sleep(1)
        if confirm_save.exists():
            confirm_save.click_input()

    @staticmethod
    def NativeChooseFolder(folder_path):
        '''
        该方法用来处理微信内部点击选择文件夹后弹出的windows本地选择文件夹窗口\n
        Args:
            folder_path:保存文件的文件夹路径
        '''
        #如果path_bar上的内容与folder_path不一致,那么删除复制粘贴
        #如果一致,点击选择文件夹窗口
        Systemsettings.copy_text_to_windowsclipboard(folder_path)
        desktop=Desktop(**Independent_window.Desktop)
        save_as_window=desktop.window(**Windows.NativeChooseFolderWindow)
        path_bar=save_as_window.child_window(class_name='ToolbarWindow32',control_type='ToolBar',auto_id='1001')
        if re.search(r':\s*(.*)',path_bar.window_text()).group(1)!=folder_path:
            rec=path_bar.rectangle()
            mouse.click(coords=(rec.right-5,int(rec.top+rec.bottom)//2))
            pyautogui.press('backspace')
            pyautogui.hotkey('ctrl','v',_pause=False)
            pyautogui.press('enter')
            time.sleep(0.5)
        choose_folder_button=save_as_window.child_window(control_type='Button',title='选择文件夹')
        choose_folder_button.click_input()

class API():
    '''这个模块包括打开指定名称小程序,打开制定名称微信公众号的功能\n
    若有其他自动化开发者需要在微信内的这两个功能下进行自动化操作可调用此模块\n
    '''
    @staticmethod
    def open_wechat_miniprogram(name:str,load_delay:float=2.5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True,close_program_pane:bool=True):
        '''
        该方法用于打开指定小程序\n
        Args:
            name:\t微信小程序名字\n
            load_delay:\t搜索小程序名称后等待时长,默认为2.5秒\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
            close_wechat:\t任务结束后是否关闭微信,默认关闭\n
        '''
        desktop=Desktop(**Independent_window.Desktop)
        if Tools.judge_independant_window_state(Independent_window.MiniProgramWindow)!='界面未打开,需进入微信打开':
            HWND=win32gui.FindWindow(Independent_window.MiniProgramWindow.get('class_name'),Independent_window.MiniProgramWindow.get('title'))
            win32gui.ShowWindow(HWND,1)
            program_window=Tools.move_window_to_center(Window_handle=HWND)
            miniprogram_tab=program_window.child_window(title='小程序',control_type='TabItem')
            if miniprogram_tab.exists():
                miniprogram_tab.click_input()
            else:
                program_window.close()
                program_window=Tools.open_program_pane(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
        else:
            program_window=Tools.open_program_pane(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
        miniprogram_tab=program_window.child_window(title='小程序',control_type='TabItem')
        miniprogram_tab.click_input()
        time.sleep(load_delay)
        try:
            more=program_window.child_window(title='更多',control_type='Text',found_index=0)#小程序面板内的更多文本
        except ElementNotFoundError:
            program_window.close()
            print('网络不良,请尝试增加load_delay时长,或更换网络')
        rec=more.rectangle()
        mouse.click(coords=(rec.right+20,rec.top-50))
        up=5
        search=program_window.child_window(control_type='Edit',title='搜索小程序')
        while not search.exists():
            mouse.click(coords=(rec.right+20,rec.top-50-up))
            search=program_window.child_window(control_type='Edit',title='搜索小程序')
            up+=5
        search.click_input()
        Systemsettings.copy_text_to_windowsclipboard(name)
        pyautogui.hotkey('ctrl','v',_pause=False)
        pyautogui.press("enter")
        time.sleep(load_delay)
        try:
            search_result=program_window.child_window(control_type="Document",class_name="Chrome_RenderWidgetHostHWND")
            text=search_result.child_window(title=name,control_type='Text',found_index=0)
            text.click_input()
            if close_program_pane:
                program_window.close()
            program=desktop.window(control_type='Pane',title=name)
            return program
        except ElementNotFoundError:
            program_window.close()
            raise NoResultsError('查无此小程序!')
        
    @staticmethod
    def open_wechat_official_account(name:str,load_delay:float=1,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用于打开指定的微信公众号\n
        Args:
            name:\t微信公众号名称\n
            load_delay:\t加载搜索公众号结果的时间,单位:s\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:\t微信界面是否全屏,默认全屏。\n
        '''
        desktop=Desktop(**Independent_window.Desktop)
        try:
            search_window=Tools.open_search(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
            time.sleep(load_delay)
        except ElementNotFoundError:
            search_window.close()
            print('网络不良,请尝试增加load_delay时长,或更换网络')
        try:
            official_acount_button=search_window.child_window(**Buttons.OfficialAcountButton)
            official_acount_button.click_input()
        except ElementNotFoundError:
            search_window.close()
            print('网络不良,请尝试增加load_delay时长,或更换网络')
        search=search_window.child_window(control_type='Edit',found_index=0)
        search.click_input()
        Systemsettings.copy_text_to_windowsclipboard(name)
        pyautogui.hotkey('ctrl','v')
        pyautogui.press('enter')
        time.sleep(load_delay)
        try:
            search_result=search_window.child_window(control_type="Button",found_index=1,framework_id="Chrome")
            search_result.click_input()
            official_acount_window=desktop.window(**Independent_window.OfficialAccountWindow)
            search_window.close()
            return official_acount_window
        except ElementNotFoundError:
            search_window.close()
            raise NoResultsError('查无此公众号!')
        
    @staticmethod
    def search_channels(search_content:str,load_delay:float=1,wechat_path:str=None,wechat_maximize:bool=True,is_maximize:bool=True,close_wechat:bool=True):
        '''
        该方法用于打开视频号并搜索指定内容\n
        Args:
            search_content:在视频号内待搜索内容\n
            load_delay:加载查询结果的时间,单位:s\n
            wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
            is_maximize:微信界面是否全屏,默认全屏。\n
        '''
        Systemsettings.copy_text_to_windowsclipboard(search_content)
        channel_widow=Tools.open_channels(wechat_maximize=wechat_maximize,is_maximize=is_maximize,wechat_path=wechat_path,close_wechat=close_wechat)
        search_bar=channel_widow.child_window(control_type='Edit',title='搜索',framework_id='Chrome')
        while not search_bar.exists():
            time.sleep(0.1)
            search_bar=channel_widow.child_window(control_type='Edit',title='搜索',framework_id='Chrome')
        search_bar.click_input()
        pyautogui.hotkey('ctrl','v')
        pyautogui.press('enter')
        time.sleep(load_delay)
        try:
            search_result=channel_widow.child_window(control_type='Document',title=f'{search_content}_搜索')
            return channel_widow
        except ElementNotFoundError:
            channel_widow.close()
            print('网络不良,请尝试增加load_delay时长,或更换网络')
    
    
def is_wechat_running():
    '''
    该方法通过检测当前windows系统的进程中\n
    是否有WeChat.exe该项进程来判断微信是否在运行
    '''
    wmi=win32com.client.GetObject('winmgmts:')
    processes=wmi.InstancesOf('Win32_Process')
    for process in processes:
        if process.Name.lower()=='Wechat.exe'.lower():
            return True
    return False
    
def language_detector():
    """
    该函数查询注册表来检测当前微信的语言版本\n
    """
    #微信3.9版本的一般注册表路径
    reg_path=r"Software\Tencent\WeChat"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            value=winreg.QueryValueEx(key,"LANG_ID")[0]
            language_map={
                0x00000009: '英文',
                0x00000004: '简体中文',
                0x00000404: '繁体中文'
            }
            return language_map.get(value)
    except FileNotFoundError:
        raise NotInstalledError

def open_wechat(wechat_path:str=None,is_maximize:bool=True):
    '''
    该函数用来打开微信\n
    Args:
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。
    微信的打开分为四种情况:\n
    1.未登录,此时调用该函数会启动wechat_path路径下的wechat.exe,在弹出的登录界面中点击进入微信打开微信主界面\n
    启动并点击登录进入微信(注:需勾选自动登录按钮,否则启动后为扫码登录)\n
    2.未登录但已弹出微信的登录界面,此时会自动点击进入微信打开微信\n
    注意:未登录的情况下打开微信需要在手机端第一次扫码登录后勾选自动登入的选项,否则启动微信后\n
    聊天界面没有进入微信按钮,将会触发异常提示扫码登录\n
    3.已登录，主界面最小化在状态栏，此时调用该函数会直接打开后台中的微信。\n
    4.已登录，主界面关闭，此时调用该函数会打开已经关闭的微信界面。
    '''
    #最多尝试40次，每次间隔0.5秒，最多20秒无法打开微信则抛出异常
    max_retry_times=40
    retry_interval=0.5
    #处理登录界面的闭包函数，点击进入微信，若微信登录界面存在直接传入窗口句柄，否则自己查找
    def handle_login_window(wechat_path=wechat_path,max_retry_times=max_retry_times, retry_interval=retry_interval, is_maximize=is_maximize):
        counter=0
        if wechat_path:#看看有没有传入wechat_path
            subprocess.Popen(wechat_path)
        if not wechat_path:#没有传入就自己找
            wechat_path=Tools.find_wechat_path(copy_to_clipboard=False)
            subprocess.Popen(wechat_path)
        #没有传入登录界面句柄，需要自己查找(此时对应的情况是微信未启动)
        login_window_handle=win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
        while not login_window_handle:
            login_window_handle= win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
            if login_window_handle:
                break
            counter+=1
            time.sleep(0.2)
            if counter>=max_retry_times:
                raise NoResultsError(f'微信打开失败,请检查网络连接或者微信是否正常启动！')
        #移动登录界面到屏幕中央
        login_window=Tools.move_window_to_center(Login_window.LoginWindow,login_window_handle)
        #点击登录按钮,等待主界面出现并返回
        try:
            login_button=login_window.child_window(**Login_window.LoginButton)
            login_button.set_focus()
            login_button.click_input()
            main_window_handle = 0
            while not main_window_handle:
                main_window_handle=win32gui.FindWindow(Main_window.MainWindow['class_name'],None)
                if main_window_handle:
                    break
                counter+=1
                time.sleep(retry_interval)
                if counter>=max_retry_times:
                    raise NetWorkNotConnectError
            main_window=Tools.move_window_to_center(Window_handle=main_window_handle)
            if is_maximize:
                main_window.maximize()
            NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
            if NetWorkErrotText.exists():
                main_window.close()
                raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
            return main_window 
        except ElementNotFoundError:
            raise ScanCodeToLogInError
    #open_wechat函数的主要逻辑：
    if Tools.is_wechat_running():#微信如果已经打开无需登录可以直接连接
        #同时查找主界面与登录界面句柄，二者有一个存在都证明微信已经启动
        main_window_handle=win32gui.FindWindow(Main_window.MainWindow['class_name'],None)
        login_window_handle=win32gui.FindWindow(Login_window.LoginWindow['class_name'],None)
        if main_window_handle:
            #威信运行时有最小化，主界面可见未关闭,主界面不可见关闭三种情况
            if win32gui.IsWindowVisible(main_window_handle):#主界面可见包含最小化
                if win32gui.GetWindowPlacement(main_window_handle)[1]==win32con.SW_SHOWMINIMIZED:#主界面最小化
                    win32gui.ShowWindow(main_window_handle,win32con.SW_SHOWNORMAL)
                    main_window=Tools.move_window_to_center(Window_handle=main_window_handle) 
                    if is_maximize:
                        main_window.maximize()
                    NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                    if NetWorkErrotText.exists():
                        main_window.close()
                        raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                    return main_window
                else:#主界面存在且未最小化
                    main_window=Tools.move_window_to_center(Window_handle=main_window_handle)
                    if is_maximize:
                        main_window.maximize()
                    NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                    if NetWorkErrotText.exists():
                        main_window.close()
                        raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                    return main_window
            else:#主界面不可见
                #打开过主界面，关闭掉了，需要重新打开 
                win32gui.ShowWindow(main_window_handle,win32con.SW_SHOWNORMAL)
                main_window=Tools.move_window_to_center(Window_handle=main_window_handle)
                if is_maximize:
                    main_window.maximize()
                NetWorkErrotText=main_window.child_window(**Texts.NetWorkError)
                if NetWorkErrotText.exists():
                    main_window.close()
                    raise NetWorkNotConnectError(f'未连接网络,请连接网络后再进行后续自动化操作！')
                return main_window
        if login_window_handle:#微信启动了，但是.是登录界面在桌面上，不是主界面
            #处理登录界面
            return handle_login_window(max_retry_times,retry_interval,is_maximize)
    else:#微信未启动，需要先使用subprocess.Popen启动微信弹出登录界面后点击进入微信
        #处理登录界面
        return handle_login_window(max_retry_times,retry_interval,is_maximize)
                       
def find_friend_in_MessageList(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5):
    '''
    该函数用于在会话列表中查询是否存在待查询好友。\n
    Args:
        friend:\t好友或群聊备注名称,需提供完整名称\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
        search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
    若存在:返回值为 (chat,main_window) 同时返回好友聊天界面与主界面\n
    否则:返回值为 (None,main_window)只返回主界面\n
    '''
    def get_window(friend):
        '''
        用来返回会话列表中满足条件的好友,如果好友是最后一个返回其在会话列表中的索引
        '''
        message_list=message_list_pane.children(control_type='ListItem')
        buttons=[friend.children()[0].children()[0] for friend in message_list]
        friend_button=None
        for i in range(len(buttons)):
            if friend == buttons[i].texts()[0]:
                friend_button=buttons[i]
                break
        if i==len(buttons)-1:
            return friend_button,i
        else:
            return friend_button,None
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    #先看看当前微信右侧界面是不是聊天界面可能存在不是聊天界面的情况比如是纯白色的微信的icon
    current_chat=main_window.child_window(**Main_window.CurrentChatWindow)
    chat_button=main_window.child_window(**SideBar.Chats)
    message_list_pane=main_window.child_window(**Main_window.ConversationList)
    if not message_list_pane.exists():
        chat_button.click_input()
    if not message_list_pane.is_visible():
        chat_button.click_input()
    rectangle=message_list_pane.rectangle()
    scrollable=Tools.is_VerticalScrollable(message_list_pane)
    if is_maximize:
        activateScollbarPosition=(rectangle.right-5, rectangle.top+20)
    if not is_maximize:
        activateScollbarPosition=(rectangle.right-4, rectangle.top+20)
    if current_chat.exists():#如果当前微信主界面右侧是聊天界面，
        if current_chat.window_text()==friend:#如果当前主界面是某个好友的聊天界面且聊天界面顶部的名称为好友名称，直接返回结果
            chat=current_chat
            chat.click_input()
            return chat,main_window
        else:#否则在消息列表中查找
            message_list=message_list_pane.children(control_type='ListItem')
            if len(message_list)==0:
                return None,main_window
            if not scrollable:#消息列表中好友数量小于10，无法滚动，直接在消息列表中查找
                friend_button,index=get_window(friend)
                if friend_button:
                    if index:
                        #最后一个
                        rec=friend_button.rectangle()
                        mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                        chat=main_window.child_window(title=friend,control_type='Edit')
                    else:
                        friend_button.click_input()
                        chat=main_window.child_window(title=friend,control_type='Edit')
                    return chat,main_window
                else:
                    return None,main_window
            if scrollable:#会话列表可以滚动，滚动查找
                rectangle=message_list_pane.rectangle()
                mouse.click(coords=activateScollbarPosition)
                pyautogui.press('Home')
                for _ in range(search_pages):
                    friend_button,index=get_window(friend)
                    if friend_button:
                        if index:
                            rec=friend_button.rectangle()
                            mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                            chat=main_window.child_window(title=friend,control_type='Edit')
                        else:
                            friend_button.click_input()
                            chat=main_window.child_window(title=friend,control_type='Edit') 
                        break
                    else:
                        pyautogui.press("pagedown")
                        time.sleep(0.5)
                #看看是否找到了好友
                chat=main_window.child_window(title=friend,control_type='Edit')
                if chat.exists():
                    return chat,main_window
                else:
                    return None,main_window
                
    else:#右侧不是聊天界面，可能刚进入微信右侧是纯白色icon或者右侧是无法发送消息的公众号界面等，这时直接在消息列表中滚动查找
        message_list=message_list_pane.children(control_type='ListItem')
        if len(message_list)==0:
            return None,main_window
        if not scrollable:
            friend_button,index=get_window(friend)
            if friend_button:
                if index:
                    rec=friend_button.rectangle()
                    mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                    chat=main_window.child_window(title=friend,control_type='Edit')
                else:
                    friend_button.click_input()
                    chat=main_window.child_window(title=friend,control_type='Edit')
                return chat,main_window
            else:
                return None,main_window
        if scrollable:
            rectangle=message_list_pane.rectangle()
            mouse.click(coords=activateScollbarPosition)
            pyautogui.press('Home')
            for _ in range(search_pages):
                friend_button,index=get_window(friend)
                if friend_button:
                    if index:
                        rec=friend_button.rectangle()
                        mouse.click(coords=(int(rec.left+rec.right)//2,rec.top-12))
                        chat=main_window.child_window(title=friend,control_type='Edit')
                    else:
                        friend_button.click_input()
                        chat=main_window.child_window(title=friend,control_type='Edit')  
                    break
                else:
                    pyautogui.press("pagedown")
                    time.sleep(0.5)
            mouse.click(coords=activateScollbarPosition)
            pyautogui.press('Home')
            chat=main_window.child_window(title=friend,control_type='Edit')
            if chat.exists():
                return chat,main_window
            else:
                return None,main_window
            
def open_dialog_window(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5): 
    '''
    该函数用于打开某个好友的聊天窗口\n
    Args:
        friend:\t好友或群聊备注名称,需提供完整名称\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
        search_pages:在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
    Returns:
        (edit_area,main_window):\nedit_area:主界面右侧下方消息编辑区域,main_window:微信主界面
    '''
    def is_in_searh_result(friend,search_result):#查看搜索列表里有没有名为friend的listitem
        listitems=search_result.children(control_type="ListItem")
        names=[item for item in listitems if item.descendants(control_type='Button')]
        names=[item.window_text() for item in names]
        if friend in names:
            return True
        else:
            return False
    #如果search_pages不为0,即需要在会话列表中滚动查找时，使用find_friend_in_Messagelist方法找到好友,并点击打开对话框
    if search_pages:
        chat,main_window=Tools.find_friend_in_MessageList(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
        chat_button=main_window.child_window(**SideBar.Chats)
        if is_maximize:
            main_window.maximize()
        if chat :#chat不为None,即说明find_friend_in_MessageKist找到了聊天窗口chat,直接返回结果
            return chat,main_window
        else:  #chat为None没有在会话列表中找到好友,直接在顶部搜索栏中搜索好友
            #先点击侧边栏的聊天按钮切回到聊天主界面
            #顶部搜索按钮搜索好友
            search=main_window.child_window(**Main_window.Search).wait(wait_for='visible',retry_interval=0.1,timeout=3)
            search.click_input()
            Systemsettings.copy_text_to_windowsclipboard(friend)
            pyautogui.hotkey('ctrl','v')
            search_results=main_window.child_window(**Main_window.SearchResult)
            time.sleep(1)
            if is_in_searh_result(friend=friend,search_result=search_results):
                result=search_results.children(control_type='ListItem',title=friend)[0]
                result.click_input()
                chat=main_window.child_window(title=friend,control_type='Edit')
                return chat,main_window #同时返回搜索到的该好友的聊天窗口与主界面！若只需要其中一个需要使用元祖索引获取。
            else:#搜索结果栏中没有关于传入参数friend好友昵称或备注的搜索结果，关闭主界面,引发NosuchFriend异常
                chat_button.click_input()
                main_window.close()
                raise NoSuchFriendError
    else: #searchpages为0，不在会话列表查找
        #这部分代码先判断微信主界面是否可见,如果可见不需要重新打开,这在多个close_wechat为False需要进行来连续操作的方式使用时要用到
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        chat_button=main_window.child_window(**SideBar.Chats)
        message_list_pane=main_window.child_window(**Main_window.ConversationList)
        #先看看当前聊天界面是不是好友的聊天界面
        current_chat=main_window.child_window(**Main_window.CurrentChatWindow)
        #如果当前主界面是某个好友的聊天界面且聊天界面顶部的名称为好友名称，直接返回结果
        if current_chat.exists() and friend==current_chat.window_text():
            chat=current_chat
            chat.click_input()
            return chat,main_window
        else:#否则直接从顶部搜索栏出搜索结果
            #如果会话列表不存在或者不可见的话才点击一下聊天按钮
            if not message_list_pane.exists():
                chat_button.click_input()
            if not message_list_pane.is_visible():
                chat_button.click_input()            
            chat_button.click_input()
            search=main_window.child_window(**Main_window.Search)
            search.click_input()
            Systemsettings.copy_text_to_windowsclipboard(friend)
            pyautogui.hotkey('ctrl','v')
            search_results=main_window.child_window(**Main_window.SearchResult)
            time.sleep(1)
            if is_in_searh_result(friend=friend,search_result=search_results):
                result=search_results.children(control_type='ListItem',title=friend)[0]
                result.click_input()
                chat=main_window.child_window(title=friend,control_type='Edit')
                return chat,main_window #同时返回该好友的聊天窗口与主界面！若只需要其中一个需要使用元祖索引获取。
            else:
                chat_button.click_input()
                main_window.close()
                raise NoSuchFriendError


def open_settings(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
    '''
    该函数用来打开微信设置界面。注意,有时微信的设置界面会出现点击设置按钮后无法正常弹出,这是微信自身的Bug\n
    Args:
        wechat_path:微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
                尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
                传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:微信界面是否全屏,默认全屏。\n
        close_wechat:任务结束后是否关闭微信,默认关闭\n
    ''' 
    SettingsWindowhandle=win32gui.FindWindow(Independent_window.SettingWindow.get('class_name'),Independent_window.SettingWindow.get('title'))
    if SettingsWindowhandle:
        win32gui.ShowWindow(SettingsWindowhandle,1)  
    else:
        main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
        setting=main_window.child_window(**SideBar.SettingsAndOthers)
        setting.click_input()
        settings_menu=main_window.child_window(**Main_window.SettingsMenu)
        settings_button=settings_menu.child_window(**Buttons.SettingsButton)
        settings_button.click_input() 
        time.sleep(2)
    desktop=Desktop(**Independent_window.Desktop)
    settings_window=desktop.window(**Independent_window.SettingWindow)
    if close_wechat:
        main_window.close()
    return settings_window

def open_wechat_moments(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
    '''
    该函数用于打开微信朋友圈\n
    Args:
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
        close_wechat:\t任务结束后是否关闭微信,默认关闭\n
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    
    moments_button=main_window.child_window(**SideBar.Moments)
    moments_button.click_input()
    moments_window=Tools.move_window_to_center(Independent_window.MomentsWindow)
    moments_window.child_window(**Buttons.RefreshButton).click_input()
    if close_wechat:
        main_window.close()
    return moments_window
   
def open_wechat_miniprogram(name:str,load_delay:float=2.5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True,close_program_pane:bool=True):
    '''
    该函数用于打开指定小程序\n
    Args:
        name:\t微信小程序名字\n
        load_delay:\t搜索小程序名称后等待时长,默认为2.5秒\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
        close_wechat:\t任务结束后是否关闭微信,默认关闭\n
    '''
    desktop=Desktop(**Independent_window.Desktop)
    if Tools.judge_independant_window_state(Independent_window.MiniProgramWindow)!='界面未打开,需进入微信打开':
        HWND=win32gui.FindWindow(Independent_window.MiniProgramWindow.get('class_name'),Independent_window.MiniProgramWindow.get('title'))
        win32gui.ShowWindow(HWND,1)
        program_window=Tools.move_window_to_center(Window_handle=HWND)
        miniprogram_tab=program_window.child_window(title='小程序',control_type='TabItem')
        if miniprogram_tab.exists():
            miniprogram_tab.click_input()
        else:
            program_window.close()
            program_window=Tools.open_program_pane(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
    else:
        program_window=Tools.open_program_pane(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
    miniprogram_tab=program_window.child_window(title='小程序',control_type='TabItem')
    miniprogram_tab.click_input()
    time.sleep(load_delay)
    try:
        more=program_window.child_window(title='更多',control_type='Text',found_index=0)#小程序面板内的更多文本
    except ElementNotFoundError:
        program_window.close()
        print('网络不良,请尝试增加load_delay时长,或更换网络')
    rec=more.rectangle()
    mouse.click(coords=(rec.right+20,rec.top-50))
    up=5
    search=program_window.child_window(control_type='Edit',title='搜索小程序')
    while not search.exists():
        mouse.click(coords=(rec.right+20,rec.top-50-up))
        search=program_window.child_window(control_type='Edit',title='搜索小程序')
        up+=5
    search.click_input()
    Systemsettings.copy_text_to_windowsclipboard(name)
    pyautogui.hotkey('ctrl','v',_pause=False)
    pyautogui.press("enter")
    time.sleep(load_delay)
    try:
        search_result=program_window.child_window(control_type="Document",class_name="Chrome_RenderWidgetHostHWND")
        text=search_result.child_window(title=name,control_type='Text',found_index=0)
        text.click_input()
        if close_program_pane:
            program_window.close()
        program=desktop.window(control_type='Pane',title=name)
        return program
    except ElementNotFoundError:
        program_window.close()
        raise NoResultsError('查无此小程序!')
    
def open_wechat_official_account(name:str,load_delay:float=1,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
    '''
    该函数用于打开指定的微信公众号\n
    Args:
        name:\t微信公众号名称\n
        load_delay:\t加载搜索公众号结果的时间,单位:s\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
    '''
    desktop=Desktop(**Independent_window.Desktop)
    try:
        search_window=Tools.open_search(wechat_path=wechat_path,is_maximize=is_maximize,close_wechat=close_wechat)
        
        time.sleep(load_delay)
    except ElementNotFoundError:
        search_window.close()
        print('网络不良,请尝试增加load_delay时长,或更换网络')
    try:
        official_acount_button=search_window.child_window(**Buttons.OfficialAcountButton)
        official_acount_button.click_input()
    except ElementNotFoundError:
        search_window.close()
        print('网络不良,请尝试增加load_delay时长,或更换网络')
    search=search_window.child_window(control_type='Edit',found_index=0)
    search.click_input()
    Systemsettings.copy_text_to_windowsclipboard(name)
    pyautogui.hotkey('ctrl','v')
    pyautogui.press('enter')
    time.sleep(load_delay)
    try:
        search_result=search_window.child_window(control_type="Button",found_index=1,framework_id="Chrome")
        search_result.click_input()
        official_acount_window=desktop.window(**Independent_window.OfficialAccountWindow)
        search_window.close()
        return official_acount_window
    except ElementNotFoundError:
        search_window.close()
        raise NoResultsError('查无此公众号!')
    
def open_contacts(wechat_path:str=None,is_maximize:bool=True):
    '''
    该函数用于打开微信通信录界面\n
    Args:
        friend:\t好友或群聊备注名称,需提供完整名称\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    contacts=main_window.child_window(**SideBar.Contacts)
    contacts.set_focus()
    contacts.click_input()
    cancel_button=main_window.child_window(**Buttons.CancelButton)
    if cancel_button.exists():
        cancel_button.click_input()
    ContactsLists=main_window.child_window(**Main_window.ContactsList)
    rec=ContactsLists.rectangle()
    mouse.click(coords=(rec.right-5,rec.top))
    pyautogui.press('Home')
    pyautogui.press('pageup')
    return main_window

def open_friend_settings(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5):
    '''
    该函数用于打开好友设置界面\n
    Args:
        friend\t:好友备注名称,需提供完整名称\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
        search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
    '''
    main_window=Tools.open_dialog_window(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
    
    try:
        ChatMessage=main_window.child_window(**Buttons.ChatMessageButton)
        ChatMessage.click_input()
        friend_settings_window=main_window.child_window(**Main_window.FriendSettingsWindow)
    except ElementNotFoundError:
        main_window.close()
        raise NotFriendError(f'非正常好友,无法打开设置界面！')
    return friend_settings_window,main_window

def open_friend_settings_menu(friend:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5):
    '''
    该方法用于打开好友设置界面\n
    Args:
        friend:\t好友备注名称,需提供完整名称\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
        search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
    '''
    friend_settings_window,main_window=Tools.open_friend_settings(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)
    friend_button=friend_settings_window.child_window(title=friend,control_type="Button",found_index=0)
    friend_button.click_input()
    profile_window=friend_settings_window.child_window(class_name="ContactProfileWnd",control_type="Pane",framework_id='Win32')
    more_button=profile_window.child_window(**Buttons.MoreButton)
    more_button.click_input()
    friend_menu=profile_window.child_window(control_type="Menu",title="",class_name='CMenuWnd',framework_id='Win32')
    return friend_menu,friend_settings_window,main_window

def open_collections(wechat_path:str=None,is_maximize:bool=True):
    '''
    该函数用于打开收藏界面\n
    Args:
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    collections_button=main_window.child_window(**SideBar.Collections)
    collections_button.click_input()
    return main_window

def open_group_settings(group_name:str,wechat_path:str=None,is_maximize:bool=True,search_pages:int=5):
    '''
    该函数用来打开群聊设置界面\n
    Args:
        group_name:\t群聊备注名称,需提供完整名称\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
        search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
    '''
    main_window=Tools.open_dialog_window(friend=group_name,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
    ChatMessage=main_window.child_window(**Buttons.ChatMessageButton)
    ChatMessage.click_input()
    group_settings_window=main_window.child_window(**Main_window.GroupSettingsWindow)
    group_settings_window.child_window(**Texts.GroupNameText).click_input()
    return group_settings_window,main_window
    
def open_chat_files(wechat_path:str=None,wechat_maximize:bool=True,is_maximize:bool=True,close_wechat:bool=True):
    '''
    该函数用于打开聊天文件\n
    Args:
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        wechat_maximize:微信界面是否全屏,默认全屏\n
        is_maximize:\t聊天文件界面是否全屏,默认全屏。\n
        close_wechat:\t任务结束后是否关闭微信,默认关闭\n
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
    moments_button=main_window.child_window(**SideBar.ChatFiles)
    moments_button.click_input()
    desktop=Desktop(**Independent_window.Desktop)
    filelist_window=desktop.window(**Independent_window.ChatFilesWindow)
    if is_maximize:
        filelist_window.maximize()
    if close_wechat:
        main_window.close()
    return filelist_window
    
def open_friend_profile(friend:str,wechat_path:str=None,is_maximize:bool=True):
    '''
    该函数用于打开好友个人简介界面\n
    Args:
        friend:\t好友备注名称,需提供完整名称\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t信界面是否全屏,默认全屏。\n
        search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
    '''
    friend_settings_window,main_window=Tools.open_friend_settings(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize)
    friend_button=friend_settings_window.child_window(title=friend,control_type="Button",found_index=0)
    friend_button.click_input()
    profile_window=friend_settings_window.child_window(class_name="ContactProfileWnd",control_type="Pane",framework_id='Win32')
    return profile_window,main_window

def open_program_pane(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True):
    '''
    该函数用来打开小程序面板\n
    Args:
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t小程序面板界面是否全屏,默认全屏。\n
        wechat_maximize:\t微信主界面是否全屏,默认全屏\n
        close_wechat:\t任务结束后是否关闭微信,默认关闭\n
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
    program_button=main_window.child_window(**SideBar.Miniprogram_pane)
    program_button.click_input()
    if close_wechat:  
        main_window.close()
    program_window=Tools.move_window_to_center(Independent_window.MiniProgramWindow)
    if is_maximize:
        program_window.maximize()
    return program_window

def open_top_stories(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True):
    '''
    该函数用于打开看一看\n
    Args:
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t看一看界面是否全屏,默认全屏。\n
        wechat_maximize:\t微信主界面是否全屏,默认全屏\n
        close_wechat:\t任务结束后是否关闭微信,默认关闭\n
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
    top_stories_button=main_window.child_window(**SideBar.Topstories)
    top_stories_button.click_input()
    desktop=Desktop(**Independent_window.Desktop)
    top_stories_window=desktop.window(**Independent_window.TopStoriesWindow)
    if is_maximize:
        top_stories_window.maximize()
    if close_wechat:
        main_window.close()
    return top_stories_window

def open_search(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True):
    '''
    该函数用于打开搜一搜\n
    Args:
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t搜一搜界面是否全屏,默认全屏。\n
        wechat_maximize:\t微信主界面是否全屏,默认全屏\n
        close_wechat:\t任务结束后是否关闭微信,默认关闭\n
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
    search_button=main_window.child_window(**SideBar.Search)
    search_button.click_input()
    desktop=Desktop(**Independent_window.Desktop)
    search_window=desktop.window(**Independent_window.SearchWindow)
    if is_maximize:
        search_window.maximize()
    if close_wechat:
        main_window.close()
    return search_window     

def open_channels(wechat_path:str=None,is_maximize:bool=True,wechat_maximize:bool=True,close_wechat:bool=True):
    '''
    该函数用于打开视频号\n
    Args: 
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t视频号界面是否全屏,默认全屏。\n
        wechat_maximize:\t微信主界面是否全屏,默认全屏\n
        close_wechat:\t任务结束后是否关闭微信,默认关闭\n  
    '''
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=wechat_maximize)
    channel_button=main_window.child_window(**SideBar.Channel)
    channel_button.click_input()
    desktop=Desktop(**Independent_window.Desktop)
    channel_window=desktop.window(**Independent_window.ChannelWindow)
    if is_maximize:
        channel_window.maximize()
    if close_wechat:
        main_window.close()
    return channel_window

def find_wechat_path(copy_to_clipboard:bool=True):
    '''该函数用来查找微信的路径,无论微信是否运行都可以查找到\n
        copy_to_clipboard:\t是否将微信路径复制到剪贴板\n
    '''
    if is_wechat_running():
        wmi=win32com.client.GetObject('winmgmts:')
        processes=wmi.InstancesOf('Win32_Process')
        for process in processes:
            if process.Name.lower() == 'WeChat.exe'.lower():
                exe_path=process.ExecutablePath
                if exe_path:
                    # 规范化路径并检查文件是否存在
                    exe_path=os.path.abspath(exe_path)
                    wechat_path=exe_path
        if copy_to_clipboard:
            Systemsettings.copy_text_to_windowsclipboard(wechat_path)
            print("已将微信程序路径复制到剪贴板")
        return wechat_path
    else:
        #windows环境变量中查找WeChat.exe路径
        wechat_environ_path=[path for path in dict(os.environ).values() if 'WeChat.exe' in path]#
        if wechat_environ_path:
            if copy_to_clipboard:
                Systemsettings.copy_text_to_windowsclipboard(wechat_environ_path[0])
                print("已将微信程序路径复制到剪贴板")
            return wechat_environ_path[0]
        if not wechat_environ_path:
            try:
                reg_path=r"Software\Tencent\WeChat"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                    Installdir=winreg.QueryValueEx(key,"InstallPath")[0]
                wechat_path=os.path.join(Installdir,'WeChat.exe')
                if copy_to_clipboard:
                    Systemsettings.copy_text_to_windowsclipboard(wechat_path)
                    print("已将微信程序路径复制到剪贴板")
                return wechat_path
            except FileNotFoundError:
                raise NotInstalledError

def set_wechat_as_environ_path():
    '''该函数用来自动打开系统环境变量设置界面,将微信路径自动添加至其中'''
    os.environ.update({"__COMPAT_LAYER":"RUnAsInvoker"})#添加管理员权限
    subprocess.Popen(["SystemPropertiesAdvanced.exe"])
    time.sleep(2)
    systemwindow=win32gui.FindWindow(None,u'系统属性')
    if win32gui.IsWindow(systemwindow):#将系统变量窗口置于桌面最前端
        win32gui.ShowWindow(systemwindow,win32con.SW_SHOW)
        win32gui.SetWindowPos(systemwindow,win32con.HWND_TOPMOST,0,0,0,0,win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)     
    pyautogui.hotkey('alt','n',interval=0.5)#添加管理员权限后使用一系列快捷键来填写微信刻路径为环境变量
    pyautogui.hotkey('alt','n',interval=0.5)
    pyautogui.press('shift')   
    pyautogui.typewrite('wechatpath')
    try:
        Tools.find_wechat_path()
        pyautogui.hotkey('Tab',interval=0.5)
        pyautogui.hotkey('ctrl','v')
        pyautogui.press('enter')
        pyautogui.press('enter')
        pyautogui.press('esc')
    except Exception:
        pyautogui.press('esc')
        pyautogui.hotkey('alt','f4')
        pyautogui.hotkey('alt','f4')
        raise NotInstalledError
   
     
def judge_wechat_state():
    '''该函数用来判断微信运行状态'''
    time.sleep(1.5)
    if Tools.is_wechat_running():
        window=win32gui.FindWindow(Main_window.MainWindow['class_name'],Main_window.MainWindow['title'])
        if win32gui.IsIconic(window):
            return '主界面最小化'
        elif win32gui.IsWindowVisible(window):
            return '主界面可见'
        else:
            return '主界面不可见'
    else:
        return "微信未打开"
 
def move_window_to_center(Window:dict=Main_window.MainWindow,Window_handle:int=0):
    '''该函数用来将已打开的界面移动到屏幕中央并返回该窗口的windowspecification实例,使用时需注意传入参数为窗口的字典形式\n
    需要包括class_name与title两个键值对,任意一个没有值可以使用None代替\n
    Args:
        Window:\tpywinauto定位元素kwargs参数字典
        Window_handle:\t窗口句柄\n
    '''
    desktop=Desktop(**Independent_window.Desktop)
    class_name=Window['class_name']
    title=Window['title'] if 'title' in Window else None
    if Window_handle==0:
        handle=win32gui.FindWindow(class_name,title)
    else:
        handle=Window_handle
    win32gui.SetWindowPos(
        handle,
        win32con.HWND_TOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE |
        win32con.SWP_NOSIZE |
        win32con.SWP_SHOWWINDOW
        )
    screen_width,screen_height=win32api.GetSystemMetrics(win32con.SM_CXSCREEN),win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    window=desktop.window(handle=handle)
    window_width,window_height=window.rectangle().width(),window.rectangle().height()
    new_left=(screen_width-window_width)//2
    new_top=(screen_height-window_height)//2
    if screen_width!=window_width:
        win32gui.MoveWindow(handle, new_left, new_top, window_width, window_height, True)
    return window
        

def open_chat_history(friend:str,TabItem:str=None,search_pages:int=5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
    '''
    该函数用于打开好友聊天记录界面\n
    Args:
        friend:\t好友备注名称,需提供完整名称\n
        TabItem:\t点击聊天记录顶部的Tab选项,默认为None,可选值为:文件,图片与视频,链接,音乐与音频,小程序,视频号,日期\n
        search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为5,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏搜索好友信息打开聊天界面\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
        close_wechat:\t任务结束后是否关闭微信,默认关闭\n
    '''
    tabItems={'文件':TabItems.FileTabItem,'图片与视频':TabItems.PhotoAndVideoTabItem,'链接':TabItems.LinkTabItem,'音乐与音频':TabItems.MusicTabItem,'小程序':TabItems.MiniProgramTabItem,'视频号':TabItems.ChannelTabItem,'日期':TabItems.DateTabItem}
    if TabItem:
        if TabItem not in tabItems.keys():
            raise WrongParameterError('TabItem参数错误!')
    main_window=Tools.open_dialog_window(friend=friend,wechat_path=wechat_path,is_maximize=is_maximize,search_pages=search_pages)[1]
    chat_toolbar=main_window.child_window(**Main_window.ChatToolBar)
    chat_history_button=chat_toolbar.child_window(**Buttons.ChatHistoryButton)
    if not chat_history_button.exists():
        #公众号没有聊天记录这个按钮
        main_window.close()
        raise NotFriendError(f'非正常好友!无法打开聊天记录界面')
    chat_history_button.click_input()
    chat_history_window=Tools.move_window_to_center(Independent_window.ChatHistoryWindow)
    if TabItem:
        chat_history_window.child_window(**tabItems[TabItem]).click_input()
    if close_wechat:
        main_window.close()
    return chat_history_window,main_window

def search_channels(search_content:str,load_delay:float=1,wechat_path:str=None,wechat_maximize:bool=True,is_maximize:bool=True,close_wechat:bool=True):
    '''
    该方法用于打开视频号并搜索指定内容\n
    Args:
        search_content:在视频号内待搜索内容\n
        load_delay:加载查询结果的时间,单位:s\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:微信界面是否全屏,默认全屏。\n
    '''
    Systemsettings.copy_text_to_windowsclipboard(search_content)
    channel_widow=Tools.open_channels(wechat_maximize=wechat_maximize,is_maximize=is_maximize,wechat_path=wechat_path,close_wechat=close_wechat)
    search_bar=channel_widow.child_window(control_type='Edit',title='搜索',framework_id='Chrome')
    while not search_bar.exists():
        time.sleep(0.1)
        search_bar=channel_widow.child_window(control_type='Edit',title='搜索',framework_id='Chrome')
    search_bar.click_input()
    pyautogui.hotkey('ctrl','v')
    pyautogui.press('enter')
    time.sleep(load_delay)
    try:
        search_result=channel_widow.child_window(control_type='Document',title=f'{search_content}_搜索')
        return channel_widow
    except ElementNotFoundError:
        channel_widow.close()
        print('网络不良,请尝试增加load_delay时长,或更换网络')

def open_contacts_settings(wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True):
    '''
    该方法用于打开通讯录设置界面\n
    Args:
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信界面是否全屏,默认全屏。\n
        close_wechat:\t任务结束后是否关闭微信,默认关闭\n
    '''
    
    main_window=Tools.open_wechat(wechat_path=wechat_path,is_maximize=is_maximize)
    
    desktop=Desktop(**Independent_window.Desktop)
    contacts=main_window.child_window(**SideBar.Contacts)
    contacts.set_focus()
    contacts.click_input()
    cancel_button=main_window.child_window(**Buttons.CancelButton)
    if cancel_button.exists():
        cancel_button.click_input()
    ContactsLists=main_window.child_window(**Main_window.ContactsList)
    #############################
    rec=ContactsLists.rectangle()
    mouse.click(coords=(rec.right-5,rec.top))
    pyautogui.press('Home')
    pyautogui.press('pageup')
    contacts_settings=main_window.child_window(**Buttons.ContactsManageButton)#通讯录管理窗口按钮 
    contacts_settings.set_focus()
    contacts_settings.click_input()
    contacts_settings_window=desktop.window(**Independent_window.ContactManagerWindow)
    if close_wechat:
        main_window.close()
    return contacts_settings_window,main_window

def parse_message_content(ListItem:ListItemWrapper,friendtype:str)->tuple[str,str,str]:
    '''
    该函数用来将主界面右侧聊天区域内的单个ListItem消息转换为文本,传入对象为Listitem\n
    Args:
        ListItem:主界面右侧聊天区域内ListItem形式的消息\n
        friendtype:聊天区域是群聊还是好友\n 
    Returns:
        message_sender:\t发送消息的对象\n
        message_content:\t发送的消息\n
        message_type:\t消息类型,具体类型:\n{'文本','图片','视频','语音','文件','动画表情','视频号','链接','聊天记录','引用消息','卡片链接','微信转账'}\n
    '''
    language=Tools.language_detector()
    message_sender=ListItem.children()[0].children(control_type='Button')[0].window_text()
    message_content=''
    message_type=''
    #至于消息的内容那就需要仔细判断一下了
    #微信在链接的判定上比较模糊,音乐和链接最后统一都以卡片的形式在聊天记录中呈现,所以这里不区分音乐和链接,都以链接卡片的形式处理
    specialMegCN={'[图片]':'图片','[视频]':'视频','[动画表情]':'动画表情','[视频号]':'视频号','[链接]':'链接','[聊天记录]':'聊天记录'}
    specialMegEN={'[Photo]':'图片','[Video]':'视频','[Sticker]':'动画表情','[Channel]':'视频号','[Link]':'链接','[Chat History]':'聊天记录'}
    specialMegTC={'[圖片]':'图片','[影片]':'视频','[動態貼圖]':'动画表情','[影音號]':'视频号','[連結]':'链接','[聊天記錄]':'聊天记录'}
    #不同语言,处理消息内容时不同
    if language=='简体中文':
        pattern=r'\[语音\]\d+秒'
        if ListItem.window_text() in specialMegCN.keys():#内容在特殊消息中
            message_content=specialMegCN.get(ListItem.window_text())
            message_type=specialMegCN.get(ListItem.window_text())
        else:#文件,卡片链接,语音,以及正常的文本消息
            if re.match(pattern,ListItem.window_text()):#匹配是否是语音消息
                try:#是语音消息就定位语音转文字结果
                    if friendtype=='群聊':
                        audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                        message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                        message_type='语音'
                    else:
                        audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                        message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                        message_type='语音'
                except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                    message_content=ListItem.window_text()
                    message_type='文本'
            elif ListItem.window_text()=='[文件]':
                filename=ListItem.descendants(control_type='Text')[0].window_text()
                stem,extension=os.path.splitext(filename)
                #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                if not extension:
                    filename=ListItem.descendants(control_type='Text')[1].window_text()
                message_content=f'{filename}'
                message_type='文件'
            elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                cardContent=ListItem.descendants(control_type='Text')
                cardContent=[link.window_text() for link in cardContent]
                message_content='卡片链接内容:'+','.join(cardContent)
                message_type='卡片链接'
                if ListItem.window_text()=='微信转账':
                    index=cardContent.index('微信转账')
                    message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                    message_type='微信转账'
                if "引用  的消息 :" in ListItem.window_text():
                    splitlines=ListItem.window_text().splitlines()
                    message_content=f'{splitlines[0]}\t引用消息内容:{splitlines[1:]}'
                    message_type='引用消息'
                if '小程序' in cardContent:
                    message_content='小程序内容:'+','.join(cardContent)
                    message_type='小程序'

            else:#正常文本
                message_content=ListItem.window_text()
                message_type='文本'
            
    if language=='英文':
        pattern=r'\[Audio\]\d+s'
        if ListItem.window_text() in specialMegEN.keys():
            message_content=specialMegEN.get(ListItem.window_text())
            message_type=specialMegEN.get(ListItem.window_text())
        else:#文件,卡片链接,语音,以及正常的文本消息
            if re.match(pattern,ListItem.window_text()):#匹配是否是语音消息
                try:#是语音消息就定位语音转文字结果
                    if friendtype=='群聊':
                        audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                        message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                        message_type='语音'
                    else:
                        audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                        message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                        message_type='语音'
                except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                    message_content=ListItem.window_text()
                    message_type='文本'
            elif ListItem.window_text()=='[File]':
                filename=ListItem.descendants(control_type='Text')[0].window_text()
                stem,extension=os.path.splitext(filename)
                #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                if not extension:
                    filename=ListItem.descendants(control_type='Text')[1].window_text()
                message_content=f'{filename}'
                message_type='文件'

            elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                cardContent=ListItem.descendants(control_type='Text')
                cardContent=[link.window_text() for link in cardContent]
                message_content='卡片链接内容:'+','.join(cardContent)
                message_type='卡片链接'
                if ListItem.window_text()=='Weixin Transfer':
                    index=cardContent.index('Weixin Transfer')
                    message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                    message_type='微信转账'
                if "Quote 's message:" in ListItem.window_text():
                    splitlines=ListItem.window_text().splitlines()
                    message_content=f'{splitlines[0]}\t引用消息内容:{splitlines[1:]}'
                    message_type='引用消息'
                if 'Mini Programs' in cardContent:
                    message_content='小程序内容:'+','.join(cardContent)
                    message_type='小程序'
                
            else:#正常文本
                message_content=ListItem.window_text()
                message_type='文本'
    
    if language=='繁体中文':
        pattern=r'\[語音\]\d+秒'
        if ListItem.window_text() in specialMegTC.keys():
            message_content=specialMegTC.get(ListItem.window_text())
            message_type=specialMegTC.get(ListItem.window_text())
        else:#文件,卡片链接,语音,以及正常的文本消息
            if re.match(pattern,ListItem.window_text()):#匹配是否是语音消息
                try:#是语音消息就定位语音转文字结果
                    if friendtype=='群聊':
                        audio_content=ListItem.descendants(control_type='Text')[2].window_text()
                        message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                        message_type='语音'
                    else:
                        audio_content=ListItem.descendants(control_type='Text')[1].window_text()
                        message_content=ListItem.window_text()+f'  消息内容:{audio_content}'
                        message_type='语音'
                except Exception:#定位时不排除有人只发送[语音]5秒这样的文本消息，所以可能出现异常
                    message_content=ListItem.window_text()
                    message_type='文本'

            elif ListItem.window_text()=='[檔案]':
                filename=ListItem.descendants(control_type='Text')[0].window_text()
                stem,extension=os.path.splitext(filename)
                #文件这个属性的ListItem内有很多文本,正常来说文件名不是第一个就是第二个,这里哪一个有后缀名哪一个就是文件名
                if not extension:
                    filename=ListItem.descendants(control_type='Text')[1].window_text()
                message_content=f'{filename}'
                message_type='文件'

            elif len(ListItem.descendants(control_type='Text'))>=3:#ListItem内部文本ui个数大于3一般是卡片链接或引用消息或聊天记录
                cardContent=ListItem.descendants(control_type='Text')
                cardContent=[link.window_text() for link in cardContent]
                message_content='卡片链接内容:'+','.join(cardContent)
                message_type='卡片链接'
                if ListItem.window_text()=='微信轉賬':
                    index=cardContent.index('微信轉賬')
                    message_content=f'微信转账:{cardContent[index-2]}:{cardContent[index-1]}'
                    message_type='微信转账'
                if "引用  的訊息 :" in ListItem.window_text():
                    splitlines=ListItem.window_text().splitlines()
                    message_content=f'{splitlines[0]}\t引用消息内容:{splitlines[1:]}'
                    message_type='引用消息'
                if '小程式' in cardContent:
                    message_content='小程序内容:'+','.join(cardContent)
                    message_type='小程序'
            else:#正常文本
                message_content=ListItem.window_text()
                message_type='文本'

    return message_sender,message_content,message_type

def pull_messages(friend:str,number:int,parse:bool=True,search_pages:int=5,wechat_path:str=None,is_maximize:bool=True,close_wechat:bool=True)->tuple[str,str,str]|list[ListItemWrapper]:
    '''该函数用来从主界面右侧的聊天区域内获取指定条数的聊天记录消息\n
    Args:
        friend:\t好友或群聊备注\n
        number:\t聊天记录条数\n
        parse:\t是否解析聊天记录为文本(主界面右侧聊天区域内的聊天记录形式为ListItem),设置为False时返回的类型为ListItem\n
        search_pages:\t在会话列表中查询查找好友时滚动列表的次数,默认为10,一次可查询5-12人,当search_pages为0时,直接从顶部搜索栏法搜索好友信息打开聊天界面\n
        wechat_path:\t微信的WeChat.exe文件地址,主要针对未登录情况而言,一般而言不需要传入该参数,因为pywechat会通过查询环境变量,注册表等一些方法\n
            尽可能地自动找到微信路径,然后实现无论PC微信是否启动都可以实现自动化操作,除非你的微信路径手动修改过,发生了变动的话可能需要\n
            传入该参数。最后,还是建议加入到环境变量里吧,这样方便一些。加入环境变量可调用set_wechat_as_environ_path函数\n
        is_maximize:\t微信主界面是否全屏,默认全屏。\n
        close_wechat:\t任务结束后是否关闭微信,默认关闭\n
    Returns:
        (message_contents,message_senders,message_types):\t消息内容,发送消息对象,消息类型\n
        消息具体类型:\t{'文本','图片','视频','语音','文件','动画表情','视频号','链接','聊天记录','引用消息','卡片链接','微信转账'}\n
        list[ListItemWrapper]:\t聊天消息的ListItem形式
    '''
    message_contents=[]
    message_senders=[]
    message_types=[]
    friendtype='好友'#默认是好友
    main_window=Tools.open_dialog_window(friend=friend,search_pages=search_pages,wechat_path=wechat_path,is_maximize=is_maximize)[1]
    chat_history_button=main_window.child_window(**Buttons.ChatHistoryButton)
    if not chat_history_button.exists():#没有聊天记录按钮是公众号或其他类型的东西
        raise NotFriendError(f'{friend}不是好友，无法获取聊天记录！')
    chatList=main_window.child_window(**Main_window.FriendChatList)#聊天区域内的消息列表
    scrollable=Tools.is_VerticalScrollable(chatList)
    viewMoreMesssageButton=main_window.child_window(**Buttons.CheckMoreMessagesButton)#查看更多消息按钮
    if len(chatList.children(control_type='ListItem'))==0:#没有聊天记录直接返回空列表
        if parse:
            return message_contents,message_senders,message_types
        else:
            return []
    video_call_button=main_window.child_window(**Buttons.VideoCallButton)
    if not video_call_button.exists():##没有视频聊天按钮是群聊
        friendtype='群聊'
    #if message.descendants(conrol_type)是用来筛选这个消息(control_type为ListItem)内有没有按钮(消息是人发的必然会有头像按钮这个UI,系统消息比如'8:55'没有这个UI)
    ListItems=[message for message in chatList.children(control_type='ListItem') if message.children()[0].children(control_type='Button')]
    ListItems=[message for message in ListItems if message.window_text()!=Buttons.CheckMoreMessagesButton['title']]#产看更多消息内部也有按钮,所以需要筛选一下
    #点击聊天区域侧边栏和头像之间的位置来激活滑块,不直接main_window.click_input()是为了防止点到消息
    x,y=chatList.rectangle().left+8,(main_window.rectangle().top+main_window.rectangle().bottom)//2#
    if len(ListItems)>=number:#聊天区域内部不需要遍历就可以获取到的消息数量大于number条
        ListItems=ListItems[-number:]#返回从后向前数number条消息
    if len(ListItems)<number:
        ##########################################################
        if scrollable:#如果可以滚动就向上
            mouse.click(coords=(chatList.rectangle().right-10,chatList.rectangle().bottom-5))
            while len(ListItems)<number:
                chatList.iface_scroll.SetScrollPercent(verticalPercent=0.0,horizontalPercent=1.0)#调用SetScrollPercent方法向上滚动,verticalPercent=0.0表示直接将scrollbar一下子置于顶部
                mouse.scroll(coords=(x,y),wheel_dist=1000)
                ListItems=[message for message in chatList.children(control_type='ListItem') if message.children()[0].children(control_type='Button')]
                ListItems=[message for message in ListItems if message.window_text()!=Buttons.CheckMoreMessagesButton['title']]#产看更多消息内部也有按钮,所以需要筛选一下
                if not viewMoreMesssageButton.exists():#向上遍历时如果查看更多消息按钮不在存在说明已经到达最顶部,没有必要继续向上,直接退出循环
                    break
            ListItems=ListItems[-number:]  
        else:#无法滚动,说明就这么多了,有可能是刚添加好友或群聊或者是清空了聊天记录,只发了几条消息
            ListItems=ListItems[-number:]  
    #######################################################
    if close_wechat:
        main_window.close()
    if parse:
        for ListItem in ListItems:
            message_sender,message_content,message_type=Tools.parse_message_content(ListItem=ListItem,friendtype=friendtype)
            message_senders.append(message_sender)
            message_contents.append(message_content)
            message_types.append(message_type)
        return message_contents,message_senders,message_types
    else:
        return ListItems

def match_duration(duration:str):
    '''
    该函数用来将字符串类型的时间段转换为秒\n
    Args:
        duration:持续时间,格式为:'30s','1min','1h'
    '''
    if "s" in duration:
        try:
            duration=duration.replace('s','')
            duration=float(duration)
            return duration
        except Exception:
            return None
    elif 'min' in duration:
        try:
            duration=duration.replace('min','')
            duration=float(duration)*60
            return duration
        except Exception:
            return None
    elif 'h' in duration:
        try:
            duration=duration.replace('h','')
            duration=float(duration)*60*60
            return duration
        except Exception:
            return None
    else:
        return None

def is_VerticalScrollable(List:ListViewWrapper)->bool:
    '''
    该函数用来判断微信内的列表是否可以垂直滚动\n
    说明:微信内的List均为UIA框架,无句柄,停靠在右侧的scrollbar组件无Ui\n
    且列表还只渲染可见部分,因此需要使用UIA的iface_scorll来判断\n
    Args:
        List:\t微信内control_type为List的列表
    '''
    try:
        #如果能获取到这个属性,说明可以滚动
        List.iface_scroll.CurrentVerticallyScrollable
        return True
    except Exception:#否则会引发NoPatternInterfaceError,返回False
        return False
    
def pull_latest_message(chatList:ListViewWrapper)->tuple[str,str]|tuple[None,None]:#获取聊天界面内的聊天记录
    '''
    该函数用来获取聊天界面内的最新的一条聊天消息(非时间戳或系统消息:以下是新消息)\n
    返回值为最新的消息内容以及消息发送人,需要注意的是如果界面内没有消息或最新消息是系统消息\n
    那么返回None,None,该方法可以用来配合自动回复方法使用\n
    Args:
        chatList:打开好友的聊天窗口后的右侧聊天列表,该函数主要用内嵌于自动回复消息功能中使用\n
            因此传入的参数为主界面右侧的聊天列表,也就是Main_window.FriendChatList\n
        
    Returns:
        (content,sender):消息发送人\t最新的新消息内容
    Examples:
        ```
        from pywechat import Tools,Main_window,pull_latest_message
        edit_area,main_window=Tools.open_dialog_window(friend='路人甲')
        content,sender=pull_latest_message(chatList=main_window.child_window(**Main_window.FriendChatList))
        print(content,sender)
        ```
    '''
    #筛选消息，每条消息都是一个listitem
    if chatList.exists():
        if chatList.children():#如果聊天列表存在(不存在的情况:清空了聊天记录)
            ###################
            if chatList.children()[-1].descendants(control_type='Button') and chatList.children()[-1].window_text()!='':#必须是非系统消息也就是消息内部含有发送人按钮这个UI
                content=chatList.children()[-1].window_text()
                sender=chatList.children()[-1].descendants(control_type='Button')[0].window_text()
                return content,sender
    return None,None

def find_current_wxid():
    """
    该方法通过微信进程文件句柄分析当前登录的wxid,使用时必须登录微信,否则返回空字符串\n
    """
    wechat_process=None
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name']=='WeChat.exe':
            wechat_process=process
            break
    if not wechat_process:
        return ''
    wxid_pattern=re.compile(r"wxid_\w+\d+")   
    #通过内存映射文件检测,
    for mem_map in wechat_process.memory_maps():
        match=wxid_pattern.search(mem_map.path)
        if match and "WeChat Files" in mem_map.path:
            return match.group()
    return ''

def where_database_folder(open_folder:bool=False):
    '''
    该函数用来获取微信数据库存放路径,当微信未登录时只返回根目录,当微信登录时返回数据库存放路径\n
    Args:
        open_folder:\t是否打开数据库存放路径,默认不打开
    Returns:
        folder_path:\t数据库存放路径
    '''
    folder_path=''
    reg_path=r"Software\Tencent\WeChat"
    wxid=find_current_wxid()
    try:
        #查注册表
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            value=winreg.QueryValueEx(key,"FileSavePath")[0]
        if value=='MyDocument:':
            #注册表的值是MyDocument:的话路径是在c:\Users\用户名\Documents\WeChat Files\wxid_abc12356\FileStorage\Files下
            #wxid是当前登录的微信号,通过内存映射文件获取，必须是登录状态，不然最多只能获取到WCchat Files
            Userdocumens=os.path.expanduser(r'~\Documents')#c:\Users\用户名\Documents\
            root_dir=os.path.join(Userdocumens,'WeChat Files')#微信聊天记录存放根目录
            if wxid:#如果wxid不为空,那么可以继续获取到
                folder_path=os.path.join(root_dir,wxid,'Msg')
            else:
                folder_path=root_dir
        else:
            root_dir=os.path.join(value,r'\WeChat Files')
            if wxid:
                folder_path=os.path.join(root_dir,wxid,'Msg')
            else:
                folder_path=root_dir
                wxid_dirs=[os.path.join(folder_path,dir) for dir in os.listdir(folder_path) if re.match(r'wxid_\w+\d+',dir)]
                if len(wxid_dirs)==1:
                    folder_path=os.path.join(root_dir,wxid_dirs[0],'Msg')
                if len(wxid_dirs)>1:
                    print(f'该设备登录过{len(wxid_dirs)}个微信账号,未登录微信只能获取到根目录!\n请登录后重试!')
                    print(f'当前设备所有登录过的微信账号存放数据的文件夹路径为:\n{wxid_dirs}')
        if open_folder:
            os.startfile(folder_path)
        return folder_path
    except Exception:#注册表查询失败,未安装微信或者注册表被删除了
        raise NotInstalledError

def where_chatfiles_folder(open_folder:bool=False):
    '''
    该函数用来获取微信聊天文件存放路径,当微信未登录时只返回根目录,当微信登录时返回聊天文件存放路径\n\n
    Args:
        open_folder:\t是否打开聊天文件存放路径,默认不打开
    Returns:
        folder_path:\t聊天文件存放路径
    '''
    folder_path=''
    reg_path=r"Software\Tencent\WeChat"
    wxid=find_current_wxid()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            value=winreg.QueryValueEx(key,"FileSavePath")[0]
        if value=='MyDocument:':#注册表的值是MyDocument:的话
            #路径是在c:\Users\用户名\Documents\WeChat Files\wxid_abc12356\FileStorage\Files下
            #wxid是当前登录的微信号,通过内存映射文件获取，必须是登录状态，不然最多只能获取到WCchat Files
            Userdocumens=os.path.expanduser(r'~\Documents')#c:\Users\用户名\Documents\
            root_dir=os.path.join(Userdocumens,'WeChat Files')#微信聊天记录存放根目录
            if wxid:#如果wxid不为空,那么可以继续获取到
                folder_path=os.path.join(root_dir,wxid,'FileStorage','File')
            else:
                folder_path=root_dir
        else:
            root_dir=os.path.join(value,r'\WeChat Files')
            if wxid:
                folder_path=os.path.join(root_dir,wxid,'FileStorage','File')
            else:
                folder_path=root_dir
                wxid_dirs=[os.path.join(folder_path,dir) for dir in os.listdir(folder_path) if re.match(r'wxid_\w+\d+',dir)]
                if len(wxid_dirs)==1:
                    folder_path=os.path.join(root_dir,wxid_dirs[0],'FileStorage','File')
                if len(wxid_dirs)>1:
                    print(f'当前设备登录过{len(wxid_dirs)}个微信账号,未登录微信只能获取到根目录!请登录后尝试!')
                    print(f'当前设备所有登录过的微信账号存放数据的文件夹路径为:\n{wxid_dirs}')
        if open_folder:
            os.startfile(folder_path)
        return folder_path
    except Exception:
        raise NotInstalledError

def NativeSaveFile(folder_path):
    '''
    该方法用来处理微信内部点击另存为后弹出的windows本地保存文件窗口\n
    Args:
        folder_path:保存文件的文件夹路径
    '''
    desktop=Desktop(**Independent_window.Desktop)
    save_as_window=desktop.window(**Windows.NativeSaveFileWindow)
    confirm_save=save_as_window.child_window(control_type='Button',found_index=0)
    path_bar=save_as_window.child_window(class_name='ToolbarWindow32',control_type='ToolBar',auto_id='1001')
    if re.search(r':\s*(.*)',path_bar.window_text()).group(1)!=folder_path:
        rec=path_bar.rectangle()
        mouse.click(coords=(rec.right-5,int(rec.top+rec.bottom)//2))
        pyautogui.press('backspace')
        pyautogui.hotkey('ctrl','v',_pause=False)
        pyautogui.press('enter')
        time.sleep(0.5)
    pyautogui.hotkey('alt','s')
    time.sleep(1)
    if confirm_save.exists():
        confirm_save.click_input()

def NativeChooseFolder(folder_path):
    '''
    该方法用来处理微信内部点击选择文件夹后弹出的windows本地选择文件夹窗口\n
    Args:
        folder_path:保存文件的文件夹路径
    '''
    #如果path_bar上的内容与folder_path不一致,那么删除复制粘贴
    #如果一致,点击选择文件夹窗口
    Systemsettings.copy_text_to_windowsclipboard(folder_path)
    desktop=Desktop(**Independent_window.Desktop)
    save_as_window=desktop.window(**Windows.NativeChooseFolderWindow)
    path_bar=save_as_window.child_window(class_name='ToolbarWindow32',control_type='ToolBar',auto_id='1001')
    if re.search(r':\s*(.*)',path_bar.window_text()).group(1)!=folder_path:
        rec=path_bar.rectangle()
        mouse.click(coords=(rec.right-5,int(rec.top+rec.bottom)//2))
        pyautogui.press('backspace')
        pyautogui.hotkey('ctrl','v',_pause=False)
        pyautogui.press('enter')
        time.sleep(0.5)
    choose_folder_button=save_as_window.child_window(control_type='Button',title='选择文件夹')
    choose_folder_button.click_input()
