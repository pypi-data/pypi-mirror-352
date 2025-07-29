from datetime import datetime
import os
import sys
import time
import LibHanger.Library.uwGetter as Getter
import LibHanger.Library.uwLogger as Logger
import LibHanger.Library.uwMath as uwMath
import netkeiber.Library.netkeiberConfiger as hc
from LibHanger.Library.DataAccess.uwPostgres import uwPostgreSQL
from LibHanger.Library.uwDeclare import uwDeclare as en
from LibHanger.Library.uwMail import uwMail
#from LibHanger.Library.uwExport import JsonExporter
#from LibHanger.Library.uwImport import JsonImporter
from LibHanger.Models.recset import recset
from LibHanger.Models.saWhere import saWhere
from LibHanger.Models.saOrderBy import saOrderBy
from LibHanger.Models.saJoin import saJoin
from netkeiber.Library.netkeiberException import getterError
from netkeiber.Library.netkeiberGlobals import *
from netkeiber.Library.netkeiberDeclare import netkeiberDeclare as nd
from netkeiber.Library.netkeiberMailer import netkeiberMailer, prmRaceIdMailer
from netkeiber.Models.trn_race_id import trn_race_id
from netkeiber.Models.trn_race_info import trn_race_info
from netkeiber.Models.prm_traning_ass import prm_traning_ass
from netkeiber.Models.viw_raceid_record_count import viw_raceid_record_count
from netkeiber.Getter.trn_race_id import getter_trn_race_id
from netkeiber.Getter.get_RaceData import getter_RaceData
from netkeiber.Getter.prm_race_table import getter_prm_race_table
from netkeiber.Getter.prm_traning_ass import getter_prm_traning_ass
from netkeiber.Register.register_RaceData import register_RaceData

def getRaceTable(filePath, fromOpenId, toOpenId):
    
    """
    出馬表データ取得メソッド ※速報系

    Parameters
    ----------
    filePath : str
        呼び出し元ファイルのパス
    fromOpenId : str
        open_id(From)
    toOpenId : str
        open_id(To)
    """

    # 共通設定
    hc.netkeiberConfiger(gv, filePath, 'config')

    # where
    w = saWhere()
    w = w.and_(trn_race_id.open_id >= fromOpenId)
    w = w.and_(trn_race_id.open_id <= toOpenId)

    # order by
    s = saOrderBy()
    s = s.asc_(trn_race_id.race_id)
    
    # uwPostgreSQL
    psgr_trid = uwPostgreSQL(gv.config) # trn_race_id用
    psgr_prtb = uwPostgreSQL(gv.config) # prm_race_table用
    
    # session - open
    psgr_trid.openSession(True)
    
    # 取得する出馬表データの対象race_id取得
    rsRaceId = recset[trn_race_id](trn_race_id)
    rsRaceId.setDA(psgr_trid)
    rsRaceId.filter(w, s)

    # 出馬表データ取得クラスインスタンス
    getRaceTable = getter_prm_race_table()

    # レコードセット初期化
    getRaceTable.init_recset()

    # 開始ログ
    Logger.logging.info('>> Started the process of acquiring stakes data.')

    # 処理結果初期化
    procResult = nd.getterResult.success

    # trn_race_idループ
    race_id = ''
    while rsRaceId.eof() == False:

        # race_id
        race_id = rsRaceId.fields(trn_race_id.race_id.key).value
        # racecourse_id
        racecourse_id = rsRaceId.fields(trn_race_id.racecourse_id.key).value
        # open_id
        open_id = rsRaceId.fields(trn_race_id.open_id.key).value
        
        try:
            # ログ出力
            Logger.logging.info('>>>> The process of retrieving stakes table data has been started.')
            Logger.logging.info('>>>> race_id={0}'.format(race_id))

            # レースデータ取得
            getRaceTable.getData(race_id=race_id, racecourse_id=racecourse_id, open_id=open_id)

        except getterError as e:
            Logger.logging.error('getter error has occurred.')
            Logger.logging.error('race_id={0},error_info={1}'.format(race_id, str(e)))

        Logger.logging.info('<<<< Successfully retrieved the stakes data.')
        Logger.logging.info('<<<< race_id={0}'.format(race_id))

    # ログ出力
    if race_id != '':

        # レコードセット退避
        rsRaceInfo = getRaceTable.rsRaceInfo
        rsRaceTable = getRaceTable.rsRaceTable
        
        # reg
        regRaceData = register_RaceData(psgr_prtb)
        regRaceData.appendRecsetList(rsRaceInfo)
        regRaceData.appendRecsetList(rsRaceTable)

        # update
        Logger.logging.info('>> Started prm_race_info regist database.')
        result = regRaceData.execUpdate()
        if result:
            Logger.logging.info('<< stakes data Regist Success. Count={0}'.format(str(rsRaceId.recordCount)))
        else:
            Logger.logging.info('<< stakes data Regist Failed.')
            procResult = nd.getterResult.error

        # 終了ログ
        Logger.logging.info('<< stakes data acquisition process has been completed. result={0}'.format(procResult))

        # webdriver - quit
        getRaceTable.wdc.browserCtl.wDriver.quit()

    else:
        Logger.logging.info('<< stakes data is none.')
        
    # psgr_trid - close
    psgr_trid.closeSession()
    
