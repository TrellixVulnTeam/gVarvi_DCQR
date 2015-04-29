# coding=utf-8
__author__ = 'nico'

import os

import wx
import wx.lib.agw.ultimatelistctrl as ULC

from config import GRID_STYLE, MAIN_ICON
from activities.PhotoPresentation import PhotoPresentation, PhotoPresentationTag, Sound
from view.wxUtils import InfoDialog
from InsModTemplate import InsModTemplate


class InsModImageActivity(InsModTemplate):
    def __init__(self, parent, control, activity_id=-1):
        super(InsModImageActivity, self).__init__(size=(800, 600), parent=parent, control=control,
                                                  insmod_tag_window_type=InsModImageTag, activity_id=activity_id,
                                                  title="New Image Activity")
        self.Show()

    def refresh_tags(self):
        self.tags_grid.DeleteAllItems()
        for tag in self.tag_ctrl.tags:
            if tag.sounds:
                self.tags_grid.Append(
                    [tag.name, tag.path, tag.sound_associated,
                     ";".join([sound.path for sound in tag.sounds])])
            else:
                self.tags_grid.Append(
                    [tag.name, tag.path, tag.sound_associated, ""])

    def build_general_data_sizer(self):
        self.general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        self.name_label = wx.StaticText(self, label='Name')
        self.name_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))

        self.gap_label = wx.StaticText(self, label='Gap (seconds)')
        self.gap_control = wx.SpinCtrl(self, value='5', min=1, max=30)

        self.random_label = wx.StaticText(self, label='Random')
        self.randomCheckBox = wx.CheckBox(self)

        if self.modifying:
            self.name_text_ctrl.SetValue(self.activity.name)
            self.gap_control.SetValue(self.activity.gap)
            if self.activity.random == "Yes":
                self.randomCheckBox.SetValue(True)
            else:
                self.randomCheckBox.SetValue(False)

        self.general_data_sizer.AddMany([self.name_label, (self.name_text_ctrl, 1, wx.EXPAND),
                                         self.gap_label, (self.gap_control, 1, wx.EXPAND),
                                         self.random_label, self.randomCheckBox])

        self.general_data_sizer.AddGrowableCol(1, 1)

    def build_tags_grid(self):
        self.tags_grid = ULC.UltimateListCtrl(self,
                                              agwStyle=GRID_STYLE)

        self.tags_grid.SetUserLineHeight(30)

        self.tags_grid.InsertColumn(0, 'Name', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(0, 115)
        self.tags_grid.InsertColumn(1, 'Path', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(1, 200)
        self.tags_grid.InsertColumn(2, 'Sound associated', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(2, 140)
        self.tags_grid.InsertColumn(3, 'Sounds', ULC.ULC_FORMAT_CENTER)
        self.tags_grid.SetColumnWidth(3, -3)

    def OnSave(self, e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        gap = str(self.gap_control.GetValue())
        if self.randomCheckBox.IsChecked():
            random = "Yes"
        else:
            random = "No"
        tags = self.tag_ctrl.tags
        if name == "" or len(tags) == 0:
            correct_data = False
        if correct_data:
            if self.modifying:
                self.controller.update_activity(PhotoPresentation, self.activity_id, name, random, gap, tags)
            else:
                self.controller.add_activity(PhotoPresentation, -1, name, random, gap, tags)
            self.main_window.refresh_activities()
            self.Destroy()
        else:
            InfoDialog("Please, fill all fields\nAlso remember to add at least one tag").show()


class InsModImageTag(wx.Frame):
    def __init__(self, parent, tag_control, tag_id=-1):
        self.parent = parent
        self.tag_control = tag_control
        self.modifying = tag_id != -1
        self.tag_id = tag_id
        if not self.modifying:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE, title="New Image Tag",
                              size=(600, 600))
        else:
            wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE,
                              title="Modifying Image Tag (id: {0})".format(tag_id),
                              size=(600, 600))
            tag = self.tag_control.tags[self.tag_id]

        self.SetBackgroundColour("#DBE6CC")

        icon = wx.Icon(MAIN_ICON, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.CenterOnScreen()

        sizer = wx.BoxSizer(wx.VERTICAL)

        general_data_sizer = wx.FlexGridSizer(cols=2, hgap=30, vgap=10)

        name_label = wx.StaticText(self, label='Name')
        self.name_text_ctrl = wx.TextCtrl(self, -1, size=((400, -1)))
        if self.modifying:
            self.name_text_ctrl.SetValue(tag.name)

        path_label = wx.StaticText(self, label='Path')
        path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.path_text_ctrl = wx.TextCtrl(self, -1, size=((350, -1)))
        if self.modifying:
            self.path_text_ctrl.SetValue(tag.path)
        self.path_button = wx.Button(self, -1, label="...")
        self.Bind(wx.EVT_BUTTON, self.OnChangePath, id=self.path_button.GetId())
        self.path_button.SetMinSize((40, 25))
        path_sizer.Add(self.path_text_ctrl, 1, wx.EXPAND)
        path_sizer.AddSpacer(20)
        path_sizer.Add(self.path_button, 0, wx.RIGHT)

        sound_associated_label = wx.StaticText(self, label='Sound associated')
        self.sound_associated_checkbox = wx.CheckBox(self)
        if self.modifying and tag.sound_associated == "Yes":
            self.sound_associated_checkbox.SetValue(True)

        general_data_sizer.AddMany([name_label, (self.name_text_ctrl, 0, wx.EXPAND),
                                    path_label, (path_sizer, 0, wx.EXPAND),
                                    sound_associated_label, self.sound_associated_checkbox])

        general_data_sizer.AddGrowableCol(1, 1)

        sounds_sizer = wx.StaticBoxSizer(wx.StaticBox(self, label="Sounds"), wx.VERTICAL)

        self.sounds_listbox = wx.ListBox(self, -1)
        if self.modifying and len(tag.sounds) != 0:
            for sound in tag.sounds:
                self.sounds_listbox.Append(sound.path)

        sounds_sizer.Add(self.sounds_listbox, 1, wx.EXPAND | wx.ALL, border=20)

        tag_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Buttons for adding and removing tags

        add_tag_bt = wx.Button(self, -1, label="Add")
        tag_buttons_sizer.Add(add_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self.OnAddSound, id=add_tag_bt.GetId())
        add_tag_bt.SetToolTip(wx.ToolTip("Add new tag"))

        remove_tag_bt = wx.Button(self, -1, label="Remove")
        tag_buttons_sizer.Add(remove_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveSound, id=remove_tag_bt.GetId())
        remove_tag_bt.SetToolTip(wx.ToolTip("Remove the selected tag"))

        up_tag_bt = wx.Button(self, -1, label="Up")
        tag_buttons_sizer.Add(up_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self.OnSoundUp, id=up_tag_bt.GetId())
        up_tag_bt.SetToolTip(wx.ToolTip("Up selected tag in the list"))

        down_tag_bt = wx.Button(self, -1, label="Down")
        tag_buttons_sizer.Add(down_tag_bt, flag=wx.ALL, border=0)
        self.Bind(wx.EVT_BUTTON, self.OnSoundDown, id=down_tag_bt.GetId())
        down_tag_bt.SetToolTip(wx.ToolTip("Down selected tag in the list"))

        sounds_sizer.Add(tag_buttons_sizer, 0, wx.ALIGN_CENTER | wx.ALL, border=10)

        buttons_sizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.HORIZONTAL)

        button_save = wx.Button(self, -1, label="Save")
        buttons_sizer.Add(button_save, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnSave, id=button_save.GetId())
        button_save.SetToolTip(wx.ToolTip("Save the activity"))

        button_cancel = wx.Button(self, -1, label="Cancel")
        buttons_sizer.Add(button_cancel, flag=wx.ALL, border=10)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=button_cancel.GetId())
        button_cancel.SetToolTip(wx.ToolTip("Return to the main window"))

        sizer.Add(general_data_sizer, 0, wx.EXPAND | wx.ALL, border=20)
        sizer.Add(sounds_sizer, 1, wx.EXPAND | wx.ALL, border=20)
        sizer.Add(buttons_sizer, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=20)
        self.SetSizer(sizer)

        self.Show()

    def OnChangePath(self, e):

        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE
                                 | wx.DD_DIR_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_OK:
            self.path_text_ctrl.SetValue(dlg.GetPath())
        dlg.Destroy()

    def OnAddSound(self, e):
        wildcard = "Audio source (*.mp3; *wav)|*.mp3;*.wav"

        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                self.sounds_listbox.Append(path)
        dlg.Destroy()

    def OnRemoveSound(self, e):
        sel = self.sounds_listbox.GetSelection()
        if sel != -1:
            self.sounds_listbox.Delete(sel)

    def OnSoundUp(self, e):
        sel_pos = self.sounds_listbox.GetSelection()
        if sel_pos > 0:
            sel_path = self.sounds_listbox.GetStringSelection()
            self.sounds_listbox.Delete(sel_pos)
            self.sounds_listbox.Insert(sel_path, sel_pos - 1)

    def OnSoundDown(self, e):
        sel_pos = self.sounds_listbox.GetSelection()
        if sel_pos < self.sounds_listbox.GetCount() - 1 and sel_pos != -1:
            sel_path = self.sounds_listbox.GetStringSelection()
            self.sounds_listbox.Delete(sel_pos)
            self.sounds_listbox.Insert(sel_path, sel_pos + 1)

    def OnSave(self, e):
        correct_data = True
        name = self.name_text_ctrl.GetValue()
        path = self.path_text_ctrl.GetValue()
        if self.sound_associated_checkbox.IsChecked():
            sound_associated = "Yes"
        else:
            sound_associated = "No"
        sounds = [Sound(sound_path) for sound_path in self.sounds_listbox.GetItems()]
        tag = PhotoPresentationTag(name, path, sound_associated, sounds)

        if name == "" or path == "" or not os.path.isdir(path):
            correct_data = False

        if sound_associated == "Yes" and len(sounds) == 0:
            correct_data = False

        if correct_data:
            if self.modifying:
                self.parent.ModifyTag(self.tag_id, tag)
                self.Destroy()
            else:
                self.parent.AddTag(tag)
                self.Destroy()
        else:
            InfoDialog("Please, fill all fields with valid data").show()


    def OnCancel(self, e):
        self.Destroy()
