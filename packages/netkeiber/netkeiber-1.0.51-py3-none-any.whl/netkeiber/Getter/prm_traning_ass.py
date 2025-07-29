import urllib.parse as urlParse
import LibHanger.Library.uwLogger as Logger
from bs4 import Tag
from pandas.core.frame import DataFrame
from enum import Enum
from decimal import Decimal
from LibHanger.Models.recset import recset
from Scrapinger.Library.browserContainer import browserContainer
from netkeiber.Library.netkeiberException import arrivalOrderValueError
from netkeiber.Library.netkeiberException import gettingValueError
from netkeiber.Library.netkeiberConfig import netkeiberConfig
from netkeiber.Library.netkeiberException import getterError
from netkeiber.Models.prm_traning_ass import prm_traning_ass
from netkeiber.Getter.Base.baseGetter import baseGetter


class getter_prm_traning_ass(baseGetter):
    """
    調教情報取得クラス
    (prm_traning_ass)
    """

    class oikiriTableCol(Enum):
        """
        調教情報列インデックス
        """

        horseNo = 3
        """ 馬番 """

        horseId = 7
        """ 競走馬ID """

        assessmentJp = 9
        """ 評価(日本語) """

        assessmentAl = 11
        """ 評価(アルファベット) """

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
        self.rsTraningAss = recset[prm_traning_ass](prm_traning_ass)

    @property
    def scrapingType(self):
        """
        ScrapingType
        スクレイピング方法を指定する(unknownの場合はconfig側で指定した設定を優先する)
        """

        return netkeiberConfig.settingValueStruct.ScrapingType.selenium

    @Logger.loggerDecorator("getData", ["race_id"])
    def getData(self, *args, **kwargs):
        """
        調教情報取得

        Parameters
        ----------
        kwargs : dict
            @race_id
                レースID
        """

        # 調教情報をDataFrameで取得
        try:
            kwargs["getter"] = self

            # 調教情報取得
            result = self.getOpenInfoDataToDataFrame(**kwargs)

        except:
            raise getterError

        return result

    @Logger.loggerDecorator("getOpenInfoDataToDataFrame")
    def getOpenInfoDataToDataFrame(self, *args, **kwargs):
        """
        調教情報取得

        Parameters
        ----------
        kwargs : dict
            @race_id
                レースID
        """

        # 検索url(ルート)
        rootUrl = urlParse.urljoin(
            self.config.netkeibaUrl_race,
            self.config.netkeibaUrlSearchKeyword.race,
        )
        # 検索url(追切情報)
        oikiriUrl = urlParse.urljoin(
            rootUrl, self.config.netkeibaUrlSearchKeyword.oikiri
        )
        oikiriUrl = oikiriUrl.format(kwargs.get("race_id"))

        # ページロード
        self.wdc.browserCtl.loadPage(oikiriUrl)

        # pandasデータを返却する
        return self.wdc.browserCtl.createSearchResultDataFrame(**kwargs)

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

            return "#delay_umai_goods_f"

        def getPrmRaceResult(self, *args, **kwargs):
            """
            調教情報をDataFrameで返す(By Selenium)

            Parameters
            ----------
            kwargs : dict
                @race_id
                    取得対象レースID
            """

            # getterインスタンス取得
            bc: getter_prm_traning_ass = kwargs.get("getter")

            # race_id取得
            race_id: str = kwargs.get("race_id")

            # bsSrc取得
            bsSrc = self.getBeautifulSoup()

            # 調教情報取得
            oikiriTable = bsSrc.find(class_="OikiriTable")
            if oikiriTable:

                # 調教情報model用意
                traningAss = recset[prm_traning_ass](prm_traning_ass)

                # 調教情報テーブル取得
                traningAssList = oikiriTable.find_all(class_="HorseList")

                for traningAssListRow in traningAssList:
                    try:
                        # 調教情報の行取得
                        traningAssListRow_t: Tag = traningAssListRow
                        drow = traningAssListRow_t.contents

                        # 馬番
                        horseId_t: Tag = drow[bc.oikiriTableCol.horseNo.value]
                        horseNo = Decimal(horseId_t.text)
                        # 競走馬ID
                        horseId_t: Tag = drow[bc.oikiriTableCol.horseId.value]
                        horseIdhref_t: Tag = horseId_t.find_all("a")[0]
                        horseId = ""
                        if horseIdhref_t:
                            horseId = str(horseIdhref_t.get("href")).split("/")[4]
                        # 評価(日本語)
                        assessment_jp = drow[bc.oikiriTableCol.assessmentJp.value].text
                        # 評価(アルファベット)
                        assessment_al = drow[bc.oikiriTableCol.assessmentAl.value].text

                        # Modelに追加
                        traningAss.newRow()
                        traningAss.fields(prm_traning_ass.race_id).value = race_id
                        traningAss.fields(prm_traning_ass.horse_no).value = horseNo
                        traningAss.fields(prm_traning_ass.assessment_jp).value = assessment_jp
                        traningAss.fields(prm_traning_ass.assessment_al).value = assessment_al
                        traningAss.fields(prm_traning_ass.updinfo).value = bc.getUpdInfo()

                        # コンソール出力
                        print("馬番={0}".format(str(horseNo)))
                        print("馬ID={0}".format(horseId))

                    except arrivalOrderValueError as aoException:  # 着順例外
                        Logger.logging.error(str(aoException))
                        raise
                    except gettingValueError as gvException:  # 値例外
                        Logger.logging.error(str(gvException))
                        raise
                    except Exception as e:  # その他例外
                        Logger.logging.error(str(e))
                        raise

                # レコードセットマージ
                bc.rsTraningAss.merge(traningAss)

                # 戻り値を返す
                return traningAss.getDataFrame()

        def createSearchResultDataFrameByWebDriver(
            self, _, *args, **kwargs
        ) -> DataFrame:
            """
            調教情報をDataFrameで返す(By Selenium)
            """

            return self.getPrmRaceResult(*args, **kwargs)