def getAllRaceResult(filePath, fromYear = 2021, toYear = 2007, **kwargs):

    """
    レース結果取得メソッド(2008年～2021年) ※蓄積系

    Parameters
    ----------
    filePath : str
        呼び出し元ファイルのパス
    fromYear : int
        取得年From
    toYear : int
        取得年To
    """
    
    # 共通設定
    hc.netkeiberConfiger(gv, filePath, 'config')

    # スクレイピング回数累計初期化
    scountCumu = 0

    # 2021->2008までループしてレース結果を作成
    for year in range(fromYear, toYear, -1):

        # レース情報取得
        scount, getResult = getRaceData(filePath, year, **kwargs)

        # スクレイピング回数の累計加算
        scountCumu += scount
        
        # スクレイピング回数上限値チェック(超過時はループを抜ける)
        if scountCumu > gv.netkeiberConfig.LimitsScrapingCount:
            Logger.logging.warning('Scraping count exceeded.')
            break
        
        if getResult == False:
            break

def getAllRaceId(filePath, fromYear = 9999, toYear = 2007):
    
    """
    レースID取得メソッド(2008年～) ※蓄積系

    Parameters
    ----------
    filePath : str
        呼び出し元ファイルのパス
    fromYear : int
        取得年From
    toYear : int
        取得年To
    """

    # 共通設定
    hc.netkeiberConfiger(gv, filePath, 'config')
    
    # uwPostgreSQL
    psgr_viw_raceid_record_count = uwPostgreSQL(gv.config)

    # race_idカウント取得
    psgr_viw_raceid_record_count.openSession(True)
    rsRaceIdRecCount = recset[viw_raceid_record_count](viw_raceid_record_count)
    rsRaceIdRecCount.setDA(psgr_viw_raceid_record_count)
    rsRaceIdRecCount.filter(viw_raceid_record_count.race_count_jra > viw_raceid_record_count.race_count_nkaz)

    # # year.jsonファイル名定義
    # yearJsonFileName = 'year.json'

    # # year.jsonを格納するフォルダ名定義
    # yearJsonDirName = 'json'
    
    # # year.jsonの出力先ディレクトリチェック
    # yearJsonDir = os.path.dirname(filePath)
    # yearJsonDir = os.path.join(yearJsonDir, 'json')
    # if not os.path.exists(yearJsonDir):
    #     os.mkdir(yearJsonDir)

    # # 取込済年dict初期化
    # yearDict = dict()
    
    # # importer,exporterクラスインスタンス
    # je = JsonExporter(filePath)
    # ji = JsonImporter(filePath)

    # スクレイピング回数累計初期化
    scountCumu = 0

    # fromYear->toYearまでループしてtrn_race_idを生成
    #for year in range(fromYear, toYear, -1):
    while rsRaceIdRecCount.eof() == False:

        # # 取込済の年取得
        # yearJsonFilePath = os.path.join(yearJsonDir, yearJsonFileName)
        # if (os.path.exists(yearJsonFilePath)):
        #     yearDict = ji.convertToDict(yearJsonDirName, yearJsonFileName)
        
        # # 対象年がyearDictに存在するか
        # if str(year) in yearDict:
        #     continue
        
        # trn_race_id取得
        open_year = rsRaceIdRecCount.fields(viw_raceid_record_count.open_year.key).value
        scount, getResult = getRaceId(filePath, open_year)
        scountCumu += scount
        
        # ログ出力
        if getResult:
            Logger.logging.info('Scraping count for year {0} is {1}.'.format(open_year, str(scount)))
        else:
            Logger.logging.error('race_id acquisition failed for year {0}'.format(open_year))

        # # 成功したらyear.jsonに出力
        # if getResult:
        #     try:
        #         yearDict[str(year)] = scount
        #         je.putJsonFile(yearJsonDirName, yearJsonFileName, yearDict)
        #     except Exception as e:
        #         Logger.logging.error(str(e))
        #         Logger.logging.error('Output of year.json failed. The Process is terminated.')
        #         sys.exit()
                
        # スクレイピング回数上限値チェック(超過時はループを抜ける)
        if scountCumu > gv.netkeiberConfig.LimitsScrapingCount:
            Logger.logging.warning('Scraping count exceeded.')
            break

