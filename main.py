# -*- coding: utf-8 -*-

"""
マクロ用csvが保存されているパスを保存する関数path_settingを追加
CSV_PATHの宣言を変更(Toolのメッセージ機能を使いたかったのでToolよりも後ろになってしまいました)
"""

from __future__ import unicode_literals

import uno, unohelper
import platform
import traceback
import os
import csv
import re
import codecs

from com.sun.star.drawing.CircleKind import FULL
from com.sun.star.awt.FontWeight import BOLD, NORMAL, THIN
from com.sun.star.drawing.PolygonFlags import NORMAL, CONTROL
from com.sun.star.drawing.TextVerticalAdjust import CENTER as X_CENTER
from com.sun.star.drawing.TextVerticalAdjust import TOP
from com.sun.star.drawing.TextHorizontalAdjust import CENTER as Y_CENTER
from com.sun.star.drawing.TextHorizontalAdjust import LEFT
from com.sun.star.awt.PosSize import POS, SIZE, POSSIZE
from com.sun.star.awt.PushButtonType import OK, CANCEL
from com.sun.star.awt.MessageBoxType import MESSAGEBOX, ERRORBOX
from com.sun.star.form.FormButtonType import URL
#from com.sun.star.system import SystemShellExecute
from com.sun.star.lang import XComponent
from com.sun.star.beans import PropertyValue

from com.sun.star.awt import XKeyHandler
from com.sun.star.awt import XMessageBox


# global vars
MACRO_VERSION = "alpha"
toan_list = []
subject = 50
MACRO_PATH = "main.py"
# TODO: pack as extension
# MACRO_PATH = "toshin.tensaku-macro.main"

class Tool:
    """
    rgbをint型に変換
    """
    @staticmethod
    def convert_rgb_into_int(rgb):
        return (rgb[0] & 255) << 16 | (rgb[1] & 255) << 8 | (rgb[2] & 255)

    """
    デザインモードを設定する
    """
    @staticmethod
    def setDesignMode(Document, status):
        Controller = Document.getCurrentController()
        Controller.setFormDesignMode(status)

    """
    メッセージボックスを表示する
    """
    @staticmethod
    def MsgBox(message, title="Debug Info", MsgType=MESSAGEBOX):
        """shows message"""
        Window = XSCRIPTCONTEXT.getDesktop().getCurrentFrame().getContainerWindow()
        Toolkit = Window.getToolkit()
        MsgBox = Toolkit.createMessageBox(Window, MsgType, 1, title, message)
        return MsgBox.execute()

    """
    URLのパラメータを処理する
    """
    @staticmethod
    def get_param(url):
        param_str_list = url[url.find("?"):].split("&")
        param_dict = {}

        for param_str in param_str_list:
            param_list = param_str.split("=")
            param_dict[param_list[0]] = param_list[1]

        return param_dict

class ShomonStatus:
    """
    小問の採点ステータスのなんちゃって構造
    """
    NONE = 0
    CIRCLE = 1
    X = 2
    TRIANGLE = 3

class InvalidPageCountError(Exception):
    """ページ数不一致"""
    pass

class InvalidParameterError(Exception):
    """パラメータ不一致"""
    pass

# ***********************************************************
#  Shape
#   - class CircleShape
#   - class BezierCircleShape
#   - class XShape
#   - class BezierXShape
#   - class TriangleShape
#   - class BezierTriangleShape
#   - class TextField
#   - class GuideLine
#   - class Inputbox
# ***********************************************************

class CircleShape:

    """
    widthとheightは定数として用意
    size_rateを用いて一律に変更される
    """
    def __init__(self, Document, page_index, Layer, pos_x, pos_y, max_score, size_rate=1.0):
        self.__Document = Document
        self.__page_index = page_index
        self.__Layer = Layer
        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.__width = 1200
        self.__height = 1200
        self.__max_score = max_score
        self.__size_rate = size_rate

        self.__draw()

    """
    Pageはマクロを適用するページを、CircleShapeは丸一つを表す
    """
    def __create_circle(self):
        self.__Page = self.__Document.getDrawPages().getByIndex(self.__page_index)
        self.__CircleShape = self.__Document.createInstance("com.sun.star.drawing.EllipseShape")

    """
    位置とサイズに関する構造体
    """
    def __create_struct(self):
        Point = uno.createUnoStruct("com.sun.star.awt.Point")
        Size = uno.createUnoStruct("com.sun.star.awt.Size")
        Point.X = self.__pos_x
        Point.Y = self.__pos_y
        Size.Width = self.__width * self.__size_rate
        Size.Height = self.__height * self.__size_rate
        return Point, Size

    """
    引数はデフォルトで指定
    丸の図形を記述
    """
    def __set_circle(
        self,
        line_width=50, line_color=(255, 0, 0), line_transparence=20,
        fill_transparence=100, circle_kind=FULL
    ):
        self.__CircleShape.LineWidth = line_width
        self.__CircleShape.LineColor = Tool.convert_rgb_into_int(line_color)
        self.__CircleShape.LineTransparence = line_transparence
        self.__CircleShape.FillTransparence = fill_transparence
        self.__CircleShape.CircleKind = circle_kind
        self.__CircleShape.MoveProtect = True
        self.__CircleShape.SizeProtect = True

    """
    引数はデフォルトで指定
    丸の中の数字を記述している
    """
    def __set_score(
        self,
        font_color=(255, 0, 0), font_size=24, font_weight=BOLD, font_name="Arial",
        text_vertical_adjust=X_CENTER, text_horizontal_adjust=Y_CENTER,
    ):
        self.__CircleShape.String = str(self.__max_score)
        self.__CircleShape.CharColor = Tool.convert_rgb_into_int(font_color)
        self.__CircleShape.CharHeight = font_size * self.__size_rate
        self.__CircleShape.CharWeight = font_weight
        self.__CircleShape.CharFontName = font_name
        self.__CircleShape.TextVerticalAdjust = text_vertical_adjust
        self.__CircleShape.TextHorizontalAdjust = text_horizontal_adjust

    """
    処理をまとめている
    特に、Page.addはPageに図形を加える
    """
    def __draw(self):
        self.__create_circle()
        self.__CircleShape.Position, self.__CircleShape.Size = self.__create_struct()
        self.__set_circle()
        self.__Page.add(self.__CircleShape)
        self.__Document.getLayerManager().attachShapeToLayer( self.__CircleShape, self.__Layer )
        self.__set_score()

    """
    public method
    図形を削除する
    """
    def remove(self):
        self.__Page.remove(self.__CircleShape)

class BezierCircleShape:

    '''
    コンストラクタ
    '''
    def __init__(self, Document, page_index, Layer, pos_x, pos_y, max_score, size_rate=1.0):
        self.__Document = Document
        self.__page_index = page_index
        self.__Layer = Layer
        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.__max_score = max_score
        self.__size_rate = size_rate

        self.__draw()

    '''
    インスタンスメソッド
    '''
    def __create_beziercircle(self):
        self.__Page = self.__Document.getDrawPages().getByIndex(self.__page_index)
        self.__BezierCircleShape = self.__Document.createInstance("com.sun.star.drawing.OpenBezierShape")
        self.__BezierCoords = uno.createUnoStruct("com.sun.star.drawing.PolyPolygonBezierCoords")

    '''
    インスタンスメソッド
    '''
    def __create_struct(self):
        Coordinates = [uno.createUnoStruct("com.sun.star.awt.Point") for _ in range(4)]
        Coordinates[0].X = self.__pos_x + 0.56*1200*self.__size_rate
        Coordinates[0].Y = self.__pos_y + (1-0.055)*1200*self.__size_rate
        Coordinates[1].X = self.__pos_x + 2.125*1200*self.__size_rate
        Coordinates[1].Y = self.__pos_y + (1-2.064)*1200*self.__size_rate
        Coordinates[2].X = self.__pos_x - 1.24*1200*self.__size_rate
        Coordinates[2].Y = self.__pos_y + (1-0.243)*1200*self.__size_rate
        Coordinates[3].X = self.__pos_x + 0.54*1200*self.__size_rate
        Coordinates[3].Y = self.__pos_y + (1-0.02)*1200*self.__size_rate
        return tuple(Coordinates),

    '''
    インスタンスメソッド
    '''
    def __set_beziercircle(
        self,
        line_width=50, line_color=(255, 0, 0), line_transparence=20
    ):
        self.__BezierCircleShape.LineWidth = line_width
        self.__BezierCircleShape.LineColor = Tool.convert_rgb_into_int(line_color)
        self.__BezierCircleShape.LineTransparence = line_transparence
        self.__BezierCircleShape.MoveProtect = True
        self.__BezierCircleShape.SizeProtect = True

    def __set_score(
        self,
        diff_x=-700, diff_y=800, width=1000, height=3000,
        font_size=10, font_name="syunka2"
    ):
        self.__TextField = TextField(
            Document=self.__Document,
            page_index=self.__page_index,
            Layer=self.__Layer,
            pos_x=self.__pos_x + diff_x,
            pos_y=self.__pos_y + diff_y,
            width=width,
            height=height,
            message=str(self.__max_score)+"/"+str(self.__max_score),
            font_size=font_size,
            font_name=font_name
        )
    '''
    インスタンスメソッド
    '''
    def __draw(self):
        self.__set_score()

        self.__create_beziercircle()
        self.__set_beziercircle()
        self.__Page.add(self.__BezierCircleShape)
        self.__BezierCoords.Coordinates = self.__create_struct()
        self.__BezierCoords.Flags = (NORMAL, CONTROL, CONTROL, NORMAL),
        self.__BezierCircleShape.PolyPolygonBezier = self.__BezierCoords

    def remove(self):
        self.__Page.remove(self.__BezierCircleShape)
        self.__Page.remove(self.__TextField)

