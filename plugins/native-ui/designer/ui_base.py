# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.1.0-0-g733bf3d)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.html2

###########################################################################
## Class RoomFrameBase
###########################################################################

class RoomFrameBase ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"blivechat - 房间 123456", pos = wx.DefaultPosition, size = wx.Size( 800,650 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )

        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer2 = wx.BoxSizer( wx.VERTICAL )

        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

        self.config_button = wx.Button( self, wx.ID_ANY, u"设置", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.config_button, 0, 0, 5 )

        self.stay_on_top_button = wx.ToggleButton( self, wx.ID_ANY, u"置顶", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.stay_on_top_button, 0, wx.LEFT, 5 )


        bSizer3.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.collapse_console_button = wx.Button( self, wx.ID_ANY, u">>", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.collapse_console_button, 0, wx.LEFT, 5 )


        bSizer2.Add( bSizer3, 0, wx.ALL|wx.EXPAND, 5 )

        self.chat_web_view = wx.html2.WebView.New(self)
        bSizer2.Add( self.chat_web_view, 1, wx.EXPAND, 5 )


        bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )

        self.console_notebook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.console_notebook.SetMinSize( wx.Size( 200,-1 ) )

        self.paid_panel = wx.Panel( self.console_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        self.paid_web_view = wx.html2.WebView.New(self.paid_panel)
        bSizer4.Add( self.paid_web_view, 1, wx.EXPAND, 5 )


        self.paid_panel.SetSizer( bSizer4 )
        self.paid_panel.Layout()
        bSizer4.Fit( self.paid_panel )
        self.console_notebook.AddPage( self.paid_panel, u"付费消息", True )
        self.super_chat_panel = wx.Panel( self.console_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer5 = wx.BoxSizer( wx.VERTICAL )

        self.super_chat_list = wx.ListCtrl( self.super_chat_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL )
        bSizer5.Add( self.super_chat_list, 1, wx.EXPAND, 5 )


        self.super_chat_panel.SetSizer( bSizer5 )
        self.super_chat_panel.Layout()
        bSizer5.Fit( self.super_chat_panel )
        self.console_notebook.AddPage( self.super_chat_panel, u"醒目留言", False )
        self.gift_panel = wx.Panel( self.console_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        self.gift_list = wx.ListCtrl( self.gift_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL )
        bSizer6.Add( self.gift_list, 1, wx.EXPAND, 5 )


        self.gift_panel.SetSizer( bSizer6 )
        self.gift_panel.Layout()
        bSizer6.Fit( self.gift_panel )
        self.console_notebook.AddPage( self.gift_panel, u"礼物&&舰长", False )
        self.statistics_panel = wx.Panel( self.console_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer7 = wx.BoxSizer( wx.VERTICAL )

        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self.statistics_panel, wx.ID_ANY, u"付费用户" ), wx.VERTICAL )

        self.paid_user_list = wx.ListCtrl( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT|wx.LC_SINGLE_SEL )
        sbSizer1.Add( self.paid_user_list, 1, wx.EXPAND, 5 )


        bSizer7.Add( sbSizer1, 1, wx.EXPAND, 5 )

        self.statistics_text = wx.StaticText( self.statistics_panel, wx.ID_ANY, u"总弹幕数：0  互动用户数：0  总付费：0 元", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.statistics_text.Wrap( -1 )

        bSizer7.Add( self.statistics_text, 0, wx.ALL, 5 )

        bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

        self.export_excel_button = wx.Button( self.statistics_panel, wx.ID_ANY, u"导出Excel", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer11.Add( self.export_excel_button, 0, 0, 5 )


        bSizer7.Add( bSizer11, 0, wx.ALL|wx.EXPAND, 5 )


        self.statistics_panel.SetSizer( bSizer7 )
        self.statistics_panel.Layout()
        bSizer7.Fit( self.statistics_panel )
        self.console_notebook.AddPage( self.statistics_panel, u"统计", False )

        bSizer1.Add( self.console_notebook, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.Bind( wx.EVT_CLOSE, self._on_close )
        self.config_button.Bind( wx.EVT_BUTTON, self._on_config_button_click )
        self.stay_on_top_button.Bind( wx.EVT_TOGGLEBUTTON, self._on_stay_on_top_button_toggle )
        self.collapse_console_button.Bind( wx.EVT_BUTTON, self._on_collapse_console_button_click )
        self.export_excel_button.Bind( wx.EVT_BUTTON, self._on_export_excel_button_click )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def _on_close( self, event ):
        event.Skip()

    def _on_config_button_click( self, event ):
        event.Skip()

    def _on_stay_on_top_button_toggle( self, event ):
        event.Skip()

    def _on_collapse_console_button_click( self, event ):
        event.Skip()

    def _on_export_excel_button_click( self, event ):
        event.Skip()


###########################################################################
## Class RoomConfigDialogBase
###########################################################################

class RoomConfigDialogBase ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"房间设置", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE|wx.DIALOG_NO_PARENT )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"界面" ), wx.VERTICAL )

        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.opacity_label = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"窗口不透明度", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.opacity_label.Wrap( -1 )

        fgSizer1.Add( self.opacity_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.opacity_slider = wx.Slider( sbSizer1.GetStaticBox(), wx.ID_ANY, 100, 10, 100, wx.DefaultPosition, wx.Size( 200,-1 ), wx.SL_HORIZONTAL )
        fgSizer1.Add( self.opacity_slider, 1, wx.ALL|wx.EXPAND, 5 )

        self.auto_translate_label = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"自动翻译弹幕到日语", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.auto_translate_label.Wrap( -1 )

        fgSizer1.Add( self.auto_translate_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.auto_translate_check = wx.CheckBox( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer1.Add( self.auto_translate_check, 1, wx.ALL|wx.EXPAND, 5 )

        self.gift_pron_label = wx.StaticText( sbSizer1.GetStaticBox(), wx.ID_ANY, u"标注打赏用户名读音", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.gift_pron_label.Wrap( -1 )

        fgSizer1.Add( self.gift_pron_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        gift_pron_choiceChoices = [ u"不显示", u"拼音", u"日文假名" ]
        self.gift_pron_choice = wx.Choice( sbSizer1.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, gift_pron_choiceChoices, 0 )
        self.gift_pron_choice.SetSelection( 0 )
        bSizer2.Add( self.gift_pron_choice, 1, wx.ALL|wx.EXPAND, 5 )


        fgSizer1.Add( bSizer2, 1, wx.ALL|wx.EXPAND, 5 )


        sbSizer1.Add( fgSizer1, 1, wx.EXPAND, 5 )


        bSizer1.Add( sbSizer1, 0, wx.ALL|wx.EXPAND, 5 )

        sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"消息屏蔽" ), wx.VERTICAL )

        fgSizer2 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer2.SetFlexibleDirection( wx.BOTH )
        fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.min_gift_price_label = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"最低显示打赏价格（元）", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.min_gift_price_label.Wrap( -1 )

        fgSizer2.Add( self.min_gift_price_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.min_gift_price_edit = wx.TextCtrl( sbSizer2.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
        self.min_gift_price_edit.SetMinSize( wx.Size( 180,-1 ) )

        fgSizer2.Add( self.min_gift_price_edit, 1, wx.ALL|wx.EXPAND, 5 )

        self.block_gift_danmaku_label = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"屏蔽礼物弹幕", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.block_gift_danmaku_label.Wrap( -1 )

        fgSizer2.Add( self.block_gift_danmaku_label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

        self.block_gift_danmaku_check = wx.CheckBox( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.block_gift_danmaku_check.SetValue(True)
        fgSizer2.Add( self.block_gift_danmaku_check, 1, wx.ALL|wx.EXPAND, 5 )


        sbSizer2.Add( fgSizer2, 1, wx.EXPAND, 5 )


        bSizer1.Add( sbSizer2, 0, wx.ALL|wx.EXPAND, 5 )

        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )


        bSizer3.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.ok_button = wx.Button( self, wx.ID_OK, u"确定", wx.DefaultPosition, wx.DefaultSize, 0 )

        self.ok_button.SetDefault()
        bSizer3.Add( self.ok_button, 0, wx.ALL, 5 )

        self.cancel_button = wx.Button( self, wx.ID_CANCEL, u"取消", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.cancel_button, 0, wx.ALL, 5 )


        bSizer1.Add( bSizer3, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )

        self.Centre( wx.BOTH )

        # Connect Events
        self.opacity_slider.Bind( wx.EVT_SLIDER, self._on_opacity_slider_change )
        self.ok_button.Bind( wx.EVT_BUTTON, self._on_ok )
        self.cancel_button.Bind( wx.EVT_BUTTON, self._on_cancel )

    def __del__( self ):
        pass


    # Virtual event handlers, override them in your derived class
    def _on_opacity_slider_change( self, event ):
        event.Skip()

    def _on_ok( self, event ):
        event.Skip()

    def _on_cancel( self, event ):
        event.Skip()