def getRaceId(filePath, year):
    
    """
    レースID取得メソッド(年単位)

    Parameters
    ----------
    filePath : str
        呼び出し元ファイルのパス
    year : int
        取得年
    """

    # 共通設定
    hc.netkeiberConfiger(gv, filePath, 'config')

    # レースID情報取得クラスインスタンス
    getTrnRaceId = getter_trn_race_id()

    # uwPostgreSQL
    psgr_trid = uwPostgreSQL(gv.config) # trn_race_id用

    # 開始ログ
    Logger.logging.info('>> Started the process of trn_race_id. year={0}'.format(str(year)))

    # レースID情報取得
    scountCumu = 0
    for cur_month in range(1,13,1):
        Logger.logging.info('>>>> Started getTrnRaceId.getData. Month={0}'.format(str(cur_month)))
        getTrnRaceId.getData(year=year, month=cur_month, day=0)
        scountCumu = getTrnRaceId.scrapingCount
        Logger.logging.info('<<<< Finished getTrnRaceId.getData. Month={0} ScrapingCount={1}'.format(str(cur_month),str(getTrnRaceId.scrapingCount)))
        if scountCumu > gv.netkeiberConfig.LimitsScrapingCount:
            return scountCumu, False

    # レコードセット退避
    rsRaceId = getTrnRaceId.rsRaceId
    
    # reg
    regRaceData = register_RaceData(psgr_trid)
    regRaceData.appendRecsetList(rsRaceId)

    # 処理結果初期化
    procResult = nd.getterResult.success

    # update
    Logger.logging.info('>>>> Started trn_race_id regist database')
    result = regRaceData.execUpdate()
    if result:
        Logger.logging.info('<<<< ◎trn_race_id Regist Success Count={0}'.format(str(rsRaceId.recordCount)))
    else:
        Logger.logging.info('<<<< ☓trn_race_id Regist Failed')
        procResult = nd.getterResult.error

    # 終了ログ
    Logger.logging.info('<< trn_race_id acquisition process has been completed. year={0} result={1}'.format(str(year), procResult))

    # メールインスタンス
    um = uwMail(
        gv.config.MailConfig.Host, 
        gv.config.MailConfig.SmtpPort, 
        gv.config.MailConfig.User, 
        gv.config.MailConfig.Password)
    
    # netkeiber - mail
    nkm = netkeiberMailer(um)

    # netkeiber - mailMsg
    mmsg = nkm.nkMessage()

    # mailMessage
    mmsg.mail_from = gv.netkeiberConfig.netkeibaMailConfig.mail_from
    mmsg.mail_to = gv.netkeiberConfig.netkeibaMailConfig.mail_to
    mmsg.subject = nkm.getSubject(nkm.nkMessageTemplate.mailMessage.raceid_subject.format(str(year)),procResult.name)
    mmsg.bodyText = nkm.getBodyTextByRaceIdGetter(year, rsRaceId.recordCount, scountCumu)
    
    # mailsend
    nkm.sendMail(mmsg)
    
    # スクレイピング回数累計を返す
    return scountCumu, True