class XShape:

    """
    コンストラクタ
    """
    def __init__(self, Document, page_index, Layer, pos_x, pos_y, size_rate=1.0):
        self.__Document = Document
        self.__page_index = page_index
        self.__Layer = Layer
        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.__size_rate = size_rate

        self.__draw()

    """
    バツ印を作成する
    """
    def __create_x(self):
        self.__Page = self.__Document.getDrawPages().getByIndex(self.__page_index)
        self.__XShape = self.__Document.createInstance("com.sun.star.drawing.PolyLineShape")

    """
    バツ印の各点の座標を用意する
    """
    def __create_struct(self):
        Coordinates = [[uno.createUnoStruct("com.sun.star.awt.Point") for i in range(2)] for j in range(2)]
        Coordinates[0][0].X = self.__pos_x
        Coordinates[0][1].X = self.__pos_x + 1200 * self.__size_rate
        Coordinates[0][0].Y = self.__pos_y
        Coordinates[0][1].Y = self.__pos_y + 1200 * self.__size_rate
        Coordinates[1][0].X = self.__pos_x + 1200 * self.__size_rate
        Coordinates[1][1].X = self.__pos_x
        Coordinates[1][0].Y = self.__pos_y
        Coordinates[1][1].Y = self.__pos_y + 1200 * self.__size_rate
        return tuple(Coordinates[0]), tuple(Coordinates[1])

    """
    各種プロパティを設定する
    """
    def __set_x(
        self,
        line_width=50, line_color=(255, 0, 0), line_transparence=20
    ):
        self.__XShape.LineWidth = line_width
        self.__XShape.LineColor = Tool.convert_rgb_into_int(line_color)
        self.__XShape.LineTransparence = line_transparence
        self.__XShape.MoveProtect = True
        self.__XShape.SizeProtect = True

    """
    実際に描画する
    """
    def __draw(self):
        self.__create_x()
        self.__set_x()
        self.__Page.add(self.__XShape)
        self.__Document.getLayerManager().attachShapeToLayer(self.__XShape, self.__Layer)
        self.__XShape.PolyPolygon = self.__create_struct()

    """
    パブリックメソッド
    図形を削除する
    """
    def remove(self):
        self.__Page.remove(self.__XShape)

class BezierXShape:

    '''
    コンストラクタ
    '''
    def __init__(self, Document, page_index, Layer, pos_x, pos_y, max_score=0, size_rate=1.0):
        self.__Document = Document
        self.__page_index = page_index
        self.__Layer = Layer
        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.__size_rate = size_rate
        self.__max_score = max_score

        self.__draw()

    '''
    インスタンスメソッド
    '''
    def __create_bezierX(self):
        self.__Page = self.__Document.getDrawPages().getByIndex(self.__page_index)
        self.__BezierXShape = self.__Document.createInstance("com.sun.star.drawing.OpenBezierShape")
        self.__BezierCoords = uno.createUnoStruct("com.sun.star.drawing.PolyPolygonBezierCoords")

    '''
    インスタンスメソッド
    '''
    def __create_struct(self):
        Coordinates = [uno.createUnoStruct("com.sun.star.awt.Point") for _ in range(4)]
        Coordinates[0].X = self.__pos_x + 1.01*1200 * self.__size_rate
        Coordinates[0].Y = self.__pos_y + (1-1.013)*1200 * self.__size_rate
        Coordinates[1].X = self.__pos_x - 0.247*1200 * self.__size_rate
        Coordinates[1].Y = self.__pos_y + (1-0.086)*1200 * self.__size_rate
        Coordinates[2].X = self.__pos_x + 0.365*1200 * self.__size_rate
        Coordinates[2].Y = self.__pos_y + (1-(-0.41))*1200 * self.__size_rate
        Coordinates[3].X = self.__pos_x - 0.02*1200 * self.__size_rate
        Coordinates[3].Y = self.__pos_y + (1-0.422)*1200 * self.__size_rate
        return tuple(Coordinates),

    '''
    インスタンスメソッド
    '''
    def __set_bezierX(
        self,
        line_width=50, line_color=(255, 0, 0), line_transparence=20
    ):
        self.__BezierXShape.LineWidth = line_width
        self.__BezierXShape.LineColor = Tool.convert_rgb_into_int(line_color)
        self.__BezierXShape.LineTransparence = line_transparence
        self.__BezierXShape.MoveProtect = True
        self.__BezierXShape.SizeProtect = True

    def __set_score(
        self,
        diff_x=-700, diff_y=800, width=1000, height=3000,
        font_size=10, font_name="syunka2"
    ):
        self.__TextField = TextField(
            Document=self.__Document,
            page_index=self.__page_index,
            Layer=self.__Layer,
            pos_x=self.__pos_x + diff_x,
            pos_y=self.__pos_y + diff_y,
            width=width,
            height=height,
            message="0/"+str(self.__max_score),
            font_size=font_size,
            font_name=font_name
        )

    '''
    インスタンスメソッド
    '''
    def __draw(self):
        self.__set_score()
        self.__create_bezierX()
        self.__set_bezierX()
        self.__Page.add(self.__BezierXShape)
        self.__BezierCoords.Coordinates = self.__create_struct()
        self.__BezierCoords.Flags = (NORMAL, CONTROL, CONTROL, NORMAL),
        self.__BezierXShape.PolyPolygonBezier = self.__BezierCoords

    def remove(self):
        self.__Page.remove(self.__BezierXShape)
        self.__Page.remove(self.__TextField)

class TriangleShape:

    """
    コンストラクタ
    """
    def __init__(self, Document, page_index, Layer, pos_x, pos_y, score, size_rate=1.0):
        self.__Document = Document
        self.__page_index = page_index
        self.__Layer = Layer
        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.__score = score
        self.__size_rate = size_rate

        self.__draw()

    """
    三角形のインスタンスを作成
    """
    def __create_triangle(self):
        self.__Page = self.__Document.getDrawPages().getByIndex(self.__page_index)
        self.__TriangleShape = self.__Document.createInstance("com.sun.star.drawing.PolyPolygonShape")

    """
    三角形の各種座標を設定
    """
    def __create_struct(self):
        Coordinates = [uno.createUnoStruct("com.sun.star.awt.Point") for _ in range(3)]
        Coordinates[0].X = self.__pos_x + 600 * self.__size_rate
        Coordinates[1].X = self.__pos_x
        Coordinates[2].X = self.__pos_x + 1200 * self.__size_rate
        Coordinates[0].Y = self.__pos_y
        Coordinates[1].Y = self.__pos_y + 1123 * self.__size_rate
        Coordinates[2].Y = self.__pos_y + 1123 * self.__size_rate
        return tuple(Coordinates),

    """
    三角形の各種プロパティを設定
    """
    def __set_triangle(
        self,
        line_width=50, line_color=(255, 0, 0), line_transparence=20,
        fill_transparence=100
    ):
        self.__TriangleShape.LineWidth = line_width
        self.__TriangleShape.LineColor = Tool.convert_rgb_into_int(line_color)
        self.__TriangleShape.LineTransparence = line_transparence
        self.__TriangleShape.FillTransparence = fill_transparence
        self.__TriangleShape.MoveProtect = True
        self.__TriangleShape.SizeProtect = True

    """
    点数を設定
    """
    def __set_score(
        self,
        font_color=(255, 0, 0), font_size=24, font_weight=NORMAL, font_name="Arial",
        text_vertical_adjust=X_CENTER, text_upper_distance=400
    ):
        self.__TriangleShape.String = str(self.__score)
        self.__TriangleShape.CharColor = Tool.convert_rgb_into_int(font_color)
        self.__TriangleShape.CharHeight = font_size * self.__size_rate
        self.__TriangleShape.CharWeight = font_weight
        self.__TriangleShape.CharFontName = font_name
        self.__TriangleShape.TextVerticalAdjust = text_vertical_adjust
        self.__TriangleShape.TextUpperDistance = text_upper_distance * self.__size_rate

    """
    描画する
    """
    def __draw(self):
        self.__create_triangle()
        self.__set_triangle()
        self.__Page.add(self.__TriangleShape)
        self.__Document.getLayerManager().attachShapeToLayer(self.__TriangleShape, self.__Layer)
        self.__TriangleShape.PolyPolygon = self.__create_struct()
        self.__set_score()

    """
    パブリックメソッド
    図形を削除する
    """
    def remove(self):
        self.__Page.remove(self.__TriangleShape)

class BezierTriangleShape:

    def __init__(self, Document, page_index, Layer, pos_x, pos_y, score, max_score=0, size_rate=1):
        self.__Document = Document
        self.__page_index = page_index
        self.__Layer = Layer
        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.__score = score
        self.__max_score = max_score
        self.__size_rate = size_rate

        self.__draw()

    def __create_beziertriangle(self):
        self.__Page = self.__Document.getDrawPages().getByIndex(self.__page_index)
        self.__BezierTriangleShape = self.__Document.createInstance("com.sun.star.drawing.OpenBezierShape")
        self.__BezierCoords = uno.createUnoStruct("com.sun.star.drawing.PolyPolygonBezierCoords")

    def __create_struct(self):
        Coordinates = [[uno.createUnoStruct("com.sun.star.awt.Point") for i in range(4)] for j in range(2)]
        Coordinates[0][0].X = self.__pos_x + 0.46 * 1200 * self.__size_rate
        Coordinates[0][0].Y = self.__pos_y + (1-0.995) * 1200 * self.__size_rate
        Coordinates[0][1].X = self.__pos_x - 0.07 * 1200 * self.__size_rate
        Coordinates[0][1].Y = self.__pos_y + (1-(-0.41)) * 1200 * self.__size_rate
        Coordinates[0][2].X = self.__pos_x - 0.343 * 1200 * self.__size_rate
        Coordinates[0][2].Y = self.__pos_y + (1-0.24) * 1200 * self.__size_rate
        Coordinates[0][3].X = self.__pos_x + 0.997 * 1200 * self.__size_rate
        Coordinates[0][3].Y = self.__pos_y + (1-0.168) * 1200 * self.__size_rate
        Coordinates[1][0].X = self.__pos_x + 0.46 * 1200 * self.__size_rate
        Coordinates[1][0].Y = self.__pos_y + (1-0.995) * 1200 * self.__size_rate
        Coordinates[1][1].X = self.__pos_x + 0.57 * 1200 * self.__size_rate
        Coordinates[1][1].Y = self.__pos_y + (1-0.645) * 1200 * self.__size_rate
        Coordinates[1][2].X = self.__pos_x + 0.76 * 1200 * self.__size_rate
        Coordinates[1][2].Y = self.__pos_y + (1-0.355) * 1200 * self.__size_rate
        Coordinates[1][3].X = self.__pos_x + 0.997 * 1200 * self.__size_rate
        Coordinates[1][3].Y = self.__pos_y + (1-0.168) * 1200 * self.__size_rate
        return tuple(Coordinates[0]), tuple(Coordinates[1])

    def __set_beziertriangle(
        self,
        line_width=50, line_color=(255,0,0), line_transparence=20
    ):
        self.__BezierTriangleShape.LineWidth = line_width
        self.__BezierTriangleShape.LineColor = Tool.convert_rgb_into_int(line_color)
        self.__BezierTriangleShape.LineTransparence = line_transparence
        self.__BezierTriangleShape.MoveProtect = True
        self.__BezierTriangleShape.SizeProtect = True

    def __set_score(
        self,
        diff_x=-700, diff_y=800, width=1000, height=3000,
        font_size=10, font_name="syunka2"
    ):
        self.__TextField = TextField(
            Document=self.__Document,
            page_index=self.__page_index,
            Layer=self.__Layer,
            pos_x=self.__pos_x + diff_x,
            pos_y=self.__pos_y + diff_y,
            width=width,
            height=height,
            message=str(self.__score)+"/"+str(self.__max_score),
            font_size=font_size,
            font_name=font_name
        )

    def __draw(self):
        self.__set_score()

        self.__create_beziertriangle()
        self.__set_beziertriangle()
        self.__Page.add(self.__BezierTriangleShape)
        self.__BezierCoords.Coordinates = self.__create_struct()
        self.__BezierCoords.Flags = (NORMAL, CONTROL, CONTROL, NORMAL), (NORMAL, CONTROL, CONTROL, NORMAL)
        self.__BezierTriangleShape.PolyPolygonBezier = self.__BezierCoords

    def remove(self):
        self.__Page.remove(self.__BezierTriangleShape)
        self.__Page.remove(self.__TextField)

