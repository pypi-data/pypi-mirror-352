#!/usr/bin/env ython
import sys  # pragma: no cover
import matplotlib  # pragma: no cover
import inspect   # pragma: no cover
import importlib   # pragma: no cover

matplotlib.use("Agg")  # pragma: no cover
matplotlib.rcParams['agg.path.chunksize'] = 64000  # pragma: no cover
## matplotlib.rc('xtick', labelsize=8)
## matplotlib.rc('ytick', labelsize=8)
import platform  # pragma: no cover
import os  # pragma: no cover
import re



try:
    from PySide6.QtUiTools import QUiLoader  # pragma: no cover
    from PySide6.QtCore import QFile  # pragma: no cover
    from PySide6.QtCore import QCoreApplication  # pragma: no cover
    from PySide6.QtWidgets import *  # pragma: no cover
    from PySide6 import QtWidgets  # pragma: no cover
    from PySide6.QtGui import *  # pragma: no cover
    from PySide6 import QtGui  # pragma: no cover
    from PySide6 import QtCore  # pragma: no cover
    from PySide6.QtWidgets import QFileDialog  # pragma: no cover
    from PySide6 import QtWidgets  # pragma: no cover
    from PySide6.QtCore import SIGNAL  # pragma: no cover
    from PySide6.QtCore import QUrl, Qt  # pragma: no cover
    import PySide6  # pragma: no cover
    import qtmodern.styles  # pragma: no cover
    from PySide6.QtGui import QPixmap
    from PySide6.QtGui import QPalette
except:
    pass

try:
    from PySide6.QtWebEngineWidgets import QWebEngineView  # pragma: no cover
    from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineUrlSchemeHandler  # pragma: no cover
except:
    pass
#    if platform.system() == 'Darwin' and platform.machine() == 'arm64':  # pragma: no cover
#        find_pyside2 = importlib.util.find_spec('PySide2')  # pragma: no cover
#        if find_pyside2.__str__() == None:  # pragma: no cover
#            print('PySide2 not installed!')  # pragma: no cover
#            sys.exit()  # pragma: no cover
#        else:  # pragma: no cover
#            script_name = os.path.join(os.path.dirname(__file__), 'bash', 'fix_pyside2')  # pragma: no cover
#            print('Error: Could not load QWebEngineView')  # pragma: no cover
#            answer = input("Do you want to fix the issue automatically (y, n) or display the fixing bash script (d)? [y, n, d]: ")  # pragma: no cover
#            while answer not in ['y', 'Y', 'n', 'N', 'd', 'D']:  # pragma: no cover
#                print('Please input y, n or d only')  # pragma: no cover
#                answer = input("Do you want to fix the issue automatically (y, n) or display the fixing bash script (d)? [y, n, d]: ")  # pragma: no cover
#
#            if answer in ['n', 'N']:  # pragma: no cover
#                print('Good luck!')  # pragma: no cover
#                sys.exit()  # pragma: no cover
#
#            if answer in ['d', 'D']:  # pragma: no cover
#                print('\n=== Bash script to fix the issue ========================================================\n')  # pragma: no cover
#                os.system('cat ' + script_name)  # pragma: no cover
#                print('\n=== End of bash script ==================================================================\n')  # pragma: no cover
#                while answer not in ['y', 'Y', 'n', 'N']:  # pragma: no cover
#                    answer = input("Do you want to fix the issue automatically? [y, n]: ")  # pragma: no cover
#                    if answer not in ['y', 'Y', 'n', 'N']:  # pragma: no cover
#                        print('Please input y or n only')  # pragma: no cover
#
#            if answer in ['n', 'N']:  # pragma: no cover
#                print('Good luck!')  # pragma: no cover
#                sys.exit()  # pragma: no cover
#
#            print('Fixing issue (PySide2/Darwin arm64 anaconda3)...')  # pragma: no cover
#            os.system(script_name)  # pragma: no cover
#            print('Fixed M1/M2 mac arm64 anaconda PySide2 issue, please start qtmetabolabpy again!')  # pragma: no cover
#            sys.exit()  # pragma: no cover

import darkdetect
import webbrowser
import pandas as pd
from PyPDF2 import PdfWriter, PdfMerger, PdfReader
from PyPDF2 import PageObject, Transformation
#import matplotlib.pyplot as pl  # pragma: no cover

if "linux" in sys.platform:  # pragma: no cover
    gui_env = ['TkAgg', 'GTKAgg', 'Qt5Agg', 'WXAgg']  # pragma: no cover
elif sys.platform == "darwin":  # pragma: no cover
    try:  # pragma: no cover
        gui_env = ['Qt5Agg']  # pragma: no cover
    except ImportError:  # pragma: no cover
        gui_env = ['TkAgg', 'GTKAgg', 'Qt5Agg', 'WXAgg']  # pragma: no cover

    # matplotlib.use("Qt5Agg")
else:  # pragma: no cover
    gui_env = ['TkAgg', 'GTKAgg', 'Qt5Agg', 'WXAgg']  # pragma: no cover

if sys.platform != "win32":  # pragma: no cover
    for gui in gui_env:  # pragma: no cover
        try:  # pragma: no cover
            matplotlib.use(gui, warn=False, force=True)  # pragma: no cover
            break  # pragma: no cover
        except:  # pragma: no cover
            continue  # pragma: no cover

try:
    from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
                                                    NavigationToolbar2QT as NavigationToolbar)  # pragma: no cover
except:
    pass

from matplotlib.figure import Figure  # pragma: no cover
import argparse  # pragma: no cover
from time import sleep  # pragma: no cover

try:  # pragma: no cover
    import pyautogui  # pragma: no cover
except:  # pragma: no cover
    pass  # pragma: no cover

import numpy as np  # pragma: no cover
import io  # pragma: no cover
from metabolabpy.nmr import nmrDataSet  # pragma: no cover
from metabolabpy.GUI import phCorr  # pragma: no cover
from metabolabpy.nmr import nmrHsqc  # pragma: no cover
import time  # pragma: no cover
##import platform  # pragma: no cover
import math  # pragma: no cover
from metabolabpy.nmr import nmrConfig  # pragma: no cover
import traceback  # pragma: no cover
import shutil  # pragma: no cover
import scipy.io  # pragma: no cover
#import inspect
from io import StringIO
import contextlib
import zipfile
from collections import defaultdict
#from notebook import notebookapp
import multiprocess
import subprocess
#import jupyterthemes
import itertools
import xlsxwriter
from string import ascii_uppercase
import metabolabpy.nmr.nmrHsqc as nmrHsqc

try:
    # ------------------ MplWidget ------------------
    class MplWidget(QWidget):  # pragma: no cover

        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            fig = Figure()
            self.canvas = FigureCanvas(fig)
            vertical_layout = QVBoxLayout()
            vertical_layout.addWidget(self.canvas)
            home = NavigationToolbar.home

            def new_home(self, *args, **kwargs):
                self.canvas.axes.autoscale()
                self.canvas.draw()
                self.canvas.toolbar.update()
                home(self, *args, **kwargs)

            NavigationToolbar.home = new_home
            self.toolbar = NavigationToolbar(self.canvas, self)
            # self.toolbar._actions['back'].setEnabled(False)
            vertical_layout.addWidget(self.toolbar)

            self.canvas.axes = self.canvas.figure.add_subplot(111)
            self.setLayout(vertical_layout)
            self.ph_corr = phCorr.PhCorr()
            # end __init__


    # ------------------ MplWidget ------------------
    # ------------------ MplWidget2 ------------------
    class MplWidget2(QWidget):  # pragma: no cover

        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            fig = Figure()
            self.canvas = FigureCanvas(fig)
            vertical_layout = QVBoxLayout()
            vertical_layout.addWidget(self.canvas)
            home = NavigationToolbar.home

            def new_home(self, *args, **kwargs):
                self.canvas.axes.autoscale()
                self.canvas.draw()
                self.canvas.toolbar.update()
                home(self, *args, **kwargs)

            NavigationToolbar.home = new_home
            self.toolbar = NavigationToolbar(self.canvas, self)
            # self.toolbar._actions['back'].setEnabled(False)
            vertical_layout.addWidget(self.toolbar)

            self.canvas.axes = self.canvas.figure.add_subplot(111)
            self.setLayout(vertical_layout)
            self.ph_corr = phCorr.PhCorr()
            # end __init__


    # ------------------ MplWidget2 ------------------
    # ------------------ MplWidget3 ------------------
    class MplWidget3(QWidget):  # pragma: no cover

        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            fig = Figure()
            self.canvas = FigureCanvas(fig)
            vertical_layout = QVBoxLayout()
            vertical_layout.addWidget(self.canvas)
            home = NavigationToolbar.home

            def new_home(self, *args, **kwargs):
                self.canvas.axes.autoscale()
                self.canvas.draw()
                self.canvas.toolbar.update()
                home(self, *args, **kwargs)

            NavigationToolbar.home = new_home
            self.toolbar = NavigationToolbar(self.canvas, self)
            # self.toolbar._actions['back'].setEnabled(False)
            vertical_layout.addWidget(self.toolbar)

            self.canvas.axes = self.canvas.figure.add_subplot(111)
            self.setLayout(vertical_layout)
            self.ph_corr = phCorr.PhCorr()
            # end __init__


    # ------------------ MplWidget3 ------------------
    # ------------------ MplWidget4 ------------------
    class MplWidget4(QWidget):  # pragma: no cover

        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            fig = Figure()
            self.canvas = FigureCanvas(fig)
            vertical_layout = QVBoxLayout()
            vertical_layout.addWidget(self.canvas)
            home = NavigationToolbar.home

            def new_home(self, *args, **kwargs):
                self.canvas.axes.autoscale()
                self.canvas.draw()
                self.canvas.toolbar.update()
                home(self, *args, **kwargs)

            NavigationToolbar.home = new_home
            self.toolbar = NavigationToolbar(self.canvas, self)
            # self.toolbar._actions['back'].setEnabled(False)
            vertical_layout.addWidget(self.toolbar)

            self.canvas.axes = self.canvas.figure.add_subplot(111)
            self.setLayout(vertical_layout)
            self.ph_corr = phCorr.PhCorr()
            # end __init__


    # ------------------ MplWidget4 ------------------
    # ------------------ MplWidget5 ------------------
    class MplWidget5(QWidget):  # pragma: no cover

        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            fig = Figure()
            self.canvas = FigureCanvas(fig)
            vertical_layout = QVBoxLayout()
            vertical_layout.addWidget(self.canvas)
            home = NavigationToolbar.home

            def new_home(self, *args, **kwargs):
                self.canvas.axes.autoscale()
                self.canvas.draw()
                self.canvas.toolbar.update()
                home(self, *args, **kwargs)

            NavigationToolbar.home = new_home
            self.toolbar = NavigationToolbar(self.canvas, self)
            # self.toolbar._actions['back'].setEnabled(False)
            vertical_layout.addWidget(self.toolbar)

            self.canvas.axes = self.canvas.figure.add_subplot(111)
            self.setLayout(vertical_layout)
            self.ph_corr = phCorr.PhCorr()
            # end __init__


    # ------------------ MplWidget5 ------------------

    # ------------------ QWebEngineView2 -------------
    class QWebEngineView2(QWebEngineView):
        def print_cmd(self):
            print("QWebEngineView2")

    # ------------------ QWebEngineView2 -------------
except:
    pass


class QtMetaboLabPy(object):  # pragma: no cover
    def __init__(self):
        self.exited_peak_picking = False
        self.zoom_was_on = True
        self.pan_was_on = False
        self.std_pos_col1 = (0.0, 0.0, 1.0)
        self.std_neg_col1 = (1.0, 0.0, 0.0)
        self.std_pos_col2 = (0.8, 0.8, 1.0)
        self.std_neg_col2 = (1.0, 0.8, 0.8)
        self.set_cols = ''
        self.n_clicks = 1
        self.cur_clicks = 0
        self.xy = [[]]
        self.xdata = []
        self.ydata = []
        self.temp_shift = 0.0
        self.find_maximum = True
        self.nd = nmrDataSet.NmrDataSet()
        self.__version__ = self.nd.__version__
        self.ph_corr = phCorr.PhCorr()
        # load ui; create w
        f_name = os.path.join(os.path.dirname(__file__), "ui", "metabolabpy_mainwindow.ui")
        self.file = QFile(f_name)
        self.file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.loader.registerCustomWidget(QWebEngineView2)
        self.loader.registerCustomWidget(MplWidget)
        self.loader.registerCustomWidget(MplWidget2)
        self.loader.registerCustomWidget(MplWidget3)
        self.loader.registerCustomWidget(MplWidget4)
        self.loader.registerCustomWidget(MplWidget5)
        # self.loader.registerCustomWidget(hsqcMultiplet)
        self.w = self.loader.load(self.file)
        self.zoom = False
        self.hide_pre_processing()
        self.hide_peak_picking()
        self.w.preprocessing.setVisible(False)
        self.w.splinebaseline.setVisible(False)
        self.w.peakPicking.setVisible(False)
        self.w.preProcPeak.setVisible(False)
        self.w.hsqcAnalysis.setVisible(False)
        self.w.multipletAnalysis.setVisible(False)
        #self.w.isotopomerAnalysis.setVisible(False)
        self.w.nmrSpectrum.setTabEnabled(1, False)
        self.w.nmrSpectrum.setTabEnabled(2, False)
        self.w.nmrSpectrum.setTabEnabled(3, False)
        #self.w.nmrSpectrum.setTabEnabled(4, False)
        self.w.nmrSpectrum.setStyleSheet(
            "QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
        # connections
        # self.w.rDolphinExport.clicked.connect(self.setrDolphinExport)
        self.w.displayAssignedMetabolites.setVisible(False)
        self.w.displayAssignedMetabolites.stateChanged.connect(self.display_assigned_metabolites)
        self.w.displayLibraryShifts.setVisible(False)
        self.w.displayLibraryShifts.stateChanged.connect(self.display_library_shifts)
        self.w.displaySelectedMetabolite.setVisible(False)
        self.w.displaySelectedMetabolite.stateChanged.connect(self.display_selected_metabolite)
        self.w.exportPath.textChanged.connect(self.set_export_path)
        self.w.multipletAnalysisIntensity.textChanged.connect(self.set_ma_intensity)
        self.w.multipletAnalysisR2.textChanged.connect(self.set_ma_r2)
        self.w.multipletAnalysisEchoTime.textChanged.connect(self.set_ma_echo_time)
        self.w.invertMatrix_1.stateChanged.connect(self.set_invert)
        self.w.invertMatrix_2.stateChanged.connect(self.set_invert)
        self.w.exportFileName.textChanged.connect(self.set_export_file_name)
        self.w.exportDelimiterTab.toggled.connect(self.set_export_delimiter_tab)
        self.w.exportCharacter.textChanged.connect(self.set_export_character)
        self.w.titleFile.textChanged.connect(self.change_title_file)
        self.w.samplesInComboBox.currentIndexChanged.connect(self.set_samples_in_combo_box)
        self.w.openWeb.activated.connect(self.open_metabolite_web)
        self.w.plotLegend.stateChanged.connect(self.set_legend)
        #self.w.startNotebookButton.clicked.connect(self.start_notebook)
        #self.w.stopNotebookButton.clicked.connect(self.stop_notebook)
        self.w.runPreProcessingButton.clicked.connect(self.data_pre_processing)
        self.w.resetPreProcessingButton.clicked.connect(self.reset_data_pre_processing)
        self.w.avoidNegValues.stateChanged.connect(self.set_avoid_neg_values)
        self.w.excludeRegion.stateChanged.connect(self.set_exclude_region)
        self.w.segmentalAlignment.stateChanged.connect(self.set_segmental_alignment)
        self.w.compressBuckets.stateChanged.connect(self.set_compress_buckets)
        self.w.noiseFiltering.stateChanged.connect(self.set_noise_filtering)
        self.w.bucketSpectra.stateChanged.connect(self.set_bucket_spectra)
        self.w.scaleSpectraRefSpc.valueChanged.connect(self.change_scale_spectra_ref_spc)
        self.w.segAlignRefSpc.valueChanged.connect(self.change_seg_align_ref_spc)
        self.w.scaleSpectra.stateChanged.connect(self.set_scale_spectra)
        self.w.pqnButton.clicked.connect(self.set_pqn_tsa_scaling)
        self.w.tsaButton.clicked.connect(self.set_pqn_tsa_scaling)
        self.w.addSplineBaselineButton.clicked.connect(self.ginput_spline_baseline)
        self.w.clearSplineBaselineButton.clicked.connect(self.clear_spline_points)
        self.w.resetSplineBaselineButton.clicked.connect(self.reset_spline_points)
        self.w.correctAllButton.clicked.connect(self.corr_spline_baseline)
        self.w.plotBaselineButton.clicked.connect(self.plot_spline_baseline)
        self.w.averagePoints.textChanged.connect(self.get_spline_average_points)
        self.w.linearSplinePoints.textChanged.connect(self.get_linear_spline_points)
        self.w.fitUpToBonds.currentIndexChanged.connect(self.set_up_to_bonds)
        self.w.autoScaling.clicked.connect(self.set_variance_stabilisation_options)
        self.w.paretoScaling.clicked.connect(self.set_variance_stabilisation_options)
        self.w.gLogTransform.clicked.connect(self.set_variance_stabilisation_options)
        self.w.varianceStabilisation.stateChanged.connect(self.set_variance_stabilisation)
        self.w.exportDataSet.stateChanged.connect(self.set_export_data_set)
        self.w.excludeRegionTW.cellChanged.connect(self.set_exclude_pre_proc)
        self.w.splineBaselineTW.cellChanged.connect(self.set_spline_baseline_tw)
        self.w.segAlignTW.cellChanged.connect(self.set_seg_align_pre_proc)
        self.w.selectClassTW.itemSelectionChanged.connect(self.set_plot_pre_proc)
        self.w.selectClassTW.cellChanged.connect(self.set_change_pre_proc)
        self.w.hsqcSpinSys.cellChanged.connect(self.hsqc_spin_sys_change)
        self.nd.hsqc_spin_sys_connected = True
        self.w.exportHsqcData.clicked.connect(self.save_hsqc_data)
        self.w.excludeClearButton.clicked.connect(self.select_clear_exclude_pre_proc)
        self.w.segAlignClearButton.clicked.connect(self.select_clear_seg_align_pre_proc)
        self.w.compressClearButton.clicked.connect(self.select_clear_compress_pre_proc)
        self.w.excludeAddButton.clicked.connect(self.select_add_exclude_pre_proc)
        self.w.segAlignAddButton.clicked.connect(self.select_add_seg_align_pre_proc)
        self.w.compressAddButton.clicked.connect(self.select_add_compress_pre_proc)
        self.w.selectAllButton.clicked.connect(self.select_all_pre_proc)
        self.w.selectEvenButton.clicked.connect(self.select_even_pre_proc)
        self.w.selectOddButton.clicked.connect(self.select_odd_pre_proc)
        self.w.selectClassButton.clicked.connect(self.select_class_pre_proc)
        self.w.selectClassLE.textChanged.connect(self.select_class_pre_proc)
        self.w.cmdLine.returnPressed.connect(self.exec_cmd)
        self.w.tmspConc.returnPressed.connect(self.set_tmsp_conc)
        self.w.internalStandard.returnPressed.connect(self.set_internal_std)
        self.w.noiseThresholdLE.returnPressed.connect(self.set_noise_reg_pre_proc)
        self.w.noiseRegionStartLE.returnPressed.connect(self.set_noise_reg_pre_proc)
        self.w.noiseRegionEndLE.returnPressed.connect(self.set_noise_reg_pre_proc)
        self.w.thLineWidthLE.returnPressed.connect(self.set_noise_reg_pre_proc)
        self.w.bucketPpmLE.returnPressed.connect(self.set_bucket_ppm_pre_proc)
        self.w.bucketDataPointsLE.returnPressed.connect(self.set_bucket_points_pre_proc)
        self.w.actionAutomatic_Referencing.triggered.connect(self.automatic_referencing)
        self.w.actionRestart_MetaboLabPy.triggered.connect(self.restart_metabolabpy)
        self.w.actionVertical_AutoScale.triggered.connect(self.vertical_auto_scale)
        self.w.actionHorizontal_AutoScale.triggered.connect(self.horizontal_auto_scale)
        self.w.actionZoom.triggered.connect(self.set_zoom)
        self.w.actionPan.triggered.connect(self.set_pan)
        self.w.actionShow_Next_Tab.triggered.connect(self.next_tab)
        self.w.actionShow_Previous_Tab.triggered.connect(self.previous_tab)
        self.w.actionPlot_spc.triggered.connect(self.plot_spc)
        self.w.actionSave.triggered.connect(self.save_button)
        self.w.actionLoad.triggered.connect(self.load_button)
        self.w.actionCheck_mlpy_file.triggered.connect(self.check_file)
        self.w.actionImport_MetaboLab_mat.triggered.connect(self.load_mat)
        self.w.actionIncrease_YLim_2fold.triggered.connect(self.increase_y_lim)
        self.w.actionDecrease_YLim_2fold.triggered.connect(self.decrease_y_lim)
        self.w.actionIncrease_XLim_2fold.triggered.connect(self.increase_x_lim)
        self.w.actionDecrease_XLim_2fold.triggered.connect(self.decrease_x_lim)
        self.w.actionOpen_NMRPipe.triggered.connect(self.read_nmrpipe_spc)
        self.w.actionActivate_Command_Line.triggered.connect(self.activate_command_line)
        self.w.actionPrevious_command.triggered.connect(self.previous_command)
        self.w.actionNext_command.triggered.connect(self.next_command)
        self.w.actionPrint.triggered.connect(self.print_spc)
        self.w.actionCorrect_Phase.triggered.connect(self.start_stop_ph_corr)
        self.w.actionUpdate_MetaboLabPy_quits_software.triggered.connect(self.update_metabolabpy)
        # self.w.actionZoomCorrect_Phase.triggered.connect(self.zoom_ph_corr)
        self.w.maResetButton.clicked.connect(self.hsqc_spin_sys_reset)
        self.w.zoomPhCorr1d.clicked.connect(self.zoom_ph_corr)
        self.w.exitZoomPhCorr1d.clicked.connect(self.zoom_ph_corr)
        self.w.exitPhCorr1d.clicked.connect(self.start_stop_ph_corr)
        self.w.actionClear.triggered.connect(self.clear)
        self.w.lambdaLE.returnPressed.connect(self.set_var_lambda)
        self.w.y0LE.returnPressed.connect(self.set_var_y0)
        self.w.actionRead_NMR_Spectrum.triggered.connect(self.read_nmr_spc)
        self.w.preprocessing.stateChanged.connect(self.set_pre_processing)
        self.w.peakPicking.stateChanged.connect(self.set_peak_picking)
        self.w.splinebaseline.stateChanged.connect(self.set_spline_baseline)
        self.w.peakAddButton.clicked.connect(self.add_peak)
        self.w.peakClearButton.clicked.connect(self.clear_peak)
        self.w.peakWidget.cellChanged.connect(self.set_add_peak)
        self.w.peakExportButton.clicked.connect(self.export_peak)
        self.w.quantify.stateChanged.connect(self.set_datasets_exps)
        self.w.intAllExps.stateChanged.connect(self.set_datasets_exps)
        self.w.localBaselineCorrection.stateChanged.connect(self.set_datasets_exps)
        self.w.exportFormatCB.currentIndexChanged.connect(self.set_datasets_exps)
        self.w.hsqcAnalysis.stateChanged.connect(self.set_hsqc_analysis)
        self.w.multipletAnalysis.stateChanged.connect(self.set_multiplet_analysis)
        self.w.resetAutobaseline.clicked.connect(self.reset_autobaseline)
        #self.w.isotopomerAnalysis.stateChanged.connect(self.set_isotopomer_analysis)
        self.w.preserveOverallScale.stateChanged.connect(self.set_preserve_overall_scale)
        self.w.actionReset.triggered.connect(self.reset_plot)
        self.w.actionShow_NMR_Spectrum.triggered.connect(self.show_nmr_spectrum)
        self.w.actionSetup_Processing_Parameters.triggered.connect(self.setup_processing_parameters)
        self.w.actionShow_Display_Parameters.triggered.connect(self.show_display_parameters)
        self.w.actionShow_Acquisition_Parameters.triggered.connect(self.show_acquisition_parameters)
        self.w.actionShow_Title_File_Information.triggered.connect(self.show_title_file_information)
        self.w.actionShow_pulseProgram.triggered.connect(self.show_pulse_program)
        self.w.actionFourier_Transform.triggered.connect(self.ft)
        self.w.actionScript_Editor.triggered.connect(self.script_editor)
        self.w.actionChange_to_next_Exp.triggered.connect(self.change_to_next_exp)
        self.w.actionChange_to_previous_Exp.triggered.connect(self.change_to_previous_exp)
        self.w.actionChange_to_next_DS.triggered.connect(self.change_to_next_ds)
        self.w.actionChange_to_previous_DS.triggered.connect(self.change_to_previous_ds)
        self.w.exampleScripts.view().pressed.connect(self.load_example_script)
        self.w.actionAutomatic_Phase_Correction.triggered.connect(self.autophase1d)
        self.w.actionAutomatic_Phase_Correction_with_Reference_Spectrum.triggered.connect(self.autophase1d_bl)
        self.w.actionAutomatic_Phase_Correction_algorithm_2.triggered.connect(self.autophase1d1)
        self.w.actionAutomatic_Baseline_Correction.triggered.connect(self.autobaseline)
        self.w.actionScale_2D_Spectrum_Up.triggered.connect(self.scale_2d_spectrum_up)
        self.w.actionScale_2D_Spectrum_Down.triggered.connect(self.scale_2d_spectrum_down)
        self.w.actionScale_all_2D_Spectra_Up.triggered.connect(self.scale_all_2d_spectra_up)
        self.w.actionScale_all_2D_Spectra_Down.triggered.connect(self.scale_all_2d_spectra_down)
        self.w.actionSelect_All.triggered.connect(self.select_plot_all)
        self.w.actionClear_All.triggered.connect(self.select_plot_clear)
        self.w.actionConsole.triggered.connect(self.show_console)
        self.w.actionConsole.triggered.connect(self.show_console)
        self.w.actionShow_Plot_Editor.triggered.connect(self.show_plot_editor)
        self.w.actionShow_SplashScreen.triggered.connect(self.splash)
        self.w.actionHelp.triggered.connect(self.show_help)
        self.w.actionToggle_FullScreen.triggered.connect(self.show_main_window)
        self.w.setBox.valueChanged.connect(self.change_data_set_exp)
        self.w.setBox.setKeyboardTracking(False)
        self.w.expBox.valueChanged.connect(self.change_data_set_exp)
        self.w.expBox.setKeyboardTracking(False)
        self.w.maFitChemShifts.stateChanged.connect(self.set_fit_ma_chem_shifts)
        self.w.maFitContributions.stateChanged.connect(self.set_fit_ma_percentages)
        self.w.doNotFitZeroPercentages.stateChanged.connect(self.set_fit_zero_percentages)
        self.w.maAutoSim.stateChanged.connect(self.set_ma_autosim)
        self.w.posCol.currentIndexChanged.connect(self.get_disp_pars1)
        self.w.negCol.currentIndexChanged.connect(self.get_disp_pars2)
        self.w.posColR.textChanged.connect(self.get_disp_pars3)
        self.w.posColG.textChanged.connect(self.get_disp_pars3)
        self.w.posColB.textChanged.connect(self.get_disp_pars3)
        self.w.negColR.textChanged.connect(self.get_disp_pars3)
        self.w.negColG.textChanged.connect(self.get_disp_pars3)
        self.w.negColB.textChanged.connect(self.get_disp_pars3)
        self.w.nLevels.textChanged.connect(self.get_disp_pars4)
        self.w.minLevel.textChanged.connect(self.get_disp_pars5)
        self.w.maxLevel.textChanged.connect(self.get_disp_pars6)
        self.w.axisType1.currentIndexChanged.connect(self.get_disp_pars7)
        self.w.axisType2.currentIndexChanged.connect(self.get_disp_pars8)
        self.w.displaySpc.currentIndexChanged.connect(self.get_disp_pars9)
        self.w.baselineCorrection.currentIndexChanged.connect(self.check_baseline_correction)
        self.w.baselineOrder.currentIndexChanged.connect(self.check_baseline_order)
        self.w.spcOffset.textChanged.connect(self.get_disp_pars10)
        self.w.spcScale.textChanged.connect(self.get_disp_pars11)
        self.w.fontSize.valueChanged.connect(self.set_font_size)
        self.w.xLabel.textChanged.connect(self.get_disp_pars12)
        self.w.yLabel.textChanged.connect(self.get_disp_pars13)
        self.w.spcLabel.textChanged.connect(self.get_disp_pars14)
        self.w.preProcessingSelect.currentIndexChanged.connect(self.set_pre_processing_options)
        self.w.exportMethod.currentIndexChanged.connect(self.set_export_method_options)
        self.w.tilt.currentIndexChanged.connect(self.set_tilt)
        self.w.symJ.currentIndexChanged.connect(self.set_sym_j)
        self.w.windowFunction.currentIndexChanged.connect(self.get_proc_pars1)
        self.w.windowFunction_2.currentIndexChanged.connect(self.get_proc_pars2)
        self.w.phaseCorrection.currentIndexChanged.connect(self.get_proc_pars3)
        self.w.phaseCorrection_2.currentIndexChanged.connect(self.get_proc_pars4)
        self.w.waterSuppression.currentIndexChanged.connect(self.get_proc_pars5)
        self.w.winType.currentIndexChanged.connect(self.get_proc_pars6)
        self.w.gibbs.currentIndexChanged.connect(self.get_proc_pars7)
        self.w.gibbs_2.currentIndexChanged.connect(self.get_proc_pars8)
        self.w.wwStartLevel.textChanged.connect(self.get_proc_pars28)
        self.w.wwZeroFilling.textChanged.connect(self.get_proc_pars29)
        self.w.wwWaveletType.currentIndexChanged.connect(self.get_proc_pars30)
        self.w.wwNumber.currentIndexChanged.connect(self.get_proc_pars31)
        self.w.autobaselineBox.stateChanged.connect(self.set_autobaseline2)
        self.w.abslAlg.currentIndexChanged.connect(self.get_proc_pars32)
        self.w.abslHw.textChanged.connect(self.get_proc_pars33)
        self.w.abslShw.textChanged.connect(self.get_proc_pars34)
        self.w.abslAe.textChanged.connect(self.get_proc_pars35)
        self.w.abslLam.textChanged.connect(self.get_proc_pars36)
        self.w.abslMi.textChanged.connect(self.get_proc_pars37)
        self.w.abslAlpha.textChanged.connect(self.get_proc_pars38)
        self.w.abslBeta.textChanged.connect(self.get_proc_pars39)
        self.w.abslGamma.textChanged.connect(self.get_proc_pars40)
        self.w.abslBetaMult.textChanged.connect(self.get_proc_pars41)
        self.w.abslGammaMult.textChanged.connect(self.get_proc_pars42)
        self.w.abslQuantile.textChanged.connect(self.get_proc_pars43)
        self.w.abslPolyOrder.textChanged.connect(self.get_proc_pars44)
        self.w.zeroFilling.textChanged.connect(self.get_proc_pars9)
        self.w.zeroFilling_2.textChanged.connect(self.get_proc_pars10)
        self.w.lb.textChanged.connect(self.get_proc_pars11)
        self.w.gb.textChanged.connect(self.get_proc_pars12)
        self.w.ssb.textChanged.connect(self.get_proc_pars13)
        self.w.lb_2.textChanged.connect(self.get_proc_pars14)
        self.w.gb_2.textChanged.connect(self.get_proc_pars15)
        self.w.ssb_2.textChanged.connect(self.get_proc_pars16)
        self.w.ph0.textChanged.connect(self.get_proc_pars17)
        self.w.ph1.textChanged.connect(self.get_proc_pars18)
        self.w.ph0_2.textChanged.connect(self.get_proc_pars19)
        self.w.ph1_2.textChanged.connect(self.get_proc_pars20)
        self.w.autobaselineBox.clicked.connect(self.get_proc_pars27)
        self.w.polyOrder.textChanged.connect(self.get_proc_pars21)
        self.w.extrapolationSize.textChanged.connect(self.get_proc_pars22)
        self.w.windowSize.textChanged.connect(self.get_proc_pars23)
        self.w.fidOffsetCorrection.textChanged.connect(self.get_proc_pars24)
        self.w.stripTransformStart.textChanged.connect(self.get_proc_pars25)
        self.w.stripTransformEnd.textChanged.connect(self.get_proc_pars26)
        self.w.phRefDS.valueChanged.connect(self.change_data_set_exp_ph_ref)
        self.w.phRefExp.valueChanged.connect(self.change_data_set_exp_ph_ref)
        self.w.phRefColour.currentIndexChanged.connect(self.get_disp_pars15)
        self.w.fourierTransformButton.clicked.connect(self.ft)
        self.w.fourierTransformButton_2.clicked.connect(self.ft)
        self.w.executeScript.clicked.connect(self.exec_script)
        self.w.openScript.clicked.connect(self.open_script)
        self.w.saveScript.clicked.connect(self.save_script)
        self.w.actionOpen_Script.triggered.connect(self.open_script)
        self.w.actionSave_Script.triggered.connect(self.save_script)
        self.w.actionExecute_Script.triggered.connect(self.exec_script)
        self.w.hsqcMetabolites.clicked.connect(self.set_hsqc_metabolite)
        self.w.hsqcAssignedMetabolites.clicked.connect(self.set_hsqc_assigned_metabolite)
        self.w.mlSaveButton.clicked.connect(self.save_ml_info)
        self.w.mlResetButton.clicked.connect(self.reset_ml_info)
        self.w.deleteAssignedHsqc.clicked.connect(self.remove_assigned_metabolite)
        self.w.maFitButton.clicked.connect(self.ma_fit_hsqc_1d)
        # self.w.helpComboBox.currentIndexChanged.connect(self.set_help)
        self.w.helpComboBox.activated.connect(self.set_help)
        self.w.tutorialComboBox.activated.connect(self.set_tutorial)
        # Quit Button
        self.w.quitButton.clicked.connect(self.quit_app)
        self.w.saveButton.clicked.connect(self.save_button)
        self.w.loadButton.clicked.connect(self.load_button)
        self.w.exportPathSelectButton.clicked.connect(self.set_export_table)
        self.w.actionQuit.triggered.connect(self.quit_app)
        self.w.dispPlotButton.clicked.connect(self.plot_spc_disp)
        self.show_version()
        self.keep_zoom = False
        self.keep_x_zoom = False
        self.ph_corr_active = False
        self.set_font_size()
        self.cf = nmrConfig.NmrConfig()
        self.cf.read_config()
        self.w.plotLegend.setChecked(self.cf.plot_legend)
        self.w.plotTop.clicked.connect(self.update_plot_top)
        self.w.plotLeft.clicked.connect(self.update_plot_left)
        self.w.plotRight.clicked.connect(self.update_plot_right)
        self.w.plotBottom.clicked.connect(self.update_plot_bottom)
        self.w.plotBackground.clicked.connect(self.update_plot_background)
        self.w.useStandardPlotColours.clicked.connect(self.update_use_standard_plot_colours)
        self.w.useDatasetPlotColours.clicked.connect(self.update_use_dataset_plot_colours)
        self.w.plotLightMode.clicked.connect(self.update_plot_light_mode)
        self.w.plotDarkMode.clicked.connect(self.update_plot_dark_mode)
        self.w.printSpectrumLabel.clicked.connect(self.update_print_spectrum_label)
        self.w.printStackedPlot.clicked.connect(self.update_print_stacked_plot)
        self.w.printAutoScale.clicked.connect(self.update_print_auto_scale)
        self.w.printRepeatAxes.clicked.connect(self.update_print_repeat_axes)
        self.w.spectrumLineWidth.valueChanged.connect(self.update_spectrum_line_width)
        self.w.axesLineWidth.valueChanged.connect(self.update_axes_line_width)
        self.w.axesFontSize.valueChanged.connect(self.update_axes_font_size)
        self.w.labelFontSize.valueChanged.connect(self.update_label_font_size)
        self.w.aspectRatioNMR.returnPressed.connect(self.update_aspect_ratio_nmr)
        self.w.aspectRatioHSQCPeak.returnPressed.connect(self.update_aspect_ratio_hsqc_peak)
        self.w.aspectRatioNMRMultiplet.returnPressed.connect(self.update_aspect_ratio_nmr_multiplet)
        #self.w.autoPlot.setChecked(self.cf.auto_plot)
        self.w.keepZoom.setChecked(self.cf.keep_zoom)
        self.w.fontSize.setValue(self.cf.font_size)
        self.std_pos_col1 = (self.cf.pos_col10, self.cf.pos_col11, self.cf.pos_col12)
        self.std_neg_col1 = (self.cf.neg_col10, self.cf.neg_col11, self.cf.neg_col12)
        self.std_pos_col2 = (self.cf.pos_col20, self.cf.pos_col21, self.cf.pos_col22)
        self.std_neg_col2 = (self.cf.neg_col20, self.cf.neg_col21, self.cf.neg_col22)
        self.w.actionSave_as_Default.triggered.connect(self.save_config)
        self.w.actionLoad_Default.triggered.connect(self.load_config)
        self.w.actionReset_Config.triggered.connect(self.reset_config)
        self.w.rSpc_p0.textChanged.connect(self.get_r_spc_p0)
        self.w.rSpc_p1.textChanged.connect(self.get_r_spc_p1)
        self.w.rSpc_p2.textChanged.connect(self.get_r_spc_p2)
        self.w.rSpc_p3.textChanged.connect(self.get_r_spc_p3)
        self.w.rSpc_p4.textChanged.connect(self.get_r_spc_p4)
        self.w.rSpc_p5.textChanged.connect(self.get_r_spc_p5)
        self.w.rSpc_p6.textChanged.connect(self.get_r_spc_p6)
        self.w.iSpc_p0.textChanged.connect(self.get_i_spc_p0)
        self.w.iSpc_p1.textChanged.connect(self.get_i_spc_p1)
        self.w.iSpc_p2.textChanged.connect(self.get_i_spc_p2)
        self.w.iSpc_p3.textChanged.connect(self.get_i_spc_p3)
        self.w.iSpc_p4.textChanged.connect(self.get_i_spc_p4)
        self.w.iSpc_p5.textChanged.connect(self.get_i_spc_p5)
        self.w.iSpc_p6.textChanged.connect(self.get_i_spc_p6)
        self.set_font_size()
        self.w.MplWidget.toolbar.setVisible(False)
        self.w.hsqcMultiplet.toolbar.setVisible(False)
        self.w.hsqcPeak.toolbar.setVisible(False)
        #self.w.startNotebookButton.setVisible(False)
        #self.w.stopNotebookButton.setVisible(False)
        # self.w.isotopomerHsqcPeak.toolbar.setVisible(False)
        # self.w.isotopomerMultiplet.toolbar.setVisible(False)
        self.w.MplWidget.setFocus()
        self.set_zoom()
        self.w.pickRowColPhCorr2d.clicked.connect(self.pick_col_row)
        self.w.emptyRowColPhCorr2d.clicked.connect(self.empty_col_row)
        self.w.removeRowColPhCorr2d.clicked.connect(self.remove_last_col_row)
        self.w.horzPhCorr2d.clicked.connect(self.horz_ph_corr_2d)
        self.w.vertPhCorr2d.clicked.connect(self.vert_ph_corr_2d)
        self.w.exitPhCorr2d.clicked.connect(self.start_stop_ph_corr)
        self.w.applyPhCorr2d.clicked.connect(self.apply_2d_ph_corr)
        self.w.cancelPhCorr2d.clicked.connect(self.cancel_2d_ph_corr)
        self.w.zoomPhCorr2d.clicked.connect(self.zoom_ph_corr)
        self.w.exitZoomPhCorr2d.clicked.connect(self.zoom_ph_corr)
        self.w.exitPhCorr1d.setVisible(False)
        self.w.zoomPhCorr1d.setVisible(False)
        self.w.exitZoomPhCorr1d.setVisible(False)
        self.w.pickRowColPhCorr2d.setVisible(False)
        self.w.emptyRowColPhCorr2d.setVisible(False)
        self.w.removeRowColPhCorr2d.setVisible(False)
        self.w.horzPhCorr2d.setVisible(False)
        self.w.vertPhCorr2d.setVisible(False)
        self.w.zoomPhCorr2d.setVisible(False)
        self.w.applyPhCorr2d.setVisible(False)
        self.w.cancelPhCorr2d.setVisible(False)
        self.w.exitPhCorr2d.setVisible(False)
        self.w.exitZoomPhCorr2d.setVisible(False)
        self.w.actionSet_light_mode_requires_restart.triggered.connect(self.set_light_mode)
        self.w.actionSet_dark_mode_requires_restart.triggered.connect(self.set_dark_mode)
        self.w.actionSet_system_mode_requires_restart.triggered.connect(self.set_system_mode)
        self.w.MplWidget.canvas.draw()
        self.w.setStyleSheet("font-size: " + str(self.cf.font_size) + "pt")
        self.w.actionreInitialise_pre_processing_plot_colours.triggered.connect(self.nd.pp.init_plot_colours)
        self.w.actionreInitialise_plot_colours.triggered.connect(self.set_standard_plot_colours)
        self.w.clearAssignedHsqc.clicked.connect(self.clear_assigned_hsqc)
        self.w.displayMetaboliteInformation.clicked.connect(self.display_metabolite_information)
        self.w.hsqcAddPeak.clicked.connect(lambda: self.ginput_hsqc(0))
        self.w.hsqcRemovePeak.clicked.connect(lambda: self.ginput_hsqc2(0))
        self.w.metaboliteResetButton.clicked.connect(self.metabolite_reset)
        self.w.metaboliteAutoButton.clicked.connect(self.autopick_hsqc)
        self.w.metaboliteAutofitButton.clicked.connect(self.autofit_hsqc)
        self.w.maSimButton.clicked.connect(self.ma_sim_hsqc_1d)
        self.buttons = {}
        self.set_water_suppression(0)
        self.set_autobaseline2()
        # print(sys.platform)
        if sys.platform == 'darwin':
            self.w.actionCreate.setText('Create Launchpad Icon')
            self.w.actionCreate.triggered.connect(self.create_icon_mac)
        elif sys.platform == 'win' or sys.platform == 'win32' or sys.platform == 'win64':
            self.w.actionCreate.setText('Create Desktop Icon')
            self.w.actionCreate.triggered.connect(self.create_icon_win)
        else:
            # print(sys.platform)
            self.w.actionCreate.setText('Create Desktop Starter')
            self.w.actionCreate.triggered.connect(self.create_icon_linux)
            # print('doing stuffs3....')
            self.w.actionCreate.setVisible(True)

        self.emp_ref_shift = 0.0
        self.process = []
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            self.load_dark_mode()
        else:
            self.load_light_mode()
        #
        self.w.helpView.page().profile().downloadRequested.connect(self._download_requested)
        self.w.peakWidget.setColumnWidth(2, 182)
        self.layout = QGridLayout(self.w.peakSelection)
        self.set_autobaseline_pars()
        # self.w.h1Range.textChanged.connect(self.get_hsqc_pars1())
        # self.w.c13Range.textChanged.connect(self.get_hsqc_pars2())
        # self.w.threshold.textChanged.connect(self.get_hsqc_pars3())
        # self.w.jCC.textChanged.connect(self.get_hsqc_pars4())
        # self.w.jCH.textChanged.connect(self.get_hsqc_pars5())
        # self.w.nMax.textChanged.connect(self.get_hsqc_pars6())
        # self.w..textChanged.connect(self.get_hsqc_pars())
        # self.set_hsqc()
        # end __init__

    def reset_autobaseline(self):
        s = self.nd.s
        e = self.nd.e
        self.nd.nmrdat[s][e].proc.autobaseline_alg = self.nd.default_baseline_alg
        idx = self.nd.baseline_algs.index(self.nd.default_baseline_alg)
        self.w.abslAlg.setCurrentIndex(idx)
        self.w.abslHw.setText(str(self.nd.default_half_window))
        self.w.abslShw.setText(str(self.nd.default_smooth_half_window))
        self.w.abslAe.setText(str(self.nd.default_add_ext))
        self.w.abslLam.setText(str(self.nd.default_lam))
        self.w.abslMi.setText(str(self.nd.default_max_iter))
        self.w.abslAlpha.setText(str(self.nd.default_alpha))
        self.w.abslBeta.setText(str(self.nd.default_beta))
        self.w.abslGamma.setText(str(self.nd.default_gamma))
        self.w.abslBetaMult.setText(str(self.nd.default_beta_mult))
        self.w.abslGammaMult.setText(str(self.nd.default_gamma_mult))
        self.w.abslQuantile.setText(str(self.nd.default_quantile))
        self.w.abslPolyOrder.setText(str(self.nd.default_poly_order))
        self.nd.nmrdat[s][e].proc.autobaseline_half_window = self.nd.default_half_window
        self.nd.nmrdat[s][e].proc.autobaseline_smooth_half_window = self.nd.default_smooth_half_window
        self.nd.nmrdat[s][e].proc.autobaseline_add_ext = self.nd.default_add_ext
        self.nd.nmrdat[s][e].proc.autobaseline_lam = self.nd.default_lam
        self.nd.nmrdat[s][e].proc.autobaseline_max_iter = self.nd.default_max_iter
        self.nd.nmrdat[s][e].proc.autobaseline_alpha = self.nd.default_alpha
        self.nd.nmrdat[s][e].proc.autobaseline_beta = self.nd.default_beta
        self.nd.nmrdat[s][e].proc.autobaseline_gamma = self.nd.default_gamma
        self.nd.nmrdat[s][e].proc.autobaseline_beta_mult = self.nd.default_beta_mult
        self.nd.nmrdat[s][e].proc.autobaseline_gamma_mult = self.nd.default_gamma_mult
        self.nd.nmrdat[s][e].proc.autobaseline_quantile = self.nd.default_quantile
        self.nd.nmrdat[s][e].proc.autobaseline_poly_order = self.nd.default_poly_order
        # end reset_autobaseline

    def set_autobaseline_pars(self):
        if self.nd.e > -1:
            alg = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_alg

        self.w.abslAlg.clear()
        self.w.abslAlg.addItems(self.nd.baseline_algs)
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_alg = alg

        if self.nd.e == -1:
            idx = self.nd.baseline_algs.index(self.nd.default_baseline_alg)
            self.w.abslAlg.setCurrentIndex(idx)
            self.w.abslHw.setText(str(self.nd.default_half_window))
            self.w.abslShw.setText(str(self.nd.default_smooth_half_window))
            self.w.abslAe.setText(str(self.nd.default_add_ext))
            self.w.abslLam.setText(str(self.nd.default_lam))
            self.w.abslMi.setText(str(self.nd.default_max_iter))
            self.w.abslAlpha.setText(str(self.nd.default_alpha))
            self.w.abslBeta.setText(str(self.nd.default_beta))
            self.w.abslGamma.setText(str(self.nd.default_gamma))
            self.w.abslBetaMult.setText(str(self.nd.default_beta_mult))
            self.w.abslGammaMult.setText(str(self.nd.default_gamma_mult))
            self.w.abslQuantile.setText(str(self.nd.default_quantile))
            self.w.abslPolyOrder.setText(str(self.nd.default_poly_order))
        else:
            s = self.nd.s
            e = self.nd.e
            alg = self.nd.nmrdat[s][e].proc.autobaseline_alg
            idx = self.nd.baseline_algs.index(alg)
            self.w.abslAlg.setCurrentIndex(idx)
            self.w.abslHw.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_half_window))
            self.w.abslShw.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_smooth_half_window))
            self.w.abslAe.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_add_ext))
            self.w.abslLam.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_lam))
            self.w.abslMi.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_max_iter))
            self.w.abslAlpha.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_alpha))
            self.w.abslBeta.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_beta))
            self.w.abslGamma.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_gamma))
            self.w.abslBetaMult.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_beta_mult))
            self.w.abslGammaMult.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_gamma_mult))
            self.w.abslQuantile.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_quantile))
            self.w.abslPolyOrder.setText(str(self.nd.nmrdat[s][e].proc.autobaseline_poly_order))

        # end set_autobaseline_pars

    def set_water_suppression(self, status=-1):
        status1 = False
        status2 = False
        status3 = False
        if status == 3:
            status3 = True
        elif status == 2:
            status2 = True
        elif status == 1:
            status1 = True

        self.w.label_74.setVisible(status3)
        self.w.wwStartLevel.setVisible(status3)
        self.w.label_100.setVisible(status3)
        self.w.wwZeroFilling.setVisible(status3)
        self.w.label_101.setVisible(status3)
        self.w.wwWaveletType.setVisible(status3)
        self.w.label_102.setVisible(status3)
        self.w.wwNumber.setVisible(status3)
        self.w.label_9.setVisible(status2)
        self.w.polyOrder.setVisible(status2)
        self.w.label_10.setVisible(status1)
        self.w.winType.setVisible(status1)
        self.w.label_11.setVisible(status1)
        self.w.extrapolationSize.setVisible(status1)
        self.w.label_12.setVisible(status1)
        self.w.windowSize.setVisible(status1)

    def activate_command_line(self):
        if (self.w.cmdLine.hasFocus() == True):
            self.w.cmdLine.clearFocus()
        else:
            self.w.cmdLine.setFocus()

        # end activate_command_line

    def add_peak(self):
        self.ginput_add_peak(2)
        # end add_peak

    def add_tmsp(self, m0=1, r2=1, all=False):
        if all:
            self.nd.add_tmsp(m0=m0, r2=r2)
        else:
            self.nd.nmrdat[self.nd.s][self.nd.e].add_tmsp(m0=m0, r2=r2)

        self.plot_spc()
        # end add_tmsp

    def autofit_hsqc(self, metabolite_list=False):
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        print(f'fitting multiplets...')
        if metabolite_list is False:
            metabolite_list = [self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite]
        elif len(metabolite_list[0]) == 0:
            metabolite_list = [self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite]

        if len(metabolite_list[0]) == 0:
            return

        if self.w.hsqcAnalysis.isChecked() == False:
            self.w.hsqcAnalysis.setChecked(True)
            self.w.hsqcAnalysis.setChecked(False)

        no_peak_selected = False
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak == -1:
            no_peak_selected = True
            cur_peak = 1
        else:
            cur_peak = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak

        text = self.nd.nmrdat[self.nd.s][self.nd.e].autofit_hsqc(metabolite_list)
        print(text)
        if no_peak_selected:
            self.w.hsqcAnalysis.setChecked(False)
            self.w.hsqcAnalysis.setChecked(True)
            idx1 = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.metabolite_list.index(metabolite_list[0])
            self.w.hsqcMetabolites.setCurrentIndex(self.w.hsqcMetabolites.model().index(idx1, 0))

        self.set_hsqc_metabolite()
        self.plot_metabolite_peak(cur_peak)
        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        code_out.close()
        code_err.close()
        self.w.console.verticalScrollBar().setValue(self.w.console.verticalScrollBar().maximum())
        # end autofit_hsqc

    def autopick_hsqc(self, metabolite_list=False):
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        if metabolite_list is False:
            metabolite_list = [self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite]
        elif len(metabolite_list[0]) == 0:
            metabolite_list = [self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite]

        print(f'autopick_hsqc: {metabolite_list}')
        if len(metabolite_list[0]) == 0:
            return

        if self.w.hsqcAnalysis.isChecked() == False:
            self.w.hsqcAnalysis.setChecked(True)
            self.w.hsqcAnalysis.setChecked(False)

        no_peak_selected = False
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak == -1:
            no_peak_selected = True
            cur_peak = 1
        else:
            cur_peak = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak

        self.nd.nmrdat[self.nd.s][self.nd.e].autopick_hsqc(metabolite_list)
        if no_peak_selected:
            self.w.hsqcAnalysis.setChecked(False)
            self.w.hsqcAnalysis.setChecked(True)
            idx1 = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.metabolite_list.index(metabolite_list[0])
            self.w.hsqcMetabolites.setCurrentIndex(self.w.hsqcMetabolites.model().index(idx1, 0))

        self.set_hsqc_metabolite()
        self.plot_metabolite_peak(cur_peak)
        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        code_out.close()
        code_err.close()
        self.w.console.verticalScrollBar().setValue(self.w.console.verticalScrollBar().maximum())
        # end autopick_hsqc

    def clear_console(self):
        self.nd.console = ""
        self.w.console.setText("")
        # end clear_console

    def clear_peak(self):
        self.nd.clear_peak()
        self.w.peakWidget.setRowCount(0)
        self.plot_spc()
        # end add_peak

    def adaptive_lb(self):
        self.nd.adaptive_lb()
        self.plot_spc()

    def apply_2d_ph_corr(self):
        s = self.nd.s
        e = self.nd.e
        if self.nd.nmrdat[s][e].proc.phase_inversion:
            self.ph_corr.ph0_2d[self.ph_corr.dim] *= -1
            self.ph_corr.ph1_2d[self.ph_corr.dim] *= -1

        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_ph_corr_click_2d)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_ph_corr_release_2d)
        cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # self.w.actionApplyPhCorr.triggered.disconnect()
        # self.w.actionCancelPhCorr.triggered.disconnect()
        self.w.pickRowColPhCorr2d.setVisible(True)
        self.w.emptyRowColPhCorr2d.setVisible(True)
        self.w.removeRowColPhCorr2d.setVisible(True)
        self.w.horzPhCorr2d.setVisible(True)
        self.w.vertPhCorr2d.setVisible(True)
        self.w.zoomPhCorr2d.setVisible(False)
        self.w.applyPhCorr2d.setVisible(False)
        self.w.cancelPhCorr2d.setVisible(False)
        self.w.exitPhCorr2d.setVisible(True)
        self.w.exitZoomPhCorr2d.setVisible(False)
        ph0 = ((self.ph_corr.ph0_2d[self.ph_corr.dim] + 180.0) % 360.0) - 180.0
        ph1 = self.ph_corr.ph1_2d[self.ph_corr.dim]
        if self.nd.nmrdat[s][e].proc.phase_inversion is False:
            self.nd.nmrdat[s][e].phase2a(ph0, ph1, self.ph_corr.dim)
        else:
            self.nd.nmrdat[s][e].phase2a(-ph0, -ph1, self.ph_corr.dim)

        ph0 = ((ph0 + self.nd.nmrdat[s][e].proc.ph0[self.ph_corr.dim] + 180.0) % 360.0) - 180.0
        ph1 = ph1 + self.nd.nmrdat[s][e].proc.ph1[self.ph_corr.dim]

        self.nd.nmrdat[s][e].proc.ph0[self.ph_corr.dim] = ph0
        self.nd.nmrdat[s][e].proc.ph1[self.ph_corr.dim] = ph1
        self.ph_corr.ph0_2d[self.ph_corr.dim] = 0
        self.ph_corr.ph1_2d[self.ph_corr.dim] = 0
        self.ph_corr.spc = np.array([[]], dtype='complex')
        self.ph_corr.spc2 = np.array([[]], dtype='complex')
        zoom_status = self.w.keepZoom.isChecked()
        self.w.keepZoom.setChecked(False)
        self.plot_spc()
        self.w.keepZoom.setChecked(zoom_status)
        self.plot_2d_col_row()
        if (self.zoom_was_on == True):
            self.set_zoom_off()
            self.set_zoom()

        if (self.pan_was_on == True):
            self.set_pan()

        self.show_ph_corr2d()
        self.set_proc_pars()
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end apply_2d_ph_corr

    def autobaseline(self, alg='rolling_ball', half_window=4096, smooth_half_window=16, lam=1e5, quantile=0.3, poly_order=4, add_ext=2):
        if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1:
            self.autobaseline1d(alg=alg, half_window=half_window, lam=lam, quantile=quantile, poly_order=poly_order, smooth_half_window=smooth_half_window, add_ext=add_ext)
        elif self.nd.nmrdat[self.nd.s][self.nd.e].dim == 2:
            self.autobaseline2d()

        # end autobaseline

    def autobaseline_all(self, alg='jbcd'):
        ce = self.nd.e
        n_exp = len(self.nd.nmrdat[self.nd.s])
        for k in range(n_exp):
            self.nd.e = k
            if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1:
                self.autobaseline1d(alg='jbcd')
            elif self.nd.nmrdat[self.nd.s][self.nd.e].dim == 2:
                self.autobaseline2d()

        self.nd.e = ce
        self.plot_spc()
        # end autobaseline

    def autobaseline1d(self, alg='rolling_ball', lam=1e5, max_iter=50, alpha=0.1, beta=10, gamma=15, beta_mult=0.98, gamma_mult=0.94, half_window=4096, quantile=0.3, poly_order=4, smooth_half_window=16, add_ext=2):
        #code_out = io.StringIO()
        #code_err = io.StringIO()
        #sys.stdout = code_out
        #sys.stderr = code_err
        self.show_auto_baseline()
        self.nd.ft()
        self.nd.auto_ref()
        self.nd.autobaseline1d(alg=alg, lam=lam, max_iter=max_iter, alpha=alpha, beta=beta, gamma=gamma, beta_mult=beta_mult, gamma_mult=gamma_mult, half_window=half_window, quantile=quantile, poly_order=poly_order, smooth_half_window=smooth_half_window, add_ext=add_ext)
        self.nd.auto_ref()
        self.show_version()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline = True
        self.set_autobaseline()
        #sys.stdout = sys.__stdout__
        #sys.stderr = sys.__stderr__
        #if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
        #    txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
        #    err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        #else:
        #    txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
        #    err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)
        #
        #self.w.console.setTextColor(txt_col)
        #self.w.console.append(code_out.getvalue())
        #self.w.console.setTextColor(err_col)
        #self.w.console.append(code_err.getvalue())
        #code_out.close()
        #code_err.close()
        # end autobaseline1d

    def autobaseline1d_old(self):
        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        self.show_auto_baseline()
        self.nd.ft()
        self.nd.auto_ref()
        self.nd.autobaseline1d()
        self.w.baselineCorrection.setCurrentIndex(1)
        self.nd.ft()
        self.nd.baseline1d()
        # self.w.baselineCorrection.setCurrentIndex(1)
        self.set_proc_pars()
        self.show_version()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        self.w.console.setTextColor(err_col)
        self.w.console.append(code_err.getvalue())
        code_out.close()
        code_err.close()
        # end autobaseline1d_old

    def autobaseline2d(self, poly_order=[16, 16], threshold=0.05):
        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        self.show_auto_baseline()
        self.nd.nmrdat[self.nd.s][self.nd.e].autobaseline2d(poly_order, threshold)
        self.show_version()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        self.w.console.setTextColor(err_col)
        self.w.console.append(code_err.getvalue())
        code_out.close()
        code_err.close()
        # end autobaseline2d

    def autobaseline1d_all(self):
        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        self.show_auto_baseline()
        self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline = True
        self.set_autobaseline()
        self.nd.ft_all()
        self.nd.auto_ref_all()
        self.nd.autobaseline1d_all()
        #self.w.baselineCorrection.setCurrentIndex(1)
        #self.nd.ft()
        #self.nd.baseline1d()
        # self.w.baselineCorrection.setCurrentIndex(1)
        self.set_proc_pars()
        self.show_version()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        self.w.console.setTextColor(err_col)
        self.w.console.append(code_err.getvalue())
        code_out.close()
        code_err.close()
        # end autobaseline1d_all

    def autophase1d(self, width=128, num_windows=1024, max_peaks=1000, noise_fact=20):
        if width == False:
            width = 128
            num_windows = 1024
            max_peaks = 1000
            noise_fact = 20

        self.show_auto_phase()
        self.nd.ft()
        self.nd.auto_ref()
        self.nd.autophase1d(width, num_windows, max_peaks, noise_fact)
        self.set_proc_pars()
        self.show_version()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        # end autophase1d

    def autophase1d1(self, gamma_factor=1.0):
        self.show_auto_phase()
        self.nd.ft()
        self.nd.auto_ref()
        self.nd.autophase1d1(gamma_factor=gamma_factor)
        self.set_proc_pars()
        self.show_version()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        # end autophase1d1

    def autophase1d_bl(self):
        self.nd.autophase1d_bl()
        self.update_gui()
        self.plot_spc(True)

    def autophase1d_bl_all(self):
        self.nd.autophase1d_bl_all()
        self.plot_spc(True)

    def autophase1d_all(self):
        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        self.show_auto_phase()
        self.nd.ft()
        self.nd.auto_ref()
        self.nd.autophase1d_all()
        self.plot_spc(True)
        self.set_proc_pars()
        self.show_version()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        self.w.console.setTextColor(err_col)
        self.w.console.append(code_err.getvalue())
        code_out.close()
        code_err.close()
        # end autophase1d_all

    def autophase1d1_all(self):
        self.nd.autophase1d1_all()
        self.plot_spc(True)

    def autophase1d_exclude_water(self, delta_sw=-1):
        self.nd.autophase1d_exclude_water(delta_sw)

    # end autophase1d_exclude_water

    def autophase1d_include_water(self):
        self.nd.autophase1d_include_water()

    # end autophase1d_hsqcinclude_water

    def auto_ref(self, tmsp=True):
        self.nd.auto_ref(tmsp)
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        return "autoref"
        # end autoref

    def auto_ref_all(self, tmsp=True):
        self.nd.auto_ref_all(tmsp)
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        return "autoref"
        # end autoref

    def automatic_referencing(self):
        self.nd.auto_ref(True)
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        # end automatic_referencing

    def baseline1d(self):
        self.nd.baseline1d()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        # end baseline1d

    def baseline1d_all(self):
        self.nd.baseline1d_all()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc(True)
        # end baseline1d

    def cancel_2d_ph_corr(self):
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_ph_corr_click_2d)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_ph_corr_release_2d)
        cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # self.w.actionApplyPhCorr.triggered.disconnect()
        # self.w.actionCancelPhCorr.triggered.disconnect()
        self.w.pickRowColPhCorr2d.setVisible(True)
        self.w.emptyRowColPhCorr2d.setVisible(True)
        self.w.removeRowColPhCorr2d.setVisible(True)
        self.w.horzPhCorr2d.setVisible(True)
        self.w.vertPhCorr2d.setVisible(True)
        self.w.zoomPhCorr2d.setVisible(False)
        self.w.applyPhCorr2d.setVisible(False)
        self.w.cancelPhCorr2d.setVisible(False)
        self.w.exitPhCorr2d.setVisible(True)
        self.w.exitZoomPhCorr2d.setVisible(False)
        self.ph_corr.ph0_2d[self.ph_corr.dim] = 0
        self.ph_corr.ph1_2d[self.ph_corr.dim] = 0
        zoomStatus = self.w.keepZoom.isChecked()
        self.w.keepZoom.setChecked(False)
        self.plot_spc()
        self.w.keepZoom.setChecked(zoomStatus)
        self.plot_2d_col_row()
        if (self.zoom_was_on == True):
            self.set_zoom_off()
            self.set_zoom()

        if (self.pan_was_on == True):
            self.set_pan()

        self.show_ph_corr2d()
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end cancel2dPhCorr

    def disconnect(self):
        self.w.posColR.textChanged.disconnect()
        self.w.posColG.textChanged.disconnect()
        self.w.posColB.textChanged.disconnect()
        self.w.negColR.textChanged.disconnect()
        self.w.negColG.textChanged.disconnect()
        self.w.negColB.textChanged.disconnect()
        self.w.nLevels.textChanged.disconnect()
        self.w.minLevel.textChanged.disconnect()
        self.w.maxLevel.textChanged.disconnect()
        self.w.axisType1.currentIndexChanged.disconnect()
        self.w.axisType2.currentIndexChanged.disconnect()
        self.w.displaySpc.currentIndexChanged.disconnect()
        self.w.baselineCorrection.currentIndexChanged.disconnect()
        self.w.baselineOrder.currentIndexChanged.disconnect()
        self.w.spcOffset.textChanged.disconnect()
        self.w.spcScale.textChanged.disconnect()
        self.w.fontSize.valueChanged.disconnect()
        self.w.xLabel.textChanged.disconnect()
        self.w.yLabel.textChanged.disconnect()
        self.w.spcLabel.textChanged.disconnect()
        # end disconnect

    def connect(self):
        self.w.posColR.textChanged.connect(self.get_disp_pars3)
        self.w.posColG.textChanged.connect(self.get_disp_pars3)
        self.w.posColB.textChanged.connect(self.get_disp_pars3)
        self.w.negColR.textChanged.connect(self.get_disp_pars3)
        self.w.negColG.textChanged.connect(self.get_disp_pars3)
        self.w.negColB.textChanged.connect(self.get_disp_pars3)
        self.w.nLevels.textChanged.connect(self.get_disp_pars4)
        self.w.minLevel.textChanged.connect(self.get_disp_pars5)
        self.w.maxLevel.textChanged.connect(self.get_disp_pars6)
        self.w.axisType1.currentIndexChanged.connect(self.get_disp_pars7)
        self.w.axisType2.currentIndexChanged.connect(self.get_disp_pars8)
        self.w.displaySpc.currentIndexChanged.connect(self.get_disp_pars9)
        self.w.baselineCorrection.currentIndexChanged.connect(self.check_baseline_correction)
        self.w.baselineOrder.currentIndexChanged.connect(self.check_baseline_order)
        self.w.spcOffset.textChanged.connect(self.get_disp_pars10)
        self.w.spcScale.textChanged.connect(self.get_disp_pars11)
        self.w.fontSize.valueChanged.connect(self.set_font_size)
        self.w.xLabel.textChanged.connect(self.get_disp_pars12)
        self.w.yLabel.textChanged.connect(self.get_disp_pars13)
        self.w.spcLabel.textChanged.connect(self.get_disp_pars14)
        # end connect

    def change_data_set_exp(self):
        self.disconnect()
        self.w.cmdLine.setFocus()
        self.w.cmdLine.clearFocus()
        met_idx = self.w.hsqcMetabolites.currentIndex()
        cur_peak = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak
        cur_metabolite = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite
        cidx = self.w.nmrSpectrum.currentIndex()
        dam = False
        dls = False
        dsm = False
        hac = False
        if self.w.displayAssignedMetabolites.isChecked() == True:
            dam = True
            self.w.displayAssignedMetabolites.setChecked(False)

        if self.w.displayLibraryShifts.isChecked() == True:
            dls = True
            self.w.displayLibraryShifts.setChecked(False)

        if self.w.displaySelectedMetabolite.isChecked() == True:
            dsm = True
            self.w.displaySelectedMetabolite.setChecked(False)

        if self.w.hsqcAnalysis.isChecked() == True:
            hac = True
            self.w.hsqcAnalysis.setChecked(False)

        if (len(self.nd.nmrdat) > 0):
            if (len(self.nd.nmrdat[self.nd.s]) > 0):
                self.keep_zoom = self.w.keepZoom.isChecked()
                old_set = self.nd.s
                old_exp = self.nd.e
                if (self.w.setBox.value() < 1):
                    self.w.setBox.setValue(1)

                if (self.w.expBox.value() < 1):
                    self.w.expBox.setValue(1)

                if (self.w.setBox.value() > len(self.nd.nmrdat)):
                    self.w.setBox.setValue(len(self.nd.nmrdat))

                self.nd.s = self.w.setBox.value() - 1
                if (self.w.expBox.value() > len(self.nd.nmrdat[self.nd.s])):
                    self.w.expBox.setValue(len(self.nd.nmrdat[self.nd.s]))

                self.nd.e = self.w.expBox.value() - 1
                if len(self.nd.nmrdat) > (self.nd.s + 1):
                    if len(self.nd.nmrdat[self.nd.s + 1]) > self.nd.e and len(self.nd.nmrdat[self.nd.s + 1]) > old_exp:
                        if self.nd.nmrdat[self.nd.s][old_exp].display.display_spc != True and self.nd.nmrdat[self.nd.s+1][old_exp].display.display_spc == True:
                            self.nd.nmrdat[self.nd.s+1][old_exp].display.display_spc = False
                            self.nd.nmrdat[self.nd.s+1][self.nd.e].display.display_spc = True
                keep_zoom = self.w.keepZoom.isChecked()
                if not ((old_set == self.nd.s) and (old_exp == self.nd.e)):
                    if (self.nd.nmrdat[old_set][old_exp].dim != self.nd.nmrdat[self.nd.s][self.nd.e].dim):
                        self.keep_x_zoom = True
                        self.keep_zoom = False
                        self.w.keepZoom.setChecked(False)

                    self.set_disp_pars()
                    self.set_proc_pars()
                    self.set_acq_pars()
                    self.set_title_file()
                    self.set_pulse_program()
                    if (self.ph_corr_active == False):
                        #if (self.w.autoPlot.isChecked()):
                        #    self.plot_spc(True)
                        #elif (self.w.nmrSpectrum.currentIndex() == 0):
                        self.plot_spc(True)

                    else:
                        if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1:
                            self.ph_corr.spc = self.nd.nmrdat[self.nd.s][self.nd.e].spc
                            self.ph_corr_plot_spc()
                        else:
                            self.plot_spc(True)
                            self.plot_2d_col_row()

                    self.keep_zoom = keep_zoom
                    self.w.keepZoom.setChecked(keep_zoom)
                    # if
                # else:
                #    if (self.ph_corr_active == False):
                #        if (self.w.autoPlot.isChecked()):
                #            self.plot_spc()
                #        elif (self.w.nmrSpectrum.currentIndex() == 0):
                #            self.plot_spc()
                #
                #    else:
                #        self.ph_corr.spc = self.nd.nmrdat[self.nd.s][self.nd.e].spc
                #        self.ph_corr_plot_spc()

                self.keep_zoom = False

            else:
                self.w.setBox.valueChanged.disconnect()
                self.w.expBox.valueChanged.disconnect()
                self.w.expBox.setValue(0)
                self.w.setBox.setValue(0)
                self.w.setBox.valueChanged.connect(self.change_data_set_exp)
                self.w.expBox.valueChanged.connect(self.change_data_set_exp)

            self.w.wwStartLevel.textChanged.disconnect()
            self.update_gui()
            self.w.wwStartLevel.textChanged.connect(self.get_proc_pars28)
        else:
            self.w.setBox.valueChanged.disconnect()
            self.w.expBox.valueChanged.disconnect()
            self.w.expBox.setValue(0)
            self.w.setBox.setValue(0)
            self.w.setBox.valueChanged.connect(lambda: self.change_data_set_exp())
            self.w.expBox.valueChanged.connect(lambda: self.change_data_set_exp())

        if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 2 and hac == True:
            self.w.hsqcAnalysis.setChecked(True)
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak = cur_peak
            self.w.hsqcMetabolites.setCurrentIndex(self.w.hsqcMetabolites.model().index(met_idx.row(), 0))
            self.w.hsqcAssignedMetabolites.setCurrentIndex(self.w.hsqcAssignedMetabolites.model().index(-1, 0))
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite = cur_metabolite
            self.set_hsqc_metabolite()

        self.w.nmrSpectrum.setCurrentIndex(cidx)
        self.connect()
        # end change_data_set_exp

    def change_data_set_exp_ph_ref(self):
        if (len(self.nd.nmrdat) > 0):
            s = self.nd.s
            e = self.nd.e
            if (len(self.nd.nmrdat[self.nd.s]) > 0):
                if (self.w.phRefDS.value() < 0):
                    self.w.phRefDS.setValue(0)

                if (self.w.phRefExp.value() < 0):
                    self.w.phRefExp.setValue(0)

                if (self.w.phRefDS.value() > len(self.nd.nmrdat)):
                    self.w.phRefExp.setValue(len(self.nd.nmrdat))

                if (self.w.expBox.value() > len(self.nd.nmrdat[self.nd.s])):
                    self.w.expBox.setValue(len(self.nd.nmrdat[self.nd.s]))

                for k in range(len(self.nd.nmrdat)):
                    for l in range(len(self.nd.nmrdat[k])):
                        self.nd.nmrdat[k][l].display.ph_ref_ds = self.w.phRefDS.value()
                        self.nd.nmrdat[k][l].display.ph_ref_exp = self.w.phRefExp.value()

        # end change_data_set_exp_ph_ref

    def change_scale_spectra_ref_spc(self):
        self.nd.pp.scale_spectra_ref_spc = self.w.scaleSpectraRefSpc.value()
        # end change_scale_spectra_ref_spc

    def change_seg_align_ref_spc(self):
        self.nd.pp.seg_align_ref_spc = self.w.segAlignRefSpc.value()
        # end change_seg_align_ref_spc

    def change_standard_colours(self, pos_col1=(), neg_col1=(), pos_col2=(), neg_col2=()):
        if len(pos_col1) != 3:
            pos_col1 = self.std_pos_col1

        if len(neg_col1) != 3:
            neg_col1 = self.std_neg_col1

        if len(pos_col2) != 3:
            pos_col2 = self.std_pos_col2

        if len(neg_col2) != 3:
            neg_col2 = self.std_neg_col2

        self.std_pos_col1 = pos_col1
        self.std_neg_col1 = neg_col1
        self.std_pos_col2 = pos_col2
        self.std_neg_col2 = neg_col2
        self.set_standard_colours()

    # end change_standard_colours

    def change_title_file(self):
        try:
            self.nd.nmrdat[self.nd.s][self.nd.e].title = self.w.titleFile.toPlainText()
        except:
            pass
        # end change_title_file

    def change_to_next_ds(self):
        self.w.setBox.setValue(self.w.setBox.value() + 1)
        # end change_to_next_ds

    def change_to_next_exp(self):
        self.w.expBox.setValue(self.w.expBox.value() + 1)
        # end change_to_next_exp

    def change_to_previous_ds(self):
        self.w.setBox.setValue(self.w.setBox.value() - 1)
        # end change_to_previous_ds

    def change_to_previous_exp(self):
        self.w.expBox.setValue(self.w.expBox.value() - 1)
        # end change_to_previous_exp

    def check_baseline_correction(self):
        cbl = self.w.baselineCorrection.currentIndex()
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.correct_baseline = cbl
        if (cbl == 1):
            self.w.baselineOrder.setEnabled(True)
        else:
            self.w.baselineOrder.setEnabled(False)

        self.check_baseline_order()
        # end check_baseline_correction

    def check_baseline_order(self):
        blo = self.w.baselineOrder.currentIndex()
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.n_order = blo
        self.w.rSpc_p0.setEnabled(False)
        self.w.rSpc_p1.setEnabled(False)
        self.w.rSpc_p2.setEnabled(False)
        self.w.rSpc_p3.setEnabled(False)
        self.w.rSpc_p4.setEnabled(False)
        self.w.rSpc_p5.setEnabled(False)
        self.w.rSpc_p6.setEnabled(False)
        self.w.iSpc_p0.setEnabled(False)
        self.w.iSpc_p1.setEnabled(False)
        self.w.iSpc_p2.setEnabled(False)
        self.w.iSpc_p3.setEnabled(False)
        self.w.iSpc_p4.setEnabled(False)
        self.w.iSpc_p5.setEnabled(False)
        self.w.iSpc_p6.setEnabled(False)
        if (self.w.baselineOrder.isEnabled() == True):
            self.w.rSpc_p0.setEnabled(True)
            self.w.iSpc_p0.setEnabled(True)
            if (blo > 0):
                self.w.rSpc_p1.setEnabled(True)
                self.w.iSpc_p1.setEnabled(True)

            if (blo > 1):
                self.w.rSpc_p2.setEnabled(True)
                self.w.iSpc_p2.setEnabled(True)

            if (blo > 2):
                self.w.rSpc_p3.setEnabled(True)
                self.w.iSpc_p3.setEnabled(True)

            if (blo > 3):
                self.w.rSpc_p4.setEnabled(True)
                self.w.iSpc_p4.setEnabled(True)

            if (blo > 4):
                self.w.rSpc_p5.setEnabled(True)
                self.w.iSpc_p5.setEnabled(True)

            if (blo > 5):
                self.w.rSpc_p6.setEnabled(True)
                self.w.iSpc_p6.setEnabled(True)

        # end check_baseline_order

    def clear(self, kz2=False):
        #sys.stdout = sys.__stdout__
        #sys.stderr = sys.__stderr__
        self.w.displayAssignedMetabolites.setChecked(False)
        self.w.displayLibraryShifts.setChecked(False)
        self.w.displaySelectedMetabolite.setChecked(False)
        self.w.displayAssignedMetabolites.setVisible(False)
        self.w.displayLibraryShifts.setVisible(False)
        self.w.displaySelectedMetabolite.setVisible(False)
        self.w.hsqcAnalysis.setChecked(False)
        self.w.hsqcAnalysis.setVisible(False)
        self.w.preprocessing.setChecked(False)
        self.w.preprocessing.setVisible(False)
        self.w.peakPicking.setChecked(False)
        self.w.peakPicking.setVisible(False)
        self.w.splinebaseline.setChecked(False)
        self.w.splinebaseline.setVisible(False)
        self.w.MplWidget.canvas.axes.clear()
        self.w.MplWidget.canvas.draw()
        self.zero_disp_pars()
        self.zero_proc_pars()
        self.zero_acq_pars()
        self.zero_console()
        self.zero_title_file()
        self.zero_pulse_program()
        self.nd.nmrdat = [[]]
        self.nd.s = 0
        self.nd.e = -1
        self.w.setBox.valueChanged.disconnect()
        self.w.expBox.valueChanged.disconnect()
        self.w.expBox.setValue(0)
        self.w.setBox.setValue(0)
        self.w.setBox.valueChanged.connect(lambda: self.change_data_set_exp())
        self.w.expBox.valueChanged.connect(lambda: self.change_data_set_exp())
        #code_out = io.StringIO()
        #code_err = io.StringIO()
        #try:
        #    sys.stdout = code_out
        #    sys.stderr = code_err
        #except:
        #    pass

        kz = self.w.keepZoom.isChecked()
        if kz2:
            self.w.keepZoom.setChecked(False)

        return kz
        # end clear

    def clear_assigned_hsqc(self):
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data = {}
        self.update_assigned_metabolites()
        self.w.hsqcMetabolites.setCurrentIndex(self.w.hsqcMetabolites.model().index(-1, 0))
        if hasattr(self.w.metaboliteImage.scene(), 'clear'):
            self.w.metaboliteImage.scene().clear()

        self.delete_buttons(0)
        self.w.hsqcPeak.canvas.axes.clear()
        self.w.hsqcPeak.canvas.draw()
        self.w.hsqcMultiplet.canvas.axes.clear()
        self.w.hsqcMultiplet.canvas.draw()
        self.w.metaboliteInformation.setText('')
        self.w.multipletAnalysisIntensity.setText('')
        self.w.multipletAnalysisR2.setText('')
        self.w.multipletAnalysisEchoTime.setText('')
        self.w.openWeb.clear()
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite = ''
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak = -1
        self.w.hsqcSpinSys.setRowCount(0)
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            colour = [180, 180, 180]
        else:
            colour = [0, 0, 0]

        self.w.coefficientOfDetermination.display(-1)
        palette = self.w.coefficientOfDetermination.palette()
        # foreground color
        #palette.setColor(palette.currentColorGroup(), QPalette.WindowText, QtGui.QColor(colour[0], colour[1], colour[2]))
        palette.setColor(palette.currentColorGroup(), QPalette.WindowText, QtGui.QColor(colour[0], colour[1], colour[2]))
        # background color
        # palette.setColor(palette.Background, QtGui.QColor(colour[0], colour[1], colour[2]))
        # "light" border
        palette.setColor(palette.currentColorGroup(), QPalette.Light, QtGui.QColor(colour[0], colour[1], colour[2]))
        # "dark" border
        palette.setColor(palette.currentColorGroup(), QPalette.Dark, QtGui.QColor(colour[0], colour[1], colour[2]))
        self.w.coefficientOfDetermination.setPalette(palette)
        # end clear_assigned_hsqc

    def clear_spline_points(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.xdata = []
            self.ydata = []
            if self.nd.nmrdat[self.nd.s][k].display.display_spc or k == self.nd.e:
                self.nd.nmrdat[self.nd.s][k].spline_baseline.baseline_points = []
                self.nd.nmrdat[self.nd.s][k].spline_baseline.baseline_points_pts = []
                self.nd.nmrdat[self.nd.s][k].spline_baseline.baseline_values = []

        self.fill_spline_baseline_tw()
        self.plot_spc(True)
        # end clear_spline_points

    def reset_spline_points(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            if self.nd.nmrdat[self.nd.s][k].display.display_spc or k == self.nd.e:
                self.nd.nmrdat[self.nd.s][k].proc_spc1d()
                self.nd.nmrdat[self.nd.s][k].add_baseline_points()

        self.plot_spc(True)
        # end clear_spline_points

    def cnst(self, index=-1):
        if index == -1:
            print(f'cnst = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.cnst}')
        else:
            print("cnst({}) = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.cnst[index]))

        # end cnst

    def corr_spline_baseline(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            if self.nd.nmrdat[self.nd.s][k].display.display_spc or k == self.nd.e:
                self.nd.nmrdat[self.nd.s][k].corr_spline_baseline()

        self.plot_spc(True)
        # end corr_spline_baseline

    def create_icon_mac(self):
        home_dir = os.path.expanduser('~')
        app_dir2 = os.path.join(home_dir, 'Applications')
        if not os.path.isdir(app_dir2):
            os.makedirs(app_dir2)

        app_dir = os.path.join(app_dir2, 'QtMetaboLabPy.app')
        app_dir1 = 'QtMetaboLabPy'
        try:
            shutil.rmtree(app_dir)
        except:
            pass

        appify = os.path.join(app_dir2, 'appify')
        f = open(appify, 'w')
        f.write('#!/usr/bin/env bash\n\n')
        f.write('APp_name=${2:-$(basename "$1" ".sh")}\n')
        f.write('DIR="$APp_name/$3.app/Contents/MacOS"\n\n')
        f.write('mkdir -p "$DIR"\n')
        f.write('cp "$1" "$DIR/$3"\n')
        f.write('chmod +x "$DIR/$3"\n')
        f.close()
        os.chmod(appify, 0o777)
        ml_starter = os.path.join(os.path.dirname(__file__), 'mlStarter')
        contents = os.path.join(ml_starter, 'Contents')
        icon = os.path.join(ml_starter, 'Icon')
        starter = os.path.join(app_dir2, 'createStarter')
        f = open(starter, 'w')
        f.write('#!/usr/bin/env bash\n\n')
        f.write(appify.replace(' ', '\ ') + ' $(which qtmetabolabpy) ' + app_dir2.replace(' ', '\ ') + ' ' + app_dir1.replace(' ', '\ ') + '\n')
        f.write('cp -r ' + contents.replace(' ', '\ ') + ' ' + app_dir.replace(' ', '\ ') + '\n')
        f.write("cp " + icon.replace(' ', '\ ') + " " + app_dir.replace(' ', '\ ') + "/Icon$'\\r'\n")
        f.close()
        os.chmod(starter, 0o777)
        subprocess.os.system(starter.replace(' ', '\ '))
        os.remove(appify)
        os.remove(starter)
        # end create_icon_mac

    def create_icon_linux(self):
        nmr_dir = os.path.split(inspect.getmodule(nmrDataSet).__file__)[0]
        base_dir = os.path.split(nmr_dir)[0]
        icon_file = os.path.join(base_dir, 'icon', 'icon-256.png')
        mlpy_file = os.path.join(os.path.expanduser('~'), '.local', 'bin', 'mlpy')
        starter_file = os.path.join(os.path.expanduser('~'), '.local', 'share', 'applications', 'metabolabpy.desktop')
        f = open(starter_file, 'w')
        f.write('[Desktop Entry]\n')
        f.write('Name=MetaboLabPy\n')
        f.write('GenericName=MetaboLabPy\n')
        f.write('Comment=Process NMR spectra\n')
        f.write('Exec="' + mlpy_file + '"\n')
        f.write('Icon=' + icon_file + '\n')
        f.write('Terminal=false\n')
        f.write('NoDisplay=true\n')
        f.write('Type=Application\n')
        f.write('StartupNotify=true\n')
        f.close()
        f = open(mlpy_file, 'w')
        f.write('#!/bin/bash\n')
        f.write('\n')
        f.write('export QT_XCB_GL_INTEGRATION=none\n')
        f.write('qtmetabolabpy')
        f.close()
        os.chmod(mlpy_file, 0o775)

        # end create_icon_linux

    def create_icon_win(self):
        nmr_dir = os.path.split(inspect.getmodule(nmrDataSet).__file__)[0]
        base_dir = os.path.split(nmr_dir)[0]
        icon_file = os.path.join(base_dir, 'icon', 'icon.ico')
        user_dir = os.environ.get('USERPROFILE')
        #desktop_dir = os.path.join(user_dir, 'Desktop')
        result = subprocess.run('powershell.exe [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)', shell=True, capture_output=True)
        desktop_dir = result.stdout.decode('ascii').replace('\r\n','')
        link_file = os.path.join(desktop_dir, 'MetaboLabPy.lnk')
        app_data =  subprocess.run('powershell.exe [Environment]::GetFolderPath([Environment+SpecialFolder]::ApplicationData)', shell=True, capture_output=True)
        start_menu_entry = os.path.join(app_data.stdout.decode('ascii').replace('\r\n',''), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'MetaboLabPy')
        if not os.path.isdir(start_menu_entry):
            os.makedirs(start_menu_entry)

        start_menu_entry = os.path.join(start_menu_entry, 'MetaboLabPy.lnk')
        ml_bat = os.path.join(base_dir, 'ml.bat')
        ml_exec_bat = os.path.join(base_dir, 'ml_exec.bat')
        f = open(ml_bat, 'w')
        f.write('start /min ' + ml_exec_bat.replace(' ', '" "'))
        f.close()
        f = open(ml_exec_bat, 'w')
        venv = sys.prefix.find('env')
        cnda = subprocess.check_output('where conda').decode()
        if venv == -1:
            f.write('qtmetabolabpy && exit')
        else:
            idx = sys.prefix.rfind('\\') + 1
            env = sys.prefix[idx:]
            f.write('"' + cnda[:-2] + '" activate ' + env + ' && qtmetabolabpy && exit')

        f.close()
        subprocess.os.system('pip install pylnk3')
        subprocess.os.system('pylnk3 create "' + ml_bat + '" "' + link_file + '" -m Minimized --icon "' + icon_file + '"')
        subprocess.os.system('pylnk3 create "' + ml_bat + '" "' + start_menu_entry + '" -m Minimized --icon "' + icon_file + '"')
        subprocess.os.system('pip uninstall pylnk3 --yes')
        # end create_icon_win

    def create_titles(self, dataset_label='', pos_label='', rack_label='', worksheet='', replace_orig_title=True, excel_name='', autosampler='SampleJet'):
        if dataset_label == '' or pos_label == '':
            msg = ''
            msg += '_____________________________________________________________________________MetaboLabPy Help__\n\n'
            msg += '    Usage:\n'
            msg += '        create_titles(dataset_label=<string>, pos_label=<string>, rack_label=<string>,\n'
            msg += '           worksheet=<string>, replace_orig_title=True/False, excel_name=<string>, autosampler=<string>)\n\n\n'
            msg += '        <string> for dataset_label, rack_label and pos_label refers to the Excel column\n'
            msg += '        headers. All three arguments are mandatory if autosampler is SampleJet. If autosampler is\n'\
                   '        SampleCase, rack_label is optional. replace_orig_title can be set to either\n'
            msg += '        True or False. If the argument is True, the previously existing title file information\n'
            msg += '        will be discarded, if the argument if False, the previous title file information will be\n'
            msg += '        added to the end of the new title file information. This argument is optional, the\n'
            msg += '        default value is to discard the original title file information.\n\n'
            msg += '        The excel_name argument should either be empty or a string containing path and file\n'
            msg += '        name information for the Excel spreadsheet. If the argument is empty, a GUI element\n'
            msg += '        pops up where the user can graphically choose the excel file. This is the default\n'
            msg += '        autosampler can be set to SampleJet or SampleCase depending on the autosampler used.\n'
            msg += '\n'
            msg += '        For autosampler=SampleCase, use the pos_label column to fill in Bruker NMR experiment numbers\n'
            msg += '        For this option, you do not need the rack_label column\n'
            msg += '\n_______________________________________________________________________________________________\n'
            print(msg)
            return

        if excel_name == '':
            answer = QFileDialog.getOpenFileName(None, 'Load Excel File', '', '*.xlsx')
            if answer[0] == '':
                return
            else:
                excel_name = answer[0]

        else:
            if not os.path.isfile(excel_name):
                return

        if len(worksheet) == 0:
            xls = pd.read_excel(excel_name).fillna('')
        else:
            xls = pd.read_excel(excel_name, worksheet).fillna('')

        something_not_found = False
        if len(np.where(xls.columns.str.contains(dataset_label))[0]) == 0:
            something_not_found = True
            print(f'dataset_label: {dataset_label} not found.')

        if len(np.where(xls.columns.str.contains(pos_label))[0]) == 0:
            something_not_found = True
            print(f'pos_label: {pos_label} not found.')

        if autosampler == 'SampleJet':
            if len(np.where(xls.columns.str.contains(rack_label))[0]) == 0:
                something_not_found = True
                print(f'rack_label: {rack_label} not found.')

        if something_not_found:
            return

        self.nd.create_titles(xls, dataset_label, pos_label, rack_label, replace_orig_title, excel_name, autosampler)
        self.update_gui()
        self.w.nmrSpectrum.setCurrentIndex(7)
    # end create_titles

    def d(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.delay) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'd = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.delay}')
        else:
            print("d{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.delay[index]))

        # end d

    def export_bruker_1d(self, all=True):
        selected_directory = QFileDialog.getExistingDirectory()
        if len(selected_directory[0]) == 0:
            return

        if all:
            self.nd.export_bruker_1d(selected_directory)
        else:
            self.nd.nmrdat[self.nd.s][self.nd.e].export_bruker_1d(selected_directory, str(10 * (self.nd.e + 1)))

        # end export_bruker

    def increase_y_lim(self):
        ylim = self.w.MplWidget.canvas.axes.get_ylim()
        ylim1 = ylim[0]*2
        ylim2 = ylim[1]*2
        self.w.MplWidget.canvas.axes.set_ylim((ylim1, ylim2))
        self.plot_spc()
        # end increase_y_lim

    def decrease_y_lim(self):
        ylim = self.w.MplWidget.canvas.axes.get_ylim()
        ylim1 = ylim[0]/2
        ylim2 = ylim[1]/2
        self.w.MplWidget.canvas.axes.set_ylim((ylim1, ylim2))
        self.plot_spc()
        # end decrease_y_lim

    def increase_x_lim(self):
        xlim = self.w.MplWidget.canvas.axes.get_xlim()
        mid_point = np.mean([xlim[0], xlim[1]])
        width = xlim[0] - xlim[1]
        xlim1 = mid_point + width
        xlim2 = mid_point - width
        self.w.MplWidget.canvas.axes.set_xlim((xlim1, xlim2))
        self.plot_spc()
        # end increase_x_lim

    def decrease_x_lim(self):
        xlim = self.w.MplWidget.canvas.axes.get_xlim()
        mid_point = np.mean([xlim[0], xlim[1]])
        width = (xlim[0] - xlim[1])/4.0
        xlim1 = mid_point + width
        xlim2 = mid_point - width
        self.w.MplWidget.canvas.axes.set_xlim((xlim1, xlim2))
        self.plot_spc()
        # end decrease_x_lim

    def peakw(self, ppm=0.0, message=True):
        self.nd.peakw(ppm = ppm, message = message)
        # end peakw_tmsp

    def peak_all(self, ppm=0.0, message=True):
        self.nd.peakw_all(ppm = ppm, message = message)
        # end peakw_tmsp_all

    def pl(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.power_level) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'pl = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.power_level} dB')
        else:
            print("pl{} = {} dB".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.power_level[index]))

        # end pl

    def plw(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.power_level_watt) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'plw = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.power_level_watt}')
        else:
            print("plw{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.power_level_watt[index]))

        # end plw

    def print_spc(self, file_name=-1):
        prg_mode = self.cf.mode
        if not file_name:
            file_name = QFileDialog.getSaveFileName(None, "Save Spectrum Plot", "", "*.pdf", "*.pdf")[0]

        if file_name.find('.pdf') == -1:
            file_name += '.pdf'

        if len(file_name) > 0:
            disp_spc = []
            ax_lw = self.w.MplWidget.canvas.axes.spines['bottom'].get_linewidth()
            ax_fs = self.w.MplWidget.canvas.axes.get_xticklabels()[0].get_fontsize()
            ax_ls = 10
            self.nd.init_print_colours()
            if self.w.nmrSpectrum.currentIndex() == 1:
                cv = []
                cv.append(self.w.hsqcMultiplet.canvas)
                cv.append(self.w.hsqcPeak.canvas)
            else:
                self.show_nmr_spectrum()
                cv = []
                cv.append(self.w.MplWidget.canvas)


            yticks = cv[0].axes.get_yticks()
            xticks = cv[0].axes.get_xticks()
            #if self.nd.cf.print_standard_colours:
            p_cols = self.nd.print_colours
            n_cols = self.nd.print_neg_colours
            cols = []
            cols_dict = {}
            cols_dict_rgb = {}
            orig_pos_col_rgb = []
            orig_pos_col = []
            orig_neg_col_rgb = []
            orig_neg_col = []
            for k in range(len(self.nd.nmrdat)):
                orig_pos_col_rgb.append([])
                orig_pos_col.append([])
                orig_neg_col_rgb.append([])
                orig_neg_col.append([])
                for l in range(len(self.nd.nmrdat[k])):
                    orig_pos_col_rgb[k].append(self.nd.nmrdat[k][l].display.pos_col_rgb)
                    orig_pos_col[k].append(self.nd.nmrdat[k][l].display.pos_col)
                    orig_neg_col_rgb[k].append(self.nd.nmrdat[k][l].display.neg_col_rgb)
                    orig_neg_col[k].append(self.nd.nmrdat[k][l].display.neg_col)
                    if self.nd.cf.print_standard_colours:
                        if self.nd.nmrdat[k][l].display.pos_col == 'RGB':
                            if self.nd.nmrdat[k][l].display.pos_col_rgb not in cols:
                                cols.append(self.nd.nmrdat[k][l].display.pos_col_rgb)
                                idx = len(cols) - 1
                                cols_dict_rgb[p_cols[idx]] = self.nd.nmrdat[k][l].display.pos_col_rgb
                                self.nd.nmrdat[k][l].display.pos_col_rgb = p_cols[idx]
                                self.nd.nmrdat[k][l].display.neg_col_rgb = n_cols[idx]
                            else:
                                idx = cols.index(self.nd.nmrdat[k][l].display.pos_col_rgb)
                                self.nd.nmrdat[k][l].display.pos_col_rgb = p_cols[idx]
                                self.nd.nmrdat[k][l].display.neg_col_rgb = n_cols[idx]
                        else:
                            if self.nd.nmrdat[k][l].display.pos_col not in cols:
                                cols.append(self.nd.nmrdat[k][l].display.pos_col)
                                idx = len(cols) - 1
                                cols_dict[p_cols[idx]] = self.nd.nmrdat[k][l].display.pos_col
                                self.nd.nmrdat[k][l].display.pos_col_rgb = p_cols[idx]
                                self.nd.nmrdat[k][l].display.neg_col_rgb = n_cols[idx]
                            else:
                                idx = cols.index(self.nd.nmrdat[k][l].display.pos_col)
                                self.nd.nmrdat[k][l].display.pos_col_rgb = p_cols[idx]
                                self.nd.nmrdat[k][l].display.pos_col_rgb = p_cols[idx]

                            self.nd.nmrdat[k][l].display.pos_col = 'RGB'


            cv[0].draw()
            if len(cv) > 1:
                cv[1].draw()

            matplotlib.pyplot.rc('axes', labelsize=self.nd.cf.print_label_font_size)
            matplotlib.pyplot.rc('xtick', labelsize=self.nd.cf.print_ticks_font_size)
            matplotlib.pyplot.rc('ytick', labelsize=self.nd.cf.print_ticks_font_size)
            if len(cv) == 1:
                self.plot_spc(linewidth=self.nd.cf.print_spc_linewidth)
            else:
                if self.cf.print_light_mode:
                    self.cf.mode = 'light'
                else:
                    self.cf.mode = 'dark'

                cur_peak = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak
                self.plot_metabolite_peak(cur_peak)
                self.cf.mode = prg_mode

            bg = self.nd.print_background_colour
            fg = self.nd.print_foreground_colour
            cv[0].figure.set_facecolor(bg)
            cv[0].axes.set_facecolor(bg)
            cv[0].axes.xaxis.label.set_color(fg)
            cv[0].axes.yaxis.label.set_color(fg)
            cv[0].axes.tick_params(axis='x', colors=fg)
            cv[0].axes.tick_params(axis='y', colors=fg)
            cv[0].axes.spines['bottom'].set_color(fg)
            cv[0].axes.spines['left'].set_color(fg)
            cv[0].axes.spines['right'].set_color(fg)
            cv[0].axes.spines['top'].set_color(fg)
            if self.cf.print_light_mode:
                self.show_legend(mode='light')
            else:
                self.show_legend(mode='dark')

            if len(cv) > 1:
                cv[1].figure.set_facecolor(bg)
                cv[1].axes.set_facecolor(bg)
                cv[1].axes.xaxis.label.set_color(fg)
                cv[1].axes.yaxis.label.set_color(fg)
                cv[1].axes.tick_params(axis='x', colors=fg)
                cv[1].axes.tick_params(axis='y', colors=fg)
                cv[1].axes.spines['bottom'].set_color(fg)
                cv[1].axes.spines['left'].set_color(fg)
                cv[1].axes.spines['right'].set_color(fg)
                cv[1].axes.spines['top'].set_color(fg)

            ylim = cv[0].axes.get_ylim()
            xlim = cv[0].axes.get_xlim()
            if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1 or len(cv) > 1:
                if self.nd.cf.print_left_axis == False:
                    cv[0].axes.set_yticks([])
                    cv[0].axes.set_ylabel('')

                if self.nd.cf.print_bottom_axis == False:
                    cv[0].axes.set_xticks([])
                    cv[0].axes.set_xlabel('')


                cv[0].draw()
                cv[0].axes.spines['bottom'].set_visible(ax_lw)
                cv[0].axes.spines['left'].set_visible(self.nd.cf.print_left_axis)
                cv[0].axes.spines['top'].set_visible(self.nd.cf.print_top_axis)
                cv[0].axes.spines['right'].set_visible(self.nd.cf.print_right_axis)
                cv[0].axes.spines['bottom'].set_visible(self.nd.cf.print_bottom_axis)

            cv[0].axes.spines['bottom'].set_linewidth(self.nd.cf.print_axes_linewidth)
            cv[0].axes.spines['left'].set_linewidth(self.nd.cf.print_axes_linewidth)
            cv[0].axes.spines['right'].set_linewidth(self.nd.cf.print_axes_linewidth)
            cv[0].axes.spines['top'].set_linewidth(self.nd.cf.print_axes_linewidth)
            cv[0].axes.tick_params(width=self.nd.cf.print_axes_linewidth)
            cv[0].axes.set_ylim(ylim)
            cv[0].axes.set_xlim(xlim)
            if len(cv) > 1:
                cv[1].draw()
                cv[1].axes.spines['bottom'].set_linewidth(self.nd.cf.print_axes_linewidth)
                cv[1].axes.spines['left'].set_linewidth(self.nd.cf.print_axes_linewidth)
                cv[1].axes.spines['right'].set_linewidth(self.nd.cf.print_axes_linewidth)
                cv[1].axes.spines['top'].set_linewidth(self.nd.cf.print_axes_linewidth)
                cv[1].axes.tick_params(width=self.nd.cf.print_axes_linewidth)

            if self.w.nmrSpectrum.currentIndex() == 0:
                orig_e = self.nd.e
                for k in range(len(self.nd.nmrdat[self.nd.s])):
                    if self.nd.nmrdat[self.nd.s][k].display.display_spc == True:
                        disp_spc.append(k)
                        self.nd.nmrdat[self.nd.s][k].display.display_spc = False

                if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1 and self.cf.print_stacked_plot and len(disp_spc) > 1:
                    for kk in range(len(disp_spc)):
                        self.nd.nmrdat[self.nd.s][self.nd.e].display.display_spc = False
                        self.nd.e = disp_spc[kk]
                        self.nd.nmrdat[self.nd.s][self.nd.e].display.display_spc = True
                        self.plot_spc(linewidth=self.nd.cf.print_spc_linewidth)
                        bg = self.nd.print_background_colour
                        fg = self.nd.print_foreground_colour
                        cv[0].figure.set_facecolor(bg)
                        cv[0].axes.set_facecolor(bg)
                        cv[0].axes.xaxis.label.set_color(fg)
                        cv[0].axes.yaxis.label.set_color(fg)
                        cv[0].axes.tick_params(axis='x', colors=fg)
                        cv[0].axes.tick_params(axis='y', colors=fg)
                        cv[0].axes.spines['bottom'].set_color(fg)
                        cv[0].axes.spines['left'].set_color(fg)
                        cv[0].axes.spines['right'].set_color(fg)
                        cv[0].axes.spines['top'].set_color(fg)
                        if self.nd.cf.print_left_axis == False:
                            cv[0].axes.set_yticks([])
                            cv[0].axes.set_ylabel('')

                        if kk > 0:
                            if not self.cf.print_stacked_plot_repeat_axes:
                                cv[0].axes.set_xticks([])
                                cv[0].axes.set_xlabel('')
                                cv[0].axes.spines['left'].set_visible(False)
                                cv[0].axes.spines['top'].set_visible(False)
                                cv[0].axes.spines['right'].set_visible(False)
                                cv[0].axes.spines['bottom'].set_visible(False)
                                cv[0].axes.set_yticks([])
                                cv[0].axes.set_ylabel('')

                        cv[0].draw()
                        cv[0].axes.set_ylim(ylim)
                        cv[0].axes.set_xlim(xlim)
                        if self.cf.print_auto_scale == True:
                            self.vertical_auto_scale()

                        f_name = file_name[:file_name.index('.pdf')]
                        figure_width = cv[0].figure.get_figwidth()
                        figure_height = cv[0].figure.get_figheight()
                        if self.cf.print_nmr_spectrum_aspect_ratio != 'auto':
                            if self.cf.print_nmr_spectrum_aspect_ratio == 'a4_portrait':
                                fw = 8.27
                                fh = 11.69 / len(disp_spc)
                                cv[0].figure.set_figwidth(fw)
                                cv[0].figure.set_figheight(fh)
                            elif self.cf.print_nmr_spectrum_aspect_ratio == 'a4_landscape':
                                fw = 11.69
                                fh = 8.27 / len(disp_spc)
                                cv[0].figure.set_figwidth(fw)
                                cv[0].figure.set_figheight(fh)
                            else:
                                cv[0].figure.set_figwidth(self.cf.print_nmr_spectrum_aspect_ratio * cv[0].figure.get_figheight())

                        if self.cf.print_nmr_spectrum_aspect_ratio == 'a4_portrait':
                            bottomval = 0.15 + 0.15 * len(disp_spc) / 7.0
                            if kk > 0:
                                if self.cf.print_stacked_plot_repeat_axes:
                                    cv[0].figure.subplots_adjust(bottom=bottomval)
                                else:
                                    cv[0].figure.subplots_adjust(bottom=0.0)
                            else:
                                if self.cf.print_bottom_axis:
                                    cv[0].figure.subplots_adjust(bottom=bottomval)
                                else:
                                    cv[0].figure.subplots_adjust(bottom=0.0)

                        elif self.cf.print_nmr_spectrum_aspect_ratio == 'a4_landscape':
                            bottomval = 0.1 + 0.3 * len(disp_spc) / 7.0
                            if kk > 0:
                                if self.cf.print_stacked_plot_repeat_axes:
                                    cv[0].figure.subplots_adjust(bottom=bottomval)
                                else:
                                    cv[0].figure.subplots_adjust(bottom=0.0)
                            else:
                                if self.cf.print_bottom_axis:
                                    cv[0].figure.subplots_adjust(bottom=bottomval)
                                else:
                                    cv[0].figure.subplots_adjust(bottom=0.0)

                        else:
                            if self.cf.print_bottom_axis:
                                cv[0].figure.subplots_adjust(bottom=0.2)
                            else:
                                cv[0].figure.subplots_adjust(bottom=0.0)

                        ff = []
                        if self.cf.print_label:
                            label = self.nd.nmrdat[self.nd.s][self.nd.e].title
                            idx1 = label.find('spcLabel:')
                            if idx1 > -1:
                                label = label[idx1:]
                                idx2 = label.find('\n')
                                if idx2 > -1:
                                    label = label[:idx2]

                                idx3 = label.find(':')
                                label = label[idx3 + 1:].strip()
                                ff = cv[0].axes.legend([label], fontsize=self.cf.print_label_font_size, frameon=False, shadow=False, loc='upper right')
                                hh = ff.legendHandles[0]
                                hh.set_linestyle("")
                                cv[0].draw()
                                cv[0].figure.savefig(f_name + f'_{kk}.pdf', transparent=not self.nd.cf.print_background)
                                ff.remove()
                            else:
                                cv[0].figure.savefig(f_name + f'_{kk}.pdf', transparent=not self.nd.cf.print_background)
                        else:
                            cv[0].figure.savefig(f_name + f'_{kk}.pdf', transparent=not self.nd.cf.print_background)

                        cv[0].draw()
                        cv[0].figure.set_figwidth(figure_width)
                        cv[0].figure.set_figheight(figure_height)
                        cv[0].figure.subplots_adjust(bottom=0.1)

                    self.nd.e = orig_e
                else:
                    figure_width = cv[0].figure.get_figwidth()
                    figure_height = cv[0].figure.get_figheight()
                    if self.cf.print_nmr_spectrum_aspect_ratio != 'auto':
                        if self.cf.print_nmr_spectrum_aspect_ratio == 'a4_portrait':
                            fw = 8.27
                            fh = 11.69
                            cv[0].figure.set_figwidth(fw)
                            cv[0].figure.set_figheight(fh)
                        elif self.cf.print_nmr_spectrum_aspect_ratio == 'a4_landscape':
                            fw = 11.69
                            fh = 8.27
                            cv[0].figure.set_figwidth(fw)
                            cv[0].figure.set_figheight(fh)
                        else:
                            cv[0].figure.set_figwidth(self.cf.print_nmr_spectrum_aspect_ratio * cv[0].figure.get_figheight())

                    cv[0].figure.savefig(file_name, transparent=not self.nd.cf.print_background)
                    cv[0].figure.set_figwidth(figure_width)
                    cv[0].figure.set_figheight(figure_height)
                for kk in range(len(disp_spc)):
                    self.nd.nmrdat[self.nd.s][disp_spc[kk]].display.display_spc = True

            elif self.w.nmrSpectrum.currentIndex() == 1:
                f_name = file_name[:file_name.index('.pdf')]
                file_name = f_name + '_multiplet.pdf'
                figure_width = cv[0].figure.get_figwidth()
                figure_height = cv[0].figure.get_figheight()
                if self.cf.print_hsqc_multiplet_aspect_ratio != 'auto':
                    if self.cf.print_hsqc_multiplet_aspect_ratio == 'a4_portrait':
                        fw = 8.27
                        fh = 11.69
                        cv[0].figure.set_figwidth(fw)
                        cv[0].figure.set_figheight(fh)
                    elif self.cf.print_hsqc_multiplet_aspect_ratio == 'a4_landscape':
                        fw = 11.69
                        fh = 8.27
                        cv[0].figure.set_figwidth(fw)
                        cv[0].figure.set_figheight(fh)
                    else:
                        cv[0].figure.set_figwidth(self.cf.print_hsqc_multiplet_aspect_ratio * cv[0].figure.get_figheight())

                cv[0].figure.savefig(file_name, transparent=not self.nd.cf.print_background)
                cv[0].figure.set_figwidth(figure_width)
                cv[0].figure.set_figheight(figure_height)
                file_name = f_name + '_peak.pdf'
                cv[1].figure.subplots_adjust(bottom=0.2, left=0.2)
                figure_width = cv[1].figure.get_figwidth()
                figure_height = cv[1].figure.get_figheight()
                if self.cf.print_hsqc_peak_aspect_ratio != 'auto':
                    if self.cf.print_hsqc_peak_aspect_ratio == 'a4_portrait':
                        fw = 8.27
                        fh = 11.69
                        cv[1].figure.set_figwidth(fw)
                        cv[1].figure.set_figheight(fh)
                    elif self.cf.print_hsqc_peak_aspect_ratio == 'a4_landscape':
                        fw = 11.69
                        fh = 8.27
                        cv[1].figure.set_figwidth(fw)
                        cv[1].figure.set_figheight(fh)
                    else:
                        cv[1].figure.set_figwidth(self.cf.print_hsqc_peak_aspect_ratio * cv[1].figure.get_figheight())

                cv[1].figure.savefig(file_name, transparent=not self.nd.cf.print_background)
                cv[1].figure.subplots_adjust(bottom=0.1, left=0.125)
                cv[1].figure.set_figwidth(figure_width)
                cv[1].figure.set_figheight(figure_height)

            self.cf.mode = prg_mode
            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                self.load_dark_mode()
            else:
                self.load_light_mode()

            #if self.nd.cf.print_standard_colours:
                #if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1:
            for k in range(len(self.nd.nmrdat)):
                for l in range(len(self.nd.nmrdat[k])):
                    self.nd.nmrdat[k][l].display.pos_col_rgb = orig_pos_col_rgb[k][l]
                    self.nd.nmrdat[k][l].display.pos_col = orig_pos_col[k][l]
                    self.nd.nmrdat[k][l].display.neg_col_rgb = orig_neg_col_rgb[k][l]
                    self.nd.nmrdat[k][l].display.neg_col = orig_neg_col[k][l]

            cv[0].axes.set_yticks(yticks)
            cv[0].axes.set_ylim(ylim)
            cv[0].axes.set_xticks(xticks)
            cv[0].axes.set_xlim(xlim)

            bg = self.nd.background_colour
            fg = self.nd.foreground_colour
            cv[0].figure.set_facecolor(bg)
            cv[0].axes.set_facecolor(bg)
            cv[0].axes.xaxis.label.set_color(fg)
            cv[0].axes.yaxis.label.set_color(fg)
            cv[0].axes.tick_params(axis='x', colors=fg)
            cv[0].axes.tick_params(axis='y', colors=fg)
            cv[0].axes.spines['bottom'].set_linewidth(ax_lw)
            cv[0].axes.spines['left'].set_linewidth(ax_lw)
            cv[0].axes.spines['right'].set_linewidth(ax_lw)
            cv[0].axes.spines['top'].set_linewidth(ax_lw)
            if len(cv) > 1:
                cv[1].figure.set_facecolor(bg)
                cv[1].axes.set_facecolor(bg)
                cv[1].axes.xaxis.label.set_color(fg)
                cv[1].axes.yaxis.label.set_color(fg)
                cv[1].axes.tick_params(axis='x', colors=fg)
                cv[1].axes.tick_params(axis='y', colors=fg)
                cv[1].axes.spines['bottom'].set_linewidth(ax_lw)
                cv[1].axes.spines['left'].set_linewidth(ax_lw)
                cv[1].axes.spines['right'].set_linewidth(ax_lw)
                cv[1].axes.spines['top'].set_linewidth(ax_lw)

            matplotlib.pyplot.rc('axes', labelsize=ax_ls)
            matplotlib.pyplot.rc('xtick', labelsize=ax_fs)
            matplotlib.pyplot.rc('ytick', labelsize=ax_fs)
            cv[0].axes.tick_params(width=ax_lw)
            cv[0].axes.spines['bottom'].set_visible(True)
            cv[0].axes.spines['top'].set_visible(True)
            cv[0].axes.spines['right'].set_visible(True)
            cv[0].axes.spines['left'].set_visible(True)
            if self.w.nmrSpectrum.currentIndex() == 0:
                self.plot_spc()
            else:
                self.plot_metabolite_peak(cur_peak)

            if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1 and self.cf.print_stacked_plot and len(disp_spc) > 1:
                writer = PdfWriter()
                pdf_file = []
                pdf_reader = []
                f1 = []
                file_name1 = []
                for k in range(len(disp_spc)):
                    file_name1.append(f_name + f'_{k}.pdf')
                    f1.append(open(file_name1[k], 'rb'))
                    pdf_file.append(f1[k])
                    pdf_reader.append(PdfReader(pdf_file[k]))

                n_files = len(pdf_file)
                width = pdf_reader[0].pages[0].mediabox.width
                height = pdf_reader[0].pages[0].mediabox.height
                merged_page = PageObject.create_blank_page(None, width, height * n_files)
                merged_page.merge_page(pdf_reader[n_files - 1].pages[0])
                op = Transformation().scale(sx=1, sy=1).translate(tx=0, ty=float(height))
                for k in range(n_files - 1):
                    merged_page.add_transformation(op)
                    merged_page.merge_page(pdf_reader[n_files - 2 - k].pages[0])

                writer.add_page(merged_page)
                file_name = f'{f_name}.pdf'
                with open(file_name, 'wb') as f:
                    writer.write(f)

                for k in range(len(f1)):
                    f1[k].close()
                    os.remove(file_name1[k])

        # end print_spc

    def pulprog(self):
        print(f'pulprog: {self.nd.nmrdat[self.nd.s][self.nd.e].acq.pul_prog_name}')

    def reshape_title(self, n_rows=2):
        return_text = self.nd.reshape_title(n_rows)
        if return_text != 'Succesfully reshaped title':
            self.show_console()
        else:
            self.update_gui()
            self.show_title_file_information()
        # end reshape_title

    def reshape_titles(self, n_rows=2):
        all_fine = self.nd.reshape_titles(n_rows)
        if all_fine:
            self.update_gui()
            self.show_title_file_information()
        else:
            self.update_gui()
            self.show_console()
        # end reshape_titles

    def set_ref(self, ref_value='auto'):
        self.nd.set_ref(ref_value)
        # end set_ref

    def set_ref_all(self, ref_value='auto'):
        self.nd.set_ref_all(ref_value)
        # end set_ref_all

    def sp(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.shaped_power) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'sp = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.shaped_power}')
        else:
            print("sp{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.shaped_power[index]))

        # end sp

    def spw(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.shaped_power_watt) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'spw = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.shaped_power_watt}')
        else:
            print("spw{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.shaped_power_watt[index]))

        # end spw

    def spoal(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.spoal) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'spoal = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.spoal}')
        else:
            print("spoal{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.spoal[index]))

        # end spoal

    def spoffs(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.spoffs) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'spoffs = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.spoffs}')
        else:
            print("spoffs{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.spoffs[index]))

        # end spoffs

    def cpdprg(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.cpd_prog) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'cpdprg = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.cpd_prog}')
        else:
            print("cpdprg{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.cpd_prog[index]))

        # end cpdprg

    def fitlw(self, ppm=0.0, message=True):
        self.show_console()
        self.update_gui()
        self.nd.fitlw(ppm = ppm, message = message)
        # end fit_tmsp()

    def fitlw_all(self, ppm=0.0, message=True):
        self.show_console()
        self.update_gui()
        self.nd.fitlw_all(ppm = ppm, message = message)
        # end fit_tmsp_all

    def gpnam(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.gp_name) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'gpnam = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.gp_name}')
        else:
            print("gpnam{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.gp_name[index]))

        # end gpnam

    def gpx(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.gpx) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'gpx = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.gpx}')
        else:
            print("gpx{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.gpx[index]))

        # end gpx

    def gpy(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.gpy) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'gpy = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.gpy}')
        else:
            print("gpy{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.gpy[index]))

        # end gpy

    def gpz(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.gpz) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'gpz = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.gpz}')
        else:
            print("gpz{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.gpz[index]))

        # end gpz

    def data_pre_processing(self):
        self.nd.reset_data_pre_processing()
        self.nd.data_pre_processing()
        self.plot_spc_pre_proc()
        self.vertical_auto_scale()
        self.w.MplWidget.canvas.flush_events()
        self.w.MplWidget.canvas.draw()
        # end data_pre_processing

    def display_assigned_metabolites(self):
        dsmwo = False
        if self.w.displaySelectedMetabolite.isChecked():
            self.w.displaySelectedMetabolite.setChecked(False)
            dsmwo = True

        if self.w.displayAssignedMetabolites.isChecked() == True:
            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                col1 = 'yellow'
                col2 = 'gray'
            else:
                col1 = 'k'
                col2 = 'r'

            deltax = 0.01
            delta_h1 = self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(
                len(self.nd.nmrdat[self.nd.s][self.nd.e].spc[0]) - 1, 0) - self.nd.nmrdat[self.nd.s][
                           self.nd.e].points2ppm(0, 0)
            delta_c13 = self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(
                len(self.nd.nmrdat[self.nd.s][self.nd.e].spc) - 1, 1) - self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(
                0, 1)
            deltay = deltax * delta_c13 * 2 / delta_h1
            for k in self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data.keys():
                display_metabolite = True
                if k == self.nd.nmrdat[self.nd.s][
                    self.nd.e].hsqc.cur_metabolite and self.w.displaySelectedMetabolite.isChecked() == True:
                    display_metabolite = False

                if display_metabolite:
                    for l in range(len(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].h1_picked)):
                        x = np.mean(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].h1_picked[l])
                        y = np.mean(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].c13_picked[l])
                        self.nd.nmrdat[self.nd.s][self.nd.e].xsa.append(
                            self.w.MplWidget.canvas.axes.plot([x - deltax, x + deltax], [y, y], color=col1,
                                                              linewidth=2))
                        self.nd.nmrdat[self.nd.s][self.nd.e].ysa.append(
                            self.w.MplWidget.canvas.axes.plot([x, x], [y - deltay, y + deltay], color=col1,
                                                              linewidth=2))
                        self.nd.nmrdat[self.nd.s][self.nd.e].assigned_text.append(
                            self.w.MplWidget.canvas.axes.text(x - 0.5 * deltax, y - 0.5 * deltay, k, color=col1,
                                                              fontweight='bold'))

            self.w.MplWidget.canvas.draw()

        else:
            for k in range(len(self.nd.nmrdat[self.nd.s][self.nd.e].xsa)):
                line1 = self.nd.nmrdat[self.nd.s][self.nd.e].xsa[k].pop(0)
                line2 = self.nd.nmrdat[self.nd.s][self.nd.e].ysa[k].pop(0)
                line1.remove()
                line2.remove()

            for k in range(len(self.nd.nmrdat[self.nd.s][self.nd.e].assigned_text)):
                self.nd.nmrdat[self.nd.s][self.nd.e].assigned_text[k].remove()

            self.nd.nmrdat[self.nd.s][self.nd.e].xsa = []
            self.nd.nmrdat[self.nd.s][self.nd.e].ysa = []
            self.nd.nmrdat[self.nd.s][self.nd.e].assigned_text = []
            self.w.MplWidget.canvas.draw()

        if dsmwo:
            self.w.displaySelectedMetabolite.setChecked(True)

        # end display_assigned_metabolites

    def display_library_shifts(self):
        dsmwo = False
        damwo = False
        if self.w.displaySelectedMetabolite.isChecked():
            dsmwo = True
            self.w.displaySelectedMetabolite.setChecked(False)

        if self.w.displayAssignedMetabolites.isChecked():
            damwo = True
            self.w.displayAssignedMetabolites.setChecked(False)

        if self.w.displayLibraryShifts.isChecked() == True:
            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                col1 = 'yellow'
                col2 = 'gray'
            else:
                col1 = 'k'
                col2 = 'gray'

            deltax = 0.01
            delta_h1 = self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(
                len(self.nd.nmrdat[self.nd.s][self.nd.e].spc[0]) - 1, 0) - self.nd.nmrdat[self.nd.s][
                           self.nd.e].points2ppm(0, 0)
            delta_c13 = self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(
                len(self.nd.nmrdat[self.nd.s][self.nd.e].spc) - 1, 1) - self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(
                0, 1)
            deltay = deltax * delta_c13 * 2 / delta_h1
            for k in self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.metabolite_list:
                if k in self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data.keys():
                    display_metabolite = True
                    if k == self.nd.nmrdat[self.nd.s][
                        self.nd.e].hsqc.cur_metabolite and self.w.displaySelectedMetabolite.isChecked() == True:
                        display_metabolite = False

                    for l in range(len(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].h1_picked)):
                        if len(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].h1_picked[
                                   l]) == 0 and display_metabolite:
                            x = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].h1_shifts[l]
                            y = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].c13_shifts[
                                self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].h1_index[l] - 1]
                            self.nd.nmrdat[self.nd.s][self.nd.e].xst.append(
                                self.w.MplWidget.canvas.axes.plot([x - deltax, x + deltax], [y, y], color=col2,
                                                                  linewidth=2))
                            self.nd.nmrdat[self.nd.s][self.nd.e].yst.append(
                                self.w.MplWidget.canvas.axes.plot([x, x], [y - deltay, y + deltay], color=col2,
                                                                  linewidth=2))
                            self.nd.nmrdat[self.nd.s][self.nd.e].library_text.append(
                                self.w.MplWidget.canvas.axes.text(x - 0.5 * deltax, y - 0.5 * deltay, k, color=col2,
                                                                  fontweight='bold'))

                else:
                    hsqc = nmrHsqc.NmrHsqc()
                    hsqc.read_metabolite_information(k)
                    hsqc.set_metabolite_information(k, hsqc.metabolite_information)
                    hsqc.hsqc_data[k].init_data(hsqc.metabolite_information)
                    print(f'{k} - h1_shifts: {hsqc.hsqc_data[k].h1_shifts}, h1_index: {hsqc.hsqc_data[k].h1_index}')
                    for l in range(len(hsqc.hsqc_data[k].h1_shifts)):
                        x = hsqc.hsqc_data[k].h1_shifts[l]
                        y = hsqc.hsqc_data[k].c13_shifts[hsqc.hsqc_data[k].h1_index[l] - 1]
                        self.nd.nmrdat[self.nd.s][self.nd.e].xst.append(
                            self.w.MplWidget.canvas.axes.plot([x - deltax, x + deltax], [y, y], color=col2,
                                                              linewidth=2))
                        self.nd.nmrdat[self.nd.s][self.nd.e].yst.append(
                            self.w.MplWidget.canvas.axes.plot([x, x], [y - deltay, y + deltay], color=col2,
                                                              linewidth=2))
                        self.nd.nmrdat[self.nd.s][self.nd.e].library_text.append(
                            self.w.MplWidget.canvas.axes.text(x - 0.5 * deltax, y - 0.5 * deltay, k, color=col2,
                                                              fontweight='bold'))

            self.w.MplWidget.canvas.draw()

        else:
            for k in range(len(self.nd.nmrdat[self.nd.s][self.nd.e].xst)):
                line1 = self.nd.nmrdat[self.nd.s][self.nd.e].xst[k].pop(0)
                line2 = self.nd.nmrdat[self.nd.s][self.nd.e].yst[k].pop(0)
                line1.remove()
                line2.remove()

            for k in range(len(self.nd.nmrdat[self.nd.s][self.nd.e].library_text)):
                self.nd.nmrdat[self.nd.s][self.nd.e].library_text[k].remove()

            self.nd.nmrdat[self.nd.s][self.nd.e].xst = []
            self.nd.nmrdat[self.nd.s][self.nd.e].yst = []
            self.nd.nmrdat[self.nd.s][self.nd.e].library_text = []
            self.w.MplWidget.canvas.draw()

        if damwo:
            self.w.displayAssignedMetabolites.setChecked(True)

        if dsmwo:
            self.w.displaySelectedMetabolite.setChecked(True)
        # end display_library_shifts

    def display_selected_metabolite(self):
        if self.w.displaySelectedMetabolite.isChecked() == True:
            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                col1 = 'lime'
                col2 = 'gray'
            else:
                col1 = 'limegreen'
                col2 = 'gray'

            deltax = 0.01
            delta_h1 = self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(
                len(self.nd.nmrdat[self.nd.s][self.nd.e].spc[0]) - 1, 0) - self.nd.nmrdat[self.nd.s][
                           self.nd.e].points2ppm(0, 0)
            delta_c13 = self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(
                len(self.nd.nmrdat[self.nd.s][self.nd.e].spc) - 1, 1) - self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(
                0, 1)
            deltay = deltax * delta_c13 * 2 / delta_h1
            # for k in self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.metabolite_list:
            k = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite
            if k in self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data.keys():
                hsqc = nmrHsqc.NmrHsqc()
                hsqc.read_metabolite_information(k)
                hsqc.set_metabolite_information(k, hsqc.metabolite_information)
                hsqc.hsqc_data[k].init_data(hsqc.metabolite_information)
                for l in range(len(hsqc.hsqc_data[k].h1_shifts)):
                    if len(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].h1_picked[l]) > 0:
                        # print("picked: {}".format(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].h1_picked[l]))
                        x = np.mean(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].h1_picked[l])
                        y = np.mean(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[k].c13_picked[l])
                        self.nd.nmrdat[self.nd.s][self.nd.e].xss.append(
                            self.w.MplWidget.canvas.axes.plot([x - deltax, x + deltax], [y, y], color=col1,
                                                              linewidth=2))
                        self.nd.nmrdat[self.nd.s][self.nd.e].yss.append(
                            self.w.MplWidget.canvas.axes.plot([x, x], [y - deltay, y + deltay], color=col1,
                                                              linewidth=2))
                        self.nd.nmrdat[self.nd.s][self.nd.e].metabolite_text.append(
                            self.w.MplWidget.canvas.axes.text(x - 0.5 * deltax, y - 0.5 * deltay, k, color=col1,
                                                              fontweight='bold'))
                    else:
                        x = hsqc.hsqc_data[k].h1_shifts[l]
                        y = hsqc.hsqc_data[k].c13_shifts[hsqc.hsqc_data[k].h1_index[l] - 1]
                        self.nd.nmrdat[self.nd.s][self.nd.e].xss.append(
                            self.w.MplWidget.canvas.axes.plot([x - deltax, x + deltax], [y, y], color=col1,
                                                              linewidth=2))
                        self.nd.nmrdat[self.nd.s][self.nd.e].yss.append(
                            self.w.MplWidget.canvas.axes.plot([x, x], [y - deltay, y + deltay], color=col1,
                                                              linewidth=2))
                        self.nd.nmrdat[self.nd.s][self.nd.e].metabolite_text.append(
                            self.w.MplWidget.canvas.axes.text(x - 0.5 * deltax, y - 0.5 * deltay, k, color=col1,
                                                              fontweight='bold'))

            self.w.MplWidget.canvas.draw()

        else:
            for k in range(len(self.nd.nmrdat[self.nd.s][self.nd.e].xss)):
                line1 = self.nd.nmrdat[self.nd.s][self.nd.e].xss[k].pop(0)
                line2 = self.nd.nmrdat[self.nd.s][self.nd.e].yss[k].pop(0)
                line1.remove()
                line2.remove()

            for k in range(len(self.nd.nmrdat[self.nd.s][self.nd.e].metabolite_text)):
                self.nd.nmrdat[self.nd.s][self.nd.e].metabolite_text[k].remove()

            self.nd.nmrdat[self.nd.s][self.nd.e].xss = []
            self.nd.nmrdat[self.nd.s][self.nd.e].yss = []
            self.nd.nmrdat[self.nd.s][self.nd.e].metabolite_text = []

        self.w.MplWidget.canvas.draw()
        # end display_selected_metabolite

    def display_metabolite_information(self):
        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        if self.w.hsqcAssignedMetabolites.currentIndex().row() < 0:
            print("No metabolite selected")
        else:
            metabolite_name = self.w.hsqcAssignedMetabolites.currentIndex().data()
            print(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].__str__())

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        self.w.console.setTextColor(err_col)
        self.w.console.append(code_err.getvalue())
        code_out.close()
        code_err.close()
        self.show_console()
        # end display_metabolite_information

    def delete_buttons(self, n_buttons=0):
        n_entries = len(self.w.peakSelection.children())
        for k in range(n_entries):
            if hasattr(self.w.peakSelection.children()[k], 'text'):
                if int(self.w.peakSelection.children()[k].text()) > n_buttons:
                    self.w.peakSelection.children()[k].deleteLater()

        # end delete_buttons

    def create_buttons(self, n_buttons=0):
        existing_buttons = len(self.w.peakSelection.children()) - 1

        if existing_buttons < 1:
            self.button1 = QPushButton("1", self.w.peakSelection)
            self.button1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button1.clicked.connect(lambda: self.plot_metabolite_peak(1))

        if n_buttons > 1 and existing_buttons < 2:
            self.button2 = QPushButton("2", self.w.peakSelection)
            self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button2.clicked.connect(lambda: self.plot_metabolite_peak(2))

        if n_buttons > 2 and existing_buttons < 3:
            self.button3 = QPushButton("3", self.w.peakSelection)
            self.button3.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button3.clicked.connect(lambda: self.plot_metabolite_peak(3))

        if n_buttons > 3 and existing_buttons < 4:
            self.button4 = QPushButton("4", self.w.peakSelection)
            self.button4.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button4.clicked.connect(lambda: self.plot_metabolite_peak(4))

        if n_buttons > 4 and existing_buttons < 5:
            self.button5 = QPushButton("5", self.w.peakSelection)
            self.button5.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button5.clicked.connect(lambda: self.plot_metabolite_peak(5))

        if n_buttons > 5 and existing_buttons < 6:
            self.button6 = QPushButton("6", self.w.peakSelection)
            self.button6.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button6.clicked.connect(lambda: self.plot_metabolite_peak(6))

        if n_buttons > 6 and existing_buttons < 7:
            self.button7 = QPushButton("7", self.w.peakSelection)
            self.button7.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button7.clicked.connect(lambda: self.plot_metabolite_peak(7))

        if n_buttons > 7 and existing_buttons < 8:
            self.button8 = QPushButton("8", self.w.peakSelection)
            self.button8.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button8.clicked.connect(lambda: self.plot_metabolite_peak(8))

        if n_buttons > 8 and existing_buttons < 9:
            self.button9 = QPushButton("9", self.w.peakSelection)
            self.button9.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button9.clicked.connect(lambda: self.plot_metabolite_peak(9))

        if n_buttons > 9 and existing_buttons < 10:
            self.button10 = QPushButton("10", self.w.peakSelection)
            self.button10.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button10.clicked.connect(lambda: self.plot_metabolite_peak(10))

        if n_buttons > 10 and existing_buttons < 11:
            self.button11 = QPushButton("11", self.w.peakSelection)
            self.button11.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button11.clicked.connect(lambda: self.plot_metabolite_peak(11))

        if n_buttons > 11 and existing_buttons < 12:
            self.button12 = QPushButton("12", self.w.peakSelection)
            self.button12.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button12.clicked.connect(lambda: self.plot_metabolite_peak(12))

        if n_buttons > 12 and existing_buttons < 13:
            self.button13 = QPushButton("13", self.w.peakSelection)
            self.button13.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button13.clicked.connect(lambda: self.plot_metabolite_peak(13))

        if n_buttons > 13 and existing_buttons < 14:
            self.button14 = QPushButton("14", self.w.peakSelection)
            self.button14.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button14.clicked.connect(lambda: self.plot_metabolite_peak(14))

        if n_buttons > 14 and existing_buttons < 15:
            self.button15 = QPushButton("15", self.w.peakSelection)
            self.button15.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button15.clicked.connect(lambda: self.plot_metabolite_peak(15))

        if n_buttons > 15 and existing_buttons < 16:
            self.button16 = QPushButton("16", self.w.peakSelection)
            self.button16.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button16.clicked.connect(lambda: self.plot_metabolite_peak(16))

        if n_buttons > 16 and existing_buttons < 17:
            self.button17 = QPushButton("17", self.w.peakSelection)
            self.button17.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button17.clicked.connect(lambda: self.plot_metabolite_peak(17))

        if n_buttons > 17 and existing_buttons < 18:
            self.button18 = QPushButton("18", self.w.peakSelection)
            self.button18.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button18.clicked.connect(lambda: self.plot_metabolite_peak(18))

        if n_buttons > 18 and existing_buttons < 19:
            self.button19 = QPushButton("19", self.w.peakSelection)
            self.button19.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button19.clicked.connect(lambda: self.plot_metabolite_peak(19))

        if n_buttons > 19 and existing_buttons < 20:
            self.button20 = QPushButton("20", self.w.peakSelection)
            self.button20.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button20.clicked.connect(lambda: self.plot_metabolite_peak(20))

        if n_buttons > 20 and existing_buttons < 21:
            self.button21 = QPushButton("21", self.w.peakSelection)
            self.button21.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button21.clicked.connect(lambda: self.plot_metabolite_peak(21))

        if n_buttons > 21 and existing_buttons < 22:
            self.button22 = QPushButton("22", self.w.peakSelection)
            self.button22.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button22.clicked.connect(lambda: self.plot_metabolite_peak(22))

        if n_buttons > 22 and existing_buttons < 23:
            self.button23 = QPushButton("23", self.w.peakSelection)
            self.button23.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button23.clicked.connect(lambda: self.plot_metabolite_peak(23))

        if n_buttons > 23 and existing_buttons < 24:
            self.button24 = QPushButton("24", self.w.peakSelection)
            self.button24.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button24.clicked.connect(lambda: self.plot_metabolite_peak(24))

        if n_buttons > 24 and existing_buttons < 25:
            self.button25 = QPushButton("25", self.w.peakSelection)
            self.button25.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button25.clicked.connect(lambda: self.plot_metabolite_peak(25))

        if n_buttons > 25 and existing_buttons < 26:
            self.button26 = QPushButton("26", self.w.peakSelection)
            self.button26.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button26.clicked.connect(lambda: self.plot_metabolite_peak(26))

        if n_buttons > 26 and existing_buttons < 27:
            self.button27 = QPushButton("27", self.w.peakSelection)
            self.button27.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button27.clicked.connect(lambda: self.plot_metabolite_peak(27))

        if n_buttons > 27 and existing_buttons < 28:
            self.button28 = QPushButton("28", self.w.peakSelection)
            self.button28.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button28.clicked.connect(lambda: self.plot_metabolite_peak(28))

        if n_buttons > 28 and existing_buttons < 29:
            self.button29 = QPushButton("29", self.w.peakSelection)
            self.button29.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button29.clicked.connect(lambda: self.plot_metabolite_peak(29))

        if n_buttons > 29 and existing_buttons < 30:
            self.button30 = QPushButton("30", self.w.peakSelection)
            self.button30.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button30.clicked.connect(lambda: self.plot_metabolite_peak(30))

        if n_buttons > 30 and existing_buttons < 31:
            self.button31 = QPushButton("31", self.w.peakSelection)
            self.button31.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button31.clicked.connect(lambda: self.plot_metabolite_peak(31))

        if n_buttons > 31 and existing_buttons < 32:
            self.button32 = QPushButton("32", self.w.peakSelection)
            self.button32.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button32.clicked.connect(lambda: self.plot_metabolite_peak(32))

        if n_buttons > 32 and existing_buttons < 33:
            self.button33 = QPushButton("33", self.w.peakSelection)
            self.button33.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button33.clicked.connect(lambda: self.plot_metabolite_peak(33))

        if n_buttons > 33 and existing_buttons < 34:
            self.button34 = QPushButton("34", self.w.peakSelection)
            self.button34.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button34.clicked.connect(lambda: self.plot_metabolite_peak(34))

        if n_buttons > 34 and existing_buttons < 35:
            self.button35 = QPushButton("35", self.w.peakSelection)
            self.button35.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button35.clicked.connect(lambda: self.plot_metabolite_peak(35))

        if n_buttons > 35 and existing_buttons < 36:
            self.button36 = QPushButton("36", self.w.peakSelection)
            self.button36.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button36.clicked.connect(lambda: self.plot_metabolite_peak(36))

        if n_buttons > 36 and existing_buttons < 37:
            self.button37 = QPushButton("37", self.w.peakSelection)
            self.button37.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button37.clicked.connect(lambda: self.plot_metabolite_peak(37))

        if n_buttons > 37 and existing_buttons < 38:
            self.button38 = QPushButton("38", self.w.peakSelection)
            self.button38.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button38.clicked.connect(lambda: self.plot_metabolite_peak(38))

        if n_buttons > 38 and existing_buttons < 39:
            self.button39 = QPushButton("39", self.w.peakSelection)
            self.button39.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button39.clicked.connect(lambda: self.plot_metabolite_peak(39))

        if n_buttons > 39 and existing_buttons < 40:
            self.button40 = QPushButton("40", self.w.peakSelection)
            self.button40.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button40.clicked.connect(lambda: self.plot_metabolite_peak(40))

        if n_buttons > 40 and existing_buttons < 41:
            self.button41 = QPushButton("41", self.w.peakSelection)
            self.button41.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button41.clicked.connect(lambda: self.plot_metabolite_peak(41))

        if n_buttons > 41 and existing_buttons < 42:
            self.button42 = QPushButton("42", self.w.peakSelection)
            self.button42.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button42.clicked.connect(lambda: self.plot_metabolite_peak(42))

        if n_buttons > 42 and existing_buttons < 43:
            self.button43 = QPushButton("43", self.w.peakSelection)
            self.button43.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button43.clicked.connect(lambda: self.plot_metabolite_peak(43))

        if n_buttons > 43 and existing_buttons < 44:
            self.button44 = QPushButton("44", self.w.peakSelection)
            self.button44.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button44.clicked.connect(lambda: self.plot_metabolite_peak(44))

        if n_buttons > 44 and existing_buttons < 45:
            self.button45 = QPushButton("45", self.w.peakSelection)
            self.button45.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button45.clicked.connect(lambda: self.plot_metabolite_peak(45))

        if n_buttons > 45 and existing_buttons < 46:
            self.button46 = QPushButton("46", self.w.peakSelection)
            self.button46.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button46.clicked.connect(lambda: self.plot_metabolite_peak(46))

        if n_buttons > 46 and existing_buttons < 47:
            self.button47 = QPushButton("47", self.w.peakSelection)
            self.button47.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button47.clicked.connect(lambda: self.plot_metabolite_peak(47))

        if n_buttons > 47 and existing_buttons < 48:
            self.button48 = QPushButton("48", self.w.peakSelection)
            self.button48.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button48.clicked.connect(lambda: self.plot_metabolite_peak(48))

        if n_buttons > 48 and existing_buttons < 49:
            self.button49 = QPushButton("49", self.w.peakSelection)
            self.button49.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            self.button49.clicked.connect(lambda: self.plot_metabolite_peak(49))
        # end create_buttons

    def make_buttons(self, n_buttons=0):
        if n_buttons == 0:
            return

        existing_buttons = len(self.w.peakSelection.children()) - 1
        self.delete_buttons(n_buttons)
        self.create_buttons(n_buttons)
        while self.layout.itemAt(0) != None:
            self.layout.removeItem(self.layout.itemAt(0))

        n_rows = round(math.sqrt(n_buttons))
        n_cols = math.ceil(n_buttons / n_rows)
        for k in range(n_buttons):
            col = k % n_cols
            row = math.floor((k + 0.1) / n_cols)
            # print("n_rows: {}, n_cols: {}, row: {}, col: {}".format(n_rows, n_cols, row, col))
            exec("self.layout.addWidget(self.button" + str(k + 1) + ", " + str(row) + " , " + str(col) + ")")

    # end make_buttons

    def empty_col_row(self):
        while len(self.w.MplWidget.canvas.axes.lines) > 0:
            self.w.MplWidget.canvas.axes.lines[0].remove()

        self.w.MplWidget.canvas.draw()
        self.ph_corr.spc_row = []
        self.ph_corr.spc_col = []
        self.ph_corr.spc_row_pts = []
        self.ph_corr.spc_col_pts = []
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end empty_col_row

    def enable_baseline(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].apc.correct_baseline = 1

        self.w.baselineOrder.setCurrentIndex(self.nd.nmrdat[self.nd.s][0].apc.n_order)
        self.w.baselineCorrection.setCurrentIndex(1)
        return "baselineCorrection enabled"
        # end enableBaseline

    def exec_cmd(self):
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        cmd_text = self.w.cmdLine.text()
        if (len(cmd_text) > 0):
            self.w.nmrSpectrum.setCurrentIndex(10)
            self.w.cmdLine.setText("")
            self.nd.cmd_buffer = np.append(self.nd.cmd_buffer, cmd_text)
            self.nd.cmd_idx = len(self.nd.cmd_buffer)
            code_out = io.StringIO()
            code_err = io.StringIO()
            sys.stdout = code_out
            sys.stderr = code_err
            print(">>> " + cmd_text)
            try:
                output = eval(cmd_text)
                if code_out.getvalue().find('clear_console()') < 0:
                    print(output)
                    self.w.console.setTextColor(txt_col)
                    self.w.console.append(code_out.getvalue())
                    
            except:  # (SyntaxError, NameError, TypeError, ZeroDivisionError, AttributeError, ArithmeticError, BufferError, LookupError):
                cmd_text2 = "self." + cmd_text
                try:
                    output = eval(cmd_text2)
                    if code_out.getvalue().find('clear_console()') < 0:
                        if cmd_text2.find('self.nd') > -1:
                            print(output)

                        self.w.console.setTextColor(txt_col)
                        self.w.console.append(code_out.getvalue())
                except:
                    traceback.print_exc()
                    self.w.console.setTextColor(err_col)
                    self.w.console.append(code_out.getvalue())
                    self.w.console.append(code_err.getvalue())

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            code_out.close()
            code_err.close()
            self.w.console.verticalScrollBar().setValue(self.w.console.verticalScrollBar().maximum())

        # end execCmd

    def exec_script(self):
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
            scr_col = QColor.fromRgbF(0.5, 0.5, 1.0, 1.0)
            scr_col2 = QColor.fromRgbF(0.4, 0.4, 1.0, 1.0)
            adm_col = QColor.fromRgbF(1.0, 1.0, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)
            scr_col = QColor.fromRgbF(0.0, 0.0, 1.0, 1.0)
            scr_col2 = QColor.fromRgbF(0.0, 0.0, 0.6, 1.0)
            adm_col = QColor.fromRgbF(0.4, 0.4, 0.4, 1.0)

        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        code = self.w.script.toPlainText()
        code = code.replace('\\', '\\' * 2)
        code = self.w.script.toPlainText()
        code = code.replace(' interactive ', ' abcint2 ')
        while code.find('''interactive''') > -1:
            data_path = QFileDialog.getExistingDirectory()
            if len(data_path) == 0:
                return

            code = code.replace('''interactive''', data_path, 1)

        code = code.replace(' abcint2 ', ' interactive ')
        self.w.script.setText(code)
        try:
            exec(code)

        except:  # (SyntaxError, NameError, TypeError, ZeroDivisionError, AttributeError):
            self.w.nmrSpectrum.setCurrentIndex(10)
            traceback.print_exc()

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.w.console.setTextColor(adm_col)
        self.w.console.append('--- Script_start -------------------------\n')
        self.w.console.setTextColor(scr_col2)
        self.w.console.append('Executing script...\n')
        self.w.console.setTextColor(scr_col)
        codeSplit = code.split('\n')
        for k in range(len(codeSplit)):
            self.w.console.append(str(k + 1) + ': ' + str(codeSplit[k]))

        self.w.console.setTextColor(adm_col)
        self.w.console.append('\n--- ScriptOutput ------------------------\n')
        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        self.w.console.setTextColor(err_col)
        self.w.console.append(code_err.getvalue())
        self.w.console.setTextColor(adm_col)
        self.w.console.append('--- Script_end ---------------------------\n')
        self.w.console.setTextColor(txt_col)
        code_out.close()
        code_err.close()
        if (len(self.nd.nmrdat[0]) > 0):
            self.update_gui()

        self.w.setBox.valueChanged.disconnect()
        self.w.expBox.valueChanged.disconnect()
        self.w.expBox.setValue(self.nd.e + 1)
        self.w.setBox.setValue(self.nd.s + 1)
        self.w.setBox.valueChanged.connect(lambda: self.change_data_set_exp())
        self.w.expBox.valueChanged.connect(lambda: self.change_data_set_exp())
        self.set_autobaseline()
        # end exec_script

    def export_peak(self):
        hsqcAnalysis = False
        peak_height = self.w.peakHeight.isChecked()
        if self.w.hsqcAnalysis.isChecked() == True:
            self.w.hsqcAnalysis.setChecked(False)

        f_name = QFileDialog.getSaveFileName(None, "Save Excel file", "", "*.xlsx", "*.xlsx")
        f_name = f_name[0]
        if len(f_name) == 0:
            return

        workbook = xlsxwriter.Workbook(f_name)
        if self.nd.int_all_data_sets == True:
            ds = range(len(self.nd.nmrdat))
        else:
            ds = [self.nd.s]

        for k in range(len(ds)):
            worksheet = workbook.add_worksheet('Dataset ' + str(ds[k] + 1))
            worksheet.set_column(1, 4, 15)
            worksheet.set_column(5, 255, 30)
            worksheet.set_row(2, 30)
            # worksheet.set_default_row(64)
            # my_format = workbook.add_format()
            # my_format.set_align('vtop')
            # my_format.set_align('hleft')
            # worksheet.set_column('A:XFD', None, my_format)
            if self.nd.int_all_exps == True:
                exps = range(len(self.nd.nmrdat[ds[k]]))
            else:
                exps = [self.nd.e]

            abc_string = []
            for s in itertools.islice(self.iter_all_strings(), 5 + len(exps)):
                abc_string.append(s)

            worksheet.write('B1', 'peak_label')
            worksheet.write('C1', 'peak_max_ppm')
            worksheet.write('D1', 'start_peakPPM')
            worksheet.write('E1', 'stopPeakPPM')
            worksheet.write('A2', 'Sample #')
            worksheet.write('A3', 'Sample ID')
            tmsp_idx = -1
            if not peak_height:
                if self.nd.quantify:
                    for idx in range(len(self.nd.nmrdat[ds[k]][self.nd.e].peak_label)):
                        if self.nd.nmrdat[ds[k]][self.nd.e].peak_label[idx].upper() == self.nd.internal_std.upper():
                            tmsp_idx = idx

                    if tmsp_idx == -1:
                        self.nd.quantify = False

            for m in range(len(exps)):
                if peak_height:
                    worksheet.write(abc_string[m + 5] + '1', 'peak_height(exp ' + str(exps[m] + 1) + ')')
                else:
                    worksheet.write(abc_string[m + 5] + '1', 'peak_int(exp ' + str(exps[m] + 1) + ')')

                worksheet.write(abc_string[m + 5] + '2', str(exps[m] + 1))
                worksheet.write(abc_string[m + 5] + '3', self.nd.nmrdat[ds[k]][exps[m]].title)

            for l in range(len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak)):
                worksheet.write('B' + str(l + 4), self.nd.nmrdat[self.nd.s][self.nd.e].peak_label[l])
                worksheet.write('C' + str(l + 4), self.nd.nmrdat[self.nd.s][self.nd.e].peak_max_ppm[l])
                worksheet.write('D' + str(l + 4), self.nd.nmrdat[self.nd.s][self.nd.e].start_peak[l])
                worksheet.write('E' + str(l + 4), self.nd.nmrdat[self.nd.s][self.nd.e].end_peak[l])
                for m in range(len(exps)):
                    if peak_height:
                        worksheet.write(abc_string[m + 5] + str(l + 4), self.nd.nmrdat[ds[k]][exps[m]].peak_max[l])
                    else:
                        worksheet.write(abc_string[m + 5] + str(l + 4), self.nd.nmrdat[ds[k]][exps[m]].peak_int[l])

            if not peak_height:
                if self.nd.quantify:
                    worksheet.write('A' + str(4 + tmsp_idx), 'Reference compound')
                    worksheet.write('B' + str(len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak) + 4), self.nd.internal_std + ' conc [mM]')
                    worksheet.write('C' + str(len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak) + 4), self.w.tmspConc.text())
                    for m in range(len(exps)):
                        worksheet.write(abc_string[m + 5] + str(len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak) + 5), 'conc. [mM]')
                    for l in range(len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak)):
                        worksheet.write('C' + str(len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak) + 6 + l), 'nProt')
                        worksheet.write('D' + str(len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak) + 6 + l), self.nd.nmrdat[ds[k]][self.nd.e].n_protons[l])
                        worksheet.write('E' + str(len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak) + 6 + l), self.nd.nmrdat[ds[k]][self.nd.e].peak_label[l])
                        for m in range(len(exps)):
                            worksheet.write(abc_string[m + 5] + str(len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak) + 6 + l),
                                            f'=C{len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak) + 4}'
                                            f'*D{len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak) + 6 + tmsp_idx}'
                                            f'*{abc_string[m + 5]}{l + 4}'
                                            f'/(D{len(self.nd.nmrdat[self.nd.s][self.nd.e].start_peak) + 6 + l}'
                                            f'*{abc_string[m + 5]}{tmsp_idx + 4})')

        workbook.close()
        # end export_peak

    def fill_peak_numbers(self):
        self.w.internalStandard.setText(self.nd.internal_std)
        self.nd.peak_fill = True
        s = self.nd.s
        e = self.nd.e
        n_peaks = len(self.nd.nmrdat[s][e].start_peak)
        start_peak = self.nd.nmrdat[s][e].start_peak
        end_peak = self.nd.nmrdat[s][e].end_peak
        peak_label = self.nd.nmrdat[s][e].peak_label
        n_protons = self.nd.nmrdat[s][e].n_protons
        self.w.peakWidget.setRowCount(n_peaks)
        for k in range(n_peaks):
            # peakNumber = QTableWidgetItem(str(k))
            # peakNumber.setTextAlignment(QtCore.Qt.AlignHCenter)
            # self.w.peakWidget.setItem(k, 0, peakNumber)
            # print('start: {}. end: {}, label: {}'.format(start_peak[k], end_peak[k], peak_label[k]))
            start_peak_tw = QTableWidgetItem(str(start_peak[k]))
            end_peak_tw = QTableWidgetItem(str(end_peak[k]))
            peak_label_tw = QTableWidgetItem(str(peak_label[k]))
            n_protons_tw =  QTableWidgetItem(str(n_protons[k]))
            start_peak_tw.setTextAlignment(QtCore.Qt.AlignHCenter)
            end_peak_tw.setTextAlignment(QtCore.Qt.AlignHCenter)
            peak_label_tw.setTextAlignment(QtCore.Qt.AlignHCenter)
            n_protons_tw.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.w.peakWidget.setItem(k, 0, start_peak_tw)
            self.w.peakWidget.setItem(k, 1, end_peak_tw)
            self.w.peakWidget.setItem(k, 2, peak_label_tw)
            self.w.peakWidget.setItem(k, 3, n_protons_tw)

        self.nd.peak_fill = False
        # end fill_peak_numbers

    def fill_pre_processing_numbers(self):
        self.nd.pp.pre_proc_fill = True
        n_spc = len(self.nd.pp.class_select)
        self.w.selectClassTW.setRowCount(n_spc)
        for k in range(n_spc):
            spc_number = QTableWidgetItem(str(k))
            spc_number.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.w.selectClassTW.setItem(k, 0, spc_number)
            # self.w.selectClassTW.setItemSelected(spc_number, False)
            class_number = QTableWidgetItem(self.nd.pp.class_select[k])
            class_number.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.w.selectClassTW.setItem(k, 1, class_number)

        self.w.selectClassTW.selectAll()
        sel_it = self.w.selectClassTW.selectedItems()
        for k in np.arange(len(sel_it) - 1, -1, -1):
            if self.w.selectClassTW.selectedItems()[k].column() == 1:
                self.w.selectClassTW.selectedItems()[k].setSelected(False)

        sel_it = self.w.selectClassTW.selectedItems()
        for k in np.arange(len(sel_it) - 1, -1, -1):
            if (np.isin(self.w.selectClassTW.selectedItems()[k].row(), self.nd.pp.plot_select)):
                self.w.selectClassTW.selectedItems()[k].setSelected(True)
            else:
                self.w.selectClassTW.selectedItems()[k].setSelected(False)

        for k in range(len(self.nd.pp.exclude_start)):
            excl_number1 = QTableWidgetItem(str(2 * k))
            excl_number1.setTextAlignment(QtCore.Qt.AlignHCenter)
            excl_number2 = QTableWidgetItem(str(2 * k + 1))
            excl_number2.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.w.excludeRegionTW.setItem(k, 0, excl_number1)
            self.w.excludeRegionTW.setItem(k, 1, excl_number2)
            self.w.excludeRegionTW.item(k, 0).setText(str(self.nd.pp.exclude_start[k]))
            self.w.excludeRegionTW.item(k, 1).setText(str(self.nd.pp.exclude_end[k]))

        for k in range(len(self.nd.pp.seg_start)):
            seg_number1 = QTableWidgetItem(str(2 * k))
            seg_number1.setTextAlignment(QtCore.Qt.AlignHCenter)
            seg_number2 = QTableWidgetItem(str(2 * k + 1))
            seg_number2.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.w.segAlignTW.setItem(k, 0, seg_number1)
            self.w.segAlignTW.setItem(k, 1, seg_number2)
            self.w.segAlignTW.item(k, 0).setText(str(self.nd.pp.seg_start[k]))
            self.w.segAlignTW.item(k, 1).setText(str(self.nd.pp.seg_end[k]))

        for k in range(len(self.nd.pp.compress_start)):
            comp_number1 = QTableWidgetItem(str(2 * k))
            comp_number1.setTextAlignment(QtCore.Qt.AlignHCenter)
            comp_number2 = QTableWidgetItem(str(2 * k + 1))
            comp_number2.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.w.compressBucketsTW.setItem(k, 0, comp_number1)
            self.w.compressBucketsTW.setItem(k, 1, comp_number2)
            self.w.compressBucketsTW.item(k, 0).setText(str(self.nd.pp.compress_start[k]))
            self.w.compressBucketsTW.item(k, 1).setText(str(self.nd.pp.compress_end[k]))

        self.w.noiseThresholdLE.setText(str(self.nd.pp.noise_threshold))
        self.w.noiseRegionStartLE.setText(str(self.nd.pp.noise_start))
        self.w.noiseRegionEndLE.setText(str(self.nd.pp.noise_end))
        self.w.thLineWidthLE.setText(str(self.nd.pp.th_line_width))
        self.w.bucketPpmLE.setText(str(self.nd.pp.bucket_ppm))
        self.set_bucket_ppm_pre_proc()
        self.w.excludeRegion.setChecked(self.nd.pp.flag_exclude_region)
        self.w.segmentalAlignment.setChecked(self.nd.pp.flag_segmental_alignment)
        self.w.noiseFiltering.setChecked(self.nd.pp.flag_noise_filtering)
        self.w.bucketSpectra.setChecked(self.nd.pp.flag_bucket_spectra)
        self.w.compressBuckets.setChecked(self.nd.pp.flag_compress_buckets)
        self.w.scaleSpectra.setChecked(self.nd.pp.flag_scale_spectra)
        if self.nd.pp.scale_pqn is True:
            self.w.pqnButton.setChecked(True)
        else:
            self.w.tsaButton.setChecked(True)

        self.w.varianceStabilisation.setChecked(self.nd.pp.flag_variance_stabilisation)
        self.w.exportDataSet.setChecked(self.nd.pp.flag_export_data_set)
        self.w.exportDelimiterTab.setChecked(self.nd.pp.export_delimiter_tab)
        self.w.exportDelimiterCharacter.setChecked(not self.nd.pp.export_delimiter_tab)
        self.w.exportCharacter.setText(self.nd.pp.export_character)
        self.w.exportMethod.setCurrentIndex(self.nd.pp.export_method)
        self.w.samplesInComboBox.setCurrentIndex(self.nd.pp.export_samples_in_rows_cols)
        self.w.segAlignRefSpc.setMaximum(len(self.nd.nmrdat[self.nd.s]))
        self.w.scaleSpectraRefSpc.setMaximum(len(self.nd.nmrdat[self.nd.s]))
        self.w.segAlignRefSpc.setValue(self.nd.pp.seg_align_ref_spc)
        self.w.scaleSpectraRefSpc.setValue(self.nd.pp.scale_spectra_ref_spc)
        self.w.preserveOverallScale.setChecked(self.nd.pp.preserve_overall_scale)
        self.w.preserveOverallScale.setDisabled(self.nd.pp.scale_pqn)
        self.w.autoScaling.setChecked(self.nd.pp.auto_scaling)
        self.w.paretoScaling.setChecked(self.nd.pp.pareto_scaling)
        self.w.gLogTransform.setChecked(self.nd.pp.g_log_transform)
        self.w.lambdaText.setEnabled(self.nd.pp.g_log_transform)
        self.w.y0Text.setEnabled(self.nd.pp.g_log_transform)
        self.w.lambdaLE.setEnabled(self.nd.pp.g_log_transform)
        self.w.y0LE.setEnabled(self.nd.pp.g_log_transform)
        self.w.lambdaLE.setText(str(self.nd.pp.var_lambda))
        self.w.y0LE.setText(str(self.nd.pp.var_y0))
        self.nd.pp.pre_proc_fill = False
        # end fill_pre_processing_numbers

    def ft(self):
        if self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline == True:
            alg = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_alg
            lam = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_lam
            max_iter = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_max_iter
            alpha = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_alpha
            beta = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_beta
            gamma = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_gamma
            beta_mult = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_beta_mult
            gamma_mult = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_gamma_mult
            half_window = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_half_window
            quantile = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_quantile
            poly_order = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_poly_order
            smooth_half_window = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_smooth_half_window
            add_ext = self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_add_ext

        self.nd.ft()
        if self.w.baselineCorrection.currentIndex() > 0 and self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1:
            self.baseline1d()

        #if self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline == True:
        #    self.autobaseline1d(alg=alg, lam=lam, max_iter=max_iter, alpha=alpha, beta=beta, gamma=gamma,
        #                        beta_mult=beta_mult, gamma_mult=gamma_mult, half_window=half_window, quantile=quantile,
        #                        poly_order=poly_order, smooth_half_window=smooth_half_window, add_ext=add_ext)


        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc()
        # end ft

    def ft_all(self):
        self.nd.ft_all()
        if (self.w.baselineCorrection.currentIndex() > 0):
            self.baseline1d_all()

        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc()
        # end ft_all

    def get_disp_pars1(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        d.pos_col = d.colours.get(self.w.posCol.currentIndex())
        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars1

    def get_disp_pars2(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        d.neg_col = d.colours.get(self.w.negCol.currentIndex())
        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars2

    def get_disp_pars3(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        try:
            pos_r = float(self.w.posColR.text())
        except:
            pass

        try:
            pos_g = float(self.w.posColG.text())
        except:
            pass

        try:
            pos_b = float(self.w.posColB.text())
        except:
            pass

        try:
            neg_r = float(self.w.negColR.text())
        except:
            pass

        try:
            neg_g = float(self.w.negColG.text())
        except:
            pass

        try:
            neg_b = float(self.w.negColB.text())
        except:
            pass

        try:
            d.pos_col_rgb = (pos_r, pos_g, pos_b)
        except:
            pass

        try:
            d.neg_col_rgb = (neg_r, neg_g, neg_b)
        except:
            pass

        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars3

    def get_disp_pars4(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        if len(self.w.nLevels.text()) > 0:
            d.n_levels = round(float(self.w.nLevels.text()))
        # end get_disp_pars4

        self.nd.nmrdat[self.nd.s][self.nd.e].display = d

    def get_disp_pars5(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        if len(self.w.minLevel.text()) > 0:
            d.min_level = float(self.w.minLevel.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars5

    def get_disp_pars6(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        if len(self.w.maxLevel.text()) > 0:
            d.max_level = float(self.w.maxLevel.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars6

    def get_disp_pars7(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        d.axis_type1 = d.axes.get(self.w.axisType1.currentIndex())
        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        self.nd.nmrdat[self.nd.s][self.nd.e].calc_ppm()
        # end get_disp_pars7

    def get_disp_pars8(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        d.axis_type2 = d.axes.get(self.w.axisType2.currentIndex())
        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        self.nd.nmrdat[self.nd.s][self.nd.e].calc_ppm()
        # end get_disp_pars8

    def get_disp_pars9(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        d.display_spc = d.false_true.get(self.w.displaySpc.currentIndex())
        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars9

    def get_disp_pars10(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        if len(self.w.spcOffset.text()) > 0:
            d.spc_offset = float(self.w.spcOffset.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars10

    def get_disp_pars11(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        if len(self.w.spcScale.text()) > 0:
            d.spc_scale = float(self.w.spcScale.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars11

    def get_disp_pars12(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        d.x_label = self.w.xLabel.text()
        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars12

    def get_disp_pars13(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        d.y_label = self.w.yLabel.text()
        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars13

    def get_disp_pars14(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        d.spc_label = self.w.spcLabel.text()
        self.nd.nmrdat[self.nd.s][self.nd.e].display = d
        # end get_disp_pars14

    def get_disp_pars15(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        d.ph_ref_col = d.colours2.get(self.w.phRefColour.currentIndex())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].display.ph_ref_col = d.ph_ref_col

        # end get_disp_pars15

    def get_hsqc_pars1(self):
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        h.range_h = float(self.w.h1Range.text())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.range_h = h.range_h

        # end get_hsqc_pars1

    def get_hsqc_pars2(self):
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        h.range_c = float(self.w.c13Range.text())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.range_c = h.range_c

        # end get_hsqc_pars2

    def get_hsqc_pars3(self):
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        h.threshold = float(self.w.threshold.text())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.threshold = h.threshold

        # end get_hsqc_pars3

    def get_hsqc_pars4(self):
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        h.j_cc = float(self.w.jCC.text())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.j_cc = h.j_cc

        # end get_hsqc_pars4

    def get_hsqc_pars5(self):
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        h.j_ch = float(self.w.jCH.text())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.j_ch = h.j_ch

        # end get_hsqc_pars5

    def get_hsqc_pars6(self):
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        h.n_max = int(self.w.nMax.text())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.n_max = h.n_max

        # end get_hsqc_pars6

    def get_hsqc_pars7(self):
        tf = [True, False]
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        tf2 = self.w.useSplittingCB.currentIndex()
        h.use_splitting = tf[tf2]
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.use_splitting = h.use_splitting

        # end get_hsqc_pars7

    def get_hsqc_pars8(self):
        tf = [True, False]
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        tf2 = self.w.tiltHsqcCB.currentIndex()
        h.tilt_hsqc = tf[tf2]
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.tilt_hsqc = h.tilt_hsqc

        # end get_hsqc_pars8

    def get_hsqc_pars9(self):
        tf = [True, False]
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        tf2 = self.w.displayLibraryCB.currentIndex()
        h.display_library_shift = tf[tf2]
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.display_library_shift = h.display_library_shift

        # end get_hsqc_pars9

    def get_hsqc_pars10(self):
        tf = [True, False]
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        tf2 = self.w.displayPickedCB.currentIndex()
        h.display_peaks_of_metabolite = tf[tf2]
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.display_peaks_of_metabolite = h.display_peaks_of_metabolite

        # end get_hsqc_pars10

    def get_hsqc_pars11(self):
        tf = [True, False]
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        tf2 = self.w.highlightDoubleCB.currentIndex()
        h.highlight_double_assignments = tf[tf2]
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.highlight_double_assignments = h.highlight_double_assignments

        # end get_hsqc_pars11

    def get_hsqc_pars12(self):
        tf = [True, False]
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        tf2 = self.w.displayOverlayShiftsCB.currentIndex()
        h.display_overlay_shifts = tf[tf2]
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.display_overlay_shifts = h.display_overlay_shifts

        # end get_hsqc_pars12

    def get_hsqc_pars13(self):
        tf = [True, False]
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        tf2 = self.w.coHsqcCB.currentIndex()
        h.co_hsqc = tf[tf2]
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.co_hsqc = h.co_hsqc

        # end get_hsqc_pars13

    def get_hsqc_pars14(self):
        tf = [True, False]
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        tf2 = self.w.pickLocalOptCB.currentIndex()
        h.pick_local_opt = tf[tf2]
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.pick_local_opt = h.pick_local_opt

        # end get_hsqc_pars14

    def get_hsqc_pars15(self):
        tf = [True, False]
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        tf2 = self.w.autoscaleCB.currentIndex()
        h.autoscale_j = tf[tf2]
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.autoscale_j = h.autoscale_j

        # end get_hsqc_pars15

    def get_hsqc_pars16(self):
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        h.autopick_range_h = float(self.w.h1RangeAutopick.text())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.autopick_range_h = h.autopick_range_h

        # end get_hsqc_pars16

    def get_hsqc_pars17(self):
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        h.autopick_range_c = float(self.w.c13RangeAutopick.text())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.autopick_range_c = h.autopick_range_c

        # end get_hsqc_pars17

    def get_hsqc_pars18(self):
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        h.cod_high = float(self.w.codHigh.text())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.cod_high = h.cod_high

        # end get_hsqc_pars18

    def get_hsqc_pars19(self):
        h = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        h.cod_low = float(self.w.codLow.text())
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].hsqc.cod_low = h.cod_low

        # end get_hsqc_pars19

    def get_proc_pars1(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        p.window_type[0] = self.w.windowFunction.currentIndex()
        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars1

    def get_proc_pars2(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        p.window_type[1] = self.w.windowFunction_2.currentIndex()
        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars2

    def get_proc_pars3(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        p.ph_corr[0] = self.w.phaseCorrection.currentIndex()
        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars3

    def get_proc_pars4(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        p.ph_corr[1] = self.w.phaseCorrection_2.currentIndex()
        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars4

    def get_proc_pars5(self):
        if len(self.nd.nmrdat[0]) > 0:
            p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
            p.water_suppression = self.w.waterSuppression.currentIndex()
            self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
            self.set_water_suppression(p.water_suppression)
        # end get_proc_pars5

    def get_proc_pars6(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        p.conv_window_type[0] = self.w.winType.currentIndex()
        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars6

    def get_proc_pars7(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        p.gibbs[0] = p.gibbs_p.get(self.w.gibbs.currentIndex())
        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars7

    def get_proc_pars8(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        p.gibbs[1] = p.gibbs_p.get(self.w.gibbs_2.currentIndex())
        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars8

    def get_proc_pars9(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.zeroFilling.text()) > 0:
            p.n_points[0] = int(self.w.zeroFilling.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars9

    def get_proc_pars10(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.zeroFilling_2.text()) > 0:
            p.n_points[1] = int(self.w.zeroFilling_2.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars10

    def get_proc_pars11(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.lb.text()) > 0:
            p.lb[0] = float(self.w.lb.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars11

    def get_proc_pars12(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.gb.text()) > 0:
            p.gb[0] = float(self.w.gb.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars12

    def get_proc_pars13(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.ssb.text()) > 0:
            p.ssb[0] = float(self.w.ssb.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars13

    def get_proc_pars14(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.lb_2.text()):
            p.lb[1] = float(self.w.lb_2.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars14

    def get_proc_pars15(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.gb_2.text()) > 0:
            p.gb[1] = float(self.w.gb_2.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars15

    def get_proc_pars16(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.ssb_2.text()) > 0:
            p.ssb[1] = float(self.w.ssb_2.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars16

    def get_proc_pars17(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.ph0.text()) > 0:
            p.ph0[0] = float(self.w.ph0.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars17

    def get_proc_pars18(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.ph1.text()) > 0:
            p.ph1[0] = float(self.w.ph1.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars18

    def get_proc_pars19(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.ph0_2.text()) > 0:
            p.ph0[1] = float(self.w.ph0_2.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars19

    def get_proc_pars20(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.ph1_2.text()) > 0:
            p.ph1[1] = float(self.w.ph1_2.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars20

    def get_proc_pars21(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.polyOrder.text()) > 0:
            p.poly_order = int(self.w.polyOrder.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars21

    def get_proc_pars22(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.extrapolationSize.text()) > 0:
            p.conv_extrapolation_size[0] = int(self.w.extrapolationSize.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars22

    def get_proc_pars23(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.windowSize.text()) > 0:
            p.conv_window_size[0] = int(self.w.windowSize.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars23

    def get_proc_pars24(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.fidOffsetCorrection.text()) > 0:
            p.fid_offset_correction = int(self.w.fidOffsetCorrection.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars24

    def get_proc_pars25(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.stripTransformStart.text()) > 0:
            p.strip_start = int(self.w.stripTransformStart.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars25

    def get_proc_pars26(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.stripTransformEnd.text()) > 0:
            p.strip_end = int(self.w.stripTransformEnd.text())

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars26

    def get_proc_pars27(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        p.autobaseline = self.w.autobaselineBox.isChecked()
        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars27

    def get_proc_pars28(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.wwStartLevel.text()) > 0:
            p.ww_start = int(self.w.wwStartLevel.text())
            self.w.wwStartLevel.setText(str(p.ww_start))

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars28

    def get_proc_pars29(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        if len(self.w.wwZeroFilling.text()) > 0:
            p.ww_zf = int(self.w.wwZeroFilling.text())
            self.w.wwZeroFilling.setText(str(p.ww_zf))

        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        # end get_proc_pars29

    def get_proc_pars30(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        idx = self.w.wwWaveletType.currentIndex()
        self.w.wwNumber.currentIndexChanged.disconnect()
        self.w.wwWaveletType.currentIndexChanged.disconnect()
        self.w.wwNumber.clear()
        self.w.wwNumber.addItems(p.wavelet_numbers[p.wavelet_names[idx]])
        idx2 = p.wavelet_default[p.wavelet_names[idx]]
        self.w.wwNumber.setCurrentIndex(idx2)
        p.ww_wavelet_type = p.wavelet_names[idx]
        p.ww_wavelet_type_number = p.wavelet_numbers[p.ww_wavelet_type][idx2]
        p.ww_wavelet_number = idx2
        self.w.wwStartLevel.setText(str(p.wavelet_start_default[p.ww_wavelet_type]))
        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        self.w.wwNumber.currentIndexChanged.connect(self.get_proc_pars31)
        self.w.wwWaveletType.currentIndexChanged.connect(self.get_proc_pars30)
        # end get_proc_pars30

    def get_proc_pars31(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        idx2 = self.w.wwNumber.currentIndex()
        self.w.wwNumber.currentIndexChanged.disconnect()
        self.w.wwNumber.clear()
        self.w.wwNumber.addItems(p.wavelet_numbers[p.ww_wavelet_type])
        self.w.wwNumber.setCurrentIndex(idx2)
        p.ww_wavelet_type_number = p.wavelet_numbers[p.ww_wavelet_type][idx2]
        p.ww_wavelet_number = idx2
        self.nd.nmrdat[self.nd.s][self.nd.e].proc = p
        self.w.wwNumber.currentIndexChanged.connect(self.get_proc_pars31)
        # end get_proc_pars31

    def get_proc_pars32(self):
        if self.nd.e > -1:
            idx = self.w.abslAlg.currentIndex()
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_alg = self.nd.baseline_algs[idx]
        # end get_proc_pars32

    def get_proc_pars33(self):
        if self.nd.e > -1:
            if self.w.abslHw.text() != 'None':
                self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_half_window = int(self.w.abslHw.text())
        # end get_proc_pars33

    def get_proc_pars34(self):
        if self.nd.e > -1:
            if self.w.abslShw.text() != 'None':
                self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_smooth_half_window = int(self.w.abslShw.text())
        # end get_proc_pars34

    def get_proc_pars35(self):
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_add_ext = float(self.w.abslAe.text())
        # end get_proc_pars35

    def get_proc_pars36(self):
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_lam = float(self.w.abslLam.text())
        # end get_proc_pars36

    def get_proc_pars37(self):
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_max_iter = int(self.w.abslMi.text())
        # end get_proc_pars37

    def get_proc_pars38(self):
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_alpha = float(self.w.abslAlpha.text())
        # end get_proc_pars38

    def get_proc_pars39(self):
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_beta = float(self.w.abslBeta.text())
        # end get_proc_pars39

    def get_proc_pars40(self):
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_gamma = float(self.w.abslGamma.text())
        # end get_proc_pars40

    def get_proc_pars41(self):
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_beta_mult = float(self.w.abslBetaMult.text())
        # end get_proc_pars41

    def get_proc_pars42(self):
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_gamma_mult = float(self.w.abslGammaMult.text())
        # end get_proc_pars42

    def get_proc_pars43(self):
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_quantile = float(self.w.abslQuantile.text())
        # end get_proc_pars43

    def get_proc_pars44(self):
        if self.nd.e > -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline_poly_order = int(self.w.abslPolyOrder.text())
        # end get_proc_pars44

    def get_bottom_top(self, line):
        margin = 0.1
        xd = line.get_xdata()
        yd = line.get_ydata()
        lo, hi = self.w.MplWidget.canvas.axes.get_xlim()
        y_displayed = yd[((xd > min(lo, hi)) & (xd < max(lo, hi)))]
        h = np.max(y_displayed) - np.min(y_displayed)
        bot = np.min(y_displayed) - margin * h
        top = np.max(y_displayed) + margin * h
        return bot, top

    def get_r_spc_p0(self):
        r = self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc
        r[0] = float(self.w.rSpc_p0.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = r
        # end get_r_spc_p0

    def get_r_spc_p1(self):
        r = self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc
        r[1] = float(self.w.rSpc_p1.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = r
        # end get_r_spc_p1

    def get_r_spc_p2(self):
        r = self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc
        r[2] = float(self.w.rSpc_p2.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = r
        # end get_r_spc_p2

    def get_r_spc_p3(self):
        r = self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc
        r[3] = float(self.w.rSpc_p3.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = r
        # end get_r_spc_p3

    def get_r_spc_p4(self):
        r = self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc
        r[4] = float(self.w.rSpc_p4.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = r
        # end get_r_spc_p4

    def get_r_spc_p5(self):
        r = self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc
        r[5] = float(self.w.rSpc_p5.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = r
        # end get_r_spc_p5

    def get_r_spc_p6(self):
        r = self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc
        r[6] = float(self.w.rSpc_p6.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = r
        # end get_r_spc_p6

    def get_i_spc_p0(self):
        i = self.nd.nmrdat[self.nd.s][self.nd.e].apc.i_spc
        i[0] = float(self.w.iSpc_p0.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = i
        # end get_i_spc_p0

    def get_i_spc_p1(self):
        i = self.nd.nmrdat[self.nd.s][self.nd.e].apc.i_spc
        i[1] = float(self.w.iSpc_p1.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = i
        # end get_i_spc_p1

    def get_i_spc_p2(self):
        i = self.nd.nmrdat[self.nd.s][self.nd.e].apc.i_spc
        i[2] = float(self.w.iSpc_p2.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = i
        # end get_i_spc_p2

    def get_i_spc_p3(self):
        i = self.nd.nmrdat[self.nd.s][self.nd.e].apc.i_spc
        i[3] = float(self.w.iSpc_p3.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = i
        # end get_i_spc_p3

    def get_i_spc_p4(self):
        i = self.nd.nmrdat[self.nd.s][self.nd.e].apc.i_spc
        i[4] = float(self.w.iSpc_p4.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = i
        # end get_i_spc_p4

    def get_i_spc_p5(self):
        i = self.nd.nmrdat[self.nd.s][self.nd.e].apc.i_spc
        i[5] = float(self.w.iSpc_p5.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = i
        # end get_i_spc_p5

    def get_i_spc_p6(self):
        i = self.nd.nmrdat[self.nd.s][self.nd.e].apc.i_spc
        i[6] = float(self.w.iSpc_p6.text())
        self.nd.nmrdat[self.nd.s][self.nd.e].apc.r_spc = i
        # end get_i_spc_p6

    def on_g_input_click(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click)
            cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
            cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click)
            cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
            code_out = io.StringIO()
            code_err = io.StringIO()
            sys.stdout = code_out
            sys.stderr = code_err
            print("x-values: {} / xDiff [ppm]: {} / xDiff [Hz]: {}".format(self.xdata, np.abs(np.diff(self.xdata)),
                                                                           np.abs(np.diff(self.xdata)) *
                                                                           self.nd.nmrdat[self.nd.s][
                                                                               self.nd.e].acq.sfo1))
            if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1:
                print("y-values: {} / yDiff: {}".format(self.ydata, -np.diff(self.ydata)))
            else:
                print("y-values: {} / yDiff: {} / yDiff [Hz]: {}".format(self.ydata, np.abs(np.diff(self.ydata)),
                                                                         np.abs(np.diff(self.ydata)) *
                                                                         self.nd.nmrdat[self.nd.s][self.nd.e].acq.sfo2))

            self.w.console.append(code_out.getvalue())
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            code_out.close()
            code_err.close()
            self.xdata = []
            self.ydata = []
            self.show_console()

    def on_g_input_spline_baseline_click(self, event):
        if event.button != 1 or event.dblclick == True:
            if event.dblclick == True:
                self.xdata.pop()

            #xdata1 = set(self.xdata)  # remove duplicate values
            #self.xdata = list(xdata1)
            #self.xdata.sort()
            cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_spline_baseline_click)
            cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
            cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_spline_baseline_click)
            cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
            for k in range(len(self.nd.nmrdat[self.nd.s])):
                if self.nd.nmrdat[self.nd.s][k].display.display_spc or k == self.nd.e:
                    self.nd.nmrdat[self.nd.s][k].spline_baseline.baseline_points = self.xdata
                    self.nd.nmrdat[self.nd.s][k].add_baseline_points()

            self.xdata = []
            self.ydata = []
            self.show_version()

        else:
            self.xdata.append(np.round(1e4 * event.xdata) / 1e4)
            self.ydata.append(event.ydata)
            #xdata1 = set(self.xdata)  # remove duplicate values
            #self.xdata = list(xdata1)
            #self.xdata.sort()
            for k in range(len(self.nd.nmrdat[self.nd.s])):
                if self.nd.nmrdat[self.nd.s][k].display.display_spc or k == self.nd.e:
                    self.nd.nmrdat[self.nd.s][k].spline_baseline.baseline_points = self.xdata
                    self.nd.nmrdat[self.nd.s][k].add_baseline_points()

        self.fill_spline_baseline_tw()
        self.plot_spc(True)
        # end on_g_input_spline_baseline_click

    def on_g_input_click_add_peak(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_add_peak)
            cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
            cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_add_peak)
            cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
            xy = []
            for k in range(len(self.xdata)):
                xy.append((self.xdata[k], self.ydata[k]))

            self.xdata = []
            self.ydata = []
            t = np.round(1e4 * np.array([xy[0][0], xy[1][0]])) / 1e4
            self.nd.add_peak(t, '')
            # self.nd.pp.exclude_start = np.append(self.nd.pp.exclude_start, min(t))
            # self.nd.pp.exclude_end = np.append(self.nd.pp.exclude_end, max(t))
            self.fill_peak_numbers()
            # self.w.excludeRegionTW.setFocus()
            # self.set_plot_pre_proc()
            # self.w.excludeRegionTW.setFocus()
            self.plot_spc()
            # self.set_exclude_pre_proc()

    def on_g_input_hsqc2_click(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.hsqcPeak.canvas.mpl_connect('button_press_event', self.on_g_input_hsqc2_click)
            cid = self.w.hsqcPeak.canvas.mpl_disconnect(cid)
            cid2 = self.w.hsqcPeak.canvas.mpl_connect('button_release_event', self.on_g_input_hsqc2_click)
            cid2 = self.w.hsqcPeak.canvas.mpl_disconnect(cid2)
            if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.pick_local_opt == True:
                new_max = self.nd.nmrdat[self.nd.s][self.nd.e].pick_local_opt([self.xdata[0], self.ydata[0]])
                self.xdata[0] = new_max[0]
                self.ydata[0] = new_max[1]

            h1_picked = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[
                self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite].h1_picked[
                self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak - 1]
            c13_picked = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[
                self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite].c13_picked[
                self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak - 1]
            dist = np.array([])
            dist.resize(len(h1_picked))
            for k in range(len(h1_picked)):
                dist[k] = (h1_picked[k] - self.xdata[0]) ** 2 + (c13_picked[k] - self.ydata[0]) ** 2

            idx = np.where(dist == dist.min())[0][0]
            # print("h1_picked: {}, c13_picked: {}, idx: {}".format(h1_picked, c13_picked, idx))
            h1_picked.remove(h1_picked[idx])
            c13_picked.remove(c13_picked[idx])
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[
                self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite].h1_picked[
                self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak - 1] = h1_picked
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[
                self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite].c13_picked[
                self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak - 1] = c13_picked
            self.xdata = []
            self.ydata = []
            self.plot_metabolite_peak(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak)
            # self.set_exclude_pre_proc()

    def on_g_input_hsqc_click(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.hsqcPeak.canvas.mpl_connect('button_press_event', self.on_g_input_hsqc_click)
            cid = self.w.hsqcPeak.canvas.mpl_disconnect(cid)
            cid2 = self.w.hsqcPeak.canvas.mpl_connect('button_release_event', self.on_g_input_hsqc_click)
            cid2 = self.w.hsqcPeak.canvas.mpl_disconnect(cid2)
            if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.pick_local_opt == True:
                new_max = self.nd.nmrdat[self.nd.s][self.nd.e].pick_local_opt([self.xdata[0], self.ydata[0]])
                self.xdata[0] = new_max[0]
                self.ydata[0] = new_max[1]

            self.nd.nmrdat[self.nd.s][self.nd.e].add_hsqc_peak(self.xdata[0], self.ydata[0])
            self.xdata = []
            self.ydata = []
            self.plot_metabolite_peak(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak)
            # self.set_exclude_pre_proc()

    def on_g_input_click_ref_1d(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_ref_1d)
            cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
            cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_ref_1d)
            cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
            xy = []
            for k in range(len(self.xdata)):
                xy.append((self.xdata[k], self.ydata[k]))

            self.xdata = []
            self.ydata = []
            self.nd.nmrdat[self.nd.s][self.nd.e].ref_point[0] = self.nd.nmrdat[self.nd.s][self.nd.e].ppm2points(
                xy[0][0],
                0)
            self.nd.nmrdat[self.nd.s][self.nd.e].ref_shift[0] = self.temp_ref_shift
            self.nd.nmrdat[self.nd.s][self.nd.e].ref = 'manual'
            self.nd.nmrdat[self.nd.s][self.nd.e].calc_ppm()
            self.plot_spc()
            #self.reset_plot()

    def on_g_input_click_ref_1d_all(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_ref_1d_all)
            cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
            cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_ref_1d_all)
            cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
            self.reference1d_all_2()


    def on_g_input_click_compress(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_compress)
            cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
            cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_compress)
            cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
            xy = []
            for k in range(len(self.xdata)):
                xy.append((self.xdata[k], self.ydata[k]))

            self.xdata = []
            self.ydata = []
            t = np.round(1e4 * np.array([xy[0][0], xy[1][0]])) / 1e4
            self.nd.pp.compress_start = np.append(self.nd.pp.compress_start, min(t))
            self.nd.pp.compress_end = np.append(self.nd.pp.compress_end, max(t))
            self.fill_pre_processing_numbers()
            self.w.compressBucketsTW.setFocus()
            self.set_plot_pre_proc()
            self.w.compressBucketsTW.setFocus()
            self.plot_spc_pre_proc()
            self.set_compress_pre_proc()

    def on_g_input_click_exclude(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_exclude)
            cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
            cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_exclude)
            cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
            xy = []
            for k in range(len(self.xdata)):
                xy.append((self.xdata[k], self.ydata[k]))

            self.xdata = []
            self.ydata = []
            t = np.round(1e4 * np.array([xy[0][0], xy[1][0]])) / 1e4
            self.nd.pp.exclude_start = np.append(self.nd.pp.exclude_start, min(t))
            self.nd.pp.exclude_end = np.append(self.nd.pp.exclude_end, max(t))
            self.fill_pre_processing_numbers()
            self.w.excludeRegionTW.setFocus()
            self.set_plot_pre_proc()
            self.w.excludeRegionTW.setFocus()
            self.plot_spc_pre_proc()
            self.set_exclude_pre_proc()

    def on_g_input_click_seg_align(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_seg_align)
            cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
            cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_seg_align)
            cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
            xy = []
            for k in range(len(self.xdata)):
                xy.append((self.xdata[k], self.ydata[k]))

            self.xdata = []
            self.ydata = []
            t = np.round(1e4 * np.array([xy[0][0], xy[1][0]])) / 1e4
            self.nd.pp.seg_start = np.append(self.nd.pp.seg_start, min(t))
            self.nd.pp.seg_end = np.append(self.nd.pp.seg_end, max(t))
            self.fill_pre_processing_numbers()
            self.w.segAlignTW.setFocus()
            self.set_plot_pre_proc()
            self.w.segAlignTW.setFocus()
            self.plot_spc_pre_proc()
            self.set_seg_align_pre_proc()

    def on_g_input_click_ref_2d(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_ref_2d)
            cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
            cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_ref_2d)
            cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
            xy = []
            for k in range(len(self.xdata)):
                xy.append((self.xdata[k], self.ydata[k]))

            self.xdata = []
            self.ydata = []
            self.nd.nmrdat[self.nd.s][self.nd.e].ref_point[0] = self.nd.nmrdat[self.nd.s][self.nd.e].ppm2points(
                xy[0][0],
                0)
            self.nd.nmrdat[self.nd.s][self.nd.e].ref_shift[0] = self.temp_ref_shift[0]
            self.nd.nmrdat[self.nd.s][self.nd.e].ref_point[1] = self.nd.nmrdat[self.nd.s][self.nd.e].ppm2points(
                xy[0][1],
                1)
            self.nd.nmrdat[self.nd.s][self.nd.e].ref_shift[1] = self.temp_ref_shift[1]
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.ref_point[0] = self.nd.nmrdat[self.nd.s][self.nd.e].ref_point[0] * \
                                                                     self.nd.nmrdat[self.nd.s][self.nd.e].proc.n_points[
                                                                         0] / (len(
                self.nd.nmrdat[self.nd.s][self.nd.e].fid[0]) * self.nd.nmrdat[self.nd.s][self.nd.e].proc.mult_factor[0])
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.ref_point[1] = self.nd.nmrdat[self.nd.s][self.nd.e].ref_point[1] * \
                                                                     self.nd.nmrdat[self.nd.s][self.nd.e].proc.n_points[
                                                                         1] / (len(
                self.nd.nmrdat[self.nd.s][self.nd.e].fid) * self.nd.nmrdat[self.nd.s][self.nd.e].proc.mult_factor[1])
            self.nd.nmrdat[self.nd.s][self.nd.e].calc_ppm()
            self.reset_plot()

    def on_g_input_2d_click(self, event):
        self.cur_clicks += 1
        if self.cur_clicks < self.n_clicks:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
        else:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.n_clicks = 1
            self.cur_clicks = 0
            cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_2d_click)
            cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
            cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_2d_click)
            cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
            self.xy = []
            self.xy = np.resize(self.xy, (1, 2))
            self.xy[0][0] = self.xdata[0]
            self.xy[0][1] = self.ydata[0]
            self.xdata = []
            self.ydata = []
            xy = self.xy
            self.show_ph_corr2d()
            xyPts = []
            xy2 = []
            xyPts.append(self.nd.nmrdat[self.nd.s][self.nd.e].ppm2points(xy[0][0], 0))
            xyPts.append(self.nd.nmrdat[self.nd.s][self.nd.e].ppm2points(xy[0][1], 1))
            self.ph_corr.spc_row_pts.append(xyPts[1])
            self.ph_corr.spc_col_pts.append(xyPts[0])
            xy2.append(self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(xyPts[0], 0))
            xy2.append(self.nd.nmrdat[self.nd.s][self.nd.e].points2ppm(xyPts[1], 1))
            self.ph_corr.spc_row.append(xy2[1])
            self.ph_corr.spc_col.append(xy2[0])
            self.plot_2d_col_row()

    def ginput(self, n_clicks=1):
        self.w.MplWidget.canvas.setFocus()
        self.show_nmr_spectrum()
        self.n_clicks = n_clicks
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # end ginput

    def ginput_spline_baseline(self):
        self.xdata = list(self.nd.nmrdat[self.nd.s][self.nd.e].spline_baseline.baseline_points)
        self.show_spline_baseline_pick()
        self.w.MplWidget.canvas.setFocus()
        self.show_nmr_spectrum()
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_spline_baseline_click)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_spline_baseline_click)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        #for k in range(len(self.nd.nmrdat[self.nd.s])):
        #    if self.nd.nmrdat[self.nd.s][k].display.display_spc:
        #        self.nd.nmrdat[self.nd.s][k].spline_baseline.baseline_points = []
        #        self.nd.nmrdat[self.nd.s][k].spline_baseline.baseline_points_pts = []

        # end ginput

    def ginput_hsqc(self, n_clicks=1):
        self.w.hsqcPeak.canvas.setFocus()
        self.n_clicks = n_clicks
        cid = self.w.hsqcPeak.canvas.mpl_connect('button_press_event', self.on_g_input_hsqc_click)
        cid2 = self.w.hsqcPeak.canvas.mpl_connect('button_release_event', self.on_g_input_hsqc_click)
        cid2 = self.w.hsqcPeak.canvas.mpl_disconnect(cid2)
        # end ginput_hsqc

    def ginput_hsqc2(self, n_clicks=1):
        self.w.hsqcPeak.canvas.setFocus()
        self.n_clicks = n_clicks
        cid = self.w.hsqcPeak.canvas.mpl_connect('button_press_event', self.on_g_input_hsqc2_click)
        cid2 = self.w.hsqcPeak.canvas.mpl_connect('button_release_event', self.on_g_input_hsqc2_click)
        cid2 = self.w.hsqcPeak.canvas.mpl_disconnect(cid2)
        # end ginput_hsqc

    def ginput_add_peak(self, n_clicks=2):
        self.w.MplWidget.canvas.setFocus()
        self.show_nmr_spectrum()
        self.n_clicks = n_clicks
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_add_peak)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_add_peak)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # end ginput_add_peak

    def ginput_ref_1d(self, n_clicks=1):
        self.w.MplWidget.canvas.setFocus()
        self.show_nmr_spectrum()
        self.n_clicks = n_clicks
        # print("ginput_ref_1d")
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_ref_1d)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_ref_1d)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # end ginput

    def ginput_ref_1d_all(self, n_clicks=1):
        self.w.MplWidget.canvas.setFocus()
        self.show_nmr_spectrum()
        self.n_clicks = n_clicks
        # print("ginput_ref_1d")
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_ref_1d_all)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_ref_1d_all)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # end ginput

    def ginput_ref_2d(self, n_clicks=1):
        self.w.MplWidget.canvas.setFocus()
        self.show_nmr_spectrum()
        self.n_clicks = n_clicks
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_ref_2d)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_ref_2d)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # end ginput

    def ginput_compress(self, n_clicks=1):
        self.w.MplWidget.canvas.setFocus()
        self.show_nmr_spectrum()
        self.n_clicks = n_clicks
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_compress)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_compress)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # end ginput

    def ginput_exclude(self, n_clicks=2):
        self.w.MplWidget.canvas.setFocus()
        self.show_nmr_spectrum()
        self.n_clicks = n_clicks
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_exclude)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_exclude)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # end ginput

    def ginput_seg_align(self, n_clicks=1):
        self.w.MplWidget.canvas.setFocus()
        self.show_nmr_spectrum()
        self.n_clicks = n_clicks
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_click_seg_align)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_click_seg_align)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # end ginput

    def ginput2d(self):
        self.w.MplWidget.canvas.setFocus()
        self.show_nmr_spectrum()
        self.n_clicks = 1
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_g_input_2d_click)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_g_input_2d_click)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        # end ginput2d

    def h(self):
        print("Command history: ")
        print(">>><<<")
        for k in range(len(self.nd.cmd_buffer)):
            print(self.nd.cmd_buffer[k])

        return (">>><<<")
        # end h

    def hide_pre_processing(self):
        self.w.preProcessingTab.setHidden(True)
        self.w.preProcPeak.setTabEnabled(0, False)
        self.w.preProcessingGroupBox.setHidden(True)
        self.w.preProcessingSelect.setHidden(True)
        self.w.preProcessingWidget.setHidden(True)
        self.w.runPreProcessingButton.setHidden(True)
        self.w.resetPreProcessingButton.setHidden(True)
        self.w.writeScriptButton.setHidden(True)
        self.plot_spc(True)
        # end hide_pre_processing

    def hide_peak_picking(self):
        self.w.peakPickingTab.setHidden(True)
        self.w.preProcPeak.setTabEnabled(1, False)
        self.w.peakWidget.setHidden(True)
        self.w.peakAddButton.setHidden(True)
        self.w.peakClearButton.setHidden(True)
        self.w.peakExportButton.setHidden(True)
        self.w.intAllExps.setHidden(True)
        self.w.quantify.setHidden(True)
        self.w.exportFormatCB.setHidden(True)
        # end hide_peak_picking

    def hide_spline_baseline(self):
        self.w.preProcPeak.setHidden(True)
        self.w.peakPickingTab.setHidden(True)
        self.w.preProcPeak.setTabEnabled(2, False)
        self.w.splineBaselineTW.setHidden(True)
        self.w.label_98.setHidden(True)
        self.w.label_99.setHidden(True)
        self.w.averagePoints.setHidden(True)
        self.w.linearSplinePoints.setHidden(True)
        self.w.addSplineBaselineButton.setHidden(True)
        self.w.clearSplineBaselineButton.setHidden(True)
        self.w.resetSplineBaselineButton.setHidden(True)
        self.w.plotBaselineButton.setHidden(True)
        self.w.correctAllButton.setHidden(True)
        # end hide_spline_baseline

    def html(self, url=''):
        if len(url) == 0:
            url = "https://ludwigc.github.io/metabolabpy"

        self.w.helpView.setUrl(url)
        self.w.nmrSpectrum.setCurrentIndex(12)
        # end html

    def show_peak_picking(self):
        self.w.preProcPeak.setHidden(False)
        self.w.peakPickingTab.setHidden(False)
        self.w.preProcPeak.setTabEnabled(0, False)
        self.w.preProcPeak.setTabEnabled(1, True)
        self.w.preProcPeak.setTabEnabled(2, False)
        self.w.peakWidget.setHidden(False)
        self.w.peakAddButton.setHidden(False)
        self.w.peakClearButton.setHidden(False)
        self.w.peakExportButton.setHidden(False)
        self.w.intAllExps.setHidden(False)
        self.w.quantify.setHidden(False)
        self.w.exportFormatCB.setHidden(False)
        # end show_peak_picking

    def show_spline_baseline(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            if self.nd.nmrdat[self.nd.s][k].display.display_spc or self.nd.e == k:
                self.nd.nmrdat[self.nd.s][k].spline_baseline.baseline_points = self.nd.nmrdat[self.nd.s][self.nd.e].spline_baseline.baseline_points
                self.nd.nmrdat[self.nd.s][k].add_baseline_points()

        self.w.preProcPeak.setHidden(False)
        self.w.splineBaselineTab.setHidden(False)
        self.w.preProcPeak.setTabEnabled(0, False)
        self.w.preProcPeak.setTabEnabled(1, False)
        self.w.preProcPeak.setTabEnabled(2, True)
        self.w.splineBaselineTW.setHidden(False)
        self.w.label_98.setHidden(False)
        self.w.label_99.setHidden(False)
        self.w.averagePoints.setHidden(False)
        self.w.linearSplinePoints.setHidden(False)
        self.w.addSplineBaselineButton.setHidden(False)
        self.w.clearSplineBaselineButton.setHidden(False)
        self.w.resetSplineBaselineButton.setHidden(False)
        self.w.plotBaselineButton.setHidden(False)
        self.w.correctAllButton.setHidden(False)
        # show_spline_baseline

    def hilbert(self, mat):
        npts = len(mat[0])
        npts1 = len(mat)
        v1 = np.ones(npts1)
        mat1 = np.array([[]], dtype='complex')
        mat1 = np.resize(mat1, (npts1, npts))
        b_mat = np.zeros(int(2 * npts), dtype='complex')
        b_mat[:(npts + 1)] = np.ones(npts + 1)
        b_mat[1:npts] += b_mat[1:npts]
        z_mat = np.zeros(int(2 * npts), dtype='complex')
        b_mat = np.outer(v1, b_mat)
        z_mat = np.outer(v1, z_mat)
        z_mat[:, :npts] = mat
        z_mat = np.fft.ifft(b_mat * np.fft.fft(z_mat))
        mat = z_mat[:, :npts]
        return mat
        # end hilbert

    def horz_ph_corr_2d(self):
        s = self.nd.s
        e = self.nd.e
        self.ph_corr.n_dims = 2
        self.ph_corr.dim = 0
        n_lines = len(self.ph_corr.spc_row_pts)
        if n_lines > 0:
            npts0 = len(self.nd.nmrdat[s][e].spc)
            npts = len(self.nd.nmrdat[s][e].spc[0])
            self.ph_corr.spc = np.zeros((n_lines, npts), dtype='complex')
            spc1 = np.copy(self.nd.nmrdat[s][e].spc)
            for k in range(n_lines):
                spc = np.array([spc1[npts0 - self.ph_corr.spc_row_pts[k]]])
                spc = self.hilbert(spc)
                self.ph_corr.spc[k] = spc[0]

            self.ph_corr.ppm = self.nd.nmrdat[s][e].ppm1
            if self.ph_corr.pivot_points2d[0] < 0:
                self.ph_corr.pivot_points2d[0] = int(len(self.ph_corr.ppm) / 2)
                self.ph_corr.pivot2d[0] = self.nd.nmrdat[s][e].points2ppm(self.ph_corr.pivot_points2d[0], 0)

        self.show_ph_corr2d_1d(self.ph_corr.dim)
        self.ph_corr.spc_max = np.max(np.max(np.abs(self.ph_corr.spc)))
        try:
            zwo = True
            self.w.MplWidget.canvas.figure.canvas.toolbar.zoom()
        except:
            pass

        self.set_zoom_off()
        self.ph_corr.max_ph0 = 90.0
        self.ph_corr.max_ph1 = 90.0
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_ph_corr_click_2d)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_ph_corr_release_2d)
        # self.w.actionApplyPhCorr.triggered.connect(self.apply_2d_ph_corr)
        # self.w.actionCancelPhCorr.triggered.connect(self.cancel2dPhCorr)
        self.w.pickRowColPhCorr2d.setVisible(False)
        self.w.emptyRowColPhCorr2d.setVisible(False)
        self.w.removeRowColPhCorr2d.setVisible(False)
        self.w.horzPhCorr2d.setVisible(False)
        self.w.vertPhCorr2d.setVisible(False)
        self.w.zoomPhCorr2d.setVisible(True)
        self.w.applyPhCorr2d.setVisible(True)
        self.w.cancelPhCorr2d.setVisible(True)
        self.w.exitPhCorr2d.setVisible(False)
        self.w.exitZoomPhCorr2d.setVisible(False)
        self.ph_corr_plot_spc_2d(False)
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end horz_ph_corr_2d

    def hsqc_spin_sys_reset(self):
        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        c13_picked = hsqc.hsqc_data[hsqc.cur_metabolite].c13_picked
        h1_picked = hsqc.hsqc_data[hsqc.cur_metabolite].h1_picked
        c13_picked_lib = hsqc.hsqc_data[hsqc.cur_metabolite].c13_picked_lib
        h1_picked_lib = hsqc.hsqc_data[hsqc.cur_metabolite].h1_picked_lib
        hsqc.hsqc_data[hsqc.cur_metabolite].init_data(hsqc.metabolite_information)
        hsqc.hsqc_data[hsqc.cur_metabolite].c13_picked = c13_picked
        hsqc.hsqc_data[hsqc.cur_metabolite].c13_picked_lib = c13_picked_lib
        hsqc.hsqc_data[hsqc.cur_metabolite].h1_picked = h1_picked
        hsqc.hsqc_data[hsqc.cur_metabolite].h1_picked_lib = h1_picked_lib
        hsqc.hsqc_data[hsqc.cur_metabolite].c13_offset = {}
        hsqc.hsqc_data[hsqc.cur_metabolite].cod = []
        for k in range(len(hsqc.hsqc_data[hsqc.cur_metabolite].h1_shifts)):
            hsqc.hsqc_data[hsqc.cur_metabolite].cod.append(-1)

        self.plot_metabolite_peak(hsqc.cur_peak)
        # end hsqc_spin_sys_reset

    def hsqc_spin_sys_change(self):
        if self.nd.hsqc_spin_sys_connected == True:
            self.w.hsqcSpinSys.cellChanged.disconnect()
            self.nd.hsqc_spin_sys_connected = False

        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        spin_sys = hsqc.hsqc_data[hsqc.cur_metabolite].spin_systems[hsqc.cur_peak - 1]
        perc_sum = 0
        jcc_list = []
        for k in range(len(spin_sys['c13_idx'])):
            if hasattr(self.w.hsqcSpinSys.item(k, 2), 'text'):
                if len(self.w.hsqcSpinSys.item(k, 2).text()) > 0:
                    jcc_list = self.w.hsqcSpinSys.item(k, 2).text().split(' ')
                    for m in range(len(jcc_list)):
                        jcc_list[m] = float(jcc_list[m])

                    spin_sys['j_cc'][k] = jcc_list

            idx = spin_sys['c13_idx'][k]
            nuc1 = idx[0]
            if len(idx) < 3:
                for l in range(len(idx) - 1):
                    idx2 = -1
                    nuc2 = idx[l + 1]
                    nuc1_list = np.where(hsqc.hsqc_data[hsqc.cur_metabolite].j_nuc1 == min(nuc1, nuc2))[0]
                    nuc2_list = np.where(hsqc.hsqc_data[hsqc.cur_metabolite].j_nuc2 == max(nuc1, nuc2))[0]
                    for m in range(len(nuc1_list)):
                        if len(np.where(nuc2_list == nuc1_list[m])[0]) > 0:
                            idx2 = np.where(nuc2_list == nuc1_list[m])[0][0]
                            idx2 = nuc2_list[idx2]
                            if len(jcc_list) > l:
                                hsqc.hsqc_data[hsqc.cur_metabolite].j_cc[idx2] = jcc_list[l]

            idx = QTableWidgetItem(' '.join(str(e) for e in spin_sys['c13_idx'][k]))
            self.w.hsqcSpinSys.setItem(k, 0, idx)
            # if self.w.hsqcSpinSys.item(k,1) != None:
            if hasattr(self.w.hsqcSpinSys.item(k, 1), 'text'):
                # print("k: {}, self.w.hsqcSpinSys.item(k,1).text(): {}".format(k, self.w.hsqcSpinSys.item(k, 1).text()))
                if len(self.w.hsqcSpinSys.item(k, 1).text()) > 0:
                    hsqc.hsqc_data[hsqc.cur_metabolite].c13_offset[idx.text()] = float(
                        self.w.hsqcSpinSys.item(k, 1).text())
                else:
                    hsqc.hsqc_data[hsqc.cur_metabolite].c13_offset[idx.text()] = 0.0
            else:
                hsqc.hsqc_data[hsqc.cur_metabolite].c13_offset[idx.text()] = 0.0

            if hasattr(self.w.hsqcSpinSys.item(k, 3), 'text'):
                if len(self.w.hsqcSpinSys.item(k, 3).text()) > 0:
                    perc_sum += float(self.w.hsqcSpinSys.item(k, 3).text())

        if self.w.spinSysAutoUpdate.isChecked():
            for k in range(len(spin_sys['c13_idx'])):
                # if self.w.hsqcSpinSys.item(k,3) != None:
                try:
                    if len(self.w.hsqcSpinSys.item(k, 3).text()) > 0:
                        perc = round(float(self.w.hsqcSpinSys.item(k, 3).text()) * 100.0 / perc_sum, 3)
                    else:
                        if k > 0:
                            perc = 0.0
                        else:
                            perc = 100.0

                # else:
                except:
                    if k > 0:
                        perc = 0.0
                    else:
                        perc = 100.0

                spin_sys['contribution'][k] = perc
        else:
            for k in range(len(spin_sys['c13_idx'])):
                perc = float(self.w.hsqcSpinSys.item(k, 3).text())
                spin_sys['contribution'][k] = perc

        self.set_hsqc_spin_sys()
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim:
            self.plot_metabolite_peak(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak)

        if self.nd.hsqc_spin_sys_connected == False:
            self.w.hsqcSpinSys.cellChanged.connect(self.hsqc_spin_sys_change)
            self.nd.hsqc_spin_sys_connected = True

        # end hsqc_spin_sys_change

    def iter_all_strings(self):
        for size in itertools.count(1):
            for s in itertools.product(ascii_uppercase, repeat=size):
                yield "".join(s)

        # end iter_all_strings+

    def load_button(self):
        if len(self.cf.current_directory) > 0:
            if os.path.isdir(self.cf.current_directory):
                os.chdir(self.cf.current_directory)

        selectedDirectory = QFileDialog.getExistingDirectory()
        if (len(selectedDirectory) > 0):
            kz = self.clear()
            self.w.keepZoom.setChecked(kz)
            self.zero_script()
        else:
            return

        self.load_file(selectedDirectory)
        if 'pygamma' in sys.modules:
            for k in range(len(self.nd.nmrdat)):
                for l in range(len(self.nd.nmrdat[k])):
                    self.nd.nmrdat[k][l].has_pg = True

        else:
            for k in range(len(self.nd.nmrdat)):
                for l in range(len(self.nd.nmrdat[k])):
                    self.nd.nmrdat[k][l].has_pg = False

        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim:
            self.w.maAutoSim.setChecked(True)
        else:
            self.w.maAutoSim.setChecked(False)

        self.w.autobaselineBox.setChecked(self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline)
        # end load_button

    def check_file(self):
        if len(self.cf.current_directory) > 0:
            if os.path.isdir(self.cf.current_directory):
                os.chdir(self.cf.current_directory)

        selectedDirectory = QFileDialog.getExistingDirectory()
        if (len(selectedDirectory) == 0):
            return

        msg = self.nd.check_file(selectedDirectory)
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        if (len(msg) > 0):
            self.w.nmrSpectrum.setCurrentIndex(10)
            code_out = io.StringIO()
            code_err = io.StringIO()
            sys.stdout = code_out
            sys.stderr = code_err
            print(msg)
            self.w.console.setTextColor(txt_col)
            self.w.console.append(code_out.getvalue())
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            code_out.close()
            code_err.close()
            self.w.console.verticalScrollBar().setValue(self.w.console.verticalScrollBar().maximum())

        # end check_file

    def load_config(self):
        self.cf.read_config()
        self.w.phRefColour.setCurrentIndex(self.nd.nmrdat[0][0].display.colours2.get(self.cf.phase_reference_colour))
        #self.w.autoPlot.setChecked(self.cf.auto_plot)
        self.w.keepZoom.setChecked(self.cf.keep_zoom)
        self.w.fontSize.setValue(self.cf.font_size)
        self.std_pos_col1 = (self.cf.pos_col10, self.cf.pos_col11, self.cf.pos_col12)
        self.std_neg_col1 = (self.cf.neg_col10, self.cf.neg_col11, self.cf.neg_col12)
        self.std_pos_col2 = (self.cf.pos_col20, self.cf.pos_col21, self.cf.pos_col22)
        self.std_neg_col2 = (self.cf.neg_col20, self.cf.neg_col21, self.cf.neg_col22)
        self.set_standard_colours()
        # end load_config

    def load_example_script(self):
        idx = self.w.exampleScripts.view().selectedIndexes()[0].row()
        self.w.exampleScripts.setCurrentIndex(idx)
        nmr_dir = os.path.split(inspect.getmodule(nmrDataSet).__file__)[0]
        base_dir = os.path.split(nmr_dir)[0]
        if (idx == 0):
            f_name = os.path.join(base_dir, "exampleScripts", "example1DScript.py")

        if (idx == 1):
            f_name = os.path.join(base_dir, "exampleScripts", "exampleAutoPhaseScript.py")

        if (idx == 2):
            f_name = os.path.join(base_dir, "exampleScripts", "exampleAutoBaselineScript.py")

        if (idx == 3):
            f_name = os.path.join(base_dir, "exampleScripts", "example2DJresScript.py")

        if (idx == 4):
            f_name = os.path.join(base_dir, "exampleScripts", "examplePreprocessingScript.py")

        if (idx == 5):
            f_name = os.path.join(base_dir, "exampleScripts", "example2DNMRPipeScript.py")

        if (idx == 6):
            f_name = os.path.join(base_dir, "exampleScripts", "adaptiveLineBroadening.py")

        f = open(f_name, 'r')
        script_text = f.read()
        self.w.script.setText(script_text)
        # end load_example_script

    def load_dark_mode(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].display.pos_col_rgb = self.std_pos_col2
            self.nd.nmrdat[self.nd.s][k].display.neg_col_rgb = self.std_neg_col2

        idx = self.w.helpComboBox.currentIndex()
        url = []
        f_name = os.path.join(os.path.dirname(__file__), "web", "index.html")
        url.append("file:///" + f_name.replace('\\', '/'))
        url.append("http://www.bml-nmr.org")
        url.append("https://www.hmdb.ca")
        url.append("https://www.smpdb.ca")
        url.append("https://bmrb.io/metabolomics/")
        url.append("https://www.genome.jp/kegg/pathway.html#metabolism")
        url.append("https://nmrshiftdb.nmr.uni-koeln.de")
        url.append("https://sdbs.db.aist.go.jp/sdbs/cgi-bin/cre_index.cgi")
        url.append("http://dmar.riken.jp/spincouple/")
        self.w.helpView.setUrl(url[idx])
        bg = (42 / 255, 42 / 255, 42 / 255)
        fg = (255 / 255, 255 / 255, 255 / 255)
        self.w.MplWidget.canvas.figure.set_facecolor(bg)
        self.w.MplWidget.canvas.axes.set_facecolor(bg)
        self.w.MplWidget.canvas.axes.xaxis.label.set_color(fg)
        self.w.MplWidget.canvas.axes.yaxis.label.set_color(fg)
        self.w.MplWidget.canvas.axes.tick_params(axis='x', colors=fg)
        self.w.MplWidget.canvas.axes.tick_params(axis='y', colors=fg)
        self.w.MplWidget.canvas.axes.spines['bottom'].set_color(fg)
        self.w.MplWidget.canvas.axes.spines['top'].set_color(fg)
        self.w.MplWidget.canvas.axes.spines['left'].set_color(fg)
        self.w.MplWidget.canvas.axes.spines['right'].set_color(fg)
        self.w.hsqcMultiplet.canvas.figure.set_facecolor(bg)
        self.w.hsqcMultiplet.canvas.axes.set_facecolor(bg)
        self.w.hsqcMultiplet.canvas.axes.xaxis.label.set_color(fg)
        self.w.hsqcMultiplet.canvas.axes.yaxis.label.set_color(fg)
        self.w.hsqcMultiplet.canvas.axes.tick_params(axis='x', colors=fg)
        self.w.hsqcMultiplet.canvas.axes.tick_params(axis='y', colors=fg)
        self.w.hsqcMultiplet.canvas.axes.spines['bottom'].set_color(fg)
        self.w.hsqcMultiplet.canvas.axes.spines['top'].set_color(fg)
        self.w.hsqcMultiplet.canvas.axes.spines['left'].set_color(fg)
        self.w.hsqcMultiplet.canvas.axes.spines['right'].set_color(fg)
        self.w.hsqcPeak.canvas.figure.set_facecolor(bg)
        self.w.hsqcPeak.canvas.axes.set_facecolor(bg)
        self.w.hsqcPeak.canvas.axes.xaxis.label.set_color(fg)
        self.w.hsqcPeak.canvas.axes.yaxis.label.set_color(fg)
        self.w.hsqcPeak.canvas.axes.tick_params(axis='x', colors=fg)
        self.w.hsqcPeak.canvas.axes.tick_params(axis='y', colors=fg)
        self.w.hsqcPeak.canvas.axes.spines['bottom'].set_color(fg)
        self.w.hsqcPeak.canvas.axes.spines['top'].set_color(fg)
        self.w.hsqcPeak.canvas.axes.spines['left'].set_color(fg)
        self.w.hsqcPeak.canvas.axes.spines['right'].set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.figure.set_facecolor(bg)
        # self.w.isotopomerHsqcPeak.canvas.axes.set_facecolor(bg)
        # self.w.isotopomerHsqcPeak.canvas.axes.xaxis.label.set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.yaxis.label.set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.tick_params(axis='x', colors=fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.tick_params(axis='y', colors=fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.spines['bottom'].set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.spines['top'].set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.spines['left'].set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.spines['right'].set_color(fg)
        # self.w.isotopomerMultiplet.canvas.figure.set_facecolor(bg)
        # self.w.isotopomerMultiplet.canvas.axes.set_facecolor(bg)
        # self.w.isotopomerMultiplet.canvas.axes.xaxis.label.set_color(fg)
        # self.w.isotopomerMultiplet.canvas.axes.yaxis.label.set_color(fg)
        # self.w.isotopomerMultiplet.canvas.axes.tick_params(axis='x', colors=fg)
        # self.w.isotopomerMultiplet.canvas.axes.tick_params(axis='y', colors=fg)
        # self.w.isotopomerMultiplet.canvas.axes.spines['bottom'].set_color(fg)
        # self.w.isotopomerMultiplet.canvas.axes.spines['top'].set_color(fg)
        # self.w.isotopomerMultiplet.canvas.axes.spines['left'].set_color(fg)
        # self.w.isotopomerMultiplet.canvas.axes.spines['right'].set_color(fg)
        # end load_dark_mode

    def load_mat(self, file_name=False):
        if not file_name:
            if len(self.cf.current_directory) > 0:
                if os.path.isdir(self.cf.current_directory):
                    os.chdir(self.cf.current_directory)

            selected_file = QFileDialog.getOpenFileName(None, "Load .mat file", self.cf.current_directory, "Matlab files (*.mat)")
            selected_file = selected_file[0]
            if (len(selected_file) > 0):
                kz = self.clear()
                self.w.keepZoom.setChecked(kz)
                self.zero_script()
            else:
                return
        else:
            selected_file = file_name

        self.nd.load_mat(selected_file)
        self.reset_plot()
        self.update_gui()
        self.w.console.verticalScrollBar().setValue(self.w.console.verticalScrollBar().maximum())
        self.show_title_file_information()
        self.show_acquisition_parameters()
        self.set_hsqc()
        self.show_nmr_spectrum()
        # end load_mat

    def set_standard_plot_colours(self):
        self.cf.read_config()
        self.std_pos_col1 = (self.cf.pos_col10, self.cf.pos_col11, self.cf.pos_col12)
        self.std_neg_col1 = (self.cf.neg_col10, self.cf.neg_col11, self.cf.neg_col12)
        self.std_pos_col2 = (self.cf.pos_col20, self.cf.pos_col21, self.cf.pos_col22)
        self.std_neg_col2 = (self.cf.neg_col20, self.cf.neg_col21, self.cf.neg_col22)
        self.set_standard_colours()

    def load_file(self, fileName):
        self.nd.load(fileName)
        self.w.script.insertHtml(self.nd.script)
        self.w.console.insertHtml(self.nd.console)
        self.w.phRefDS.valueChanged.disconnect()
        self.w.phRefExp.valueChanged.disconnect()
        self.w.phRefDS.setValue(self.nd.nmrdat[0][0].display.ph_ref_ds)
        self.w.phRefDS.valueChanged.connect(self.change_data_set_exp_ph_ref)
        self.w.phRefExp.valueChanged.connect(self.change_data_set_exp_ph_ref)
        self.w.phRefExp.setValue(self.nd.nmrdat[0][0].display.ph_ref_exp)
        self.reset_plot()
        self.update_gui()
        self.w.console.verticalScrollBar().setValue(self.w.console.verticalScrollBar().maximum())
        self.show_title_file_information()
        self.show_acquisition_parameters()
        self.set_hsqc()
        self.show_nmr_spectrum()
        # end load_file

    def load_light_mode(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].display.pos_col_rgb = self.std_pos_col1
            self.nd.nmrdat[self.nd.s][k].display.neg_col_rgb = self.std_neg_col1

        idx = self.w.helpComboBox.currentIndex()
        url = []
        f_name = os.path.join(os.path.dirname(__file__), "web", "index.html")
        url.append("file:///" + f_name.replace('\\', '/'))
        url.append("http://www.bml-nmr.org")
        url.append("https://www.hmdb.ca")
        url.append("https://www.smpdb.ca")
        url.append("https://bmrb.io/metabolomics/")
        url.append("https://www.genome.jp/kegg/pathway.html#metabolism")
        url.append("https://nmrshiftdb.nmr.uni-koeln.de")
        url.append("https://sdbs.db.aist.go.jp/sdbs/cgi-bin/cre_index.cgi")
        url.append("http://dmar.riken.jp/spincouple/")
        self.w.helpView.setUrl(url[idx])
        bg = (255 / 255, 255 / 255, 255 / 255)
        fg = (0 / 255, 0 / 255, 0 / 255)
        self.w.MplWidget.canvas.figure.set_facecolor(bg)
        self.w.MplWidget.canvas.axes.set_facecolor(bg)
        self.w.MplWidget.canvas.axes.xaxis.label.set_color(fg)
        self.w.MplWidget.canvas.axes.yaxis.label.set_color(fg)
        self.w.MplWidget.canvas.axes.tick_params(axis='x', colors=fg)
        self.w.MplWidget.canvas.axes.tick_params(axis='y', colors=fg)
        self.w.MplWidget.canvas.axes.spines['bottom'].set_color(fg)
        self.w.MplWidget.canvas.axes.spines['top'].set_color(fg)
        self.w.MplWidget.canvas.axes.spines['left'].set_color(fg)
        self.w.MplWidget.canvas.axes.spines['right'].set_color(fg)
        self.w.hsqcMultiplet.canvas.figure.set_facecolor(bg)
        self.w.hsqcMultiplet.canvas.axes.set_facecolor(bg)
        self.w.hsqcMultiplet.canvas.axes.xaxis.label.set_color(fg)
        self.w.hsqcMultiplet.canvas.axes.yaxis.label.set_color(fg)
        self.w.hsqcMultiplet.canvas.axes.tick_params(axis='x', colors=fg)
        self.w.hsqcMultiplet.canvas.axes.tick_params(axis='y', colors=fg)
        self.w.hsqcMultiplet.canvas.axes.spines['bottom'].set_color(fg)
        self.w.hsqcMultiplet.canvas.axes.spines['top'].set_color(fg)
        self.w.hsqcMultiplet.canvas.axes.spines['left'].set_color(fg)
        self.w.hsqcMultiplet.canvas.axes.spines['right'].set_color(fg)
        self.w.hsqcPeak.canvas.figure.set_facecolor(bg)
        self.w.hsqcPeak.canvas.axes.set_facecolor(bg)
        self.w.hsqcPeak.canvas.axes.xaxis.label.set_color(fg)
        self.w.hsqcPeak.canvas.axes.yaxis.label.set_color(fg)
        self.w.hsqcPeak.canvas.axes.tick_params(axis='x', colors=fg)
        self.w.hsqcPeak.canvas.axes.tick_params(axis='y', colors=fg)
        self.w.hsqcPeak.canvas.axes.spines['bottom'].set_color(fg)
        self.w.hsqcPeak.canvas.axes.spines['top'].set_color(fg)
        self.w.hsqcPeak.canvas.axes.spines['left'].set_color(fg)
        self.w.hsqcPeak.canvas.axes.spines['right'].set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.figure.set_facecolor(bg)
        # self.w.isotopomerHsqcPeak.canvas.axes.set_facecolor(bg)
        # self.w.isotopomerHsqcPeak.canvas.axes.xaxis.label.set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.yaxis.label.set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.tick_params(axis='x', colors=fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.tick_params(axis='y', colors=fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.spines['bottom'].set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.spines['top'].set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.spines['left'].set_color(fg)
        # self.w.isotopomerHsqcPeak.canvas.axes.spines['right'].set_color(fg)
        # self.w.isotopomerMultiplet.canvas.figure.set_facecolor(bg)
        # self.w.isotopomerMultiplet.canvas.axes.set_facecolor(bg)
        # self.w.isotopomerMultiplet.canvas.axes.xaxis.label.set_color(fg)
        # self.w.isotopomerMultiplet.canvas.axes.yaxis.label.set_color(fg)
        # self.w.isotopomerMultiplet.canvas.axes.tick_params(axis='x', colors=fg)
        # self.w.isotopomerMultiplet.canvas.axes.tick_params(axis='y', colors=fg)
        # self.w.isotopomerMultiplet.canvas.axes.spines['bottom'].set_color(fg)
        # self.w.isotopomerMultiplet.canvas.axes.spines['top'].set_color(fg)
        # self.w.isotopomerMultiplet.canvas.axes.spines['left'].set_color(fg)
        # self.w.isotopomerMultiplet.canvas.axes.spines['right'].set_color(fg)
        # end load_light_mode

    def ma_fit_hsqc_1d(self):
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        print(f'fitting multiplet...')
        fit_again_counter = 0
        auto_scale = self.w.maAutoScale.isChecked()
        if self.w.maAutoScale.isChecked():
            self.w.maAutoScale.setChecked(False)

        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        if hsqc.hsqc_data[hsqc.cur_metabolite].spin_systems[hsqc.cur_peak - 1]['contribution'][0] == 100.0:
            self.nd.nmrdat[self.nd.s][self.nd.e].fit_hsqc_1d()

        self.nd.nmrdat[self.nd.s][self.nd.e].fit_hsqc_1d()
        while self.nd.nmrdat[self.nd.s][self.nd.e].fit_hsqc_again:
            if fit_again_counter < self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.n_max:
                fit_again_counter += 1
                print(f'self.nd.nmrdat[{self.nd.s}][{self.nd.e}].fit_hsqc[iteration: {fit_again_counter}]: '
                      f'{self.nd.nmrdat[self.nd.s][self.nd.e].fit_hsqc_again}')
                self.nd.nmrdat[self.nd.s][self.nd.e].fit_hsqc_again = False
                self.nd.nmrdat[self.nd.s][self.nd.e].fit_hsqc_1d()
            else:
                self.nd.nmrdat[self.nd.s][self.nd.e].fit_hsqc_again = False

        # self.hsqc_spin_sys_change()
        self.w.maAutoScale.setChecked(auto_scale)
        self.ma_sim_hsqc_1d()
        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        code_out.close()
        code_err.close()
        self.w.console.verticalScrollBar().setValue(self.w.console.verticalScrollBar().maximum())
        # end ma_fit_hsqc_1d

    def ma_sim_hsqc_1d(self):
        if self.nd.hsqc_spin_sys_connected == True:
            self.w.hsqcSpinSys.cellChanged.disconnect()
            self.nd.hsqc_spin_sys_connected = False

        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        if self.w.maAutoScale.isChecked():
            hsqc.hsqc_data[hsqc.cur_metabolite].intensities[hsqc.cur_peak - 1] = 1

        intensities = hsqc.hsqc_data[hsqc.cur_metabolite].intensities[hsqc.cur_peak - 1]
        self.nd.nmrdat[self.nd.s][self.nd.e].sim_hsqc_1d()
        self.w.multipletAnalysisIntensity.setText(
            str(hsqc.hsqc_data[hsqc.cur_metabolite].intensities[hsqc.cur_peak - 1]))
        if intensities == 1:
            self.nd.nmrdat[self.nd.s][self.nd.e].sim_hsqc_1d()

        self.plot_metabolite_peak(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak)
        if self.nd.hsqc_spin_sys_connected == False:
            self.w.hsqcSpinSys.cellChanged.connect(self.hsqc_spin_sys_change)
            self.nd.hsqc_spin_sys_connected = True

        # end ma_sim_hsqc_1d

    def metabolite_reset(self):
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite].h1_picked[
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak - 1] = []
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite].c13_picked[
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak - 1] = []
        self.plot_metabolite_peak(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak)
        # end metabolite_reset

    def next_command(self):
        if (self.w.cmdLine.hasFocus() == True):
            if (self.nd.cmd_idx < len(self.nd.cmd_buffer)):
                self.nd.cmd_idx += 1
                if (self.nd.cmd_idx == len(self.nd.cmd_buffer)):
                    self.w.cmdLine.setText("")
                else:
                    self.w.cmdLine.setText(self.nd.cmd_buffer[self.nd.cmd_idx])

        # end next_command

    def next_tab(self):
        cidx = self.w.nmrSpectrum.currentIndex()
        while self.w.nmrSpectrum.isTabEnabled(cidx + 1) is False and cidx < 11:
            cidx += 1

        if cidx < 12:
            self.w.nmrSpectrum.setCurrentIndex(cidx + 1)
        else:
            self.w.nmrSpectrum.setCurrentIndex(0)

        # end next_tab

    def previous_tab(self):
        cidx = self.w.nmrSpectrum.currentIndex()
        while self.w.nmrSpectrum.isTabEnabled(cidx - 1) is False and cidx > 1:
            cidx -= 1

        if cidx > 0:
            self.w.nmrSpectrum.setCurrentIndex(cidx - 1)
            self.w.nmrSpectrum.setFocus()
        else:
            self.w.nmrSpectrum.setCurrentIndex(12)

        # end previous_tab

    def on_ph_corr_click(self, event):
        s = self.nd.s
        e = self.nd.e
        if (self.zoom == False):
            self.ph_corr.spc = self.nd.nmrdat[s][e].spc
            self.ph_corr.spc_max = max(max(abs(self.ph_corr.spc)))
            # self.w.MplWidget.canvas.toolbar._zoom_mode.__init__()
            if (event.button == 1):
                mods = QApplication.queryKeyboardModifiers()
                if (mods == QtCore.Qt.ControlModifier):
                    # set pivot for phase correction
                    self.ph_corr.start = event.xdata
                    self.ph_corr.pivot = event.xdata
                    self.ph_corr.piv_points = self.nd.nmrdat[s][e].ppm2points(self.ph_corr.pivot, 0)

                if (mods == QtCore.Qt.ShiftModifier):
                    # first order phase correction
                    self.ph_corr.start = event.ydata

                if (mods == QtCore.Qt.NoModifier):
                    # zero order phase correction
                    self.ph_corr.start = event.ydata

                if (mods == QtCore.Qt.AltModifier):
                    self.w.MplWidget.canvas.manager.toolbar.zoom()

            else:
                if (event.button == 2):
                    # set pivot for phase correction
                    self.ph_corr.start = event.xdata
                    self.ph_corr.pivot = event.xdata
                    self.ph_corr.piv_points = self.nd.nmrdat[s][e].ppm2points(self.ph_corr.pivot, 0)
                else:
                    # first order phase correction
                    self.ph_corr.start = event.ydata

            cid3 = self.w.MplWidget.canvas.mpl_connect('motion_notify_event', self.on_ph_corr_draw)

        # end on_ph_corr_click

    def on_ph_corr_click_2d(self, event):
        s = self.nd.s
        e = self.nd.e
        if (self.zoom == False):
            self.ph_corr.spc2 = np.copy(self.ph_corr.spc)
            # self.ph_corr.spc = self.nd.nmrdat[s][e].spc
            # self.ph_corr.spc_max = max(max(abs(self.ph_corr.spc)))
            if (event.button == 1):
                mods = QApplication.queryKeyboardModifiers()
                if (mods == QtCore.Qt.ControlModifier):
                    # set pivot for phase correction
                    self.ph_corr.start = event.xdata
                    self.ph_corr.pivot = event.xdata
                    self.ph_corr.pivot_points2d[self.ph_corr.dim] = self.nd.nmrdat[s][e].ppm2points(
                        self.ph_corr.pivot2d[self.ph_corr.dim], self.ph_corr.dim)

                if (mods == QtCore.Qt.ShiftModifier):
                    # first order phase correction
                    self.ph_corr.start = event.ydata

                if (mods == QtCore.Qt.NoModifier):
                    # zero order phase correction
                    self.ph_corr.start = event.ydata

                if (mods == QtCore.Qt.AltModifier):
                    self.w.MplWidget.canvas.manager.toolbar.zoom()

            else:
                if (event.button == 2):
                    # set pivot for phase correction
                    self.ph_corr.start = event.xdata
                    self.ph_corr.pivot2d[self.ph_corr.dim] = event.xdata
                    self.ph_corr.pivot_points2d[self.ph_corr.dim] = self.nd.nmrdat[s][e].ppm2points(
                        self.ph_corr.pivot2d[self.ph_corr.dim], self.ph_corr.dim)
                else:
                    # first order phase correction
                    self.ph_corr.start = event.ydata

            cid3 = self.w.MplWidget.canvas.mpl_connect('motion_notify_event', self.on_ph_corr_draw2d)

        # end on_ph_corr_click_2d

    def on_ph_corr_draw(self, event):
        if (self.zoom == False):
            s = self.nd.s
            e = self.nd.e
            if ((event.xdata != None) & (event.ydata != None)):
                self.ph_corr.x_data = event.xdata
                self.ph_corr.y_data = event.ydata
                if (event.button == 1):
                    mods = QApplication.queryKeyboardModifiers()
                    if (mods == QtCore.Qt.ControlModifier):
                        # set pivot for phase correction
                        self.ph_corr.pivot = event.xdata
                        self.ph_corr.piv_points = self.nd.nmrdat[s][e].ppm2points(self.ph_corr.pivot, 0)

                    if (mods == QtCore.Qt.ShiftModifier):
                        # first order phase correction
                        ph0 = 0
                        ph1 = - self.ph_corr.max_ph1 * (event.ydata - self.ph_corr.start) / self.ph_corr.spc_max
                        self.ph_corr.spc = self.phase1d(self.nd.nmrdat[s][e].spc, ph0, ph1, self.ph_corr.piv_points)

                    if (mods == QtCore.Qt.NoModifier):
                        # zero order phase correction
                        ph0 = self.ph_corr.max_ph0 * (event.ydata - self.ph_corr.start) / self.ph_corr.spc_max
                        ph1 = 0
                        self.ph_corr.spc = self.phase1d(self.nd.nmrdat[s][e].spc, ph0, ph1, self.ph_corr.piv_points)

                else:
                    if (event.button == 2):
                        # set pivot for phase correction
                        self.ph_corr.x_data = event.xdata
                        self.ph_corr.y_data = event.ydata
                        self.ph_corr.pivot = event.xdata
                        self.ph_corr.piv_points = self.nd.nmrdat[s][e].ppm2points(self.ph_corr.pivot, 0)
                    else:
                        # first order phase correction
                        self.ph_corr.x_data = event.xdata
                        self.ph_corr.y_data = event.ydata
                        ph0 = 0
                        ph1 = - self.ph_corr.max_ph1 * (event.ydata - self.ph_corr.start) / self.ph_corr.spc_max
                        self.ph_corr.spc = self.phase1d(self.nd.nmrdat[s][e].spc, ph0, ph1, self.ph_corr.piv_points)

            self.ph_corr_plot_spc()

        # end on_ph_corr_draw

    def on_ph_corr_draw2d(self, event):
        if (self.zoom == False):
            s = self.nd.s
            e = self.nd.e
            if ((event.xdata != None) & (event.ydata != None)):
                self.ph_corr.x_data = event.xdata
                self.ph_corr.y_data = event.ydata
                if (event.button == 1):
                    mods = QApplication.queryKeyboardModifiers()
                    if (mods == QtCore.Qt.ControlModifier):
                        # set pivot for phase correction
                        self.ph_corr.pivot2d[self.ph_corr.dim] = event.xdata
                        self.ph_corr.pivot_points2d[self.ph_corr.dim] = self.nd.nmrdat[s][e].ppm2points(
                            self.ph_corr.pivot2d[self.ph_corr.dim], self.ph_corr.dim)

                    if (mods == QtCore.Qt.ShiftModifier):
                        # first order phase correction
                        ph0 = 0
                        if self.ph_corr.dim == 0:
                            ph1 = self.ph_corr.max_ph1 * (event.ydata - self.ph_corr.start) / self.ph_corr.spc_max
                        else:
                            ph1 = - self.ph_corr.max_ph1 * (event.ydata - self.ph_corr.start) / self.ph_corr.spc_max

                        self.ph_corr.spc = self.phase1d(self.ph_corr.spc2, ph0, ph1,
                                                        self.ph_corr.pivot_points2d[self.ph_corr.dim])

                    if (mods == QtCore.Qt.NoModifier):
                        # zero order phase correction
                        if self.ph_corr.dim == 0:
                            ph0 = - self.ph_corr.max_ph0 * (event.ydata - self.ph_corr.start) / self.ph_corr.spc_max
                        else:
                            ph0 = self.ph_corr.max_ph0 * (event.ydata - self.ph_corr.start) / self.ph_corr.spc_max

                        ph1 = 0
                        self.ph_corr.spc = self.phase1d(self.ph_corr.spc2, ph0, ph1,
                                                        self.ph_corr.pivot_points2d[self.ph_corr.dim])

                else:
                    if (event.button == 2):
                        # set pivot for phase correction
                        self.ph_corr.x_data = event.xdata
                        self.ph_corr.y_data = event.ydata
                        self.ph_corr.pivot2d[self.ph_corr.dim] = event.xdata
                        self.ph_corr.pivot_points2d[self.ph_corr.dim] = self.nd.nmrdat[s][e].ppm2points(
                            self.ph_corr.pivot2d[self.ph_corr.dim], self.ph_corr.dim)
                    else:
                        # first order phase correction
                        self.ph_corr.x_data = event.xdata
                        self.ph_corr.y_data = event.ydata
                        ph0 = 0
                        if self.ph_corr.dim == 0:
                            ph1 = self.ph_corr.max_ph1 * (event.ydata - self.ph_corr.start) / self.ph_corr.spc_max
                        else:
                            ph1 = - self.ph_corr.max_ph1 * (event.ydata - self.ph_corr.start) / self.ph_corr.spc_max

                        self.ph_corr.spc = self.phase1d(self.ph_corr.spc2, ph0, ph1,
                                                        self.ph_corr.pivot_points2d[self.ph_corr.dim])

            self.ph_corr_plot_spc_2d()

        # end on_ph_corr_drawd

    def on_ph_corr_release(self, event):
        s = self.nd.s
        e = self.nd.e
        if ((event.xdata != None) & (event.ydata != None)):
            xdata = event.xdata
            ydata = event.ydata
        else:
            xdata = self.ph_corr.x_data
            ydata = self.ph_corr.y_data

        if (self.zoom == False):
            if (event.button == 1):
                mods = QApplication.queryKeyboardModifiers()
                if (mods == QtCore.Qt.ControlModifier):
                    # set pivot for phase correction
                    self.ph_corr.pivot = xdata
                    self.ph_corr.piv_points = self.nd.nmrdat[s][e].ppm2points(self.ph_corr.pivot, 0)

                if (mods == QtCore.Qt.ShiftModifier):
                    # first order phase correction
                    ph1 = - (self.ph_corr.max_ph1 * (ydata - self.ph_corr.start) / self.ph_corr.spc_max)
                    ph = self.phases_remove_pivot(0.0, ph1, self.ph_corr.piv_points, len(self.ph_corr.spc[0]))
                    ph0 = ((self.nd.nmrdat[s][e].proc.ph0[0] + ph[0] + 180.0) % 360.0) - 180.0
                    ph1 = self.nd.nmrdat[s][e].proc.ph1[0] + ph[1]
                    self.nd.nmrdat[s][e].proc.ph0[0] = ph0
                    self.nd.nmrdat[s][e].proc.ph1[0] = ph1

                if (mods == QtCore.Qt.NoModifier):
                    # zero order phase correction
                    ph0a = (self.ph_corr.max_ph0 * (ydata - self.ph_corr.start) / self.ph_corr.spc_max) % 360.0
                    ph1a = 0.0
                    ph = self.phases_remove_pivot(ph0a, ph1a, self.ph_corr.piv_points, len(self.ph_corr.spc[0]))
                    ph0 = ((self.nd.nmrdat[s][e].proc.ph0[0] + ph[0] + 180.0) % 360.0) - 180.0
                    ph1 = self.nd.nmrdat[s][e].proc.ph1[0] + ph[1]
                    self.nd.nmrdat[s][e].proc.ph0[0] = ph0
                    self.nd.nmrdat[s][e].proc.ph1[0] = ph1

            else:
                if (event.button == 2):
                    # set pivot for phase correction
                    self.ph_corr.pivot = xdata
                    self.ph_corr.piv_points = self.nd.nmrdat[s][e].ppm2points(self.ph_corr.pivot, 0)
                else:
                    # first order phase correction
                    ph1 = - (self.ph_corr.max_ph1 * (ydata - self.ph_corr.start) / self.ph_corr.spc_max)
                    ph = self.phases_remove_pivot(0.0, ph1, self.ph_corr.piv_points, len(self.ph_corr.spc[0]))
                    ph0 = ((self.nd.nmrdat[s][e].proc.ph0[0] + ph[0] + 180.0) % 360.0) - 180.0
                    ph1 = self.nd.nmrdat[s][e].proc.ph1[0] + ph[1]
                    self.nd.nmrdat[s][e].proc.ph0[0] = ph0
                    self.nd.nmrdat[s][e].proc.ph1[0] = ph1

            cid3 = self.w.MplWidget.canvas.mpl_connect('motion_notify_event', self.on_ph_corr_draw)
            cid3 = self.w.MplWidget.canvas.mpl_disconnect(cid3)
            self.nd.nmrdat[s][e].spc = self.ph_corr.spc
            self.set_proc_pars()
            self.nd.ft()
            self.ph_corr_plot_spc()
        else:
            # zoom mode activated
            if (event.button > 1):
                # Right MB click will unzoom the plot
                try:
                    self.w.MplWidget.canvas.figure.canvas.toolbar.home()
                except:
                    pass

        # end on_ph_corr_release

    def on_ph_corr_release_2d(self, event):
        s = self.nd.s
        e = self.nd.e
        if ((event.xdata != None) & (event.ydata != None)):
            xdata = event.xdata
            ydata = event.ydata
        else:
            xdata = self.ph_corr.x_data
            ydata = self.ph_corr.y_data

        if (self.zoom == False):
            if event.button == 1:
                mods = QApplication.queryKeyboardModifiers()
                if mods == QtCore.Qt.ControlModifier:
                    # set pivot for phase correction
                    self.ph_corr.pivot2d[self.ph_corr.dim] = xdata
                    self.ph_corr.pivot_points2d[self.ph_corr.dim] = self.nd.nmrdat[s][e].ppm2points(
                        self.ph_corr.pivot2d[self.ph_corr.dim], self.ph_corr.dim)

                if mods == QtCore.Qt.ShiftModifier:
                    # first order phase correction
                    if self.ph_corr.dim == 0:
                        ph1 = (self.ph_corr.max_ph1 * (ydata - self.ph_corr.start) / self.ph_corr.spc_max)
                    else:
                        ph1 = - (self.ph_corr.max_ph1 * (ydata - self.ph_corr.start) / self.ph_corr.spc_max)

                    ph = self.phases_remove_pivot(0.0, ph1, self.ph_corr.pivot_points2d[self.ph_corr.dim],
                                                  len(self.ph_corr.spc[0]))
                    ph0 = ((self.ph_corr.ph0_2d[self.ph_corr.dim] + ph[0] + 180.0) % 360.0) - 180.0
                    ph1 = self.ph_corr.ph1_2d[self.ph_corr.dim] + ph[1]
                    self.ph_corr.ph0_2d[self.ph_corr.dim] = ph0
                    self.ph_corr.ph1_2d[self.ph_corr.dim] = ph1

                if mods == QtCore.Qt.NoModifier:
                    # zero order phase correction
                    if self.ph_corr.dim == 0:
                        ph0a = - (self.ph_corr.max_ph0 * (ydata - self.ph_corr.start) / self.ph_corr.spc_max) % 360.0
                    else:
                        ph0a = (self.ph_corr.max_ph0 * (ydata - self.ph_corr.start) / self.ph_corr.spc_max) % 360.0

                    ph1a = 0.0
                    ph = self.phases_remove_pivot(ph0a, ph1a, self.ph_corr.pivot_points2d[self.ph_corr.dim],
                                                  len(self.ph_corr.spc[0]))
                    ph0 = ((self.ph_corr.ph0_2d[self.ph_corr.dim] + ph[0] + 180.0) % 360.0) - 180.0
                    ph1 = self.ph_corr.ph1_2d[self.ph_corr.dim] + ph[1]
                    self.ph_corr.ph0_2d[self.ph_corr.dim] = ph0
                    self.ph_corr.ph1_2d[self.ph_corr.dim] = ph1

            else:
                if event.button == 2:
                    # set pivot for phase correction
                    self.ph_corr.pivot2d[self.ph_corr.dim] = xdata
                    self.ph_corr.pivot_points2d[self.ph_corr.dim] = self.nd.nmrdat[s][e].ppm2points(
                        self.ph_corr.pivot2d[self.ph_corr.dim], self.ph_corr.dim)

                else:
                    # first order phase correction
                    if self.ph_corr.dim == 0:
                        ph1 = (self.ph_corr.max_ph1 * (ydata - self.ph_corr.start) / self.ph_corr.spc_max)
                    else:
                        ph1 = - (self.ph_corr.max_ph1 * (ydata - self.ph_corr.start) / self.ph_corr.spc_max)

                    ph = self.phases_remove_pivot(0.0, ph1, self.ph_corr.pivot_points2d[self.ph_corr.dim],
                                                  len(self.ph_corr.spc[0]))
                    ph0 = ((self.ph_corr.ph0_2d[self.ph_corr.dim] + ph[0] + 180.0) % 360.0) - 180.0
                    ph1 = self.ph_corr.ph1_2d[self.ph_corr.dim] + ph[1]
                    self.ph_corr.ph0_2d[self.ph_corr.dim] = ph0
                    self.ph_corr.ph1_2d[self.ph_corr.dim] = ph1

            cid3 = self.w.MplWidget.canvas.mpl_connect('motion_notify_event', self.on_ph_corr_draw2d)
            cid3 = self.w.MplWidget.canvas.mpl_disconnect(cid3)
            self.ph_corr.spc2 = np.copy(self.ph_corr.spc)
            self.ph_corr_plot_spc_2d()
        else:
            # zoom mode activated
            if (event.button > 1):
                # Right MB click will unzoom the plot
                try:
                    self.w.MplWidget.canvas.figure.canvas.toolbar.home()
                except:
                    pass

        # end on_ph_corr_release_2d

    def open_metabolite_web(self):
        current_text = self.w.openWeb.currentText()
        base_url = ''
        if current_text.find('HMDB') > -1:
            base_url = 'https://hmdb.ca/metabolites/'

        if current_text.find('SMP') > - 1:
            base_url = 'https://smpdb.ca/view/'

        self.html(base_url + current_text)
        # end open_metabolite_web

    def open_script(self, f_name=""):
        if (f_name == False):
            f_name = ""

        if (len(f_name) == 0):
            f_name = QFileDialog.getOpenFileName(None, 'Open Script File', '', 'Python files (*.py)')
            f_name = f_name[0]

        if (len(f_name) > 0):
            f = open(f_name, 'r')
            scriptText = f.read()
            self.w.script.setText(scriptText)

        self.w.nmrSpectrum.setCurrentIndex(9)
        # end open_script

    def p(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.pulse) - 1 or index < -1:
            index = -1

        if index == -1:
            print("p = {}".format(self.nd.nmrdat[self.nd.s][self.nd.e].acq.pulse))
        else:
            print("p{} = {}".format(index, self.nd.nmrdat[self.nd.s][self.nd.e].acq.pulse[index]))

        # end p

    def pcpd(self, index=-1):
        if index > len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.pcpd) - 1 or index < -1:
            index = -1

        if index == -1:
            print(f'pcpd = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.pcpd}')
        else:
            print(f'pcpd({index}) = {self.nd.nmrdat[self.nd.s][self.nd.e].acq.pcpd[index]}')

        # end pcpd

    def ph_corr_plot_spc(self):
        xlim = self.w.MplWidget.canvas.axes.get_xlim()
        ylim = self.w.MplWidget.canvas.axes.get_ylim()
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        if (d.pos_col == "RGB"):
            pos_col = d.pos_col_rgb
        else:
            pos_col = d.pos_col

        if (d.neg_col == "RGB"):
            neg_col = d.neg_col_rgb
        else:
            neg_col = d.neg_col

        ref_col = d.ph_ref_col
        pos_col = matplotlib.colors.to_hex(pos_col)
        neg_col = matplotlib.colors.to_hex(neg_col)
        ref_col = matplotlib.colors.to_hex(ref_col)
        xlabel = d.x_label + " [" + d.axis_type1 + "]"
        ylabel = d.y_label + " [" + d.axis_type2 + "]"
        if (self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1):
            self.w.MplWidget.canvas.axes.clear()
            if ((d.ph_ref_ds > 0) & (d.ph_ref_exp > 0) & (
                    ((d.ph_ref_ds - 1 == self.nd.s) & (d.ph_ref_exp - 1 == self.nd.e)) is False)):
                self.w.MplWidget.canvas.axes.plot(self.nd.nmrdat[d.ph_ref_ds - 1][d.ph_ref_exp - 1].ppm1,
                                                  self.nd.nmrdat[d.ph_ref_ds - 1][d.ph_ref_exp - 1].spc[0].real,
                                                  color=ref_col)

            self.w.MplWidget.canvas.axes.plot(self.nd.nmrdat[self.nd.s][self.nd.e].ppm1, self.ph_corr.spc[0].real,
                                              color=pos_col)
            self.w.MplWidget.canvas.axes.plot([self.ph_corr.pivot, self.ph_corr.pivot],
                                              [2.0 * self.ph_corr.spc_max, -2.0 * self.ph_corr.spc_max], color='r')
            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                bg = (42 / 255, 42 / 255, 42 / 255)
                fg = (255 / 255, 255 / 255, 255 / 255)
            else:
                bg = (255 / 255, 255 / 255, 255 / 255)
                fg = (0 / 255, 0 / 255, 0 / 255)

            self.w.MplWidget.canvas.axes.set_xlabel(xlabel, color=fg)
            ylabel = d.y_label
            self.w.MplWidget.canvas.axes.set_ylabel(ylabel, color=fg)
            self.w.MplWidget.canvas.axes.invert_xaxis()
            self.w.MplWidget.canvas.axes.set_xlim(xlim)
            self.w.MplWidget.canvas.axes.set_ylim(ylim)

        self.set_proc_pars()
        self.w.MplWidget.canvas.draw()
        # This is a messy solution to force the matplotlib widget to update the plot by introducing an error (calling
        # a figure object and redirecting the error output
        code_err = io.StringIO()
        sys.stderr = code_err
        try:
            self.w.MplWidget.canvas.figure()
        except:
            pass

        sys.stderr = sys.__stderr__
        # end ph_corr_plot_spc

    def ph_corr_plot_spc_2d(self, keep_zoom=True):
        if keep_zoom:
            xlim = self.w.MplWidget.canvas.axes.get_xlim()
            ylim = self.w.MplWidget.canvas.axes.get_ylim()

        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        self.w.MplWidget.canvas.axes.set_prop_cycle(None)
        if self.ph_corr.dim == 0:
            xlabel = d.x_label + " [" + d.axis_type1 + "]"
        else:
            xlabel = d.y_label + " [" + d.axis_type2 + "]"

        self.w.MplWidget.canvas.axes.clear()
        self.ph_corr.spc_max = 0.0
        for k in range(len(self.ph_corr.spc)):
            self.w.MplWidget.canvas.axes.plot(self.ph_corr.ppm, self.ph_corr.spc[k].real)
            self.ph_corr.spc_max = max(self.ph_corr.spc_max, np.max(np.max(np.abs(self.ph_corr.spc[k].real))))

        self.w.MplWidget.canvas.axes.invert_xaxis()
        if not keep_zoom:
            xlim = self.w.MplWidget.canvas.axes.get_xlim()
            ylim = self.w.MplWidget.canvas.axes.get_ylim()

        self.w.MplWidget.canvas.axes.plot(
            [self.ph_corr.pivot2d[self.ph_corr.dim], self.ph_corr.pivot2d[self.ph_corr.dim]],
            [2.0 * self.ph_corr.spc_max, -2.0 * self.ph_corr.spc_max], color='r')

        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            bg = (42 / 255, 42 / 255, 42 / 255)
            fg = (255 / 255, 255 / 255, 255 / 255)
        else:
            bg = (255 / 255, 255 / 255, 255 / 255)
            fg = (0 / 255, 0 / 255, 0 / 255)

        self.w.MplWidget.canvas.axes.set_xlabel(xlabel, color=fg)
        #cd cd self.w.MplWidget.canvas.axes.set_ylabel(ylabel, color=fg)
        self.w.MplWidget.canvas.axes.invert_xaxis()
        self.w.MplWidget.canvas.axes.set_xlim(xlim)
        self.w.MplWidget.canvas.axes.set_ylim(ylim)
        self.w.MplWidget.canvas.draw()
        # This is a messy solution to force the matplotlib widget to update the plot by introducing an error (calling
        # a figure object and redirecting the error output
        code_err = io.StringIO()
        sys.stderr = code_err
        try:
            self.w.MplWidget.canvas.figure()
        except:
            pass

        sys.stderr = sys.__stderr__
        # end ph_corr_plot_spc_2d

    def phase1d(self, mat, ph0, ph1, piv):
        npts = len(mat[0])
        ph0 = -ph0 * math.pi / 180.0
        ph1 = -ph1 * math.pi / 180.0
        frac = np.linspace(0, 1, npts) - float(npts - piv) / float(npts)
        ph = ph0 + frac * ph1
        mat = np.cos(ph) * mat.real + np.sin(ph) * mat.imag + 1j * (-np.sin(ph) * mat.real + np.cos(ph) * mat.imag)
        return mat
        # end phase1d

    def phases_remove_pivot(self, phc0, phc1, piv, npts):
        phases = np.array([0.0, 0.0])
        frac = np.linspace(0, 1, npts) - float(npts - piv) / float(npts)
        ph = -phc0 - frac * phc1
        phases[0] = -ph[0]
        phases[1] = ph[0] - ph[len(ph) - 1]
        return phases
        # end phases_remove_pivot

    def pick_col_row(self):
        self.w.statusBar().clearMessage()
        self.w.statusBar().showMessage("Click to add row/col")
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        self.ginput2d()
        # end pick_col_row

    def plot_2d_col_row(self):
        while len(self.w.MplWidget.canvas.axes.lines) > 0:
            self.w.MplWidget.canvas.axes.lines[0].remove()

        self.w.MplWidget.canvas.axes.set_prop_cycle(None)
        ppm1 = self.nd.nmrdat[self.nd.s][self.nd.e].ppm1
        ppm2 = self.nd.nmrdat[self.nd.s][self.nd.e].ppm2
        for k in range(len(self.ph_corr.spc_row)):
            pid = self.w.MplWidget.canvas.axes.plot([self.ph_corr.spc_col[k], self.ph_corr.spc_col[k]],
                                                    [np.min(ppm2), np.max(ppm2)])
            self.w.MplWidget.canvas.axes.plot([np.min(ppm1), np.max(ppm1)],
                                              [self.ph_corr.spc_row[k], self.ph_corr.spc_row[k]],
                                              color=pid[0].get_color())

        self.w.MplWidget.canvas.draw()

    def plot_metabolite_peak(self, spin_number=0):
        if spin_number == 0:
            return

        if self.nd.hsqc_spin_sys_connected == True:
            self.w.hsqcSpinSys.cellChanged.disconnect()
            self.nd.hsqc_spin_sys_connected = False

        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak = spin_number
        metabolite_name = self.w.hsqcAssignedMetabolites.currentIndex().data()
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite = metabolite_name
        my_autosim = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim
        if metabolite_name in self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data.keys():
            if len(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].c13_picked[
                       spin_number - 1]) == 0:
                self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim = False

        self.w.fitUpToBonds.setCurrentIndex(
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].n_bonds)
        self.w.multipletAnalysisIntensity.setText(
            str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].intensities[spin_number - 1]))
        self.w.multipletAnalysisR2.setText(
            str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].r2[spin_number - 1]))
        self.w.multipletAnalysisEchoTime.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.echo_time))
        hd = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name]
        h1_shift = hd.h1_shifts[spin_number - 1]
        # print(hd.c13_shifts[np.where(hd.hsqc == 1)[0]])
        # c13_shifts = hd.c13_shifts[np.where(hd.hsqc == 1)[0]]
        c13_shift = hd.c13_shifts[hd.h1_index[spin_number - 1] - 1]
        h1_picked = hd.h1_picked[spin_number - 1]
        c13_picked = hd.c13_picked[spin_number - 1]
        if len(c13_picked) > 0:
            h1_centre = np.mean(h1_picked)
            c13_centre = np.mean(c13_picked)
        else:
            h1_centre = h1_shift
            c13_centre = c13_shift

        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autoscale_j == True:
            scale = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.j_scale
        else:
            scale = 1.0

        hsqc_idx = np.where(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].hsqc == 1)[0]
        h1_index = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].h1_index[spin_number - 1]
        c13_index = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].c13_index[
            hd.h1_index[spin_number - 1] - 1]
        h1_suffix = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].h1_suffix[spin_number - 1]
        h1_beg = h1_centre + self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.range_h
        h1_end = h1_centre - self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.range_h
        c13_beg = c13_centre + self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.range_c * scale
        c13_end = c13_centre - self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.range_c * scale
        h1_pts = len(self.nd.nmrdat[self.nd.s][self.nd.e].spc[0])
        c13_pts = len(self.nd.nmrdat[self.nd.s][self.nd.e].spc)
        h1_pts1 = h1_pts - self.nd.nmrdat[self.nd.s][self.nd.e].ppm2points(h1_beg, 0) - 1
        h1_pts2 = h1_pts - self.nd.nmrdat[self.nd.s][self.nd.e].ppm2points(h1_end, 0) - 1
        c13_pts1 = c13_pts - self.nd.nmrdat[self.nd.s][self.nd.e].ppm2points(c13_beg, 1) - 1
        c13_pts2 = c13_pts - self.nd.nmrdat[self.nd.s][self.nd.e].ppm2points(c13_end, 1) - 1
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        if d.pos_col == "RGB":
            pos_col = d.pos_col_rgb
        else:
            pos_col = d.pos_col

        if d.neg_col == "RGB":
            neg_col = d.neg_col_rgb
        else:
            neg_col = d.neg_col

        pos_col = matplotlib.colors.to_hex(pos_col)
        neg_col = matplotlib.colors.to_hex(neg_col)
        xlabel = d.x_label + " C" + str(c13_index) + "H" + str(h1_index) + h1_suffix + " [" + d.axis_type1 + "]"
        ylabel = d.y_label + " C" + str(c13_index) + "H" + str(h1_index) + h1_suffix + " [" + d.axis_type2 + "]"
        mm = np.max(np.abs(self.nd.nmrdat[self.nd.s][self.nd.e].spc.real))
        pos_lev = np.linspace(d.min_level * mm, d.max_level * mm, d.n_levels)
        neg_lev = np.linspace(-d.max_level * mm, -d.min_level * mm, d.n_levels)
        self.w.hsqcPeak.canvas.axes.clear()
        self.w.hsqcPeak.canvas.axes.contour(self.nd.nmrdat[self.nd.s][self.nd.e].ppm1[h1_pts1:h1_pts2],
                                            self.nd.nmrdat[self.nd.s][self.nd.e].ppm2[c13_pts1:c13_pts2],
                                            self.nd.nmrdat[self.nd.s][self.nd.e].spc[c13_pts1:c13_pts2,
                                            h1_pts1:h1_pts2].real, pos_lev, colors=pos_col,
                                            linestyles='solid', antialiased=True)
        self.w.hsqcPeak.canvas.axes.contour(self.nd.nmrdat[self.nd.s][self.nd.e].ppm1[h1_pts1:h1_pts2],
                                            self.nd.nmrdat[self.nd.s][self.nd.e].ppm2[c13_pts1:c13_pts2],
                                            self.nd.nmrdat[self.nd.s][self.nd.e].spc.real[c13_pts1:c13_pts2,
                                            h1_pts1:h1_pts2], neg_lev, colors=neg_col,
                                            linestyles='solid', antialiased=True)
        self.w.hsqcPeak.canvas.axes.autoscale()
        self.w.hsqcPeak.canvas.axes.invert_xaxis()
        self.w.hsqcPeak.canvas.axes.invert_yaxis()
        xlim = self.w.hsqcPeak.canvas.axes.get_xlim()
        ylim = self.w.hsqcPeak.canvas.axes.get_ylim()
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            col1 = 'w'
            col2 = 'yellow'
        else:
            col1 = 'k'
            col2 = 'r'

        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.display_library_shift == True:
            self.w.hsqcPeak.canvas.axes.plot([np.min(xlim), np.max(xlim)], [c13_shift, c13_shift], color=col1)
            self.w.hsqcPeak.canvas.axes.plot([h1_shift, h1_shift], [np.min(ylim), np.max(ylim)], color=col1)

        cur_peak = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak
        cur_metabolite = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite
        h1_picked = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[cur_metabolite].h1_picked
        c13_picked = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[cur_metabolite].c13_picked
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.display_peaks_of_metabolite == True:
            if len(h1_picked[spin_number - 1]) > 0:
                xdata = h1_picked[spin_number - 1]
                ydata = c13_picked[spin_number - 1]
                delta_x = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.range_h
                delta_y = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.range_c * scale
                factor = 0.05
                for k in range(len(xdata)):
                    self.w.hsqcPeak.canvas.axes.plot([xdata[k] - factor * delta_x, xdata[k] + factor * delta_x],
                                                     [ydata[k], ydata[k]], color=col2, linewidth=4)
                    self.w.hsqcPeak.canvas.axes.plot([xdata[k], xdata[k]],
                                                     [ydata[k] - factor * delta_y, ydata[k] + factor * delta_y],
                                                     color=col2, linewidth=4)

        if len(h1_picked[spin_number - 1]) == 1:
            xlabel += " (Peak {}, {} signal picked)".format(spin_number, len(h1_picked[spin_number - 1]))
        else:
            xlabel += " (Peak {}, {} signals picked)".format(spin_number, len(h1_picked[spin_number - 1]))

        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            bg = (42 / 255, 42 / 255, 42 / 255)
            fg = (255 / 255, 255 / 255, 255 / 255)
        else:
            bg = (255 / 255, 255 / 255, 255 / 255)
            fg = (0 / 255, 0 / 255, 0 / 255)

        self.w.hsqcPeak.canvas.axes.set_xlabel(xlabel, color=fg)
        self.w.hsqcPeak.canvas.axes.set_ylabel(ylabel, color=fg)
        self.w.hsqcPeak.canvas.draw()
        self.w.hsqcMultiplet.canvas.axes.clear()
        if len(h1_picked[spin_number - 1]) > 0:
            h1_pos = np.mean(h1_picked[spin_number - 1])
        else:
            h1_pos = h1_shift

        h1_pts = len(self.nd.nmrdat[self.nd.s][self.nd.e].spc[0]) - self.nd.nmrdat[self.nd.s][self.nd.e].ppm2points(
            h1_pos, 0) - 1
        self.w.hsqcMultiplet.canvas.axes.plot(self.nd.nmrdat[self.nd.s][self.nd.e].ppm2[c13_pts1:c13_pts2],
                                              self.nd.nmrdat[self.nd.s][self.nd.e].spc.real[c13_pts1:c13_pts2, h1_pts],
                                              color=col1, linewidth=2)
        if len(hd.sim_spc[spin_number - 1]) > 0:
            self.w.hsqcMultiplet.canvas.axes.plot(self.nd.nmrdat[self.nd.s][self.nd.e].ppm2[c13_pts1:c13_pts2],
                                                  hd.sim_spc[spin_number - 1][c13_pts1:c13_pts2], color=col2,
                                                  linewidth=2)

        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            bg = (42 / 255, 42 / 255, 42 / 255)
            fg = (255 / 255, 255 / 255, 255 / 255)
        else:
            bg = (255 / 255, 255 / 255, 255 / 255)
            fg = (0 / 255, 0 / 255, 0 / 255)

        self.w.hsqcMultiplet.canvas.axes.set_xlabel(ylabel, color=fg)
        self.w.hsqcMultiplet.canvas.axes.autoscale()
        self.w.hsqcMultiplet.canvas.axes.invert_xaxis()
        self.w.hsqcMultiplet.canvas.draw()
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.set_peak_information()
        # self.clear_hsqc_spin_sys()
        self.set_hsqc_spin_sys()
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim:
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim = False
            self.ma_sim_hsqc_1d()
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim = True

        if self.nd.hsqc_spin_sys_connected == False:
            self.w.hsqcSpinSys.cellChanged.connect(self.hsqc_spin_sys_change)
            self.nd.hsqc_spin_sys_connected = True

        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim = my_autosim
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            n_colour = [180, 180, 180]
        else:
            n_colour = [0, 0, 0]

        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        if len(hsqc.hsqc_data[hsqc.cur_metabolite].sim_spc[hsqc.cur_peak - 1]) == 0:
            hsqc.hsqc_data[hsqc.cur_metabolite].cod[hsqc.cur_peak - 1] = -1

        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            if hsqc.hsqc_data[hsqc.cur_metabolite].cod[hsqc.cur_peak - 1] > hsqc.cod_high:
                colour = [0, 255, 0]
            elif hsqc.hsqc_data[hsqc.cur_metabolite].cod[hsqc.cur_peak - 1] == -1:
                colour = n_colour
            elif hsqc.hsqc_data[hsqc.cur_metabolite].cod[hsqc.cur_peak - 1] < hsqc.cod_low:
                colour = [255, 0, 0]
            else:
                colour = [255, 170, 0]

        else:
            if hsqc.hsqc_data[hsqc.cur_metabolite].cod[hsqc.cur_peak - 1] > hsqc.cod_high:
                colour = [0, 200, 0]
            elif hsqc.hsqc_data[hsqc.cur_metabolite].cod[hsqc.cur_peak - 1] == -1:
                colour = n_colour
            elif hsqc.hsqc_data[hsqc.cur_metabolite].cod[hsqc.cur_peak - 1] < hsqc.cod_low:
                colour = [200, 0, 0]
            else:
                colour = [200, 150, 0]

        self.w.coefficientOfDetermination.display(hsqc.hsqc_data[hsqc.cur_metabolite].cod[hsqc.cur_peak - 1])
        palette = self.w.coefficientOfDetermination.palette()
        # foreground color
        #palette.setColor(palette.windowText, QtGui.QColor(colour[0], colour[1], colour[2]))
        palette.setColor(palette.currentColorGroup(), QPalette.WindowText, QtGui.QColor(colour[0], colour[1], colour[2]))        # background color
        # palette.setColor(palette.Background, QtGui.QColor(colour[0], colour[1], colour[2]))
        # "light" border
        #palette.setColor(palette.Light, QtGui.QColor(colour[0], colour[1], colour[2]))
        palette.setColor(palette.currentColorGroup(), QPalette.Light, QtGui.QColor(colour[0], colour[1], colour[2]))        # "dark" border
        #palette.setColor(palette.Dark, QtGui.QColor(colour[0], colour[1], colour[2]))
        palette.setColor(palette.currentColorGroup(), QPalette.Dark, QtGui.QColor(colour[0], colour[1], colour[2]))
        self.w.coefficientOfDetermination.setPalette(palette)
        # end

    def plot_spc(self, hide_pre_processing=False, plot_spline_baseline=False, linewidth=1.5, keep_zoom=-1):
        s = self.nd.s
        e = self.nd.e
        self.keep_zoom = self.w.keepZoom.isChecked()
        xlim = self.w.MplWidget.canvas.axes.get_xlim()
        ylim = self.w.MplWidget.canvas.axes.get_ylim()
        self.w.nmrSpectrum.setCurrentIndex(0)
        if (len(self.nd.nmrdat[s]) == 0):
            return

        if (len(self.nd.nmrdat[s][e].spc) == 0):
            return

        d = self.nd.nmrdat[s][e].display
        if d.pos_col == "RGB":
            pos_col = d.pos_col_rgb
        else:
            pos_col = d.pos_col

        if d.neg_col == "RGB":
            neg_col = d.neg_col_rgb
        else:
            neg_col = d.neg_col

        pos_col = matplotlib.colors.to_hex(pos_col)
        neg_col = matplotlib.colors.to_hex(neg_col)
        xlabel = d.x_label + " [" + d.axis_type1 + "]"
        ylabel = d.y_label + " [" + d.axis_type2 + "]"
        # print(self.nd.nmrdat[self.nd.s][self.nd.e].dim)
        if self.nd.nmrdat[s][e].dim == 1:
            self.w.MplWidget.canvas.axes.clear()
            for s1 in range(len(self.nd.nmrdat)):
                for k in range(len(self.nd.nmrdat[s1])):
                    if k == e and s1 == s:
                        d = self.nd.nmrdat[s][e].display
                        if (d.pos_col == "RGB"):
                            pos_col = d.pos_col_rgb
                        else:
                            pos_col = d.pos_col

                        if (d.neg_col == "RGB"):
                            neg_col = d.neg_col_rgb
                        else:
                            neg_col = d.neg_col

                        pos_col = matplotlib.colors.to_hex(pos_col)
                        neg_col = matplotlib.colors.to_hex(neg_col)
                        xlabel = d.x_label + " [" + d.axis_type1 + "]"
                        ylabel = d.y_label + " [" + d.axis_type2 + "]"
                        self.w.MplWidget.canvas.axes.plot(self.nd.nmrdat[self.nd.s][self.nd.e].ppm1,
                                                          self.nd.nmrdat[self.nd.s][self.nd.e].spc[0].real,
                                                          color=pos_col, linewidth=linewidth)


                    if ((k != e) or (s1 != s)) and (self.nd.nmrdat[s1][k].display.display_spc == True):
                        #d = self.nd.nmrdat[s1][k].display
                        if self.nd.nmrdat[s1][k].display.pos_col == "RGB":
                            pos_col = self.nd.nmrdat[s1][k].display.pos_col_rgb
                        else:
                            pos_col = self.nd.nmrdat[s1][k].display.pos_col

                        if self.nd.nmrdat[s1][k].display.neg_col == "RGB":
                            neg_col = self.nd.nmrdat[s1][k].display.neg_col_rgb
                        else:
                            neg_col = self.nd.nmrdat[s1][k].display.neg_col

                        pos_col = matplotlib.colors.to_hex(pos_col)
                        neg_col = matplotlib.colors.to_hex(neg_col)
                        #print(f'Dataset: {s1}, Exp: {k}, pos_col: {pos_col}')
                        self.w.MplWidget.canvas.axes.plot(self.nd.nmrdat[s1][k].ppm1,
                                                          self.nd.nmrdat[s1][k].spc[0].real, color=pos_col, linewidth=linewidth)

                        if self.w.splinebaseline.isChecked() and s1 == s:
                            if len(self.nd.nmrdat[s][k].spline_baseline.baseline_points) > 0:
                                self.w.MplWidget.canvas.axes.plot(self.nd.nmrdat[s][k].spline_baseline.baseline_points,
                                                                  self.nd.nmrdat[s][k].spline_baseline.baseline_values, 'o', color="lightgreen")
                                if plot_spline_baseline:
                                    self.w.MplWidget.canvas.axes.plot(self.nd.nmrdat[s][k].ppm1,
                                                                      self.nd.nmrdat[s][k].calc_spline_baseline(),
                                                                      color="lightgreen", linewidth=linewidth)

            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                bg = (42 / 255, 42 / 255, 42 / 255)
                fg = (255 / 255, 255 / 255, 255 / 255)
            else:
                bg = (255 / 255, 255 / 255, 255 / 255)
                fg = (0 / 255, 0 / 255, 0 / 255)

            d = self.nd.nmrdat[s][e].display
            if (d.pos_col == "RGB"):
                pos_col = d.pos_col_rgb
            else:
                pos_col = d.pos_col

            if (d.neg_col == "RGB"):
                neg_col = d.neg_col_rgb
            else:
                neg_col = d.neg_col

            pos_col = matplotlib.colors.to_hex(pos_col)
            neg_col = matplotlib.colors.to_hex(neg_col)
            xlabel = d.x_label + " [" + d.axis_type1 + "]"
            ylabel = d.y_label + " [" + d.axis_type2 + "]"
            if len(self.nd.nmrdat[s][e].start_peak) > 0:
                if self.w.peakPicking.isChecked() == True:
                    for k in range(len(self.nd.nmrdat[s][e].start_peak)):
                        self.w.MplWidget.canvas.axes.axvspan(self.nd.nmrdat[s][e].start_peak[k],
                                                             self.nd.nmrdat[s][e].end_peak[k],
                                                             alpha=self.nd.pp.alpha, color=self.nd.pp.colour)

            self.w.MplWidget.canvas.axes.plot(self.nd.nmrdat[self.nd.s][self.nd.e].ppm1,
                                              self.nd.nmrdat[self.nd.s][self.nd.e].spc[0].real, color=pos_col, linewidth=linewidth)

            if self.w.splinebaseline.isChecked():
                if len(self.nd.nmrdat[s][k].spline_baseline.baseline_points) > 0:
                    self.w.MplWidget.canvas.axes.plot(self.nd.nmrdat[s][e].spline_baseline.baseline_points,
                                                      self.nd.nmrdat[s][e].spline_baseline.baseline_values, 'o', color="lightgreen")
                    if plot_spline_baseline:
                        baseline = self.nd.nmrdat[s][e].calc_spline_baseline()
                        self.w.MplWidget.canvas.axes.plot(self.nd.nmrdat[s][e].ppm1, baseline, color="lightgreen", linewidth=linewidth)

            self.w.MplWidget.canvas.axes.set_xlabel(xlabel, color=fg)
            ylabel = d.y_label
            self.w.MplWidget.canvas.axes.set_ylabel(ylabel, color=fg)
            self.w.MplWidget.canvas.axes.autoscale()
            self.w.MplWidget.canvas.axes.invert_xaxis()
            self.w.MplWidget.canvas.axes.tick_params(axis='y', colors=fg)
            if (self.keep_zoom == True):
                self.w.MplWidget.canvas.axes.set_xlim(xlim)
                self.w.MplWidget.canvas.axes.set_ylim(ylim)

            # self.w.MplWidget.canvas.toolbar.update()
            self.w.MplWidget.canvas.draw()
            if (self.keep_x_zoom == True):
                self.w.MplWidget.canvas.axes.set_xlim(xlim)
                self.vertical_auto_scale()
                self.keep_x_zoom = False

            if self.cf.plot_legend:
                self.show_legend()

        else:
            mm = np.max(np.abs(self.nd.nmrdat[self.nd.s][self.nd.e].spc.real))
            pos_lev = np.linspace(d.min_level * mm, d.max_level * mm, d.n_levels)
            neg_lev = np.linspace(-d.max_level * mm, -d.min_level * mm, d.n_levels)
            self.w.MplWidget.canvas.axes.clear()
            self.w.MplWidget.canvas.axes.contour(self.nd.nmrdat[self.nd.s][self.nd.e].ppm1,
                                                 self.nd.nmrdat[self.nd.s][self.nd.e].ppm2,
                                                 self.nd.nmrdat[self.nd.s][self.nd.e].spc.real, pos_lev, colors=pos_col,
                                                 linestyles='solid', antialiased=True, linewidths=linewidth)
            self.w.MplWidget.canvas.axes.contour(self.nd.nmrdat[self.nd.s][self.nd.e].ppm1,
                                                 self.nd.nmrdat[self.nd.s][self.nd.e].ppm2,
                                                 self.nd.nmrdat[self.nd.s][self.nd.e].spc.real, neg_lev, colors=neg_col,
                                                 linestyles='solid', antialiased=True, linewidths=linewidth)

            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                bg = (42 / 255, 42 / 255, 42 / 255)
                fg = (255 / 255, 255 / 255, 255 / 255)
            else:
                bg = (255 / 255, 255 / 255, 255 / 255)
                fg = (0 / 255, 0 / 255, 0 / 255)

            self.w.MplWidget.canvas.axes.set_xlabel(xlabel, color=fg)
            self.w.MplWidget.canvas.axes.set_ylabel(ylabel, color=fg)
            self.w.MplWidget.canvas.axes.autoscale()
            self.w.MplWidget.canvas.axes.invert_xaxis()
            self.w.MplWidget.canvas.axes.invert_yaxis()
            if (self.keep_zoom == True):
                self.w.MplWidget.canvas.axes.set_xlim(xlim)
                self.w.MplWidget.canvas.axes.set_ylim(ylim)
            else:
                if (self.keep_x_zoom == True):
                    self.w.MplWidget.canvas.axes.set_xlim(xlim)
                    self.keep_x_zoom = False

            # self.w.MplWidget.canvas.toolbar.update()
            self.w.MplWidget.canvas.draw()
            if self.w.displayLibraryShifts.isChecked():
                self.w.displayLibraryShifts.setChecked(False)
                self.w.displayLibraryShifts.setChecked(True)

            else:
                if self.w.displayAssignedMetabolites.isChecked():
                    self.w.displayAssignedMetabolites.setChecked(False)
                    self.w.displayAssignedMetabolites.setChecked(True)

                else:
                    if self.w.displaySelectedMetabolite.isChecked():
                        self.w.displaySelectedMetabolite(False)
                        self.w.displaySelectedMetabolite(True)

        self.keep_zoom = False
        if hide_pre_processing == False and self.w.peakPicking.isChecked() == False:
            if self.exited_peak_picking == False:
                # a = 3
                pyautogui.click(clicks=1)
            else:
                self.exited_peak_picking = True

        if keep_zoom != -1:
            self.w.keepZoom.setChecked(keep_zoom)

        # end plot_spc

    def plot_spc_disp(self):
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        if (self.ph_corr_active == False):
            self.plot_spc()
        else:
            self.ph_corr_plot_spc()

        # end plot_spc_disp

    def plot_spc_pre_proc(self):
        if (len(self.nd.pp.class_select) == 0):
            self.nd.pre_proc_init()

        # self.w.rDolphinExport.setChecked(self.nd.pp.rDolphinExport)
        self.fill_pre_processing_numbers()
        sel = self.w.selectClassTW.selectedIndexes()
        cls = np.array([])
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            cls = np.append(cls, self.w.selectClassTW.item(k, 1).text())

        self.nd.pp.class_select = cls
        cls2 = np.unique(cls)
        sel2 = np.array([], dtype='int')
        for k in range(len(sel)):
            if (sel[k].column() == 0):
                sel2 = np.append(sel2, int(sel[k].row()))

        self.nd.pp.plot_select = sel2
        self.keep_zoom = self.w.keepZoom.isChecked()
        xlim = self.w.MplWidget.canvas.axes.get_xlim()
        ylim = self.w.MplWidget.canvas.axes.get_ylim()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.w.MplWidget.canvas.axes.clear()
        if (self.w.preProcessingWidget.currentIndex() == 1):
            for k in range(len(self.nd.pp.exclude_start)):
                self.w.MplWidget.canvas.axes.axvspan(self.nd.pp.exclude_start[k], self.nd.pp.exclude_end[k],
                                                     alpha=self.nd.pp.alpha, color=self.nd.pp.colour)

        if (self.w.preProcessingWidget.currentIndex() == 2):
            for k in range(len(self.nd.pp.seg_start)):
                self.w.MplWidget.canvas.axes.axvspan(self.nd.pp.seg_start[k], self.nd.pp.seg_end[k],
                                                     alpha=self.nd.pp.alpha, color=self.nd.pp.colour)

        for k in range(len(self.nd.pp.plot_select)):
            colIdx = np.where(cls2 == cls[self.nd.pp.plot_select[k]])[0][0]
            plotCol = matplotlib.colors.to_hex(self.nd.pp.plot_colours[colIdx])
            self.w.MplWidget.canvas.axes.plot(self.nd.nmrdat[self.nd.s][self.nd.pp.plot_select[k]].ppm1,
                                              self.nd.nmrdat[self.nd.s][self.nd.pp.plot_select[k]].spc[0].real,
                                              color=plotCol)

        if (self.w.preProcessingWidget.currentIndex() == 3):
            self.w.MplWidget.canvas.axes.axvspan(self.nd.pp.noise_start, self.nd.pp.noise_end, alpha=self.nd.pp.alpha,
                                                 color=self.nd.pp.colour)
            val = self.nd.pp.noise_threshold * self.nd.pp.std_val
            #print(f'noise_threshold: {self.nd.pp.noise_threshold}, std_val: {self.nd.pp.std_val}')
            x = [self.nd.nmrdat[self.nd.s][0].ppm1[0], self.nd.nmrdat[self.nd.s][0].ppm1[-1]]
            y = [val, val]
            self.w.MplWidget.canvas.axes.plot(x, y, color=self.nd.pp.th_colour, linewidth=self.nd.pp.th_line_width)

        if (self.w.preProcessingWidget.currentIndex() == 5):
            for k in range(len(self.nd.pp.compress_start)):
                self.w.MplWidget.canvas.axes.axvspan(self.nd.pp.compress_start[k], self.nd.pp.compress_end[k],
                                                     alpha=self.nd.pp.alpha, color=self.nd.pp.colour)

        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        xlabel = d.x_label + " [" + d.axis_type1 + "]"
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            bg = (42 / 255, 42 / 255, 42 / 255)
            fg = (255 / 255, 255 / 255, 255 / 255)
        else:
            bg = (255 / 255, 255 / 255, 255 / 255)
            fg = (0 / 255, 0 / 255, 0 / 255)

        self.w.MplWidget.canvas.axes.set_xlabel(xlabel, color=fg)
        self.w.MplWidget.canvas.axes.autoscale()
        self.w.MplWidget.canvas.axes.invert_xaxis()
        if (self.keep_zoom == True):
            self.w.MplWidget.canvas.axes.set_xlim(xlim)
            self.w.MplWidget.canvas.axes.set_ylim(ylim)

        # self.w.MplWidget.canvas.toolbar.update()
        self.w.MplWidget.canvas.draw()

    def plot_spline_baseline(self):
        self.plot_spc(True, True)
        # end plot_spline_baseline

    def previous_command(self):
        if (self.w.cmdLine.hasFocus() == True):
            if (self.nd.cmd_idx > 0):
                self.nd.cmd_idx -= 1
                self.w.cmdLine.setText(self.nd.cmd_buffer[self.nd.cmd_idx])

        # end previous_command

    def quit_app(self):
        # some actions to perform before actually quitting:
        try:
            self.p.terminate()
            sleep(2)
        except:
            pass

        self.w.close()
        # end quit_app

    def read_nmr_spc(self):
        kz = self.w.keepZoom.isChecked()
        if (len(self.nd.nmrdat[0]) == 0):
            self.w.keepZoom.setChecked(False)

        selected_directory = QFileDialog.getExistingDirectory()
        if (len(selected_directory) > 0):
            # Use the selected directory...
            idx = selected_directory.rfind('/')
            ds_name = selected_directory[:idx]
            exp_name = selected_directory[idx + 1:]
            self.nd.read_spc(ds_name, exp_name)
            self.set_j_res()
            self.nd.ft()
            if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 0:
                self.nd.auto_ref(True)
            else:
                self.nd.auto_ref(False)

            self.nd.e = len(self.nd.nmrdat[self.nd.s]) - 1
            self.nd.auto_ref()
            self.plot_spc()
            self.w.keepZoom.setChecked(kz)
            self.set_proc_pars()
            self.set_acq_pars()
            self.set_title_file()
            self.set_pulse_program()
            self.w.expBox.setValue(self.nd.e + 1)
            self.set_disp_pars()
            self.update_gui()

        # end read_nmr_spc

    def read_nmrpipe_spc(self, sfile=False):
        if sfile == False:
            selected_file = QFileDialog.getOpenFileName()
            if len(selected_file[0]) == 0:
                return

        else:
            selected_file = (sfile, '')

        # print(selected_file)
        f_name = os.path.split(selected_file[0])[1]
        spc3d = re.compile('.+\d+.+')
        if len(spc3d.findall(f_name)) == 0:
            data_path = os.path.split(os.path.split(selected_file[0])[0])[0]
            exp_num = os.path.split(os.path.split(selected_file[0])[0])[1]
            ft_dir = ''
        else:
            data_path = os.path.split(os.path.split(os.path.split(selected_file[0])[0])[0])[0]
            exp_num = os.path.split(os.path.split(os.path.split(selected_file[0])[0])[0])[1]
            ft_dir = os.path.split(os.path.split(selected_file[0])[0])[1]

        #print(f'data_path: {data_path}')
        #print(f'exp_num: {exp_num}')
        if exp_num.find('.') > -1:
            exp_num = exp_num[:exp_num.find('.')]

        self.read_nmrpipe_spcs([data_path], [exp_num], f_name, ft_dir)
        self.set_standard_colours()
        self.update_gui()
        self.reset_plot()
        # end read_nmrpipe_spc

    def read_nmrpipe_spcs(self, data_path, data_sets, proc_data_name='test.dat', ft_dir=''):
        z_fill = 25
        if (data_path[0] == 'interactive'):
            data_path = [QFileDialog.getExistingDirectory()]

        if (len(data_path) > 0):
            if (str(data_sets) == 'all'):
                folders = []
                for r, d, f in os.walk(data_path):
                    for folder in d:
                        if (os.path.isfile(os.path.join(r, folder, proc_data_name))):
                            folders.append(folder.z_fill(z_fill).rstrip('.proc'))

                folders.sort()
                data_sets = []
                for k in range(len(folders)):
                    data_sets.append(int(folders[k]))

            self.nd.read_nmrpipe_spcs(data_path, data_sets, proc_data_name, ft_dir)
        # end read_nmrpipe_spcs

    def read_spcs(self, data_path, data_sets, dataset=1):
        z_fill = 25
        if (data_path[0] == 'interactive'):
            data_path = [QFileDialog.getExistingDirectory()]

        if (len(data_path) > 0):
            if (str(data_sets[0]) == 'all'):
                folders = []
                for r, d, f in os.walk(data_path[0]):
                    for folder in d:
                        if (os.path.isfile(os.path.join(r, folder, 'fid'))):
                            if (folder != '99999'):
                                folders.append(folder.z_fill(z_fill))

                        if (os.path.isfile(os.path.join(r, folder, 'ser'))):
                            folders.append(folder.z_fill(z_fill))

                folders.sort()
                data_sets = []
                for k in range(len(folders)):
                    data_sets.append(int(folders[k]))

            if (str(data_sets[0]) == 'all1d'):
                folders = []
                for r, d, f in os.walk(data_path[0]):
                    for folder in d:
                        if (os.path.isfile(os.path.join(r, folder, 'fid'))):
                            if (folder != '99999'):
                                folders.append(folder.z_fill(z_fill))

                folders.sort()
                data_sets = []
                for k in range(len(folders)):
                    data_sets.append(int(folders[k]))

            if (str(data_sets[0]) == 'all2d'):
                folders = []
                for r, d, f in os.walk(data_path[0]):
                    for folder in d:
                        if (os.path.isfile(os.path.join(r, folder, 'ser'))):
                            folders.append(folder.z_fill(z_fill))

                folders.sort()
                data_sets = []
                for k in range(len(folders)):
                    data_sets.append(int(folders[k]))

            if len(data_path) > 1:
                dp = []
                for d in data_path:
                    if os.path.isfile(os.path.join(d, data_sets[0], 'fid')) or os.path.isfile(
                            os.path.join(d, data_sets[0], 'ser')):
                        dp.append(d)

                data_path = dp

            else:
                ds = []
                for d in data_sets:
                    if os.path.isfile(os.path.join(data_path[0], str(d), 'fid')) or os.path.isfile(
                            os.path.join(data_path[0], str(d), 'ser')):
                        ds.append(d)

                data_sets = ds

            if len(data_path) > 0 and len(data_sets) > 0:
                self.nd.read_spcs(data_path, data_sets, dataset)

        # end read_spcs

    def reference1d(self, ref_shift=0.0, peak_number=-1):
        if peak_number == -1 and not isinstance(ref_shift, str):
            self.temp_ref_shift = ref_shift
            self.w.MplWidget.canvas.setFocus()
            self.show_nmr_spectrum()
            self.ginput_ref_1d(1)
        else:
            if peak_number == -1:
                return

            else:
                metabolite_name = ref_shift
                ref_shift = 0.0
                hsqc = nmrHsqc.NmrHsqc()
                hsqc.read_metabolite_information(metabolite_name)
                hsqc.set_metabolite_information(metabolite_name, hsqc.metabolite_information)
                peak_number = max(peak_number, 1)
                peak_number = min(peak_number, len(hsqc.hsqc_data[metabolite_name].h1_shifts))
                ref_shift = hsqc.hsqc_data[metabolite_name].h1_shifts[peak_number - 1]
                self.temp_ref_shift = ref_shift
                self.w.MplWidget.canvas.setFocus()
                self.show_nmr_spectrum()
                self.ginput_ref_1d(1)

        # end reference1d

    def reference1d_all(self, new_shift, find_maximum=True):
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.temp_shift = new_shift
        self.find_maximum = find_maximum
        self.ginput_ref_1d_all(1)
        # end reference1d_all

    def reference1d_all_2(self):
        self.nd.reference1d_all(self.xdata[0], self.temp_shift, self.find_maximum)
        self.xdata = []
        self.ydata = []
        self.temp_shift = 0.0
        self.plot_spc()
        # end reference1d_all_2

    def reference2d(self, ref_shift=[0.0, 0.0], peak_number=-1):
        if peak_number == -1 and not isinstance(ref_shift, str):
            self.temp_ref_shift = ref_shift
            self.w.MplWidget.canvas.setFocus()
            self.show_nmr_spectrum()
            self.ginput_ref_2d(1)
        else:
            if peak_number == -1:
                return

            else:
                metabolite_name = ref_shift
                ref_shift = [0.0, 0.0]
                hsqc = nmrHsqc.NmrHsqc()
                hsqc.read_metabolite_information(metabolite_name)
                hsqc.set_metabolite_information(metabolite_name, hsqc.metabolite_information)
                peak_number = max(peak_number, 1)
                peak_number = min(peak_number, len(hsqc.hsqc_data[metabolite_name].h1_shifts))
                ref_shift[0] = hsqc.hsqc_data[metabolite_name].h1_shifts[peak_number - 1]
                c13idx = np.where(hsqc.hsqc_data[metabolite_name].hsqc == 1)[0]
                ref_shift[1] = hsqc.hsqc_data[metabolite_name].c13_shifts[c13idx[peak_number - 1]]
                self.temp_ref_shift = ref_shift
                self.w.MplWidget.canvas.setFocus()
                self.show_nmr_spectrum()
                self.ginput_ref_2d(1)

        # end reference2d

    def remove_assigned_metabolite(self):
        idx = self.w.hsqcAssignedMetabolites.currentIndex().row()
        if idx == -1:
            return

        metabolite_name = self.w.hsqcAssignedMetabolites.currentIndex().data()
        del self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name]
        self.update_assigned_metabolites()
        self.w.hsqcMetabolites.setCurrentIndex(self.w.hsqcMetabolites.model().index(-1, 0))
        self.w.metaboliteImage.scene().clear()
        self.delete_buttons(0)
        self.w.hsqcPeak.canvas.axes.clear()
        self.w.hsqcPeak.canvas.draw()
        self.w.hsqcMultiplet.canvas.axes.clear()
        self.w.hsqcMultiplet.canvas.draw()
        self.w.metaboliteInformation.setText('')
        self.w.multipletAnalysisIntensity.setText('')
        self.w.multipletAnalysisR2.setText('')
        self.w.multipletAnalysisEchoTime.setText('')
        self.w.openWeb.clear()
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite = ''
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak = -1
        self.w.hsqcSpinSys.setRowCount(0)
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            colour = [180, 180, 180]
        else:
            colour = [0, 0, 0]

        self.w.coefficientOfDetermination.display(-1)
        palette = self.w.coefficientOfDetermination.palette()
        # foreground color
        palette.setColor(palette.windowText, QtGui.QColor(colour[0], colour[1], colour[2]))
        # background color
        # palette.setColor(palette.Background, QtGui.QColor(colour[0], colour[1], colour[2]))
        # "light" border
        palette.setColor(palette.Light, QtGui.QColor(colour[0], colour[1], colour[2]))
        # "dark" border
        palette.setColor(palette.Dark, QtGui.QColor(colour[0], colour[1], colour[2]))
        self.w.coefficientOfDetermination.setPalette(palette)
        # end remove_asssigned_metabolite

    def remove_last_col_row(self):
        n_lines = len(self.w.MplWidget.canvas.axes.lines)
        if n_lines > 0:
            self.w.MplWidget.canvas.axes.lines[n_lines - 1].remove()
            self.ph_corr.spc_row = self.ph_corr.spc_row[:-1]
            self.ph_corr.spc_col = self.ph_corr.spc_col[:-1]
            self.ph_corr.spc_row_pts = self.ph_corr.spc_row_pts[:-1]
            self.ph_corr.spc_col_pts = self.ph_corr.spc_col_pts[:-1]
            self.plot_2d_col_row()
            self.show_acquisition_parameters()
            self.show_nmr_spectrum()

        # end remove_last_col_row

    def reset_config(self):
        self.cf = nmrConfig.NmrConfig()
        self.cf.save_config()
        self.load_config()
        # end reset_config

    def reset_data_pre_processing(self):
        self.nd.reset_data_pre_processing()
        self.plot_spc_pre_proc()
        self.vertical_auto_scale()
        self.w.MplWidget.canvas.flush_events()
        self.w.MplWidget.canvas.draw()
        # end data_pre_processing

    def reset_help(self):
        f_name = os.path.join(os.path.dirname(__file__), "web", "index.html")
        url = "file:///" + f_name.replace('\\', '/')
        self.w.helpView.setUrl(url)
        self.w.nmrSpectrum.setCurrentIndex(12)
        # end reset_help

    def reset_ml_info(self):
        idx = self.w.hsqcMetabolites.currentIndex().row()
        if idx == -1:
            return

        metabolite_name = self.w.hsqcMetabolites.currentIndex().data()
        nmr_dir = os.path.split(inspect.getmodule(nmrDataSet).__file__)[0]
        base_dir = os.path.split(nmr_dir)[0]
        file_name1 = os.path.join(base_dir, 'nmr', 'reset_metabolites', metabolite_name + '.mlInfo')
        file_name2 = os.path.join(base_dir, 'nmr', 'metabolites', metabolite_name + '.mlInfo')
        fid = open(file_name1, 'r')
        metabolite_text = fid.read()
        fid.close()
        fid = open(file_name2, 'w')
        fid.write(metabolite_text)
        fid.close()
        self.w.metaboliteInformation.setText(metabolite_text)
        # end reset_ml_info

    def reset_plot(self):
        zoom_checked = self.w.keepZoom.isChecked()
        self.w.keepZoom.setChecked(False)
        self.plot_spc()
        if (zoom_checked == True):
            self.w.keepZoom.setChecked(True)

        # end reset_plot

    def restart_metabolabpy(self):
        os.execl(sys.executable, sys.executable.replace(' ', '" "'), *sys.argv)
        # end restart_metabolabpy

    def save_button(self):
        if len(self.cf.current_directory) > 0:
            if os.path.isdir(self.cf.current_directory):
                os.chdir(self.cf.current_directory)

        pf_name = QFileDialog.getSaveFileName(None, "Save MetaboLabPy DataSet","", "*.mlpy", "*.mlpy")
        if len(pf_name[0]) == 0:
            return

        f_name = pf_name[0].rstrip('.mlpy').rstrip(' ').rstrip('/').rstrip('.mlpy') + '.mlpy'
        if (os.path.isfile(f_name)):
            os.remove(f_name)

        if (os.path.isdir(f_name)):
            shutil.rmtree(f_name)

        self.nd.script = self.w.script.toHtml()
        self.nd.console = self.w.console.toHtml()
        if self.w.hsqcAnalysis.isChecked() == True:
            self.w.hsqcAnalysis.setChecked(False)

        self.nd.save(f_name)
        # end save_button

    def save_hsqc_data(self):
        pf_name = QFileDialog.getSaveFileName(None, "Save HSQC Data", "", "*.xlsx", "*.xlsx")
        f_name = pf_name[0].rstrip('.xlsx').rstrip(' ').rstrip('/').rstrip('.xlsx') + '.xlsx'
        self.nd.export_hsqc_data(f_name)
        # end save_hsqc_data

    def save_config(self):
        #self.cf.auto_plot = self.w.autoPlot.isChecked()
        self.cf.keep_zoom = self.w.keepZoom.isChecked()
        self.cf.font_size = self.w.fontSize.value()
        self.cf.phase_reference_colour = self.nd.nmrdat[0][0].display.ph_ref_col
        self.cf.pos_col10 = self.std_pos_col1[0]
        self.cf.pos_col11 = self.std_pos_col1[1]
        self.cf.pos_col12 = self.std_pos_col1[2]
        self.cf.neg_col10 = self.std_neg_col1[0]
        self.cf.neg_col11 = self.std_neg_col1[1]
        self.cf.neg_col12 = self.std_neg_col1[2]
        self.cf.pos_col20 = self.std_pos_col2[0]
        self.cf.pos_col21 = self.std_pos_col2[1]
        self.cf.pos_col22 = self.std_pos_col2[2]
        self.cf.neg_col20 = self.std_neg_col2[0]
        self.cf.neg_col21 = self.std_neg_col2[1]
        self.cf.neg_col22 = self.std_neg_col2[2]
        self.cf.save_config()
        # end save_config

    def save_mat(self):
        scipy.io.save_mat('/Users/ludwigc/metabolabpy.mat',
                          {'spc': self.nd.nmrdat[0][0].spc, 'fid': self.nd.nmrdat[0][0].fid})
        # end save_mat

    def save_ml_info(self):
        idx = self.w.hsqcMetabolites.currentIndex().row()
        if idx == -1:
            return

        metabolite_name = self.w.hsqcMetabolites.currentIndex().data()
        nmr_dir = os.path.split(inspect.getmodule(nmrDataSet).__file__)[0]
        base_dir = os.path.split(nmr_dir)[0]
        file_name = os.path.join(base_dir, 'nmr', 'metabolites', metabolite_name + '.mlInfo')
        fid = open(file_name, 'w')
        fid.write(self.w.metaboliteInformation.toPlainText())
        fid.close()
        # end save_ml_info

    def save_script(self, f_name=""):
        if (f_name == False):
            f_name = ""

        if (len(f_name) == 0):
            f_name = QFileDialog.getSaveFileName(None, 'Save Script File', '', 'Python files (*.py)')
            f_name = f_name[0]

        if (len(f_name) > 0):
            scriptText = self.w.script.toPlainText()
            f = open(f_name, 'w')
            f.write(scriptText)

        # end open_script

    def scale_1d(self, factor=1.0):
        self.nd.nmrdat[self.nd.s][self.nd.e].fid *= factor
        self.nd.nmrdat[self.nd.s][self.nd.e].spc *= factor
        self.plot_spc()

    def scale_2d_spectrum_up(self):
        self.nd.nmrdat[self.nd.s][self.nd.e].display.min_level /= 1.1
        self.nd.nmrdat[self.nd.s][self.nd.e].display.max_level /= 1.1
        self.set_disp_pars()
        self.plot_spc()
        # end scale_2d_spectrum_up

    def scale_2d_spectrum_down(self):
        self.nd.nmrdat[self.nd.s][self.nd.e].display.min_level *= 1.1
        self.nd.nmrdat[self.nd.s][self.nd.e].display.max_level *= 1.1
        self.set_disp_pars()
        self.plot_spc()
        # end scale_2d_spectrum_down

    def scale_all_2d_spectra_up(self):
        self.nd.nmrdat[self.nd.s][self.nd.e].display.min_level /= 1.1
        self.nd.nmrdat[self.nd.s][self.nd.e].display.max_level /= 1.1
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].display.min_level = self.nd.nmrdat[self.nd.s][self.nd.e].display.min_level
            self.nd.nmrdat[self.nd.s][k].display.max_level = self.nd.nmrdat[self.nd.s][self.nd.e].display.max_level

        self.set_disp_pars()
        self.plot_spc()
        # end scaleAll_2d_spectra_up

    def scale_all_2d_spectra_down(self):
        self.nd.nmrdat[self.nd.s][self.nd.e].display.min_level *= 1.1
        self.nd.nmrdat[self.nd.s][self.nd.e].display.max_level *= 1.1
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].display.min_level = self.nd.nmrdat[self.nd.s][self.nd.e].display.min_level
            self.nd.nmrdat[self.nd.s][k].display.max_level = self.nd.nmrdat[self.nd.s][self.nd.e].display.max_level

        self.set_disp_pars()
        self.plot_spc()
        # end scaleAll_2d_spectra_down

    def script_editor(self):
        self.w.nmrSpectrum.setCurrentIndex(9)
        # end script_editor

    def set_datasets_exps(self):
        if self.w.quantify.isChecked() == True:
            self.nd.quantify = True
        else:
            self.nd.quantify = False

        if self.w.intAllExps.isChecked() == True:
            self.nd.int_all_exps = True
        else:
            self.nd.int_all_exps = False

        if self.w.exportFormatCB.currentIndex() == 0:
            self.nd.export_peak_excel = True
        else:
            self.nd.export_peak_excel = False

        if self.w.localBaselineCorrection.isChecked() == True:
            self.cf.local_baseline_correction = True
            self.cf.save_config()
        else:
            self.cf.local_baseline_correction = False
            self.cf.save_config()

        start_peak = self.nd.nmrdat[self.nd.s][self.nd.e].start_peak
        end_peak = self.nd.nmrdat[self.nd.s][self.nd.e].end_peak
        peak_label = self.nd.nmrdat[self.nd.s][self.nd.e].peak_label
        n_protons = self.nd.nmrdat[self.nd.s][self.nd.e].n_protons
        self.nd.set_peak(start_peak, end_peak, peak_label, n_protons)
        # end set_datasets_exps

    def set_fit_ma_chem_shifts(self):
        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        hsqc.fit_chemical_shifts = self.w.maFitChemShifts.isChecked()

    # end set_fit_ma_chem_shifts

    def set_fit_ph1(self, fit_ph1=True):
        self.cf.fit_ph1 = fit_ph1
        self.cf.save_config()
        for k in range(len(self.nd.nmrdat)):
            for l in range(len(self.nd.nmrdat[k])):
                self.nd.nmrdat[k][l].cf.read_config()

    # end set_fit_ph1

    def set_ma_autosim(self):
        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        hsqc.autosim = self.w.maAutoSim.isChecked()

    # end set_ma_autosim

    def set_fit_ma_percentages(self):
        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        hsqc.fit_percentages = self.w.maFitContributions.isChecked()

    # end set_fit_ma_percentages

    def set_fit_zero_percentages(self):
        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        hsqc.fit_zero_percentages = not self.w.doNotFitZeroPercentages.isChecked()

    def set_spline_average_points(self):
        self.w.averagePoints.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].spline_baseline.average_points))
        self.nd.nmrdat[self.nd.s][self.nd.e].add_baseline_points()
        self.plot_spc(True)
        # end set_spline_average_points

    def get_spline_average_points(self):
        try:
            self.nd.nmrdat[self.nd.s][self.nd.e].spline_baseline.average_points = int(self.w.averagePoints.text())
        except:
            self.nd.nmrdat[self.nd.s][self.nd.e].spline_baseline.average_points = 20

        for k in range(len(self.nd.nmrdat[self.nd.s])):
            if self.nd.nmrdat[self.nd.s][k].display.display_spc:
                self.nd.nmrdat[self.nd.s][k].spline_baseline.average_points = self.nd.nmrdat[self.nd.s][
                    self.nd.e].spline_baseline.average_points

        self.set_spline_average_points()
        # end set_spline_average_points

    def set_linear_spline_points(self):
        self.w.linearSplinePoints.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].spline_baseline.linear_spline))
        self.nd.nmrdat[self.nd.s][self.nd.e].add_baseline_points()
        self.plot_spc(True)
        # end set_spline_average_points

    def get_linear_spline_points(self):
        try:
            self.nd.nmrdat[self.nd.s][self.nd.e].spline_baseline.linear_spline = int(self.w.linearSplinePoints.text())
        except:
            self.nd.nmrdat[self.nd.s][self.nd.e].spline_baseline.linear_spline = 200

        for k in range(len(self.nd.nmrdat[self.nd.s])):
            if self.nd.nmrdat[self.nd.s][k].display.display_spc:
                self.nd.nmrdat[self.nd.s][k].spline_baseline.linear_spline = self.nd.nmrdat[self.nd.s][
                    self.nd.e].spline_baseline.linear_spline

        self.set_spline_average_points()
        # end set_spline_average_points

    def set_spline_baseline(self):
        if self.w.splinebaseline.isChecked():
            self.w.peakPicking.setChecked(False)
            self.w.preprocessing.setChecked(False)
            self.show_spline_baseline()
            self.set_spline_average_points()
            self.set_linear_spline_points()
            self.fill_spline_baseline_tw()
        else:
            self.hide_spline_baseline()

        self.plot_spc(True)

        # end set_spline_baseline

    def select_add_compress_pre_proc(self):
        self.ginput_compress(2)
        # end select_add_exclude_pre_proc

    def select_add_exclude_pre_proc(self):
        self.ginput_exclude(2)
        # end select_add_exclude_pre_proc

    def select_add_seg_align_pre_proc(self):
        self.ginput_seg_align(2)
        # end select_add_exclude_pre_proc

    def select_all_pre_proc(self):
        n_spc = len(self.nd.pp.class_select)
        self.nd.pp.plot_select = np.arange(n_spc)
        self.fill_pre_processing_numbers()
        self.set_plot_pre_proc()
        self.plot_spc_pre_proc()
        self.w.selectClassTW.setFocus()
        # end select_all_pre_proc

    def select_class_pre_proc(self):
        cls = self.w.selectClassLE.text()
        cls2 = self.nd.pp.class_select
        sel = np.array([])
        for k in range(len(cls2)):
            if (cls2[k] == cls):
                sel = np.append(sel, k)

        if (len(sel) == 0):
            sel = np.arange(len(cls2))

        self.nd.pp.plot_select = sel
        self.fill_pre_processing_numbers()
        self.set_plot_pre_proc()
        self.plot_spc_pre_proc()
        self.w.selectClassTW.setFocus()
        # end select_class_pre_proc

    def select_clear_compress_pre_proc(self):
        self.nd.pp.pre_proc_fill = True
        for k in range(len(self.nd.pp.compress_start)):
            self.w.compressBucketsTW.item(k, 0).setText("")
            self.w.compressBucketsTW.setFocus()
            self.w.compressBucketsTW.item(k, 1).setText("")
            self.w.compressBucketsTW.setFocus()

        self.nd.pp.pre_proc_fill = False
        self.nd.pp.compress_start = np.array([])
        self.nd.pp.compress_end = np.array([])
        self.w.compressBucketsTW.setFocus()
        self.fill_pre_processing_numbers()
        self.w.compressBucketsTW.setFocus()
        self.set_plot_pre_proc()
        self.w.compressBucketsTW.setFocus()
        self.plot_spc_pre_proc()
        self.set_compress_pre_proc()
        self.w.MplWidget.canvas.flush_events()
        self.w.MplWidget.canvas.draw()
        # end select_clear_exclude_pre_proc

    def clear_hsqc_spin_sys(self):
        for k in range(self.w.hsqcSpinSys.rowCount()):
            self.w.hsqcSpinSys.item(k, 0).setText("")
            self.w.hsqcSpinSys.setFocus()
            self.w.hsqcSpinSys.item(k, 1).setText("")
            self.w.hsqcSpinSys.setFocus()

        # end select_clear_exclude_pre_proc

    def select_clear_exclude_pre_proc(self):
        self.nd.pp.pre_proc_fill = True
        for k in range(len(self.nd.pp.exclude_start)):
            self.w.excludeRegionTW.item(k, 0).setText("")
            self.w.excludeRegionTW.setFocus()
            self.w.excludeRegionTW.item(k, 1).setText("")
            self.w.excludeRegionTW.setFocus()

        self.nd.pp.pre_proc_fill = False
        self.nd.pp.exclude_start = np.array([])
        self.nd.pp.exclude_end = np.array([])
        self.w.excludeRegionTW.setFocus()
        self.fill_pre_processing_numbers()
        self.w.excludeRegionTW.setFocus()
        self.set_plot_pre_proc()
        self.w.excludeRegionTW.setFocus()
        self.plot_spc_pre_proc()
        self.set_exclude_pre_proc()
        self.w.MplWidget.canvas.flush_events()
        self.w.MplWidget.canvas.draw()
        # end select_clear_exclude_pre_proc

    def select_clear_seg_align_pre_proc(self):
        self.nd.pp.pre_proc_fill = True
        for k in range(len(self.nd.pp.seg_start)):
            self.w.segAlignTW.item(k, 0).setText("")
            self.w.segAlignTW.setFocus()
            self.w.segAlignTW.item(k, 1).setText("")
            self.w.segAlignTW.setFocus()

        self.nd.pp.pre_proc_fill = False
        self.nd.pp.seg_start = np.array([])
        self.nd.pp.seg_end = np.array([])
        self.w.segAlignTW.setFocus()
        self.fill_pre_processing_numbers()
        self.w.segAlignTW.setFocus()
        self.set_plot_pre_proc()
        self.w.segAlignTW.setFocus()
        self.plot_spc_pre_proc()
        self.set_seg_align_pre_proc()
        self.w.MplWidget.canvas.flush_events()
        self.w.MplWidget.canvas.draw()
        # end select_clear_exclude_pre_proc

    def select_even_pre_proc(self):
        n_spc = len(self.nd.pp.class_select)
        self.nd.pp.plot_select = np.arange(n_spc)
        self.nd.pp.plot_select = self.nd.pp.plot_select[1::2]
        self.fill_pre_processing_numbers()
        self.set_plot_pre_proc()
        self.plot_spc_pre_proc()
        self.w.selectClassTW.setFocus()
        # end select_even_pre_proc

    def select_odd_pre_proc(self):
        n_spc = len(self.nd.pp.class_select)
        self.nd.pp.plot_select = np.arange(n_spc)
        self.nd.pp.plot_select = self.nd.pp.plot_select[0::2]
        self.fill_pre_processing_numbers()
        self.set_plot_pre_proc()
        self.plot_spc_pre_proc()
        self.w.selectClassTW.setFocus()
        # end select_odd_pre_proc

    def select_plot_all(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].display.display_spc = True

        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc()
        return "select_plot_all"
        # end select_plot_all

    def select_plot_clear(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].display.display_spc = False

        # self.plot_spc()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        self.plot_spc()
        return "select_plot_clear"
        # end select_plot_clear

    def select_plot_list(self, plot_select, auto_plot_spc=True):
        plot_select = np.array(plot_select)
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].display.display_spc = False

        plot_select -= 1
        for k in range(len(plot_select)):
            if ((plot_select[k] > -1) and (plot_select[k] < len(self.nd.nmrdat[self.nd.s]))):
                self.nd.nmrdat[self.nd.s][plot_select[k]].display.display_spc = True

        # self.plot_spc()
        self.w.nmrSpectrum.setCurrentIndex(0)
        self.change_data_set_exp()
        if auto_plot_spc:
            self.plot_spc()

        if self.w.preprocessing.isChecked():
            self.fill_pre_processing_numbers()

        return "select_plot_list"
        # end select_plot_list

    def select_plot_pp(self, keywords=[], classes=[]):
        if len(keywords) == 0 or len(classes) == 0:
            return

        if len(keywords) != len(classes):
            return

        self.nd.pp.plot_select = []
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            sum_value = 0
            for l in range(len(keywords)):
                title = self.nd.nmrdat[self.nd.s][k].title
                idx1 = title.find(keywords[l] + ' ')
                idx2 = title[idx1:].find(':')
                idx3 = title[idx1:].find('\n')
                if title[idx1 + idx2 + 1:idx1 + idx3].strip() in classes[l]:
                    sum_value += 1

            if sum_value == len(keywords):
                self.nd.pp.plot_select.append(k)

        self.fill_pre_processing_numbers()
        self.set_plot_pre_proc()
        self.plot_spc_pre_proc()
        self.w.selectClassTW.setFocus()
        # end select_plot_pp

    def set_acq_pars(self):
        s = self.nd.s
        e = self.nd.e
        a = self.nd.nmrdat[s][e].acq
        acq_str = "originalDataset      " + self.nd.nmrdat[s][e].orig_data_set + "\n"
        acq_str += "___________________________________________________________________________________________________\n"
        acq_str += "\n"
        acq_str += "metaInfo             "
        for k in range(len(a.title)):
            acq_str += a.title[k] + " "

        acq_str += "\n                    "
        acq_str += " Origin\t" + a.origin + "\n                    "
        acq_str += " Owner\t" + a.owner + "\n"
        acq_str += "___________________________________________________________________________________________________\n"
        acq_str += "\n"
        acq_str += "probe                          " + a.probe + "\n"
        pp = a.pul_prog_name
        pp = pp[1:]
        pp = pp[:len(pp) - 1]
        acq_str += "pulseProgram                   " + pp + "\n\n"
        acq_str += "sw                   [ppm]    " + "% 9.2f" % a.sw[0] + "        |    % 9.2f" % a.sw[
            1] + "        |    % 9.2f\n" % a.sw[2]
        acq_str += "sw_h                 [Hz]     " + "% 9.2f" % a.sw_h[0] + "        |    % 9.2f" % a.sw_h[
            1] + "        |    % 9.2f\n" % a.sw_h[2]
        acq_str += "bf1/2/3              [MHz]    " + "% 9.2f" % a.bf1 + "        |    % 9.2f" % a.bf2 + "        |    % 9.2f\n" % a.bf3
        acq_str += "sfo1/2/3             [MHz]    " + "% 9.2f" % a.sfo1 + "        |    % 9.2f" % a.sfo2 + "        |    % 9.2f\n" % a.sfo3
        acq_str += "o1/2/3               [Hz]     " + "% 9.2f" % a.o1 + "        |    % 9.2f" % a.o2 + "        |    % 9.2f\n" % a.o3
        acq_str += "nPoints                       " + "% 6d" % a.n_data_points[0] + "           |    % 6d" % \
                   a.n_data_points[1] + "           |    % 6d\n" % a.n_data_points[2]
        acq_str += "transients                    " + "% 6d\n" % a.transients
        acq_str += "steadyStateScans              " + "% 6d\n\n" % a.steady_state_scans
        acq_str += "groupDelay           [us]     " + "% 9.2f\n" % a.group_delay
        acq_str += "decim                         " + "% 6d\n" % a.decim
        acq_str += "dspfvs                        " + "% 6d\n" % a.dspfvs
        acq_str += "temperature          [K]      " + "% 9.2f\n" % a.temperature
        self.w.acqPars.setText(acq_str)
        # end set_acq_pars

    def set_autobaseline(self):
        if self.nd.e > -1:
            self.w.autobaselineBox.setChecked(self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline)
        # end set_autobaseline

    def set_autobaseline_all(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].proc.autobaseline = True

        self.set_autobaseline()
        # end set_autobaseline_all

    def unset_autobaseline_all(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].proc.autobaseline = False

        self.set_autobaseline()
        # end set_autobaseline_all

    def set_autobaseline2(self):
        if self.nd.e > -1:
            if self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1:
                show = self.w.autobaselineBox.isChecked()
                self.w.autobaselineGroupBox.setVisible(show)
                self.nd.nmrdat[self.nd.s][self.nd.e].proc.autobaseline = show
            else:
                self.w.autobaselineGroupBox.setVisible(False)
                self.w.autobaselineBox.setChecked(False)

        else:
            self.w.autobaselineGroupBox.setVisible(False)
            self.w.autobaselineBox.setChecked(False)

        # end set_autobaseline2

    def set_avoid_neg_values(self):
        if (self.nd.pp.pre_proc_fill == False):
            if (self.w.avoidNegValues.isChecked() == True):
                self.nd.pp.avoid_negative_values = True
            else:
                self.nd.pp.avoid_negative_values = False

        # end set_avoid_neg_values

    def set_bucket_ppm_pre_proc(self):
        try:
            bucket_ppm = float(self.w.bucketPpmLE.text())
        except:
            bucket_ppm = self.nd.pp.bucket_ppm

        ppm_per_point = abs(self.nd.nmrdat[self.nd.s][0].ppm1[0] - self.nd.nmrdat[self.nd.s][0].ppm1[1])
        bucket_points = round(bucket_ppm / ppm_per_point)
        bucket_ppm = np.round(1e4 * bucket_points * ppm_per_point) / 1e4
        self.w.bucketPpmLE.setText(str(bucket_ppm))
        self.w.bucketDataPointsLE.setText(str(int(bucket_points)))
        self.nd.pp.bucket_points = bucket_points
        self.nd.pp.bucket_ppm = bucket_ppm
        # end set_bucket_ppm_pre_proc

    def set_bucket_points_pre_proc(self):
        try:
            bucket_points = float(self.w.bucketDataPointsLE.text())
        except:
            bucket_points = self.nd.pp.bucket_points

        ppm_per_point = abs(self.nd.nmrdat[self.nd.s][0].ppm1[0] - self.nd.nmrdat[self.nd.s][0].ppm1[1])
        bucket_points = round(bucket_points)
        bucket_ppm = np.round(1e4 * bucket_points * ppm_per_point) / 1e4
        self.w.bucketPpmLE.setText(str(bucket_ppm))
        self.w.bucketDataPointsLE.setText(str(int(bucket_points)))
        self.nd.pp.bucket_points = bucket_points
        self.nd.pp.bucket_ppm = bucket_ppm
        # end set_bucket_points_pre_proc

    def set_bucket_spectra(self):
        if (self.nd.pp.pre_proc_fill == False):
            if (self.w.bucketSpectra.isChecked() == True):
                self.nd.pp.flag_bucket_spectra = True
                self.w.preProcessingSelect.setCurrentIndex(4)
            else:
                self.nd.pp.flag_bucket_spectra = False

        # end set_bucket_spectra

    def set_change_pre_proc(self):
        if (self.nd.pp.pre_proc_fill == False):
            cls = np.array([])
            for k in range(len(self.nd.pp.class_select)):
                cls = np.append(cls, self.w.selectClassTW.item(k, 1).text())

            self.nd.pp.class_select = cls

        # end set_change_pre_proc

    def set_class_pp(self, keyword=''):
        if len(keyword) == 0:
            return

        self.nd.pp.class_select = []
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            idx0 = self.nd.nmrdat[self.nd.s][k].title.find('Excel File ')
            if idx0 > -1:
                idx0 = self.nd.nmrdat[self.nd.s][k].title.find('\n') + 1
            else:
                idx0 = 0

            title = self.nd.nmrdat[self.nd.s][k].title[idx0:]
            idx1 = title.find(keyword + ' ')
            idx2 = title[idx1:].find(':')
            idx3 = title[idx1:].find('\n')
            self.nd.pp.class_select.append(title[idx1 + idx2 + 1:idx1 + idx3].strip())

        self.fill_pre_processing_numbers()
        self.set_plot_pre_proc()
        self.plot_spc_pre_proc()
        self.w.selectClassTW.setFocus()
        # end select_plot_pp

    def set_colours(self, keyword=''):
        if len(keyword) == 0:
            return

        class_select = []
        class_select_unique = []
        self.nd.pp.init_plot_colours()
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            idx0 = self.nd.nmrdat[self.nd.s][k].title.find('Excel File ')
            if idx0 > -1:
                idx0 = self.nd.nmrdat[self.nd.s][k].title.find('\n') + 1
            else:
                idx0 = 0

            title = self.nd.nmrdat[self.nd.s][k].title[idx0:]
            idx1 = title.find(keyword + ' ')
            idx2 = title[idx1:].find(':')
            idx3 = title[idx1:].find('\n')
            class_select.append(title[idx1 + idx2 + 1:idx1 + idx3].strip())
            if title[idx1 + idx2 + 1:idx1 + idx3].strip() not in class_select_unique:
                class_select_unique.append(title[idx1 + idx2 + 1:idx1 + idx3].strip())

        for k in range(len(class_select)):
            if len(class_select_unique) > 1:
                col_idx = np.where(np.array(class_select_unique) == class_select[k])[0][0]
                self.nd.nmrdat[self.nd.s][k].display.pos_col = 'RGB'
                self.nd.nmrdat[self.nd.s][k].display.pos_col_rgb = self.nd.pp.plot_colours[col_idx]


        print(keyword)
        if len(class_select_unique) > 1:
            self.set_cols = keyword
            self.plot_spc()
        else:
            self.set_cols = ''
            self.set_standard_colours()

        # end set_colours

    def set_legend(self):
        self.cf.plot_legend = self.w.plotLegend.isChecked()
        self.cf.save_config()
        # end set_legend

    def show_legend(self, mode=''):
        if len(self.set_cols) == 0:
            return

        class_select = []
        class_select_unique = []
        title = self.nd.nmrdat[self.nd.s][self.nd.e].title
        idx1 = title.find(self.set_cols + ' ')
        idx2 = title[idx1:].find(':')
        idx3 = title[idx1:].find('\n')
        class_select.append(title[idx1 + idx2 + 1:idx1 + idx3].strip())
        if title[idx1 + idx2 + 1:idx1 + idx3].strip() not in class_select_unique:
            class_select_unique.append(title[idx1 + idx2 + 1:idx1 + idx3].strip())

        #self.nd.pp.init_plot_colours()
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            if self.nd.nmrdat[self.nd.s][k].display.display_spc:
                title = self.nd.nmrdat[self.nd.s][k].title
                idx1 = title.find(self.set_cols + ' ')
                idx2 = title[idx1:].find(':')
                idx3 = title[idx1:].find('\n')
                class_select.append(title[idx1 + idx2 + 1:idx1 + idx3].strip())
                if title[idx1 + idx2 + 1:idx1 + idx3].strip() not in class_select_unique:
                    class_select_unique.append(title[idx1 + idx2 + 1:idx1 + idx3].strip())

        ll = self.w.MplWidget.canvas.axes.legend(class_select_unique, fontsize=self.cf.print_label_font_size, frameon=False, shadow=False)
        if len(mode) == 0:
            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                for text in ll.get_texts():
                    text.set_color("white")

        else:
            if mode == 'dark':
                for text in ll.get_texts():
                    text.set_color("white")
            else:
                for text in ll.get_texts():
                    text.set_color("black")

        self.w.MplWidget.canvas.draw()
        self.show_nmr_spectrum()
        # end set_colours

    def select_spectra(self, keyword=[], values=[]):
        if len(keyword) == 0 or len(values) == 0:
            msg = ''
            msg += '_____________________________________________________________________________MetaboLabPy Help__\n\n'
            msg += '    Usage:\n'
            msg += '        select_spectra(keyword=[<string>,<string>], values=[[<string>,<string>],[<string>,<string>]])\n\n\n'
            msg += '        [<string>,<string>] for keyword is a list of keywords to be scanned. Every sample\n'
            msg += '        to be displayed must have at least one of the options specified in values for every\n'
            msg += '        keyword specified. All lists can just contain a single item.\n'
            msg += '\n_______________________________________________________________________________________________\n'
            print(msg)
            return

        new_exp = -1
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            self.nd.nmrdat[self.nd.s][k].display.display_spc = False
            idx0 = self.nd.nmrdat[self.nd.s][k].title.find('Excel File ')
            if idx0 > -1:
                idx0 = self.nd.nmrdat[self.nd.s][k].title.find('\n') + 1
            else:
                idx0 = 0

            title = self.nd.nmrdat[self.nd.s][k].title[idx0:]
            idx4 = np.zeros(len(keyword))
            for l in range(len(keyword)):
                idx1 = title.find(keyword[l] + ' ')
                idx2 = title[idx1:].find(':')
                idx3 = title[idx1:].find('\n')
                idx4[l] = -1
                for m in range(len(values[l])):
                    if title[idx1 + idx2 + 1:idx1 + idx3].strip() == values[l][m]:
                        idx4[l] = 1

            if int(idx4.sum()) == len(keyword):
                self.nd.nmrdat[self.nd.s][k].display.display_spc = True
                if new_exp == -1:
                    new_exp = k

        if new_exp > -1:
            self.nd.e = new_exp

        self.update_gui()
        if self.cf.print_standard_colours:
            self.set_colours(self.set_cols)

        self.plot_spc()
        # end select_spectra

    def set_compress_buckets(self):
        if (self.nd.pp.pre_proc_fill == False):
            if (self.w.compressBuckets.isChecked() == True):
                self.nd.pp.flag_compress_buckets = True
                self.w.preProcessingSelect.setCurrentIndex(5)
            else:
                self.nd.pp.flag_compress_buckets = False

        # end set_compress_buckets

    def set_compress_pre_proc(self):
        if (self.nd.pp.pre_proc_fill == False):
            n_rows = self.w.compressBucketsTW.rowCount()
            co_start = np.array([])
            co_end = np.array([])
            t_start = np.array([])
            t_end = np.array([])
            for k in range(n_rows):
                # t_start = np.array([])
                # t_end   = np.array([])
                try:
                    t_start = np.append(t_start, float(self.w.compressBucketsTW.item(k, 0).text()))
                    # self.w.compressBucketsTW.item(k,0).clearContents()
                except:
                    t_start = np.append(t_start, -10000.0)

                try:
                    t_end = np.append(t_end, float(self.w.compressBucketsTW.item(k, 1).text()))
                    # self.w.compressBucketsTW.item(k,1).clearContents()
                except:
                    t_end = np.append(t_end, -10000.0)

            # self.w.compressBucketsTW.clearContents()
            self.w.compressBucketsTW.setRowCount(0)
            self.w.compressBucketsTW.setRowCount(n_rows)
            self.nd.pp.pre_proc_fill = True
            for k in np.arange(len(t_start) - 1, -1, -1):  # range(len(t_start)):
                comp_number1 = QTableWidgetItem(2 * k)
                comp_number1.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.w.compressBucketsTW.setItem(k, 0, comp_number1)
                comp_number2 = QTableWidgetItem(2 * k + 1)
                comp_number2.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.w.compressBucketsTW.setItem(k, 1, comp_number2)
                if ((t_start[k] > -10000.0) & (t_end[k] > -10000.0)):
                    t_min = min(t_start[k], t_end[k])
                    t_end[k] = max(t_start[k], t_end[k])
                    t_start[k] = t_min
                    co_start = np.append(co_start, t_start[k])
                    co_end = np.append(co_end, t_end[k])
                    t_start = np.delete(t_start, k)
                    t_end = np.delete(t_end, k)

                if (t_start[k] > -10000.0):
                    self.w.compressBucketsTW.item(k, 0).setText(str(t_start[k]))
                    self.w.compressBucketsTW.setFocus()
                else:
                    self.w.compressBucketsTW.item(k, 0).setText("")
                    self.w.compressBucketsTW.setFocus()

                if (t_end[k] > -10000.0):
                    self.w.compressBucketsTW.item(k, 1).setText(str(t_end[k]))
                    self.w.compressBucketsTW.setFocus()
                else:
                    self.w.compressBucketsTW.item(k, 1).setText("")
                    self.w.compressBucketsTW.setFocus()

            self.nd.pp.pre_proc_fill = False
            sort_idx = np.argsort(co_start)
            self.nd.pp.compress_start = co_start[sort_idx]
            self.nd.pp.compress_end = co_end[sort_idx]
            self.plot_spc_pre_proc()

        # end set_compress_pre_proc

    def set_dark_mode(self):
        arg = sys.argv[0].replace('\\\\?\\','')
        if sys.platform == 'win' or sys.platform == 'win32' or sys.platform == 'win64':
            sys.argv[0] = arg + '-script.py'

        self.cf.read_config()
        self.cf.mode = 'dark'
        self.cf.save_config()
        ## restart program
        if sys.platform == 'win' or sys.platform == 'win32' or sys.platform == 'win64':
            ml_path = os.path.split(os.path.split(inspect.getmodule(nmrDataSet).__file__)[0])[0]
            bat_file = os.path.join(ml_path, 'ml.bat')
            os.execl(bat_file, bat_file.replace(' ', '" "'), *[])
        else:
            os.execl(sys.executable, sys.executable.replace(' ', '" "'), *sys.argv)
        ## end save_config

    def set_disp_pars(self):
        d = self.nd.nmrdat[self.nd.s][self.nd.e].display
        self.w.posColR.setText(str(d.pos_col_rgb[0]))
        self.w.posColG.setText(str(d.pos_col_rgb[1]))
        self.w.posColB.setText(str(d.pos_col_rgb[2]))
        self.w.negColR.setText(str(d.neg_col_rgb[0]))
        self.w.negColG.setText(str(d.neg_col_rgb[1]))
        self.w.negColB.setText(str(d.neg_col_rgb[2]))
        self.w.nLevels.setText(str(d.n_levels))
        self.w.minLevel.setText(str(d.min_level))
        self.w.maxLevel.setText(str(d.max_level))
        self.w.spcOffset.setText(str(d.spc_offset))
        self.w.spcScale.setText(str(d.spc_scale))
        self.w.xLabel.setText(d.x_label)
        self.w.yLabel.setText(d.y_label)
        self.w.spcLabel.setText(d.spc_label)
        self.w.posCol.setCurrentIndex(d.colours.get(d.pos_col))
        self.w.negCol.setCurrentIndex(d.colours.get(d.neg_col))
        self.w.axisType1.setCurrentIndex(d.axes.get(d.axis_type1))
        self.w.axisType2.setCurrentIndex(d.axes.get(d.axis_type2))
        self.w.displaySpc.setCurrentIndex(d.false_true.get(d.display_spc))
        self.w.phRefColour.setCurrentIndex(d.colours2.get(d.ph_ref_col))
        self.w.phRefDS.setValue(d.ph_ref_ds)
        self.w.phRefExp.setValue(d.ph_ref_exp)
        # end set_disp_pars

    def set_hsqc(self):
        self.set_hsqc_pars1()
        self.set_hsqc_pars2()
        self.set_hsqc_pars3()
        self.set_hsqc_pars4()
        self.set_hsqc_pars5()
        self.set_hsqc_pars6()
        self.set_hsqc_pars7()
        self.set_hsqc_pars8()
        self.set_hsqc_pars9()
        self.set_hsqc_pars10()
        self.set_hsqc_pars11()
        self.set_hsqc_pars12()
        self.set_hsqc_pars13()
        self.set_hsqc_pars14()
        self.set_hsqc_pars15()
        self.set_hsqc_pars16()
        self.set_hsqc_pars17()
        self.set_hsqc_pars18()
        self.set_hsqc_pars19()
        # end set_hsqc

    def set_add_peak(self):
        if (self.nd.peak_fill == False):
            n_rows = self.w.peakWidget.rowCount()
            start_peak = np.array([])
            end_peak = np.array([])
            peak_label = np.array([])
            n_protons = np.array([])
            s_peak = np.array([])
            e_peak = np.array([])
            p_label = np.array([])
            n_prot = np.array([])
            for k in range(n_rows):
                try:
                    s_peak = np.append(s_peak, float(self.w.peakWidget.item(k, 0).text()))
                except:
                    s_peak = np.append(s_peak, -10000.0)

                try:
                    e_peak = np.append(e_peak, float(self.w.peakWidget.item(k, 1).text()))
                except:
                    e_peak = np.append(e_peak, -10000.0)

                try:
                    p_label = np.append(p_label, self.w.peakWidget.item(k, 2).text())
                except:
                    p_label = np.append(p_label, '')

                try:
                    n_prot = np.append(n_prot, self.w.peakWidget.item(k, 3).text())
                except:
                    n_prot = np.append(n_prot, '')

            # print("s: {}, e: {}, l: {}".format(s_peak, e_peak, p_label))
            self.w.peakWidget.setRowCount(0)
            self.w.peakWidget.setRowCount(n_rows)
            self.nd.peak_fill = True
            for k in np.arange(len(s_peak) - 1, -1, -1):  # range(len(t_start)):
                p_number1 = QTableWidgetItem(3 * k)
                p_number1.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.w.peakWidget.setItem(k, 0, p_number1)
                p_number2 = QTableWidgetItem(3 * k + 1)
                p_number2.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.w.peakWidget.setItem(k, 1, p_number2)
                p_label1 = QTableWidgetItem(3 * k + 2)
                p_label1.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.w.peakWidget.setItem(k, 3, p_label1)
                n_prot1 = QTableWidgetItem(3 * k + 3)
                n_prot1.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.w.peakWidget.setItem(k, 4, n_prot1)
                if ((s_peak[k] > -10000.0) & (e_peak[k] > -10000.0)):
                    p_min = min(s_peak[k], e_peak[k])
                    e_peak[k] = max(s_peak[k], e_peak[k])
                    s_peak[k] = p_min
                    start_peak = np.append(start_peak, s_peak[k])
                    end_peak = np.append(end_peak, e_peak[k])
                    peak_label = np.append(peak_label, p_label[k])
                    n_protons = np.append(n_protons, n_prot[k])
                    s_peak = np.delete(s_peak, k)
                    e_peak = np.delete(e_peak, k)

            sort_idx = np.argsort(start_peak)
            start_peak = start_peak[sort_idx]
            end_peak = end_peak[sort_idx]
            peak_label = peak_label[sort_idx]
            n_protons = n_protons[sort_idx]
            self.nd.set_peak(start_peak, end_peak, peak_label, n_protons)
            self.set_peak_picking()
            self.nd.peak_fill = False
            self.plot_spc()

        # end set_exclude_pre_proc

    def set_exclude_pre_proc(self):
        if (self.nd.pp.pre_proc_fill == False):
            n_rows = self.w.excludeRegionTW.rowCount()
            ex_start = np.array([])
            ex_end = np.array([])
            t_start = np.array([])
            t_end = np.array([])
            for k in range(n_rows):
                # t_start = np.array([])
                # t_end   = np.array([])
                try:
                    t_start = np.append(t_start, float(self.w.excludeRegionTW.item(k, 0).text()))
                    # self.w.excludeRegionTW.item(k,0).clearContents()
                except:
                    t_start = np.append(t_start, -10000.0)

                try:
                    t_end = np.append(t_end, float(self.w.excludeRegionTW.item(k, 1).text()))
                    # self.w.excludeRegionTW.item(k,1).clearContents()
                except:
                    t_end = np.append(t_end, -10000.0)

            # self.w.excludeRegionTW.clearContents()
            self.w.excludeRegionTW.setRowCount(0)
            self.w.excludeRegionTW.setRowCount(n_rows)
            self.nd.pp.pre_proc_fill = True
            for k in np.arange(len(t_start) - 1, -1, -1):  # range(len(t_start)):
                excl_number1 = QTableWidgetItem(2 * k)
                excl_number1.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.w.excludeRegionTW.setItem(k, 0, excl_number1)
                excl_number2 = QTableWidgetItem(2 * k + 1)
                excl_number2.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.w.excludeRegionTW.setItem(k, 1, excl_number2)
                if ((t_start[k] > -10000.0) & (t_end[k] > -10000.0)):
                    t_min = min(t_start[k], t_end[k])
                    t_end[k] = max(t_start[k], t_end[k])
                    t_start[k] = t_min
                    ex_start = np.append(ex_start, t_start[k])
                    ex_end = np.append(ex_end, t_end[k])
                    t_start = np.delete(t_start, k)
                    t_end = np.delete(t_end, k)

                if (t_start[k] > -10000.0):
                    self.w.excludeRegionTW.item(k, 0).setText(str(t_start[k]))
                    self.w.excludeRegionTW.setFocus()
                else:
                    self.w.excludeRegionTW.item(k, 0).setText("")
                    self.w.excludeRegionTW.setFocus()

                if (t_end[k] > -10000.0):
                    self.w.excludeRegionTW.item(k, 1).setText(str(t_end[k]))
                    self.w.excludeRegionTW.setFocus()
                else:
                    self.w.excludeRegionTW.item(k, 1).setText("")
                    self.w.excludeRegionTW.setFocus()

            self.nd.pp.pre_proc_fill = False
            sort_idx = np.argsort(ex_start)
            self.nd.pp.exclude_start = ex_start[sort_idx]
            self.nd.pp.exclude_end = ex_end[sort_idx]
            self.plot_spc_pre_proc()

        # end set_exclude_pre_proc

    def fill_spline_baseline_tw(self):
        self.w.splineBaselineTW.cellChanged.disconnect()
        n_rows = len(self.nd.nmrdat[self.nd.s][self.nd.e].spline_baseline.baseline_points)
        self.w.splineBaselineTW.setRowCount(0)
        self.w.splineBaselineTW.setRowCount(n_rows)
        for k in range(n_rows):
            baseline_number = QTableWidgetItem(k)
            baseline_number.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.w.splineBaselineTW.setItem(k, 0, baseline_number)
            self.w.splineBaselineTW.item(k, 0).setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].spline_baseline.baseline_points[k]))

        self.w.splineBaselineTW.cellChanged.connect(self.set_spline_baseline_tw)
        # end fill_spline_baseline_tw

    def set_spline_baseline_tw(self):
        n_rows = self.w.excludeRegionTW.rowCount()
        baseline_pts = np.array([])
        for k in range(n_rows):
            try:
                baseline_pts = np.append(baseline_pts, float(self.w.splineBaselineTW.item(k, 0).text()))
            except:
                pass

        for k in range(len(self.nd.nmrdat[self.nd.s])):
            if self.nd.nmrdat[self.nd.s][k].display.display_spc or k == self.nd.e:
                self.nd.nmrdat[self.nd.s][k].spline_baseline.baseline_points = baseline_pts
                self.nd.nmrdat[self.nd.s][k].add_baseline_points()

        self.fill_spline_baseline_tw()
        self.plot_spc(True)
        # end set_spline_baseline_tw

    def set_exclude_region(self):
        if (self.nd.pp.pre_proc_fill == False):
            if (self.w.excludeRegion.isChecked() == True):
                self.nd.pp.flag_exclude_region = True
                self.w.preProcessingSelect.setCurrentIndex(1)
            else:
                self.nd.pp.flag_exclude_region = False

        # end set_exclude_region

    def set_export_character(self):
        tt = self.w.exportCharacter.text()
        if (len(tt) > 0):
            self.nd.pp.export_character = tt[0]
            self.w.exportCharacter.setText(tt[0])

        # end set_export_character

    def set_export_delimiter_tab(self):
        self.nd.pp.export_delimiter_tab = self.w.exportDelimiterTab.isChecked()
        # end set_export_delimiter_tab

    def set_export_file_name(self):
        if self.nd.pp.export_method == 0:
            self.nd.pp.export_excel = self.w.exportFileName.text()

        if self.nd.pp.export_method == 1:
            self.nd.pp.export_file_name = self.w.exportFileName.text()

        if self.nd.pp.export_method == 2:
            self.nd.pp.export_metabo_analyst = self.w.exportFileName.text()

        if self.nd.pp.export_method == 3:
            self.nd.pp.export_r_dolphin = self.w.exportFileName.text()

        if self.nd.pp.export_method == 4:
            self.nd.pp.export_batman = self.w.exportFileName.text()

        if self.nd.pp.export_method == 5:
            self.nd.pp.export_bruker = self.w.exportFileName.text()

        # end set_export_file_name

    def set_export_method(self):
        if self.nd.pp.export_method == 0:
            self.w.delimiterLabel.setHidden(True)
            self.w.exportDelimiterTab.setHidden(True)
            self.w.exportDelimiterCharacter.setHidden(True)
            self.w.exportCharacter.setHidden(True)
            self.w.samplesInRowsLabel.setHidden(False)
            self.w.samplesInComboBox.setHidden(False)
            self.w.exportPath.setText(self.nd.pp.export_excel_path)
            self.w.exportFileName.setText(self.nd.pp.export_excel)

        if self.nd.pp.export_method == 1:
            self.w.delimiterLabel.setHidden(False)
            self.w.exportDelimiterTab.setHidden(False)
            self.w.exportDelimiterCharacter.setHidden(False)
            self.w.exportCharacter.setHidden(False)
            self.w.samplesInRowsLabel.setHidden(False)
            self.w.samplesInComboBox.setHidden(False)
            self.w.exportPath.setText(self.nd.pp.export_path_name)
            self.w.exportFileName.setText(self.nd.pp.export_file_name)

        if self.nd.pp.export_method == 2:
            self.w.delimiterLabel.setHidden(True)
            self.w.exportDelimiterTab.setHidden(True)
            self.w.exportDelimiterCharacter.setHidden(True)
            self.w.exportCharacter.setHidden(True)
            self.w.samplesInRowsLabel.setHidden(True)
            self.w.samplesInComboBox.setHidden(True)
            self.w.exportPath.setText(self.nd.pp.export_metabo_analyst_path)
            self.w.exportFileName.setText(self.nd.pp.export_metabo_analyst)

        if self.nd.pp.export_method == 3:
            self.w.delimiterLabel.setHidden(True)
            self.w.exportDelimiterTab.setHidden(True)
            self.w.exportDelimiterCharacter.setHidden(True)
            self.w.exportCharacter.setHidden(True)
            self.w.samplesInRowsLabel.setHidden(True)
            self.w.samplesInComboBox.setHidden(True)
            self.w.exportPath.setText(self.nd.pp.export_r_dolphin_path)
            self.w.exportFileName.setText(self.nd.pp.export_r_dolphin)

        if self.nd.pp.export_method == 4:
            self.w.delimiterLabel.setHidden(True)
            self.w.exportDelimiterTab.setHidden(True)
            self.w.exportDelimiterCharacter.setHidden(True)
            self.w.exportCharacter.setHidden(True)
            self.w.samplesInRowsLabel.setHidden(True)
            self.w.samplesInComboBox.setHidden(True)
            self.w.exportPath.setText(self.nd.pp.export_batman_path)
            self.w.exportFileName.setText(self.nd.pp.export_batman)

        if self.nd.pp.export_method == 5:
            self.w.delimiterLabel.setHidden(True)
            self.w.exportDelimiterTab.setHidden(True)
            self.w.exportDelimiterCharacter.setHidden(True)
            self.w.exportCharacter.setHidden(True)
            self.w.samplesInRowsLabel.setHidden(True)
            self.w.samplesInComboBox.setHidden(True)
            self.w.exportPath.setText(self.nd.pp.export_bruker_path)
            self.w.exportFileName.setText(self.nd.pp.export_bruker)

        # end set_export_method

    def set_export_method_options(self):
        self.nd.pp.export_method = self.w.exportMethod.currentIndex()
        self.set_export_method()
        # end set_export_method_options

    def set_export_path(self):
        if self.nd.pp.export_method == 0:
            self.nd.pp.export_excel_path = self.w.exportPath.text()

        if self.nd.pp.export_method == 1:
            self.nd.pp.export_path_name = self.w.exportPath.text()

        if self.nd.pp.export_method == 2:
            self.nd.pp.export_metabo_analyst_path = self.w.exportPath.text()

        if self.nd.pp.export_method == 3:
            self.nd.pp.export_r_dolphin_path = self.w.exportPath.text()

        if self.nd.pp.export_method == 4:
            self.nd.pp.export_batman_path = self.w.exportPath.text()

        if self.nd.pp.export_method == 5:
            self.nd.pp.export_bruker_path = self.w.exportPath.text()

        # end set_export_path

    def set_export_data_set(self):
        if (self.nd.pp.pre_proc_fill == False):
            if (self.w.exportDataSet.isChecked() == True):
                self.nd.pp.flag_export_data_set = True
                self.w.preProcessingSelect.setCurrentIndex(8)
            else:
                self.nd.pp.flag_export_data_set = False

        # end set_export_data_set

    def set_export_table(self):
        p_name = QFileDialog.getExistingDirectory()
        # p_name = p_name[0]
        if (len(p_name) > 0):
            if self.nd.pp.export_method == 0:
                self.w.exportPath.setText(p_name)
                self.nd.pp.export_excel_path = p_name

            if self.nd.pp.export_method == 1:
                self.w.exportPath.setText(p_name)
                self.nd.pp.export_path_name = p_name

            if self.nd.pp.export_method == 2:
                self.w.exportPath.setText(p_name)
                self.nd.pp.export_metabo_analyst_path = p_name

            if self.nd.pp.export_method == 3:
                self.w.exportPath.setText(p_name)
                self.nd.pp.export_r_dolphin_path = p_name

            if self.nd.pp.export_method == 4:
                self.w.exportPath.setText(p_name)
                self.nd.pp.export_batman_path = p_name

            if self.nd.pp.export_method == 5:
                self.w.exportPath.setText(p_name)
                self.nd.pp.export_bruker_path = p_name

        # end set_export_table

    def set_font_size(self):
        font_size = self.w.fontSize.value()
        f = self.w.acqPars.font()
        f.setPointSize(font_size)
        self.w.acqPars.setFont(f)
        self.w.titleFile.setFont(f)
        cursor = self.w.script.textCursor()
        self.w.script.selectAll()
        self.w.script.setFontPointSize(font_size)
        self.w.script.setTextCursor(cursor)
        self.w.script.setCurrentFont(f)
        # self.w.script.setFont(f)
        cursor = self.w.console.textCursor()
        self.w.console.selectAll()
        self.w.console.setFontPointSize(font_size)
        self.w.console.setTextCursor(cursor)
        self.w.console.setCurrentFont(f)
        # self.w.console.setFont(f)
        self.w.pulseProgram.setFont(f)
        self.w.cmdLine.setFont(f)
        self.w.setStyleSheet("font-size: " + str(font_size) + "pt")
        # end set_font_size

    def set_help(self):
        url = []
        idx = self.w.helpComboBox.currentIndex()
        f_name = os.path.join(os.path.dirname(__file__), "web", "index.html")
        url.append("file:///" + f_name.replace('\\', '/'))
        url.append("http://www.bml-nmr.org")
        url.append("https://www.hmdb.ca")
        url.append("https://www.smpdb.ca")
        url.append("https://bmrb.io/metabolomics/")
        url.append("https://www.genome.jp/kegg/pathway.html#metabolism")
        url.append("https://nmrshiftdb.nmr.uni-koeln.de")
        url.append("https://sdbs.db.aist.go.jp/sdbs/cgi-bin/cre_index.cgi")
        url.append("http://dmar.riken.jp/spincouple/")
        self.w.helpView.setUrl(url[idx])
        # end set_help

    def set_tmsp_conc(self):
        try:
            self.nd.tmsp_conc = float(self.w.tmspConc.text())
            self.w.tmspConc.setText(str(self.nd.tmsp_conc))
        except:
            self.w.tmspConc.setText(str(self.nd.tmsp_conc))
        # end set_tmsp_conc

    def set_internal_std(self):
        if len(self.w.internalStandard.text()) > 0:
            self.nd.internal_std = self.w.internalStandard.text()
        else:
            self.w.internalStandard.setText(str(self.nd.internal_std))
        # end set_tmsp_conc

    def set_tutorial(self):
        url = []
        idx = self.w.tutorialComboBox.currentIndex()
        url.append("https://youtu.be/uUNRintjUIo")
        url.append("https://youtu.be/AeEoq0bwLJg")
        webbrowser.open(url[idx], new=2)
        # end set_help

    def set_hsqc_pars1(self):
        self.w.h1Range.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.range_h))
        # end set_hsqc_pars1

    def set_hsqc_pars2(self):
        self.w.c13Range.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.range_c))
        # end set_hsqc_pars2

    def set_hsqc_pars3(self):
        self.w.threshold.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.threshold))
        # end set_hsqc_pars3

    def set_hsqc_pars4(self):
        self.w.jCC.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.j_cc))
        # end set_hsqc_pars4

    def set_hsqc_pars5(self):
        self.w.jCH.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.j_ch))
        # end set_hsqc_pars5

    def set_hsqc_pars6(self):
        self.w.nMax.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.n_max))
        # end set_hsqc_pars6

    def set_hsqc_pars7(self):
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.use_splitting == True:
            idx = 0
        else:
            idx = 1

        # self.w.useSplittingCB.setCurrentIndex(idx)
        # end set_hsqc_pars7

    def set_hsqc_pars8(self):
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.tilt_hsqc == True:
            idx = 0
        else:
            idx = 1

        self.w.tiltHsqcCB.setCurrentIndex(idx)
        # end set_hsqc_pars8

    def set_hsqc_pars9(self):
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.display_library_shift == True:
            idx = 0
        else:
            idx = 1

        self.w.displayLibraryCB.setCurrentIndex(idx)
        # end set_hsqc_pars9

    def set_hsqc_pars10(self):
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.display_peaks_of_metabolite == True:
            idx = 0
        else:
            idx = 1

        self.w.displayPickedCB.setCurrentIndex(idx)
        # end set_hsqc_pars10

    def set_hsqc_pars11(self):
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.highlight_double_assignments == True:
            idx = 0
        else:
            idx = 1

        # self.w.highlightDoubleCB.setCurrentIndex(idx)
        # end set_hsqc_pars11

    def set_hsqc_pars12(self):
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.display_overlay_shifts == True:
            idx = 0
        else:
            idx = 1

        # self.w.displayOverlayShiftsCB.setCurrentIndex(idx)
        # end set_hsqc_pars12

    def set_hsqc_pars13(self):
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.co_hsqc == True:
            idx = 0
        else:
            idx = 1

        self.w.coHsqcCB.setCurrentIndex(idx)
        # end set_hsqc_pars13

    def set_hsqc_pars14(self):
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.pick_local_opt == True:
            idx = 0
        else:
            idx = 1

        self.w.pickLocalOptCB.setCurrentIndex(idx)
        # end set_hsqc_pars14

    def set_hsqc_pars15(self):
        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autoscale_j == True:
            idx = 0
        else:
            idx = 1

        self.w.autoscaleCB.setCurrentIndex(idx)
        # end set_hsqc_pars15

    def set_hsqc_pars16(self):
        self.w.h1RangeAutopick.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autopick_range_h))
        # end set_hsqc_pars16

    def set_hsqc_pars17(self):
        self.w.c13RangeAutopick.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autopick_range_c))
        # end set_hsqc_pars17

    def set_hsqc_pars18(self):
        self.w.codHigh.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cod_high))
        # end set_hsqc_pars18

    def set_hsqc_pars19(self):
        self.w.codLow.setText(str(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cod_low))
        # end set_hsqc_pars19

    def set_hsqc_spin_sys(self):
        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        spin_sys = hsqc.hsqc_data[hsqc.cur_metabolite].spin_systems[hsqc.cur_peak - 1]
        self.w.hsqcSpinSys.setRowCount(0)
        self.w.hsqcSpinSys.setRowCount(len(spin_sys['c13_idx']))
        for k in range(len(spin_sys['c13_idx'])):
            idx = QTableWidgetItem(' '.join(str(e) for e in spin_sys['c13_idx'][k]))
            idx_key_num = spin_sys['c13_idx'][k]
            idx_key_str = ' '.join(str(e) for e in idx_key_num)
            if idx_key_str in hsqc.hsqc_data[hsqc.cur_metabolite].c13_offset.keys():
                offset = QTableWidgetItem(str(hsqc.hsqc_data[hsqc.cur_metabolite].c13_offset[idx_key_str]))
            else:
                offset = QTableWidgetItem("0")

            j_cc = QTableWidgetItem(' '.join(str(e) for e in spin_sys['j_cc'][k]))
            perc = QTableWidgetItem(str(spin_sys['contribution'][k]))
            try:
                idx.setTextAlignment(QtCore.Qt.AlignLeft)
                offset.setTextAlignment(QtCore.Qt.AlignHCenter)
                j_cc.setTextAlignment(QtCore.Qt.AlignLeft)
                perc.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
            except:
                idx.setTextAlignment(0) #QtCore.Qt.AlignLeft)
                offset.setTextAlignment(4) #QtCore.Qt.AlignHCenter)
                j_cc.setTextAlignment(0) #QtCore.Qt.AlignLeft)
                perc.setTextAlignment(4) #QtCore.Qt.AlignmentFlag.AlignHCenter)

            self.w.hsqcSpinSys.setItem(k, 0, idx)
            self.w.hsqcSpinSys.setItem(k, 1, offset)
            self.w.hsqcSpinSys.setItem(k, 2, j_cc)
            self.w.hsqcSpinSys.setItem(k, 3, perc)
            # self.w.hsqcSpinSys.item(k, 0).setText(' '.join(str(e) for e in spin_sys['c13_shifts'][k]))
            # self.w.hsqcSpinSys.item(k, 1).setText('0') # '.join(str(e) for e in spin_sys['c13_shifts'][k]))
            # self.w.hsqcSpinSys.item(k, 2).setText(' '.join(str(e) for e in spin_sys['j_cc'][k]))
            # self.w.hsqcSpinSys.item(k, 3).setText(str(spin_sys['contribution'][k]))

        # end set_hsqc_spin_sys

    def set_invert(self):
        s = self.nd.s
        e = self.nd.e
        self.nd.nmrdat[s][e].proc.invert_matrix[0] = self.w.invertMatrix_1.isChecked()
        self.nd.nmrdat[s][e].proc.invert_matrix[1] = self.w.invertMatrix_2.isChecked()
        # end set_invert

    def set_j_res(self):
        if (self.nd.nmrdat[self.nd.s][self.nd.e].acq.fn_mode == 1):
            self.nd.nmrdat[self.nd.s][self.nd.e].display.y_label = '1H'
            self.nd.nmrdat[self.nd.s][self.nd.e].display.axis_type2 = 'Hz'
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.window_type = np.array([5, 3, 0])
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.lb[0] = 0.5

        # end set_j_res

    def set_light_mode(self):
        arg = sys.argv[0].replace('\\\\?\\','')
        if sys.platform == 'win' or sys.platform == 'win32' or sys.platform == 'win64':
            sys.argv[0] = arg + '-script.py'

        self.cf.read_config()
        self.cf.mode = 'light'
        self.cf.save_config()
        # restart program
        if sys.platform == 'win' or sys.platform == 'win32' or sys.platform == 'win64':
            ml_path = os.path.split(os.path.split(inspect.getmodule(nmrDataSet).__file__)[0])[0]
            bat_file = os.path.join(ml_path, 'ml.bat')
            os.execl(bat_file, bat_file.replace(' ', '" "'), *[])
        else:
            os.execl(sys.executable, sys.executable.replace(' ', '" "'), *sys.argv)
        # end save_config

    def set_ma_echo_time(self):
        if len(self.w.multipletAnalysisEchoTime.text()) > 0:
            echo_time = float(self.w.multipletAnalysisEchoTime.text())
            if self.w.maApplyToAll.isChecked():
                for k in range(len(self.nd.nmrdat[self.nd.s])):
                    self.nd.nmrdat[self.nd.s][k].hsqc.echo_time = echo_time

            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.echo_time = echo_time

    # end set_ma_echo_time

    def set_ma_intensity(self):
        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        if len(self.w.multipletAnalysisIntensity.text()) > 0:
            intensity = float(self.w.multipletAnalysisIntensity.text())
            hsqc.hsqc_data[hsqc.cur_metabolite].intensities[hsqc.cur_peak - 1] = intensity
        else:
            self.w.multipletAnalysisIntensity.setText('')

    # end set_ma_intensity

    def set_ma_r2(self):
        hsqc = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc
        if len(self.w.multipletAnalysisR2.text()) > 0:
            r2 = float(self.w.multipletAnalysisR2.text())
            hsqc.hsqc_data[hsqc.cur_metabolite].r2[hsqc.cur_peak - 1] = r2
            if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim:
                self.plot_metabolite_peak(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak)

        else:
            self.w.multipletAnalysisR2.setText('')

    # end set_ma_r2

    def set_noise_filtering(self):
        if (self.nd.pp.pre_proc_fill == False):
            if (self.w.noiseFiltering.isChecked() == True):
                self.nd.pp.flag_noise_filtering = True
                self.w.preProcessingSelect.setCurrentIndex(3)
            else:
                self.nd.pp.flag_noise_filtering = False

        # end set_noise_filtering

    def set_noise_reg_pre_proc(self):
        try:
            th = float(self.w.noiseThresholdLE.text())
        except:
            th = self.nd.pp.noise_threshold

        try:
            ns = float(self.w.noiseRegionStartLE.text())
        except:
            ns = self.nd.pp.noise_start

        try:
            ne = float(self.w.noiseRegionEndLE.text())
        except:
            ne = self.nd.pp.noise_end

        try:
            lw = float(self.w.thLineWidthLE.text())
        except:
            lw = self.nd.pp.th_line_width

        tm = min(ns, ne)
        ne = max(ns, ne)
        ns = tm
        self.nd.pp.noise_threshold = th
        self.nd.pp.noise_start = ns
        self.nd.pp.noise_end = ne
        self.nd.pp.th_line_width = lw
        self.w.noiseThresholdLE.setText(str(th))
        self.w.noiseRegionStartLE.setText(str(ns))
        self.w.noiseRegionEndLE.setText(str(ne))
        self.w.thLineWidthLE.setText(str(lw))
        self.plot_spc_pre_proc()
        # end set_noise_reg_pre_proc

    def set_ph_ref_exp(self, phRefExp, phRefDS=1):
        self.w.phRefDS.setValue(phRefDS)
        self.w.phRefExp.setValue(phRefExp)
        # end set_ph_ref_exp

    def set_plot_pre_proc(self):
        if (self.nd.pp.pre_proc_fill == False):
            sel = np.array([])
            sel = self.w.selectClassTW.selectedIndexes()
            sel2 = np.array([])
            for k in range(len(sel)):
                if (sel[k].column() == 0):
                    sel2 = np.append(sel2, sel[k].row())

            self.nd.pp.plot_select = sel2
            self.plot_spc_pre_proc()

        # end set_plot_pre_proc

    def set_pqn_tsa_scaling(self):
        if self.w.pqnButton.isChecked() is True:
            self.nd.pp.scale_pqn = True
        else:
            self.nd.pp.scale_pqn = False

        self.w.preserveOverallScale.setDisabled(self.nd.pp.scale_pqn)

        # end set_pqn_tsa_scaling

    def set_pre_processing(self):
        if (self.w.preprocessing.isChecked() == True):
            self.w.peakPicking.setChecked(False)
            self.w.splinebaseline.setChecked(False)
            # self.w.peakPickingTab.setHidden(True)
            self.w.preProcPeak.setCurrentIndex(0)
            if len(self.nd.nmrdat[self.nd.s]) != len(self.nd.pp.class_select):
                self.nd.pre_proc_init()

            self.show_pre_processing()
            self.fill_pre_processing_numbers()
            self.nd.noise_filtering_init()
        else:
            self.hide_pre_processing()
            self.w.preProcPeak.setHidden(True)

        # end set_pre_processing

    def set_plot_all_ds(self):
        for k in range(len(self.nd.nmrdat)):
            if k != self.nd.s:
                self.nd.nmrdat[k][self.nd.e].display.display_spc = True

        self.plot_spc()
        # end set_plot_all_ds

    def set_peak_picking(self):
        if (self.w.peakPicking.isChecked() == True):
            self.w.preprocessing.setChecked(False)
            self.w.splinebaseline.setChecked(False)
            # self.w.preProcessingTab.setHidden(True)
            self.w.preProcPeak.setCurrentIndex(1)
            self.w.intAllExps.stateChanged.disconnect()
            if self.nd.int_all_exps == True:
                self.w.intAllExps.setChecked(True)
            else:
                self.w.intAllExps.setChecked(False)

            self.w.intAllExps.stateChanged.connect(self.set_datasets_exps)
            if self.nd.quantify == True:
                self.w.quantify.setChecked(True)
            else:
                self.w.quantify.setChecked(False)

            if self.nd.export_peak_excel == True:
                self.w.exportFormatCB.setCurrentIndex(0)
            else:
                self.w.exportFormatCB.setCurrentIndex(1)

            try:
                self.w.tmspConc.setText(str(self.nd.tmsp_conc))
            except:
                self.w.tmspConc.setText('0.5')
                self.nd.tmsp_conc = 0.5

            self.w.localBaselineCorrection.stateChanged.disconnect()
            if self.cf.local_baseline_correction is True:
                self.w.localBaselineCorrection.setChecked(True)
                self.cf.local_baseline_correction = True
            else:
                self.w.localBaselineCorrection.setChecked(False)
                self.cf.local_baseline_correction = False

            self.cf.save_config()
            self.w.localBaselineCorrection.stateChanged.connect(self.set_datasets_exps)

            self.show_peak_picking()
            self.fill_peak_numbers()
        else:
            self.exited_peak_picking = True
            self.hide_peak_picking()
            self.w.preProcPeak.setHidden(True)
            self.w.peakPicking.setChecked(False)

        self.plot_spc()
        # end set_pre_processing

    def set_standard_colours(self):
        for k in range(len(self.nd.nmrdat[self.nd.s])):
            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                self.nd.nmrdat[self.nd.s][k].display.pos_col_rgb = self.std_pos_col2
                self.nd.nmrdat[self.nd.s][k].display.neg_col_rgb = self.std_neg_col2
            else:
                self.nd.nmrdat[self.nd.s][k].display.pos_col_rgb = self.std_pos_col1
                self.nd.nmrdat[self.nd.s][k].display.neg_col_rgb = self.std_neg_col1

        self.plot_spc()
        # end set_standard_colours

    def set_system_mode(self):
        arg = sys.argv[0].replace('\\\\?\\','')
        if sys.platform == 'win' or sys.platform == 'win32' or sys.platform == 'win64':
            sys.argv[0] = arg + '-script.py'

        self.cf.read_config()
        self.cf.mode = 'system'
        self.cf.save_config()
        # restart program
        if sys.platform == 'win' or sys.platform == 'win32' or sys.platform == 'win64':
            ml_path = os.path.split(os.path.split(inspect.getmodule(nmrDataSet).__file__)[0])[0]
            bat_file = os.path.join(ml_path, 'ml.bat')
            os.execl(bat_file, bat_file.replace(' ', '" "'), *[])
        else:
            os.execl(sys.executable, sys.executable.replace(' ', '" "'), *sys.argv)
        # end save_config

    def update_assigned_metabolites(self):
        model = QtGui.QStandardItemModel()
        for l in sorted(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data.keys()):
            it = QtGui.QStandardItem(l)
            model.appendRow(it)

        self.w.hsqcAssignedMetabolites.setModel(model)
        metabolite_name = self.w.hsqcMetabolites.currentIndex().data()
        try:
            idx1 = sorted(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data.keys()).index(metabolite_name)
            self.w.hsqcAssignedMetabolites.setCurrentIndex(self.w.hsqcAssignedMetabolites.model().index(idx1, 0))
        except:
            pass
        # end update_assigned_metabolites

    def set_hsqc_analysis(self):
        if (self.w.hsqcAnalysis.isChecked() == True):
            for k in range(len(self.nd.nmrdat)):
                for l in range(len(self.nd.nmrdat[k])):
                    self.nd.nmrdat[k][l].hsqc.cur_metabolite = ''
                    self.nd.nmrdat[k][l].hsqc.cur_peak = -1

            # self.w.fitUpToBonds.setCurrentIndex(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.n_bonds)
            self.w.hsqcSpinSys.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.w.hsqcSpinSys.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            self.w.hsqcSpinSys.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            # self.w.hsqcSpinSys.setResizeMode()
            # header = table.horizontalHeader()
            # header.setResizeMode(QHeaderView.ResizeToContents)
            # header.setStretchLastSection(True)
            self.w.displayAssignedMetabolites.setVisible(True)
            self.w.displayLibraryShifts.setVisible(True)
            self.w.displaySelectedMetabolite.setVisible(True)
            self.nd.old_data_set = self.nd.s
            self.nd.old_data_exp = self.nd.e
            self.w.multipletAnalysis.setVisible(False)
            #self.w.isotopomerAnalysis.setVisible(False)
            self.w.nmrSpectrum.setTabEnabled(1, True)
            # self.w.nmrSpectrum.setTabEnabled(2, True)
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.set_metabolite_list()
            model = QtGui.QStandardItemModel()
            if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autoscale_j == True:
                if len(self.nd.nmrdat[self.nd.s][self.nd.e].acq.cnst) > 0:
                    self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.j_scale = self.nd.nmrdat[self.nd.s][self.nd.e].acq.cnst[
                        18]

            for l in self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.metabolite_list:
                it = QtGui.QStandardItem(l)
                model.appendRow(it)

            self.w.hsqcMetabolites.setModel(model)
            self.update_assigned_metabolites()
            self.w.nmrSpectrum.setStyleSheet(
                "QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
            self.set_hsqc()
            self.w.h1Range.textChanged.connect(self.get_hsqc_pars1)
            self.w.c13Range.textChanged.connect(self.get_hsqc_pars2)
            self.w.threshold.textChanged.connect(self.get_hsqc_pars3)
            self.w.jCC.textChanged.connect(self.get_hsqc_pars4)
            self.w.jCH.textChanged.connect(self.get_hsqc_pars5)
            self.w.nMax.textChanged.connect(self.get_hsqc_pars6)
            # self.w.useSplittingCB.currentIndexChanged.connect(self.get_hsqc_pars7)
            # self.w.useSplittingCB.setVisible(False)
            # self.w.label_82.setVisible(False)
            self.w.tiltHsqcCB.currentIndexChanged.connect(self.get_hsqc_pars8)
            self.w.tiltHsqcCB.setVisible(False)
            self.w.label_78.setVisible(False)
            self.w.displayLibraryCB.currentIndexChanged.connect(self.get_hsqc_pars9)
            self.w.displayPickedCB.currentIndexChanged.connect(self.get_hsqc_pars10)
            # self.w.highlightDoubleCB.currentIndexChanged.connect(self.get_hsqc_pars11)
            # self.w.highlightDoubleCB.setVisible(False)
            # self.w.label_84.setVisible(False)
            # self.w.displayOverlayShiftsCB.currentIndexChanged.connect(self.get_hsqc_pars12)
            # self.w.displayOverlayShiftsCB.setVisible(False)
            # self.w.label_83.setVisible(False)
            self.w.coHsqcCB.currentIndexChanged.connect(self.get_hsqc_pars13)
            self.w.pickLocalOptCB.currentIndexChanged.connect(self.get_hsqc_pars14)
            self.w.autoscaleCB.currentIndexChanged.connect(self.get_hsqc_pars15)
            self.w.h1RangeAutopick.textChanged.connect(self.get_hsqc_pars16)
            self.w.c13RangeAutopick.textChanged.connect(self.get_hsqc_pars17)
            self.w.codHigh.textChanged.connect(self.get_hsqc_pars18)
            self.w.codLow.textChanged.connect(self.get_hsqc_pars19)
            self.w.nmrSpectrum.setCurrentIndex(1)
            self.activate_command_line()
            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                colour = [180, 180, 180]
            else:
                colour = [0, 0, 0]

            self.w.coefficientOfDetermination.display(-1)
            palette = self.w.coefficientOfDetermination.palette()
            # foreground color
            #palette.setColor(palette.currentColorGroup(), QtGui.QColor(colour[0], colour[1], colour[2]))
            palette.setColor(palette.currentColorGroup(), QPalette.WindowText, QtGui.QColor(colour[0], colour[1], colour[2]))
            # background color
            # palette.setColor(palette.Background, QtGui.QColor(colour[0], colour[1], colour[2]))
            # "light" border
            palette.setColor(palette.currentColorGroup(), QPalette.Light, QtGui.QColor(colour[0], colour[1], colour[2]))
            # "dark" border
            palette.setColor(palette.currentColorGroup(), QPalette.Dark, QtGui.QColor(colour[0], colour[1], colour[2]))
            self.w.coefficientOfDetermination.setPalette(palette)
        else:
            self.w.displayAssignedMetabolites.setChecked(False)
            self.w.displayAssignedMetabolites.setVisible(False)
            self.w.displayLibraryShifts.setChecked(False)
            self.w.displayLibraryShifts.setVisible(False)
            self.w.displaySelectedMetabolite.setChecked(False)
            self.w.displaySelectedMetabolite.setVisible(False)
            self.w.multipletAnalysis.setChecked(False)
            #self.w.isotopomerAnalysis.setChecked(False)
            self.w.multipletAnalysis.setVisible(False)
            #self.w.isotopomerAnalysis.setVisible(False)
            self.w.nmrSpectrum.setTabEnabled(1, False)
            self.w.nmrSpectrum.setTabEnabled(2, False)
            self.w.openWeb.clear()
            self.w.hsqcMetabolites.setCurrentIndex(self.w.hsqcMetabolites.model().index(-1, 0))
            self.w.hsqcAssignedMetabolites.setCurrentIndex(self.w.hsqcMetabolites.model().index(-1, 0))
            for k in range(len(self.nd.nmrdat)):
                for l in range(len(self.nd.nmrdat[k])):
                    self.nd.nmrdat[k][l].hsqc.cur_metabolite = ''
                    self.nd.nmrdat[k][l].hsqc.cur_peak = -1

            if hasattr(self.w.metaboliteImage.scene(), 'clear'):
                self.w.metaboliteImage.scene().clear()

            self.w.hsqcPeak.canvas.axes.clear()
            self.w.hsqcPeak.canvas.draw()
            self.w.hsqcMultiplet.canvas.axes.clear()
            self.w.hsqcMultiplet.canvas.draw()
            self.w.nmrSpectrum.setStyleSheet(
                "QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
            self.delete_buttons(0)
            if self.nd.s != self.nd.old_data_set or self.nd.e != self.nd.old_data_exp:
                self.plot_spc()

            self.w.metaboliteInformation.setText('')
            self.w.multipletAnalysisIntensity.setText('')
            self.w.multipletAnalysisR2.setText('')
            self.w.multipletAnalysisEchoTime.setText('')
            self.w.hsqcSpinSys.setRowCount(0)
            self.w.nmrSpectrum.setCurrentIndex(0)

        # end set_hsqc_analysis

    def set_hsqc_assigned_metabolite(self):
        idx = self.w.hsqcAssignedMetabolites.currentIndex().row()
        if idx == -1:
            return

        metabolite_name = self.w.hsqcAssignedMetabolites.currentIndex().data()
        try:
            idx1 = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.metabolite_list.index(metabolite_name)
            self.w.hsqcMetabolites.setCurrentIndex(self.w.hsqcMetabolites.model().index(idx1, 0))
            self.set_hsqc_metabolite()
        except:
            pass

        # end set_hsqc_assigned_metabolite

    def set_hsqc_metabolite(self):
        #print("set_hsqc_metabolite")
        my_autosim = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim = False
        self.w.openWeb.clear()
        idx = self.w.hsqcMetabolites.currentIndex().row()
        if idx == -1:
            return

        if self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.j_scale == -1:
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.j_scale = self.nd.nmrdat[self.nd.s][self.nd.e].acq.cnst[18]

        metabolite_name = self.w.hsqcMetabolites.currentIndex().data()
        cur_peak = self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_peak
        if cur_peak < 1:
            cur_peak = 1

        if metabolite_name in self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data.keys():
            if cur_peak > len(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].h1_picked):
                cur_peak = 1

        else:
            cur_peak = 1

        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.read_metabolite_information(metabolite_name)
        self.w.metaboliteInformation.setText(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.metabolite_information)
        nmr_dir = os.path.split(inspect.getmodule(nmrDataSet).__file__)[0]
        base_dir = os.path.split(nmr_dir)[0]
        image_path = os.path.join(base_dir, 'nmr', 'metabolites_png', metabolite_name + '.png')
        pix = QPixmap(image_path)
        item = QtWidgets.QGraphicsPixmapItem(pix)
        scene = QtWidgets.QGraphicsScene()
        scene.addItem(item)
        self.w.metaboliteImage.setScene(scene)
        self.w.metaboliteImage.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.set_metabolite_information(metabolite_name, self.nd.nmrdat[self.nd.s][
            self.nd.e].hsqc.metabolite_information)
        self.update_assigned_metabolites()
        n_peaks = len(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].h1_shifts)
        self.make_buttons(n_peaks)
        self.make_buttons(n_peaks)
        for k in self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].hmdb:
            self.w.openWeb.addItem(k)

        for k in self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[metabolite_name].smpdb:
            self.w.openWeb.addItem(k)

        self.plot_metabolite_peak(cur_peak)
        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.autosim = my_autosim
        # end set_hsqc_metabolite

    def set_multiplet_analysis(self):
        if (self.w.multipletAnalysis.isChecked() == True):
            self.w.nmrSpectrum.setTabEnabled(3, True)
            self.w.nmrSpectrum.setStyleSheet(
                "QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
            self.w.nmrSpectrum.setCurrentIndex(2)
        else:
            self.w.nmrSpectrum.setTabEnabled(3, False)
            self.w.nmrSpectrum.setStyleSheet(
                "QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
            self.w.nmrSpectrum.setCurrentIndex(1)

        # end set_multiplet_analysis


    def set_pre_processing_options(self):
        cur_idx = self.w.preProcessingSelect.currentIndex()
        self.w.preProcessingWidget.setCurrentIndex(cur_idx)
        if self.nd.nmrdat[self.nd.s][0].acq.manufacturer == 'Bruker':
            if self.w.exportMethod.count() == 5:
                self.w.exportMethod.addItem('Bruker Dataset')

        else:
            if self.w.exportMethod.count() == 6:
                self.w.exportMethod.removeItem(5)

        self.plot_spc_pre_proc()
        # end set_pre_processingOption

    def set_preserve_overall_scale(self):
        self.nd.pp.preserve_overall_scale = self.w.preserveOverallScale.isChecked()
        # end set_preserve_overall_scale

    def set_proc_pars(self):
        p = self.nd.nmrdat[self.nd.s][self.nd.e].proc
        a = self.nd.nmrdat[self.nd.s][self.nd.e].apc
        self.w.zeroFilling.setText(str(p.n_points[0]))
        self.w.zeroFilling_2.setText(str(p.n_points[1]))
        self.w.lb.setText(str(p.lb[0]))
        self.w.gb.setText(str(p.gb[0]))
        self.w.ssb.setText(str(p.ssb[0]))
        self.w.lb_2.setText(str(p.lb[1]))
        self.w.gb_2.setText(str(p.gb[1]))
        self.w.ssb_2.setText(str(p.ssb[1]))
        self.w.ph0.setText(str(p.ph0[0]))
        self.w.ph1.setText(str(p.ph1[0]))
        self.w.ph0_2.setText(str(p.ph0[1]))
        self.w.ph1_2.setText(str(p.ph1[1]))
        self.w.polyOrder.setText(str(p.poly_order))
        self.w.extrapolationSize.setText(str(p.conv_extrapolation_size[0]))
        self.w.windowSize.setText(str(p.conv_window_size[0]))
        self.w.fidOffsetCorrection.setText(str(p.fid_offset_correction))
        self.w.windowFunction.setCurrentIndex(p.window_type[0])
        self.w.windowFunction_2.setCurrentIndex(p.window_type[1])
        self.w.phaseCorrection.setCurrentIndex(p.ph_corr[0])
        self.w.phaseCorrection_2.setCurrentIndex(p.ph_corr[1])
        self.w.waterSuppression.setCurrentIndex(p.water_suppression)
        self.w.stripTransformStart.setText(str(p.strip_start))
        self.w.stripTransformEnd.setText(str(p.strip_end))
        self.w.winType.setCurrentIndex(p.conv_window_type[0])
        self.w.gibbs.setCurrentIndex(p.gibbs_p.get(p.gibbs[0]))
        self.w.gibbs_2.setCurrentIndex(p.gibbs_p.get(p.gibbs[1]))
        self.w.wwStartLevel.setText(f'{p.ww_start}')
        self.w.wwZeroFilling.setText(f'{p.ww_zf}')
        idx1 = p.wavelet_names.index(p.ww_wavelet_type)
        idx2 = p.wavelet_numbers[p.ww_wavelet_type].index(p.ww_wavelet_type_number)
        if self.w.wwWaveletType.count() == 0:
            self.w.wwWaveletType.addItems(p.wavelet_names)
            self.w.wwWaveletType.setCurrentIndex(idx1)

        #self.w.wwNumber.addItems(p.wavelet_numbers[p.ww_wavelet_type])
        #self.w.wwNumber.setCurrentIndex(idx2)
        self.w.rSpc_p0.setText(str(a.r_spc[0]))
        self.w.rSpc_p1.setText(str(a.r_spc[1]))
        self.w.rSpc_p2.setText(str(a.r_spc[2]))
        self.w.rSpc_p3.setText(str(a.r_spc[3]))
        self.w.rSpc_p4.setText(str(a.r_spc[4]))
        self.w.rSpc_p5.setText(str(a.r_spc[5]))
        self.w.rSpc_p6.setText(str(a.r_spc[6]))
        self.w.iSpc_p0.setText(str(a.i_spc[0]))
        self.w.iSpc_p1.setText(str(a.i_spc[1]))
        self.w.iSpc_p2.setText(str(a.i_spc[2]))
        self.w.iSpc_p3.setText(str(a.i_spc[3]))
        self.w.iSpc_p4.setText(str(a.i_spc[4]))
        self.w.iSpc_p5.setText(str(a.i_spc[5]))
        self.w.iSpc_p6.setText(str(a.i_spc[6]))
        self.w.baselineOrder.setCurrentIndex(a.n_order)
        self.w.baselineCorrection.setCurrentIndex(a.correct_baseline)
        self.set_autobaseline_pars()
        # end set_proc_pars

    def set_pulse_program(self):
        self.w.pulseProgram.setText(self.nd.nmrdat[self.nd.s][self.nd.e].pulse_program)
        # end set_pulse_program

    # def setrDolphinExport(self):
    #    self.nd.pp.rDolphinExport = self.w.rDolphinExport.isChecked()
    #
    def set_samples_in_combo_box(self):
        self.nd.pp.export_samples_in_rows_cols = self.w.samplesInComboBox.currentIndex()
        # end set_samples_in_combo_box

    def set_scale_spectra(self):
        if (self.nd.pp.pre_proc_fill == False):
            if (self.w.scaleSpectra.isChecked() == True):
                self.nd.pp.flag_scale_spectra = True
                self.w.preProcessingSelect.setCurrentIndex(6)
            else:
                self.nd.pp.flag_scale_spectra = False

        # end set_scale_spectra

    def set_seg_align_pre_proc(self):
        if (self.nd.pp.pre_proc_fill == False):
            n_rows = self.w.segAlignTW.rowCount()
            segStart = np.array([])
            segEnd = np.array([])
            t_start = np.array([])
            t_end = np.array([])
            for k in range(n_rows):
                # t_start = np.array([])
                # t_end   = np.array([])
                try:
                    t_start = np.append(t_start, float(self.w.segAlignTW.item(k, 0).text()))
                    # self.w.segAlignTW.item(k,0).clearContents()
                except:
                    t_start = np.append(t_start, -10000.0)

                try:
                    t_end = np.append(t_end, float(self.w.segAlignTW.item(k, 1).text()))
                    # self.w.segAlignTW.item(k,1).clearContents()
                except:
                    t_end = np.append(t_end, -10000.0)

            # self.w.segAlignTW.clearContents()
            self.w.segAlignTW.setRowCount(0)
            self.w.segAlignTW.setRowCount(n_rows)
            self.nd.pp.pre_proc_fill = True
            for k in np.arange(len(t_start) - 1, -1, -1):  # range(len(t_start)):
                seg_number1 = QTableWidgetItem(2 * k)
                seg_number1.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.w.segAlignTW.setItem(k, 0, seg_number1)
                seg_number2 = QTableWidgetItem(2 * k + 1)
                seg_number2.setTextAlignment(QtCore.Qt.AlignHCenter)
                self.w.segAlignTW.setItem(k, 1, seg_number2)
                if ((t_start[k] > -10000.0) & (t_end[k] > -10000.0)):
                    t_min = min(t_start[k], t_end[k])
                    t_end[k] = max(t_start[k], t_end[k])
                    t_start[k] = t_min
                    segStart = np.append(segStart, t_start[k])
                    segEnd = np.append(segEnd, t_end[k])
                    t_start = np.delete(t_start, k)
                    t_end = np.delete(t_end, k)

                if (t_start[k] > -10000.0):
                    self.w.segAlignTW.item(k, 0).setText(str(t_start[k]))
                    self.w.segAlignTW.setFocus()
                else:
                    self.w.segAlignTW.item(k, 0).setText("")
                    self.w.segAlignTW.setFocus()

                if (t_end[k] > -10000.0):
                    self.w.segAlignTW.item(k, 1).setText(str(t_end[k]))
                    self.w.segAlignTW.setFocus()
                else:
                    self.w.segAlignTW.item(k, 1).setText("")
                    self.w.segAlignTW.setFocus()

            self.nd.pp.pre_proc_fill = False
            sort_idx = np.argsort(segStart)
            self.nd.pp.seg_start = segStart[sort_idx]
            self.nd.pp.seg_end = segEnd[sort_idx]
            self.plot_spc_pre_proc()

        # end set_seg_align_pre_proc

    def set_segmental_alignment(self):
        if (self.nd.pp.pre_proc_fill == False):
            if (self.w.segmentalAlignment.isChecked() == True):
                self.nd.pp.flag_segmental_alignment = True
                self.w.preProcessingSelect.setCurrentIndex(2)
            else:
                self.nd.pp.flag_segmental_alignment = False

        # end set_segmental_alignment

    def set_select_class(self):
        for k in range(len(self.nd.pp.class_select)):
            self.w.selectClassTW.item(k, 1).setText(self.nd.pp.class_select[k])

        # end set_select_class

    def set_sym_j(self):
        cur_idx = self.w.symJ.currentIndex()
        if (cur_idx == 0):
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.symj = True
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.tilt = True
            self.w.tilt.setCurrentIndex(0)
        else:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.symj = False

        # end set_tilt

    def set_tilt(self):
        cur_idx = self.w.tilt.currentIndex()
        if (cur_idx == 0):
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.tilt = True
        else:
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.tilt = False
            self.nd.nmrdat[self.nd.s][self.nd.e].proc.symj = False
            self.w.symJ.setCurrentIndex(1)

        # end set_tilt

    def set_title_file(self):
        self.w.titleFile.setText(self.nd.nmrdat[self.nd.s][self.nd.e].title)
        # end set_title_file

    def setup_processing_parameters(self):
        self.w.nmrSpectrum.setCurrentIndex(4)
        # end setup_processing_parameters

    def set_up_to_bonds(self):
        if len(self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite) == 0:
            self.w.fitUpToBonds.setCurrentIndex(1)
            return

        self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.hsqc_data[
            self.nd.nmrdat[self.nd.s][self.nd.e].hsqc.cur_metabolite].n_bonds = \
            int(self.w.fitUpToBonds.currentText())

        # end set_up_to_bonds

    def set_variance_stabilisation(self):
        if (self.nd.pp.pre_proc_fill == False):
            if (self.w.varianceStabilisation.isChecked() == True):
                self.nd.pp.flag_variance_stabilisation = True
                self.w.preProcessingSelect.setCurrentIndex(7)
            else:
                self.nd.pp.flag_variance_stabilisation = False

        # end set_variance_stabilisation

    def set_variance_stabilisation_options(self):
        if self.w.autoScaling.isChecked():
            self.nd.pp.auto_scaling = True
            self.nd.pp.pareto_scaling = False
            self.nd.pp.g_log_transform = False
        elif self.w.paretoScaling.isChecked():
            self.nd.pp.auto_scaling = False
            self.nd.pp.pareto_scaling = True
            self.nd.pp.g_log_transform = False
        else:
            self.nd.pp.auto_scaling = False
            self.nd.pp.pareto_scaling = False
            self.nd.pp.g_log_transform = True

        self.w.lambdaText.setEnabled(self.nd.pp.g_log_transform)
        self.w.y0Text.setEnabled(self.nd.pp.g_log_transform)
        self.w.lambdaLE.setEnabled(self.nd.pp.g_log_transform)
        self.w.y0LE.setEnabled(self.nd.pp.g_log_transform)
        # end set_variance_stabilisation_options

    def set_var_lambda(self):
        self.nd.pp.var_lambda = float(self.w.lambdaLE.text())
        # end set_var_lambda

    def set_var_y0(self):
        self.nd.pp.var_y0 = float(self.w.y0LE.text())
        # end set_var_lambda

    def set_pan(self):
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.set_zoom_release)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
        try:
            self.w.MplWidget.canvas.figure.canvas.toolbar.pan()
        except:
            pass

        self.zoom_was_on = False
        self.pan_was_on = True

    def set_xlim(self, xlim1=0.006, xlim2=-0.006):
        self.w.MplWidget.canvas.axes.set_xlim((max(xlim1, xlim2), min(xlim1, xlim2)))
        self.show_nmr_spectrum()
        self.vertical_auto_scale()
        # end set_xlim

    def set_xlim2(self, xlim1=0.006, xlim2=-0.006):
        self.w.MplWidget.canvas.axes.set_xlim((max(xlim1, xlim2), min(xlim1, xlim2)))
        self.show_nmr_spectrum()
        # end set_xlim

    def get_xlim(self):
        xlim = self.w.MplWidget.canvas.axes.get_xlim()
        print(xlim)
        # end set_xlim

    def set_ylim(self, ylim1=0, ylim2=1):
        self.w.MplWidget.canvas.axes.set_ylim((min(ylim1, ylim2), max(ylim1, ylim2)))
        self.show_nmr_spectrum()
        self.w.MplWidget.canvas.draw()
        #self.vertical_auto_scale()
        # end set_xlim

    def get_ylim(self):
        ylim = self.w.MplWidget.canvas.axes.get_ylim()
        print(ylim)
        # end set_xlim

    def set_zoom(self):
        try:
            self.w.MplWidget.canvas.figure.canvas.toolbar.zoom()
        except:
            pass

        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.set_zoom_release)
        self.zoom_was_on = True
        self.pan_was_on = False

    def set_zoom_off(self):
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.set_zoom_release)
        cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)

    def set_zoom_release(self, event):
        if (event.button > 1):
            # Right MB click will unzoom the plot
            try:
                self.w.MplWidget.canvas.figure.canvas.toolbar.home()
            except:
                pass

            pyautogui.click(clicks=1)
            # self.w.MplWidget.setFocus()

    def show(self):
        self.w.show()
        # end show

    def show_acquisition_parameters(self):
        self.w.nmrSpectrum.setCurrentIndex(6)
        # end show_acquisition_parameters

    def show_auto_baseline(self):
        self.w.statusBar().clearMessage()
        self.w.statusBar().showMessage("Automatic baseline correction in progress...")
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end show_auto_baseline

    def show_auto_phase(self):
        self.w.statusBar().clearMessage()
        self.w.statusBar().showMessage("Automatic phase correction in progress...")
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end show_auto_phase

    def show_console(self):
        self.w.nmrSpectrum.setCurrentIndex(10)
        # end show_console

    def show_plot_editor(self):
        self.w.nmrSpectrum.setCurrentIndex(11)
        # end show_console

    def show_display_parameters(self):
        self.w.nmrSpectrum.setCurrentIndex(5)
        # end show_display_parameters

    def show_help(self):
        self.w.nmrSpectrum.setCurrentIndex(12)
        # end show_help

    def show_main_window(self):
        if (self.w.isFullScreen() == True):
            self.w.showNormal()
        else:
            self.w.showFullScreen()

        # end show_main_window

    def show_nmr_spectrum(self):
        self.w.nmrSpectrum.setCurrentIndex(0)
        # if (self.w.preprocessing.isChecked() == False):
        #    self.plot_spc()
        # end show_nmr_spectrum

    def show_ph_corr(self):
        self.w.statusBar().clearMessage()
        self.w.statusBar().showMessage(
            "Left Mouse Button (MB) for ph0, Right MB or Left MB + shift for ph1, Middle MB or Left MB + Cmd to set pivot")
        #    #"Left Mouse Button (MB) for ph0, Right MB or Left MB + shift for ph1, Middle MB or Left MB + Cmd to set pivot        |        Press Alt+p to exit    |   Press Alt+z to zoom")
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end show_ph_corr

    def show_ph_corr2d(self):
        self.w.statusBar().clearMessage()
        self.w.statusBar().showMessage(
            "2D Interactive Phase Correction")
        #    "Press: Alt+k to pick row/col | Alt+e to empty selection | Alt+r to remove last row/col | Alt+1 for horizontal phase correction | Alt+2 for vertical phase correction | Alt+x to eXit")
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end show_ph_corr2d

    def show_ph_corr2d_1d(self, dim=0):
        self.w.statusBar().clearMessage()
        self.w.statusBar().showMessage(
            "Left Mouse Button (MB) for ph0, Right MB or Left MB + shift for ph1, Middle MB or Left MB + Cmd to set pivot")
        #    "Left Mouse Button (MB) for ph0, Right MB or Left MB + shift for ph1, Middle MB or Left MB + Cmd to set pivot | Press: Alt+Shift+p to apply phCorr | Alt+Shift+x to cancel | Alt+z to zoom")
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end show_ph_corr2d

    def show_ph_zoom(self):
        self.w.statusBar().clearMessage()
        self.w.statusBar().showMessage(
            "Left Mouse Button (MB) for rectangular zoom, Right MB to unzoom")
        #    "Left Mouse Button (MB) for rectangular zoom, Right MB to unzoom        |        Press Alt+z to exit to phase correction")
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end show_ph_zoom

    def show_pre_processing(self):
        self.w.preProcPeak.setHidden(False)
        self.w.preProcessingTab.setHidden(False)
        self.w.peakPickingTab.setHidden(True)
        self.w.preProcPeak.setTabEnabled(0, True)
        self.w.preProcPeak.setTabEnabled(1, False)
        self.w.preProcPeak.setTabEnabled(2, False)
        self.w.preProcessingGroupBox.setHidden(False)
        self.w.preProcessingSelect.setHidden(False)
        self.w.preProcessingWidget.setHidden(False)
        self.w.runPreProcessingButton.setHidden(False)
        self.w.resetPreProcessingButton.setHidden(False)
        self.w.writeScriptButton.setHidden(False)
        self.set_export_method()
        # self.set_select_class()
        self.plot_spc_pre_proc()
        # end show_pre_processing

    def show_pulse_program(self):
        self.w.nmrSpectrum.setCurrentIndex(8)
        # end show_pulse_program

    def show_spline_baseline_pick(self):
        self.w.statusBar().clearMessage()
        self.w.statusBar().showMessage("Left click to add baseline point, right click or double click to exit peak picking mode")

    def show_title_file_information(self):
        self.w.nmrSpectrum.setCurrentIndex(7)
        # end show_title_file_information

    def show_version(self):
        self.w.statusBar().clearMessage()
        self.w.statusBar().showMessage("MetaboLabPy " + self.__version__)
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end show_version

    def splash(self):
        nmr_dir = os.path.split(inspect.getmodule(nmrDataSet).__file__)[0]
        base_dir = os.path.split(nmr_dir)[0]
        p_name = os.path.join(base_dir, "png")
        cf = nmrConfig.NmrConfig()
        cf.read_config()
        if cf.mode == 'system':
            if darkdetect.isDark():
                splash_pix = QPixmap(os.path.join(p_name, "metabolabpy_dark.png"))
            else:
                splash_pix = QPixmap(os.path.join(p_name, "metabolabpy.png"))
        elif cf.mode == 'dark':
            splash_pix = QPixmap(os.path.join(p_name, "metabolabpy_dark.png"))
        else:
            splash_pix = QPixmap(os.path.join(p_name, "metabolabpy.png"))

        splash = QSplashScreen(splash_pix)
        splash.setMask(splash_pix.mask())
        # adding progress bar
        splash.show()
        QCoreApplication.processEvents()
        max_time = 5
        max_range = 100
        time_inc = max_range
        for i in range(max_range):
            # Simulate something that takes time
            time.sleep(max_time / float(max_range))

        splash.close()
        # end splash

    #def start_notebook(self):
    #    try:
    #        self.p.terminate()
    #        sleep(2)
    #    except:
    #        pass
    #
    #    if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
    #        jupyterthemes.install_theme('chesterish')
    #    else:
    #        jupyterthemes.install_theme('grade3')
    #
    #    nmr_dir = os.path.split(inspect.getmodule(nmrDataSet).__file__)[0]
    #    base_dir = os.path.split(nmr_dir)[0]
    #    jupyter_path = os.path.join(base_dir, "nmr", "jupyter")
    #    jobs = []
    #    print("-----------------")
    #    self.process = multiprocess.Process(target=notebookapp.main,args=([jupyter_path, '--ip=127.0.0.1', '--port=9997'],))
    #    #self.process = multiprocess.Process(target=notebookapp.main,args=([jupyter_path, '--no-browser', '--ip=127.0.0.1', '--port=9997', '--NotebookApp.token=''', '--NotebookApp.password='''],))
    #    print('=======================')
    #    jobs.append(self.process)
    #    print('#########################')
    #    self.process.start()
    #    print('//////////////////////////')
    #    sleep(2)
    #    print('__________________________')
    #    self.w.helpView.setUrl('http://127.0.0.1:9997')
    #    self.w.nmrSpectrum.setCurrentIndex(12)
    #    # end startNotebook

    #def stop_notebook(self):
    #    try:
    #        self.process.terminate()
    #        sleep(2)
    #    except:
    #        pass
    #
    #    self.reset_help()
    #    # end stop_notebook

    def start_stop_ph_corr(self):
        s = self.nd.s
        e = self.nd.e
        if self.nd.nmrdat[s][e].projected_j_res:
            if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
                txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
                err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
            else:
                txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
                err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

            self.w.nmrSpectrum.setCurrentIndex(10)
            code_out = io.StringIO()
            code_err = io.StringIO()
            sys.stdout = code_out
            sys.stderr = code_err
            self.w.console.setTextColor(err_col)
            print("This is a pojected jRes spectrum, phase correction is impossible")
            self.w.console.append(code_out.getvalue())
            self.w.console.append(code_err.getvalue())
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            code_out.close()
            code_err.close()
            self.w.console.verticalScrollBar().setValue(self.w.console.verticalScrollBar().maximum())
            return

        if (self.nd.nmrdat[s][e].dim == 1):
            try:
                self.zoom_was_on = True
                self.w.MplWidget.canvas.figure.canvas.toolbar.zoom()
            except:
                pass

            self.set_zoom_off()
            if (self.ph_corr_active == False):
                self.ph_corr.spc = self.nd.nmrdat[s][e].spc
                self.ph_corr.spc_max = max(max(abs(self.ph_corr.spc)))
                self.ph_corr.piv_points = self.nd.nmrdat[s][e].ppm2points(self.ph_corr.pivot, 0)
                cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_ph_corr_click)
                cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_ph_corr_release)
                self.ph_corr_active = True
                self.show_ph_corr()
                # self.w.MplWidget.canvas.figure.canvas.toolbar.setEnabled(False)
                self.w.exitPhCorr1d.setVisible(True)
                self.w.zoomPhCorr1d.setVisible(True)
                self.w.exitZoomPhCorr1d.setVisible(False)
                self.update_gui()
                self.ph_corr_plot_spc()
            else:
                cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_ph_corr_click)
                cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_ph_corr_release)
                cid = self.w.MplWidget.canvas.mpl_disconnect(cid)
                cid2 = self.w.MplWidget.canvas.mpl_disconnect(cid2)
                self.ph_corr_active = False
                # self.w.MplWidget.canvas.figure.canvas.toolbar.setEnabled(True)
                self.show_version()
                self.w.exitPhCorr1d.setVisible(False)
                self.w.zoomPhCorr1d.setVisible(False)
                self.w.exitZoomPhCorr1d.setVisible(False)
                self.update_gui()
                self.nd.ft()
                self.plot_spc()
                self.set_zoom_off()
                # self.set_zoom()
                # print("setted Zoom!")
                cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.set_zoom_release)

        else:  # dim == 2
            # try:
            #    self.zoom_was_on = True
            #    self.w.MplWidget.canvas.figure.canvas.toolbar.zoom()
            # except:
            #    pass
            #
            # self.set_zoom_off()
            if (self.ph_corr_active == False):
                self.w.pickRowColPhCorr2d.setVisible(True)
                self.w.emptyRowColPhCorr2d.setVisible(True)
                self.w.removeRowColPhCorr2d.setVisible(True)
                self.w.horzPhCorr2d.setVisible(True)
                self.w.vertPhCorr2d.setVisible(True)
                self.w.exitPhCorr2d.setVisible(True)
                self.ph_corr_active = True
                self.show_ph_corr2d()
            else:
                self.empty_col_row()
                self.w.pickRowColPhCorr2d.setVisible(False)
                self.w.emptyRowColPhCorr2d.setVisible(False)
                self.w.removeRowColPhCorr2d.setVisible(False)
                self.w.horzPhCorr2d.setVisible(False)
                self.w.vertPhCorr2d.setVisible(False)
                self.w.exitPhCorr2d.setVisible(False)
                self.ph_corr_active = False
                self.show_version()
                # self.set_zoom_off()
                # self.set_zoom()
                cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.set_zoom_release)

        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end start_stop_ph_corr

    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old
        # end stdoutIO

    def sub_lists(self, l):
        lists = [[]]
        for i in range(len(l) + 1):
            for j in range(i):
                lists.append(l[j: i])
        return lists

    def tutorials(self):
        # url = "http://beregond.bham.ac.uk/~ludwigc/tutorials"
        f_name = os.path.join(os.path.dirname(__file__), "web", "tutorials", "index.html")
        url = "file:///" + f_name.replace('\\', '/')
        self.w.helpView.setUrl(url)
        self.w.nmrSpectrum.setCurrentIndex(12)
        # end tutorials

    def update_metabolabpy(self):
        os.execl(sys.executable, sys.executable.replace(' ', '" "'), *['-m', 'pip', 'install', '--upgrade', 'metabolabpy', 'qtmetabolabpy', 'metabolabpytools'])
        # end update_metabolabpy


    def update_plot_editor(self):
        self.w.plotTop.setChecked(self.cf.print_top_axis)
        if self.w.plotTop.isChecked():
            self.w.plotTop.setStyleSheet("background-color: black")
        else:
            self.w.plotTop.setStyleSheet("background-color: darkgrey")
        self.w.plotLeft.setChecked(self.cf.print_left_axis)
        if self.w.plotLeft.isChecked():
            self.w.plotLeft.setStyleSheet("background-color: black")
        else:
            self.w.plotLeft.setStyleSheet("background-color: darkgrey")
        self.w.plotRight.setChecked(self.cf.print_right_axis)
        if self.w.plotRight.isChecked():
            self.w.plotRight.setStyleSheet("background-color: black")
        else:
            self.w.plotRight.setStyleSheet("background-color: darkgrey")
        self.w.plotBottom.setChecked(self.cf.print_bottom_axis)
        if self.w.plotBottom.isChecked():
            self.w.plotBottom.setStyleSheet("background-color: black")
        else:
            self.w.plotBottom.setStyleSheet("background-color: darkgrey")

        self.w.plotBackground.setChecked(self.cf.print_background)
        self.w.useStandardPlotColours.setChecked(self.cf.print_standard_colours)
        self.w.useDatasetPlotColours.setChecked(self.cf.print_dataset_colours)
        self.w.plotLightMode.setChecked(self.cf.print_light_mode)
        self.w.plotDarkMode.setChecked(not self.cf.print_light_mode)
        self.w.spectrumLineWidth.setValue(self.cf.print_spc_linewidth)
        self.w.axesLineWidth.setValue(self.cf.print_axes_linewidth)
        self.w.axesFontSize.setValue(self.cf.print_ticks_font_size)
        self.w.labelFontSize.setValue(self.cf.print_label_font_size)
        self.w.printStackedPlot.setChecked(self.cf.print_stacked_plot)
        self.w.printAutoScale.setChecked(self.cf.print_auto_scale)
        self.w.printRepeatAxes.setChecked(self.cf.print_stacked_plot_repeat_axes)
        self.w.aspectRatioNMR.setText(str(self.cf.print_nmr_spectrum_aspect_ratio))
        self.w.aspectRatioHSQCPeak.setText(str(self.cf.print_hsqc_peak_aspect_ratio))
        self.w.aspectRatioNMRMultiplet.setText(str(self.cf.print_hsqc_multiplet_aspect_ratio))
        self.w.printSpectrumLabel.setChecked(self.cf.print_label)
        self.nd.cf = self.cf
        # end update_plot_editor

    def update_gui(self):
        self.w.setBox.valueChanged.disconnect()
        self.w.expBox.valueChanged.disconnect()
        self.w.expBox.setValue(self.nd.e + 1)
        self.w.setBox.setValue(self.nd.s + 1)
        self.w.setBox.valueChanged.connect(self.change_data_set_exp)
        self.w.expBox.valueChanged.connect(self.change_data_set_exp)
        self.set_disp_pars()
        self.set_proc_pars()
        self.set_acq_pars()
        self.set_title_file()
        self.set_pulse_program()
        self.w.expBox.setValue(self.nd.e + 1)
        self.w.invertMatrix_1.setChecked(self.nd.nmrdat[self.nd.s][self.nd.e].proc.invert_matrix[0])
        self.w.invertMatrix_2.setChecked(self.nd.nmrdat[self.nd.s][self.nd.e].proc.invert_matrix[1])
        #self.update_plot_editor()
        if (self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1):
            self.w.preprocessing.setVisible(True)
            self.w.peakPicking.setVisible(True)
            self.w.splinebaseline.setVisible(True)
        else:
            self.w.preprocessing.setChecked(False)
            self.w.preprocessing.setVisible(False)
            self.w.peakPicking.setChecked(False)
            self.w.peakPicking.setVisible(False)
            self.w.splinebaseline.setChecked(False)
            self.w.splinebaseline.setVisible(False)

        if self.nd.nmrdat[self.nd.s][self.nd.e].dim > 1:
            if self.nd.nmrdat[self.nd.s][self.nd.e].acq.pul_prog_name.find("hsqc") > 0 or self.nd.nmrdat[self.nd.s][
                self.nd.e].acq.pul_prog_name.find("hmqc") > 0:
                self.w.hsqcAnalysis.setVisible(True)  # develop set true

            else:
                self.w.hsqcAnalysis.setChecked(False)
                self.w.hsqcAnalysis.setVisible(False)

        else:
            self.w.hsqcAnalysis.setChecked(False)
            self.w.hsqcAnalysis.setVisible(False)

        self.w.multipletAnalysis.setVisible(False)
        #self.w.isotopomerAnalysis.setVisible(False)
        self.update_plot_editor()
        return "updated GUI"
        # end update_gui

    def update_metabolabpy1(self):
        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        cmd_msg = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'metabolabpy'],
                                 stdout=subprocess.PIPE)
        print(cmd_msg.stdout.decode('utf-8'))
        print("Update finished.\nPlease restart MetaboLabPy to use the new version.")
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        self.w.console.setTextColor(err_col)
        self.w.console.append(code_err.getvalue())
        code_out.close()
        code_err.close()
        self.show_console()
        # end update_metabolabpy


    def update_plot_top(self):
        self.cf.print_top_axis = self.w.plotTop.isChecked()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_plot_top

    def update_plot_left(self):
        self.cf.print_left_axis = self.w.plotLeft.isChecked()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_plot_left

    def update_plot_right(self):
        self.cf.print_right_axis = self.w.plotRight.isChecked()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_plot_right

    def update_plot_bottom(self):
        self.cf.print_bottom_axis = self.w.plotBottom.isChecked()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_plot_bottom

    def update_plot_background(self):
        self.cf.print_background = self.w.plotBackground.isChecked()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_plot_background

    def update_use_standard_plot_colours(self):
        self.cf.print_standard_colours = self.w.useStandardPlotColours.isChecked()
        self.cf.print_dataset_colours = not self.w.useStandardPlotColours.isChecked()
        self.w.useDatasetPlotColours.setChecked(not self.w.useStandardPlotColours.isChecked())
        self.cf.save_config()
        self.update_plot_editor()
        # end update_use_standard_plot_colours

    # self.w.useDatasetPlotColours.clicked.connect(update_use_dataset_plot_colours)
    def update_use_dataset_plot_colours(self):
        self.cf.print_dataset_colours = self.w.useDatasetPlotColours.isChecked()
        self.cf.print_standard_colours = not self.w.useDatasetPlotColours.isChecked()
        self.w.useStandardPlotColours.setChecked(not self.w.useDatasetPlotColours.isChecked())
        self.cf.save_config()
        self.update_plot_editor()
        # end update_use_dataset_plot_colours

    # self.w.plotLightMode.clicked.connect(self.update_plot_light_mode)
    def update_plot_light_mode(self):
        self.cf.print_light_mode = self.w.plotLightMode.isChecked()
        self.w.plotDarkMode.setChecked(not self.w.plotLightMode.isChecked())
        self.cf.save_config()
        self.update_plot_editor()
        # end update_plot_light_mode

    # self.w.plotDarkMode.clicked.connect(self.update_plot_dark_mode)
    def update_plot_dark_mode(self):
        self.cf.print_light_mode = not self.w.plotDarkMode.isChecked()
        self.w.plotLightMode.setChecked(not self.w.plotDarkMode.isChecked())
        self.cf.save_config()
        self.update_plot_editor()
        # end update_plot_dark_mode

    def update_print_stacked_plot(self):
        self.cf.print_stacked_plot = self.w.printStackedPlot.isChecked()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_print_stacked_plot

    def update_print_spectrum_label(self):
        self.cf.print_label = self.w.printSpectrumLabel.isChecked()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_print_stacked_plot

    def update_print_auto_scale(self):
        self.cf.print_auto_scale = self.w.printAutoScale.isChecked()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_print_auto_scale

    def update_print_repeat_axes(self):
        self.cf.print_stacked_plot_repeat_axes = self.w.printRepeatAxes.isChecked()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_print_repeat_axes

    # self.w.spectrumLineWidth.valueChanged.connect(self.update_spectrum_line_width)
    def update_spectrum_line_width(self):
        self.cf.print_spc_linewidth = self.w.spectrumLineWidth.value()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_spectrum_line_width

    # self.w.axesLineWidth.valueChanged.connect(self.update_axes_line_width)
    def update_axes_line_width(self):
        self.cf.print_axes_linewidth = self.w.axesLineWidth.value()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_

    # self.w.axesFontSize.valueChanged.connect(self.update_axes_font_size)
    def update_axes_font_size(self):
        self.cf.print_ticks_font_size = self.w.axesFontSize.value()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_axes_font_size

    def update_aspect_ratio_nmr(self):
        value = self.w.aspectRatioNMR.text()
        if value == 'auto' or value == 'a4_landscape' or value == 'a4_portrait':
            self.cf.print_nmr_spectrum_aspect_ratio = value
        else:
            try:
                value = float(value)
            except:
                value = 'auto'

            self.cf.print_nmr_spectrum_aspect_ratio = value

        self.cf.save_config()
        self.update_plot_editor()
        # end update_aspect_ratio_nmr

    def update_aspect_ratio_hsqc_peak(self):
        value = self.w.aspectRatioHSQCPeak.text()
        if value == 'auto' or value == 'a4_landscape' or value == 'a4_portrait':
            self.cf.print_hsqc_peak_aspect_ratio = value
        else:
            try:
                value = float(value)
            except:
                value = 'auto'

            self.cf.print_hsqc_peak_aspect_ratio = value

        self.cf.save_config()
        self.update_plot_editor()
    # end update_aspect_ratio_hsqc_peak

    def update_aspect_ratio_nmr_multiplet(self):
        value = self.w.aspectRatioNMRMultiplet.text()
        if value == 'auto' or value == 'a4_landscape' or value == 'a4_portrait':
            self.cf.print_hsqc_multiplet_aspect_ratio = value
        else:
            try:
                value = float(value)
            except:
                value = 'auto'

            self.cf.print_hsqc_multiplet_aspect_ratio = value

        self.cf.save_config()
        self.update_plot_editor()
        # end update_aspect_ratio_nmr_multiplet

    def update_label_font_size(self):
        self.cf.print_label_font_size = self.w.labelFontSize.value()
        self.cf.save_config()
        self.update_plot_editor()
        # end update_label_font_size


    def vertical_auto_scale(self):
        if (self.nd.nmrdat[self.nd.s][self.nd.e].dim == 1):
            lines = self.w.MplWidget.canvas.axes.get_lines()
            bottom, top = np.inf, -np.inf
            for line in lines:
                new_bottom, new_top = self.get_bottom_top(line)
                if new_bottom < bottom:
                    bottom = new_bottom

                if new_top > top:
                    top = new_top

        else:
            bottom = self.nd.nmrdat[self.nd.s][self.nd.e].ppm2[0]
            top = self.nd.nmrdat[self.nd.s][self.nd.e].ppm2[-1]

        if bottom != np.inf and top != -np.inf:
            self.w.MplWidget.canvas.axes.set_ylim(bottom, top)

        self.w.MplWidget.canvas.draw()

        # end vertical_auto_scale

    def horizontal_auto_scale(self):
        left = self.nd.nmrdat[self.nd.s][self.nd.e].ppm1[0]
        right = self.nd.nmrdat[self.nd.s][self.nd.e].ppm1[-1]
        self.w.MplWidget.canvas.axes.set_xlim(left, right)
        self.w.MplWidget.canvas.draw()

        # end horizontal_auto_scale

    def vert_ph_corr_2d(self):
        s = self.nd.s
        e = self.nd.e
        self.ph_corr.n_dims = 2
        self.ph_corr.dim = 1
        n_lines = len(self.ph_corr.spc_col_pts)
        if n_lines > 0:
            npts0 = len(self.nd.nmrdat[s][e].spc)
            npts = len(self.nd.nmrdat[s][e].spc[0])
            self.ph_corr.spc = np.zeros((n_lines, npts0), dtype='complex')
            spc1 = np.copy(self.nd.nmrdat[s][e].spc)
            spc1 = np.ndarray.transpose(spc1)
            for k in range(n_lines):
                spc = np.array([spc1[npts - self.ph_corr.spc_col_pts[k]]])
                spc = self.hilbert(spc)
                self.ph_corr.spc[k] = spc[0]

            self.ph_corr.ppm = self.nd.nmrdat[s][e].ppm2
            if self.ph_corr.pivot_points2d[1] < 0:
                self.ph_corr.pivot_points2d[1] = int(len(self.ph_corr.ppm) / 2)
                self.ph_corr.pivot2d[1] = self.nd.nmrdat[s][e].points2ppm(self.ph_corr.pivot_points2d[1], 1)

        self.show_ph_corr2d_1d(self.ph_corr.dim)
        self.ph_corr.spc_max = np.max(np.max(np.abs(self.ph_corr.spc)))
        try:
            zwo = True
            self.w.MplWidget.canvas.figure.canvas.toolbar.zoom()
        except:
            pass

        self.set_zoom_off()
        self.ph_corr.max_ph0 = 90.0
        self.ph_corr.max_ph1 = 90.0
        cid = self.w.MplWidget.canvas.mpl_connect('button_press_event', self.on_ph_corr_click_2d)
        cid2 = self.w.MplWidget.canvas.mpl_connect('button_release_event', self.on_ph_corr_release_2d)
        # self.w.actionApplyPhCorr.triggered.connect(self.apply_2d_ph_corr)
        # self.w.actionCancelPhCorr.triggered.connect(self.cancel2dPhCorr)
        self.ph_corr_plot_spc_2d(False)
        self.w.pickRowColPhCorr2d.setVisible(False)
        self.w.emptyRowColPhCorr2d.setVisible(False)
        self.w.removeRowColPhCorr2d.setVisible(False)
        self.w.horzPhCorr2d.setVisible(False)
        self.w.vertPhCorr2d.setVisible(False)
        self.w.zoomPhCorr2d.setVisible(True)
        self.w.applyPhCorr2d.setVisible(True)
        self.w.cancelPhCorr2d.setVisible(True)
        self.w.exitPhCorr2d.setVisible(False)
        self.w.exitZoomPhCorr2d.setVisible(False)
        self.ph_corr_plot_spc_2d(False)
        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end vert_ph_corr_2d

    def zero_acq_pars(self):
        self.w.acqPars.setText("")
        # end zero_acq_pars

    def zero_console(self):
        self.w.console.setText("")
        # end zero_console

    def zero_disp_pars(self):
        self.w.posColR.setText("")
        self.w.posColG.setText("")
        self.w.posColB.setText("")
        self.w.negColR.setText("")
        self.w.negColG.setText("")
        self.w.negColB.setText("")
        self.w.nLevels.setText("")
        self.w.minLevel.setText("")
        self.w.maxLevel.setText("")
        self.w.spcOffset.setText("")
        self.w.spcScale.setText("")
        self.w.xLabel.setText("")
        self.w.yLabel.setText("")
        self.w.spcLabel.setText("")
        self.w.posCol.setCurrentIndex(0)
        self.w.negCol.setCurrentIndex(0)
        self.w.axisType1.setCurrentIndex(0)
        self.w.axisType2.setCurrentIndex(0)
        self.w.displaySpc.setCurrentIndex(0)
        self.w.phRefDS.setValue(0)
        self.w.phRefExp.setValue(0)
        # end zero_disp_pars

    def zero_proc_pars(self):
        self.w.zeroFilling.setText("")
        self.w.zeroFilling_2.setText("")
        self.w.lb.setText("")
        self.w.gb.setText("")
        self.w.ssb.setText("")
        self.w.lb_2.setText("")
        self.w.gb_2.setText("")
        self.w.ssb_2.setText("")
        self.w.ph0.setText("")
        self.w.ph1.setText("")
        self.w.ph0_2.setText("")
        self.w.ph1_2.setText("")
        self.w.polyOrder.setText("")
        self.w.extrapolationSize.setText("")
        self.w.windowSize.setText("")
        self.w.fidOffsetCorrection.setText("")
        self.w.windowFunction.setCurrentIndex(0)
        self.w.windowFunction_2.setCurrentIndex(0)
        self.w.phaseCorrection.setCurrentIndex(0)
        self.w.phaseCorrection_2.setCurrentIndex(0)
        self.w.waterSuppression.setCurrentIndex(0)
        self.w.winType.setCurrentIndex(0)
        self.w.gibbs.setCurrentIndex(0)
        self.w.gibbs_2.setCurrentIndex(0)
        # end zero_proc_pars

    def zero_pulse_program(self):
        self.w.pulseProgram.setText("")
        # end zero_pulse_program

    def zero_script(self):
        self.w.script.setText("")
        # end zero_console

    def zero_title_file(self):
        self.w.titleFile.setText("")
        # end zero_title_file

    def zoom_ph_corr(self):
        if (self.ph_corr_active == True):
            try:
                self.set_zoom()
            except:
                pass

            if (self.zoom == False):
                # Enable zoom
                self.zoom = True
                self.show_ph_zoom()
                if self.ph_corr.n_dims == 1:
                    self.w.exitPhCorr1d.setVisible(False)
                    self.w.zoomPhCorr1d.setVisible(False)
                    self.w.exitZoomPhCorr1d.setVisible(True)
                else:
                    self.w.zoomPhCorr2d.setVisible(False)
                    self.w.applyPhCorr2d.setVisible(False)
                    self.w.cancelPhCorr2d.setVisible(False)
                    self.w.exitZoomPhCorr2d.setVisible(True)

            else:
                # Disable zoom
                self.zoom = False
                if self.ph_corr.n_dims == 1:
                    self.show_ph_corr()
                    self.w.exitPhCorr1d.setVisible(True)
                    self.w.zoomPhCorr1d.setVisible(True)
                    self.w.exitZoomPhCorr1d.setVisible(False)
                    self.set_zoom_off()
                else:
                    self.show_ph_corr2d_1d()
                    self.w.zoomPhCorr2d.setVisible(True)
                    self.w.applyPhCorr2d.setVisible(True)
                    self.w.cancelPhCorr2d.setVisible(True)
                    self.w.exitZoomPhCorr2d.setVisible(False)
                    self.set_zoom_off()

        self.show_acquisition_parameters()
        self.show_nmr_spectrum()
        # end zoom_ph_corr

    def _download_requested(self, download_item) -> None:
        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        dialog = QFileDialog(self.w)
        path = dialog.getSaveFileName(dialog, "Save File", os.path.join(download_item.downloadDirectory(), download_item.downloadFileName()))
        if path[0]:
            download_item.setDownloadDirectory(os.path.split(path[0])[0])
            print(f"downloading file to:( {download_item.downloadDirectory()} )")
            download_item.accept()
            self.download_item = download_item
            self.download_item.isFinishedChanged.connect(self._download_finished)
        else:
            print("Download canceled")

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        self.w.console.setTextColor(err_col)
        self.w.console.append(code_err.getvalue())
        code_out.close()
        code_err.close()
        self.w.nmrSpectrum.setCurrentIndex(10)

    def _download_finished(self) -> None:
        code_out = io.StringIO()
        code_err = io.StringIO()
        sys.stdout = code_out
        sys.stderr = code_err
        print("Download complete")
        if self.w.autoUnzip.isChecked() == True:
            f_name, fExt = os.path.splitext(self.download_item.downloadFileName())
            if fExt == '.zip':
                print('Extracting .zip-file')
                with zipfile.ZipFile(
                        os.path.join(self.download_item.downloadDirectory(), self.download_item.downloadFileName()),
                        'r') as zip_ref:
                    zip_ref.extractall(os.path.join(self.download_item.downloadDirectory(), f_name))

                print('.zip-file extraction finished')
                os.remove(os.path.join(self.download_item.downloadDirectory(), self.download_item.downloadFileName()))


        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if self.cf.mode == 'dark' or (self.cf.mode == 'system' and darkdetect.isDark()):
            txt_col = QColor.fromRgbF(1.0, 1.0, 1.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.5, 0.5, 1.0)
        else:
            txt_col = QColor.fromRgbF(0.0, 0.0, 0.0, 1.0)
            err_col = QColor.fromRgbF(1.0, 0.0, 0.0, 1.0)

        self.w.console.setTextColor(txt_col)
        self.w.console.append(code_out.getvalue())
        self.w.console.setTextColor(err_col)
        self.w.console.append(code_err.getvalue())
        code_out.close()
        code_err.close()
        self.w.nmrSpectrum.setCurrentIndex(10)