def getPrmRaceId(filePath, kaisai_date:datetime):
    
    """
    レースID取得メソッド(日次)

    Parameters
    ----------
    filePath : str
        呼び出し元ファイルのパス
    kaisai_date : datetime
        開催日
    """

    # 共通設定
    hc.netkeiberConfiger(gv, filePath, 'config')

    # 現在日付の2日後の年と月を取得する
    year = kaisai_date.year
    month = kaisai_date.month
    day = kaisai_date.day

    # レースID情報取得クラスインスタンス
    getTrnRaceId = getter_trn_race_id()

    # uwPostgreSQL
    psgr_trid = uwPostgreSQL(gv.config) # trn_race_id用

    # 開始ログ
    Logger.logging.info('>> Started the process of trn_race_id. to_date={0}'.format(str(kaisai_date)))

    # レースID情報取得
    scountCumu = 0
    Logger.logging.info('>>>> Started getTrnRaceId.getData. to_date={0}'.format(str(kaisai_date)))
    getTrnRaceId.getData(year=year, month=month, day=day)
    scountCumu = getTrnRaceId.scrapingCount
    Logger.logging.info('<<<< Finished getTrnRaceId.getData. to_date={0} ScrapingCount={1}'.format(str(month),str(getTrnRaceId.scrapingCount)))
    if scountCumu > gv.netkeiberConfig.LimitsScrapingCount:
        return scountCumu, False
    
    # レコードセット退避
    rsRaceId = getTrnRaceId.rsRaceId
    
    # reg
    regRaceData = register_RaceData(psgr_trid)
    regRaceData.appendRecsetList(rsRaceId)

    # 処理結果初期化
    procResult = nd.getterResult.success

    # update
    Logger.logging.info('>>>> Started trn_race_id regist database')
    result = regRaceData.execUpdate()
    if result:
        Logger.logging.info('<<<< ◎trn_race_id Regist Success Count={0}'.format(str(rsRaceId.recordCount)))
    else:
        Logger.logging.info('<<<< ☓trn_race_id Regist Failed')
        procResult = nd.getterResult.error

    # 終了ログ
    Logger.logging.info('<< trn_race_id acquisition process has been completed. year={0} result={1}'.format(str(kaisai_date), procResult))

    # メールインスタンス
    um = uwMail(
        gv.config.MailConfig.Host, 
        gv.config.MailConfig.SmtpPort, 
        gv.config.MailConfig.User, 
        gv.config.MailConfig.Password)
    
    # netkeiber - mail
    nkm = prmRaceIdMailer(um)

    # netkeiber - mailMsg
    mmsg = nkm.nkMessage()

    # mailMessage
    mmsg.mail_from = gv.netkeiberConfig.netkeibaMailConfig.mail_from
    mmsg.mail_to = gv.netkeiberConfig.netkeibaMailConfig.mail_to
    mmsg.subject = nkm.getSubject(nkm.nkMessageTemplate.mailMessage.raceid_subject.format(str(kaisai_date)),procResult.name)
    mmsg.bodyText = nkm.getBodyTextByRaceIdGetter(kaisai_date, rsRaceId.recordCount, scountCumu)
    
    # mailsend
    nkm.sendMail(mmsg)
    
    # スクレイピング回数累計を返す
    return scountCumu, True