class TextField:
    def __init__(
        self, Document, page_index, Layer, pos_x, pos_y, width, height, message,
        font_size=13, font_size_asian=13, font_weight=NORMAL, font_color=(255,0,0),
        font_name="Times New Roman", font_name_asian="syunka2"
    ):
        self.__Document = Document
        self.__page_index = page_index
        self.__Layer = Layer
        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.__width = width
        self.__height = height
        self.__message = message

        self.__font_size = font_size
        self.__font_size_asian = font_size_asian
        self.__font_weight = font_weight
        self.__font_weight_asian = font_weight
        self.__font_color = font_color
        self.__font_name = font_name
        self.__font_name_asian = font_name_asian

        self.__draw()

    def __create_textfield(self):
        self.__Page = self.__Document.getDrawPages().getByIndex(self.__page_index)
        self.__TextShape = self.__Document.createInstance("com.sun.star.drawing.TextShape")

    def __create_struct(self):
        Point = uno.createUnoStruct("com.sun.star.awt.Point")
        Size = uno.createUnoStruct("com.sun.star.awt.Size")
        Point.X = self.__pos_x
        Point.Y = self.__pos_y
        Size.Width = self.__width
        Size.Height = self.__height
        return Point, Size

    def __set_textshape(
        self,
        text_vertical_adjust=TOP, text_horizontal_adjust=LEFT
    ):
        self.__TextShape.Position, self.__TextShape.Size = self.__create_struct()
        self.__TextShape.String = self.__message
        self.__TextShape.CharColor = Tool.convert_rgb_into_int(self.__font_color)
        self.__TextShape.CharWeightAsian = self.__font_weight_asian
        self.__TextShape.CharHeightAsian = self.__font_size_asian
        self.__TextShape.CharFontNameAsian = self.__font_name_asian
        self.__TextShape.CharWeight = self.__font_weight
        self.__TextShape.CharHeight = self.__font_size
        self.__TextShape.CharFontName = self.__font_name
        self.__TextShape.TextVerticalAdjust = text_vertical_adjust
        self.__TextShape.TextHorizontalAdjust = text_horizontal_adjust

    """
    インスタンス作成からPageへの追加を行う
    """
    def __draw(self):
        self.__create_textfield()
        self.__Page.add(self.__TextShape)
        self.__Document.getLayerManager().attachShapeToLayer(self.__TextShape, self.__Layer)
        self.__set_textshape()

    """
    パブリックメソッド
    テキストボックスの削除
    """
    def remove(self):
        self.__Page.remove(self.__TextShape)

    """
    パブリックボックス
    テキストを更新する
    """
    def update_string(self, message):
        self.__message = message
        self.__TextShape.String = self.__message

    """
    パブリックメソッド
    座標を変更する
    """
    def update_pos(self, pos_x, pos_y):
        self.__pos_x = pos_x
        self.__pos_y = pos_y

        point = uno.createUnoStruct("com.sun.star.awt.Point")
        point.X = self.__pos_x
        point.Y = self.__pos_y
        self.__TextShape.Position = point

    """
    パブリックメソッド
    ページを変更する
    """
    def update_page_index(self, page_index):
        self.__page_index = page_index
        self.remove()

        self.__Page = self.__Document.getDrawPages().getByIndex(self.__page_index)
        self.__create_textfield()
        self.__Page.add(self.__TextShape)
        self.__Document.getLayerManager().attachShapeToLayer(self.__TextShape, self.__Layer)
        self.__set_textshape()

    @property
    def string(self):
        return self.__TextShape.String

class GuideLine:

    def __init__(self, Document, page_index, Layer):
        self.__Document = Document
        self.__page_index = page_index
        self.__Layer = Layer

        self.__draw()

    def __create_guideline(self):
        self.__Page = self.__Document.getDrawPages().getByIndex(self.__page_index)
        self.__GuideLineShape = self.__Document.createInstance("com.sun.star.drawing.PolyLineShape")

    def __create_struct(self):
        Coordinates = [[uno.createUnoStruct("com.sun.star.awt.Point") for i in range(3)] for j in range(4)]

        Coordinates[0][0].X = 2250
        Coordinates[0][0].Y = 1300
        Coordinates[0][1].X = 1250
        Coordinates[0][1].Y = 1300
        Coordinates[0][2].X = 1250
        Coordinates[0][2].Y = 2300

        Coordinates[1][0].X = 18750
        Coordinates[1][0].Y = 1300
        Coordinates[1][1].X = 19750
        Coordinates[1][1].Y = 1300
        Coordinates[1][2].X = 19750
        Coordinates[1][2].Y = 2300

        Coordinates[2][0].X = 2250
        Coordinates[2][0].Y = 28250
        Coordinates[2][1].X = 1250
        Coordinates[2][1].Y = 28250
        Coordinates[2][2].X = 1250
        Coordinates[2][2].Y = 27250

        Coordinates[3][0].X = 18750
        Coordinates[3][0].Y = 28250
        Coordinates[3][1].X = 19750
        Coordinates[3][1].Y = 28250
        Coordinates[3][2].X = 19750
        Coordinates[3][2].Y = 27250

        return (
            tuple(Coordinates[0]), tuple(Coordinates[1]),
            tuple(Coordinates[2]), tuple(Coordinates[3])
        )

    def __set_guideline(
        self,
        line_width=50, line_color=(0, 0, 255), line_transparence=20
    ):
        self.__GuideLineShape.LineWidth = line_width
        self.__GuideLineShape.LineColor = Tool.convert_rgb_into_int(line_color)
        self.__GuideLineShape.LineTransparence = line_transparence
        self.__GuideLineShape.MoveProtect = True
        self.__GuideLineShape.SizeProtect = True
        self.__GuideLineShape.Printable = False

    def __draw(self):
        self.__create_guideline()
        self.__set_guideline()
        self.__Page.add(self.__GuideLineShape)
        self.__Document.getLayerManager().attachShapeToLayer(self.__GuideLineShape, self.__Layer)
        self.__GuideLineShape.PolyPolygon = self.__create_struct()

    def remove(self):
        self.__Page.remove(self.__GuideLineShape)

class InputBox:
    """
    各種パラメータの初期化をする
    引数に取っていない定数も定義
    """
    def __init__(self, message, title, default):
        self.__message = message
        self.__title = title
        self.__default = default
        self.__hori_margin = 8  # 水平方向の余白
        self.__vert_margin = 8  # 垂直方向の余白
        self.__hori_sep = 8  # 水平方向の、コントロール間の余白
        self.__vert_sep = 8  # 垂直方向の、コントロール間の余白
        self.__button_height = 26  # ボタンの高さ
        self.__button_width = 100  # ボタンの幅
        self.__edit_height = 24  # テキストボックスの高さ
        self.__width = 600  # インプットボックスの幅
        self.__label_width = self.__width - self.__button_width - self.__hori_sep - self.__hori_margin * 2  # ラベル(テキスト)の幅
        self.__label_height = self.__button_height * 2 + 5  # ラベル(テキスト)の高さ
        self.__height = self.__vert_margin * 2 + self.__label_height + self.__vert_sep + self.__edit_height  # インプットボックスの高さ

    """
    各種インスタンスを作成するためのヘルパー関数
    """
    def __create(self, name):
        self.__ComponentContext = uno.getComponentContext()
        ServiceManager = self.__ComponentContext.getServiceManager()
        return ServiceManager.createInstanceWithContext(name, self.__ComponentContext)

    """
    各種インスタンスを作成する
    """
    def __create_instances(self):
        self.__Dialog = self.__create("com.sun.star.awt.UnoControlDialog")
        self.__DialogModel = self.__create("com.sun.star.awt.UnoControlDialogModel")
        self.__Frame = self.__create("com.sun.star.frame.Desktop").getCurrentFrame()
        self.__Window = self.__Frame.getContainerWindow() if self.__Frame else None

    """
    ダイアログ自身のプロパティを設定する
    """
    def __set_dialog(self):
        self.__Dialog.setModel(self.__DialogModel)
        self.__Dialog.setVisible(False)
        self.__Dialog.setTitle(self.__title)
        self.__Dialog.setPosSize(0, 0, self.__width, self.__height, SIZE)

    """
    ダイアログに部品を追加するヘルパー関数
    """
    def __add(self, name, type, x_pos, y_pos, width, height, props):
        model = self.__DialogModel.createInstance("com.sun.star.awt.UnoControl" + type + "Model")
        self.__DialogModel.insertByName(name, model)
        control = self.__Dialog.getControl(name)
        control.setPosSize(x_pos, y_pos, width, height, POSSIZE)
        for key, value in props.items():
            setattr(model, key, value)

    """
    各種部品を追加していく
    """
    def __add_instances(self):
        self.__add(
            "label", "FixedText",
            self.__hori_margin, self.__vert_margin,
            self.__label_width, self.__label_height,
            {"Label": self.__message, "NoLabel": True}
        )
        self.__add(
            "btn_ok", "Button",
            self.__hori_margin + self.__label_width + self.__hori_sep, self.__vert_margin,
            self.__button_width, self.__button_height,
            {"PushButtonType": OK, "DefaultButton": True}
        )
        self.__add(
            "btn_cancel", "Button",
            self.__hori_margin + self.__label_width + self.__hori_sep, self.__vert_margin + self.__button_height + 5,
            self.__button_width, self.__button_height,
            {"PushButtonType": CANCEL}
        )
        self.__add(
            "edit", "Edit",
            self.__hori_margin, self.__label_height + self.__vert_margin + self.__vert_sep,
            self.__width - self.__hori_margin * 2, self.__edit_height,
            {"Text": self.__default}
        )
        self.__Dialog.createPeer(self.__create("com.sun.star.awt.Toolkit"), self.__Window)

    """
    実際にインプットボックスを表示する
    """
    def __set_window(self):
        self.__Dialog.createPeer(self.__create("com.sun.star.awt.Toolkit"), self.__Window)
        self.__Dialog.setPosSize(
            self.__Window.getPosSize().Width / 2 - self.__width / 2,
            self.__Window.getPosSize().Height / 2 - self.__height / 2,
            0, 0, POS
        )

    """
    インプットボックスのテキストボックスに入っていた値を取得する
    """
    def __get_input(self):
        edit = self.__Dialog.getControl("edit")
        edit.setSelection(uno.createUnoStruct("com.sun.star.awt.Selection", 0, len(self.__default)))
        edit.setFocus()
        ret = edit.getModel().Text if self.__Dialog.execute() else ""
        self.__Dialog.dispose()
        return ret

    """
    インスタンス生成から表示、値の取得といった一連の動作を行う
    """
    def show(self):
        self.__create_instances()
        self.__set_dialog()
        self.__add_instances()
        self.__set_window()
        return self.__get_input()


