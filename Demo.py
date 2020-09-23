from time import sleep
import requests, time, logging
from lxml import etree
import CustomLogger
import openpyxl
import sys
import os


class DHgate:
    """实现输入目标url，获取当前所在的页数和当前页的所在位置
    
    此站点是无限循环，所以循环遍历没有尽头。
    但是到达末页之后，往后的每页是循环重复的，可用此来判断结束点。

    实现：
        1、商品目录过长，单个商品的爬取会浪费时间，采取网络异步请求
            - 问题：短时间内大批量访问会造成ip封禁 <-采用代理形式
            - 问题：

        2、需求刷新次数，以及刷新目标商品的存储位置

        3、更换设计模式，采取商品id的形式进行比较


    keywords:要检索的商品名称
    """
    def __init__(self) -> None:
        # 日志输出
        self.logger = CustomLogger.custom().logger
        # 目标商品地址
        self.targetgoods = self.explain()
        # 检索商品名
        self.keywords = self.searchKey()
        # 目标起始地址
        self.url = "https://pt.dhgate.com/w/{keywords}/{pagenum}.html"
        # 上一页的数据
        self.uppagedata = [""]

        # 实例openpyxl
        self.wb = openpyxl.Workbook()
        # 首先运行说明
        self.ws = self.wb.active
        self.ws.append([
            "序号",
            "标题",
            "链接",
            "编号",
            "价格",
        ])
        self.page_num = self.search_page_num()
        self.index = 0
        self.filename = "数据.xlsx"

    # 用户输入以及简单介绍
    def explain(self) -> str:
        text = """
        author:Rm
        ---------此程序仅为魏总使用---------
        "按照下方提示进行输入操作"
        """
        self.logger.warning(text)
        sleep(1)
        self.logger.warning("输入或复制粘贴目标产品地址：(code或者url)")
        result = input()
        if self.input_process(result):
            return result
        else:
            self.logger.error("程序退出")
            sys.exit()

    # 检索的关键字
    def searchKey(self) -> str:
        self.logger.warning("请输入要搜索的关键词：")
        return input()

    # 需要检索的页数
    def search_page_num(self) -> int:
        self.logger.warning("请输入要比对的页数：")
        page_num = input()
        return int(page_num)

    # 根据网址获取目标网址商品的id
    def target_goods(self) -> str:
        try:
            if int(self.targetgoods):
                self.logger.debug(f'已获取到目标地址的id:{self.targetgoods}')
                return self.targetgoods
        except ValueError as error:
            targetid = self.targetgoods.split("?")[0].split("/")[-1].split(
                ".")[0]
            self.logger.debug(f'已获取到目标地址的id:{targetid}')
            return targetid

    # 判断输入字符串限制
    def input_process(slef, input) -> bool:
        flag = False
        # 字符串以http开头
        if input.startswith("http"):
            flag = True
        try:
            if int(input):
                flag = True
        except ValueError as error:
            slef.logger.error(f"输入类型错误-->{error}")
            flag = False
        return flag

    # 网站页数迭代
    def page_iter(self, pagenum: int) -> list:
        url = self.url.format(keywords=self.keywords, pagenum=pagenum)
        self.logger.info(f"当前地址为：{url}")
        resp = requests.get(url)
        xpath_obj = etree.HTML(resp.text)
        # 产品标题
        item_title_list = xpath_obj.xpath(
            "//div[@class='gitem ']//h3/a/@title")
        # 产品地址
        item_url_list = xpath_obj.xpath("//div[@class='gitem ']//h3/a/@href")
        # 产品编码
        item_code_list = xpath_obj.xpath(
            '//div[@class="gitem "]/div/a/@itemcode')
        # 产品价格
        item_price_list = xpath_obj.xpath(
            '//div[@class="gitem "]//span[@class="weight"]/text()')
        # TODO:将每一页的code和price保存到Excel中
        self.save_excel(item_title_list, item_url_list, item_code_list,
                        item_price_list)
        if len(item_code_list) == 0:
            return
        else:
            # 判断是否重复
            if (self.is_repeat(item_code_list)):
                self.logger.info("当前页与上一页重复")
                yield item_code_list
            else:
                self.logger.info("当前页与上一页不重复")
                self.uppagedata = item_code_list
                yield item_code_list
                # 将现在爬取的存储在变量中，需要与下一页作比较

    # 判断网站结束位置
    def is_repeat(self, newpagedata) -> bool:
        flag = True
        for old, new in zip(self.uppagedata, newpagedata):
            if old == new:
                flag = True
            else:
                flag = False
        return flag

    # 保存结果到本地
    def save_local(self, url, data_list, target_tile) -> None:
        filename = "result.txt"
        target_tile_index = 0
        for index, item in enumerate(data_list):
            if item == target_tile:
                target_tile_index = index + 1
        result = f'定位地址：{url}\n数据列表：{data_list}\n目标id：{target_tile}\n目标id排行为：{str(target_tile_index)}'
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(result)
        file_path = os.path.join(os.path.abspath(os.path.dirname(__name__)),
                                 filename)
        self.logger.debug(f"当前检索id已保存在：{file_path}")

    # 保存Excel
    def save_excel(self, title_list, url_list, code_list, price_list) -> None:
        for title_item, url_item, code_item, price_item in zip(
                title_list, url_list, code_list, price_list):
            # self.logger.info(f"{title_item}{url_item}{code_item}{price_item}")
            self.index += 1
            self.ws.append(
                [str(self.index), title_item, url_item, code_item, price_item])
        try:
            self.wb.save(self.filename)
            path_file = os.path.join(
                os.path.abspath(os.path.dirname(__name__)), self.filename)
            self.logger.warning(f"数据已保存在：{path_file}")
        except PermissionError as error:
            # 文件读取出错解决
            self.logger.error(f"文件读取异常，请关闭目标文件后重新运行--->{error}")
            self.logger.error("程序退出")
            sys.exit()

    # 类中所有方法在此调用
    def main(self):
        try:
            target_tile = self.target_goods()
            for item in range(self.page_num):
                data_list = next(self.page_iter(item))
                if data_list:
                    if target_tile in data_list:
                        # 目标产品在当前页
                        url = self.url.format(keywords=self.keywords,
                                              pagenum=str(item))
                        self.logger.warning("目标产品id在当前页内")
                        # 存储结果到本地`
                        self.save_local(url, data_list, target_tile)

                    else:
                        self.logger.info("目标产品id在不当前页内")
                else:
                    self.logger.warning("获取到产品页面为空，停止运行程序")
                    break
        except:
            try:
                # 如果运行中存在异常，则直接保存现有数据
                self.wb.save("数据.xlsx")
            except PermissionError as error:
                # 文件读取出错解决
                self.logger.error("文件读取异常，请关闭目标文件后重新运行")
                self.logger.error("程序退出")
                sys.exit()


# 主程序运行
if __name__ == "__main__":
    dhgate = DHgate()
    dhgate.main()
