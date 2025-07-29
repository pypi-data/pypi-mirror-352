import urllib.parse as urlParse
import LibHanger.Library.uwLogger as Logger
from pandas.core.frame import DataFrame
from bs4 import Tag
from LibHanger.Models.recset import recset
from Scrapinger.Library.browserContainer import browserContainer
from netkeiber.Library.netkeiberConfig import netkeiberConfig
from netkeiber.Library.netkeiberException import getterError
from netkeiber.Models.trn_open_info import trn_open_info
from netkeiber.Getter.Base.baseGetter import baseGetter


class getter_trn_open_info(baseGetter):
    """
    開催情報取得クラス
    (trn_open_info)
    """

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
        self.rsOpenInfo = recset[trn_open_info](trn_open_info)

    @property
    def scrapingType(self):
        """
        ScrapingType
        スクレイピング方法を指定する(unknownの場合はconfig側で指定した設定を優先する)
        """

        return netkeiberConfig.settingValueStruct.ScrapingType.selenium

    @Logger.loggerDecorator("getData", ["open_id"])
    def getData(self, *args, **kwargs):
        """
        開催情報取得

        Parameters
        ----------
        kwargs : dict
            @open_id
                開催ID
        """

        # 開催情報をDataFrameで取得
        try:
            kwargs["getter"] = self
            result = self.getOpenInfoDataToDataFrame(**kwargs)
        except Exception as e:
            raise getterError(e)
        return result

    @Logger.loggerDecorator("getOpenInfoDataToDataFrame")
    def getOpenInfoDataToDataFrame(self, *args, **kwargs):
        """
        開催情報取得

        Parameters
        ----------
        kwargs : dict
            @open_id
                開催ID
        """

        # 検索url(ルート)
        rootUrl = urlParse.urljoin(
            self.config.netkeibaUrl, self.config.netkeibaUrlSearchKeyword.open
        )
        # 検索url(開催情報)
        openInfoUrl = urlParse.urljoin(
            rootUrl, kwargs.get("racecourse_id") + "/" + kwargs.get("open_id")
        )

        # ページロード
        self.wdc.browserCtl.loadPage(openInfoUrl)

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

            return "#contents"

        def createSearchResultDataFrameByWebDriver(
            self, _, *args, **kwargs
        ) -> DataFrame:
            """
            開催情報をDataFrameで返す(By Selenium)
            """

            return self.getOpenInfo(*args, **kwargs)

        def getOpenInfo(self, *args, **kwargs):
            """
            開催情報を取得する

            Parameters
            ----------
            kwargs : dict
                @open_id
                    取得対象開催ID
            """

            # getterインスタンス取得
            bc: getter_trn_open_info = kwargs.get("getter")

            # 開催ID取得
            open_id: str = kwargs.get("open_id")

            # 競馬場ID取得
            racecourse_id: str = kwargs.get("racecourse_id")

            # bsSrc取得
            bsSrc = self.getBeautifulSoup()

            # class取得
            tables = bsSrc.find(class_="race_table_01").find_all("tr")

            if tables:

                # 開催情報model用意
                openInfo = recset[trn_open_info](trn_open_info)

                for index in range(len(tables)):
                    if index == 0:
                        continue
                    try:
                        tables_t: Tag = tables[index]
                        row: list[Tag] = tables_t.find_all("td")
                        # レースNO
                        race_no = row[0].text
                        # レースID
                        race_id = str(row[1].find_all("a")[0].get("href")).split("/")[2]
                        # 勝ち馬ID
                        win_horse = str(row[3].find_all("a")[0].get("href")).split("/")[2]
                        # 勝ち馬騎手ID
                        win_jockey = str(row[3].find_all("a")[1].get("href")).split("/")[4] if len(row[3].find_all("a")) > 1 else ''
                        # 2着馬ID
                        snd_horse = str(row[4].find_all("a")[0].get("href")).split("/")[2]
                        # 2着馬騎手ID
                        snd_jockey = str(row[4].find_all("a")[1].get("href")).split("/")[4] if len(row[4].find_all("a")) > 1 else ''
                        # 3着馬ID
                        trd_horse = str(row[5].find_all("a")[0].get("href")).split("/")[2]
                        # 3着馬騎手ID
                        trd_jockey = str(row[5].find_all("a")[1].get("href")).split("/")[4] if len(row[5].find_all("a")) > 1 else ''

                        # Modelに追加
                        openInfo.newRow()
                        openInfo.fields(trn_open_info.open_id).value = open_id
                        openInfo.fields(trn_open_info.racecourse_id).value = racecourse_id
                        openInfo.fields(trn_open_info.race_no).value = race_no
                        openInfo.fields(trn_open_info.race_id).value = race_id
                        openInfo.fields(trn_open_info.win_horse).value = win_horse
                        openInfo.fields(trn_open_info.win_jockey).value = win_jockey
                        openInfo.fields(trn_open_info.snd_horse).value = snd_horse
                        openInfo.fields(trn_open_info.snd_jockey).value = snd_jockey
                        openInfo.fields(trn_open_info.trd_horse).value = trd_horse
                        openInfo.fields(trn_open_info.trd_jockey).value = trd_jockey
                        openInfo.fields(trn_open_info.updinfo).value = bc.getUpdInfo()

                        # コンソール出力
                        print(
                            "開催ID={0}".format(open_id),
                            end="レースNo={0}".format(race_no),
                        )

                    except Exception as e:  # その他例外
                        Logger.logging.error(str(e))
                        raise

                # レコードセットマージ
                bc.rsOpenInfo.merge(openInfo)

                # 戻り値を返す
                return openInfo.getDataFrame()