# ***********************************************************
#  Button
#
#   - class Button
#      - class CircleButton(Button)
#      - class XButton(Button)
#      - class TriangleButton(Button)
#      - class GentenButton(Button)
#      - class MenuButton(Button)
# ***********************************************************


class Button:

    """
    widthとheightは定数として用意
    PageとControlShape, ButtonModelはcreate_button関数により中身を与えられる
    """
    def __init__(self, Document, page_index, Layer, pos_x, pos_y, name, label, width=650, height=650, size_rate=1.0):
        self.__Document = Document
        self.__page_index = page_index
        self.__Layer = Layer
        self.__pos_x = pos_x
        self.__pos_y = pos_y
        self.__name = name
        self.__label = label
        self.__width = width * size_rate
        self.__height = height * size_rate

        self.__draw()

    """
    Pageはマクロを適用するページを、ButtonModelはボタンを、ControlShapeはボタンのラッパーを表す
    最後に実際の描画関数drawを呼び出す
    """
    def __create_button(self):
        self.__Page = self.__Document.getDrawPages().getByIndex(self.__page_index)
        self.__ControlShape = self.__Document.createInstance("com.sun.star.drawing.ControlShape")
        self.__ButtonModel = self.__Document.createInstance("com.sun.star.form.component.CommandButton")

    """
    位置とサイズに関する構造体を生成する
    """
    def __create_struct(self):
        Point = uno.createUnoStruct("com.sun.star.awt.Point")
        Size = uno.createUnoStruct("com.sun.star.awt.Size")
        FontDescriptor = uno.createUnoStruct("com.sun.star.awt.FontDescriptor")
        Point.X = self.__pos_x
        Point.Y = self.__pos_y
        Size.Width = self.__width
        Size.Height = self.__height
        FontDescriptor.Height = 12
        return Point, Size, FontDescriptor

    def __set_button(self, text_color=(255,0,0), printable=0):
        self.__ButtonModel.Name = self.__name
        self.__ButtonModel.Label = self.__label
        self.__ButtonModel.TextColor = Tool.convert_rgb_into_int(text_color)
        self.__ButtonModel.FocusOnClick = False

        self.__ControlShape.setControl(self.__ButtonModel)
        self.__ControlShape.Printable = False
        self.__ControlShape.MoveProtect = True
        self.__ControlShape.SizeProtect = True

    def __draw(self):
        self.__create_button()
        self.__ControlShape.Position, self.__ControlShape.Size, self.__ButtonModel.FontDescriptor = self.__create_struct()
        self.__set_button()
        self.__Page.add(self.__ControlShape)
        self.__Document.getLayerManager().attachShapeToLayer( self.__ControlShape, self.__Layer )

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def _Document(self):
        return self.__Document

    @property
    def _ButtonModel(self):
        return self.__ButtonModel

    @property
    def _page_index(self):
        return self.__page_index

class CircleButton(Button):

    """
    作成親Shomonのインスタンスを引数とし、Class Buttonのコンストラクタを
    オーバーラップするような形で呼び出す
    """
    def __init__(self, Document, page_index, Layer, pos_x, pos_y, shomon):
        Button.__init__(
            self, Document, page_index, Layer, pos_x, pos_y,
            ",".join(["circle", str(shomon.daimon.toan.toan_index), str(shomon.daimon.daimon_index), str(shomon.shomon_index)]),
            "○"
        )
        self.__shomon = shomon
        self.__set_handler()

    """
    クリック時の呼び出し関数を設定する
    """
    def __set_handler(self):
        self._ButtonModel.ButtonType = URL
        self._ButtonModel.TargetURL = \
            MACRO_PATH + "$set_status_by_button?language=Python&location=user" \
            + "&button_type=" + "circle" \
            + "&toan_index=" + str(self.__shomon.daimon.toan.toan_index) \
            + "&daimon_index=" + str(self.__shomon.daimon.daimon_index) \
            + "&shomon_index=" + str(self.__shomon.shomon_index)

class XButton(Button):
    """
    コンストラクタ
    小問番号shomon_indexを引数とし、Class Buttonのコンストラクタを
    オーバーラップするような形で呼び出す
    """
    def __init__(self, Document, page_index, Layer, pos_x, pos_y, shomon):
        Button.__init__(
            self, Document, page_index, Layer, pos_x, pos_y,
            ",".join(["x", str(shomon.daimon.toan.toan_index), str(shomon.daimon.daimon_index), str(shomon.shomon_index)]),
             "×"
        )
        self.__shomon = shomon
        self.__set_handler()

    """
    インスタンスメソッド
    クリック時の呼び出し関数を設定する
    """
    def __set_handler(self):
        self._ButtonModel.ButtonType = URL
        self._ButtonModel.TargetURL = \
            MACRO_PATH + "$set_status_by_button?language=Python&location=user" \
            + "&button_type=" + "x" \
            + "&toan_index=" + str(self.__shomon.daimon.toan.toan_index) \
            + "&daimon_index=" + str(self.__shomon.daimon.daimon_index) \
            + "&shomon_index=" + str(self.__shomon.shomon_index)

class TriangleButton(Button):
    """
    コンストラクタ
    小問番号shomon_indexを引数とし、Class Buttonのコンストラクタを
    オーバーラップするような形で呼び出す
    """
    def __init__(self, Document, page_index, Layer, pos_x, pos_y, shomon):
        Button.__init__(
            self, Document, page_index, Layer, pos_x, pos_y,
            ",".join(["triangle", str(shomon.daimon.toan.toan_index), str(shomon.daimon.daimon_index), str(shomon.shomon_index)]), "△")
        self.__shomon = shomon
        self.__set_handler()

    """
    インスタンスメソッド
    クリック時の呼び出し関数を設定する
    """
    def __set_handler(self):
        self._ButtonModel.ButtonType = URL
        self._ButtonModel.TargetURL = \
            MACRO_PATH + "$set_status_by_button?language=Python&location=user" \
            + "&button_type=" + "triangle" \
            + "&toan_index=" + str(self.__shomon.daimon.toan.toan_index) \
            + "&daimon_index=" + str(self.__shomon.daimon.daimon_index) \
            + "&shomon_index=" + str(self.__shomon.shomon_index)

class GentenButton(Button):
    """
    コンストラクタ
    大問番号daimon_indexを引数とし、Class Buttonのコンストラクタを
    オーバーラップするような形で呼び出す
    """
    def __init__(self, Document, page_index, Layer, pos_x, pos_y, daimon):
        Button.__init__(
            self, Document, page_index, Layer, pos_x, pos_y,
            ",".join(["genten", str(daimon.toan.toan_index), str(daimon.daimon_index)]),
            "構造式減点", 2500, 700
        )
        self.__daimon = daimon
        self.__set_handler()

    """
    インスタンスメソッド
    クリック時の呼び出し関数を設定する
    """
    def __set_handler(self):
        self._ButtonModel.ButtonType = URL
        self._ButtonModel.TargetURL = \
        MACRO_PATH + "$set_status_by_button?language=Python&location=user" \
        + "&button_type=" + "genten" \
        + "&toan_index=" + str(self.__daimon.toan.toan_index) \
        + "&daimon_index=" + str(self.__daimon.daimon_index)

class MenuButton(Button):
    """
    大問daimonを引数とし、ClassButtonのコンストラクタを
    オーバーラップするような形で呼び出す
    """
    def __init__(self, Document, page_index, Layer, toan_index, menu_index, label, method_name):
        Button.__init__(
            self,
            Document,
            page_index,
            Layer,
            3750*menu_index+1250,
            300,
            ",".join([label, str(page_index)]),
            label,
            3750,
            1000
        )
        self.__toan_index = toan_index
        self.__menu_index = menu_index
        self.__method_name = method_name
        self.__set_handler()

    """
    クリック時の呼び出し関数を設定する
    """
    def __set_handler(self):
        self._ButtonModel.ButtonType = URL
        self._ButtonModel.TargetURL = \
            MACRO_PATH + "$" + self.__method_name + "?language=Python&location=user" \
            + "&toan_index=" + str(self.__toan_index) \
            + "&page_index=" + str(self._page_index)


# ***********************************************************
#  Saiten
#   - class Shomon
#      - class Daimon
#         - class Toan
# ***********************************************************


