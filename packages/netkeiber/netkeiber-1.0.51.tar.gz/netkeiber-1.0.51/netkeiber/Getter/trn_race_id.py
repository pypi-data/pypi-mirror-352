import urllib.parse as urlParse
import LibHanger.Library.uwLogger as Logger
from enum import Enum
from bs4 import Tag
from pandas.core.frame import DataFrame
from selenium.webdriver.remote.webelement import WebElement
from LibHanger.Models.recset import recset
from Scrapinger.Library.browserContainer import browserContainer
from netkeiber.Library.netkeiberConfig import netkeiberConfig
from netkeiber.Library.netkeiberException import racdIdCheckError
from netkeiber.Library.netkeiberDeclare import netkeiberDeclare as nd
from netkeiber.Models.trn_race_id import trn_race_id
from netkeiber.Getter.Base.baseGetter import baseGetter


class getter_trn_race_id(baseGetter):
    """
    レースID情報取得クラス
    (trn_race_id)
    """

    class methodType(Enum):
        """
        データ取得メソッド
        """

        getOpenCal = 0
        """ 開催カレンダー取得メソッド """

        getRaceId = 1
        """ レースID情報取得メソッド(蓄積系) """

        getPrmRaceId = 2
        """ レースID情報取得メソッド(速報系) """

    def __init__(self) -> None:
        """
        コンストラクタ
        """

        super().__init__()

        # レコードセット初期化
        self.init_recset()

    def init_recset(self):
        """
        レコードセット初期化
        """

        # レコードセット初期化
        self.rsRaceId = recset[trn_race_id](trn_race_id)

    @property
    def scrapingType(self):
        """
        ScrapingType
        スクレイピング方法を指定する(unknownの場合はconfig側で指定した設定を優先する)
        """

        return netkeiberConfig.settingValueStruct.ScrapingType.selenium

    @Logger.loggerDecorator("getData", ["year"])
    def getData(self, *args, **kwargs):
        """
        開催情報取得

        Parameters
        ----------
        kwargs : dict
            @year
                開催年
            @month
                開催月
            @day
                カレンダーを取得する日にちの終端
        """

        # Getterクラス取得
        kwargs["getter"] = self

        # methodType指定
        kwargs["methodType"] = self.methodType.getOpenCal
        # 開催日情報をDataFrameで取得
        dfRaceIdCal = self.getRaceIdCalToDataFrame(**kwargs)

        # 取得した開催日をループして1つずつRaceIdを取り出す
        for _, item in dfRaceIdCal.iterrows():

            # open_id,racecourse_id指定
            kwargs["open_id"] = item[trn_race_id.open_id.key]
            kwargs["racecourse_id"] = item[trn_race_id.racecourse_id.key]
            if kwargs["day"] == 0:
                # methodType指定
                kwargs["methodType"] = self.methodType.getRaceId
                # レースID取得(蓄積系)
                self.getRaceIdToDataFrame(**kwargs)
            else:
                # 開催日指定
                kwargs["kaisai_date"] = (
                    str(kwargs["year"])
                    + str(kwargs["month"]).rjust(2, "0")
                    + str(kwargs["day"]).rjust(2, "0")
                )
                # methodType指定
                kwargs["methodType"] = self.methodType.getPrmRaceId
                # レースID取得(速報系)
                self.getPrmRaceIdToDataFrame(**kwargs)

    @Logger.loggerDecorator("getRaceIdDataToDataFrame")
    def getRaceIdCalToDataFrame(self, *args, **kwargs):
        """
        レースID情報取得(カレンダー取得)

        Parameters
        ----------
        kwargs : dict
            @year
                開催年度
            @month
                開催月
        """

        # 検索url(ルート)
        rootUrl: str = urlParse.urljoin(
            self.config.netkeibaUrl_race,
            self.config.netkeibaUrlSearchKeyword.race_id_cal,
        )
        # 検索url(レースID情報[カレンダー])
        raceIdCalUrl = rootUrl.format(kwargs.get("year"), kwargs.get("month"))

        # ページロード
        self.wdc.browserCtl.loadPage(raceIdCalUrl)

        # pandasデータを返却する
        return self.wdc.browserCtl.createSearchResultDataFrame(**kwargs)

    @Logger.loggerDecorator("getRaceIdToDataFrame")
    def getRaceIdToDataFrame(self, *args, **kwargs):
        """
        レースID情報取得(蓄積系)

        Parameters
        ----------
        kwargs : dict
            @racecourse_id
                競馬場ID
            @open_id
                開催ID
        """

        # 検索url(ルート)
        rootUrl = urlParse.urljoin(
            self.config.netkeibaUrl,
            self.config.netkeibaUrlSearchKeyword.open,
        )
        # 検索url(開催情報)
        raceIdUrl = urlParse.urljoin(
            rootUrl, kwargs.get("racecourse_id") + "/" + kwargs.get("open_id")
        )

        # ページロード
        self.wdc.browserCtl.loadPage(raceIdUrl)

        # pandasデータを返却する
        return self.wdc.browserCtl.createSearchResultDataFrame(**kwargs)

    @Logger.loggerDecorator("getPrmRaceIdToDataFrame")
    def getPrmRaceIdToDataFrame(self, *args, **kwargs):
        """
        レースID情報取得(速報系)

        Parameters
        ----------
        kwargs : dict
            @racecourse_id
                競馬場ID
            @open_id
                開催ID
        """

        # 検索url(ルート)
        rootUrl = urlParse.urljoin(
            self.config.netkeibaUrl_race,
            self.config.netkeibaUrlSearchKeyword.race_id_kaisai_date,
        )
        # 検索url(開催情報)
        raceIdUrl = rootUrl.format(kwargs.get("kaisai_date"))

        # ページロード
        self.wdc.browserCtl.loadPage(raceIdUrl)

        # pandasデータを返却する
        return self.wdc.browserCtl.createSearchResultDataFrame(**kwargs)

    def getRaceIdByLink(self, raceId_url):
        """
        リンクURLからrace_idを取得する
        
        Parameters
        ----------
        raceId_url : Any
            レースIDエレメント(a)
        """

        race_id_point = raceId_url.find("=") + 1
        return raceId_url[race_id_point : race_id_point + 12]

    class chrome(browserContainer.chrome):
        """
        ブラウザコンテナ:chrome
        """

        def __init__(
            self,
            _config: netkeiberConfig,
            _scrapingType: netkeiberConfig.settingValueStruct.ScrapingType,
        ):
            """
            コンストラクタ

            Parameters
            ----------
            _config : netkeiberConfig
                共通設定
            _scrapingType : netkeiberConfig.settingValueStruct.ScrapingType
                スクレイピングタイプ
            """

            # 基底側コンストラクタ
            super().__init__(_config, _scrapingType)

            self.cbCreateSearchResultDataFrameByWebDriver = (
                self.createSearchResultDataFrameByWebDriver
            )

        @property
        def delayWaitElement(self):
            """
            delayWaitElement
            delayWaitElementを文字列で指定する(指定したlocatorに対応するElementを指定する。未指定の場合はconfig側で指定した設定を優先する)
            """

            return "#navi_link_top"

        def getOpenCal(self, *args, **kwargs):
            """
            開催日カレンダー情報を取得する

            Parameters
            ----------
            kwargs : dict
            @day
                カレンダーを取得する日にちの終端
            """

            # getterインスタンス取得
            bc: getter_trn_race_id = kwargs.get("getter")

            # 取得対象日(下限)取得
            # (Weekly取得対応)
            targetDayFrom = int(kwargs.get("day")) - 2 if kwargs.get("day") != 0 else 0

            # bsSrc取得
            bsSrc = self.getBeautifulSoup()

            # class取得
            tables = bsSrc.find(class_="Calendar_Table").find_all(class_="RaceCellBox")

            if tables:

                # レースIDカレンダー情報model用意
                raceIdCalInfo = recset[trn_race_id](trn_race_id)

                for index in range(len(tables)):
                    try:
                        # tableTag取得
                        table_t:Tag = tables[index]

                        # 開催ID
                        open_id_a = table_t.find_all("a")
                        if open_id_a:
                            open_id_href_t:Tag = open_id_a[0]
                            open_id_href = open_id_href_t.get("href")
                            open_id = str(open_id_href).split("=")[1]
                        else:
                            continue

                        # カレンダーの日にち取得
                        targetDay = 0
                        day: str = table_t.find(class_="Day").text
                        if day.isdigit():
                            targetDay = int(day)

                        # 取得対象日(下限)と比較して対象外だった場合はスキップする
                        if targetDay < targetDayFrom:
                            continue

                        jyo_name = table_t.find_all(class_="JyoName")
                        for index in range(len(jyo_name)):
                            
                            # JyoNameエレメント取得
                            jyo_name_t:Tag = jyo_name[index]
                            
                            # 競馬場名
                            course_nm = jyo_name_t.text
                            # 競馬場ID
                            racecourse_id = bc.config.courseList[course_nm]

                            # Modelに追加
                            raceIdCalInfo.newRow()
                            raceIdCalInfo.fields(trn_race_id.race_id).value = "*"
                            raceIdCalInfo.fields(trn_race_id.racecourse_id).value = racecourse_id
                            raceIdCalInfo.fields(trn_race_id.open_id).value = open_id
                            raceIdCalInfo.fields(trn_race_id.updinfo).value = bc.getUpdInfo()

                            # コンソール出力
                            print("競馬場ID={0}".format(racecourse_id))
                            print("開催ID={0}".format(open_id))

                    except Exception as e:  # その他例外
                        Logger.logging.error(str(e))

                return raceIdCalInfo.getDataFrame(keyDrop=False)

        def getRaceId(self, *args, **kwargs):
            """
            レースID情報を取得する(蓄積系)

            Parameters
            ----------

            kwargs : dict
                @open_id
                    開催ID
                @racecourse_id
                    競馬場ID
            """

            # getterインスタンス取得
            bc: getter_trn_race_id = kwargs.get("getter")

            # 開催ID取得
            open_id: str = kwargs.get("open_id")

            # 競馬場ID取得
            racecourse_id: str = kwargs.get("racecourse_id")

            # bsSrc取得
            bsSrc = self.getBeautifulSoup()

            # class取得
            tables = bsSrc.find(class_="race_table_01").find_all("tr")

            if tables:

                # レースID情報model用意
                raceIdInfo = recset[trn_race_id](trn_race_id)

                for index in range(len(tables)):
                    if index == 0:
                        continue
                    try:
                        # tableTag取得
                        table_t:Tag = tables[index]
                        
                        # tdTag取得
                        row = table_t.find_all("td")

                        # レースID
                        row_t:Tag = row[1]
                        race_id = str(row_t.find_all("a")[0].get("href")).split("/")[2]

                        # レースIDが数値で構成されていなければ例外を発生させる
                        if not race_id.isdigit():
                            raise racdIdCheckError

                        # Modelに追加
                        raceIdInfo.newRow()
                        raceIdInfo.fields(trn_race_id.race_id).value = race_id
                        raceIdInfo.fields(trn_race_id.racecourse_id).value = racecourse_id
                        raceIdInfo.fields(trn_race_id.open_id).value = open_id
                        raceIdInfo.fields(trn_race_id.scraping_count).value = 0
                        raceIdInfo.fields(trn_race_id.get_time).value = 0
                        raceIdInfo.fields(trn_race_id.get_status).value = nd.getStatus.unacquired.value
                        raceIdInfo.fields(trn_race_id.updinfo).value = bc.getUpdInfo()

                        # コンソール出力
                        print("レースID={0}".format(race_id))
                        print("競馬場ID={0}".format(racecourse_id))
                        print("開催日={0}".format(open_id))

                    except racdIdCheckError as e:
                        Logger.logging.error(str(e))
                        Logger.logging.error("race_id Value={0}".format(race_id))
                        Logger.logging.error("open_id Value={0}".format(open_id))

                    except Exception as e:  # その他例外
                        Logger.logging.error(str(e))

                # レコードセットマージ
                bc.rsRaceId.merge(raceIdInfo, False)

                # 戻り値をDataFrameで返却
                return raceIdInfo.getDataFrame()

        def getPrmRaceId(self, *args, **kwargs):
            """
            レースID情報を取得する(速報系)

            Parameters
            ----------
            kwargs : dict
                @open_id
                    開催ID
                @racecourse_id
                    競馬場ID
            """

            # getterインスタンス取得
            bc: getter_trn_race_id = kwargs.get("getter")

            # 開催ID取得
            open_id: str = kwargs.get("open_id")

            # 競馬場ID取得
            racecourse_id: str = kwargs.get("racecourse_id")

            # レースID情報model用意
            raceIdInfo = recset[trn_race_id](trn_race_id)

            # element取得
            elements = self.wDriver.find_elements_by_class_name("RaceList_DataItem")
            for elm in elements:

                try:

                    # aタグ取得
                    elm_we: WebElement = elm
                    elems_a: WebElement = elm_we.find_element_by_tag_name("a")

                    # race_id取得
                    race_id:str = bc.getRaceIdByLink(elems_a.get_attribute("href"))

                    # レースIDが数値で構成されていなければ例外を発生させる
                    if not race_id.isdigit():
                        raise racdIdCheckError

                    # Modelに追加
                    raceIdInfo.newRow()
                    raceIdInfo.fields(trn_race_id.race_id).value = race_id
                    raceIdInfo.fields(trn_race_id.racecourse_id).value = racecourse_id
                    raceIdInfo.fields(trn_race_id.open_id).value = open_id
                    raceIdInfo.fields(trn_race_id.scraping_count).value = 0
                    raceIdInfo.fields(trn_race_id.get_time).value = 0
                    raceIdInfo.fields(trn_race_id.get_status).value = nd.getStatus.unacquired.value
                    raceIdInfo.fields(trn_race_id.updinfo).value = bc.getUpdInfo()

                    # コンソール出力
                    print("レースID={0}".format(race_id))
                    print("競馬場ID={0}".format(racecourse_id))
                    print("開催日={0}".format(open_id))

                except racdIdCheckError as e:
                    Logger.logging.error(str(e))
                    Logger.logging.error("race_id Value={0}".format(race_id))
                    Logger.logging.error("open_id Value={0}".format(open_id))

                except Exception as e:  # その他例外
                    Logger.logging.error(str(e))

            # レコードセットマージ
            bc.rsRaceId.merge(raceIdInfo, False)

            # 戻り値をDataFrameで返却
            return raceIdInfo.getDataFrame()

        def createSearchResultDataFrameByWebDriver(
            self, _, *args, **kwargs
        ) -> DataFrame:
            """
            レースID情報をDataFrameで返す(By Selenium)
            """

            bc: getter_trn_race_id = kwargs.get("getter")
            if kwargs["methodType"] == bc.methodType.getOpenCal:
                return self.getOpenCal(*args, **kwargs)
            elif kwargs["methodType"] == bc.methodType.getRaceId:
                return self.getRaceId(*args, **kwargs)
            elif kwargs["methodType"] == bc.methodType.getPrmRaceId:
                return self.getPrmRaceId(*args, **kwargs)
