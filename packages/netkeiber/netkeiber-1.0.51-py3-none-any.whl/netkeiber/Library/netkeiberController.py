import re
import LibHanger.Library.uwGetter as CmnGetter
from netkeiber.Library.netkeiberGlobals import *
from LibHanger.Models.fields import *
from Scrapinger.Library.browserContainer import browserContainer
from netkeiber.Library.netkeiberConfig import netkeiberConfig

class netkeibaBrowserController(browserContainer):
    
    """
    netkeiberブラウザコントローラー
    """
    
    def __init__(self, _config: netkeiberConfig) -> None:
        
        """
        コンストラクタ
        """
        
        # 基底側コンストラクタ
        super().__init__(_config)
        
        # configをnetkeiberConfigにCast
        self.config:netkeiberConfig = _config
        
        # スクレイピング準備
        self.wdc.settingScrape()

    def getData(self, *args, **kwargs):
        
        """
        データ取得
        """
        
        pass
    
    def getUpdInfo(self):

        """
        更新情報取得
        """

        return CmnGetter.getNow().strftime('%Y/%m/%d %H:%M:%S')
    
    def isdigitEx(self, targetString:str) -> bool:
        
        """
        数値判定
        """
        
        return re.compile("^\d+\.?\d*\Z").match(targetString)
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
            _scrapingType : scrapingConfig.settingValueStruct.ScrapingType
                スクレイピングタイプ
            """

            super().__init__(_config, _scrapingType)