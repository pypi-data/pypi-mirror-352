import LibHanger.Library.uwLogger as Logger
from LibHanger.Library.DataAccess.uwPostgres import uwPostgreSQL
from LibHanger.Models.recset import recset
from LibHanger.Models.saWhere import saWhere
from netkeiber.Getter.prm_traning_ass import getter_prm_traning_ass
from netkeiber.Getter.trn_race_result import getter_trn_race_result
from netkeiber.Getter.trn_horse_result import getter_trn_horse_result
from netkeiber.Getter.trn_open_info import getter_trn_open_info
from netkeiber.Getter.trn_refund_info import getter_trn_refund_info
from netkeiber.Getter.log_race_id import getter_log_race_id
from netkeiber.Models.trn_horse_result import trn_horse_result
from netkeiber.Models.trn_race_info import trn_race_info
from netkeiber.Models.trn_open_info import trn_open_info
from netkeiber.Models.trn_refund_info import trn_refund_info
from netkeiber.Library.netkeiberDeclare import netkeiberDeclare as nd
from netkeiber.Library.netkeiberException import getterError


class getter_RaceData:
    """
    レースデータ取得クラス
    """

    def __init__(self, __psgr: uwPostgreSQL):
        """
        コンストラクタ

        Parameters
        ----------
        __psgr : uwPostgreSQL
            uwPostgreSQLクラスインスタンス
        """

        # uwPostgreSQL
        self.__psgr = __psgr

        # Getterインスタンス生成
        self.createGetterInstance()

        # レコードセット初期化
        self.init_recset()

        # 取得フラグ
        self.raceResultRead = True
        self.traningAssRead = True
        self.horseResultRead = True
        self.openInfoRead = True
        self.refundInfoRead = True

        # エラー有無
        self.__hasError = False

        # スクレイピング回数
        self.__scrapingCount = 0

    def __exit__(self, ex_type, ex_value, trace):
        """
        ContextManger - exit

        Parameters
        ----------
            ex_type : Any
                ex_type
            ex_value : Any
                ex_value
            trace : Any
                trace
        """

        # with内で例外発生時
        if ex_type != None:
            # ログ出力
            Logger.logging.error(f"Exception Type={ex_type}")
            Logger.logging.error(f"Exception Value={ex_value}")
            Logger.logging.error(f"Stack trace={trace}")

        # WebDriver - Quit
        self.raceResult.quitWebDriver()
        self.horseResult.quitWebDriver()
        self.openInfo.quitWebDriver()
        self.refundInfo.quitWebDriver()
        self.traningAssInfo.quitWebDriver()
        self.raceIdLog.quitWebDriver()
        
        # Trueを返して例外を握りつぶす
        return True
    
    def createGetterInstance(self):
        """
        Getterインスタンス生成
        """

        # レース結果取得クラスインスタンス
        self.raceResult = getter_trn_race_result()

        # 競走馬成績取得クラスインスタンス
        self.horseResult = getter_trn_horse_result()

        # 開催情報取得クラスインスタンス
        self.openInfo = getter_trn_open_info()

        # 払戻情報取得クラスインスタンス
        self.refundInfo = getter_trn_refund_info()

        # 調教情報取得クラスインスタンス
        self.traningAssInfo = getter_prm_traning_ass()

        # レースIDログ
        self.raceIdLog = getter_log_race_id()

    def init_recset(self):
        """
        レコードセット初期化
        """

        self.raceResult.init_recset()
        self.horseResult.init_recset()
        self.openInfo.init_recset()
        self.refundInfo.init_recset()
        self.traningAssInfo.init_recset()
        if self.raceResult.wdc.browserCtl != None:
            self.raceResult.wdc.browserCtl.resetLoadPageCount()
        if self.horseResult.wdc.browserCtl != None:
            self.horseResult.wdc.browserCtl.resetLoadPageCount()
        if self.openInfo.wdc.browserCtl != None:
            self.openInfo.wdc.browserCtl.resetLoadPageCount()
        if self.refundInfo.wdc.browserCtl != None:
            self.refundInfo.wdc.browserCtl.resetLoadPageCount()
        if self.traningAssInfo.wdc.browserCtl != None:
            self.traningAssInfo.wdc.browserCtl.resetLoadPageCount()
        self.raceResult.rsRaceResult.setDA(self.__psgr)
        self.horseResult.rsHorseResult.setDA(self.__psgr)
        self.openInfo.rsOpenInfo.setDA(self.__psgr)
        self.refundInfo.rsRefundInfo.setDA(self.__psgr)
        self.traningAssInfo.rsTraningAss.setDA(self.__psgr)

    @property
    def scrapingCount(self):
        """
        スクレイピング回数
        """

        return self.__scrapingCount

    @property
    def hasError(self):
        """
        エラー有無
        """

        return self.__hasError

    def getData(self, race_id, open_id, racecourse_id):
        """
        データ取得

        Parameters
        ----------
        race_id : str
            レースID
        open_id : str
            開催ID
        racecourse_id : str
            競馬場ID
        """

        try:

            # エラーフラグ初期化
            self.__hasError = False

            # session - open
            self.__psgr.openSession()

            # レース結果取得判定
            if self.raceResultRead:

                # レース結果取得
                self.raceResult.getData(race_id=race_id)
                
                # レース結果の取得件数が0件だった場合は処理を抜ける
                if self.raceResult.rsRaceResult.recordCount == 0:
                    return

            # raceResult - quitWebDriver
            self.raceResult.quitWebDriver()

            # 調教情報取得判定
            if self.traningAssRead:

                # 調教情報取得
                self.traningAssInfo.getData(race_id=race_id)
            
            # traningAssInfo - quitWebDriver
            self.traningAssInfo.quitWebDriver()

            # saWhereインスタンス
            saw = saWhere()

            # レース結果ループ開始
            rsRaceResult = self.raceResult.rsRaceResult
            rsRaceInfo = self.raceResult.rsRaceInfo
            rsRaceInfo.first()
            while rsRaceResult.eof() == False:

                # 競走馬成績取得
                if self.horseResultRead:
                    
                    # 取得済データチェック
                    saw.clear()
                    saw.and_(trn_horse_result.horse_id == rsRaceResult.fields(trn_horse_result.horse_id).value
                    ).and_(trn_horse_result.race_id == rsRaceResult.fields(trn_horse_result.race_id).value
                    )
                    if self.horseResult.rsHorseResult.find(saw, recset.findOption.dataBase) == False:

                        # 競走馬成績取得
                        self.horseResult.getData(horse_id=rsRaceResult.fields(trn_horse_result.horse_id).value)

                # 払戻情報取得
                if self.refundInfoRead:

                    # 払戻ID取得
                    refund_id = rsRaceInfo.fields(trn_race_info.refund_id).value

                    # 取得済データチェック
                    rsRefundInfo = self.refundInfo.rsRefundInfo
                    saw.clear()
                    saw.and_(trn_refund_info.refund_id == refund_id
                    ).and_(trn_refund_info.racecourse_id == racecourse_id
                    ).and_(trn_refund_info.race_no == rsRaceInfo.fields(trn_race_info.race_no).value
                    )
                    if rsRefundInfo.find(saw, recset.findOption.dataBase) == False:

                        # 払戻情報取得
                        self.refundInfo.getData(refund_id=refund_id, racecourse_id=racecourse_id)

            # horseResult - quitWebDriver
            self.horseResult.quitWebDriver()
            # refundInfo - quitWebDriver
            self.refundInfo.quitWebDriver()
            
            # 開催情報取得
            if self.openInfoRead:
                
                # 取得済データチェック
                rsOpenInfo = self.openInfo.rsOpenInfo
                saw.clear()
                saw.and_(trn_open_info.open_id == open_id
                ).and_(trn_open_info.racecourse_id == racecourse_id
                )
                if rsOpenInfo.find(saw, recset.findOption.dataBase) == False:

                    # 開催情報取得
                    self.openInfo.getData(open_id=open_id, racecourse_id=racecourse_id)

            # openInfo - quitWebDriver
            self.openInfo.quitWebDriver()
                        
            # スクレイピング回数取得
            rsList = []
            rsList.append(self.raceResult.scrapingCount)
            rsList.append(self.horseResult.scrapingCount)
            rsList.append(self.openInfo.scrapingCount)
            rsList.append(self.refundInfo.scrapingCount)
            rsList.append(self.traningAssInfo.scrapingCount)
            self.__scrapingCount = sum(rsList)

        except getterError as geException:
            self.__hasError = True
            self.raceIdLog.setLogRaceId(race_id, nd.getterResult.error, geException)
        except Exception as e:
            self.__hasError = True
            self.raceIdLog.setLogRaceId(race_id, nd.getterResult.error, e)
        finally:
            # session - close
            self.__psgr.closeSession()