def getRaceData(filePath, year, race_id = '*', open_id = '*', **kwargs):
    
    """
    レースデータ取得メソッド(年単位)

    Parameters
    ----------
    filePath : str
        呼び出し元ファイルのパス
    year : int
        取得年
    race_id : str
        レースID
    open_id : str
        開催ID
    """

    # 共通設定
    hc.netkeiberConfiger(gv, filePath, 'config')
    
    # process abort file - path
    processAbortFilePath = os.path.join(os.path.dirname(filePath), gv.netkeiberConfig.processAbortFile)
    
    # メールインスタンス
    um = uwMail(
        gv.config.MailConfig.Host, 
        gv.config.MailConfig.SmtpPort, 
        gv.config.MailConfig.User, 
        gv.config.MailConfig.Password)
    
    # uwPostgreSQL
    psgr_trid = uwPostgreSQL(gv.config) # trn_race_id用
    psgr_grad = uwPostgreSQL(gv.config) # getter用
    psgr_regt = uwPostgreSQL(gv.config) # register用

    # netkeiber - mail
    nkm = netkeiberMailer(um)

    # netkeiber - mailMsg
    mmsg = nkm.nkMessage()
    
    # 開始ログ
    Logger.logging.info('>> Started get trn_race_id. year={0}'.format(str(year)))

    # where
    ts = saWhere()
    if year >= 2008 and race_id == '*' and open_id == '*':
        w = ts.and_(trn_race_id.race_id >= str(year) + '00000000').and_(trn_race_id.race_id <= str(year) + '99999999')
        w = w.and_(trn_race_id.get_status == 0)
    elif year < 2007 and race_id == '*' and open_id == '*':
        print('year is invalid.')
        sys.exit()
    elif race_id != '*':
        w = ts.and_(trn_race_id.race_id == race_id)
        w = w.and_(trn_race_id.get_status == 0)
    elif open_id != '*':
        w = ts.and_(trn_race_id.open_id == open_id)
        w = w.and_(trn_race_id.get_status == 0)
    else:
        print('args is invalid..')
        sys.exit()

    # order by
    ob = saOrderBy()
    s = ob.asc_(trn_race_id.race_id)
    
    # 更新用レコードセット用意
    psgr_trid.openSession(True)
    rsRaceId = recset[trn_race_id](trn_race_id)
    rsRaceId.setDA(psgr_trid)
    rsRaceId.filter(w, s)

    # 終了ログ
    Logger.logging.info('<< Finished get trn_race_id. year={0}'.format(str(year)))
        
    # レースデータ取得クラスインスタンス
    getRaceData = getter_RaceData(psgr_grad)

    # 開始ログ
    Logger.logging.info('>> Started the process of acquiring race data. year={0}'.format(str(year)))

    # データ取得判定フラグ取得
    raceResultRead = bool(kwargs.get('raceResultRead'))
    traningAssRead = bool(kwargs.get('traningAssRead'))
    horseResultRead = bool(kwargs.get('horseResultRead'))
    openInfoRead = bool(kwargs.get('openInfoRead'))

    # trn_race_idループ
    msgLine = []
    scountCumu = 0
    getResult = True
    while rsRaceId.eof() == False:
        
        # 処理時間計測 - 開始
        start = time.perf_counter()
        
        # レースデータ取得:パラメーター設定
        getRaceData.raceResultRead = raceResultRead
        getRaceData.traningAssRead = traningAssRead
        getRaceData.horseResultRead = horseResultRead
        getRaceData.openInfoRead = openInfoRead
        race_id = rsRaceId.fields(trn_race_id.race_id).value
        open_id = rsRaceId.fields(trn_race_id.open_id).value
        racecourse_id = rsRaceId.fields(trn_race_id.racecourse_id).value

        # 処理結果初期化
        procResult = nd.getterResult.success
        
        # 開始ログ
        Logger.logging.info('>>>> □===== Started get race_id={0} ====='.format(race_id))

        # レースデータ取得
        getRaceData.init_recset()
        getRaceData.getData(race_id=race_id, open_id=open_id, racecourse_id=racecourse_id)
        scountCumu += getRaceData.scrapingCount
        
        # レコードセット退避
        rsRaceResult = getRaceData.raceResult.rsRaceResult
        rsRaceInfo = getRaceData.raceResult.rsRaceInfo
        rsMstHorse = getRaceData.raceResult.rsMstHourse
        rsMstJockey = getRaceData.raceResult.rsMstJockey
        rsMstTrainer = getRaceData.raceResult.rsMstTrainer
        rsMstHowner = getRaceData.raceResult.rsMstHowner
        rsHorseResult = getRaceData.horseResult.rsHorseResult
        rsOpenInfo = getRaceData.openInfo.rsOpenInfo
        rsRefundInfo = getRaceData.refundInfo.rsRefundInfo
        rsPrmTraningAss = getRaceData.traningAssInfo.rsTraningAss
        rsRaceIdLog = getRaceData.raceIdLog.rsLogRaceId

        # レースNo,レース名退避
        race_no = ''
        race_nm = ''
        if getRaceData.hasError == False:
            if rsRaceInfo.recordCount > 0:
                race_no = rsRaceInfo.fields(trn_race_info.race_no).value
                race_nm = rsRaceInfo.fields(trn_race_info.race_nm).value

        # rsRaceIdLog - setDA
        rsRaceIdLog.setDA(psgr_regt)

        # エラー有無判定
        if getRaceData.hasError == True:

            # 終了ログ
            Logger.logging.info('<<< ■===== Finished get race_id={0} (getter_RaceData is terminated with an error) ====='.format(race_id))
            
            # レースIDログ登録
            upResult = rsRaceIdLog.upsert()
            if upResult.result == en.resultRegister.success:
                Logger.logging.warning('<<<< ◎log_race_id registration process Succeeded. [Error]')
            elif upResult.result == en.resultRegister.failure:
                Logger.logging.error('<<<< ☓log_race_id registration process failed.')
            procResult = nd.getterResult.error
        else:
            
            # DB更新対象セット
            regRaceData = register_RaceData(psgr_regt, race_id)
            regRaceData.appendRecsetList(rsRaceResult)
            regRaceData.appendRecsetList(rsRaceInfo)
            regRaceData.appendRecsetList(rsMstHorse)
            regRaceData.appendRecsetList(rsMstJockey)
            regRaceData.appendRecsetList(rsMstTrainer)
            regRaceData.appendRecsetList(rsMstHowner)
            regRaceData.appendRecsetList(rsHorseResult)
            regRaceData.appendRecsetList(rsOpenInfo)
            regRaceData.appendRecsetList(rsRefundInfo)
            regRaceData.appendRecsetList(rsPrmTraningAss)

            # 開始ログ
            Logger.logging.info('>>>> □===== Started race data registration process race_id={0} ====='.format(race_id))

            # update
            result = regRaceData.execUpdate()

            # 終了ログ
            Logger.logging.info('<<<< □===== Finished race data registration process race_id={0} ====='.format(race_id))

            if result == en.resultRegister.success:
                Logger.logging.info('<<<< ◎Race data registration process Succeeded.')
            elif result == en.resultRegister.failure:
                Logger.logging.error('<<<< ☓Race data registration process Failed.')
                procResult = nd.getterResult.error

            # 処理時間 - 取得
            procTime = time.perf_counter() - start

            # 開始ログ
            Logger.logging.info('>>>> □===== Started trn_race_id registration process race_id={0} ====='.format(race_id))

            # スクレイピング回数、データ取得時間セット
            rsRaceId.editRow()
            rsRaceId.fields(trn_race_id.scraping_count).value = getRaceData.scrapingCount
            rsRaceId.fields(trn_race_id.get_time).value = uwMath.round(procTime, uwMath.fraction.round)
            rsRaceId.fields(trn_race_id.get_status).value = (
                nd.getStatus.acquired.value 
                if result == en.resultRegister.success 
                else nd.getStatus.unacquired.value
            )
            rsRaceId.fields(trn_race_id.updinfo).value = Getter.getNow(Getter.datetimeFormat.updinfo)

            # レースID情報登録
            riResult = rsRaceId.upsert()

            # 終了ログ
            Logger.logging.info('<<<< □===== Finished trn_race_id registration process race_id={0} ====='.format(race_id))

            if riResult.result == en.resultRegister.success:
                Logger.logging.info('<<<< ◎trn_race_id registration process Succeeded.')
            elif riResult.result == en.resultRegister.failure:
                Logger.logging.error('<<<< ☓trn_race_id registration process Failed.')
                procResult = nd.getterResult.warning

            # 開始ログ
            Logger.logging.info('>>>> □===== Started log_race_id registration process race_id={0} ====='.format(race_id))
            
            # レースIDログ登録
            rsRaceIdLog = regRaceData.raceIdLog.rsLogRaceId
            rsRaceIdLog.setDA(psgr_regt)
            upResult = rsRaceIdLog.upsert()
            
            # 終了ログ
            Logger.logging.info('<<<< □===== Finished log_race_id registration process race_id={0} ====='.format(race_id))
            
            if upResult.result == en.resultRegister.success:
                Logger.logging.info('◎log_race_id registration process Succeeded.')
            elif upResult.result == en.resultRegister.failure:
                Logger.logging.error('☓log_race_id registration process Failed.')
                procResult = nd.getterResult.warning

            # 終了ログ
            if procResult == nd.getterResult.success:
                Logger.logging.info('>>> □===== Finished get race_id={0} ====='.format(race_id))
            else:
                Logger.logging.warning('>>> ■===== Finished get race_id={0} (An error has occured)====='.format(race_id))
        
        # msgLine追加
        AddMailMessage(nkm, msgLine, rsRaceId, race_no, race_nm, procResult)
        
        # open_idと次open_idをlogging
        Logger.logging.info('Current Open_id={0}'.format(open_id))
        if rsRaceId.nexteof() == False:
            Logger.logging.info('Next Open_id={0}'.format(rsRaceId.fields(trn_race_id.open_id.key).nextvalue))
        
        # open_idが変わったらメール送信
        if rsRaceId.nexteof() == True or \
        rsRaceId.fields(trn_race_id.open_id).nextvalue != open_id:

            # subject
            subjectStr = nkm.getSubject('race data acquisition process has been completed. open_id={0} scraping_count_cumu={1}'.format(open_id, str(scountCumu)), procResult.name)
            # mailMessage
            mmsg.mail_from = gv.netkeiberConfig.netkeibaMailConfig.mail_from
            mmsg.mail_to = gv.netkeiberConfig.netkeibaMailConfig.mail_to
            mmsg.subject = subjectStr
            mmsg.bodyText = nkm.getBodyTextByRaceInfoGetter(msgLine)
            # mailsend
            nkm.sendMail(mmsg)
            # msgLine初期化
            msgLine = []

            # メール送信ログ
            Logger.logging.info(subjectStr)

        # スクレイピング回数を超過したら処理を終了
        Logger.logging.info('Current ScrapingCumu={0}'.format(str(scountCumu)))
        if scountCumu > gv.netkeiberConfig.LimitsScrapingCount:
            getResult = False
            break
        
        # process abort file 存在チェック
        if os.path.exists(processAbortFilePath):
            getResult = False
            Logger.logging.warning(gv.netkeiberConfig.processAbortFile + ' is found. Abort process.')
            break
    
    # getRaceData - del
    del getRaceData
    
    # 終了ログ
    Logger.logging.info('<< Race data acquisition process has been completed. year={0}'.format(str(year)))

    # psgr_trid - close
    psgr_trid.closeSession()

    # スクレイピング回数累計を返す
    return scountCumu, getResult