class Shomon:

    """
    引数にとった基本的な値をインスタンス変数に保存し、
    インスタンスメソッドprepareを呼び出す
    """
    def __init__(self, Document, data, daimon, shomon_index):
        self.__Document = Document
        self.__data = data
        self.__daimon = daimon
        self.__shomon_index = shomon_index

        self.__size_rate = 1.0

        self.__shape = None

        self.__prepare()

    """
    各種ボタンを配置する
    """
    def __prepare(self):

        self.__current_score = 0
        left_margin = 800
        self.__serial_number = self.daimon.toan.serial_number

        self.__circleButton = CircleButton(
            Document=self.__Document,
            page_index=self.__data["page_index"],
            Layer=self.daimon.toan.button_layer,
            pos_x=self.__data["pos_x"] - left_margin,
            pos_y=self.__data["pos_y"] - 50*self.__size_rate,
            shomon=self
        )

        self.__xButton = XButton(
            Document=self.__Document,
            page_index=self.__data["page_index"],
            Layer=self.daimon.toan.button_layer,
            pos_x=self.__data["pos_x"] - left_margin,
            pos_y=self.__data["pos_y"] + (self.__circleButton.height - 50)*self.__size_rate,
            shomon=self
        )

        if self.__data["allow_triangle"]:
            self.__triangleButton = TriangleButton(
                Document=self.__Document,
                page_index=self.__data["page_index"],
                Layer=self.daimon.toan.button_layer,
                pos_x=self.__data["pos_x"] - left_margin,
                pos_y=self.__data["pos_y"] + (self.__circleButton.height + self.__xButton.height - 50)*self.__size_rate,
                shomon=self
            )

        # 採点状態を未採点に
        self.__status = ShomonStatus.NONE

    """
    パブリックメソッド
    小問の採点状態を設定する
    引数scoreはShomonStatus.TRIANGLEの時に必要
    """
    def set_status(self, new_status, allow_switch=False, score=-1):

        if not self.__shape == None:
            self.__shape.remove()

        # TODO: 自動追加する各種ツールはここで処理
        # if hasattr(self, "__tensaku_shape_list")みたいな
        if self.__status == new_status and allow_switch == True:
            # 未採点状態にする
            self.__status = ShomonStatus.NONE
            self.daimon.toan.saiten_data[self.__serial_number] = -1
            self.daimon.toan.update_saiten_data()
        else:
            # ステータスを更新
            self.__status = new_status

        # 各種ステータスに応じて図形、得点の処理
        # TODO: 採点ツールを自動追加するならここら辺で
        if self.__status == ShomonStatus.NONE:
            # 図形処理はない
            self.__current_score = 0
            self.daimon.toan.saiten_data[self.__serial_number] = -1
            self.daimon.toan.update_saiten_data()
        else:
            if self.__status == ShomonStatus.CIRCLE:
                if subject == 50:
                    self.__shape = BezierCircleShape(
                        Document=self.__Document,
                        page_index=self.__data["page_index"],
                        Layer=self.__daimon.toan.mark_layer,
                        pos_x=self.__data["pos_x"],
                        pos_y=self.__data["pos_y"],
                        max_score=self.__data["max_score"]
                    )
                else:
                    self.__shape = CircleShape(
                        Document=self.__Document,
                        page_index=self.__data["page_index"],
                        Layer=self.daimon.toan.mark_layer,
                        pos_x=self.__data["pos_x"],
                        pos_y=self.__data["pos_y"],
                        max_score=self.__data["max_score"]
                    )
                self.__current_score = self.__data["max_score"]
                self.daimon.toan.saiten_data[self.__serial_number] = self.__data["max_score"]
                self.daimon.toan.update_saiten_data()

            elif self.__status == ShomonStatus.X:
                if subject == 50:
                    self.__shape = BezierXShape(
                        Document=self.__Document,
                        page_index=self.__data["page_index"],
                        Layer=self.daimon.toan.mark_layer,
                        pos_x=self.__data["pos_x"],
                        pos_y=self.__data["pos_y"],
                        max_score=self.__data["max_score"]
                    )
                else:
                    self.__shape = XShape(
                        Document=self.__Document,
                        page_index=self.__data["page_index"],
                        Layer=self.daimon.toan.mark_layer,
                        pos_x=self.__data["pos_x"],
                        pos_y=self.__data["pos_y"]
                    )
                self.__current_score = 0
                self.daimon.toan.saiten_data[self.__serial_number] = 0
                self.daimon.toan.update_saiten_data()

            elif self.__status == ShomonStatus.TRIANGLE:
                while (score <= 0) or (self.__data["max_score"] <= score):
                    score = float(InputBox(
                        message="減点後の点数を入力してください。",
                        title="部分点メニュー",
                        default=str(self.__data["max_score"] - 1)
                    ).show())
                    score = int(score) if score == int(score) else score
                if subject == 50:
                    self.__shape = BezierTriangleShape(
                        Document=self.__Document,
                        page_index=self.__data["page_index"],
                        Layer=self.daimon.toan.mark_layer,
                        pos_x=self.__data["pos_x"],
                        pos_y=self.__data["pos_y"],
                        score=score,
                        max_score=self.__data["max_score"]
                    )
                else:
                    self.__shape = TriangleShape(
                        Document=self.__Document,
                        page_index=self.__data["page_index"],
                        Layer=self.daimon.toan.mark_layer,
                        pos_x=self.__data["pos_x"],
                        pos_y=self.__data["pos_y"],
                        score=score
                    )
                self.current_score = score
                self.daimon.toan.saiten_data[self.__serial_number] = score
                self.daimon.toan.update_saiten_data()

        # 総得点を更新する
        self.daimon.refresh_total_score(self.__shomon_index)

    @property
    def current_score(self):
        return self.__current_score

    @property
    def current_status(self):
        return self.__status

    @property
    def shomon_index(self):
        return self.__shomon_index

    @property
    def daimon(self):
        return self.__daimon

    @property
    def serial_number(self):
        return self.__serial_number

class Daimon:

    """
    引数にとった基本的な値をインスタンス変数に保存し、インスタンスメソッドprepareを呼び出す
    """
    def __init__(self, Document, data, toan, daimon_index):
        self.__Document = Document
        self.__data = data
        self.__toan = toan  # toanからbutton_layerを継承する
        self.__daimon_index = daimon_index

        self.__prepare()

    """
    必要数のclass Shomonと構造式減点、大問総得点のテキストボックスを用意する
    """
    def __prepare(self):
        # 小問の数だけShomonのインスタンスを作成
        self.__shomon_list = []
        self.__shomon_current_score_list = []
        self.__total_current_score = 0
        self.__total_max_score = 0

        for i in range(len(self.__data["shomon_list"])):
            self.__shomon_list.append(Shomon(
                Document=self.__Document,
                data=self.__data["shomon_list"][i],
                daimon=self,
                shomon_index=i
            ))
            self.__shomon_current_score_list.append(0)
            self.__total_max_score += self.__data["shomon_list"][i]["max_score"]
            if self.toan.doc_line < 0:
                self.toan.saiten_data.append(-1)
            self.toan.add_serial_number

        self.__genten_score = 0
        if self.__data["kozoshiki_genten"]["exists"]:
            self.__set_genten_button()
        self.__set_score_info()
        self.__set_sohyo()

    """
    構造式減点ボタンを設置
    """
    def __set_genten_button(self):
        self.__genten_button = GentenButton(
            Document=self.__Document,
            page_index=self.__data["kozoshiki_genten"]["page_index"],
            Layer=self.toan.button_layer,
            pos_x=self.__data["kozoshiki_genten"]["pos_x"] + 1500,
            pos_y=self.__data["kozoshiki_genten"]["pos_y"] - 500,
            daimon=self
        )

    """
    大問総得点を設置
    """
    def __set_score_info(self):
        self.__score_textField = TextField(
            Document=self.__Document,
            page_index=self.__data["total_score"]["page_index"],
            Layer=self.toan.mark_layer,
            pos_x=self.__data["total_score"]["pos_x"],
            pos_y=self.__data["total_score"]["pos_y"],
            width=5000,
            height=1000,
            message=self.total_score_text,
            font_size=13,
            font_weight=NORMAL,
            font_name="Times New Roman"
        )

    """
    総評を用意
    """
    def __set_sohyo(self):
        self.__sohyo_textField = TextField(
            Document=self.__Document,
            page_index=self.__data["sohyo"]["page_index"],
            Layer=self.toan.comment_layer,
            pos_x=self.__data["sohyo"]["pos_x"],
            pos_y=self.__data["sohyo"]["pos_y"],
            width=self.__data["sohyo"]["width"],
            height=self.__data["sohyo"]["height"],
            message="【総評】 \n"
        )

    """
    パブリックメソッド
    構造式減点の状態を切り替える
    構造式減点がなかったら特に何もしない
    """
    def switch_genten_status(self):
        if self.__data["kozoshiki_genten"]["exists"] == False:
            return

        if self.__genten_score == 0:
            score = 0
            while 0 <= score:
                score = float(InputBox(
                    message="減点する点数を入力してください。 \n (点数 < 0)",
                    title="構造式減点メニュー",
                    default="-1"
                ).show())
            # 整数ならint型に
            self.__genten_score = int(score) if int(score) == score else score  # 整数ならint型

            self.__genten_shape = TriangleShape(
                Document=self.__Document,
                Layer=self.toan.mark_layer,
                page_index=self.__data["kozoshiki_genten"]["page_index"],
                pos_x=self.__data["kozoshiki_genten"]["pos_x"],
                pos_y=self.__data["kozoshiki_genten"]["pos_y"],
                score=self.__genten_score
            )

            self.__genten_textField = TextField(
                Document=self.__Document,
                Layer=self.toan.mark_layer,
                page_index=self.__data["kozoshiki_genten"]["page_index"],
                pos_x=self.__data["kozoshiki_genten"]["pos_x"] + 1500,
                pos_y=self.__data["kozoshiki_genten"]["pos_y"] + 500,
                width=15000,
                height=1000,
                message="構造式が例に倣っていないため大問全体から減点"
            )

        else:
            self.__genten_shape.remove()
            self.__genten_textField.remove()
            self.__genten_score = 0

        self.__score_textField.update_string(self.total_score_text)
        self.toan.refresh_total_score(self.__daimon_index)

    """
    パブリックメソッド
    大問総得点、小問別得点リストを更新する
    引数のshomon__indexは更新された小問番号
    """
    def refresh_total_score(self, shomon_index=-1):
        # total_current_scoreに構造式減点は考慮されない
        if 0 <= shomon_index:
            self.__total_current_score -= self.__shomon_current_score_list[shomon_index]
            self.__shomon_current_score_list[shomon_index] = self.__shomon_list[shomon_index].current_score
            self.__total_current_score += self.__shomon_current_score_list[shomon_index]

        self.__score_textField.update_string(self.total_score_text)
        self.toan.refresh_total_score(self.__daimon_index)


    """
    各種ゲッター
    大問得点での切り捨て操作も行う
    """
    @property
    def current_score(self):
        return max(self.__total_current_score + self.__genten_score, 0)

    @property
    def total_score_text(self):
        return str(int(self.current_score)) + " / " + str(self.__total_max_score)

    @property
    def total_max_score(self):
        return self.__total_max_score

    @property
    def daimon_index(self):
        return self.__daimon_index

    @property
    def toan(self):
        return self.__toan

    @property
    def shomon_list(self):
        return self.__shomon_list

