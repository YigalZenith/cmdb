#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import xlwt

pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('msyh', 'msyh.ttf'))
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
import time
from reportlab.lib.units import inch


def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('msyh', 9)
    canvas.drawString(inch, 0.75 * inch, "塔读运维自动化平台")
    canvas.restoreState()


def rpt(data):
    story = []
    stylesheet = getSampleStyleSheet()
    normalStyle = stylesheet['Normal']
    curr_date = time.strftime("%Y-%m-%d", time.localtime())
    # 标题：段落的用法详见reportlab-userguide.pdf中chapter 6 Paragraph
    rpt_title = '<para autoLeading="off" fontSize=15 align=center><b><font face="msyh">塔读资产管理系统导出信息%s</font></b><br/><br/><br/></para>' % curr_date
    story.append(Paragraph(rpt_title, normalStyle))
    # component_data= [['模块', '', '', '', "", ''],]
    component_data = [['主机名','ip', '机房', '机柜', '高度','创建时间', '状态']]
    for i in data:
        node_data = "%s-%s" % (i.cabinet, i.cabinet_id)
        s = [i.hostname,i.eth1,i.idc.name,node_data,i.height,i.create_time,i.status]
        component_data.append(s)

    # 创建表格对象，并设定各列宽度
    component_table = Table(component_data, colWidths=[30, 40, 40, 30, 30, 30,60,30])
    # 添加表格样式
    component_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'msyh'),  # 字体
        ('FONTSIZE', (0, 0), (-1, -1), 5),  # 字体大小
        # ('SPAN', (0, 0), (5, 0)),#合并第一行前三列
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightskyblue),  # 设置第一行背景颜色
        # ('SPAN', (-1, 0), (-2, 0)), #合并第一行后两列
        ('ALIGN', (-1, 0), (-2, 0), 'RIGHT'),  # 对齐
        ('VALIGN', (-1, 0), (-2, 0), 'MIDDLE'),  # 对齐
        ('LINEBEFORE', (0, 0), (0, -1), 0.1, colors.grey),  # 设置表格左边线颜色为灰色，线宽为0.1
        # ('TEXTCOLOR', (0, 1), (-2, -1), colors.royalblue),#设置表格内文字颜色
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # 设置表格框线为红色，线宽为0.5
    ]))
    story.append(component_table)
    doc = SimpleDocTemplate('static/pdf/fun.pdf')
    doc.build(story, onFirstPage=myLaterPages, onLaterPages=myLaterPages)
    return True


def groups_str2(group_list):
    s = []
    for i in group_list:
        i = "%s" % (i)
        s.append(i)
    data = " | ".join(s)
    data = u"%s" % data
    return data


def group_service(data):
    s = []

    for i in data:
        i = "%s" % (i)
        s.append(i)
    data = " | ".join(s)
    data = u"%s" % data

    return data


def excel_output(data):
    """
    导出excel
    """
    file = xlwt.Workbook(encoding='utf-8')
    table = file.add_sheet(u'资产', cell_overwrite_ok=True)
    table.write(0, 1, u'主机名')
    table.write(0, 2, u'ip')
    table.write(0, 3, u'项目')
    table.write(0, 4, u'idc')
    table.write(0, 5, u'机柜')
    table.write(0, 6, u'机柜位置')
    table.write(0, 7, u'高度')
    table.write(0, 8, u'创建时间')
    table.write(0, 9, u'服务器状态')
    # table.write(0, 6, u'ip', u'主机名', u'idc', u'资产编号', u'品牌', u'配置', u'机柜')
    s = 0
    for i in data:
        s += 1
        node_data = "%s-%s" % (i.cabinet, i.cabinet_id)
        business_data = groups_str2(i.service.all())
        table.write(s, 1, i.hostname)
        table.write(s, 2, i.eth1)
        table.write(s, 3, u"%s" % business_data)
        table.write(s, 4, i.idc.name)
        if i.cabinet or i.cabinet_id:
            table.write(s, 5, node_data)
        else:
            table.write(s, 6, "")
        table.write(s, 7, i.height)
        table.write(s, 8, i.create_time)
        if i.status == 0:
            table.write(s, 9, u'未安装系统')
        elif i.status == 1:
            table.write(s, 9, u'已安装系统')
        elif i.status == 2:
            table.write(s, 9, u'安装系统中')
        elif i.status == 1:
            table.write(s, 9, u'报废')

    file.save('static/pdf/fun.xls')

    return True


if __name__ == '__main__':
    rpt("test")