def getTraningAss(filePath):
    
    """
    調教データ取得メソッド ※速報系

    Parameters
    ----------
    filePath : str
        呼び出し元ファイルのパス
    """

    # 共通設定
    hc.netkeiberConfiger(gv, filePath, 'config')

    # 調教データ取得クラスインスタンス
    getTraningAss = getter_prm_traning_ass()

    # uwPostgreSQL
    psgr_trid = uwPostgreSQL(gv.config) # trn_race_id用
    
    # session - open
    psgr_trid.openSession(True)

    # join
    j = saJoin()
    j.joinTable_(prm_traning_ass, j.joinKey_(trn_race_id.race_id == prm_traning_ass.race_id))
    j.columns_(trn_race_id.race_id)
    
    # where
    ts = saWhere()
    w = ts.and_(prm_traning_ass.race_id == None)

    # orderBy
    ob = saOrderBy()
    s = ob.asc_(trn_race_id.race_id)

    # trn_race_id - recset
    rsRaceId = recset[trn_race_id](trn_race_id)
    rsRaceId.setDA(psgr_trid)
    rsRaceId.outerjoinFilter(j, w, s)
    while rsRaceId.eof() == False:
        
        # race_id
        race_id = rsRaceId.fields(trn_race_id.race_id.key).value
        
        try:
            # ログ出力
            Logger.logging.info('>>>> The process of retrieving traning data has been started.')
            Logger.logging.info('>>>> race_id={0}'.format(race_id))

            # レースデータ取得
            getTraningAss.getData(race_id=race_id)

        except getterError as e:
            Logger.logging.error('getter error has occurred.')
            Logger.logging.error('race_id={0},error_info={1}'.format(race_id, str(e)))

        Logger.logging.info('<<<< Successfully retrieved the traning data.')
        Logger.logging.info('<<<< race_id={0}'.format(race_id))

    # close
    psgr_trid.closeSession()
    