class Toan:

    """
    基本的な値(Document, data)をインスタンス変数に保存し、インスタンスメソッドprepareを呼び出す
    """
    def __init__(self, Document, data, toan_index):
        self.__Document = Document
        self.__data = data
        self.__toan_index = toan_index

        # ページ数は十分か
        current_page_count = self.__Document.getDrawPages().getCount()
        last_page_count = self.last_page_index + 1
        if current_page_count != last_page_count:
            raise InvalidPageCountError("ページ数が異なります！\n(現在:" + str(current_page_count) + "ページ / 必要数:" + str(last_page_count) + "ページ")

        self.__prepare()

    """
    必要数のclass Daimonと総得点、大問得点一覧、添削者名のテキストボックスを用意する
    """
    def __prepare(self):
        self.__set_layer()

        self.__daimon_list = []
        self.__daimon_current_score_list = []
        self.__total_current_score = 0
        self.__total_max_score = 0

        self.__saiten_data = []
        self.__doc_line = -1
        self.__serial_number = 0  # len(saiten_data)

        # 答案idを呼び出し、記録する
        self.__doc_url = uno.fileUrlToSystemPath(self.__Document.getURL())  # /Users/.../答案.pdf
        self.__pdf_name = os.path.splitext(os.path.basename(self.__doc_url))[0]  # 答案番号(拡張子なし)
        self.__path = os.path.dirname(self.__doc_url)  # 答案番号.pdfを含むディレクトリまでのシステムpath
        self.__csv_url = CSV_PATH + "saiten_data.csv"

        self.__read_saiten_data()

        if self.__doc_line < 0:
            self.__saiten_data.append(self.__pdf_name)
        self.add_serial_number

        for i in range(len(self.__data["daimon_list"])):
            self.__daimon_list.append(Daimon(
                Document=self.__Document,
                data=self.__data["daimon_list"][i],
                toan=self,
                daimon_index=i
            ))
            self.__total_max_score += self.__daimon_list[i].total_max_score
            self.__daimon_current_score_list.append(0)

        if self.__doc_line < 0:
            self.__write_saiten_data()

        # 各種テキストボックスを表示
        self.__set_tensaku_info()
        self.__set_macro_mark()
        self.__set_debug_info()
        self.__set_menu_buttons()

        # KeyHandlerをつける
        self.__Controller = self.__Document.getCurrentController()
        self.__KeyHandler = SaitenKeyHandler(self)
        self.__Controller.addKeyHandler(self.__KeyHandler)

        # key_tensakuあたりを初期化
        self.__key_tensaku_status = False
        self.__key_tensaku_focus = {
            "daimon_index": 0,
            "shomon_index": 0
        }

        self.__guideline_shape_list = []
        self.__guideline_status = False

    """
    添削情報を用意
    """
    def __set_tensaku_info(self):
        self.__total_score_textField = TextField(
            Document=self.__Document,
            page_index=self.__data["general"]["total_score"]["page_index"],
            Layer=self.__mark_layer,
            pos_x=self.__data["general"]["total_score"]["pos_x"],
            pos_y=self.__data["general"]["total_score"]["pos_y"],
            width=3000,
            height=1000,
            message=self.total_current_score_text,
            font_size=11,
            font_weight=NORMAL,
            font_name="Times New Roman"
        )

        # 大問得点一覧を用意
        self.__daimon_current_score_list_textField = TextField(
            Document=self.__Document,
            page_index=self.__data["general"]["daimon_score_list"]["page_index"],
            Layer=self.__mark_layer,
            pos_x=self.__data["general"]["daimon_score_list"]["pos_x"],
            pos_y=self.__data["general"]["daimon_score_list"]["pos_y"],
            width=3000,
            height=1000,
            message=self.daimon_current_score_list_text,
            font_size=9,
            font_weight=NORMAL,
            font_name="Times New Roman"
        )

        self.__name_textField = TextField(
            Document=self.__Document,
            page_index=self.__data["general"]["staff"]["page_index"],
            Layer=self.mark_layer,
            pos_x=self.__data["general"]["staff"]["pos_x"],
            pos_y=self.__data["general"]["staff"]["pos_y"],
            width=3000,
            height=1000,
            message=self.staff_name_text,
            font_size_asian=10
        )

    """
    マクロを利用した印を用意
    """
    def __set_macro_mark(self):
        self.__mark_textField_list = []
        for i in range(self.last_page_index + 1):
            self.__mark_textField_list.append(
                TextField(
                    Document=self.__Document,
                    page_index=i,
                    Layer=self.__mark_layer,
                    pos_x=0,
                    pos_y=0,
                    width=500,
                    height=500,
                    message="✔︎"
                )
            )

    """
    OS名とOpenOfficeのバージョンを用意
    """
    def __set_debug_info(self):
        system = platform.system()

        ComponentContext = uno.getComponentContext()
        ServiceManager = ComponentContext.getServiceManager()

        ConfigProvider = ServiceManager.createInstance("com.sun.star.configuration.ConfigurationProvider")
        Arguments = uno.createUnoStruct("com.sun.star.beans.PropertyValue"),
        Arguments[0].Name = "nodepath"
        Arguments[0].Value = "/org.openoffice.Setup/Product"

        Settings = ConfigProvider.createInstanceWithArguments("com.sun.star.configuration.ConfigurationAccess", Arguments)
        version = Settings.getByName("ooSetupVersion")
        self.__debug_textField_list = []
        for i in range(self.last_page_index + 1):
            self.__debug_textField_list.append(TextField(
                Document=self.__Document,
                page_index=i,
                Layer=self.tool_layer,
                pos_x=0,
                pos_y=-850,
                width=20000,
                height=500,
                message=" / ".join(["Tensaku-Macro Version " + MACRO_VERSION, "OpenOffice Version " + version, system])
            ))

    """
    メニューボタンを描画
    """
    def __set_menu_buttons(self):
        self.__key_tensaku_button = MenuButton(
            Document=self.__Document,
            page_index=0,
            Layer=self.button_layer,
            toan_index=self.toan_index,
            menu_index=0,
            label="キーボード採点",
            method_name="switch_key_tensaku_status"
        )
        self.__guideline_button = MenuButton(
            Document=self.__Document,
            page_index=0,
            Layer=self.button_layer,
            toan_index=self.toan_index,
            menu_index=1,
            label="ガイドライン",
            method_name="switch_guideline_status"
        )
        self.__export_button = MenuButton(
            Document=self.__Document,
            page_index=0,
            Layer=self.button_layer,
            toan_index=self.toan_index,
            menu_index=2,
            label="採点終了",
            method_name="switch_export_status"
        )
        self.__reconstitute_button = MenuButton(
            Document=self.__Document,
            page_index=0,
            Layer=self.button_layer,
            toan_index=self.toan_index,
            menu_index=3,
            label="答案データの復元",
            method_name="switch_reconstitute_status"
        )

    """
    レイヤーを追加し、オブジェクト変数として保存しておく
    """
    def __set_layer(self):
        self.__LayerManager = self.__Document.getLayerManager()
        button_layer_name = "採点ボタン"
        tool_layer_name = "採点ツール"
        mark_layer_name = "採点マーク"
        comment_layer_name = "コメント用"

        if self.__LayerManager.hasByName(button_layer_name):
            self.__button_layer = self.__LayerManager.getByName(button_layer_name)
        else:
            self.__button_layer = self.__LayerManager.insertNewByIndex(1)
            self.__button_layer.Name = button_layer_name
            self.__button_layer.IsVisible = True
            self.__button_layer.IsPrintable = False
            self.__button_layer.IsLocked = False
        if self.__LayerManager.hasByName(tool_layer_name):
            self.__tool_layer = self.__LayerManager.getByName(tool_layer_name)
        else:
            self.__tool_layer = self.__LayerManager.insertNewByIndex(1)
            self.__tool_layer.Name = tool_layer_name
            self.__tool_layer.IsVisible = True
            self.__tool_layer.IsPrintable = False
            self.__tool_layer.IsLocked = True
        if self.__LayerManager.hasByName(mark_layer_name):
            self.__mark_layer = self.__LayerManager.getByName(mark_layer_name)
        else:
            self.__mark_layer = self.__LayerManager.insertNewByIndex(1)
            self.__mark_layer.Name = mark_layer_name
            self.__mark_layer.IsVisible = True
            self.__mark_layer.IsPrintable = True
            self.__mark_layer.IsLocked = True
        if self.__LayerManager.hasByName(comment_layer_name):
            self.__comment_layer = self.__LayerManager.getByName(comment_layer_name)
        else:
            self.__comment_layer = self.__LayerManager.insertNewByIndex(0)
            self.__comment_layer.Name = comment_layer_name
            self.__comment_layer.IsVisible = True
            self.__comment_layer.IsPrintable = True
            self.__comment_layer.IsLocked = False

    """
    パブリックメソッド
    現在の得点についての各種インスタンス変数を更新している
    daimon_indexは更新された大問のインデックス(0始まり)
    """
    def refresh_total_score(self, daimon_index):
        self.__total_current_score -= int(self.__daimon_current_score_list[daimon_index])
        self.__daimon_current_score_list[daimon_index] = self.__daimon_list[daimon_index].current_score
        self.__total_current_score += int(self.__daimon_current_score_list[daimon_index])

        self.__total_score_textField.update_string(self.total_current_score_text)
        self.__daimon_current_score_list_textField.update_string(self.daimon_current_score_list_text)

    """
    パブリックメソッド
    キーボード採点の状態を変更する
    """
    def switch_key_tensaku_status(self):
        self.__key_tensaku_status = not self.__key_tensaku_status
        if self.__key_tensaku_status == True:
            self.__key_tensaku_cursor = TextField(
                Document=self.__Document,
                page_index=self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["shomon_list"][self.__key_tensaku_focus["shomon_index"]]["page_index"],
                Layer=self.tool_layer,
                pos_x=self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["shomon_list"][self.__key_tensaku_focus["shomon_index"]]["pos_x"] - 2300,
                pos_y=self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["shomon_list"][self.__key_tensaku_focus["shomon_index"]]["pos_y"] + 250,
                width = 1500,
                height=500,
                message="▶︎",
                font_size=24,
                font_weight=BOLD,
                font_color=(0,0,255)
            )
        else:
            self.__key_tensaku_cursor.remove()
            self.__key_tensaku_cursor = None

    def switch_guideline_status(self):
        self.__guideline_status = not self.__guideline_status
        if self.__guideline_status == True:
            for i in range(self.last_page_index):
                self.__guideline_shape_list.append(
                    GuideLine(
                        Document=self.__Document,
                        page_index=i,
                        Layer=self.tool_layer
                    )
                )
        else:
            for i in range(self.last_page_index):
                self.__guideline_shape_list[i].remove()

    def switch_export_status(self):
        self.__LayerManager.remove(self.__tool_layer)
        self.__LayerManager.remove(self.__button_layer)

        pdf_name_with_extension = self.__pdf_name + "?.pdf"   # 答案番号?.pdf
        pdf_url = uno.systemPathToFileUrl(self.__path+"/"+pdf_name_with_extension)  # pdfまでのurl

        subprops = []
        subprop1 = PropertyValue()
        subprop2 = PropertyValue()
        subprop1.Name = "UseLossLessCompression"
        subprop1.Value = True
        subprop2.Name = "ExportBookmarks"
        subprop2.Value = True
        subprops.append(subprop1)
        subprops.append(subprop2)

        props = []
        prop1 = PropertyValue()
        prop2 = PropertyValue()
        prop1.Name = "FilterName"
        prop1.Value = "draw_pdf_Export"
        prop2.Name = "FilterData"
        prop2.Value = uno.Any("[]com.sun.star.beans.PropertyValue", tuple(subprops))
        props.append(prop1)
        props.append(prop2)

        self.__Document.storeToURL(pdf_url, tuple(props))

    def switch_reconstitute_status(self):

        self.__LayerManager.remove(self.__mark_layer)
        self.__LayerManager.remove(self.__tool_layer)
        self.__LayerManager.remove(self.__button_layer)
        self.__set_layer()

        self.__daimon_list = []
        self.__daimon_current_score_list = []
        self.__total_current_score = 0
        self.__total_max_score = 0
        self.__serial_number = 1  # len(saiten_data)

        for i in range(len(self.__data["daimon_list"])):
            self.__daimon_list.append(Daimon(
                Document=self.__Document,
                data=self.__data["daimon_list"][i],
                toan=self,
                daimon_index=i
            ))
            self.__total_max_score += self.__daimon_list[i].total_max_score
            self.__daimon_current_score_list.append(0)

        self.__set_tensaku_info()
        self.__set_macro_mark()
        self.__set_debug_info()
        self.__set_menu_buttons()

        self.__guideline_shape_list = []
        self.__guideline_status = False

        serial_number = 1
        for i in range(len(self.daimon_list)):
            for j in range(len(self.__daimon_list[i].shomon_list)):
                if int(self.__saiten_data[serial_number]) == self.__data["daimon_list"][i]["shomon_list"][j]["max_score"]:
                    self.daimon_list[i].shomon_list[j].set_status(new_status=ShomonStatus.CIRCLE)
                elif int(self.__saiten_data[serial_number]) == 0:
                    self.daimon_list[i].shomon_list[j].set_status(new_status=ShomonStatus.X)
                elif int(self.__saiten_data[serial_number]) < self.__data["daimon_list"][i]["shomon_list"][j]["max_score"] and int(self.__saiten_data[serial_number]) > 0:
                    self.daimon_list[i].shomon_list[j].set_status(new_status=ShomonStatus.TRIANGLE, score=int(self.__saiten_data[serial_number]))
                serial_number += 1

    """
    パブリックメソッド
    キーボード採点をする
    """
    def set_status_by_key_tensaku(self, status, score=-1):
        max_score = self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["shomon_list"][self.__key_tensaku_focus["shomon_index"]]["max_score"]

        # scoreが設定されている時は、点数に応じて処理を変える
        # 0: ばつ
        # 1~max_score-1: さんかく
        # max_score: まる
        # max_score~: エラー
        if score == 0:
            status = ShomonStatus.NONE
        elif 0 < score and score < max_score:
            status = ShomonStatus.TRIANGLE
        elif max_score == score:
            status = ShomonStatus.CIRCLE
        elif max_score < score:
            Tool.MsgBox("得点が最高点を上回っています", "キーボード採点エラー", ERRORBOX)
            return

        shomon = self.daimon_list[self.__key_tensaku_focus["daimon_index"]].shomon_list[self.__key_tensaku_focus["shomon_index"]]
        if status == ShomonStatus.TRIANGLE:
            if self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["shomon_list"][self.__key_tensaku_focus["shomon_index"]]["allow_triangle"] == False:
                Tool.MsgBox("△が許容されていない問題です", "キーボード採点エラー", ERRORBOX)
                return
            else:
                shomon.set_status(new_status=status, score=score)
        else:
            shomon.set_status(status)
        self.move_key_tensaku_focus(1)

    """
    パブリックメソッド
    キーボードで構造式減点を操作
    """
    def switch_genten_by_key_tensaku(self):
        if self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["kozoshiki_genten"]["exists"] == False:
            Tool.MsgBox("構造式減点がない大問です", "キーボード採点エラー", ERRORBOX)
        else:
            self.daimon_list[self.__key_tensaku_focus["daimon_index"]].switch_genten_status()

    """
    kuriage / kuriageはmove_key_tensaku_focusのヘルパーメソッド
    """
    def __kuriage_key_tensaku_focus(self):
        if self.__key_tensaku_focus["daimon_index"] + 1 == len(self.__data["daimon_list"]):
            # すでに最後の大問
            return
        # daimon_indexを繰り上げる
        self.__key_tensaku_focus["daimon_index"] += 1
        self.__key_tensaku_focus["shomon_index"] = 0

    def __kurisage_key_tensaku_focus(self):
        if self.__key_tensaku_focus["daimon_index"] == 0:
            # すでに最初の大問
            return
        # daimon_indexを繰り下げる
        self.__key_tensaku_focus["daimon_index"] -= 1
        self.__key_tensaku_focus["shomon_index"] = len(self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["shomon_list"]) - 1

    """
    パブリックメソッド
    キーボード採点のフォーカスを移動させる
    """
    def move_key_tensaku_focus(self, step, daimon_step=0):
        if 0 < daimon_step:
            for _ in range(daimon_step):
                self.__kuriage_key_tensaku_focus()
        elif daimon_step < 0:
            for _ in range(-1 * daimon_step):
                self.__kurisage_key_tensaku_focus()
                # フォーカスを最初の小問に
                # self.__key_tensaku_focus["shomon_index"] = 0

        if 0 < step:
            for _ in range(step):
                if self.__key_tensaku_focus["shomon_index"] + 1 < len(self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["shomon_list"]):
                    # shomon_indexを増やす
                    self.__key_tensaku_focus["shomon_index"] += 1
                else:
                    self.__kuriage_key_tensaku_focus()
        elif step < 0:
            for _ in range(-1 * step):
                if self.__key_tensaku_focus["shomon_index"] == 0:
                    self.__kurisage_key_tensaku_focus()
                else:
                    # shomon_indexを減らすだけで良い
                    self.__key_tensaku_focus["shomon_index"] -= 1

        self.__key_tensaku_cursor.update_page_index(
            page_index=self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["shomon_list"][self.__key_tensaku_focus["shomon_index"]]["page_index"]
        )

        self.__key_tensaku_cursor.update_pos(
            pos_x=self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["shomon_list"][self.__key_tensaku_focus["shomon_index"]]["pos_x"] - 2300,
            pos_y=self.__data["daimon_list"][self.__key_tensaku_focus["daimon_index"]]["shomon_list"][self.__key_tensaku_focus["shomon_index"]]["pos_y"] + 250
        )

    # ***********************************************************
    #  再採点
    # ***********************************************************

    """初めに答案番号を探し、あったらsaiten_dataに代入し、doc_lineを返す"""
    def __read_saiten_data(self):
        with codecs.open(self.__csv_url, 'rU', 'UTF-8') as f: #'r'
            reader = csv.reader((line.replace('\0','') for line in f))
            l = [row for row in reader]  #if row[0]!=''
        for i, row in enumerate(l):
            if row[0] == self.__pdf_name:
                self.__saiten_data = row
                self.__doc_line = i

    """csvの新しい行にsaiten_dataを代入し、doc_lineを返す"""
    def __write_saiten_data(self):
        with codecs.open(self.__csv_url, 'r') as f:
            reader = csv.reader((line.replace('\0','') for line in f))
            l = [row for row in reader]
        self.__doc_line = len(l)
        l.append(self.__saiten_data)
        with codecs.open(self.__csv_url, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(l)

    """csvの指定の行にsaiten_dataを再代入してアップデート"""
    def update_saiten_data(self):
        with codecs.open(self.__csv_url, 'rU', 'UTF-8') as f:
            reader = csv.reader((line.replace('\0', '') for line in f))
            l = [row for row in reader]
            for i in range(len(l)):
                if i == self.__doc_line:
                    l[i] = self.__saiten_data
        with codecs.open(self.__csv_url, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(l)

    """
    各種ゲッター
    get_total_current_score_list_textは切り捨て処理も行う
    """
    @property
    def total_current_score_text(self):
        return self.__total_current_score

    @property
    def daimon_current_score_list_text(self):
        return ",".join(str(int(val)) for val in self.__daimon_current_score_list)

    @property
    def staff_name_text(self):
        return self.__data["general"]["staff"]["name"]

    @property
    def last_page_index(self):
        # TODO: ページ数をデータ型から取得した方が確実
        return self.__data["daimon_list"][-1]["shomon_list"][-1]["page_index"]

    @property
    def button_layer(self):
        return self.__button_layer

    @property
    def tool_layer(self):
        return self.__tool_layer

    @property
    def mark_layer(self):
        return self.__mark_layer

    @property
    def comment_layer(self):
        return self.__comment_layer

    @property
    def toan_index(self):
        return self.__toan_index

    @property
    def daimon_list(self):
        return self.__daimon_list

    @property
    def key_tensaku_status(self):
        return self.__key_tensaku_status

    @property
    def saiten_data(self):
        return self.__saiten_data

    @property
    def doc_line(self):
        return self.__doc_line

    @property
    def serial_number(self):
        return self.__serial_number

    @property
    def add_serial_number(self):
        self.__serial_number += 1

class SaitenKeyHandler(unohelper.Base, XKeyHandler):
    def __init__(self, toan):
        self.__toan = toan

    def keyPressed(self, key_event):
        if self.__toan.key_tensaku_status == False:
            pass

        elif key_event.KeyChar == uno.Char("q"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.CIRCLE)
        elif key_event.KeyChar == uno.Char("w"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.X)
        elif key_event.KeyChar == uno.Char("e"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.TRIANGLE)
        elif key_event.KeyChar == uno.Char("r"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE)

        elif key_event.KeyChar == uno.Char("t"):
            self.__toan.switch_genten_by_key_tensaku()

        elif key_event.KeyChar == uno.Char("a"):
            self.__toan.move_key_tensaku_focus(-1)
        elif key_event.KeyChar == uno.Char("d"):
            self.__toan.move_key_tensaku_focus(1)
        elif key_event.KeyChar == uno.Char("z"):
            self.__toan.move_key_tensaku_focus(0, -1)
        elif key_event.KeyChar == uno.Char("c"):
            self.__toan.move_key_tensaku_focus(0, 1)

        elif key_event.KeyChar == uno.Char("1"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE, 1)
        elif key_event.KeyChar == uno.Char("2"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE, 2)
        elif key_event.KeyChar == uno.Char("3"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE, 3)
        elif key_event.KeyChar == uno.Char("4"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE, 4)
        elif key_event.KeyChar == uno.Char("5"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE, 5)
        elif key_event.KeyChar == uno.Char("6"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE, 6)
        elif key_event.KeyChar == uno.Char("7"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE, 7)
        elif key_event.KeyChar == uno.Char("8"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE, 8)
        elif key_event.KeyChar == uno.Char("9"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE, 9)
        elif key_event.KeyChar == uno.Char("0"):
            self.__toan.set_status_by_key_tensaku(ShomonStatus.NONE, 0)

        else:
            pass

        return True

    def keyReleased(self, key_event):
        return False

    def disposing(self, source):
        pass


# ***********************************************************
#  CSVファイルの読み込み
#  OpenPDF
#  - CSVreader
# ***********************************************************


# ***********************************************************
#  CSVファイルの読み込み
#  OpenPDF
#  - CSVreader
# ***********************************************************

class OpenPDF:
    def __init__(self, doc):
        self.__doc = doc
        self.__main()

    def __prepare(self):
        self.__ctx = XSCRIPTCONTEXT.getComponentContext()
        self.__smgr = self.__ctx.getServiceManager()
        self.__desktop = XSCRIPTCONTEXT.getDesktop()

    """pdfからマクロcsvを呼び出すためのurlを取得"""
    def __call_macro(self):
        self.__file_url = self.__doc.getURL()
        self.__file_path = uno.fileUrlToSystemPath(self.__file_url)

        regex = re.compile(r"(\d{18})")
        mo = regex.search(self.__file_url)
        csv_num = mo.group(0)

        # マクロの名前は02[大学名4桁][科目2桁][年度2桁].csvに統一
        self.__csv_url = CSV_PATH + csv_num[:10] + ".csv"

    def __main(self):
        self.__prepare()
        self.__call_macro()

    """グローバルオブジェクトを作成するヘルパー関数"""
    def __create(self, c_class):
        return self.__smgr.createInstance(c_class)

    @property
    def csv_url(self):
        return self.__csv_url

class CSVreader(OpenPDF):
    def __init__(self, doc):
        self.__class_instance = OpenPDF(doc)
        self.__csv_url = self.__class_instance.csv_url
        self.__main()

    def __open_csv(self):
        try:
            with codecs.open(self.__csv_url, 'rU', 'UTF-8') as f: #'r'
                reader = csv.reader((line.replace('\0','') for line in f))
                l = [row for row in reader]  #if row[0]!=''
        except:
            with codecs.open(self.__csv_url, 'rU', 'Shift-JIS') as f: #'r'
                reader = csv.reader((line.replace('\0','') for line in f))
                l = [row for row in reader]  #if row[0]!=''

        self.__line = []
        for row in l:
            lx = []
            for v in row:
                if v.isdigit():
                    lx.append(int(v))
                elif v == '-1':
                    lx.append(-1)
                else:
                    lx.append(v)
            self.__line.append(lx)

    """
    TODO:
        [終]ページ番号とcsvのリストが1ズレている
        [終]csvに総評欄追加
        [終]部分点時の false or true と 0 or 1 の統一
        1~100行のA,B,E列が不要 -> E参照バージョンと比較して高速かつ軽量な方を選ぶ
        [終]大問得点情報には構造式の欄を必ず作る
    """

    def __data_cons(self):

        self.__data = {
            "general": {
                "staff": {
                    "name": "東進(太)",
                    "page_index": 0,
                    "pos_x": self.__line[117][4],
                    "pos_y": self.__line[117][5]
                },
                "daimon_score_list": {
                    "page_index": 0,
                    "pos_x": self.__line[118][4],
                    "pos_y": self.__line[118][5]
                },
                "total_score": {
                    "page_index": 0,
                    "pos_x": self.__line[100][5],
                    "pos_y": self.__line[100][6]
                }
            },
            "daimon_list": []
        }

        self.__daimon_index= 1
        self.__row = 0
        self.__data["daimon_list"].append(self.__dict_dai())
        while self.__row < 100:
            self.__data["daimon_list"][self.__daimon_index - 1]["shomon_list"].append(self.__dict_sho())
            #print(daimonnum)
            self.__row += 1
            if self.__line[self.__row][1] == self.__daimon_index:
                pass
            elif self.__line[self.__row][1] == self.__daimon_index + 1:
                self.__daimon_index += 1
                self.__data["daimon_list"].append(self.__dict_dai())
            else:
                break

    def __dict_sho(self):
        return {
            "page_index": self.__line[self.__row][0],
            "max_score": self.__line[self.__row][3],
            "pos_x": self.__line[self.__row][4],
            "pos_y": self.__line[self.__row][5],
            "allow_triangle": self.__line[self.__row][3]
        }

    def __dict_dai(self):
        return {
            "kozoshiki_genten": {
                "exists": True if self.__line[self.__row][3]==-1 else False,
                "page_index": self.__line[self.__row][0],
                "pos_x": self.__line[self.__row][4],
                "pos_y": self.__line[self.__row][5]
            },
            "total_score": {
                "page_index": self.__line[99+self.__daimon_index][2],
                "pos_x": self.__line[99+self.__daimon_index][4],
                "pos_y": self.__line[99+self.__daimon_index][5]
            },
            "sohyo": {
                "page_index": self.__line[122+self.__daimon_index][2],
                "pos_x": self.__line[122+self.__daimon_index][4],
                "pos_y": self.__line[122+self.__daimon_index][5],
                "width": 12000,
                "height": 2000
            },
            "shomon_list": []
        }

    def __main(self):
        self.__open_csv()
        self.__data_cons()

    @property
    def data(self):
        return self.__data

# ***********************************************************
#  CSV_PATHの読み込み
# ***********************************************************
"""
CSV_PATHの読み込み
"""

def get_csvpath():
    scriptpath = os.path.dirname(os.path.abspath('__file__'))
    Tool.MsgBox(scriptpath)
    csv_path = scriptpath + r'/csv_path_save.txt'

    with open(uno.fileUrlToSystemPath(csv_path)) as f:
        CSV_PATH = f.read()

    try:
        with open(uno.fileUrlToSystemPath(csv_path)) as f:
            CSV_PATH = f.read()
        return CSV_PATH

    except:
        Tool.MsgBox(r'デフォルトフォルダが設定されていません。最初にpath_settingから設定をしてください。')
# ***********************************************************
#  test
# ***********************************************************
'''CSV_PATHをグローバル変数として設定する'''
CSV_PATH = get_csvpath()


def test(*args):

    """
    採点する答案
    """
    Document = XSCRIPTCONTEXT.getDocument()

    """
    データの取り出し
    """

    csv_instance = CSVreader(Document)
    data = csv_instance.data
    Tool.MsgBox(str(data))


    """
    インスタンス生成
    ・1つの答案に対して1つの採点インスタンスを生成
    ・採点インスタンスをprepare()するとボタンの配置が行われる。
    """
    try:
        toan_list.append(Toan(Document, data, len(toan_list)))
    except InvalidPageCountError as e:
        Tool.MsgBox(e.args[0], "マクロ起動エラー", ERRORBOX)

    """
    デザインモードをオフに
    """
    Tool.setDesignMode(Document, False)

    # TODO: only for debugging
    Tool.MsgBox("finished\n" + "version " + MACRO_VERSION + "\n" + str(len(toan_list)) + "件の答案を(並行)採点中です。")

def path_setting():
    '''ファイルを指定しパスを取得する'''
    text_path = uno.fileUrlToSystemPath(os.path.dirname(os.path.abspath(os.path.abspath('__file__'))) + r'/csv_path_save.txt')

    try:
        oCtx = uno.getComponentContext()
        oServiceManager = oCtx.ServiceManager
        oFilePicker = oServiceManager.createInstance('com.sun.star.ui.dialogs.FilePicker')
        oFilePicker.appendFilter("All Files (*.*)", "*.*")
        oAccept = oFilePicker.execute()
        if oAccept == 1:
            oFiles = oFilePicker.getFiles()
            oFileURL = oFiles[0]

            CSV_PATH = os.path.dirname(uno.fileUrlToSystemPath(oFileURL))+r'/'
            with open(text_path, mode='w') as f:
                f.write(CSV_PATH)

            Tool.MsgBox(r'デフォルトフォルダの設定に成功しました。')#+'\n\n'+r'以降'+'\n'+r'1. フォルダの場所を変更する際'+'\n'+r'2. 別のフォルダにマクロ用データを保存する場合'+'\n'+r'には、再度デフォルトフォルダを設定し直してください。'+'\n\n\n'+r'不明な点がございましたら、マニュアルやトラブルシューティングを参考にするか、もしくは科目リーダーに問い合わせ頂くようお願い致します。'

        else:
            Tool.MsgBox(r'フォルダが選択されませんでした。')

    except:
        oDisp = ''
        oDisp = r'エラーが発生しました。'+'\n'+str(traceback.format_exc())+'\n'
        Tool.MsgBox(oDisp)

def set_status_by_button(*args):

    param_dict = Tool.get_param(args[0])

    # button_typeがない場合
    if "button_type" in param_dict == True:
        raise InvalidParameterError("Parameter ""button_type"" Required (" + args[0] + ")")

    if param_dict["button_type"] == "genten":
        # 構造式減点
        toan_list[int(param_dict["toan_index"])] \
            .daimon_list[int(param_dict["daimon_index"])] \
            .switch_genten_status()

    elif param_dict["button_type"] == "circle":
        # まる
        toan_list[int(param_dict["toan_index"])] \
            .daimon_list[int(param_dict["daimon_index"])] \
            .shomon_list[int(param_dict["shomon_index"])] \
            .set_status(ShomonStatus.CIRCLE, True)

    elif param_dict["button_type"] == "x":
        # ばつ
        toan_list[int(param_dict["toan_index"])] \
            .daimon_list[int(param_dict["daimon_index"])] \
            .shomon_list[int(param_dict["shomon_index"])] \
            .set_status(ShomonStatus.X, True)

    elif param_dict["button_type"] == "triangle":
        # さんかく
        toan_list[int(param_dict["toan_index"])] \
            .daimon_list[int(param_dict["daimon_index"])] \
            .shomon_list[int(param_dict["shomon_index"])] \
            .set_status(ShomonStatus.TRIANGLE, True)

def switch_key_tensaku_status(*args):
    param_dict = Tool.get_param(args[0])
    toan_list[int(param_dict["toan_index"])].switch_key_tensaku_status()

def switch_guideline_status(*args):
    param_dict = Tool.get_param(args[0])
    toan_list[int(param_dict["toan_index"])].switch_guideline_status()

def switch_export_status(*args):
    param_dict = Tool.get_param(args[0])
    toan_list[int(param_dict["toan_index"])].switch_export_status()

def switch_reconstitute_status(*args):
    param_dict = Tool.get_param(args[0])
    toan_list[int(param_dict["toan_index"])].switch_reconstitute_status()


# test以外のメソッドを管理画面で非表示にする
g_exportedScripts = test,path_setting


# Extensionとしてのパスを設定する
# TODO: pack as extension
# g_ImplementationHelper = unohelper.ImplementationHelper()
# g_ImplementationHelper.addImplementation(None, MACRO_PATH, (MACRO_PATH,),)
