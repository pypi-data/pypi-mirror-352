from Scrapinger.Library.scrapingConfigre import scrapingConfiger
from netkeiber.Library.netkeiberConfig import netkeiberConfig


class netkeiberConfiger(scrapingConfiger):
    """
    netkeiber共通設定クラス
    """

    def __init__(self, _tgv, _file, _configFolderName):
        """
        コンストラクタ
        """

        # 基底側コンストラクタ
        super().__init__(_tgv, _file, _configFolderName)

        # netkeibar.ini
        da = netkeiberConfig()
        da.getConfig(_file, _configFolderName)

        # gvセット
        _tgv.netkeiberConfig = da