def AddMailMessage(nkm:netkeiberMailer, msgLine:list, rsRaceId:recset[trn_race_id], race_no, race_nm, procResult:nd.getterResult):
    
    """
    メール本文追加
    
    Parameters
    ----------
    nkm : netkeiberMailer
        netkeiberMailerインスタンス
    msgLine : list
        メッセージリスト
    rsRaceId : recset
        trn_race_id - recset
    race_no : str
        レース番号
    race_nm : str
        レース名
    procResult : getterResult
        処理結果
    """
    
    # メッセージヘッダ部挿入
    if len(msgLine) == 0:
        msgLine.append(nkm.nkMessageTemplate.mailMessage.importDataInfoHeaderH)
        msgLine.append(nkm.nkMessageTemplate.mailMessage.importDataInfoHeaderL)
    
    # msgArgs追加
    msgArgs = []
    msgArgs.append(rsRaceId.fields(trn_race_id.race_id.key).value)
    msgArgs.append(rsRaceId.fields(trn_race_id.racecourse_id.key).value)
    msgArgs.append(race_no)
    msgArgs.append(race_nm)
    msgArgs.append(rsRaceId.fields(trn_race_id.scraping_count.key).value)
    msgArgs.append(rsRaceId.fields(trn_race_id.get_time.key).value)
    msgArgs.append(procResult.name)
    # msgLine追加
    msgLine.append(nkm.nkMessageTemplate.mailMessage.importDataInfoDetailD.format(msgArgs))
