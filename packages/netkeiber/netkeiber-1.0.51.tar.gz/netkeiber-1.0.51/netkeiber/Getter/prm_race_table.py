import re
import urllib.parse as urlParse
import datetime
import LibHanger.Library.uwLogger as Logger
from selenium.webdriver.remote.webelement import WebElement
from enum import Enum
from decimal import Decimal
from pandas.core.frame import DataFrame
from LibHanger.Models.recset import recset
from Scrapinger.Library.browserContainer import browserContainer
from netkeiber.Library.netkeiberConfig import netkeiberConfig
from netkeiber.Library.netkeiberException import getterError
from netkeiber.Library.netkeiberException import arrivalOrderValueError
from netkeiber.Library.netkeiberException import gettingValueError
from netkeiber.Models.prm_race_table import prm_race_table
from netkeiber.Models.prm_race_info import prm_race_info
from netkeiber.Models.prm_odds import prm_odds
from netkeiber.Getter.Base.baseGetter import baseGetter


class getter_prm_race_table(baseGetter):
    """
    出馬表データ取得クラス
    (prm_race_result)
    """

    class raceTableCol(Enum):
        """
        出馬表列インデックス
        """

        frameNo = 0
        """ 枠番 """

        horseNo = 1
        """ 馬番 """

        horseId = 3
        """ 競走馬ID """

        sexAge = 4
        """ 性齢 """

        weight = 5
        """ 斤量 """

        jockey_id = 6
        """ 騎手ID """

        trainer_id = 7
        """ 調教師ID """

        horse_weight = 8
        """ 馬体重増減 """

        win_odds = 9
        """ 単勝オッズ """

        popular = 10
        """ 人気 """
            
    def __init__(self) -> None:
        """
        コンストラクタ
        """

        # 基底コンストラクタ
        super().__init__()

        # レコードセット初期化
        self.init_recset()

    def init_recset(self):
        """
        レコードセット初期化
        """

        # レコードセット初期化
        self.rsRaceTable = recset[prm_race_table](prm_race_table)
        self.rsRaceInfo = recset[prm_race_info](prm_race_info)

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
        出馬表データ取得

        Parameters
        ----------
        kwargs : dict
            @race_id
                取得対象レースID
        """

        # 出馬表をDataFrameで取得
        try:
            kwargs["getter"] = self

            # 出馬表データ取得
            result = self.getRaceDataToDataFrame(**kwargs)

        except:
            raise getterError

        return result

    def getOpenInfo(self, openInfoString: str):
        return openInfoString

    def getDirection(self, directionString: str):
        drc = self.config.settingValueStruct.Direction
        direction = ""

        if drc.Steeplechase in directionString:
            direction = drc.Steeplechase
        elif "左" in directionString:
            direction = drc.left
        elif "右" in directionString:
            direction = drc.right

        return direction

    def getDistance(self, distanceString: str):
        distance = 0

        distanceTmp = distanceString.replace("内2周", "")
        distanceTmp = str(re.sub(r"\D", "", distanceTmp))
        if distanceTmp.isdigit():
            distance = int(distanceTmp)

        return distance

    def getGroundKbn(self, groundKbnString: str):
        gkb = self.config.settingValueStruct.GroundKbn
        ground_kbn = gkb.Turf

        if gkb.SteeplechaseAbbr in groundKbnString and not (
            gkb.DirtAbbr in groundKbnString
        ):
            ground_kbn = gkb.Steeplechase_Turf
        elif gkb.SteeplechaseAbbr in groundKbnString and not (
            gkb.TurfAbbr in groundKbnString
        ):
            ground_kbn = gkb.Steeplechase_Dirt
        elif (
            gkb.SteeplechaseAbbr in groundKbnString
            and gkb.TurfAbbr in groundKbnString
            and gkb.DirtAbbr in groundKbnString
        ):
            ground_kbn = gkb.Steeplechase_TurfAndDirt
        elif gkb.TurfAbbr in groundKbnString:
            ground_kbn = gkb.Turf
        elif gkb.DirtAbbr in groundKbnString:
            ground_kbn = gkb.Dirt
        return ground_kbn

    def getWeather(self, weatherString: str):
        weather = ""

        weatherTmp = weatherString.split(":")
        if len(weatherTmp) > 0:
            weather = weatherTmp[1]
        return weather.strip()

    def getGroundCond(self, groundCondString: str, groundCond_dString: str):
        groundCond = ""
        groundCond_d = ""

        groundCondTmp = groundCondString.split(":")
        groundCond = groundCondTmp[1]
        if groundCond_dString != "":
            groundCond_dTmp = groundCond_dString.split(":")
            groundCond_d = groundCond_dTmp[1]
        return groundCond.strip(), groundCond_d.strip()

    def getRaceTime(self, raceTimeString: str):
        raceTime = ""

        raceTime = raceTimeString.replace("発走", "")
        return raceTime.strip()

    def getGrade(self, race_nm: str):
        grd = self.config.settingValueStruct.Grade
        grade = grd.defaultGrade

        # レース名の中にG1,G2,G3の文字列が存在するか
        if "G1" in race_nm:
            grade = grd.g1Grade
        elif "G2" in race_nm:
            grade = grd.g2Grade
        elif "G3" in race_nm:
            grade = grd.g3Grade

        return grade

    def getRaceDate(self, open_id: str):
        raceDate = datetime.date(
            int(open_id[0:4]), int(open_id[4:6]), int(open_id[6:8])
        )
        return raceDate

    def getHeadCount(self, headCountStr: str):
        headCountTmp = str(re.sub(r"\D", "", headCountStr))
        if headCountTmp.isdigit():
            headCount = int(headCountTmp)
        return headCount

    def getWinOdds(self, winOddsString: str):
        winOdds = 0
        if winOddsString == "":
            return winOdds
        if winOddsString == "---":
            return winOdds

        try:
            # 単勝オッズ
            winOdds = Decimal(winOddsString)

        except Exception as e:
            Logger.logging.error("win_odds Get Error : Value=" + winOddsString)
            Logger.logging.error(str(e))

        return winOdds

    def getPopular(self, popularString: str):
        popular = 0

        try:
            # 人気
            if popularString.isdigit():
                popular = Decimal(popularString)

        except Exception as e:
            Logger.logging.error("popular Get Error : Value=" + popularString)
            Logger.logging.error(str(e))

        return popular

    def getHorseWeight(self, horseWeightString: str):
        """
        馬体重取得
        """

        horseWeight = 0
        if horseWeightString == "":
            return horseWeight

        try:
            # 馬体重(体重部分取得)
            horseWeightTemp = re.sub("\(.+?\)", "", horseWeightString)
            if horseWeightTemp.isdigit():
                horseWeight = int(horseWeightTemp)

        except Exception as e:
            Logger.logging.error("horse_weight Get Error : Value=" + horseWeight)
            Logger.logging.error(str(e))

        return horseWeight

    def getWeightDiff(self, weightDiffString: str):
        """
        馬体重差分取得
        """

        weightDiff = 0
        if weightDiffString == "":
            return weightDiff
        if weightDiffString == "計不":
            return weightDiff

        try:
            # 馬体重(増減部分取得)
            weightDiffTemp: str = re.findall("(?<=\().+?(?=\))", weightDiffString)[0]
            if weightDiffTemp.replace("+", "").replace("-", "").isdigit():
                weightDiff = int(weightDiffTemp)

        except Exception as e:
            Logger.logging.error(
                "horse_weight(diff) Get Error : Value=" + weightDiffString
            )
            Logger.logging.error(str(e))

        return weightDiff

    @Logger.loggerDecorator("getRaceDataToDataFrame")
    def getRaceDataToDataFrame(self, *args, **kwargs):
        """
        出馬表データ取得

        Parameters
        ----------
        kwargs : dict
            @race_id
                取得対象レースID
        """

        # 検索url(ルート)
        rootUrl = urlParse.urljoin(
            self.config.netkeibaUrl_race,
            self.config.netkeibaUrlSearchKeyword.race,
        )
        # 検索url(レース結果)
        raceUrl = urlParse.urljoin(
            rootUrl, self.config.netkeibaUrlSearchKeyword.shutuba
        )
        raceUrl = raceUrl.format(kwargs.get("race_id"))

        # ページロード
        self.wdc.browserCtl.loadPage(raceUrl)

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

            # 基底コンストラクタ
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
            出馬表データをDataFrameで返す(By Selenium)

            Parameters
            ----------
            kwargs : dict
                @race_id
                    取得対象レースID
                @racecourse_id
                    コースID
                @open_id
                    開催ID
            """

            # getterインスタンス取得
            bc: getter_prm_race_table = kwargs.get("getter")

            # race_id取得
            race_id: str = kwargs.get("race_id")
            # racecourse_id取得
            racecourse_id: str = kwargs.get("racecourse_id")
            # open_id取得
            open_id: str = kwargs.get("open_id")

            # RaceList_Item01取得
            raceListItem01 = self.wDriver.find_elements_by_class_name("RaceList_Item01")

            if raceListItem01:

                # レース番号
                raceNo_we: WebElement = raceListItem01[0]
                raceNo: str = (
                    raceNo_we.find_element_by_class_name("RaceNum").text
                )
                raceNo = raceNo.replace("R", "")

                # RaceList_Item02取得
                raceListItem02 = self.wDriver.find_elements_by_class_name(
                    "RaceList_Item02"
                )

                # レース名
                raceNm_we: WebElement = raceListItem02[0]
                raceNm = raceNm_we.find_element_by_class_name("RaceName").text

                # グレード
                grade = bc.getGrade(raceNm)

                # RaceData01取得
                raceData01: WebElement = raceNm_we.find_element_by_class_name("RaceData01")
                # RaceData02取得
                raceData02: WebElement = raceNm_we.find_element_by_class_name("RaceData02")

                # レース概要1
                race_summary1 = raceData01.text
                race_summary1_split = str(race_summary1).split("/")

                # レース概要2
                race_summary2_List = []
                for spanIndex in range(0, 8):
                    race_summary2_List.append(
                        raceData02.find_elements_by_tag_name("span")[spanIndex].text
                    )
                race_summary2 = " ".join(race_summary2_List)
                # レース概要3
                race_summary3 = raceData02.find_elements_by_tag_name("span")[8].text
                # 頭数
                headCount = bc.getHeadCount(
                    raceData02.find_elements_by_tag_name("span")[7].text
                )

                # レース概要1取得
                # 取得例)10:45発走 / ダ1700m (右) / 天候:晴 / 馬場:良
                # [0]:発送時刻
                # [1]:馬場・距離
                # [2]:天候
                # [3]:馬場状態
                # [4]:馬場状態(ダート)　※阪神障害の時に入る

                # 向き
                direction = bc.getDirection(race_summary1_split[1])
                # 距離
                distance = bc.getDistance(race_summary1_split[1])
                # 芝/ダート
                ground_kbn = bc.getGroundKbn(race_summary1_split[1])
                # 天候
                weather = bc.getWeather(race_summary1_split[2])
                # 馬場状態
                groundCondString = ""
                groundCond_dString = ""
                if len(race_summary1_split) > 4:
                    groundCondString = race_summary1_split[3]
                    groundCond_dString = race_summary1_split[4]
                else:
                    groundCondString = race_summary1_split[3]
                ground_cond, ground_cond_d = bc.getGroundCond(
                    groundCondString, groundCond_dString
                )
                # 発送時刻
                race_time = bc.getRaceTime(race_summary1_split[0])
                # 日付
                race_date = bc.getRaceDate(open_id)

                # レース情報model用意
                prmRaceInfo = recset[prm_race_info](prm_race_info)

                # Modelに追加
                prmRaceInfo.newRow()
                prmRaceInfo.fields(prm_race_info.race_id).value = race_id
                prmRaceInfo.fields(prm_race_info.race_no).value = raceNo
                prmRaceInfo.fields(prm_race_info.race_nm).value = raceNm
                prmRaceInfo.fields(prm_race_info.grade).value = grade
                prmRaceInfo.fields(prm_race_info.race_summary1).value = race_summary1
                prmRaceInfo.fields(prm_race_info.race_summary2).value = race_summary2
                prmRaceInfo.fields(prm_race_info.race_summary3).value = race_summary3
                prmRaceInfo.fields(prm_race_info.direction).value = direction
                prmRaceInfo.fields(prm_race_info.distance).value = distance
                prmRaceInfo.fields(prm_race_info.ground_kbn).value = ground_kbn
                prmRaceInfo.fields(prm_race_info.weather).value = weather
                prmRaceInfo.fields(prm_race_info.ground_cond).value = ground_cond
                prmRaceInfo.fields(prm_race_info.ground_cond_d).value = ground_cond_d
                prmRaceInfo.fields(prm_race_info.race_time).value = race_time
                prmRaceInfo.fields(prm_race_info.race_date).value = race_date
                prmRaceInfo.fields(prm_race_info.head_count).value = headCount
                prmRaceInfo.fields(prm_race_info.racecourse_id).value = racecourse_id
                prmRaceInfo.fields(prm_race_info.updinfo).value = bc.getUpdInfo()

                # 出馬表テーブル取得
                raceTables: WebElement = self.wDriver.find_element_by_class_name("RaceTableArea")
                if raceTables:

                    # 出馬表データmodel用意
                    raceResult = recset[prm_race_table](prm_race_table)

                    # HorseList取得
                    horseList = raceTables.find_elements_by_class_name("HorseList")

                    for horseListRow in horseList:
                        try:
                            # 出馬表の行取得
                            horseListRow_we: WebElement = horseListRow
                            drow: list[WebElement] = horseListRow_we.find_elements_by_tag_name("td")
                            # 枠番
                            frameNo = Decimal(
                                drow[bc.raceTableCol.frameNo.value].text
                            )
                            # 馬番
                            horseNo = Decimal(
                                drow[bc.raceTableCol.horseNo.value].text
                            )
                            # 競走馬ID
                            horseIdhref_we: WebElement = drow[bc.raceTableCol.horseId.value]
                            horseIdhref_we = horseIdhref_we.find_element_by_tag_name("a")
                            horseId = ""
                            if horseIdhref_we:
                                horseId = horseIdhref_we.get_attribute("href").split("/")[4]
                            # 馬名
                            horseNm_we: WebElement = drow[bc.raceTableCol.horseId.value]
                            horseNm = horseNm_we.text
                            # 性齢
                            sexAge_we: WebElement = drow[bc.raceTableCol.sexAge.value]
                            sexAge = sexAge_we.text
                            # 斤量
                            weight_we: WebElement = drow[bc.raceTableCol.weight.value]
                            weight = Decimal(weight_we.text)
                            # 騎手ID
                            jockeyIdhref_we: WebElement = drow[bc.raceTableCol.jockey_id.value]
                            jockeyIdhref_we = jockeyIdhref_we.find_element_by_tag_name("a")
                            jockey_id = ""
                            if jockeyIdhref_we:
                                jockey_id = jockeyIdhref_we.get_attribute("href").split("/")[6]
                            # 調教師ID
                            trainerIdhref_we: WebElement = drow[bc.raceTableCol.trainer_id.value]
                            trainerIdhref_we = trainerIdhref_we.find_element_by_tag_name("a")
                            trainer_id = ""
                            if trainerIdhref_we:
                                trainer_id = trainerIdhref_we.get_attribute("href").split("/")[6]
                            # 単勝オッズ
                            win_odds_we: WebElement = drow[bc.raceTableCol.win_odds.value]
                            win_odds = bc.getWinOdds(win_odds_we.text)
                            # 人気
                            popular_we: WebElement = drow[bc.raceTableCol.popular.value]
                            popular = bc.getPopular(popular_we.text)
                            # 馬体重
                            horse_weight_we: WebElement = drow[bc.raceTableCol.horse_weight.value]
                            horse_weight = bc.getHorseWeight(horse_weight_we.text)
                            weight_diff_we: WebElement = drow[bc.raceTableCol.horse_weight.value]
                            weight_diff = bc.getWeightDiff(weight_diff_we.text)
                            # Modelに追加
                            raceResult.newRow()
                            raceResult.fields(prm_race_table.race_id).value = race_id
                            raceResult.fields(prm_race_table.frame_no).value = frameNo
                            raceResult.fields(prm_race_table.horse_no).value = horseNo
                            raceResult.fields(prm_race_table.horse_id).value = horseId
                            raceResult.fields(prm_race_table.horse_nm_en).value = horseNm
                            raceResult.fields(prm_race_table.sex_age).value = sexAge
                            raceResult.fields(prm_race_table.weight).value = weight
                            raceResult.fields(prm_race_table.jockey_id).value = jockey_id
                            raceResult.fields(prm_race_table.trainer_id).value = trainer_id
                            raceResult.fields(prm_race_table.win_odds).value = win_odds
                            raceResult.fields(prm_race_table.popular).value = popular
                            raceResult.fields(prm_race_table.horse_weight).value = horse_weight
                            raceResult.fields(prm_race_table.weight_diff).value = weight_diff
                            raceResult.fields(prm_race_table.updinfo).value = bc.getUpdInfo()

                            # コンソール出力
                            print("枠番={0}".format(str(frameNo)))
                            print("馬番={0}".format(str(horseNo)))
                            print("馬ID={0}".format(horseId))
                            print("馬名={0}".format(horseNm))

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
                bc.rsRaceTable.merge(raceResult)
                bc.rsRaceInfo.merge(prmRaceInfo)

                # 戻り値を返す
                return raceResult.getDataFrame()

        def createSearchResultDataFrameByWebDriver(
            self, element, *args, **kwargs
        ) -> DataFrame:
            """
            レースID情報をDataFrameで返す(By Selenium)
            """

            return self.getPrmRaceResult(*args, **kwargs)
